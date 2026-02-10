"""Supabase-first enricher: bulk lookup from Supabase, TMDB fallback for misses."""
import json
import re
import requests
import time
import unicodedata
import urllib.parse
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from app import config


class SupabaseEnricher:
    """Enriches film data using Supabase as primary source, TMDB as fallback."""

    # Set to True to re-enable TMDB fallback for films not found in Supabase.
    # Disabled by default: ~90% of misses are TV shows/shorts not in the database,
    # and TMDB calls dominate processing time.
    TMDB_FALLBACK_ENABLED = False

    def __init__(self, on_progress: Callable = None):
        self.on_progress = on_progress
        self._new_cache_entries = 0
        self._tmdb_fallback_films: List[Dict] = []  # Track films not in Supabase

        # Supabase config
        self.supabase_url = config.SUPABASE_URL
        self.supabase_key = config.SUPABASE_KEY
        self.supabase_session = requests.Session()
        self.supabase_session.headers.update({
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
        })

        # TMDB fallback
        self.tmdb_base = config.TMDB_BASE_URL
        self.tmdb_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10, pool_maxsize=10,
            max_retries=requests.adapters.Retry(total=2, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
        )
        self.tmdb_session.mount('https://', adapter)
        self.tmdb_session.params = {'api_key': config.TMDB_API_KEY}

        self._rate_lock = threading.Lock()
        self._request_times: List[float] = []
        self._tmdb_session_cache: Dict[Tuple[str, int], Optional[Dict]] = {}

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize a title for fuzzy matching.

        Handles mojibake (â€" → –) common in Letterboxd CSV exports where UTF-8
        bytes were mis-decoded as Windows-1252, plus Unicode accents and punctuation.
        """
        # Fix mojibake: try re-encoding as Windows-1252 and decoding as UTF-8.
        # e.g. "â€"" (mis-decoded en dash) → "–", "â€"Â\u00a0" → "–\u00a0"
        # If encoding fails (non-Windows-1252 chars) or decoding produces invalid UTF-8,
        # leave the title unchanged.
        try:
            title = title.encode('windows-1252').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        # Normalize unicode (e.g. é → e, ñ → n)
        normalized = unicodedata.normalize('NFKD', title)
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        normalized = normalized.lower()
        # Remove punctuation except spaces
        normalized = re.sub(r"[^\w\s]", '', normalized)
        # Collapse whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def get_new_cache_count(self) -> int:
        return self._new_cache_entries

    def get_tmdb_fallback_films(self) -> List[Dict]:
        """Return list of films that were not in Supabase and needed TMDB fallback."""
        return self._tmdb_fallback_films

    def _transform_supabase_row(self, row: Dict) -> Dict:
        """Transform a Supabase movie row into the enricher output format."""
        # Parse genres from comma-separated string
        genres = [g.strip() for g in (row.get('genres') or '').split(',') if g.strip()]

        # Parse production companies from comma-separated string (no logos from Supabase)
        companies_str = row.get('production_companies') or ''
        production_companies = [
            {'name': c.strip(), 'logo_path': None}
            for c in companies_str.split(',') if c.strip()
        ]

        # Parse production countries
        countries_str = row.get('production_countries') or ''
        production_countries = [c.strip() for c in countries_str.split(',') if c.strip()]

        # Parse cast_details (may be JSON array or JSON string)
        cast_details = row.get('cast_details') or []
        if isinstance(cast_details, str):
            try:
                cast_details = json.loads(cast_details)
            except (json.JSONDecodeError, TypeError):
                cast_details = []
        actors = [
            {'name': a['name'], 'character': a.get('character', ''), 'profile_path': a.get('profile_path')}
            for a in cast_details[:10]
        ]

        # Director
        director_name = row.get('director') or ''
        directors = [d.strip() for d in director_name.split(',') if d.strip()][:3]
        director_profiles = {d: None for d in directors}

        # Cinematographers
        dop = row.get('director_of_photography') or ''
        cinematographers = [{'name': c.strip(), 'profile_path': None} for c in dop.split(',') if c.strip()][:2]

        # Composers
        composer = row.get('music_composer') or ''
        composers = [{'name': c.strip(), 'profile_path': None} for c in composer.split(',') if c.strip()][:2]

        # Writers
        writers_str = row.get('writers') or ''
        writers = [{'name': w.strip(), 'profile_path': None} for w in writers_str.split(',') if w.strip()][:3]

        return {
            'tmdb_id': row.get('id'),
            'title': row.get('title'),
            'original_title': row.get('original_title'),
            'release_date': row.get('release_date'),
            'runtime': row.get('runtime'),
            'genres': genres,
            'overview': row.get('overview'),
            'popularity': row.get('popularity'),
            'vote_average': row.get('imdb_rating'),
            'vote_count': row.get('imdb_votes'),
            'poster_path': row.get('poster_path'),
            'backdrop_path': None,
            'original_language': row.get('original_language'),
            'production_countries': production_countries,
            'budget': row.get('budget'),
            'revenue': row.get('revenue'),
            'production_companies': production_companies,
            'actors': actors,
            'directors': directors,
            'director_profiles': director_profiles,
            'cinematographers': cinematographers,
            'composers': composers,
            'writers': writers,
        }

    def _query_supabase_batch(self, titles: List[str]) -> List[Dict]:
        """Query Supabase for a batch of titles."""
        # Build URL manually to avoid requests encoding commas in the in.() filter
        # PostgREST needs: ?title=in.("Title 1","Title 2")
        escaped_titles = ','.join(f'"{t}"' for t in titles)
        filter_value = f'in.({escaped_titles})'
        # Encode only the filter value, preserving PostgREST syntax
        url = f'{self.supabase_url}/rest/v1/movies?select=*&title={urllib.parse.quote(filter_value, safe="().,\"")}'
        try:
            resp = self.supabase_session.get(url, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Supabase batch query failed: {e}")
            return []

    def _query_supabase_ilike(self, prefix: str) -> List[Dict]:
        """Query Supabase for titles starting with prefix (case-insensitive).

        Used as Pass 4 to catch title mismatches like:
        - "Die Hard With a Vengeance" → "Die Hard: With a Vengeance"
        - "Glass Onion" → "Glass Onion: A Knives Out Mystery"
        """
        pattern = f'{prefix}*'
        encoded = urllib.parse.quote(pattern, safe='*')
        url = f'{self.supabase_url}/rest/v1/movies?select=*&title=ilike.{encoded}&limit=50'
        try:
            resp = self.supabase_session.get(url, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Supabase ilike query failed for '{prefix}': {e}")
            return []

    def _tmdb_rate_limit(self):
        with self._rate_lock:
            now = time.time()
            self._request_times = [t for t in self._request_times if now - t < 10]
            if len(self._request_times) >= config.TMDB_RATE_LIMIT:
                sleep_time = 10 - (now - self._request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self._request_times = []
            self._request_times.append(time.time())

    def _tmdb_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        self._tmdb_rate_limit()
        try:
            resp = self.tmdb_session.get(f'{self.tmdb_base}/{endpoint}', params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except:
            return None

    def _tmdb_search(self, title: str, year: int) -> Optional[Dict]:
        """Search TMDB as fallback."""
        params = {'query': title, 'year': year, 'include_adult': False}
        result = self._tmdb_request('search/movie', params)

        if not result or not result.get('results'):
            params.pop('year')
            result = self._tmdb_request('search/movie', params)

        if not result or not result.get('results'):
            return None

        movie = result['results'][0]
        # Validate using normalized titles so that dash/punctuation differences don't block matches
        # e.g. "Mission: Impossible – Ghost Protocol" (en dash) matches TMDB's "Mission: Impossible - Ghost Protocol"
        norm_search = self._normalize_title(title)
        norm_result = self._normalize_title(movie.get('title', ''))
        norm_orig = self._normalize_title(movie.get('original_title', ''))
        if (norm_search not in norm_result and norm_result not in norm_search
                and norm_search not in norm_orig and norm_orig not in norm_search):
            return None

        # Get full details
        details = self._tmdb_request(f"movie/{movie['id']}", {'append_to_response': 'credits'})
        if not details:
            return None

        credits = details.get('credits') or {}
        cast = credits.get('cast', [])[:10]
        crew = credits.get('crew', [])

        directors_list = [p for p in crew if p.get('job') == 'Director'][:3]

        return {
            'tmdb_id': movie['id'],
            'title': details.get('title'),
            'original_title': details.get('original_title'),
            'release_date': details.get('release_date'),
            'runtime': details.get('runtime'),
            'genres': [g['name'] for g in details.get('genres', [])],
            'overview': details.get('overview'),
            'popularity': details.get('popularity'),
            'vote_average': details.get('vote_average'),
            'vote_count': details.get('vote_count'),
            'poster_path': details.get('poster_path'),
            'backdrop_path': details.get('backdrop_path'),
            'original_language': details.get('original_language'),
            'production_countries': [c['name'] for c in details.get('production_countries', [])],
            'budget': details.get('budget'),
            'revenue': details.get('revenue'),
            'production_companies': [
                {'name': c['name'], 'logo_path': c.get('logo_path')}
                for c in details.get('production_companies', [])
            ][:3],
            'actors': [
                {'name': a['name'], 'character': a.get('character'), 'profile_path': a.get('profile_path')}
                for a in cast
            ],
            'directors': [d['name'] for d in directors_list],
            'director_profiles': {d['name']: d.get('profile_path') for d in directors_list},
            'cinematographers': [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') == 'Director of Photography'
            ][:2],
            'composers': [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') == 'Original Music Composer'
            ][:2],
            'writers': [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') in ('Screenplay', 'Writer')
            ][:3],
        }

    def _fetch_tmdb_single(self, title: str, year: int) -> Tuple[str, int, Optional[Dict]]:
        if year == 0:
            return (title, year, None)
        cache_key = (title, year)
        if cache_key in self._tmdb_session_cache:
            return (title, year, self._tmdb_session_cache[cache_key])
        result = self._tmdb_search(title, year)
        self._tmdb_session_cache[cache_key] = result
        return (title, year, result)

    def enrich_films(self, films_df, diary_df=None) -> Dict[Tuple, Dict]:
        """Enrich films: Supabase first, TMDB fallback."""
        enriched: Dict[Tuple, Dict] = {}

        # Collect all films to look up
        film_list = []
        for _, row in films_df.iterrows():
            title = row['Name']
            year = int(row['Year']) if row['Year'] else 0
            if year > 0:
                film_list.append((title, year))

        total = len(film_list)
        if self.on_progress:
            self.on_progress(f"Looking up {total} films in database...", 0)

        # Phase 1: Parallel batch query Supabase
        unique_titles = list({title for title, _ in film_list})
        batch_size = 50
        batches = [unique_titles[i:i + batch_size] for i in range(0, len(unique_titles), batch_size)]
        total_batches = len(batches)

        # Collect all batch results, then merge (thread-safe: no shared writes)
        batch_results: List[List[Dict]] = [[] for _ in range(total_batches)]
        max_supabase_workers = min(5, total_batches)
        completed_batches = 0
        batch_lock = threading.Lock()

        def _fetch_batch(idx: int, batch: List[str]) -> Tuple[int, List[Dict]]:
            return (idx, self._query_supabase_batch(batch))

        with ThreadPoolExecutor(max_workers=max_supabase_workers) as executor:
            futures = {
                executor.submit(_fetch_batch, i, batch): i
                for i, batch in enumerate(batches)
            }
            for future in as_completed(futures):
                idx, rows = future.result()
                batch_results[idx] = rows
                with batch_lock:
                    completed_batches += 1
                    if self.on_progress:
                        pct = completed_batches / total_batches * 60
                        self.on_progress(f"Scanning database... ({completed_batches}/{total_batches} batches)", pct)

        # Merge all batch results into lookup dict
        supabase_results: Dict[str, List[Dict]] = {}
        for rows in batch_results:
            for row in rows:
                t = row.get('title', '')
                if t not in supabase_results:
                    supabase_results[t] = []
                supabase_results[t].append(row)

        # Pass 1: Exact title match + year within ±2
        tmdb_needed = []
        tmdb_needed_reasons: Dict[Tuple[str, int], str] = {}
        supabase_hits = 0
        for title, year in film_list:
            candidates = supabase_results.get(title, [])
            matched = None
            for row in candidates:
                row_year = row.get('year')
                if row_year and abs(int(row_year) - year) <= 2:
                    matched = row
                    break
            if matched:
                enriched[(title, year)] = self._transform_supabase_row(matched)
                supabase_hits += 1
            else:
                if candidates:
                    tmdb_needed_reasons[(title, year)] = "year_mismatch"
                else:
                    tmdb_needed_reasons[(title, year)] = "not_in_db"
                tmdb_needed.append((title, year))

        # Pass 2: Normalized title fallback for remaining misses
        # Handles punctuation/dash/unicode differences (e.g. "Mission: Impossible – Rogue Nation"
        # matching Supabase "Mission: Impossible - Rogue Nation")
        if tmdb_needed:
            # Build normalized lookup from ALL Supabase results
            normalized_lookup: Dict[str, List[Dict]] = {}
            for title_key, rows in supabase_results.items():
                norm_key = self._normalize_title(title_key)
                if norm_key not in normalized_lookup:
                    normalized_lookup[norm_key] = []
                normalized_lookup[norm_key].extend(rows)

            still_needed = []
            for title, year in tmdb_needed:
                norm_title = self._normalize_title(title)
                candidates = normalized_lookup.get(norm_title, [])
                matched = None
                for row in candidates:
                    row_year = row.get('year')
                    if row_year and abs(int(row_year) - year) <= 2:
                        matched = row
                        break
                if matched:
                    enriched[(title, year)] = self._transform_supabase_row(matched)
                    supabase_hits += 1
                    tmdb_needed_reasons.pop((title, year), None)
                else:
                    still_needed.append((title, year))
            tmdb_needed = still_needed

        # Pass 3: Prefix match against already-fetched Supabase results.
        # Handles cases where another film in the same batch has the full title (rare but free).
        if tmdb_needed:
            norm_supabase_entries: List[Tuple[str, Dict]] = []
            for title_key, rows in supabase_results.items():
                norm_key = self._normalize_title(title_key)
                for row in rows:
                    norm_supabase_entries.append((norm_key, row))

            still_needed = []
            for title, year in tmdb_needed:
                norm_title = self._normalize_title(title)
                if len(norm_title) < 5:
                    still_needed.append((title, year))
                    continue
                matched = None
                for norm_key, row in norm_supabase_entries:
                    if (norm_key.startswith(norm_title)
                            and (len(norm_key) == len(norm_title) or norm_key[len(norm_title)] == ' ')):
                        row_year = row.get('year')
                        if row_year and abs(int(row_year) - year) <= 2:
                            matched = row
                            break
                if matched:
                    enriched[(title, year)] = self._transform_supabase_row(matched)
                    supabase_hits += 1
                    tmdb_needed_reasons.pop((title, year), None)
                else:
                    still_needed.append((title, year))
            tmdb_needed = still_needed

        # Pass 4: ilike prefix query — the main fix for punctuation/subtitle mismatches.
        # Queries Supabase with "first two normalized words*" then validates with normalized comparison.
        # Catches:
        #   "Die Hard With a Vengeance"  → "Die Hard: With a Vengeance"
        #   "Glass Onion"                → "Glass Onion: A Knives Out Mystery"
        #   "Wake Up Dead Man"           → "Wake Up Dead Man: A Knives Out Mystery"
        #   "Mission: Impossible – …"   → "Mission: Impossible - …"  (after mojibake fix)
        if tmdb_needed:
            # Group unmatched films by their 2-word normalized prefix to batch ilike queries
            prefix_to_films: Dict[str, List[Tuple[str, int]]] = {}
            no_prefix_films = []
            for title, year in tmdb_needed:
                words = self._normalize_title(title).split()
                if len(words) < 2:
                    no_prefix_films.append((title, year))
                    continue
                prefix = ' '.join(words[:2])
                prefix_to_films.setdefault(prefix, []).append((title, year))

            # Parallel ilike fetches (one per unique prefix)
            prefix_results: Dict[str, List[Dict]] = {}
            if prefix_to_films:
                with ThreadPoolExecutor(max_workers=min(5, len(prefix_to_films))) as executor:
                    futures = {
                        executor.submit(self._query_supabase_ilike, prefix): prefix
                        for prefix in prefix_to_films
                    }
                    for future in as_completed(futures):
                        prefix = futures[future]
                        prefix_results[prefix] = future.result()

            still_needed = list(no_prefix_films)
            for prefix, films_for_prefix in prefix_to_films.items():
                candidate_rows = prefix_results.get(prefix, [])
                for title, year in films_for_prefix:
                    norm_title = self._normalize_title(title)
                    matched = None
                    for row in candidate_rows:
                        row_year = row.get('year')
                        if not row_year or abs(int(row_year) - year) > 2:
                            continue
                        norm_row = self._normalize_title(row.get('title', ''))
                        # Exact normalized match
                        if norm_row == norm_title:
                            matched = row
                            break
                        # Prefix match: Supabase has a longer subtitle (e.g. "Glass Onion: A Knives Out Mystery")
                        if (len(norm_title) >= 5
                                and norm_row.startswith(norm_title)
                                and (len(norm_row) == len(norm_title) or norm_row[len(norm_title)] == ' ')):
                            matched = row
                            break
                    if matched:
                        enriched[(title, year)] = self._transform_supabase_row(matched)
                        supabase_hits += 1
                        tmdb_needed_reasons.pop((title, year), None)
                    else:
                        still_needed.append((title, year))
            tmdb_needed = still_needed

        if self.on_progress:
            self.on_progress(f"Found {supabase_hits}/{total} films in database.", 70)

        # Phase 2: TMDB fallback (disabled by default — ~90% of misses are TV shows/shorts)
        if self.TMDB_FALLBACK_ENABLED and tmdb_needed:
            tmdb_total = len(tmdb_needed)
            completed = 0
            max_workers = min(15, tmdb_total)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_tmdb_single, title, year): (title, year)
                    for title, year in tmdb_needed
                }
                for future in as_completed(futures):
                    title, year, metadata = future.result()
                    if metadata:
                        enriched[(title, year)] = metadata
                        self._new_cache_entries += 1
                    completed += 1

                    if self.on_progress and completed % 5 == 0:
                        pct = 70 + completed / tmdb_total * 25
                        self.on_progress(f"Fetching metadata for rare films... ({completed}/{tmdb_total})", min(pct, 95))

        # Store list of films not found in database (for CSV download)
        self._tmdb_fallback_films = [
            {
                'title': t,
                'year': y,
                'tmdb_found': (t, y) in enriched,
                'supabase_miss_reason': tmdb_needed_reasons.get((t, y), 'not_in_db'),
            }
            for t, y in tmdb_needed
        ]

        if self.on_progress:
            self.on_progress(f"Enrichment complete: {len(enriched)}/{total} films", 98)

        return enriched

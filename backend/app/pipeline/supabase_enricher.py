"""Supabase-first enricher: bulk lookup from Supabase, TMDB fallback for misses."""
import json
import requests
import time
import urllib.parse
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from app import config


class SupabaseEnricher:
    """Enriches film data using Supabase as primary source, TMDB as fallback."""

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
        # Basic validation
        result_title = movie.get('title', '').lower()
        search_lower = title.lower()
        if search_lower not in result_title and result_title not in search_lower:
            orig = movie.get('original_title', '').lower()
            if search_lower not in orig and orig not in search_lower:
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
        return (title, year, self._tmdb_search(title, year))

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

        # Phase 1: Batch query Supabase
        # Group by unique titles for batch queries
        unique_titles = list({title for title, _ in film_list})
        batch_size = 50
        supabase_results: Dict[str, List[Dict]] = {}  # title -> list of rows

        for i in range(0, len(unique_titles), batch_size):
            batch = unique_titles[i:i + batch_size]
            rows = self._query_supabase_batch(batch)
            for row in rows:
                t = row.get('title', '')
                if t not in supabase_results:
                    supabase_results[t] = []
                supabase_results[t].append(row)

            if self.on_progress:
                pct = min(i + batch_size, len(unique_titles)) / len(unique_titles) * 60
                self.on_progress(f"Database lookup ({min(i + batch_size, len(unique_titles))}/{len(unique_titles)})...", pct)

        # Match by title + year
        tmdb_needed = []
        supabase_hits = 0
        for title, year in film_list:
            candidates = supabase_results.get(title, [])
            matched = None
            for row in candidates:
                row_year = row.get('year')
                if row_year and abs(int(row_year) - year) <= 1:
                    matched = row
                    break
            if matched:
                enriched[(title, year)] = self._transform_supabase_row(matched)
                supabase_hits += 1
            else:
                tmdb_needed.append((title, year))

        # Store the list of films needing TMDB fallback
        self._tmdb_fallback_films = [{'title': t, 'year': y} for t, y in tmdb_needed]

        if self.on_progress:
            self.on_progress(f"{supabase_hits} found in database, {len(tmdb_needed)} need TMDB lookup", 65)

        # Phase 2: TMDB fallback for misses
        if tmdb_needed:
            tmdb_total = len(tmdb_needed)
            completed = 0
            max_workers = min(8, tmdb_total)

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
                        pct = 65 + completed / tmdb_total * 30
                        self.on_progress(f"TMDB fallback ({completed}/{tmdb_total})...", min(pct, 95))

        if self.on_progress:
            self.on_progress(f"Enrichment complete: {len(enriched)}/{total} films", 98)

        return enriched

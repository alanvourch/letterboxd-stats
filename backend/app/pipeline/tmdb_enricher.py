"""TMDB API integration for enriching Letterboxd data with metadata."""
import requests
import time
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from app import config


class TMDBEnricher:
    """Enriches film data using The Movie Database (TMDB) API."""

    def __init__(self, shared_cache: dict = None, on_progress: Callable = None):
        self.api_key = config.TMDB_API_KEY
        self.base_url = config.TMDB_BASE_URL
        self.cache = shared_cache if shared_cache is not None else {}
        self.on_progress = on_progress
        self._lock = threading.Lock()
        self._rate_lock = threading.Lock()
        self._request_times: List[float] = []
        self._new_cache_entries = 0
        self.stats = {
            'total': 0,
            'matched': 0,
            'cached': 0,
            'failed': 0,
            'unmatched_films': []
        }

        # Connection-pooled session
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=requests.adapters.Retry(
                total=2,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self.session.mount('https://', adapter)
        self.session.params = {'api_key': self.api_key}

        if not self.api_key:
            raise ValueError("TMDB API key is required")

    def get_new_cache_count(self) -> int:
        """Return count of new cache entries added."""
        return self._new_cache_entries

    def _rate_limit(self):
        """Enforce TMDB rate limiting."""
        with self._rate_lock:
            now = time.time()
            window = 10  # 10 seconds
            self._request_times = [t for t in self._request_times if now - t < window]
            if len(self._request_times) >= config.TMDB_RATE_LIMIT:
                sleep_time = window - (now - self._request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self._request_times = []
            self._request_times.append(time.time())

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a rate-limited request to TMDB API."""
        self._rate_limit()
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def _normalize_cache_key(self, title: str, year: int) -> str:
        """Create normalized cache key."""
        return f"{title.lower().strip()}_{year}"

    def _is_cache_valid(self, cached_data: Dict) -> bool:
        """Check if cached data is still valid."""
        cached_date = cached_data.get('cached_at')
        if not cached_date:
            return True
        try:
            cached_dt = datetime.fromisoformat(cached_date)
            expiry = timedelta(days=config.CACHE_EXPIRY_DAYS)
            return datetime.now() - cached_dt < expiry
        except:
            return True

    def search_movie(self, title: str, year: int) -> Optional[Dict]:
        """Search for a movie by title and year."""
        cache_key = self._normalize_cache_key(title, year)

        with self._lock:
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if self._is_cache_valid(cached):
                    self.stats['cached'] += 1
                    return cached

        params = {'query': title, 'year': year, 'include_adult': False}
        result = self._make_request('search/movie', params)

        if not result or not result.get('results'):
            params.pop('year')
            result = self._make_request('search/movie', params)

        if result and result.get('results'):
            movie = result['results'][0]
            if self._validate_match(title, year, movie):
                full_details = self.get_movie_details(movie['id'])
                if full_details:
                    full_details['cached_at'] = datetime.now().isoformat()
                    with self._lock:
                        self.cache[cache_key] = full_details
                        self._new_cache_entries += 1
                        self.stats['matched'] += 1
                    return full_details

        with self._lock:
            self.stats['failed'] += 1
            self.stats['unmatched_films'].append({'title': title, 'year': year})
        return None

    def _validate_match(self, search_title: str, search_year: int, tmdb_result: Dict) -> bool:
        """Validate TMDB result is a good match."""
        result_title = tmdb_result.get('title', '').lower()
        search_title_lower = search_title.lower()

        if search_title_lower not in result_title and result_title not in search_title_lower:
            original_title = tmdb_result.get('original_title', '').lower()
            if search_title_lower not in original_title and original_title not in search_title_lower:
                return False

        release_date = tmdb_result.get('release_date', '')
        if release_date:
            try:
                result_year = int(release_date[:4])
                if abs(result_year - search_year) > 1:
                    return False
            except:
                pass
        return True

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Get full movie details including credits."""
        movie = self._make_request(f'movie/{tmdb_id}', params={
            'append_to_response': 'credits'
        })
        if not movie:
            return None

        credits = movie.get('credits')

        details = {
            'tmdb_id': tmdb_id,
            'title': movie.get('title'),
            'original_title': movie.get('original_title'),
            'release_date': movie.get('release_date'),
            'runtime': movie.get('runtime'),
            'genres': [g['name'] for g in movie.get('genres', [])],
            'overview': movie.get('overview'),
            'popularity': movie.get('popularity'),
            'vote_average': movie.get('vote_average'),
            'vote_count': movie.get('vote_count'),
            'poster_path': movie.get('poster_path'),
            'backdrop_path': movie.get('backdrop_path'),
            'original_language': movie.get('original_language'),
            'production_countries': [c['name'] for c in movie.get('production_countries', [])],
            'budget': movie.get('budget'),
            'revenue': movie.get('revenue'),
        }

        details['production_companies'] = [
            {'name': c['name'], 'logo_path': c.get('logo_path')}
            for c in movie.get('production_companies', [])
        ][:3]

        if credits:
            cast = credits.get('cast', [])[:10]
            details['actors'] = [
                {'name': actor['name'], 'character': actor.get('character'), 'profile_path': actor.get('profile_path')}
                for actor in cast
            ]

            crew = credits.get('crew', [])
            directors = [{'name': p['name'], 'profile_path': p.get('profile_path')}
                        for p in crew if p.get('job') == 'Director']
            details['directors'] = [d['name'] for d in directors[:3]]
            details['director_profiles'] = {d['name']: d['profile_path'] for d in directors[:3]}

            details['cinematographers'] = [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') == 'Director of Photography'
            ][:2]

            details['composers'] = [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') == 'Original Music Composer'
            ][:2]

            details['writers'] = [
                {'name': p['name'], 'profile_path': p.get('profile_path')}
                for p in crew if p.get('job') in ('Screenplay', 'Writer')
            ][:3]

        return details

    def _fetch_single_film(self, title: str, year: int) -> Tuple[str, int, Optional[Dict]]:
        """Fetch a single film for thread pool."""
        if year == 0:
            return (title, year, None)
        metadata = self.search_movie(title, year)
        return (title, year, metadata)

    def enrich_films(self, films_df, diary_df=None) -> Dict[str, Dict]:
        """Enrich a dataframe of films with TMDB metadata."""
        enriched = {}
        self.stats['total'] = len(films_df)

        # Separate cached vs uncached films
        to_fetch = []
        for _, row in films_df.iterrows():
            title = row['Name']
            year = int(row['Year']) if row['Year'] else 0
            if year == 0:
                continue

            cache_key = self._normalize_cache_key(title, year)
            if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
                enriched[(title, year)] = self.cache[cache_key]
                self.stats['cached'] += 1
            else:
                to_fetch.append((title, year))

        cached_count = len(enriched)
        total_to_fetch = len(to_fetch)

        if self.on_progress:
            self.on_progress(f"{cached_count} from cache, {total_to_fetch} to fetch", 0)

        if to_fetch:
            max_workers = min(8, len(to_fetch))
            completed = 0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_single_film, title, year): (title, year)
                    for title, year in to_fetch
                }

                for future in as_completed(futures):
                    title, year, metadata = future.result()
                    if metadata:
                        enriched[(title, year)] = metadata
                    completed += 1

                    if self.on_progress and completed % 10 == 0:
                        pct = completed / total_to_fetch * 100
                        self.on_progress(f"Fetching metadata ({completed}/{total_to_fetch})...", pct)

        # Backfill studio logos
        self._backfill_studio_logos(enriched)

        return enriched

    def _backfill_studio_logos(self, enriched: Dict):
        """Backfill logo_path for production_companies missing logos."""
        needs_logo = set()
        for data in enriched.values():
            for comp in data.get('production_companies', []):
                if isinstance(comp, str):
                    needs_logo.add(comp)
                elif isinstance(comp, dict) and not comp.get('logo_path'):
                    needs_logo.add(comp['name'])

        if not needs_logo:
            return

        if self.on_progress:
            self.on_progress(f"Backfilling logos for {len(needs_logo)} studios...", 0)

        logo_map = {}
        for name in needs_logo:
            result = self._make_request('search/company', {'query': name})
            if result and result.get('results'):
                for r in result['results']:
                    if r['name'].lower() == name.lower() and r.get('logo_path'):
                        logo_map[name] = r['logo_path']
                        break

        if not logo_map:
            return

        for data in list(enriched.values()) + list(self.cache.values()):
            companies = data.get('production_companies', [])
            new_companies = []
            changed = False
            for comp in companies:
                if isinstance(comp, str):
                    new_companies.append({'name': comp, 'logo_path': logo_map.get(comp)})
                    changed = True
                elif isinstance(comp, dict) and not comp.get('logo_path') and comp['name'] in logo_map:
                    comp['logo_path'] = logo_map[comp['name']]
                    new_companies.append(comp)
                    changed = True
                else:
                    new_companies.append(comp)
            if changed:
                data['production_companies'] = new_companies

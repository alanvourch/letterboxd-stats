"""
Calculate enhanced statistics from Letterboxd and TMDB data
"""
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app import config


class StatsCalculator:
    """Calculate comprehensive statistics from enriched film data"""

    def __init__(self, letterboxd_data: Dict[str, pd.DataFrame], tmdb_data: Dict[Tuple, Dict]):
        self.lb_data = letterboxd_data
        self.tmdb_data = tmdb_data
        self.stats = {}
        # Build lookup sets/dicts for fast checking
        self._build_liked_lookup()
        self._build_watched_lookup()
        self._build_rating_lookup()

    def _build_liked_lookup(self):
        """Build a set of liked films for fast lookup"""
        liked = self.lb_data.get('liked_films', pd.DataFrame())
        self.liked_set = set()
        if not liked.empty:
            for _, row in liked.iterrows():
                self.liked_set.add((row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0))

    def _build_watched_lookup(self):
        """Build a set of watched films for fast lookup (excludes watchlist)"""
        watched = self.lb_data.get('watched', pd.DataFrame())
        self.watched_set = set()
        if not watched.empty:
            for _, row in watched.iterrows():
                self.watched_set.add((row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0))

    def _build_rating_lookup(self):
        """Build a dict of (title, year) -> rating for O(1) lookup"""
        ratings = self.lb_data.get('ratings', pd.DataFrame())
        self.rating_dict = {}
        if not ratings.empty:
            for _, row in ratings.iterrows():
                key = (row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0)
                self.rating_dict[key] = float(row['Rating'])

    def is_film_watched(self, title: str, year: int) -> bool:
        """Check if a film is in the watched list (not just watchlist)"""
        return (title, year) in self.watched_set

    def is_film_liked(self, title: str, year: int) -> bool:
        """Check if a film is liked"""
        return (title, year) in self.liked_set

    def calculate_all(self) -> Dict:
        """Calculate all statistics"""
        print("\nCalculating statistics...")

        # Basic stats
        self._calculate_basic_stats()

        # TMDB-enriched stats
        self._calculate_genre_stats()
        self._calculate_actor_stats()
        self._calculate_director_stats()
        self._calculate_runtime_stats()
        self._calculate_country_language_stats()

        # Advanced correlations
        self._calculate_rating_trends()
        self._calculate_genre_rating_correlation()
        self._calculate_tag_stats()

        # Temporal stats
        self._calculate_temporal_stats()

        # NEW: Yearly breakdown (last full year vs current year)
        self._calculate_yearly_breakdown()

        # NEW: Liked-specific stats
        self._calculate_liked_stats()

        # NEW: Rating distribution for charts
        self._calculate_rating_distribution()

        # V5.0: New statistics
        self._calculate_crew_stats()
        self._calculate_studio_stats()
        self._calculate_decade_stats()
        self._calculate_rewatch_stats()
        self._calculate_journey_stats()
        self._calculate_five_star_films()
        self._calculate_fun_facts()

        print("[OK] Statistics calculated")
        return self.stats

    def enrich_people_profiles(self, enricher):
        """Fetch TMDB profile images for top people missing photos."""
        names_needing_profiles = set()

        for role in ['directors', 'composers', 'cinematographers', 'writers']:
            for person in self.stats.get(role, {}).get('top_by_count', []):
                if not person.get('profile_path'):
                    names_needing_profiles.add(person['name'])

        # Also check yearly breakdown top actor/director
        for year_key in ['last_full_year', 'current_year']:
            year_data = self.stats.get('yearly_breakdown', {}).get(year_key, {})
            for person_key in ['top_actor', 'top_director']:
                person = year_data.get(person_key)
                if person and not person.get('profile_path'):
                    names_needing_profiles.add(person['name'])

        if not names_needing_profiles:
            return

        print(f"Fetching profile images for {len(names_needing_profiles)} people...")
        profiles = enricher.fetch_person_profiles(list(names_needing_profiles))
        print(f"Found {len(profiles)} profile images")

        # Patch the stats
        for role in ['directors', 'composers', 'cinematographers', 'writers']:
            for person in self.stats.get(role, {}).get('top_by_count', []):
                if not person.get('profile_path') and person['name'] in profiles:
                    person['profile_path'] = profiles[person['name']]

        for year_key in ['last_full_year', 'current_year']:
            year_data = self.stats.get('yearly_breakdown', {}).get(year_key, {})
            for person_key in ['top_actor', 'top_director']:
                person = year_data.get(person_key)
                if person and not person.get('profile_path') and person['name'] in profiles:
                    person['profile_path'] = profiles[person['name']]

    def _calculate_basic_stats(self):
        """Calculate basic Letterboxd statistics"""
        watched = self.lb_data.get('watched', pd.DataFrame())
        diary = self.lb_data.get('diary', pd.DataFrame())
        ratings = self.lb_data.get('ratings', pd.DataFrame())
        watchlist = self.lb_data.get('watchlist', pd.DataFrame())
        liked = self.lb_data.get('liked_films', pd.DataFrame())

        self.stats['basic'] = {
            'total_watched': len(watched),
            'total_rated': len(ratings),
            'total_liked': len(liked),
            'total_watchlist': len(watchlist),
            'total_diary_entries': len(diary),
            'avg_rating': round(ratings['Rating'].mean(), 2) if not ratings.empty else 0,
            'rewatches': int(diary['Rewatch'].notna().sum()) if not diary.empty else 0
        }

    def _calculate_genre_stats(self):
        """Calculate genre-related statistics (only for watched films)"""
        genre_counts = Counter()
        genre_ratings = {}

        for (title, year), metadata in self.tmdb_data.items():
            # Skip films not in watched list
            if not self.is_film_watched(title, year):
                continue

            genres = metadata.get('genres', [])

            # Get user rating for this film
            rating = self._get_film_rating(title, year)

            for genre in genres:
                genre_counts[genre] += 1

                if rating and rating > 0:
                    if genre not in genre_ratings:
                        genre_ratings[genre] = []
                    genre_ratings[genre].append(rating)

        # Top genres
        top_genres = genre_counts.most_common(config.TOP_GENRES_COUNT)

        # Favorite genres (by average rating)
        favorite_genres = []
        for genre, ratings_list in genre_ratings.items():
            if len(ratings_list) >= 3:  # Minimum 3 films
                avg_rating = sum(ratings_list) / len(ratings_list)
                favorite_genres.append({
                    'genre': genre,
                    'avg_rating': round(avg_rating, 2),
                    'count': len(ratings_list)
                })

        favorite_genres.sort(key=lambda x: x['avg_rating'], reverse=True)

        self.stats['genres'] = {
            'distribution': [{'genre': g, 'count': c} for g, c in top_genres],
            'favorites': favorite_genres[:10],
            'total_unique': len(genre_counts)
        }

    def _calculate_actor_stats(self):
        """Calculate actor-related statistics with film lists (only for watched films)"""
        actor_counts = Counter()
        actor_ratings = {}
        actor_films = defaultdict(list)  # Track films per actor
        actor_liked_counts = Counter()  # Track liked films per actor
        actor_profiles = {}  # Store profile_path per actor

        for (title, year), metadata in self.tmdb_data.items():
            # Skip films not in watched list
            if not self.is_film_watched(title, year):
                continue

            actors = metadata.get('actors', [])
            rating = self._get_film_rating(title, year)
            is_liked = self.is_film_liked(title, year)

            for actor_info in actors:
                actor_name = actor_info['name']
                actor_counts[actor_name] += 1

                # Store profile path (first one found)
                if actor_name not in actor_profiles and actor_info.get('profile_path'):
                    actor_profiles[actor_name] = actor_info['profile_path']

                if is_liked:
                    actor_liked_counts[actor_name] += 1

                # Store film info for this actor
                actor_films[actor_name].append({
                    'title': title,
                    'year': year,
                    'rating': rating if rating else None,
                    'liked': is_liked,
                    'poster_path': metadata.get('poster_path'),
                    'character': actor_info.get('character', '')
                })

                if rating and rating > 0:
                    if actor_name not in actor_ratings:
                        actor_ratings[actor_name] = []
                    actor_ratings[actor_name].append(rating)

        # Top actors by appearance
        top_actors = actor_counts.most_common(config.TOP_ACTORS_COUNT)

        # Favorite actors (by average rating, min 3 films)
        favorite_actors = []
        for actor, ratings_list in actor_ratings.items():
            if len(ratings_list) >= 3:
                avg_rating = sum(ratings_list) / len(ratings_list)
                favorite_actors.append({
                    'name': actor,
                    'avg_rating': round(avg_rating, 2),
                    'count': len(ratings_list)
                })

        favorite_actors.sort(key=lambda x: x['avg_rating'], reverse=True)

        # Build top actors with their film lists
        top_actors_with_films = []
        for actor_name, count in top_actors:
            films = sorted(actor_films[actor_name], key=lambda x: x['year'], reverse=True)
            liked_count = actor_liked_counts[actor_name]
            avg_rating = 0
            if actor_name in actor_ratings:
                avg_rating = round(sum(actor_ratings[actor_name]) / len(actor_ratings[actor_name]), 2)
            top_actors_with_films.append({
                'name': actor_name,
                'count': count,
                'liked_count': liked_count,
                'like_ratio': round(liked_count / count * 100, 1) if count > 0 else 0,
                'avg_rating': avg_rating,
                'profile_path': actor_profiles.get(actor_name),
                'films': films
            })

        self.stats['actors'] = {
            'top_by_count': top_actors_with_films,
            'favorites': favorite_actors[:15],
            'total_unique': len(actor_counts)
        }

    def _calculate_director_stats(self):
        """Calculate director-related statistics with film lists (only for watched films)"""
        director_counts = Counter()
        director_ratings = {}
        director_films = defaultdict(list)
        director_liked_counts = Counter()
        director_profiles = {}

        for (title, year), metadata in self.tmdb_data.items():
            if not self.is_film_watched(title, year):
                continue

            directors = metadata.get('directors', [])
            director_profile_map = metadata.get('director_profiles', {})
            rating = self._get_film_rating(title, year)
            is_liked = self.is_film_liked(title, year)

            for director in directors:
                director_counts[director] += 1

                if director not in director_profiles and director_profile_map.get(director):
                    director_profiles[director] = director_profile_map[director]

                if is_liked:
                    director_liked_counts[director] += 1

                director_films[director].append({
                    'title': title,
                    'year': year,
                    'rating': rating if rating else None,
                    'liked': is_liked,
                    'poster_path': metadata.get('poster_path')
                })

                if rating and rating > 0:
                    if director not in director_ratings:
                        director_ratings[director] = []
                    director_ratings[director].append(rating)

        # Top directors by film count
        top_directors = director_counts.most_common(config.TOP_DIRECTORS_COUNT)

        # Favorite directors (by average rating, min 2 films)
        favorite_directors = []
        for director, ratings_list in director_ratings.items():
            if len(ratings_list) >= 2:
                avg_rating = sum(ratings_list) / len(ratings_list)
                favorite_directors.append({
                    'name': director,
                    'avg_rating': round(avg_rating, 2),
                    'count': len(ratings_list)
                })

        favorite_directors.sort(key=lambda x: x['avg_rating'], reverse=True)

        # Build top directors with their film lists
        top_directors_with_films = []
        for director_name, count in top_directors:
            films = sorted(director_films[director_name], key=lambda x: x['year'], reverse=True)
            liked_count = director_liked_counts[director_name]
            avg_rating = 0
            if director_name in director_ratings:
                avg_rating = round(sum(director_ratings[director_name]) / len(director_ratings[director_name]), 2)
            top_directors_with_films.append({
                'name': director_name,
                'count': count,
                'liked_count': liked_count,
                'like_ratio': round(liked_count / count * 100, 1) if count > 0 else 0,
                'avg_rating': avg_rating,
                'profile_path': director_profiles.get(director_name),
                'films': films
            })

        self.stats['directors'] = {
            'top_by_count': top_directors_with_films,
            'favorites': favorite_directors[:10],
            'total_unique': len(director_counts)
        }

    def _calculate_runtime_stats(self):
        """Calculate runtime-related statistics (only for watched films)"""
        runtimes = []
        runtime_distribution = {'<90': 0, '90-120': 0, '120-150': 0, '150-180': 0, '180+': 0}
        shortest_film = {'title': 'N/A', 'runtime': 999999}
        longest_film = {'title': 'N/A', 'runtime': 0}

        for (title, year), metadata in self.tmdb_data.items():
            # Skip films not in watched list
            if not self.is_film_watched(title, year):
                continue

            runtime = metadata.get('runtime')
            if runtime and runtime > 0:
                runtimes.append(runtime)

                # Track shortest and longest
                if runtime < shortest_film['runtime']:
                    shortest_film = {'title': title, 'year': year, 'runtime': runtime}
                if runtime > longest_film['runtime']:
                    longest_film = {'title': title, 'year': year, 'runtime': runtime}

                # Categorize
                if runtime < 90:
                    runtime_distribution['<90'] += 1
                elif runtime < 120:
                    runtime_distribution['90-120'] += 1
                elif runtime < 150:
                    runtime_distribution['120-150'] += 1
                elif runtime < 180:
                    runtime_distribution['150-180'] += 1
                else:
                    runtime_distribution['180+'] += 1

        total_minutes = sum(runtimes) if runtimes else 0
        total_hours = round(total_minutes / 60)

        self.stats['runtime'] = {
            'average': round(sum(runtimes) / len(runtimes), 1) if runtimes else 0,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'shortest': shortest_film if shortest_film['runtime'] != 999999 else {'title': 'N/A', 'runtime': 0},
            'longest': longest_film,
            'min_runtime': min(runtimes) if runtimes else 0,
            'max_runtime': max(runtimes) if runtimes else 0,
            'distribution': runtime_distribution
        }

    def _calculate_country_language_stats(self):
        """Calculate country and language statistics (only for watched films)"""
        country_counts = Counter()
        language_counts = Counter()

        for (title, year), metadata in self.tmdb_data.items():
            # Skip films not in watched list
            if not self.is_film_watched(title, year):
                continue

            countries = metadata.get('production_countries', [])
            for country in countries:
                country_counts[country] += 1

            language = metadata.get('original_language')
            if language:
                language_counts[language] += 1

        top_countries = country_counts.most_common(config.TOP_COUNTRIES_COUNT)
        top_languages = language_counts.most_common(config.TOP_LANGUAGES_COUNT)

        self.stats['geography'] = {
            'top_countries': [{'country': c, 'count': count} for c, count in top_countries],
            'top_languages': [{'language': l, 'count': count} for l, count in top_languages],
            'total_countries': len(country_counts),
            'total_languages': len(language_counts)
        }

    def _calculate_rating_trends(self):
        """Calculate how ratings evolve over time"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty or 'Rating' not in diary.columns:
            self.stats['rating_trends'] = {'monthly': [], 'yearly': []}
            return

        # Filter out entries without ratings
        rated_diary = diary[diary['Rating'].notna()].copy()

        if rated_diary.empty:
            self.stats['rating_trends'] = {'monthly': [], 'yearly': []}
            return

        # Monthly average ratings
        rated_diary['month'] = rated_diary['Watched Date'].dt.to_period('M')
        monthly = rated_diary.groupby('month')['Rating'].mean()

        # Yearly average ratings
        rated_diary['year'] = rated_diary['Watched Date'].dt.year
        yearly = rated_diary.groupby('year')['Rating'].mean()

        self.stats['rating_trends'] = {
            'monthly': [{'month': str(m), 'avg_rating': round(r, 2)} for m, r in monthly.items()],
            'yearly': [{'year': int(y), 'avg_rating': round(r, 2)} for y, r in yearly.items()]
        }

    def _calculate_genre_rating_correlation(self):
        """Calculate correlation between genres and ratings"""
        genre_rating_matrix = {}

        for (title, year), metadata in self.tmdb_data.items():
            genres = metadata.get('genres', [])
            rating = self._get_film_rating(title, year)

            if rating and rating > 0:
                # Round rating to nearest 0.5
                rating_bucket = round(rating * 2) / 2

                for genre in genres:
                    if genre not in genre_rating_matrix:
                        genre_rating_matrix[genre] = Counter()
                    genre_rating_matrix[genre][rating_bucket] += 1

        self.stats['genre_rating_correlation'] = genre_rating_matrix

    def _calculate_tag_stats(self):
        """Calculate statistics from user tags"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty or 'Tags' not in diary.columns:
            self.stats['tags'] = {'top_tags': [], 'total': 0}
            return

        tag_counts = Counter()

        for tags in diary['Tags'].dropna():
            if isinstance(tags, str):
                # Split by comma
                tag_list = [t.strip() for t in tags.split(',')]
                tag_counts.update(tag_list)

        top_tags = tag_counts.most_common(20)

        self.stats['tags'] = {
            'top_tags': [{'tag': t, 'count': c} for t, c in top_tags],
            'total': len(tag_counts)
        }

    def _calculate_temporal_stats(self):
        """Calculate temporal viewing patterns"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty:
            self.stats['temporal'] = {}
            return

        # Watch activity by year
        diary['watch_year'] = diary['Watched Date'].dt.year
        yearly_counts = diary['watch_year'].value_counts().sort_index()

        # Watch activity by month (last 24 months)
        diary['watch_month'] = diary['Watched Date'].dt.to_period('M')
        monthly_counts = diary.groupby('watch_month').size().tail(24)

        # Watch activity by weekday
        diary['weekday'] = diary['Watched Date'].dt.day_name()
        weekday_counts = diary['weekday'].value_counts()

        self.stats['temporal'] = {
            'yearly': [{'year': int(y), 'count': int(c)} for y, c in yearly_counts.items()],
            'monthly': [{'month': str(m), 'count': int(c)} for m, c in monthly_counts.items()],
            'by_weekday': [{'day': d, 'count': int(c)} for d, c in weekday_counts.items()]
        }

    def _get_film_rating(self, title: str, year: int) -> float:
        """Get user rating for a specific film (O(1) dict lookup)"""
        return self.rating_dict.get((title, year), 0)

    def get_top_rated_films(self, count: int = 20) -> List[Dict]:
        """Get top rated films (5 stars)"""
        ratings = self.lb_data.get('ratings', pd.DataFrame())

        if ratings.empty:
            return []

        top = ratings[ratings['Rating'] == 5.0][['Name', 'Year']].head(count)
        return top.to_dict('records')

    def get_recent_diary(self, count: int = 10) -> List[Dict]:
        """Get recent diary entries"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty:
            return []

        recent = diary.sort_values('Watched Date', ascending=False).head(count)
        recent = recent[['Name', 'Year', 'Rating', 'Watched Date', 'Rewatch']].copy()
        recent['Watched Date'] = recent['Watched Date'].dt.strftime('%Y-%m-%d')

        return recent.to_dict('records')

    def _calculate_yearly_breakdown(self):
        """Calculate detailed stats for last full year and current year"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty:
            self.stats['yearly_breakdown'] = {}
            return

        current_year = datetime.now().year
        last_full_year = current_year - 1

        self.stats['yearly_breakdown'] = {
            'last_full_year': self._get_year_stats(last_full_year),
            'current_year': self._get_year_stats(current_year),
            'last_full_year_value': last_full_year,
            'current_year_value': current_year
        }

    def _get_year_stats(self, year: int) -> Dict:
        """Get comprehensive stats for a specific year"""
        diary = self.lb_data.get('diary', pd.DataFrame())
        ratings = self.lb_data.get('ratings', pd.DataFrame())

        if diary.empty:
            return self._empty_year_stats()

        # Filter diary entries for this year
        year_diary = diary[diary['Watched Date'].dt.year == year].copy()

        if year_diary.empty:
            return self._empty_year_stats()

        # Basic counts
        total_films = len(year_diary)

        # Count liked films for this year
        liked_count = 0
        for _, row in year_diary.iterrows():
            if self.is_film_liked(row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0):
                liked_count += 1

        # Get films with ratings
        year_diary_rated = year_diary[year_diary['Rating'].notna()].copy()

        # Top 8 highest rated (2 rows of 4)
        top_rated = []
        if not year_diary_rated.empty:
            top_sorted = year_diary_rated.nlargest(8, 'Rating')
            for _, row in top_sorted.iterrows():
                title, yr = row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0
                metadata = self.tmdb_data.get((title, yr), {})
                top_rated.append({
                    'title': title,
                    'year': yr,
                    'rating': float(row['Rating']),
                    'poster_path': metadata.get('poster_path'),
                    'liked': self.is_film_liked(title, yr)
                })

        # Bottom 8 lowest rated (minimum 8 entries for full display)
        bottom_rated = []
        if len(year_diary_rated) >= 8:
            bottom_sorted = year_diary_rated.nsmallest(8, 'Rating')
            for _, row in bottom_sorted.iterrows():
                title, yr = row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0
                metadata = self.tmdb_data.get((title, yr), {})
                bottom_rated.append({
                    'title': title,
                    'year': yr,
                    'rating': float(row['Rating']),
                    'poster_path': metadata.get('poster_path'),
                    'liked': self.is_film_liked(title, yr)
                })

        # Most active month
        year_diary['month'] = year_diary['Watched Date'].dt.month
        month_counts = year_diary['month'].value_counts()
        most_active_month = int(month_counts.idxmax()) if not month_counts.empty else 0
        most_active_month_count = int(month_counts.max()) if not month_counts.empty else 0

        # Single pass: count actors, directors, genres AND build film lists
        actor_counts = Counter()
        director_counts = Counter()
        genre_counts = Counter()
        actor_year_films = defaultdict(list)
        director_year_films = defaultdict(list)

        for _, row in year_diary.iterrows():
            title, yr = row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0
            metadata = self.tmdb_data.get((title, yr), {})
            film_info = {
                'title': title, 'year': yr,
                'poster_path': metadata.get('poster_path'),
                'rating': float(row['Rating']) if pd.notna(row['Rating']) else None
            }

            for actor_info in metadata.get('actors', []):
                name = actor_info['name']
                actor_counts[name] += 1
                actor_year_films[name].append(film_info)

            for director in metadata.get('directors', []):
                director_counts[director] += 1
                director_year_films[director].append(film_info)

            for genre in metadata.get('genres', []):
                genre_counts[genre] += 1

        # Get top actor with films (already built)
        top_actor = None
        if actor_counts:
            top_actor_name, top_actor_count = actor_counts.most_common(1)[0]
            top_actor = {
                'name': top_actor_name,
                'count': top_actor_count,
                'films': actor_year_films[top_actor_name][:10]
            }

        # Get top director with films (already built)
        top_director = None
        if director_counts:
            top_director_name, top_director_count = director_counts.most_common(1)[0]
            top_director = {
                'name': top_director_name,
                'count': top_director_count,
                'films': director_year_films[top_director_name]
            }

        # Genre distribution for this year
        genre_distribution = [{'genre': g, 'count': c} for g, c in genre_counts.most_common(10)]

        # Average rating for the year
        avg_rating = round(year_diary_rated['Rating'].mean(), 2) if not year_diary_rated.empty else 0

        # Monthly breakdown
        monthly_counts = year_diary.groupby(year_diary['Watched Date'].dt.month).size()
        monthly_breakdown = [{'month': int(m), 'count': int(c)} for m, c in monthly_counts.items()]

        return {
            'total_films': total_films,
            'total_liked': liked_count,
            'total_rated': len(year_diary_rated),
            'avg_rating': avg_rating,
            'top_rated': top_rated,
            'bottom_rated': bottom_rated,
            'top_actor': top_actor,
            'top_director': top_director,
            'genre_distribution': genre_distribution,
            'most_active_month': most_active_month,
            'most_active_month_count': most_active_month_count,
            'monthly_breakdown': monthly_breakdown
        }

    def _empty_year_stats(self) -> Dict:
        """Return empty year stats structure"""
        return {
            'total_films': 0,
            'total_liked': 0,
            'total_rated': 0,
            'avg_rating': 0,
            'top_rated': [],
            'bottom_rated': [],
            'top_actor': None,
            'top_director': None,
            'genre_distribution': [],
            'most_active_month': 0,
            'most_active_month_count': 0,
            'monthly_breakdown': []
        }

    def _calculate_liked_stats(self):
        """Calculate statistics specifically for liked films"""
        liked_films = self.lb_data.get('liked_films', pd.DataFrame())

        if liked_films.empty:
            self.stats['liked'] = {
                'top_actors': [],
                'top_directors': [],
                'top_genres': [],
                'total': 0
            }
            return

        # Single pass: count and build film lists per actor/director
        actor_counts = Counter()
        director_counts = Counter()
        genre_counts = Counter()
        actor_films = defaultdict(list)
        director_films = defaultdict(list)

        for _, row in liked_films.iterrows():
            title = row['Name']
            year = int(row['Year']) if pd.notna(row['Year']) else 0
            metadata = self.tmdb_data.get((title, year), {})
            rating = self._get_film_rating(title, year)
            film_info = {
                'title': title, 'year': year,
                'poster_path': metadata.get('poster_path'),
                'rating': rating if rating else None
            }

            for actor_info in metadata.get('actors', []):
                name = actor_info['name']
                actor_counts[name] += 1
                actor_films[name].append(film_info)

            for director in metadata.get('directors', []):
                director_counts[director] += 1
                director_films[director].append(film_info)

            for genre in metadata.get('genres', []):
                genre_counts[genre] += 1

        # Build top lists directly from pre-built mappings
        top_liked_actors = [
            {'name': name, 'count': count,
             'films': sorted(actor_films[name], key=lambda x: x['year'], reverse=True)}
            for name, count in actor_counts.most_common(15)
        ]

        top_liked_directors = [
            {'name': name, 'count': count,
             'films': sorted(director_films[name], key=lambda x: x['year'], reverse=True)}
            for name, count in director_counts.most_common(15)
        ]

        top_liked_genres = [{'genre': g, 'count': c} for g, c in genre_counts.most_common(10)]

        self.stats['liked'] = {
            'top_actors': top_liked_actors,
            'top_directors': top_liked_directors,
            'top_genres': top_liked_genres,
            'total': len(liked_films)
        }

    def _calculate_rating_distribution(self):
        """Calculate distribution of ratings (how many films at each star level)"""
        ratings = self.lb_data.get('ratings', pd.DataFrame())

        if ratings.empty:
            self.stats['rating_distribution'] = []
            return

        # Count ratings by star level (0.5 to 5.0)
        rating_counts = {}
        for rating in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            count = len(ratings[ratings['Rating'] == rating])
            rating_counts[rating] = count

        self.stats['rating_distribution'] = [
            {'rating': r, 'count': c} for r, c in rating_counts.items()
        ]

    def _calculate_decade_stats(self):
        """Calculate decade-based statistics for films watched"""
        watched = self.lb_data.get('watched', pd.DataFrame())

        if watched.empty:
            self.stats['decades'] = {'distribution': [], 'top_per_decade': {}}
            return

        decade_counts = Counter()
        decade_films = defaultdict(list)
        decade_ratings = defaultdict(list)

        for _, row in watched.iterrows():
            title = row['Name']
            year = int(row['Year']) if pd.notna(row['Year']) else 0
            if year > 0:
                decade = (year // 10) * 10
                decade_counts[decade] += 1

                # Get rating and metadata
                rating = self._get_film_rating(title, year)
                metadata = self.tmdb_data.get((title, year), {})
                is_liked = self.is_film_liked(title, year)

                decade_films[decade].append({
                    'title': title,
                    'year': year,
                    'rating': rating if rating else None,
                    'liked': is_liked,
                    'poster_path': metadata.get('poster_path')
                })

                if rating and rating > 0:
                    decade_ratings[decade].append(rating)

        # Sort decades and create distribution
        decade_distribution = [
            {'decade': f"{d}s", 'count': c, 'decade_num': d}
            for d, c in sorted(decade_counts.items())
        ]

        # Get top 5 films per decade (by rating)
        top_per_decade = {}
        for decade, films in decade_films.items():
            rated_films = [f for f in films if f['rating']]
            sorted_films = sorted(rated_films, key=lambda x: (x['rating'], x['liked']), reverse=True)[:5]
            avg_rating = round(sum(decade_ratings[decade]) / len(decade_ratings[decade]), 2) if decade_ratings[decade] else 0
            top_per_decade[f"{decade}s"] = {
                'films': sorted_films,
                'total': decade_counts[decade],
                'avg_rating': avg_rating
            }

        # Find favorite decade (by average rating, min 10 films)
        favorite_decade = None
        best_avg = 0
        for decade, ratings_list in decade_ratings.items():
            if len(ratings_list) >= 10:
                avg = sum(ratings_list) / len(ratings_list)
                if avg > best_avg:
                    best_avg = avg
                    favorite_decade = f"{decade}s"

        self.stats['decades'] = {
            'distribution': decade_distribution,
            'top_per_decade': top_per_decade,
            'favorite_decade': favorite_decade,
            'favorite_decade_avg': round(best_avg, 2)
        }

    def _calculate_rewatch_stats(self):
        """Calculate rewatch statistics"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty or 'Rewatch' not in diary.columns:
            self.stats['rewatches'] = {'total': 0, 'films': [], 'most_rewatched': []}
            return

        # Find rewatched entries
        rewatches = diary[diary['Rewatch'] == 'Yes'].copy() if 'Rewatch' in diary.columns else pd.DataFrame()

        if rewatches.empty:
            self.stats['rewatches'] = {'total': 0, 'films': [], 'most_rewatched': []}
            return

        # Count rewatches per film
        rewatch_counts = Counter()
        for _, row in rewatches.iterrows():
            key = (row['Name'], int(row['Year']) if pd.notna(row['Year']) else 0)
            rewatch_counts[key] += 1

        # Get most rewatched films
        most_rewatched = []
        for (title, year), count in rewatch_counts.most_common(10):
            metadata = self.tmdb_data.get((title, year), {})
            rating = self._get_film_rating(title, year)
            most_rewatched.append({
                'title': title,
                'year': year,
                'rewatch_count': count + 1,  # +1 for original watch
                'rating': rating if rating else None,
                'liked': self.is_film_liked(title, year),
                'poster_path': metadata.get('poster_path')
            })

        self.stats['rewatches'] = {
            'total': len(rewatches),
            'unique_films': len(rewatch_counts),
            'most_rewatched': most_rewatched
        }

    def _calculate_journey_stats(self):
        """Calculate film journey milestones and streaks"""
        diary = self.lb_data.get('diary', pd.DataFrame())

        if diary.empty:
            self.stats['journey'] = {}
            return

        # Sort by watch date
        diary_sorted = diary.sort_values('Watched Date').reset_index(drop=True)

        # First film ever
        first_entry = diary_sorted.iloc[0]
        first_film = {
            'title': first_entry['Name'],
            'year': int(first_entry['Year']) if pd.notna(first_entry['Year']) else 0,
            'date': first_entry['Watched Date'].strftime('%B %d, %Y'),
            'poster_path': self.tmdb_data.get(
                (first_entry['Name'], int(first_entry['Year']) if pd.notna(first_entry['Year']) else 0), {}
            ).get('poster_path')
        }

        # Most recent film
        recent_entry = diary_sorted.iloc[-1]
        recent_film = {
            'title': recent_entry['Name'],
            'year': int(recent_entry['Year']) if pd.notna(recent_entry['Year']) else 0,
            'date': recent_entry['Watched Date'].strftime('%B %d, %Y'),
            'poster_path': self.tmdb_data.get(
                (recent_entry['Name'], int(recent_entry['Year']) if pd.notna(recent_entry['Year']) else 0), {}
            ).get('poster_path')
        }

        # Milestones (100th, 250th, 500th, 1000th, etc.)
        milestones = []
        milestone_numbers = [100, 250, 500, 750, 1000, 1500, 2000]
        for num in milestone_numbers:
            if len(diary_sorted) >= num:
                entry = diary_sorted.iloc[num - 1]
                milestones.append({
                    'number': num,
                    'title': entry['Name'],
                    'year': int(entry['Year']) if pd.notna(entry['Year']) else 0,
                    'date': entry['Watched Date'].strftime('%B %d, %Y'),
                    'poster_path': self.tmdb_data.get(
                        (entry['Name'], int(entry['Year']) if pd.notna(entry['Year']) else 0), {}
                    ).get('poster_path')
                })

        # Calculate streaks and records
        diary_sorted['date_only'] = diary_sorted['Watched Date'].dt.date
        daily_counts = diary_sorted.groupby('date_only').size()

        # Most films in a single day
        max_day = daily_counts.idxmax() if not daily_counts.empty else None
        max_day_count = int(daily_counts.max()) if not daily_counts.empty else 0

        # Most active month ever
        diary_sorted['month'] = diary_sorted['Watched Date'].dt.to_period('M')
        monthly_counts = diary_sorted.groupby('month').size()
        max_month = str(monthly_counts.idxmax()) if not monthly_counts.empty else None
        max_month_count = int(monthly_counts.max()) if not monthly_counts.empty else 0

        # Calculate longest streak (consecutive days watching)
        dates = sorted(set(diary_sorted['date_only']))
        longest_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        self.stats['journey'] = {
            'first_film': first_film,
            'recent_film': recent_film,
            'milestones': milestones,
            'total_diary_entries': len(diary_sorted),
            'max_day': str(max_day) if max_day else None,
            'max_day_count': max_day_count,
            'max_month': max_month,
            'max_month_count': max_month_count,
            'longest_streak': longest_streak,
            'days_since_first': (datetime.now().date() - dates[0]).days if dates else 0
        }

    def _calculate_five_star_films(self):
        """Get all 5-star rated films for the poster wall"""
        ratings = self.lb_data.get('ratings', pd.DataFrame())

        if ratings.empty:
            self.stats['five_star_films'] = []
            return

        five_stars = ratings[ratings['Rating'] == 5.0].copy()

        films = []
        for _, row in five_stars.iterrows():
            title = row['Name']
            year = int(row['Year']) if pd.notna(row['Year']) else 0
            metadata = self.tmdb_data.get((title, year), {})
            films.append({
                'title': title,
                'year': year,
                'poster_path': metadata.get('poster_path'),
                'liked': self.is_film_liked(title, year)
            })

        # Sort by year descending
        films.sort(key=lambda x: x['year'], reverse=True)

        self.stats['five_star_films'] = films

    def _calculate_fun_facts(self):
        """Calculate personalized fun facts and insights"""
        watched = self.lb_data.get('watched', pd.DataFrame())
        diary = self.lb_data.get('diary', pd.DataFrame())
        runtime = self.stats.get('runtime', {})
        actors = self.stats.get('actors', {}).get('top_by_count', [])
        directors = self.stats.get('directors', {}).get('top_by_count', [])
        decades = self.stats.get('decades', {})

        fun_facts = []

        # Total watch time in different units
        total_hours = runtime.get('total_hours', 0)
        if total_hours > 0:
            days = round(total_hours / 24, 1)
            weeks = round(total_hours / 168, 1)
            fun_facts.append({
                'icon': '⏰',
                'text': f"You've spent {total_hours:,} hours watching films",
                'subtext': f"That's {days} days or {weeks} weeks of your life!"
            })

        # Time spent with favorite actor
        if actors:
            top_actor = actors[0]
            actor_films = top_actor.get('films', [])
            actor_runtime = 0
            for film in actor_films:
                title, year = film['title'], film['year']
                metadata = self.tmdb_data.get((title, year), {})
                actor_runtime += metadata.get('runtime', 0)
            if actor_runtime > 0:
                fun_facts.append({
                    'icon': '🎭',
                    'text': f"You've watched {round(actor_runtime / 60, 1)} hours of {top_actor['name']}",
                    'subtext': f"Across {top_actor['count']} films"
                })

        # Director dedication
        if directors:
            top_director = directors[0]
            fun_facts.append({
                'icon': '🎬',
                'text': f"Your most watched director is {top_director['name']}",
                'subtext': f"{top_director['count']} films, {top_director.get('liked_count', 0)} liked"
            })

        # Decade preference
        favorite_decade = decades.get('favorite_decade')
        if favorite_decade:
            fun_facts.append({
                'icon': '📅',
                'text': f"You rate {favorite_decade} films highest",
                'subtext': f"Average rating: {decades.get('favorite_decade_avg', 0)}★"
            })

        # Oldest and newest film watched
        oldest_film = None
        newest_film = None
        for _, row in watched.iterrows():
            year = int(row['Year']) if pd.notna(row['Year']) else 0
            if year > 1800:  # Valid year
                if oldest_film is None or year < oldest_film['year']:
                    oldest_film = {'title': row['Name'], 'year': year}
                if newest_film is None or year > newest_film['year']:
                    newest_film = {'title': row['Name'], 'year': year}

        if oldest_film and newest_film:
            span = newest_film['year'] - oldest_film['year']
            fun_facts.append({
                'icon': '📽️',
                'text': f"Your films span {span} years of cinema",
                'subtext': f"From {oldest_film['year']} to {newest_film['year']}"
            })

        # Average film age
        current_year = datetime.now().year
        ages = []
        for _, row in watched.iterrows():
            year = int(row['Year']) if pd.notna(row['Year']) else 0
            if year > 1800:
                ages.append(current_year - year)

        if ages:
            avg_age = round(sum(ages) / len(ages), 1)
            fun_facts.append({
                'icon': '🎞️',
                'text': f"Average age of films you watch: {avg_age} years",
                'subtext': "A mix of classics and contemporary!"
            })

        # Films per year average
        if not diary.empty:
            years_active = diary['Watched Date'].dt.year.nunique()
            if years_active > 0:
                avg_per_year = round(len(diary) / years_active, 1)
                fun_facts.append({
                    'icon': '📊',
                    'text': f"You average {avg_per_year} films per year",
                    'subtext': f"Across {years_active} years of logging"
                })

        self.stats['fun_facts'] = fun_facts

    def _calculate_crew_stats(self):
        """Calculate stats for composers, cinematographers, and writers"""
        crew_roles = {
            'composers': 'composers',
            'cinematographers': 'cinematographers',
            'writers': 'writers'
        }

        for stat_key, metadata_key in crew_roles.items():
            person_counts = Counter()
            person_films = defaultdict(list)
            person_liked = Counter()
            person_profiles = {}

            for (title, year), metadata in self.tmdb_data.items():
                if not self.is_film_watched(title, year):
                    continue

                crew_list = metadata.get(metadata_key, [])
                rating = self._get_film_rating(title, year)
                is_liked = self.is_film_liked(title, year)

                for person in crew_list:
                    name = person.get('name') if isinstance(person, dict) else person
                    person_counts[name] += 1

                    if isinstance(person, dict) and person.get('profile_path') and name not in person_profiles:
                        person_profiles[name] = person['profile_path']

                    if is_liked:
                        person_liked[name] += 1

                    person_films[name].append({
                        'title': title,
                        'year': year,
                        'rating': rating if rating else None,
                        'liked': is_liked,
                        'poster_path': metadata.get('poster_path')
                    })

            top_people = []
            for name, count in person_counts.most_common(10):
                films = sorted(person_films[name], key=lambda x: x['year'], reverse=True)
                liked_count = person_liked[name]
                ratings_list = [f['rating'] for f in films if f['rating']]
                avg_rating = round(sum(ratings_list) / len(ratings_list), 2) if ratings_list else 0
                top_people.append({
                    'name': name,
                    'count': count,
                    'liked_count': liked_count,
                    'like_ratio': round(liked_count / count * 100, 1) if count > 0 else 0,
                    'avg_rating': avg_rating,
                    'profile_path': person_profiles.get(name),
                    'films': films
                })

            self.stats[stat_key] = {
                'top_by_count': top_people,
                'total_unique': len(person_counts)
            }

    def _calculate_studio_stats(self):
        """Calculate production studio/company statistics"""
        studio_counts = Counter()
        studio_films = defaultdict(list)
        studio_liked = Counter()
        studio_logos = {}

        for (title, year), metadata in self.tmdb_data.items():
            if not self.is_film_watched(title, year):
                continue

            companies = metadata.get('production_companies', [])
            rating = self._get_film_rating(title, year)
            is_liked = self.is_film_liked(title, year)

            for company in companies:
                # Handle both old (string) and new (dict) format
                if isinstance(company, dict):
                    company_name = company['name']
                    if company.get('logo_path') and company_name not in studio_logos:
                        studio_logos[company_name] = company['logo_path']
                else:
                    company_name = company

                studio_counts[company_name] += 1

                if is_liked:
                    studio_liked[company_name] += 1

                studio_films[company_name].append({
                    'title': title,
                    'year': year,
                    'rating': rating if rating else None,
                    'liked': is_liked,
                    'poster_path': metadata.get('poster_path')
                })

        top_studios = []
        for name, count in studio_counts.most_common(10):
            films = sorted(studio_films[name], key=lambda x: x['year'], reverse=True)
            liked_count = studio_liked[name]
            ratings_list = [f['rating'] for f in films if f['rating']]
            avg_rating = round(sum(ratings_list) / len(ratings_list), 2) if ratings_list else 0
            top_studios.append({
                'name': name,
                'count': count,
                'liked_count': liked_count,
                'avg_rating': avg_rating,
                'logo_path': studio_logos.get(name),
                'films': films
            })

        self.stats['studios'] = {
            'top_by_count': top_studios,
            'total_unique': len(studio_counts)
        }

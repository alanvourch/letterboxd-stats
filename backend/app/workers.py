"""Background job runner for the pipeline."""
import asyncio
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Callable

from app.models import JobState, JobStatus

# Global job storage
jobs: Dict[str, JobState] = {}
executor = ThreadPoolExecutor(max_workers=2)


def _run_pipeline(job: JobState, shared_cache: dict, on_cache_dirty: Callable, on_force_save: Callable = None):
    """Run the full pipeline synchronously."""
    from app.pipeline.data_loader import load_all_data
    from app.pipeline.tmdb_enricher import TMDBEnricher
    from app.pipeline.stats_calculator import StatsCalculator
    from app.pipeline.chart_generator import ChartGenerator
    from app.pipeline.html_generator import HTMLGenerator

    try:
        # Step 1: Load data (0-20%)
        job.status = JobStatus.LOADING
        job.message = "Loading Letterboxd data..."
        job.percent = 5

        def on_load_progress(msg: str, pct: float):
            job.message = msg
            job.percent = int(5 + pct * 0.15)

        data = load_all_data(job.data_dir, on_progress=on_load_progress)
        job.percent = 20

        # Step 2: Enrich with TMDB (20-70%)
        job.status = JobStatus.ENRICHING
        job.message = "Fetching TMDB metadata..."

        def on_enrich_progress(msg: str, pct: float):
            job.message = msg
            # Map 0-100 to 20-70
            job.percent = int(20 + pct * 0.5)

        enricher = TMDBEnricher(
            shared_cache=shared_cache,
            on_progress=on_enrich_progress,
            on_cache_dirty=on_cache_dirty
        )
        enriched_films = enricher.enrich_films(data['watched'], data.get('diary'))

        # Save cache immediately after enrichment
        new_count = enricher.get_new_cache_count()
        if new_count > 0:
            on_cache_dirty(new_count)
        if on_force_save:
            on_force_save()

        job.percent = 70

        # Step 3: Calculate stats (70-85%)
        job.status = JobStatus.CALCULATING
        job.message = "Calculating statistics..."
        job.percent = 75

        letterboxd_data = {
            'watched': data['watched'],
            'diary': data.get('diary'),
            'ratings': data.get('ratings'),
            'watchlist': data.get('watchlist'),
            'liked_films': data.get('likes'),
        }
        calculator = StatsCalculator(letterboxd_data, enriched_films)
        stats = calculator.calculate_all()
        job.percent = 85

        # Step 4: Generate charts (85-90%)
        job.message = "Generating charts..."
        job.percent = 87
        chart_gen = ChartGenerator(stats)
        charts = chart_gen.generate_all_charts()
        job.percent = 90

        # Step 5: Generate HTML (90-100%)
        job.status = JobStatus.GENERATING
        job.message = "Building dashboard..."
        job.percent = 95
        html_gen = HTMLGenerator(stats, charts)
        html = html_gen.generate()

        # Store results
        job.stats_json = json.dumps(stats, default=str)
        job.charts_json = json.dumps(charts)
        job.html = html

        job.status = JobStatus.COMPLETE
        job.message = "Dashboard ready!"
        job.percent = 100

    except Exception as e:
        job.status = JobStatus.ERROR
        job.error = str(e)
        job.message = f"Error: {e}"
        import traceback
        traceback.print_exc()

    finally:
        # Always save cache before cleanup
        try:
            if on_force_save:
                on_force_save()
        except:
            pass
        # Cleanup temp directory
        try:
            shutil.rmtree(job.data_dir, ignore_errors=True)
        except:
            pass


async def start_pipeline(job: JobState, shared_cache: dict, on_cache_dirty: Callable, on_force_save: Callable = None):
    """Start pipeline in background thread."""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_pipeline, job, shared_cache, on_cache_dirty, on_force_save)

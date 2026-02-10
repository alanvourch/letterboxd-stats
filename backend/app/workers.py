"""Background job runner for the pipeline."""
import asyncio
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, Callable

from app.models import JobState, JobStatus
from app import config

# Global job storage
jobs: Dict[str, JobState] = {}
executor = ThreadPoolExecutor(max_workers=2)


def _run_pipeline(job: JobState):
    """Run the full pipeline synchronously."""
    from app.pipeline.data_loader import load_all_data
    from app.pipeline.supabase_enricher import SupabaseEnricher
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

        # Step 2: Enrich with Supabase + TMDB fallback (20-70%)
        job.status = JobStatus.ENRICHING
        job.message = "Looking up film metadata..."

        def on_enrich_progress(msg: str, pct: float):
            job.message = msg
            # Map 0-100 to 20-70
            job.percent = int(20 + pct * 0.5)

        enricher = SupabaseEnricher(on_progress=on_enrich_progress)
        enriched_films = enricher.enrich_films(data['watched'], data.get('diary'))

        # Store TMDB fallback list for user to see what's missing from Supabase
        job.tmdb_fallback_films = json.dumps(enricher.get_tmdb_fallback_films())

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
        # Cleanup temp directory
        try:
            shutil.rmtree(job.data_dir, ignore_errors=True)
        except:
            pass


async def start_pipeline(job: JobState):
    """Start pipeline in background thread."""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_pipeline, job)


async def cleanup_old_jobs():
    """Periodically clean up old completed/error jobs."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=config.JOB_EXPIRY_MINUTES)
        expired = [
            jid for jid, job in jobs.items()
            if job.status in (JobStatus.COMPLETE, JobStatus.ERROR)
            and job.created_at < cutoff
        ]
        for jid in expired:
            del jobs[jid]

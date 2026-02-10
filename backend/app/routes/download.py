"""Download endpoints for job results."""
import csv
import io
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response

from app.models import JobStatus
from app.workers import jobs

router = APIRouter()


@router.get("/result/{job_id}/json")
async def get_result_json(job_id: str):
    """Get job results as JSON (stats + charts)."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]

    if job.status == JobStatus.ERROR:
        raise HTTPException(500, job.error)

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(400, "Job not complete")

    return JSONResponse({
        "stats": json.loads(job.stats_json) if job.stats_json else {},
        "charts": json.loads(job.charts_json) if job.charts_json else {}
    })


@router.get("/result/{job_id}/html")
async def get_result_html(job_id: str):
    """Get job results as downloadable HTML."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]

    if job.status == JobStatus.ERROR:
        raise HTTPException(500, job.error)

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(400, "Job not complete")

    return HTMLResponse(
        content=job.html,
        headers={
            "Content-Disposition": "attachment; filename=letterboxd_stats.html"
        }
    )


@router.get("/result/{job_id}/missing")
async def get_missing_films(job_id: str):
    """Get list of films not found in Supabase (needed TMDB fallback)."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(400, "Job not complete")

    films = json.loads(job.tmdb_fallback_films) if job.tmdb_fallback_films else []
    tmdb_found = sum(1 for f in films if f.get('tmdb_found'))
    tmdb_not_found = len(films) - tmdb_found
    return JSONResponse({
        "count": len(films),
        "tmdb_found": tmdb_found,
        "tmdb_not_found": tmdb_not_found,
        "films": films
    })


@router.get("/result/{job_id}/missing/csv")
async def get_missing_films_csv(job_id: str):
    """Download missing films as CSV."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(400, "Job not complete")

    films = json.loads(job.tmdb_fallback_films) if job.tmdb_fallback_films else []

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['title', 'year', 'tmdb_found', 'supabase_miss_reason'])
    writer.writeheader()
    for film in sorted(films, key=lambda x: (x.get('year', 0), x.get('title', ''))):
        writer.writerow({
            'title': film.get('title', ''),
            'year': film.get('year', ''),
            'tmdb_found': film.get('tmdb_found', False),
            'supabase_miss_reason': film.get('supabase_miss_reason', ''),
        })

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=missing_from_supabase.csv"}
    )

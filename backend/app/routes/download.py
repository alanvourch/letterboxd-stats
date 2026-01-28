"""Download endpoints for job results."""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

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

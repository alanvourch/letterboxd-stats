"""SSE status endpoint for job progress."""
import asyncio
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models import JobStatus
from app.workers import jobs

router = APIRouter()


@router.get("/status/{job_id}")
async def job_status(job_id: str):
    """Stream job progress via Server-Sent Events."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    async def event_stream():
        job = jobs[job_id]
        last_percent = -1

        while True:
            if job.percent != last_percent or job.status in (JobStatus.COMPLETE, JobStatus.ERROR):
                last_percent = job.percent

                if job.status == JobStatus.ERROR:
                    yield f"event: error\ndata: {json.dumps({'error': job.error})}\n\n"
                    break
                elif job.status == JobStatus.COMPLETE:
                    yield f"event: progress\ndata: {json.dumps({'step': 'complete', 'message': job.message, 'percent': 100})}\n\n"
                    yield f"event: complete\ndata: {json.dumps({'job_id': job_id})}\n\n"
                    break
                else:
                    yield f"event: progress\ndata: {json.dumps({'step': job.status.value, 'message': job.message, 'percent': job.percent})}\n\n"

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

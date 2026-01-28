"""Upload endpoint for Letterboxd ZIP files."""
import os
import uuid
import zipfile
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException

from app import config
from app.models import JobState, UploadResponse
from app.workers import jobs, start_pipeline

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_zip(zip_file: UploadFile = File(...)):
    """Upload a Letterboxd export ZIP file."""
    # Validate file size
    content = await zip_file.read()
    if len(content) > config.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large. Max size: {config.MAX_UPLOAD_SIZE_MB}MB")

    # Validate ZIP
    try:
        import io
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = zf.namelist()
            # Check for watched.csv (may be in root or subfolder)
            has_watched = any('watched.csv' in n for n in names)
            if not has_watched:
                raise HTTPException(400, "Invalid Letterboxd export: missing watched.csv")
    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid ZIP file")

    # Extract to temp directory
    temp_dir = tempfile.mkdtemp(prefix="lb_")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            zf.extractall(temp_dir)
    except Exception as e:
        raise HTTPException(500, f"Failed to extract ZIP: {e}")

    # Find data directory (might be root or subfolder)
    data_dir = temp_dir
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'watched.csv')):
            data_dir = item_path
            break

    # Create job
    job_id = str(uuid.uuid4())
    job = JobState(job_id=job_id, data_dir=data_dir)
    jobs[job_id] = job

    # Start pipeline
    await start_pipeline(job)

    return UploadResponse(job_id=job_id)

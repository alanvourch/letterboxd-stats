"""Pydantic models for API requests/responses."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    PENDING = "pending"
    LOADING = "loading"
    ENRICHING = "enriching"
    CALCULATING = "calculating"
    GENERATING = "generating"
    COMPLETE = "complete"
    ERROR = "error"


class JobState:
    """In-memory job state."""
    def __init__(self, job_id: str, data_dir: str):
        self.job_id = job_id
        self.data_dir = data_dir
        self.status = JobStatus.PENDING
        self.percent = 0
        self.message = "Waiting to start..."
        self.error: Optional[str] = None
        self.stats_json: Optional[str] = None
        self.charts_json: Optional[str] = None
        self.html: Optional[str] = None


class UploadResponse(BaseModel):
    job_id: str


class ProgressEvent(BaseModel):
    step: str
    message: str
    percent: int

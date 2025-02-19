# tldw_tube/api/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

class SummarizeRequest(BaseModel):
    url: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    video_id: Optional[str] = None
    title: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    webpage_url: Optional[str] = None
    summary: Optional[Dict] = None

class SummarizeResponse(BaseModel):
    success: bool = True
    error: str = ""
    video_id: str
    title: str
    thumbnail_url: HttpUrl
    aspect_ratio: float
    webpage_url: str
    summary: Dict

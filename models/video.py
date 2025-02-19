# tldw_tube/models/video.py
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional

class CaptionTrack(BaseModel):
    url: str
    ext: str
    name: str

class VideoMetadata(BaseModel):
    id: str
    title: str
    description: str
    duration: int
    thumbnail_url: Optional[HttpUrl] = None  # Use HttpUrl for URL validation
    aspect_ratio: float
    webpage_url: str
    subtitles: Dict[str, List[CaptionTrack]]
    automatic_captions: Dict[str, List[CaptionTrack]]

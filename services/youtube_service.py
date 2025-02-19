# tldw_tube/services/youtube_service.py
import aiohttp
from core.video_extractor import VideoExtractor
from core.caption_processor import CaptionProcessor
from core.summarizer import Summarizer
from models.video import VideoMetadata, CaptionTrack
from models.summary import SummaryData
from typing import Optional
import logging
from fastapi import Depends # Add import
from database.database import get_db # Add import
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class YouTubeService:
    def __init__(self, db: Session = Depends(get_db), proxy: Optional[str] = None):
        self.db = db # Add this
        self.video_extractor = VideoExtractor(proxy=proxy)
        self.caption_processor = CaptionProcessor()
        self.summarizer = Summarizer()

    async def summarize_video(self, url: str) -> Optional[dict]:
        """Summarizes a YouTube video given its URL."""
        async with aiohttp.ClientSession() as session:
            video_metadata = await self.video_extractor.extract_video_info_async(url, session)
            if not video_metadata:
                logger.error(f"Failed to extract video metadata for URL: {url}")
                return None

            if video_metadata.duration >= 5400:  # 90 minutes in seconds
                logger.warning(f"Video too long to summarize (duration: {video_metadata.duration}s)")
                return None

            caption_track = self.video_extractor.get_captions_by_priority(video_metadata)
            if not caption_track:
                logger.error(f"No captions found for video: {video_metadata.id}")
                return None

            try:
                downloaded_captions = await self.video_extractor.download_captions_async(video_metadata.id, caption_track, session)
                caption_text = self.caption_processor.parse_captions(caption_track.ext, downloaded_captions)

            except ValueError as e:
                logger.error(f"Error during caption processing {str(e)}")
                return None

            summaries = await self.summarizer.summarize_async(
                caption_text, video_metadata.title, video_metadata.description, video_metadata.id
            )
            if not summaries:
                logger.error(f"Failed to generate summaries for video: {video_metadata.id}")
                return None

            result = {
                "video_id": video_metadata.id,
                "title": video_metadata.title,
                "thumbnail_url": str(video_metadata.thumbnail_url),  # Convert HttpUrl to string
                "aspect_ratio": video_metadata.aspect_ratio,
                "webpage_url": video_metadata.webpage_url,
                "summary": summaries.model_dump(), # Convert SummaryData to dict
            }
            return result

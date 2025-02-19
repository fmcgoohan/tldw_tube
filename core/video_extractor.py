# tldw_tube/core/video_extractor.py
import os
import json
import re
import aiohttp
from typing import Dict, Optional, List
from urllib.parse import urlparse, parse_qs
from core.config import settings
from models.video import VideoMetadata, CaptionTrack
from services.cache_service import CacheService  # Import CacheService
from fastapi import Depends  # Import Depends
import logging

logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self, proxy: Optional[str] = None, cache: CacheService = Depends(CacheService)):
        self.proxy = proxy or settings.proxy_url
        self.subtitle_priorities = ['en-US', 'en-CA', 'en']
        self.auto_caption_priorities = ['en-orig', 'en-US', 'en-CA', 'en']
        self.format_priorities = ['vtt', 'srt', 'ttml']
        self.cache = cache  # Use injected CacheService

    async def fetch_url(self, url: str, session: aiohttp.ClientSession) -> str:
        """Fetch content from a URL asynchronously."""
        async with session.get(url, proxy=self.proxy) as response:
            response.raise_for_status()
            return await response.text()

    async def extract_video_info_async(self, url: str, session: aiohttp.ClientSession) -> Optional[VideoMetadata]:
        """Extract video metadata asynchronously."""
        video_id = self._extract_video_id(url)
        cache_key = f"video_info_{video_id}"

        cached_data = self.cache.get(cache_key, cache_type="video") # Use cache_type
        if cached_data is not None:
            logger.info(f"Using cached video info for: {video_id}")
            return VideoMetadata(**cached_data)

        try:
            html = await self.fetch_url(f"https://www.youtube.com/watch?v={video_id}", session)
            metadata_dict = self._parse_video_info(html, video_id)
            metadata = VideoMetadata(**metadata_dict)

            # Convert HttpUrl to string BEFORE caching
            metadata_dump = metadata.model_dump()
            if metadata_dump.get("thumbnail_url"):
                metadata_dump["thumbnail_url"] = str(metadata_dump["thumbnail_url"])

            self.cache.set(cache_key, metadata_dump, cache_type="video")  # Use cache_type
            return metadata
        except Exception as e:
            logger.error(f"Error extracting video info for {video_id}: {str(e)}")
            return None

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        parsed = urlparse(url)
        if parsed.netloc == "youtu.be":
            return parsed.path.strip("/")
        query = parse_qs(parsed.query)
        return query["v"][0] if "v" in query else ""

    def _parse_video_info(self, html: str, video_id: str) -> Dict:
        """Parse video metadata from HTML (simplified)."""
        pattern = r"ytInitialPlayerResponse\s*=\s*({.*?});"
        match = re.search(pattern, html)
        if not match:
            raise ValueError("Could not find video metadata")

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}")

        video_details = data.get("videoDetails", {})
        captions = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])

        metadata = {
            "id": video_id,
            "title": video_details.get("title", ""),
            "description": data.get("microformat", {}).get("playerMicroformatRenderer", {}).get("description", {}).get("simpleText", ""),
            "duration": int(video_details.get("lengthSeconds", 0)),
            "thumbnail_url": video_details.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", ""),
            "aspect_ratio": 1.78,
            "webpage_url": f"https://www.youtube.com/watch?v={video_id}",
            "subtitles": {},
            "automatic_captions": {}
        }

        for track in captions:
            language_code = track.get("languageCode")
            if not language_code:
                continue
            track_data = {
                "url": track.get("baseUrl", ""),
                "ext": "vtt",
                "name": track.get("name", {}).get("simpleText", "Unknown")
            }
            kind = track.get("kind", "")
            if kind != "asr" and language_code:
                metadata["subtitles"].setdefault(language_code, []).append(track_data)
            elif kind == "asr" and language_code:
                metadata["automatic_captions"].setdefault(language_code, []).append(track_data)
        return metadata

    def get_captions_by_priority(self, video_metadata: VideoMetadata) -> Optional[CaptionTrack]:
        """Get captions based on priority order."""
        caption_tracks = []
        if video_metadata.subtitles:
            for lang in self.subtitle_priorities:
                if lang in video_metadata.subtitles:
                    caption_tracks = video_metadata.subtitles[lang]
                    break
            else:
                for lang in video_metadata.subtitles.keys():
                    if lang.startswith("en-"):
                        caption_tracks = video_metadata.subtitles[lang]
                        break

        if not caption_tracks and video_metadata.automatic_captions:
            for lang in self.auto_caption_priorities:
                if lang in video_metadata.automatic_captions:
                    caption_tracks = video_metadata.automatic_captions[lang]
                    break

        if not caption_tracks:
            return None


        for format_priority in self.format_priorities:
            for track in caption_tracks:
                if isinstance(track, CaptionTrack):
                    if track.ext == format_priority:
                        return track
                elif isinstance(track, dict):
                    if track["ext"] == format_priority:
                        return CaptionTrack(**track)
                else:
                    logger.warning(f"Unexpected track type: {type(track)}")

        return None

    async def download_captions_async(self, video_id: str, caption_track: CaptionTrack, session: aiohttp.ClientSession) -> str:
        """Download captions asynchronously, forcing VTT format."""
        cache_key = f"captions_{video_id}"

        cached_captions = self.cache.get(cache_key, cache_type="caption")  # Use cache_type
        if cached_captions:
            logger.info(f"Using cached captions for: {video_id}")
            return cached_captions

        url = caption_track.url + "&fmt=vtt"
        content = await self.fetch_url(url, session)
        self.cache.set(cache_key, content, cache_type="caption")  # Use cache_type
        return content

# tldw_tube/services/cache_service.py
# import os # No longer needed
# import json # No longer needed
from typing import Optional, Any
from core.config import settings
import logging
from fastapi import Depends 
from sqlalchemy.orm import Session
from database.database import get_db  # Import the get_db dependency
from database import crud # Import the crud operations

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, db: Session = Depends(get_db)):  # Use dependency injection
        self.db = db

    def get(self, key: str, cache_type: str = "video") -> Optional[Any]:
        """Retrieve data from the database cache."""
        try:
            with self.db as db: # Use "with" statement for session management.
                if cache_type == "video":
                    return crud.get_video_cache(db, key)
                elif cache_type == "caption":
                    return crud.get_caption_cache(db, key)
                elif cache_type == "summary":
                    return crud.get_summary_cache(db, key)
                else:
                    logger.warning(f"Unknown cache type: {cache_type}")
                    return None
        except Exception as e:
            logger.error(f"Error getting from cache: {type(e).__name__} - {e}")
            return None


    def set(self, key: str, data: Any, cache_type: str = "video"):
        """Store data in the database cache."""
        try:
            with self.db as db:
                if cache_type == "video":
                    existing = crud.get_video_cache(db, key)
                    if existing:
                        crud.update_video_cache(db,key,data)
                    else:
                        crud.create_video_cache(db, key, data)
                elif cache_type == "caption":
                    existing = crud.get_caption_cache(db, key)
                    if existing:
                        crud.update_caption_cache(db, key, data)
                    else:
                        crud.create_caption_cache(db, key, data)
                elif cache_type == "summary":
                    existing = crud.get_summary_cache(db, key)
                    if existing:
                        crud.update_summary_cache(db, key, data)
                    else:
                        crud.create_summary_cache(db, key, data)
                else:
                    logger.warning(f"Unknown cache type: {cache_type}")
        except Exception as e:
            logger.error(f"Error setting cache: {type(e).__name__} - {e}")

    def delete(self, key: str, cache_type: str = "video"):
        """Delete a key from the cache"""
        #Implement DB Delete here.
        logger.warning("Delete not yet implemented for DB cache")
        pass

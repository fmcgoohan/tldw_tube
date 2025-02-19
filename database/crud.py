# tldw_tube/database/crud.py
from sqlalchemy.orm import Session
from database import models
from models.video import VideoMetadata
from models.summary import SummaryData
from typing import Optional, Dict, Any


# --- VideoCache ---
def get_video_cache(db: Session, video_id: str) -> Optional[Dict]:
    cached = db.query(models.VideoCache).filter(models.VideoCache.id == video_id).first()
    return cached.data if cached else None

def create_video_cache(db: Session, video_id: str, data: Dict):
    db_item = models.VideoCache(id=video_id, data=data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_video_cache(db: Session, video_id: str, data: Dict):
    db_item = db.query(models.VideoCache).filter(models.VideoCache.id == video_id).first()
    if db_item:
        db_item.data = data
        db.commit()
        db.refresh(db_item)
    return db_item

# --- CaptionCache ---
def get_caption_cache(db: Session, video_id: str) -> Optional[str]:
    cached = db.query(models.CaptionCache).filter(models.CaptionCache.id == video_id).first()
    return cached.data if cached else None

def create_caption_cache(db: Session, video_id: str, data: str):
    db_item = models.CaptionCache(id=video_id, data=data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_caption_cache(db:Session, video_id:str, data:str):
    db_item = db.query(models.CaptionCache).filter(models.CaptionCache.id == video_id).first()
    if db_item:
        db_item.data = data
        db.commit()
        db.refresh(db_item)
    return db_item

# --- SummaryCache ---
def get_summary_cache(db: Session, video_id: str) -> Optional[Dict]:
    cached = db.query(models.SummaryCache).filter(models.SummaryCache.id == video_id).first()
    return cached.data if cached else None

def create_summary_cache(db: Session, video_id: str, data: Dict):
    db_item = models.SummaryCache(id=video_id, data=data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_summary_cache(db:Session, video_id: str, data: Dict):
    db_item = db.query(models.SummaryCache).filter(models.SummaryCache.id == video_id).first()
    if db_item:
        db_item.data = data
        db.commit()
        db.refresh(db_item)
    return db_item

# --- ApiKey (Example) ---
def get_api_key(db: Session, key_name: str) -> Optional[str]:
    api_key_entry = db.query(models.ApiKey).filter(models.ApiKey.key_name == key_name, models.ApiKey.is_active == True).first()
    return api_key_entry.key_value if api_key_entry else None  # Decrypt here in a real implementation

def create_api_key(db: Session, key_name: str, key_value: str):
    db_item = models.ApiKey(key_name = key_name, key_value = key_value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

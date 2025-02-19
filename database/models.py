# tldw_tube/database/models.py
from sqlalchemy import Boolean, Column, Integer, String, Text, JSON, DateTime, Float
from sqlalchemy.sql import func
from database.database import Base  # Import the Base class

class VideoCache(Base):
    __tablename__ = "video_cache"

    id = Column(String, primary_key=True, index=True) # video id
    data = Column(JSON)  # Store the VideoMetadata as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CaptionCache(Base):
    __tablename__ = "caption_cache"

    id = Column(String, primary_key=True, index=True)  # video id
    data = Column(Text)  # Store the caption text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SummaryCache(Base):
    __tablename__ = "summary_cache"

    id = Column(String, primary_key=True, index=True) # video id
    data = Column(JSON) # Store the SummaryData as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ApiKey(Base):  # Example for storing API keys
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, unique=True, index=True)  # e.g., "openai"
    key_value = Column(String)  # Store the encrypted key.  See note below.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


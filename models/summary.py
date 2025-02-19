# tldw_tube/models/summary.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class SummaryData(BaseModel):
    paragraph: str
    sentence: str
    question: str
    word: str
    wikipedia: Optional[HttpUrl] = None # Use HttpUrl
    themes: str


# tldw_tube/api/routers/summaries.py
from fastapi import APIRouter, Depends, Request, HTTPException
from api.schemas import SummarizeRequest, SummarizeResponse, ErrorResponse
from api.dependencies import rate_limit
from services.youtube_service import YouTubeService
from core.utils import validate_youtube_url
from api.exceptions import *  # Custom Exceptions
import logging
import traceback
from database.database import get_db  # Import get_db
from sqlalchemy.orm import Session  # Import Session

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse, responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
@rate_limit()  # Apply rate limiting
async def summarize_video(
    request: Request,
    summarize_request: SummarizeRequest,
    db: Session = Depends(get_db),  # Inject the database session
    youtube_service: YouTubeService = Depends(YouTubeService)  # Inject YouTubeService
):
    """Summarize a YouTube video based on its URL."""

    if not validate_youtube_url(summarize_request.url):
        raise InvalidYouTubeURLException()

    try:
        result = await youtube_service.summarize_video(summarize_request.url)
        if result:
            return SummarizeResponse(**result)
        else:
            raise SummarizationException()  # Should not get here. Kept for safety

    except HTTPException as e:  # Catching http exceptions and re-raising lets us keep specific status codes
        raise e
    except Exception as e:
        logger.error(f"Error processing summarization request: {type(e).__name__} - {e}\n{traceback.format_exc()}")
        # Use a generic 500 error for unexpected exceptions.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}")

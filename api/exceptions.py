# tldw_tube/api/exceptions.py
from fastapi import HTTPException, status

class InvalidYouTubeURLException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL"
        )

class VideoTooLongException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is too long to summarize"
        )

class CaptionsUnavailableException(HTTPException):
    def __init__(self, video_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Captions are not available for video: {video_id}"
        )

class SummarizationException(HTTPException):
     def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video summary"
        )

class VideoExtractionException(HTTPException):
     def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract video information"
        )

class CaptionProcessingException(HTTPException):
     def __init__(self, message:str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process video captions. {message}"
        )

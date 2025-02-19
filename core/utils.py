# tldw_tube/core/utils.py
from urllib.parse import urlparse, parse_qs

def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a YouTube video URL."""
    parsed = urlparse(url)
    if parsed.netloc not in ("www.youtube.com", "youtube.com", "youtu.be"):
        return False
    if parsed.netloc == "youtu.be":
        return bool(parsed.path.strip("/"))
    query = parse_qs(parsed.query)
    return "v" in query and bool(query["v"][0])


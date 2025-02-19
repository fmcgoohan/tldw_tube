# tldw_tube/core/caption_processor.py
import re
import webvtt
import xml.etree.ElementTree as ET
from typing import List
import logging

logger = logging.getLogger(__name__)

class CaptionProcessor:
    def __init__(self):
        pass # No initialization needed at this time

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert WebVTT timestamp to seconds."""
        time_parts = timestamp.split(":")
        hours = float(time_parts[0])
        minutes = float(time_parts[1])
        seconds = float(time_parts[2])
        return hours * 3600 + minutes * 60 + seconds

    def _seconds_to_timestamp(self, total_seconds: float) -> str:
        """Convert seconds to WebVTT timestamp."""
        hours = int(total_seconds // 3600)
        remaining = total_seconds % 3600
        minutes = int(remaining // 60)
        seconds = remaining % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

    def dedupe_yt_captions(self, subs_iter):
        """Deduplicate and adjust caption timings."""
        previous_subtitle = None
        for subtitle in subs_iter:
            if previous_subtitle is None:
                previous_subtitle = subtitle
                continue

            subtitle.text = subtitle.text.strip()
            if not subtitle.text:
                continue

            if (self._timestamp_to_seconds(subtitle.start) - self._timestamp_to_seconds(subtitle.end) < 0.15 and
                    subtitle.text in previous_subtitle.text):
                previous_subtitle.end = subtitle.end
                continue

            current_lines = subtitle.text.split("\n")
            last_lines = previous_subtitle.text.split("\n")
            singleword = False

            if current_lines[0] == last_lines[-1]:
                if len(last_lines) == 1:
                    if len(last_lines[0].split(" ")) < 2 and len(last_lines[0]) > 2:
                        singleword = True
                        subtitle.text = current_lines[0] + " " + "\n".join(current_lines[1:])
                    else:
                        subtitle.text = "\n".join(current_lines[1:])
                else:
                    subtitle.text = "\n".join(current_lines[1:])
            elif len(subtitle.text.split(" ")) <= 2:
                previous_subtitle.end = subtitle.end
                title_text = " " + subtitle.text if subtitle.text[0] != " " else subtitle.text
                previous_subtitle.text += title_text
                continue

            if self._timestamp_to_seconds(subtitle.start) <= self._timestamp_to_seconds(previous_subtitle.end):
                new_time = max(self._timestamp_to_seconds(subtitle.start) - 0.001, 0)
                previous_subtitle.end = self._seconds_to_timestamp(new_time)
            if self._timestamp_to_seconds(subtitle.start) >= self._timestamp_to_seconds(subtitle.end):
                subtitle.start, subtitle.end = subtitle.end, subtitle.start

            if not singleword:
                yield previous_subtitle
            previous_subtitle = subtitle
        if previous_subtitle:
            yield previous_subtitle

    def parse_captions(self, ext: str, content: str) -> str:
        """Parse caption content with formatting, handling XML if needed."""
        if ext != "vtt":
            raise ValueError(f"Unsupported caption format: {ext}")

        # Check if it's WebVTT
        if content.strip().startswith("WEBVTT"):
            try:
                captions = webvtt.from_string(content)
            except webvtt.errors.MalformedFileError as e:
                logger.error(f"Failed to parse WebVTT: {str(e)}. Raw content: {content[:200]}...")
                raise ValueError("Invalid WebVTT format: Malformed content") from e
        else:
            # Handle XML format
            logger.info("Detected XML caption format, converting to text")
            try:
                root = ET.fromstring(content)
                caption_text = ""
                for text_elem in root.findall(".//text"):
                    start = float(text_elem.get("start", 0))
                    # dur = float(text_elem.get("dur", 0))  # Not currently using duration
                    text = text_elem.text or ""
                    # Decode HTML entities (e.g., &#39; -> ')
                    text = text.replace("&#39;", "'").replace("&amp;", "&").replace("&quot;", '"')
                    if caption_text:
                        # Simple timing-based formatting (could refine with start/dur)
                        caption_text += " "
                    caption_text += text.strip()
                if not caption_text:
                    raise ValueError("No text found in XML captions")
                return caption_text  # Return as plain text for now
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML captions: {str(e)}. Raw content: {content[:200]}...")
                raise ValueError("Invalid caption format: Malformed XML") from e

        result = ""
        captions = list(self.dedupe_yt_captions(captions))

        for i, caption in enumerate(captions):
            current_text = caption.text.replace("\n", " ").strip()
            if i > 0:
                prev_end = self._timestamp_to_seconds(captions[i-1].end)
                current_start = self._timestamp_to_seconds(caption.start)
                time_diff = current_start - prev_end
                if time_diff >= 2:
                    result += "\n\n"
                elif time_diff >= 1:
                    result += "\n"
                else:
                    result += " "
            result += current_text

        return " ".join(re.split(" +", result))

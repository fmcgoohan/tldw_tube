# tldw_tube/core/summarizer.py
import json
import os
from typing import Dict
from openai import AsyncOpenAI
from core.config import settings
from models.summary import SummaryData
from services.cache_service import CacheService  # Import CacheService
from fastapi import Depends
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, cache: CacheService = Depends(CacheService)):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.cache = cache  # Use injected CacheService

    async def summarize_async(self, text: str, video_title: str, video_description: str, video_id: str) -> SummaryData:
        """Generate summaries asynchronously using OpenAI."""

        cache_key = f"summaries_{video_id}"

        cached_summaries = self.cache.get(cache_key, cache_type="summary") # Use cache_type
        if cached_summaries:
            logger.info(f"Using cached summaries for: {video_id}")
            # Convert potential HttpUrl to string
            if "wikipedia" in cached_summaries and cached_summaries["wikipedia"] is not None:
                cached_summaries["wikipedia"] = str(cached_summaries["wikipedia"])
            return SummaryData(**cached_summaries)

        summaries = {}
        messages = [
            {"role": "user", "content": f"Summarize this video given its subtitles into increasing levels of conciseness. Begin by summarizing it into a single paragraph.\nTitle: {video_title}\nDescription:\n`{video_description}`\n\nDo not describe or mention the video itself. Simply summarize the points it makes. Focus on the overall or underlying takeaway, cause, reason, or answer BEYOND what's already in the title and description, which is already shown to the user. PROVIDE NO OTHER OUTPUT OTHER THAN THE PARAGRAPH.\nSubtitles follow:"},
            {"role": "user", "content": text}
        ]

        # Paragraph summary
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        summaries["paragraph"] = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": summaries["paragraph"]})
        logger.info(f"Paragraph summary: {summaries['paragraph']}")

        # Sentence summary
        messages.append({"role": "user", "content": "Now summarize it into a single sentence. Focus on the overall or underlying takeaway, cause, reason, or answer BEYOND what's already in the title and description, which is already shown to the user. Basically, provide a single sentence answer to the question the video poses. PROVIDE NO OTHER OUTPUT OTHER THAN THE SENTENCE."})
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        summaries["sentence"] = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": summaries["sentence"]})
        logger.info(f"Sentence summary: {summaries['sentence']}")

        # Question
        messages.append({"role": "user", "content": f'Rephrase the video title into a single motivating question. Focus on the overall TOPIC or SUBJECT of the video. This could be just the video title verbatim, especially if it is already a question. Don\'t use information outside of the video title. For example, if the title is "This problem ...", the question would be "What problem ...?". As a reminder, here is the video title again: "{video_title}". PROVIDE NO OTHER OUTPUT OTHER THAN THE QUESTION.'})
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        summaries["question"] = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": summaries["question"]})
        logger.info(f"Question: {summaries['question']}")

        # Word answer
        messages.append({"role": "user", "content": 'Answer the question we just asked with just a single phrase, ideally one or two words. Examples: "Is EVOLUTION REAL?" -> "Yes." "Have scientists achieved fusion?" -> "No." "It depends." "Will AI take over the world?" -> "Nobody knows." "Why NO ONE lives here" -> "Poor geography." "Inside Disney\'s $1 BILLION disaster" -> "No market need." "Scientists FEAR this one thing" -> "Climate change." "Why is there war in the middle east?" -> "It\'s complicated." "Have we unlocked the secret to QUANTUM COMPUTING?" -> "Not really." "A day from Hell" -> "1999 Moore tornado" ... -> "Mostly." ... -> "Usually." PROVIDE NO OTHER OUTPUT OTHER THAN THE WORD(S) OF THE ANSWER.'})
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        summaries["word"] = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": summaries["word"]})
        logger.info(f"Word answer: {summaries['word']}")

        # Wikipedia search term
        messages.append({"role": "user", "content": 'Now suggest a search term for a Wikipedia search that replaces watching the video. Make the search SPECIFIC to the TOPIC of the video. For example: "The $6 Billion Transit Project with No Ridership" -> "FasTracks"; "Why NOBODY lives in this part of China" -> "Gobi Desert"; "This unknown professor REVOLUTIONIZED ..." -> "Joseph-Louis Lagrange"; "Every Computer Can Be Hacked!" -> "Zero-Day Vulnerability"; Provide the Wikipedia page name with no special punctuation:'})
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        wikipedia_term = completion.choices[0].message.content.strip()
        summaries["word"] += f" ({wikipedia_term})"  # Keep combined answer
        summaries["wikipedia"] = f"https://en.wikipedia.org/w/index.php?search={quote_plus(wikipedia_term)}"
        messages.append({"role": "assistant", "content": wikipedia_term})
        logger.info(f"Wikipedia term: {wikipedia_term}")

        # Structured summary with themes
        messages.append({
            "role": "user",
            "content": (
                "Now create a structured summary by dividing the content into major themes or sections. "
                "For each theme, provide a clear heading (like a short title), sentiment, and a concise paragraph or two "
                "that explains the key points under that theme. Only output these headings and paragraphs. "
                "Do not repeat the entire transcript, and do not include any disclaimers or extra text."
            )
        })
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        summaries["themes"] = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": summaries["themes"]})
        logger.info(f"Themes: {summaries['themes']}")

        summary_data = SummaryData(**summaries)

        # Convert HttpUrl to string BEFORE caching
        summary_data_dump = summary_data.model_dump()
        if summary_data_dump.get("wikipedia"):
            summary_data_dump["wikipedia"] = str(summary_data_dump["wikipedia"])

        self.cache.set(cache_key, summary_data_dump, cache_type="summary")  # Use cache_type

        return summary_data

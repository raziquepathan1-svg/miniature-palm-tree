"""Uses Claude to pick a fresh topic and write the full video script + YouTube metadata."""

import os

import anthropic
from pydantic import BaseModel, Field

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5")
WORDS_PER_MINUTE = 150


class VideoPlan(BaseModel):
    topic: str = Field(description="The specific topic of this video")
    title: str = Field(description="YouTube title, under 70 characters, curiosity-driven but not clickbait")
    description: str = Field(description="YouTube description: 2-3 sentence summary, key points as bullets, 3-5 hashtags")
    tags: list[str] = Field(description="8-15 YouTube search tags")
    thumbnail_text: str = Field(description="2-5 punchy words for the thumbnail")
    scenes: list[str] = Field(
        description="The spoken script split into scenes. Each scene is 1-4 short paragraphs of exactly "
        "what the avatar says, max 1200 characters. First scene is a strong hook, last scene is a "
        "recap plus a call to like and subscribe."
    )


def plan_video(channel: dict, video: dict, past_topics: list[str], requested_topic: str | None = None,
               style: dict | None = None) -> VideoPlan:
    target_words = int(video["target_minutes"] * WORDS_PER_MINUTE)
    shorts = video.get("format") == "shorts"
    if shorts:
        target_words = min(target_words, 130)  # Shorts must stay under 60 seconds

    if requested_topic:
        topic_instruction = f"The topic for this video is: {requested_topic}"
    else:
        recent = "\n".join(f"- {t}" for t in past_topics[-200:]) or "(none yet)"
        topic_instruction = (
            "Choose ONE specific, interesting topic inside the niche that people actually search for. "
            f"It must be clearly different from every topic already published:\n{recent}"
        )

    prompt = f"""You are the head writer for an educational YouTube channel presented by an AI avatar.

Channel niche: {channel['niche']}
Audience: {channel['audience']}
Target country: {channel.get('country', 'United States')}
Language of the script, title and description: {channel['language']}
Presenter: {channel.get('presenter', 'the channel host')}
Presenter tone: {channel['tone']}
Format: {"YouTube Short (vertical, under 60 seconds)" if shorts else "standard YouTube video"}

{topic_instruction}
{f"Video style for this episode: {style['name']}. {style['instructions']}" if style else ""}

Write a script of about {target_words} spoken words. Requirements:
- Factually accurate. If something is uncertain or debated, say so. No invented statistics.
- Hook the viewer in the first 10 seconds.
- Explain with simple analogies and concrete examples; one idea at a time.
- Written for viewers in {channel.get('country', 'United States')}: use local spelling, everyday examples,
  places, money and cultural references they know. For US viewers use American English and US customary
  units (miles, °F, pounds), giving metric in parentheses when it helps.
- Pick topics and titles people in that country actually search for.
{channel.get('content_rules', '')}
- Written to be spoken aloud: short sentences, no markdown, no stage directions, no emojis,
  no bracketed notes - only the words the presenter says.
"""

    client = anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
        output_format=VideoPlan,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to write this script; try a different topic.")
    if response.stop_reason == "max_tokens" or response.parsed_output is None:
        raise RuntimeError(f"Script generation did not complete (stop_reason={response.stop_reason}).")
    return response.parsed_output

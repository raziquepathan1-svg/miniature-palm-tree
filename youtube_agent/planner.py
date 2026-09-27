"""Uses Claude to pick a fresh topic and write the full video script + YouTube metadata."""

import os
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

# Sonnet 5 keeps quality high at a fraction of Opus's cost (budget choice).
MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5")


def _fallback_kwargs() -> dict:
    """Server-side refusal fallbacks are documented for the Opus/Fable tiers only."""
    if MODEL.startswith(("claude-opus", "claude-fable")):
        return {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}
    return {}
WORDS_PER_MINUTE = 150


class Scene(BaseModel):
    narration: str = Field(
        description="Exactly what the narrator says in this scene: 2-5 short sentences (about 15-35 seconds), "
        "max 900 characters. Plain spoken words only."
    )
    layout: Literal["title", "bullets", "big_number", "warning", "myth_fact", "outro"] = Field(
        description="On-screen graphic: title = hook/topic card; bullets = 2-4 key points; big_number = one "
        "key number or fact in huge type; warning = red-flag symptoms / call 911; myth_fact = points[0] is the "
        "myth, points[1] the fact; outro = recap + subscribe"
    )
    heading: str = Field(description="Short on-screen heading, max 6 words (for big_number: the number itself, e.g. '120/80')")
    points: list[str] = Field(description="0-4 very short on-screen lines, max 8 words each. Must match what is said.")
    footage_query: str = Field(
        description="2-4 word stock-video search for a calm, relevant, non-graphic background clip, "
        "e.g. 'doctor checking blood pressure', 'person drinking water'"
    )


class VideoPlan(BaseModel):
    topic: str = Field(description="The specific topic of this video")
    title: str = Field(description="YouTube title, under 70 characters, curiosity-driven but not clickbait")
    description: str = Field(description="YouTube description: 2-3 sentence summary, key points as bullets, 3-5 hashtags")
    tags: list[str] = Field(description="8-15 YouTube search tags")
    thumbnail_text: str = Field(description="2-5 punchy words for the thumbnail")
    scenes: list[Scene] = Field(
        description="The video split into scenes, each with its narration and on-screen graphic. First scene "
        "is a strong hook (layout 'title'), last scene is a recap plus a call to like and subscribe (layout 'outro')."
    )

    short_scenes: list[Scene] = Field(
        description="A separate standalone vertical Short (for Instagram/Facebook Reels) on the same topic: 2-4 "
        "scenes, about 90-120 spoken words in total (under 50 seconds). Scene 1 is a punchy hook (layout "
        "'title'); the middle gives the single most useful takeaway; the last scene (layout 'outro') says the full "
        "video is on the Health Support Studio YouTube channel. Empty list if this video is itself a Short."
    )
    short_caption: str = Field(
        description="Instagram/Facebook caption for the Short: 1-2 friendly sentences, then 'Full video on our "
        "YouTube channel: Health Support Studio', then 'Educational only, not medical advice.', then 5-8 hashtags."
    )

    def narration(self) -> list[str]:
        return [s.narration for s in self.scenes]


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

    presented_by = "an AI avatar" if video.get("mode") == "avatar" else "an AI narrator voice over on-screen graphics and stock footage"
    prompt = f"""You are the head writer for an educational YouTube channel presented by {presented_by}.

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
- In the narration, write out anything a text-to-speech voice might misread: "milligrams" not "mg",
  "for example" not "e.g.", "120 over 80" not "120/80". (On-screen text may use the short forms.)
- On-screen text must be short, consistent with the narration, and easy to read on a phone.
"""

    client = anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        **_fallback_kwargs(),
        messages=[{"role": "user", "content": prompt}],
        output_format=VideoPlan,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to write this script; try a different topic.")
    if response.stop_reason == "max_tokens" or response.parsed_output is None:
        raise RuntimeError(f"Script generation did not complete (stop_reason={response.stop_reason}).")
    return response.parsed_output

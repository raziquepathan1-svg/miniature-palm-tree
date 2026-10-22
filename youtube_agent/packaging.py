"""The owner's growth rules for every long video (Health Support Studio; on with growth.retention in config.yaml).

Claude rewrites the day's script for retention, without adding facts (the fact check runs again afterwards):
- 5 title + thumbnail combinations (titles under 50 characters, thumbnail text max 3 words that never repeat
  the title); the strongest is used, all 5 are kept for the daily message.
- The first 15 seconds deliver the thumbnail's promise; no long intro; an open loop around the 60-second mark.
- Spoken grammar: short, punchy sentences; visual directions stay in footage_query, never in the narration.
- A 20-second ending that bridges to the most helpful related video already on the channel (no goodbyes).
- The first 2 description lines carry broad search keywords; one open, personal question to pin.
"""

import re

from pydantic import BaseModel, Field

from .planner import Scene

LAST: dict | None = None  # today's packaging (main adds it to the history entry)
ERROR: str | None = None  # why it failed, if it did


class Package(BaseModel):
    title: str = Field(description="YouTube title, UNDER 50 characters, high-emotion but accurate power words "
                       "(e.g. mistake, hidden, never, warning, truth), sparks curiosity, matches the video exactly")
    thumbnail_text: str = Field(description="Max 3 BIG words for the thumbnail, a short statement or a 1-3 word "
                                "question (e.g. 'TOO LATE?'). Must NOT repeat any word of the title.")
    thumbnail_highlight: str = Field(description="The one word of thumbnail_text shown in yellow")
    thumbnail_scene: str = Field(description="Simple high-contrast thumbnail picture with max 3 visual elements: "
                                 "the host (chest-up, right side, expression) + 1-2 topic objects beside him. "
                                 "He never holds the object.")


class Retention(BaseModel):
    packages: list[Package] = Field(description="Exactly 5 distinct title + thumbnail combinations")
    best: int = Field(description="Index (0-4) of the package most likely to get the highest click-through rate")
    scenes: list[Scene] = Field(description="The whole script rewritten for retention (same facts, same order "
                                "of ideas, similar length). Scene 1 is the hook; the last scene (layout 'outro') "
                                "is a short recap plus the spoken line that the video is educational, not medical "
                                "advice. No goodbye, no 'thanks for watching', no subscribe line (added later).")
    bridge_video: int = Field(description="Index of the related video (from the list given) to send viewers to next")
    bridge: str = Field(description="The 20-second spoken ending (45-55 words) that makes watching that video feel "
                        "like the necessary next step to solve the viewer's problem. Ends by saying it is linked in "
                        "the pinned comment and the description. No goodbye phrases.")
    description_top: str = Field(description="Exactly 2 lines for the top of the description, rich in broad "
                                 "searchable keywords for this topic, natural (not a keyword list), no hashtags")
    pin_questions: list[str] = Field(description="3 open, personal questions that make viewers want to answer "
                                     "(experience, habits, opinions). Best one first. Never invite arguments about "
                                     "medical facts, vaccines or treatments.")


def _candidates(history: list[dict], episode) -> list[dict]:
    """Recent public-bound videos to bridge to (newest first); the previous series part first when there is one."""
    vids = [h for h in reversed(history) if h.get("youtube_id") and h.get("title")][:25]
    if episode and episode.n > 1:
        prev = next((h for h in vids if h.get("series") == episode.series and h.get("episode") == episode.n - 1),
                    None)
        if prev:
            vids = [prev] + [h for h in vids if h is not prev]
    return vids


def _clean(text: str) -> str:
    text = re.sub(r"\[[^\]]*\]", "", text)  # visual directions never reach the voice
    text = re.sub(r"\s*[—–]\s*", ", ", text)  # dashes sounded wrong in the cloned voice
    text = re.sub(r"\s*(\.\.\.|…)\s*", ", ", text)
    return re.sub(r"\s+", " ", text).strip()


def _overlaps(p: Package) -> bool:
    title = {w.strip("?!.,:'\"").lower() for w in p.title.split()}
    words = [w.strip("?!.,:'\"").lower() for w in p.thumbnail_text.split()]
    small = {"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "your", "you"}
    return len(words) > 3 or any(w in title and w not in small for w in words)


def improve(plan, episode, history: list[dict], channel: dict) -> Retention:
    """Rewrites plan in place (scenes, title, thumbnail text) and returns the full result."""
    import anthropic

    from .planner import MODEL, _fallback_kwargs

    cands = _candidates(history, episode)
    listing = "\n".join(f"{i}. {h['title']}" + (" (previous part of this series)" if i == 0 and episode and
                                                  episode.n > 1 and h.get("series") == episode.series else "")
                        for i, h in enumerate(cands)) or "(none yet)"
    script = "\n\n".join(f"[Scene {i + 1}] layout={s.layout} heading={s.heading!r} points={s.points} "
                         f"footage={s.footage_query!r}\n{s.narration}" for i, s in enumerate(plan.scenes))
    series = f'It is part {episode.n} of {episode.total} of our series "{episode.series}".' if episode else ""
    prompt = f"""You are the Executive Growth Director for {channel.get('name', 'Health Support Studio')}, a calm,
trustworthy health-education YouTube channel for US adults. Goal: maximum click-through rate, average view
duration and subscriber conversion, without ever misleading anyone about health.

Topic: {plan.topic}. {series}

Current script (already fact-checked; you may rephrase, shorten, reorder within a scene and cut fluff, but do
NOT add any new fact, number, claim or advice, and do not drop safety warnings or "call 911" lines):
{script}

Do all of this:
1. PACKAGING: 5 distinct title + thumbnail combinations. Titles under 50 characters, high-emotion power words,
   curiosity, but every title must be fully true to this video (YouTube limits misleading health titles).
   Thumbnail text max 3 words and never repeating title words. Thumbnail picture: max 3 visual elements.
   At least 2 of the 5 thumbnail texts are a short question of 1-3 words (e.g. "SAY WHAT?", "TOO LATE?",
   "NORMAL?") paired with a title that is NOT a question; never a question title with a question thumbnail.
   Pick the best one.
2. HOOK: rewrite scene 1 so the first 15 seconds instantly deliver on the best package's promise with a
   high-stakes hook and an immediate payoff. No "welcome", no channel intro, no "in this video".
3. RETENTION: short, punchy spoken sentences (spoken grammar, contractions, direct "you"). Around the
   60-second mark (after about 150 spoken words) end a scene with an open loop that makes the viewer stay
   (e.g. "But the mistake most people make comes later, and it's the one that matters most."), and pay it off
   later. Vary layouts so something new appears on screen at least every 45 seconds; visual directions go
   only in heading/points/footage_query, never in the narration. No brackets, ellipses or dashes in the
   narration: only commas and periods.
4. ENDING: the last scene recaps briefly and keeps the spoken "educational, not medical advice" line.
   Then write the separate 20-second bridge to the most helpful video from this list (give its number):
{listing}
5. DESCRIPTION: 2 natural top lines with broad searchable keywords.
6. PINNED COMMENT: 3 open, personal questions (best first).

Rules: never call the host a doctor or nurse, never invent personal stories, American English, write numbers
as they are spoken ("120 over 80"). Keep roughly the same number of scenes and the same total length."""
    client = anthropic.Anthropic()
    response = client.beta.messages.parse(model=MODEL, max_tokens=16000, **_fallback_kwargs(),
                                          messages=[{"role": "user", "content": prompt}], output_format=Retention)
    r = response.parsed_output
    if r is None or len(r.scenes) < 3 or not r.packages:
        raise RuntimeError(f"packaging did not complete ({response.stop_reason})")
    print(f"    packaging tokens: in {response.usage.input_tokens}, out {response.usage.output_tokens}")
    return use(plan, r, cands)


def use(plan, r: Retention, cands: list[dict]) -> Retention:
    """Puts Claude's answer into the plan: the best valid package, the rewritten scenes, the bridge."""
    global LAST
    order = [r.best] + [i for i in range(len(r.packages)) if i != r.best]
    best = next((r.packages[i] for i in order if 0 <= i < len(r.packages) and len(r.packages[i].title) <= 50
                 and not _overlaps(r.packages[i])), r.packages[min(max(r.best, 0), len(r.packages) - 1)])
    for s in r.scenes:
        s.narration = _clean(s.narration)
    plan.scenes = r.scenes
    plan.title = best.title
    plan.thumbnail_text, plan.thumbnail_highlight = best.thumbnail_text, best.thumbnail_highlight
    target = cands[r.bridge_video] if 0 <= r.bridge_video < len(cands) else (cands[0] if cands else None)
    LAST = {"packages": [p.model_dump() for p in r.packages], "chosen": best.model_dump(),
            "bridge": _clean(r.bridge) if target else "", "bridge_id": target["youtube_id"] if target else None,
            "bridge_title": target["title"] if target else None,
            "description_top": r.description_top.strip(), "pin_question": r.pin_questions[0].strip(),
            "pin_questions": [q.strip() for q in r.pin_questions]}
    return r


def finish_description(plan) -> None:
    """Keyword lines first, then the related video, then the rest (series line, summary...)."""
    if not LAST:
        return
    top = LAST["description_top"]
    if LAST.get("bridge_id"):
        top += f"\n\n▶ Watch next: {LAST['bridge_title']}: https://youtu.be/{LAST['bridge_id']}"
    plan.description = f"{top}\n\n{plan.description}"

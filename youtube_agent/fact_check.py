"""Medical fact-check: Claude verifies every health claim in a script against
authoritative sources on the web, fixes errors, and blocks unsafe videos."""

import os

import anthropic
from pydantic import BaseModel, ValidationError

# Sonnet 5 keeps quality high at a fraction of Opus's cost (budget choice).
MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5")


def _fallback_kwargs() -> dict:
    """Server-side refusal fallbacks are documented for the Opus/Fable tiers only."""
    if MODEL.startswith(("claude-opus", "claude-fable")):
        return {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}
    return {}
MAX_ROUNDS = 12

TRUSTED_SOURCES = (
    "CDC (cdc.gov), NIH / MedlinePlus (nih.gov, medlineplus.gov), FDA (fda.gov), WHO (who.int), "
    "Mayo Clinic, Cleveland Clinic, Johns Hopkins Medicine, American Heart Association, "
    "American Diabetes Association, American Academy of Pediatrics, USPSTF, peer-reviewed journals"
)


class CorrectedScene(BaseModel):
    narration: str
    heading: str
    points: list[str]


class Review(BaseModel):
    approved: bool
    issues: list[str]
    corrected_scenes: list[CorrectedScene]
    sources: list[str]

    def apply_to(self, scenes: list) -> list:
        """Copy corrected text onto the original scene objects (keeping layout and footage)."""
        if len(self.corrected_scenes) != len(scenes):
            raise RuntimeError("Fact-check changed the number of scenes; video skipped to be safe.")
        return [
            s.model_copy(update={"narration": c.narration, "heading": c.heading, "points": c.points})
            for s, c in zip(scenes, self.corrected_scenes)
        ]


SUBMIT_TOOL = {
    "name": "submit_review",
    "description": "Submit the final fact-check result. Call this exactly once, when the review is complete.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "approved": {
                "type": "boolean",
                "description": "true if the corrected script is accurate and safe to publish; false if it "
                "cannot be made safe (e.g. the topic itself promotes unproven or dangerous treatment).",
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Every problem found and how it was fixed (empty if none).",
            },
            "corrected_scenes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "narration": {"type": "string"},
                        "heading": {"type": "string"},
                        "points": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["narration", "heading", "points"],
                    "additionalProperties": False,
                },
                "description": "Every scene after corrections, in the same order and the SAME NUMBER of scenes "
                "as the input. Unchanged scenes are copied as-is.",
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-6 authoritative source URLs that support the script, for the video description.",
            },
        },
        "required": ["approved", "issues", "corrected_scenes", "sources"],
        "additionalProperties": False,
    },
}


def fact_check(topic: str, scenes: list, searches: int = 6) -> Review:
    """searches=0 is budget mode: the review uses Claude's own medical knowledge, no web search
    (web search results are resent on every step and were most of the cost of a video)."""
    script = "\n\n".join(
        f"[Scene {i + 1}]\nNarration: {s.narration}\nOn-screen heading: {s.heading}\n"
        f"On-screen points: {' | '.join(s.points) or '(none)'}"
        for i, s in enumerate(scenes)
    )
    if searches:
        research = (f"Use web search (up to {searches} searches) to verify the key numbers and recommendations "
                    "against official sources; search for the most important claims first. Prefer current US "
                    f"guidance from: {TRUSTED_SOURCES}.")
    else:
        research = (f"Verify each claim against what current US guidance says ({TRUSTED_SOURCES}). If you are "
                    "not confident a specific number or claim is correct and current, make it more general or "
                    "remove it rather than guess. For sources, list only the organizations' main websites "
                    "(e.g. 'CDC: https://www.cdc.gov'), never guessed deep links.")
    prompt = f"""You are a meticulous medical fact-checker for a health-education YouTube channel
for a US audience.

Topic: {topic}

Script:
{script}

Check EVERY factual health claim (numbers, symptoms, doses, risks, recommendations, guidelines),
in both the narration and the on-screen text. {research}

Fix anything that is wrong, outdated, overstated, or missing an important safety caveat. Also make sure:
- No individual diagnosis, no specific medication doses for self-treatment, no advice to start, stop or
  change a prescribed medicine without a clinician.
- Warning signs that need urgent care are mentioned when relevant (e.g. "call 911").
- Nothing contradicts CDC/WHO/FDA guidance or promotes unproven treatments.
- No invented personal stories or patient anecdotes.
Keep the same friendly spoken style and roughly the same length. Change only what needs changing.

When done, call submit_review."""

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]
    tools = [SUBMIT_TOOL]
    if searches:
        tools.insert(0, {"type": "web_search_20260209", "name": "web_search", "max_uses": searches})

    for _ in range(MAX_ROUNDS):
        # Streaming is required for long responses (web research + a full corrected script).
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=32000,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},  # thorough enough to verify claims, cheaper than high
            **_fallback_kwargs(),
            tools=tools,
            messages=messages,
        ) as stream:
            response = stream.get_final_message()
        u = response.usage
        print(f"    fact-check tokens: in {u.input_tokens} (+cache {u.cache_read_input_tokens or 0}), out {u.output_tokens}")
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            raise RuntimeError("Fact-check was declined by the model; video skipped.")
        if response.stop_reason == "max_tokens":
            raise RuntimeError("Fact-check response was cut off (max_tokens); video skipped to be safe.")
        if response.stop_reason == "pause_turn":
            continue  # long web-search turn; resend to let it finish

        submit = next((b for b in response.content if b.type == "tool_use" and b.name == "submit_review"), None)
        if submit:
            try:
                return Review.model_validate(submit.input)
            except ValidationError as e:
                raise RuntimeError(f"Fact-check returned malformed data: {e}")

        # Finished without submitting: remind it once more.
        messages.append({"role": "user", "content": "Please call submit_review with your final result now."})

    raise RuntimeError("Fact-check did not finish.")

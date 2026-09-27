"""Medical fact-check: Claude verifies every health claim in a script against
authoritative sources on the web, fixes errors, and blocks unsafe videos."""

import os

import anthropic
from pydantic import BaseModel, ValidationError

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5")
MAX_ROUNDS = 12

TRUSTED_SOURCES = (
    "CDC (cdc.gov), NIH / MedlinePlus (nih.gov, medlineplus.gov), FDA (fda.gov), WHO (who.int), "
    "Mayo Clinic, Cleveland Clinic, Johns Hopkins Medicine, American Heart Association, "
    "American Diabetes Association, American Academy of Pediatrics, USPSTF, peer-reviewed journals"
)


class Review(BaseModel):
    approved: bool
    issues: list[str]
    corrected_scenes: list[str]
    sources: list[str]


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
                "items": {"type": "string"},
                "description": "The full script scenes after corrections, same structure as the input.",
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


def fact_check(topic: str, scenes: list[str]) -> Review:
    script = "\n\n".join(f"[Scene {i + 1}]\n{s}" for i, s in enumerate(scenes))
    prompt = f"""You are a meticulous medical fact-checker for a health-education YouTube channel
for a US audience.

Topic: {topic}

Script:
{script}

Check EVERY factual health claim (numbers, symptoms, doses, risks, recommendations, guidelines)
using web search. Prefer current US guidance from: {TRUSTED_SOURCES}.

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
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 15}, SUBMIT_TOOL]

    for _ in range(MAX_ROUNDS):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=32000,
            thinking={"type": "adaptive"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            raise RuntimeError("Fact-check was declined by the model; video skipped.")
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

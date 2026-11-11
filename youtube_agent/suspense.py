"""Movie-style suspense (owner, Nov 9: "act like a story writer and movie director ... for our reel and our video").

Two layers, both true by construction (nothing is invented about real people):
1. Automatic, every video: after the hook, an open loop that names the myth/warning saved for later ("I'm saving one
   for last ... true or false? Stay to the end"), and 2 "Up next: ... true or false?" cliffhangers at page ends,
   so every few pages the viewer has an unanswered question.
2. Optional, written per script in the bank file (`story:`): a short, clearly hypothetical case ("Imagine ...") told
   like a film - set-up after the hook, a twist mid-video, the ending just before the outro - and a cold open +
   cliffhanger for Short 1 / the Reel. Characters are always "imagine"/"say" examples, never real patients.

Every added line is remembered in ADDED so Shorts cut from a page can leave it out.
"""

import re

ADDED: list[str] = []
REEL_ANSWER: str = ""  # the Reel cannot send people to YouTube, so it reveals the cliffhanger's answer


def _q(text: str) -> str:
    return text.strip().rstrip(".?!")


def _lower_first(text: str) -> str:  # "A nightcap helps" -> "a nightcap helps", but "CBT-I works" stays
    first = text.split(" ", 1)[0]
    return text[:1].lower() + text[1:] if text[1:2].islower() or first in ("A", "An") else text


def _words(text: str) -> set:
    return {w for w in re.findall(r"[a-z]{5,}", text.lower())}


def _add(scene, line: str, before: bool = False) -> None:
    ADDED.append(line)
    scene.narration = f"{line} {scene.narration.strip()}" if before else f"{scene.narration.rstrip()} {line}"


def apply(plan, story: dict | None = None) -> None:
    """Adds the suspense lines to the long video (plan.scenes) and to Short 1 / the Reel (plan.short_scenes)."""
    global REEL_ANSWER
    ADDED.clear()
    story = story or {}
    REEL_ANSWER = (story.get("reel_answer") or "").strip() if story.get("short_cliff") else ""
    scenes = plan.scenes
    if len(scenes) >= 5:
        middle = list(range(1, len(scenes) - 1))
        myths = [i for i in middle if scenes[i].layout == "myth_fact" and scenes[i].points]
        warns = [i for i in middle if scenes[i].layout == "warning"]

        # 2. the hand-written story first (the case is set up before the open loop is promised)
        if story.get("open"):
            _add(scenes[0], story["open"].strip())
        if story.get("twist") and len(scenes) >= 6:  # on the page it talks about, else the middle page
            tw = _words(story["twist"])
            best = max(middle, key=lambda i: (len(tw & _words(f"{scenes[i].heading} {scenes[i].narration}")),
                                              -abs(i - len(scenes) // 2)))
            if not tw & _words(f"{scenes[best].heading} {scenes[best].narration}"):
                best = len(scenes) // 2
            _add(scenes[best], story["twist"].strip())
        if story.get("end"):
            _add(scenes[-1], story["end"].strip(), before=True)

        # 1a. open loop: the last myth (or the last warning page) is promised now and paid off later
        saved = myths[-1] if len(myths) >= 3 else (warns[-1] if warns else None)
        if saved is not None and scenes[saved].layout != "myth_fact" and story.get("open"):
            saved = None  # the story already promises what comes later; a second "stay with me" sounds repeated
        if saved is not None and saved > 3:
            if scenes[saved].layout == "myth_fact":
                loop = (f"And later in this video: {_lower_first(_q(scenes[saved].points[0]))}. "
                        "True or false? Stay with me to find out.")
            else:
                loop = "And stay with me: later I'll show you the signs that mean you need help fast."
            _add(scenes[0], loop)
            if scenes[saved].layout == "myth_fact":
                _add(scenes[saved], "Now, the one I promised at the start.", before=True)

        # 1b. two cliffhangers: a page ends by naming the next myth as a question
        cands = [i for i in myths if i - 1 >= 2 and i != saved and scenes[i - 1].layout != "outro"]
        picks = [cands[len(cands) // 3], cands[(2 * len(cands)) // 3]] if len(cands) >= 4 else cands[:1]
        for i in dict.fromkeys(picks):
            _add(scenes[i - 1], f"Up next: {_lower_first(_q(scenes[i].points[0]))}. True or false?")

    shorts = getattr(plan, "short_scenes", None) or []
    if shorts and story.get("short_open"):
        _add(shorts[0], story["short_open"].strip())
    if shorts and story.get("short_cliff"):
        last = shorts[-1]
        parts = re.split(r"(?<=[.!?])\s+", last.narration.strip())
        line = story["short_cliff"].strip()
        ADDED.append(line)
        last.narration = " ".join([line] + parts)  # the cliffhanger, then "find out in the full video"


def strip(text: str) -> str:
    """The text without any line this module added (for Shorts cut from a long-video page)."""
    for line in ADDED:
        text = text.replace(line, "")
    return re.sub(r"\s{2,}", " ", text).strip()

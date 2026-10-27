"""Merge this run's history.json into the newest one on the branch, entry by entry, instead of failing on a
git conflict when something else changed history.json while the run was busy (approve, publish now...).

    python -m youtube_agent.merge_history OURS.json   # merges into youtube_agent/history.json
"""

import json
import sys

from .main import load_history, save_history


def _key(h: dict) -> str:
    return h.get("youtube_id") or f"{h.get('date')}|{h.get('title')}"


def main() -> None:
    ours = json.loads(open(sys.argv[1]).read())
    theirs = load_history()
    index = {_key(h): h for h in theirs}
    added = 0
    for h in ours:
        if _key(h) in index:  # both have it: keep the branch's values, add any field only we have
            for k, v in h.items():
                index[_key(h)].setdefault(k, v)
        else:
            theirs.append(h)
            added += 1
    theirs.sort(key=lambda h: str(h.get("date", "")))
    save_history(theirs)
    print(f"Merged history: {added} new entr{'y' if added == 1 else 'ies'}")


if __name__ == "__main__":
    main()

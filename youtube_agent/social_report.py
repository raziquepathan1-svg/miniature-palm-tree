"""Read-only weekly report for the Facebook Page and the Instagram account (owner, Nov 17: "our fb followers are not
increasing and no views"). Prints followers and the views/reach of the latest Reels so we can see what works.
Nothing is posted or changed. Every number is asked for separately, so a metric Meta no longer offers shows n/a
instead of stopping the report.

    python -m youtube_agent.social_report
"""

import os
import sys

import requests

from . import social

GRAPH = social.GRAPH


def _get(path: str, token: str, **params):
    r = requests.get(f"{GRAPH}/{path}", params={**params, "access_token": token}, timeout=60)
    try:
        data = r.json()
    except Exception:
        return None, f"HTTP {r.status_code}"
    if isinstance(data, dict) and data.get("error"):
        return None, data["error"].get("message", "error")[:120]
    return data, ""


ERRORS: dict[str, str] = {}


def _metric(obj_id: str, token: str, metrics: list[str], edge: str = "insights") -> dict:
    out = {}
    for m in metrics:  # one at a time: a retired metric must not hide the others
        data, err = _get(f"{obj_id}/{edge}", token, metric=m)
        if err:
            ERRORS.setdefault(m, err)
        value = None
        if data and data.get("data"):
            vals = data["data"][0].get("values") or []
            if vals:
                value = vals[0].get("value")
            elif data["data"][0].get("total_value") is not None:
                value = data["data"][0]["total_value"].get("value")
        out[m] = value if value is not None else "n/a"
    return out


def facebook(page_id: str, token: str) -> None:
    page, err = _get(page_id, token, fields="name,fan_count,followers_count")
    print("FACEBOOK PAGE")
    if not page:
        print(f"  could not read the Page: {err}")
        return
    print(f"  {page.get('name')}: followers={page.get('followers_count', 'n/a')} likes={page.get('fan_count', 'n/a')}")
    reels, err = _get(f"{page_id}/video_reels", token, fields="id,description,created_time,length", limit=12)
    if not reels:
        reels, err = _get(f"{page_id}/videos", token, fields="id,description,created_time,length,views", limit=12)
    if not reels:
        print(f"  could not list Reels: {err}")
        return
    print("  date        plays   reach   reactions  comments  shares  caption")
    for v in reels.get("data", []):
        m = _metric(v["id"], token, ["blue_reels_play_count", "post_impressions_unique",
                                     "post_video_likes_by_reaction_type", "post_video_social_actions"],
                    edge="video_insights")
        plays = m["blue_reels_play_count"] if m["blue_reels_play_count"] != "n/a" else v.get("views", "n/a")
        react = m["post_video_likes_by_reaction_type"]
        react = sum(react.values()) if isinstance(react, dict) else react
        acts = m["post_video_social_actions"]
        com, sh = (acts.get("COMMENT", 0), acts.get("SHARE", 0)) if isinstance(acts, dict) else ("n/a", "n/a")
        print(f"  {v.get('created_time', '')[:10]}  {plays!s:>6}  {m['post_impressions_unique']!s:>6}  "
              f"{react!s:>9}  {com!s:>8}  {sh!s:>6}  {(v.get('description') or '')[:40]!r}")


def instagram(ig_id: str | None, token: str) -> None:
    if not ig_id:
        return
    print("INSTAGRAM")
    acc, err = _get(ig_id, token, fields="username,followers_count,media_count")
    if not acc:
        print(f"  could not read the account: {err}")
        return
    print(f"  @{acc.get('username')}: followers={acc.get('followers_count', 'n/a')} posts={acc.get('media_count')}")
    media, err = _get(f"{ig_id}/media", token, fields="id,caption,timestamp,like_count,comments_count", limit=12)
    if not media:
        print(f"  could not list posts: {err}")
        return
    print("  date        views   reach   likes  comments  shares  caption")
    for v in media.get("data", []):
        m = _metric(v["id"], token, ["views", "reach", "shares"])
        print(f"  {v.get('timestamp', '')[:10]}  {m['views']!s:>6}  {m['reach']!s:>6}  {v.get('like_count', 'n/a')!s:>5}  "
              f"{v.get('comments_count', 'n/a')!s:>8}  {m['shares']!s:>6}  {(v.get('caption') or '')[:40]!r}")


def main() -> None:
    page_id, token = social._env("META_PAGE_ID"), social._env("META_PAGE_TOKEN")
    if not page_id or not token:
        sys.exit("META_PAGE_ID / META_PAGE_TOKEN are not set.")
    token, _ = social.page_token(page_id, token)
    facebook(page_id, token)
    instagram(social._env("IG_USER_ID"), token)
    if ERRORS:
        print("NOT AVAILABLE FROM META (first error per metric)")
        for m, e in ERRORS.items():
            print(f"  {m}: {e}")


if __name__ == "__main__":
    main()

"""List the channel's private and scheduled videos, and delete the stray copies.

    python -m youtube_agent.private_videos                 # list (marks videos that are not in history.json)
    python -m youtube_agent.private_videos --delete ID ... # delete these, ONLY if private and not in history.json
"""

import sys

from .main import load_history


def _known() -> set:
    ids = set()
    for h in load_history():
        for k in ("youtube_id", "short_youtube_id", "short2_youtube_id"):
            if h.get(k):
                ids.add(h[k])
        ids.update(h.get("replaced_ids", []))
    return ids


def main() -> None:
    from googleapiclient.discovery import build

    from .uploader import _credentials

    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    uploads = youtube.channels().list(part="contentDetails", mine=True).execute()["items"][0][
        "contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < 300:
        r = youtube.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50,
                                         pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    known, private = _known(), {}
    for k in range(0, len(ids), 50):
        for v in youtube.videos().list(part="snippet,status", id=",".join(ids[k:k + 50])).execute()["items"]:
            if v["status"]["privacyStatus"] != "public":
                private[v["id"]] = v
    if "--delete" in sys.argv:
        for vid in sys.argv[sys.argv.index("--delete") + 1:]:
            if vid not in private or vid in known:
                print(f"NOT deleted {vid}: it is public or it is a real video in history.json")
                continue
            youtube.videos().delete(id=vid).execute()
            print(f"Deleted {vid}: {private[vid]['snippet']['title']}")
        return
    for vid, v in private.items():
        s = v["status"]
        mark = "in history" if vid in known else "NOT IN HISTORY (stray copy)"
        print(f"{vid} | {s['privacyStatus']} | publishAt={s.get('publishAt', '-')} | "
              f"{v['snippet']['publishedAt'][:16]} | {mark} | {v['snippet']['title']}")


if __name__ == "__main__":
    main()

"""Public view counts of other health channels' latest videos, for the yt-viral skill (which video beat
its own channel's median by the most). Reads public data only, with our YouTube API access.

    python -m youtube_agent.niche_scan @ClevelandClinic @mayoclinic ...   -> youtube_agent/niche.json
"""
import json
import re
import sys
from pathlib import Path


def _secs(d: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)) if m else 0


def main() -> None:
    from googleapiclient.discovery import build

    from .uploader import _credentials

    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    rows = []
    for handle in sys.argv[1:]:
        ch = yt.channels().list(part="contentDetails,snippet", forHandle=handle.lstrip("@")).execute().get("items")
        if not ch:
            print(f"{handle}: not found")
            continue
        name = ch[0]["snippet"]["title"]
        uploads = ch[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        ids = [i["contentDetails"]["videoId"] for i in yt.playlistItems().list(
            part="contentDetails", playlistId=uploads, maxResults=50).execute()["items"]]
        for v in yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids)).execute()["items"]:
            secs = _secs(v["contentDetails"].get("duration"))
            rows.append({"channel": f"{name} {'Shorts' if secs <= 75 else 'Long'}", "title": v["snippet"]["title"],
                         "views": int(v["statistics"].get("viewCount", 0)), "url": f"https://youtu.be/{v['id']}",
                         "duration": secs, "published": v["snippet"]["publishedAt"][:10]})
        print(f"{handle}: {name}, {len(ids)} videos")
    Path(__file__).with_name("niche.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

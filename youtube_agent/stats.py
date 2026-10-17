"""Channel numbers for deciding what to change: subscribers, and views/likes/comments of recent uploads
(long videos and Shorts), newest first.  python -m youtube_agent.stats"""

from googleapiclient.discovery import build

from .uploader import _credentials


def main() -> None:
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    ch = yt.channels().list(part="statistics,contentDetails,snippet", mine=True).execute()["items"][0]
    s = ch["statistics"]
    print(f"CHANNEL {ch['snippet']['title']}: subscribers={s.get('subscriberCount')} views={s.get('viewCount')} "
          f"videos={s.get('videoCount')}")
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, req = [], yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50)
    while req is not None and len(ids) < 150:
        resp = req.execute()
        ids += [i["contentDetails"]["videoId"] for i in resp.get("items", [])]
        req = yt.playlistItems().list_next(req, resp)
    rows = []
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(ids[k:k + 50])
                                  ).execute().get("items", []):
            st, sn = v["statistics"], v["snippet"]
            dur = v["contentDetails"]["duration"]
            rows.append((sn["publishedAt"][:10], v["status"]["privacyStatus"][:4], dur, int(st.get("viewCount", 0)),
                         int(st.get("likeCount", 0)), int(st.get("commentCount", 0)), v["id"], sn["title"][:70]))
    print("date       priv dur        views likes comm id          title")
    for r in sorted(rows, reverse=True):
        print(f"{r[0]} {r[1]} {r[2]:<10} {r[3]:>5} {r[4]:>5} {r[5]:>4} {r[6]} {r[7]}")


if __name__ == "__main__":
    main()

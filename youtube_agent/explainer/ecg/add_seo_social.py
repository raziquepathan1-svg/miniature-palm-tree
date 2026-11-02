"""Add an episode's search keywords/tags (seo_tags.EP) and Instagram/Facebook Reel captions to the queue."""
import json, sys
from pathlib import Path
REPO = Path(sys.argv[1])
eid, kw, tags, hs, caps = json.loads(Path(sys.argv[2]).read_text()).values()
p = REPO / "youtube_agent/explainer/seo_tags.py"
s = p.read_text()
if f'"{eid}"' not in s:
    entry = f' "{eid}": ({json.dumps(kw)},\n    {json.dumps(tags)},\n    {json.dumps(hs)}),\n}}\n'
    i = s.index("\n}\n", s.index("EP = {"))
    s = s[:i] + "\n" + entry + s[i + 3:]
    p.write_text(s)
sys.path.insert(0, str(REPO))
from youtube_agent.explainer import seo_tags
seo_tags.apply()
q = json.load(open(REPO / "explainer_queue/queue.json"))
tagline = " ".join(dict.fromkeys(hs + ["#" + t.replace(" ", "").replace("/", "") for t in tags[:4]] +
                                 ["#anatomy", "#physiology", "#medicalstudent", "#mbbs", "#nursingstudent", "#theanatomyunfolded"]))
for x in q:
    if x["id"] in caps:
        x["social_caption"] = (f"{' • '.join(kw)}\n\n{caps[x['id']]}\n\nFull video on YouTube: The Anatomy Unfolded (link in bio) 👆\n"
                               f"Follow for a new body explainer every day.\n\n{tagline}")
json.dump(q, open(REPO / "explainer_queue/queue.json", "w"), indent=1, ensure_ascii=False)
print("ok", eid, sum(1 for x in q if x.get("update")))

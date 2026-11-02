"""Owner (2 Nov 2026): search keywords + tags on EVERY upload (videos AND Shorts), and on Instagram/Facebook.
YouTube: description line 1 = 3 exact search phrases, rich tags (<= 480 chars), 3 hashtags at the end.
Instagram/Facebook: keyword first line, keywords in the caption text, 8-12 hashtags."""
import json
from pathlib import Path

Q = Path(__file__).resolve().parents[2] / "explainer_queue" / "queue.json"
BASE = ["anatomy and physiology", "human anatomy", "medical animation", "mbbs", "nursing", "biology",
        "medical students", "cardiovascular system", "the anatomy unfolded"]
EP = {
 "heart_anatomy_v2": (["Heart anatomy", "Anatomy of the heart", "Heart chambers and valves"],
    ["heart anatomy", "anatomy of the heart", "heart chambers", "heart valves", "structure of the heart", "4 chambers of the heart",
     "left ventricle", "right ventricle", "atria", "chordae tendineae", "pericardium", "heart wall layers", "cardiac anatomy"],
    ["#heartanatomy", "#anatomy", "#heart"]),
 "heart_physiology": (["Heart physiology", "Cardiac cycle", "Lub dub heart sounds"],
    ["heart physiology", "cardiac cycle", "systole and diastole", "heart sounds", "lub dub", "how the heart works",
     "blood flow through the heart", "cardiac output", "pulmonary circulation", "systemic circulation", "heart valves closing"],
    ["#physiology", "#cardiaccycle", "#heart"]),
 "heart_electrical": (["Heart electrical system", "Cardiac conduction system", "SA node"],
    ["electrical conduction system of the heart", "cardiac conduction system", "sa node", "av node", "bundle of his",
     "purkinje fibers", "ecg explained", "p wave qrs t wave", "heart pacemaker", "how the heart beats", "heart rate"],
    ["#ecg", "#cardiology", "#heart"]),
 "heart_attack": (["Heart attack", "Heart attack symptoms", "What happens during a heart attack"],
    ["heart attack", "myocardial infarction", "heart attack symptoms", "heart attack warning signs", "coronary artery disease",
     "plaque and blood clot", "heart attack vs cardiac arrest", "cardiac arrest", "chest pain", "time is muscle", "heart attack treatment"],
    ["#heartattack", "#cardiology", "#health"]),
 "blood_vessels": (["Blood vessels", "Arteries vs veins", "Capillaries"],
    ["blood vessels", "arteries vs veins", "arteries veins capillaries", "capillary exchange", "vein valves",
     "artery wall layers", "tunica intima media externa", "pulmonary artery", "circulatory system", "blood circulation"],
    ["#bloodvessels", "#anatomy", "#circulation"]),
 "blood_pressure": (["Blood pressure", "Systolic and diastolic", "What does 120/80 mean"],
    ["blood pressure", "blood pressure explained", "systolic and diastolic", "what does 120/80 mean", "normal blood pressure",
     "how blood pressure is measured", "baroreceptors", "baroreceptor reflex", "raas", "renin angiotensin aldosterone system",
     "blood pressure physiology"],
    ["#bloodpressure", "#physiology", "#health"]),
 "high_blood_pressure": (["High blood pressure", "Hypertension explained", "Silent killer"],
    ["high blood pressure", "hypertension", "hypertension explained", "silent killer", "high blood pressure symptoms",
     "causes of high blood pressure", "primary and secondary hypertension", "left ventricular hypertrophy",
     "hypertensive crisis", "how to lower blood pressure", "blood pressure 130/80"],
    ["#hypertension", "#bloodpressure", "#health"]),
 "heart_failure": (["Heart failure", "Congestive heart failure", "Heart failure symptoms"],
    ["heart failure", "congestive heart failure", "heart failure symptoms", "what is heart failure", "ejection fraction",
     "left sided heart failure", "right sided heart failure", "pitting edema", "bnp test", "echocardiogram",
     "cardiomyopathy", "heart failure treatment"],
    ["#heartfailure", "#cardiology", "#heart"]),
 "arrhythmia": (["Arrhythmia", "Heart skipping beats", "Atrial fibrillation"],
    ["arrhythmia", "heart skipping beats", "atrial fibrillation", "afib", "tachycardia", "bradycardia", "ventricular fibrillation", "palpitations", "premature beats", "irregular heartbeat", "normal heart rate", "cardiac arrest"],
    ["#arrhythmia", "#afib", "#heart"]),
 "heart_valves": (["Heart valve disease", "Valve stenosis and regurgitation", "Heart murmur"],
    ["heart valve disease", "heart valves", "aortic stenosis", "mitral regurgitation", "valve stenosis", "valve regurgitation", "heart murmur", "rheumatic heart disease", "valve replacement", "echocardiogram", "tricuspid pulmonary mitral aortic"],
    ["#heartvalves", "#cardiology", "#heart"]),
}


def tags_for(eid, short=False):
    kw, tags, _ = EP[eid]
    out, seen = [], set()
    for t in tags + (["shorts", "anatomy shorts"] if short else []) + BASE:
        if t.lower() not in seen and sum(len(x) + 3 for x in out) + len(t) + 3 <= 480:
            out.append(t); seen.add(t.lower())
    return out


def apply():
    q = json.loads(Q.read_text())
    for x in q:
        eid = x["id"].split("_short")[0]
        if eid not in EP:
            continue
        kw, _, hs = EP[eid]
        short = x["kind"] == "short"
        line = " • ".join(kw)
        d = x["description"]
        lines = d.split("\n")
        if " • " in lines[0]:
            d = "\n".join(lines[2:] if len(lines) > 1 and lines[1] == "" else lines[1:])
        d = d.rstrip()
        while d.split("\n")[-1].startswith("#") or d.endswith(" #shorts"):   # old hashtag lines -> one merged line
            d = d[: -len(" #shorts")].rstrip() if d.endswith(" #shorts") and not d.split("\n")[-1].startswith("#") else "\n".join(d.split("\n")[:-1]).rstrip()
        tagset = (["#shorts"] if short else []) + hs + ["#anatomy", "#physiology", "#medicalstudent", "#nursing"]
        hashtag = " ".join(dict.fromkeys(tagset))
        new_d = f"{line}\n\n{d}\n\n{hashtag}"
        new_t = tags_for(eid, short)
        if new_d != x["description"] or new_t != x["tags"]:
            x["description"], x["tags"] = new_d, new_t
            if x.get("youtube_id"):
                x["update"] = True
    Q.write_text(json.dumps(q, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    apply()

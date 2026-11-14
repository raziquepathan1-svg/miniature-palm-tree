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
 "lung_anatomy": (["Lung anatomy", "Respiratory system", "Alveoli"],
    ["lung anatomy", "respiratory system", "alveoli", "trachea", "bronchi", "bronchioles", "lobes of the lung", "cardiac notch", "pleura", "diaphragm", "right lung vs left lung", "gas exchange"],
    ["#lunganatomy", "#lungs", "#respiratorysystem"]),
 "how_breathing_works": (["How breathing works", "Diaphragm breathing", "Inhalation and exhalation"],
    ["how breathing works", "mechanism of breathing", "diaphragm", "inhalation and exhalation", "respiratory physiology", "intercostal muscles", "boyles law", "control of breathing", "respiratory rate", "tidal volume", "hemoglobin oxygen", "carbon dioxide breathing"],
    ["#breathing", "#respiratorysystem", "#lungs"]),
 "asthma": (["Asthma", "Asthma attack", "Asthma symptoms"],
    ["asthma", "asthma attack", "asthma symptoms", "asthma triggers", "what is asthma", "asthma inhaler", "reliever vs preventer inhaler", "wheezing", "spirometry", "bronchospasm", "peak flow", "asthma treatment"],
    ["#asthma", "#respiratorysystem", "#lungs"]),
 "pneumonia": (["Pneumonia", "Pneumonia symptoms", "Lung infection"],
    ["pneumonia", "pneumonia symptoms", "what is pneumonia", "lung infection", "bacterial pneumonia", "viral pneumonia", "alveoli", "chest x-ray", "pneumonia treatment", "pneumococcal vaccine", "streptococcus pneumoniae", "respiratory infection"],
    ["#pneumonia", "#lunginfection", "#lungs"]),
 "copd": (["COPD", "Emphysema", "Chronic bronchitis"],
    ["copd", "what is copd", "emphysema", "chronic bronchitis", "copd symptoms", "smoking and lungs", "chronic obstructive pulmonary disease", "spirometry", "copd treatment", "indoor air pollution", "quit smoking", "lung disease"],
    ["#copd", "#lungs", "#quitsmoking"]),
 "brain": (["Brain anatomy", "Parts of the brain", "Brain lobes explained"],
    ["brain anatomy", "parts of the brain", "brain lobes", "frontal lobe", "parietal lobe", "temporal lobe", "occipital lobe", "cerebellum", "brainstem", "hippocampus", "thalamus", "amygdala", "meninges", "cerebrospinal fluid", "nervous system", "phineas gage"],
    ["#brain", "#neuroscience", "#nervoussystem"]),
 "neuron": (["How neurons work", "Action potential explained", "Synapse and neurotransmitters"],
    ["how neurons work", "how brain cells talk", "neuron structure", "action potential", "synapse", "neurotransmitters", "dopamine", "serotonin", "acetylcholine", "myelin sheath", "dendrites and axon", "nerve signal", "reflex arc", "nervous system"],
    ["#neurons", "#neuroscience", "#nervoussystem"]),
 "spine": (["Spinal cord anatomy", "Spinal reflex explained", "Cauda equina"],
    ["spinal cord anatomy", "what does the spinal cord do", "spinal cord function", "spinal reflex", "knee jerk reflex", "reflex arc", "cauda equina", "gray matter and white matter", "dorsal and ventral roots", "meninges", "cerebrospinal fluid", "spinal cord injury", "spinal nerves", "nervous system"],
    ["#spinalcord", "#nervoussystem", "#reflex"]),
 "autonomic": (["Autonomic nervous system", "Sympathetic vs parasympathetic", "Vagus nerve"],
    ["autonomic nervous system", "sympathetic vs parasympathetic", "fight or flight", "rest and digest", "vagus nerve", "vagal tone", "parasympathetic nervous system", "sympathetic nervous system", "acetylcholine", "norepinephrine", "ganglion", "why do people faint", "how the heart rate is controlled", "nervous system"],
    ["#autonomicnervoussystem", "#vagusnerve", "#nervoussystem"]),
 "endocrine": (["Endocrine system explained", "Hormones and glands", "Pituitary, thyroid, adrenal, pancreas"],
    ["endocrine system", "what does the endocrine system do", "hormones explained", "endocrine glands", "pituitary gland", "thyroid gland", "adrenal gland", "cortisol and adrenaline", "insulin and glucagon", "hypothalamus", "feedback loop", "master gland", "metabolism", "anatomy and physiology"],
    ["#endocrinesystem", "#hormones", "#physiology"]),
 "digestive": (["Digestive system explained", "How digestion works", "Stomach and small intestine"],
    ["digestive system", "how does digestion work", "digestive system explained", "stomach acid", "why stomach doesn't digest itself", "small intestine", "villi", "bile and pancreatic enzymes", "peristalsis", "large intestine", "gut bacteria", "how long does digestion take", "anatomy and physiology"],
    ["#digestivesystem", "#digestion", "#stomach"]),
 "kidney": (["How kidneys work", "Nephron and urine formation", "Kidney anatomy"],
    ["how do kidneys work", "kidney anatomy", "kidney function", "nephron", "glomerulus", "urine formation", "tubular reabsorption", "renal artery and vein", "erythropoietin", "renin", "urinary system", "ureter bladder urethra", "anatomy and physiology"],
    ["#kidneys", "#urinarysystem", "#nephron"]),
 "immune": (["Immune system explained", "Innate vs adaptive immunity", "T cells and B cells"],
    ["how does the immune system work", "immune system explained", "innate vs adaptive immunity", "inflammation", "neutrophils", "macrophages", "t cells", "b cells and antibodies", "memory cells", "how vaccines work", "lymph nodes", "white blood cells", "anatomy and physiology"],
    ["#immunesystem", "#immunity", "#tcells"]),
 "skin": (["Skin anatomy explained", "Layers of the skin", "Melanin and keratin"],
    ["what does skin do", "skin anatomy", "layers of the skin", "epidermis dermis hypodermis", "keratin", "melanin", "melanocytes", "sweat glands", "sebaceous glands", "collagen", "vitamin D from sunlight", "why skin cells are dead", "anatomy and physiology"],
    ["#skin", "#skinanatomy", "#melanin"]),
 "musc": (["Musculoskeletal system explained", "Bones and muscles", "How muscles contract"],
    ["musculoskeletal system", "how do bones and muscles work", "how many bones do babies have", "206 bones", "bone remodeling", "tendons and ligaments", "joints", "types of muscle", "how muscles contract", "biceps and triceps", "actin and myosin", "skeletal muscle", "anatomy and physiology"],
    ["#musculoskeletal", "#bones", "#muscles"]),
 "lymph": (["Lymphatic system explained", "Lymph nodes", "How lymph drains"],
    ["lymphatic system", "what does the lymphatic system do", "lymph nodes", "what is lymph", "lymphatic drainage", "lymphedema", "spleen thymus tonsils", "lacteals", "subclavian vein", "swollen lymph nodes", "interstitial fluid", "immune system", "anatomy and physiology"],
    ["#lymphaticsystem", "#lymphnodes", "#lymph"]),
 "eye": (["How the eye works", "Retina, rods and cones", "The blind spot"],
    ["how does the eye see", "eye anatomy", "how the eye works", "retina rods and cones", "why image is upside down on the retina", "blind spot", "optic nerve", "cornea pupil iris lens", "fovea", "color vision cones", "vision explained", "senses", "anatomy and physiology"],
    ["#eyeanatomy", "#vision", "#retina"]),
}


def tags_for(eid, short=False):
    kw, tags, _ = EP[eid]
    out, seen = [], set()
    base = [b for b in BASE if not (eid in ("brain", "neuron", "spine", "autonomic", "endocrine", "digestive", "kidney", "immune", "skin", "musc", "lymph", "eye") and b == "cardiovascular system")]
    for t in tags + (["shorts", "anatomy shorts"] if short else []) + base:
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

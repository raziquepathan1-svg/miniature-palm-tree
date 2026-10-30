#!/usr/bin/env python3
"""Build beat-synced Reels from reels/raw3 clips.
Usage: build_reels.py REEL_NO [REEL_NO...]   (or 'all')
Each reel: 1.5s teaser + opening (first clip) + clips, slow-mo per outfit, hook text 0-2.4s, song1 music, loop end."""
import subprocess, sys, os, tempfile
R = os.path.dirname(os.path.abspath(__file__)) + "/.."
RAW = R + "/raw3/"
FILES = open(os.environ.get("CLIPLIST", R + "/tools/raw3_list.txt")).read().split("\n")
B = 0.789          # one beat of song1 (76 bpm)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def single(walk=3.5, end=7.0):            # one outfit clip: walk, slow walk, end look (4 beats)
    return [(walk, 1, 0), (walk + 0.8, 2, 1), (end, 1, 0)]
def multi(*outs):                          # multi-outfit clip: list of (a, b) outfit intervals
    seg = []
    for k, (a, b) in enumerate(outs):
        if k == 0 and b - a >= 1.9:
            seg += [(a + 0.1, 1, 0), (a + 0.9, 2, 1)]
        else:
            seg += [(max(a, (a + b) / 2 - 0.4), 2, 1)]
    return seg
S, M = single, multi
CLIP = {i: S() for i in list(range(0, 23)) + list(range(76, 101))}
CLIP.update({
 23: [(0.3,1,0),(1.5,2,1),(4.5,1,0),(6.8,1,0)],
 24: [(0.2,2,1),(2.0,1,0),(4.0,1,0),(6.8,1,0)],
 25: M((1.0,3.0),(3.0,4.5),(4.5,6.0),(6.5,8.0)),
 26: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 27: M((2.0,4.0),(4.0,6.0),(7.0,8.0)),
 28: M((1.5,3.5),(3.5,5.0),(5.0,6.5)) + [(6.55,1,1)],
 29: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 30: M((2.0,4.0),(4.0,6.0),(7.0,8.0)),
 31: M((1.5,3.5),(3.5,5.0),(5.0,6.0),(6.5,8.0)),
 32: M((2.0,4.0),(4.0,6.0),(7.0,8.0)),
 33: M((1.5,3.5),(3.5,5.5),(5.5,8.0)),
 34: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,7.0)),
 35: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 36: [(0.2,1,0),(2.2,2,1),(6.3,1,0)],
 37: [(0.2,1,0),(4.3,2,1),(6.5,1,0)],
 38: [(0.3,1,0),(2.5,1,0),(5.0,2,1),(7.0,1,0)],
 39: M((0.0,3.0),(3.0,5.5),(5.5,6.5)) + [(7.0,1,0)],
 40: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 41: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 42: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 43: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 44: M((1.5,3.5),(3.5,5.5),(5.5,8.0)),
 45: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 46: M((2.5,4.0),(4.0,6.0),(6.5,8.0)),
 47: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 48: M((2.5,3.5),(3.5,5.0)),
 49: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 50: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 52: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 53: M((1.5,3.5),(3.5,5.0),(5.0,5.8),(6.5,8.0)),
 54: [(0.2,1,0),(1.0,2,1),(2.5,1,0),(6.5,1,0)],
 55: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 56: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 57: [(0.2,1,0),(1.0,2,1),(2.5,1,0),(6.5,1,0)],
 59: M((2.5,4.0),(4.0,6.0),(6.0,8.0)),
 60: M((2.5,4.0),(4.5,6.0),(6.0,8.0)),
 61: M((2.5,4.0),(4.0,6.0),(6.0,8.0)),
 62: M((0.0,3.0),(3.0,5.5),(5.5,6.5)) + [(7.0,1,0)],
 63: M((2.5,4.0),(4.0,6.0),(6.0,8.0)),
 64: M((2.5,4.0),(4.5,6.5),(6.5,8.0)),
 65: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 66: M((2.0,4.0),(4.5,6.0),(6.0,8.0)),
 67: M((1.5,3.5),(3.5,5.0)) + [(5.0,1,1)] + M((6.5,8.0)),
 68: M((2.0,4.0),(5.0,6.0),(6.0,8.0)),
 69: M((2.0,4.0),(4.0,6.0),(6.0,8.0)),
 70: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 71: M((2.0,4.0),(4.0,6.0),(7.0,8.0)),
 72: [(0.5,1,0),(3.0,1,0),(5.5,2,1),(7.0,1,0)],
 73: M((1.5,3.5),(3.5,5.0),(5.0,6.5),(6.5,8.0)),
 75: [(1.5,1,0),(3.5,2,1),(5.5,1,0),(7.0,1,0)],
 101: [(0.5,1,0),(3.5,2,1),(7.0,1,0)],
 102: [(0.3,1,0),(1.3,2,1),(3.6,1,0),(6.5,1,0)],
 103: [(1.0,1,0),(1.8,2,1),(2.6,1,0),(6.8,1,0)],
 104: M((0.0,3.0),(3.0,6.5),(6.5,8.0)),
 105: [(0.3,1,0),(1.2,2,1),(6.5,1,0)],
 106: [(0.3,1,0),(1.2,2,1),(6.0,1,0)],
 107: M((0.5,2.0),(2.0,4.0),(5.0,6.0),(6.0,8.0)),
 108: [(0.3,1,0),(1.3,2,1),(3.6,1,0),(6.5,1,0)],
 109: [(0.3,1,0),(1.2,2,1),(5.0,1,0),(7.0,1,0)],
})
MULTI_OPEN = {25,26,27,28,29,30,31,32,33,34,35,40,41,42,43,44,45,46,47,48,49,50,52,53,55,56,59,60,61,63,64,65,66,67,68,69,70,71,73}
def opening(i):
    if i in MULTI_OPEN:
        return [(0.0, 2, 0)]
    if i in CLIP and CLIP[i][0][0] >= 3.0:   # single with macro+hold+toss at start
        return [(0.07, 4, 0)]
    return []

# reel: (title, teaser (clip, start), [clips], hook line1, hook line2, blur list (clip, x,y,w,h))
REELS = {
 2: ("suits_b", (47, 6.3), [0, 3, 4, 47], "POV: you dress for", "the life you want"),
 3: ("suits_c", (68, 6.4), [68, 82, 78, 44], "Suits that speak", "before you do"),
 4: ("tuxedo", (52, 5.1), [52, 92, 86, 9, 60], "POV: black tie is", "your comfort zone"),
 5: ("blazers", (42, 6.6), [42, 38, 55, 59], "One blazer", "changes everything"),
 6: ("old_money", (56, 6.2), [56, 29, 15, 72, 76], "POV: old money", "summer energy"),
 7: ("knitwear_a", (28, 5.1), [28, 94, 95], "POV: knitwear season", "just started"),
 8: ("knitwear_b", (39, 3.2), [39, 77, 5], "Soft knits.", "Sharp man."),
 9: ("coats_a", (43, 3.6), [43, 7, 11, 54], "POV: your coat", "enters first"),
 10: ("winter_coats", (70, 6.6), [70, 22, 71, 69], "Winter is my", "favourite runway"),
 11: ("autumn", (27, 4.2), [27, 99, 30, 23, 10], "POV: autumn fits", "hit different"),
 12: ("leather", (41, 6.6), [41, 104, 75, 109], "Leather never", "goes out of style"),
 13: ("street_a", (31, 3.6), [31, 14, 105, 84], "POV: street style", "but make it luxury"),
 14: ("street_b", (73, 3.6), [73, 90, 79, 50], "POV: off-duty", "but still iconic"),
 15: ("overshirts", (49, 5.1), [49, 57, 17, 19], "The overshirt", "every man needs"),
 16: ("layers", (46, 6.6), [46, 107, 62, 13], "POV: you mastered", "the art of layering"),
 17: ("summer_a", (67, 6.6), [67, 6, 12, 102], "POV: summer in linen", "hits different"),
 18: ("summer_b", (66, 6.3), [66, 18, 108], "Sunlight. Linen.", "No worries."),
 19: ("safari_desert", (32, 4.2), [64, 83, 61, 32], "POV: you dress like", "you own the desert"),
 20: ("night_out", (65, 6.3), [65, 20, 106, 93], "POV: the night", "is yours"),
 21: ("pathani", (25, 6.6), [25, 88, 101, 36], "POV: Pathani suit", "with full swag"),
 22: ("kurta", (45, 5.1), [45, 98, 37, 40], "Simple kurta.", "Royal vibes."),
 23: ("nehru_jacket", (34, 3.6), [34, 96, 97, 2], "POV: the Nehru jacket", "does the talking"),
 24: ("sherwani", (53, 3.6), [53, 24, 16, 80], "POV: you are the", "best-dressed groom"),
 25: ("festive_a", (35, 6.6), [35, 85, 100, 21], "Festive season", "calls for this"),
 26: ("festive_b", (33, 6.0), [33, 87, 81, 1], "POV: desi royalty", "unlocked"),
 27: ("ethnic_heritage", (26, 4.2), [26, 48, 63], "Heritage in", "every thread"),
}
BLUR = {94: [(570, 580, 140, 140, 0, 6.5), (700, 965, 140, 140, 6.5, 8)]}   # chest logo boxes (x,y,w,h,t0,t1) on 1080x1920 (clip 94)

def run(c): subprocess.run(c, check=True)

def build(n):
    title, (tc, ts), clips, h1, h2 = REELS[n]
    segs = [(tc, ts, 2, 0)]
    for k, c in enumerate(clips):
        parts = (opening(c) if k == 0 else []) + CLIP[c]
        segs += [(c, st, b, sl) for st, b, sl in parts]
    args, total = [], 0.0
    W = tempfile.mkdtemp()
    for c, st, b, sl in segs:
        f = RAW + FILES[c]
        if c in BLUR:     # pre-blur logo clip once
            bf = f"{W}/blur{c}.mp4"
            if not os.path.exists(bf):
                fc, prev = "[0:v]scale=1080:1920,setsar=1[v0]", "v0"
                for k, (x, y, w, h, t0, t1) in enumerate(BLUR[c]):
                    fc += f";[{prev}]split[m{k}][s{k}];[s{k}]crop={w}:{h}:{x}:{y},boxblur=14[b{k}];[m{k}][b{k}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[v{k+1}]"
                    prev = f"v{k+1}"
                run(["ffmpeg","-nostdin","-v","error","-y","-i",f,"-filter_complex",fc,"-map",f"[{prev}]",
                     "-c:v","libx264","-crf","14","-preset","fast","-an",bf])
            f = bf
        dur = b * B / 2 if sl else b * B
        st = min(st, 8.0 - dur - 0.02)
        args.append(f"{f}|{st:.3f}|{dur:.3f}|0" + ("|0.5" if sl else ""))
        total += b * B
    base = f"{W}/base.mp4"
    run(["bash", R + "/tools/make_reel.sh", base] + args)
    for k, t in enumerate((h1, h2)):
        open(f"{W}/t{k}.txt", "w").write(t)
    st = "fontsize=60:fontcolor=white:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-tw)/2:enable='between(t,0.15,2.4)':alpha='if(lt(t,0.35),(t-0.15)/0.2,if(gt(t,2.2),(2.4-t)/0.2,1))'"
    vf = f"drawtext=fontfile={FONT}:textfile={W}/t0.txt:y=45:{st},drawtext=fontfile={FONT}:textfile={W}/t1.txt:y=115:{st}"
    out = f"{R}/final/reel{n:02d}_{title}.mp4"
    run(["ffmpeg","-nostdin","-v","error","-y","-t",f"{total:.3f}","-i",base,"-stream_loop","-1","-i",R+"/music/song1.mp3",
         "-map","0:v","-map","1:a","-vf",vf,"-af",f"afade=t=in:d=0.05,afade=t=out:st={total-0.35:.3f}:d=0.35","-t",f"{total:.3f}",
         "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",out])
    subprocess.run(["rm","-rf",W])
    print(f"reel {n}: {out} {total:.1f}s clips {clips}", flush=True)

if __name__ == "__main__":
    ns = sorted(REELS) if sys.argv[1:] == ["all"] else [int(a) for a in sys.argv[1:]]
    for n in ns: build(n)

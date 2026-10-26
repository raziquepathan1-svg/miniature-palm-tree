#!/usr/bin/env python3
"""Add one smooth slow-motion moment (0.8s source -> 1.6s) in the middle of each shot
that starts after the 3-second hook. Shots found by scene-cut detection.
Usage: add_slowmo.py IN.mp4 OUT.mp4"""
import subprocess, sys, re, tempfile, os
IN, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.join(HERE, '..', 'music', 'song1.mp3')
def dur(f):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
D = dur(IN)
log = subprocess.run(['ffmpeg','-i',IN,'-vf',"select='gt(scene,0.30)',showinfo",'-f','null','-'],capture_output=True,text=True).stderr
cuts = sorted(set(round(float(t),3) for t in re.findall(r'pts_time:([\d.]+)', log)))
bounds = [0.0] + cuts + [D]
slows = []
for s, e in zip(bounds, bounds[1:]):
    s2 = max(s, 3.0)
    if e - s2 >= 2.0:
        c = (s2 + e) / 2
        slows.append((round(c - 0.4, 3), round(c + 0.4, 3)))
pieces, t = [], 0.0
for a, b in slows:
    pieces.append((t, a, 1)); pieces.append((a, b, 0.5)); t = b
pieces.append((t, D, 1))
W = tempfile.mkdtemp()
ENC = ['-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-an','-r','24']
lst = []
for i, (a, b, sp) in enumerate(pieces):
    if b - a < 0.05: continue
    vf = 'fps=24' if sp == 1 else 'minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=PTS*2,fps=24'
    o = f'{W}/p{i}.mp4'
    subprocess.check_call(['ffmpeg','-v','error','-y','-ss',str(a),'-t',str(b-a),'-i',IN,'-vf',vf]+ENC+[o])
    lst.append(f"file '{o}'")
open(f'{W}/l.txt','w').write('\n'.join(lst))
subprocess.check_call(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{W}/l.txt','-c','copy',f'{W}/v.mp4'])
d = dur(f'{W}/v.mp4')
subprocess.check_call(['ffmpeg','-v','error','-y','-i',f'{W}/v.mp4','-stream_loop','-1','-i',MUSIC,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={d-0.3:.2f}:d=0.3','-t',f'{d:.3f}','-movflags','+faststart',OUT])
print(OUT, f'{D:.1f}s -> {d:.1f}s', 'slow at', slows)

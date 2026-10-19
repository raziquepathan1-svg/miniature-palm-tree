#!/usr/bin/env bash
# Usage: make_reel.sh OUT.mp4 "file|start|dur|flash" ...   (flash = 1 for white flash at segment start)
# Clean 1080x1920 Reel, no text, silent audio track, last frame held 1s with fade-out.
set -e
OUT="$1"; shift
W=$(mktemp -d)
G="scale=1080:1920:flags=lanczos,setsar=1,eq=contrast=1.05:saturation=1.06,vignette=PI/5,fps=24"
ENC="-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -an"
i=0; : > "$W/list.txt"; last=""
for seg in "$@"; do
  IFS='|' read -r f st du fl <<< "$seg"
  vf="$G"; [ "$fl" = "1" ] && vf="$vf,fade=in:st=0:d=0.15:color=white"
  ffmpeg -v error -y -ss "$st" -t "$du" -i "$f" -vf "$vf" $ENC "$W/s$i.mp4"
  echo "file s$i.mp4" >> "$W/list.txt"; last="$W/s$i.mp4"; i=$((i+1))
done
ffmpeg -v error -y -sseof -0.05 -i "$last" -frames:v 1 "$W/last.png"
ffmpeg -v error -y -loop 1 -t 1.0 -i "$W/last.png" -vf "scale=1080:1920,setsar=1,fps=24,fade=out:st=0.6:d=0.4" $ENC "$W/end.mp4"
echo "file end.mp4" >> "$W/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$W/list.txt" -f lavfi -i anullsrc=r=48000:cl=stereo -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
rm -rf "$W"

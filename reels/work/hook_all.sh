#!/usr/bin/env bash
# Apply 3-second-rule hook to reels 7-34 (6 and 30 done separately)
cd "$(dirname "$0")/.."
for f in final/reel*.mp4; do
  b=$(basename "$f" .mp4); n=$(echo "$b" | sed -E 's/reel0?([0-9]+)_.*/\1/')
  [ "$n" -lt 7 ] && continue; [ "$n" -eq 30 ] && continue
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  bash tools/hookify.sh "$f" "final/hooked/${b}_hook.mp4" $(echo "$d-2.0"|bc) 1.0 $(echo "$d-1.0"|bc)
done

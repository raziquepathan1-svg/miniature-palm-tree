#!/usr/bin/env bash
# 3-second-rule re-edit of a finished Reel (no text):
#  - opens with a 1s "teaser" of the best final look (cold open), so the first frame is the payoff
#  - removes the fade-to-black ending so the last hero shot loops straight back into the teaser
#  - fresh music from 0s so the beat hits on frame 1
# Usage: hookify.sh IN.mp4 OUT.mp4 TEASER_START TEASER_DUR MAIN_END
set -e
IN=$1; OUT=$2; TS=$3; TD=$4; ME=$5
W=$(mktemp -d)
ENC="-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -an -r 24"
ffmpeg -v error -y -ss "$TS" -t "$TD" -i "$IN" $ENC "$W/a.mp4"
ffmpeg -v error -y -t "$ME" -i "$IN" $ENC "$W/b.mp4"
printf "file a.mp4\nfile b.mp4\n" > "$W/l.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$W/l.txt" -c copy "$W/v.mp4"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/v.mp4")
ffmpeg -v error -y -i "$W/v.mp4" -i "$(dirname "$0")/../music/song1.mp3" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "afade=t=out:st=$(echo "$d-0.3"|bc):d=0.3" -t "$d" -movflags +faststart "$OUT"
rm -rf "$W"; echo "$OUT $d"

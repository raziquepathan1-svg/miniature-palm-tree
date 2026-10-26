#!/usr/bin/env bash
cd "$(dirname "$0")/.."
for n in $(seq 7 27); do
  f=$(ls final/hooked/reel$(printf %02d $n)_*_hook.mp4)
  python3 tools/add_slowmo.py "$f" "${f%.mp4}.tmp.mp4" && mv "${f%.mp4}.tmp.mp4" "$f"
done
echo ALLDONE

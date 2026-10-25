#!/usr/bin/env bash
# Reels 28-34 (Oct 25 clips) with slow motion on every look + music
set -e
cd "$(dirname "$0")/.."
R=raw2
mk(){ out=$1; shift; tmp=$(mktemp --suffix .mp4); bash tools/make_reel.sh "$tmp" "$@"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$tmp")
  ffmpeg -v error -y -i "$tmp" -i music/song1.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "afade=t=out:st=$(echo "$d-1.2"|bc):d=1.2" -t "$d" -movflags +faststart "final/$out"; rm -f "$tmp"; echo "$out $d"; }

K=$R/Man_modeling_knitwear_on_walking__20261025114214.mp4
mk reel28_knit_edit.mp4 "$K|0|1.2|0" "$K|1.2|0.8|0|0.5" "$K|2.0|0.78|0" "$K|2.92|0.48|0" "$K|3.4|0.8|0|0.5" "$K|4.2|1.28|0" "$K|5.78|0.42|0" "$K|6.2|0.8|0|0.5" "$K|7.0|1.0|0"

O=work/office_blur.mp4
mk reel29_modern_office.mp4 "$O|0|1.82|0" "$O|2.15|0.45|0" "$O|2.6|0.8|0|0.5" "$O|3.4|1.2|0" "$O|4.6|0.8|0|0.5" "$O|5.4|1.2|0" "$O|6.6|0.8|0|0.5" "$O|7.4|0.6|0"

C=$R/Man_modeling_countryside_menswea__20261025120123.mp4
mk reel30_countryside.mp4 "$C|0|3.0|0" "$C|3.0|0.8|0|0.5" "$C|3.8|0.6|0" "$C|4.4|0.8|0|0.5" "$C|5.2|1.0|0" "$C|6.2|0.8|0|0.5" "$C|7.0|1.0|0"

M=$R/Man_modeling_luxury_fashion_outfits_20261025120638.mp4
mk reel31_moroccan_luxury.mp4 "$M|0|1.42|0" "$M|1.65|0.55|0" "$M|2.2|0.8|0|0.5" "$M|3.0|1.3|0" "$M|4.3|0.8|0|0.5" "$M|5.1|1.3|0" "$M|6.4|0.8|0|0.5" "$M|7.2|0.8|0"

J=$R/Man_modeling_luxury_menswear_com__20261025121059.mp4
mk reel32_japanese_minimal.mp4 "$J|0|1.62|0" "$J|2.2|0.4|0" "$J|2.6|0.8|0|0.5" "$J|3.4|1.2|0" "$J|4.6|0.8|0|0.5" "$J|5.4|1.2|0" "$J|6.6|0.8|0|0.5" "$J|7.4|0.6|0"

I=work/istanbul_blur.mp4
mk reel33_istanbul_winter.mp4 "$I|0|2.5|0" "$I|2.5|0.8|0|0.5" "$I|3.3|1.3|0" "$I|4.6|0.8|0|0.5" "$I|5.4|0.8|0" "$I|6.2|0.8|0|0.5" "$I|7.0|1.0|0"

A=$R/Man_modeling_winter_clothing_20261025122223.mp4
mk reel34_alpine_apres_ski.mp4 "$A|0|2.5|0" "$A|2.5|0.8|0|0.5" "$A|3.3|1.3|0" "$A|4.6|0.8|0|0.5" "$A|5.4|1.3|0" "$A|6.7|0.8|0|0.5" "$A|7.5|0.5|0"

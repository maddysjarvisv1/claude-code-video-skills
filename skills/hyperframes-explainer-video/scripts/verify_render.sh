#!/bin/bash
# Verify a HyperFrames-rendered MP4 is complete AND has real audio.
# Usage: bash verify_render.sh /path/to/output.mp4
set -e
MP4="${1:-}"
if [ -z "$MP4" ] || [ ! -f "$MP4" ]; then echo "Usage: $0 /path/to/render.mp4"; exit 2; fi

echo "=== streams (need h264 video + aac audio) ==="
ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,duration -of compact=p=0:nk=1 "$MP4"

echo "=== duration + size ==="
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$MP4"

echo "=== audio volume (non-silent if max_volume well above -30 dB) ==="
ffmpeg -i "$MP4" -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"

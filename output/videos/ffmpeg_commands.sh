#!/bin/bash
# FFmpeg commands to create the final video
# Run these once ffmpeg is installed

VIDEO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_VIDEO="/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/04bde690-Module_00__Set_up_your_AI_content_studio.mp4"
OUTPUT="${VIDEO_DIR}/Module_00_Complete.mp4"

echo "Creating intro video..."
ffmpeg -loop 1 -i "${VIDEO_DIR}/intro_title_card.png" -c:v libx264 -preset fast -crf 18 \
  -pix_fmt yuv420p -t 3 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \
  "${VIDEO_DIR}/intro.mp4" -y

echo "Creating image overlay videos..."
for i in 1 2 3 4; do
  ffmpeg -loop 1 -i "${VIDEO_DIR}/image_overlay_${i}.png" -c:v libx264 -preset fast -crf 18 \
    -pix_fmt yuv420p -t 2 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \
    "${VIDEO_DIR}/image_overlay_${i}.mp4" -y
done

echo "Creating outro video..."
ffmpeg -loop 1 -i "${VIDEO_DIR}/outro_cta_card.png" -c:v libx264 -preset fast -crf 18 \
  -pix_fmt yuv420p -t 3 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \
  "${VIDEO_DIR}/outro.mp4" -y

echo "Creating concatenation file..."
cat > "${VIDEO_DIR}/concat.txt" << 'EOF'
file '${VIDEO_DIR}/intro.mp4'
file '${MAIN_VIDEO}'
file '${VIDEO_DIR}/image_overlay_1.mp4'
file '${VIDEO_DIR}/image_overlay_2.mp4'
file '${VIDEO_DIR}/image_overlay_3.mp4'
file '${VIDEO_DIR}/image_overlay_4.mp4'
file '${VIDEO_DIR}/outro.mp4'
EOF

echo "Creating final video..."
ffmpeg -f concat -safe 0 -i "${VIDEO_DIR}/concat.txt" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  "${OUTPUT}" -y

echo "✅ Video created: ${OUTPUT}"
ls -lh "${OUTPUT}"

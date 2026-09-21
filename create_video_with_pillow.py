#!/usr/bin/env python3
"""
AI Content Engine Video Creator (Alternative - Image-based approach)
Creates video overlays and preparation files for engagement
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_title_card(width, height, output_path, title, subtitle):
    """Create a branded title card image."""
    img = Image.new('RGB', (width, height), color=(14, 11, 31))  # Dark navy background
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Draw title (cyan color: #4DD9E8)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = (height // 2) - 100
    draw.text((title_x, title_y), title, fill=(77, 217, 232), font=title_font)

    # Draw subtitle (light purple: #F3EEFF)
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 100
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(243, 238, 255), font=subtitle_font)

    img.save(output_path)
    print(f"✓ Created: {output_path}")

def create_image_overlay(input_image, width, height, step_number, output_path):
    """Add step overlay to an image."""
    # Open and resize the input image
    img = Image.open(input_image)
    img.thumbnail((width, height), Image.Resampling.LANCZOS)

    # Create a new image with padding
    final_img = Image.new('RGB', (width, height), color=(14, 11, 31))
    x_offset = (width - img.width) // 2
    y_offset = (height - img.height) // 2
    final_img.paste(img, (x_offset, y_offset))

    # Add header bar
    draw = ImageDraw.Draw(final_img)
    draw.rectangle([(0, 0), (width, 80)], fill=(14, 11, 31, 230))

    # Add step text
    try:
        step_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        step_font = ImageFont.load_default()

    step_text = f"Step {step_number}"
    text_bbox = draw.textbbox((0, 0), step_text, font=step_font)
    text_x = 30
    text_y = (80 - (text_bbox[3] - text_bbox[1])) // 2
    draw.text((text_x, text_y), step_text, fill=(77, 217, 232), font=step_font)

    final_img.save(output_path)
    print(f"✓ Created: {output_path}")

def create_cta_card(width, height, output_path):
    """Create a call-to-action card."""
    img = Image.new('RGB', (width, height), color=(14, 11, 31))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Main CTA text
    main_text = "Ready to Build Your Content Engine?"
    main_bbox = draw.textbbox((0, 0), main_text, font=title_font)
    main_width = main_bbox[2] - main_bbox[0]
    main_x = (width - main_width) // 2
    main_y = (height // 2) - 60
    draw.text((main_x, main_y), main_text, fill=(77, 217, 232), font=title_font)

    # Subtitle text
    sub_text = "Start creating engaging content today"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=subtitle_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_width) // 2
    sub_y = main_y + 100
    draw.text((sub_x, sub_y), sub_text, fill=(243, 238, 255), font=subtitle_font)

    img.save(output_path)
    print(f"✓ Created: {output_path}")

def create_video_metadata(output_dir):
    """Create metadata file describing the video composition."""
    metadata = {
        "project": "AI Content Engine",
        "module": "00",
        "title": "Set Up Your AI Content Studio",
        "branding": {
            "colors": {
                "primary": "#4DD9E8",
                "secondary": "#F3EEFF",
                "background": "#0E0B1F"
            },
            "fonts": ["DejaVuSans-Bold", "DejaVuSans"]
        },
        "video_spec": {
            "resolution": "1920x1080",
            "fps": 30,
            "duration_intro": 3,
            "duration_main": None,
            "duration_images": 2,
            "duration_outro": 3
        },
        "assets_created": {
            "intro": "intro_title_card.png",
            "images": ["image_overlay_1.png", "image_overlay_2.png", "image_overlay_3.png", "image_overlay_4.png"],
            "outro": "outro_cta_card.png"
        },
        "instructions": "Use ffmpeg to convert these images into videos and concatenate with main video"
    }

    metadata_path = output_dir / "video_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Created metadata: {metadata_path}")

def main():
    base_dir = Path("/home/user/AI-Future-Mindset-Video-Editor-Suite")
    tmp_images_dir = Path("/tmp/claude-0/-home-user-AI-Future-Mindset-Video-Editor-Suite/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/images")
    output_dir = base_dir / "output" / "videos"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Video specifications
    width, height = 1920, 1080

    print("🎬 AI Content Engine - Video Asset Creator")
    print("=" * 60)
    print(f"Creating video assets in: {output_dir}")
    print(f"Resolution: {width}x{height}")

    # Create title card
    print("\n📝 Creating title card...")
    create_title_card(
        width, height,
        output_dir / "intro_title_card.png",
        "AI CONTENT ENGINE",
        "Module 00: Set Up Your AI Content Studio"
    )

    # Create image overlays
    print("\n🖼️  Creating image overlays...")
    for i in range(1, 5):
        img_path = tmp_images_dir / f"{i}.png"
        if img_path.exists():
            create_image_overlay(
                img_path,
                width, height,
                i,
                output_dir / f"image_overlay_{i}.png"
            )
        else:
            print(f"⚠️  Image {i} not found: {img_path}")

    # Create CTA card
    print("\n📢 Creating call-to-action card...")
    create_cta_card(
        width, height,
        output_dir / "outro_cta_card.png"
    )

    # Create metadata
    print("\n📋 Creating metadata...")
    create_video_metadata(output_dir)

    # Create FFmpeg command file
    ffmpeg_cmd_file = output_dir / "ffmpeg_commands.sh"
    with open(ffmpeg_cmd_file, 'w') as f:
        f.write("""#!/bin/bash
# FFmpeg commands to create the final video
# Run these once ffmpeg is installed

VIDEO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_VIDEO="/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/04bde690-Module_00__Set_up_your_AI_content_studio.mp4"
OUTPUT="${VIDEO_DIR}/Module_00_Complete.mp4"

echo "Creating intro video..."
ffmpeg -loop 1 -i "${VIDEO_DIR}/intro_title_card.png" -c:v libx264 -preset fast -crf 18 \\
  -pix_fmt yuv420p -t 3 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \\
  "${VIDEO_DIR}/intro.mp4" -y

echo "Creating image overlay videos..."
for i in 1 2 3 4; do
  ffmpeg -loop 1 -i "${VIDEO_DIR}/image_overlay_${i}.png" -c:v libx264 -preset fast -crf 18 \\
    -pix_fmt yuv420p -t 2 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \\
    "${VIDEO_DIR}/image_overlay_${i}.mp4" -y
done

echo "Creating outro video..."
ffmpeg -loop 1 -i "${VIDEO_DIR}/outro_cta_card.png" -c:v libx264 -preset fast -crf 18 \\
  -pix_fmt yuv420p -t 3 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \\
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
ffmpeg -f concat -safe 0 -i "${VIDEO_DIR}/concat.txt" \\
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \\
  -c:a aac -b:a 192k \\
  "${OUTPUT}" -y

echo "✅ Video created: ${OUTPUT}"
ls -lh "${OUTPUT}"
""")

    os.chmod(ffmpeg_cmd_file, 0o755)
    print(f"✓ Created FFmpeg script: {ffmpeg_cmd_file}")

    print("\n" + "=" * 60)
    print("✅ Asset Creation Complete!")
    print("=" * 60)
    print(f"\n📦 Assets created in: {output_dir}")
    print(f"   - intro_title_card.png")
    print(f"   - image_overlay_1-4.png")
    print(f"   - outro_cta_card.png")
    print(f"   - video_metadata.json")
    print(f"\n🎬 Next: Install ffmpeg and run:")
    print(f"   bash {ffmpeg_cmd_file}")

if __name__ == "__main__":
    main()

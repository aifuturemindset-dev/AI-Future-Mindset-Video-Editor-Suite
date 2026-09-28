#!/usr/bin/env python3
"""Create professional YouTube/social media thumbnail from intro card."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_youtube_thumbnail():
    """Create 1280x720 YouTube thumbnail."""
    # Create base image
    img = Image.new('RGB', (1280, 720), color=(14, 11, 31))
    draw = ImageDraw.Draw(img)

    # Load or create fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Add gradient background effect with rectangles
    for i in range(720):
        ratio = i / 720
        r = int(14 * (1 - ratio * 0.2))
        g = int(11 * (1 - ratio * 0.1))
        b = int(31 * (1 + ratio * 0.3))
        draw.rectangle([(0, i), (1280, i+1)], fill=(r, g, b))

    # Add accent bars
    draw.rectangle([(0, 0), (1280, 40)], fill=(77, 217, 232))
    draw.rectangle([(0, 680), (1280, 720)], fill=(77, 217, 232))

    # Add main title
    title = "AI CONTENT ENGINE"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (1280 - title_width) // 2
    draw.text((title_x, 150), title, fill=(77, 217, 232), font=title_font)

    # Add subtitle
    subtitle = "Module 00: Set Up Your AI Content Studio"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (1280 - subtitle_width) // 2
    draw.text((subtitle_x, 320), subtitle, fill=(243, 238, 255), font=subtitle_font)

    # Add corner accent
    draw.rectangle([(0, 0), (300, 300)], outline=(77, 217, 232), width=3)
    draw.polygon([(0, 0), (100, 0), (0, 100)], fill=(77, 217, 232))

    img.save("thumbnail.jpg", quality=95)
    print("✓ YouTube Thumbnail created: thumbnail.jpg (1280×720)")

    return img

def create_social_thumbnails():
    """Create thumbnails for different social platforms."""
    base_img = Image.new('RGB', (1080, 1080), color=(14, 11, 31))
    draw = ImageDraw.Draw(base_img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Background gradient
    for i in range(1080):
        ratio = i / 1080
        r = int(14 * (1 - ratio * 0.3))
        g = int(11 * (1 - ratio * 0.2))
        b = int(31 * (1 + ratio * 0.4))
        draw.rectangle([(0, i), (1080, i+1)], fill=(r, g, b))

    # Top bar
    draw.rectangle([(0, 0), (1080, 80)], fill=(77, 217, 232))
    draw.text((40, 25), "AI CONTENT ENGINE", fill=(14, 11, 31), font=subtitle_font)

    # Main title
    title = "SET UP YOUR\nAI CONTENT STUDIO"
    title_lines = title.split('\n')
    y_pos = 250
    for line in title_lines:
        title_bbox = draw.textbbox((0, 0), line, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((1080 - title_width) // 2, y_pos), line, fill=(243, 238, 255), font=title_font)
        y_pos += 120

    # Module info
    info_font = subtitle_font
    info_bbox = draw.textbbox((0, 0), "Module 00", font=info_font)
    info_width = info_bbox[2] - info_bbox[0]
    draw.text(((1080 - info_width) // 2, 700), "Module 00", fill=(77, 217, 232), font=info_font)

    base_img.save("thumbnail_square.jpg", quality=95)
    print("✓ Square Thumbnail created: thumbnail_square.jpg (1080×1080)")

    return base_img

def main():
    output_dir = Path(".")
    print("🎨 Creating professional thumbnails...\n")

    create_youtube_thumbnail()
    create_social_thumbnails()

    print("\n✅ All thumbnails created successfully!")
    print("\nFile sizes:")
    for f in ["thumbnail.jpg", "thumbnail_square.jpg"]:
        if Path(f).exists():
            size = Path(f).stat().st_size / 1024
            print(f"  {f}: {size:.1f} KB")

if __name__ == "__main__":
    main()

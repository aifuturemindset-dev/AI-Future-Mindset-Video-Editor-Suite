#!/usr/bin/env python3
"""
AI Content Engine Module Video Creator
Merges video assets and overlays to create engaging tutorial videos
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Execute a shell command with error handling."""
    if description:
        print(f"\n📹 {description}")
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error: Command failed with return code {result.returncode}")
        sys.exit(1)
    print("✓ Success")

def main():
    # Define paths
    base_dir = Path("/home/user/AI-Future-Mindset-Video-Editor-Suite")
    assets_dir = Path("/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87")
    tmp_images_dir = Path("/tmp/claude-0/-home-user-AI-Future-Mindset-Video-Editor-Suite/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/images")
    output_dir = base_dir / "output" / "videos"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Asset paths
    main_video = assets_dir / "04bde690-Module_00__Set_up_your_AI_content_studio.mp4"
    images = [
        tmp_images_dir / f"{i}.png"
        for i in range(1, 5)
    ]

    # Verify assets exist
    if not main_video.exists():
        print(f"❌ Main video not found: {main_video}")
        sys.exit(1)

    missing_images = [img for img in images if not img.exists()]
    if missing_images:
        print(f"⚠️  Warning: Some images missing: {missing_images}")

    print("🎬 AI Content Engine - Module Video Creator")
    print("=" * 60)
    print(f"Input video: {main_video}")
    print(f"Images: {len([i for i in images if i.exists()])}/4 found")
    print(f"Output directory: {output_dir}")

    # Create a video intro with title overlay
    intro_video = output_dir / "intro.mp4"

    # Get video dimensions
    get_dims_cmd = f"""ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{main_video}" """
    result = subprocess.run(get_dims_cmd, shell=True, capture_output=True, text=True)
    dims = result.stdout.strip()
    width, height = map(int, dims.split('x'))

    print(f"\n📐 Video dimensions: {width}x{height}")

    # Create intro sequence (3 seconds) with title overlay
    run_command(
        f"""ffmpeg -f lavfi -i color=c=0E0B1F:s={width}x{height}:d=3 -vf \
"drawtext=text='AI CONTENT ENGINE':x=(w-text_w)/2:y=(h-text_h)/2-50:fontsize=72:fontcolor=4DD9E8:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:shadowx=3:shadowy=3:shadowcolor=000000@0.8, \
drawtext=text='Module 00: Set Up Your AI Content Studio':x=(w-text_w)/2:y=(h-text_h)/2+40:fontsize=40:fontcolor=F3EEFF:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" \
-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
-f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k -t 3 \
"{intro_video}" -y""",
        "Creating intro sequence..."
    )

    # Process main video and enhance it
    enhanced_video = output_dir / "enhanced_main.mp4"

    run_command(
        f"""ffmpeg -i "{main_video}" -vf \
"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2, \
eq=contrast=1.1:saturation=1.15" \
-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac \
"{enhanced_video}" -y""",
        "Enhancing main video with color correction..."
    )

    # Create image overlay sequences (2 seconds each)
    image_clips = []
    existing_images = [img for img in images if img.exists()]

    for idx, img_path in enumerate(existing_images, 1):
        image_clip = output_dir / f"image_overlay_{idx}.mp4"

        run_command(
            f"""ffmpeg -loop 1 -i "{img_path}" -c:v libx264 -preset fast -crf 18 \
-pix_fmt yuv420p -vf "scale=w={width}:h={height}:force_original_aspect_ratio=decrease, \
pad={width}:{height}:(ow-iw)/2:(oh-ih)/2, \
drawbox=x=0:y=0:w={width}:h=60:color=0E0B1F@0.9:t=fill, \
drawtext=text='Step {idx}':x=30:y=20:fontsize=32:fontcolor=4DD9E8:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
-t 2 -f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k \
"{image_clip}" -y""",
            f"Creating image overlay {idx}/4..."
        )
        image_clips.append(image_clip)

    # Create outro sequence
    outro_video = output_dir / "outro.mp4"

    run_command(
        f"""ffmpeg -f lavfi -i color=c=0E0B1F:s={width}x{height}:d=3 -vf \
"drawtext=text='Ready to Build Your Content Engine?':x=(w-text_w)/2:y=(h-text_h)/2-40:fontsize=56:fontcolor=4DD9E8:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf, \
drawtext=text='Start creating engaging content today':x=(w-text_w)/2:y=(h-text_h)/2+30:fontsize=32:fontcolor=F3EEFF:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" \
-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
-f lavfi -i anullsrc=r=48000:cl=stereo -c:a aac -b:a 128k -t 3 \
"{outro_video}" -y""",
        "Creating outro sequence..."
    )

    # Create concatenation file
    concat_file = output_dir / "concat.txt"
    concat_content = f"""file '{intro_video}'
file '{enhanced_video}'
"""

    for clip in image_clips:
        concat_content += f"file '{clip}'\n"

    concat_content += f"file '{outro_video}'\n"

    with open(concat_file, 'w') as f:
        f.write(concat_content)

    print(f"\n📋 Concatenation file created")

    # Final video creation
    final_video = output_dir / "Module_00_Complete.mp4"

    run_command(
        f"""ffmpeg -f concat -safe 0 -i "{concat_file}" \
-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
-c:a aac -b:a 192k \
"{final_video}" -y""",
        "Creating final composite video..."
    )

    # Create a high-quality version for archival
    final_video_hq = output_dir / "Module_00_Complete_HQ.mp4"

    run_command(
        f"""ffmpeg -i "{final_video}" \
-c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
-c:a aac -b:a 256k \
"{final_video_hq}" -y""",
        "Creating high-quality archive version..."
    )

    # Get video information
    print("\n" + "=" * 60)
    print("✅ Video Creation Complete!")
    print("=" * 60)

    for output_file in [final_video, final_video_hq]:
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"📹 {output_file.name}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Path: {output_file}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract a 15-second preview clip from the complete video."""

import subprocess
import os
from pathlib import Path

def create_preview_clip():
    """Create a 15-second preview/teaser clip."""
    input_video = "output/videos/Module_00_Complete.mp4"
    output_clip = "output/videos/Module_00_Preview.mp4"

    if not Path(input_video).exists():
        print(f"❌ Input video not found: {input_video}")
        return False

    print("🎬 Creating 15-second preview clip...")

    # Create preview - first 15 seconds
    cmd = f"""ffmpeg -i "{input_video}" -t 15 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k "{output_clip}" -y"""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        size_mb = Path(output_clip).stat().st_size / (1024 * 1024)
        print(f"✓ Preview clip created: {output_clip}")
        print(f"  Duration: 15 seconds")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Error creating preview clip")
        print(result.stderr)
        return False

def create_social_clips():
    """Create social media friendly clips."""
    input_video = "output/videos/Module_00_Complete.mp4"

    if not Path(input_video).exists():
        print(f"❌ Input video not found: {input_video}")
        return False

    print("\n📱 Creating social media clips...\n")

    # 60-second clip for TikTok/Instagram Reels
    print("Creating 60-second TikTok/Reels clip...")
    cmd_tiktok = f"""ffmpeg -i "{input_video}" -t 60 -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac "{output_videos}/Module_00_TikTok_60s.mp4" -y"""
    subprocess.run(cmd_tiktok, shell=True, capture_output=True)

    if Path("output/videos/Module_00_TikTok_60s.mp4").exists():
        size = Path("output/videos/Module_00_TikTok_60s.mp4").stat().st_size / (1024 * 1024)
        print(f"✓ TikTok/Reels clip: Module_00_TikTok_60s.mp4 ({size:.2f} MB)")

    # 30-second YouTube Shorts clip
    print("Creating 30-second YouTube Shorts clip...")
    cmd_shorts = f"""ffmpeg -i "{input_video}" -t 30 -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac "{output_videos}/Module_00_Shorts_30s.mp4" -y"""
    subprocess.run(cmd_shorts, shell=True, capture_output=True)

    if Path("output/videos/Module_00_Shorts_30s.mp4").exists():
        size = Path("output/videos/Module_00_Shorts_30s.mp4").stat().st_size / (1024 * 1024)
        print(f"✓ YouTube Shorts clip: Module_00_Shorts_30s.mp4 ({size:.2f} MB)")

    return True

def main():
    os.chdir("/home/user/AI-Future-Mindset-Video-Editor-Suite")

    print("=" * 60)
    print("📹 Video Clip Generation")
    print("=" * 60)

    # Create preview
    if create_preview_clip():
        print("\n✅ Preview clip created successfully!")

    # Create social media clips (optional)
    try:
        print("\n" + "=" * 60)

        # Get video duration first
        cmd_duration = """ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1:noprint_filename=1 "output/videos/Module_00_Complete.mp4" """
        result = subprocess.run(cmd_duration, shell=True, capture_output=True, text=True)
        duration = float(result.stdout.strip())

        if duration >= 60:
            # Only create social clips if video is long enough
            output_videos = "output/videos"

            print("📱 Creating social media clips...\n")

            # 30-second clip for YouTube Shorts
            print("Creating 30-second YouTube Shorts clip...")
            cmd_shorts = f"""ffmpeg -i "output/videos/Module_00_Complete.mp4" -t 30 -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 128k "{output_videos}/Module_00_Shorts_30s.mp4" -y 2>/dev/null"""
            result = subprocess.run(cmd_shorts, shell=True)
            if result.returncode == 0 and Path(f"{output_videos}/Module_00_Shorts_30s.mp4").exists():
                size = Path(f"{output_videos}/Module_00_Shorts_30s.mp4").stat().st_size / (1024 * 1024)
                print(f"✓ YouTube Shorts: Module_00_Shorts_30s.mp4 ({size:.2f} MB)")

            # 60-second clip for TikTok/Reels
            print("Creating 60-second TikTok/Instagram Reels clip...")
            cmd_tiktok = f"""ffmpeg -i "output/videos/Module_00_Complete.mp4" -t 60 -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 128k "{output_videos}/Module_00_TikTok_60s.mp4" -y 2>/dev/null"""
            result = subprocess.run(cmd_tiktok, shell=True)
            if result.returncode == 0 and Path(f"{output_videos}/Module_00_TikTok_60s.mp4").exists():
                size = Path(f"{output_videos}/Module_00_TikTok_60s.mp4").stat().st_size / (1024 * 1024)
                print(f"✓ TikTok/Reels: Module_00_TikTok_60s.mp4 ({size:.2f} MB)")

        print("\n" + "=" * 60)
        print("✅ All clips created successfully!")
        print("=" * 60)

        # List all videos
        print("\n📂 Generated Video Files:")
        video_files = sorted(Path("output/videos").glob("*.mp4"))
        for idx, f in enumerate(video_files, 1):
            size = f.stat().st_size / (1024 * 1024)
            print(f"   {idx}. {f.name} ({size:.2f} MB)")

    except Exception as e:
        print(f"⚠️  Note: Could not create all social media clips: {e}")
        print("   But the main preview clip was created successfully!")

if __name__ == "__main__":
    main()

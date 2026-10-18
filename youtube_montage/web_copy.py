"""Delivery copy of a master, sized to the 30 MiB send limit: two-pass x264 at the bitrate that lands the file at TARGET MiB
(ffmpeg skill, "target file size"), instead of a fixed CRF that leaves half the budget unused. This file is what gets
uploaded to YouTube, which re-compresses it, so every spare bit is headroom.
Usage: python3 web_copy.py out/compound_16x9.mp4 web/compound_interest.mp4 [target_mib]"""
import os
import subprocess
import sys

src, dst = sys.argv[1], sys.argv[2]
TARGET = float(sys.argv[3]) if len(sys.argv) > 3 else 27.0
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                           capture_output=True, text=True, check=True).stdout)
# the master's AAC is copied as it is: a second AAC encode overshoots the true peak (+1 dBFS seen) and loses quality
AUDIO_K = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=bit_rate", "-of", "csv=p=0", src],
                             capture_output=True, text=True, check=True).stdout.strip() or 192000) // 1000
vk = int(min(3000, TARGET * 8 * 1048.576 / dur - AUDIO_K) * 0.97)      # 3 % margin for the container
log = os.path.join(os.path.dirname(os.path.abspath(dst)), f".{os.path.basename(dst)}.2pass")
common = ["-vf", "hqdn3d=2:1.5:4:3", "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-b:v", f"{vk}k",
          "-maxrate", f"{int(vk * 1.6)}k", "-bufsize", f"{vk * 2}k", "-pix_fmt", "yuv420p", "-passlogfile", log]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, *common, "-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, *common, "-pass", "2", "-c:a", "copy",
                "-movflags", "+faststart", dst], check=True)
for f in os.listdir(os.path.dirname(os.path.abspath(dst))):
    if f.startswith(os.path.basename(log)):
        os.remove(os.path.join(os.path.dirname(os.path.abspath(dst)), f))
print(f"{dst}: {os.path.getsize(dst) / 1048576:.1f} MiB, video {vk} kb/s, {dur:.1f} s")

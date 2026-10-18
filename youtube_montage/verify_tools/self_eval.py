"""video-use self-eval for the doodle videos: loudness + true peak, RMS per section (voice / music-only / end card),
timeline_view (filmstrip + waveform) at every scene cut, first/last 2 s and mid-points, tiled into sheets."""
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

FIN = os.environ.get("FIN", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))          # the folder with the build_*.py
TV = os.environ.get("TIMELINE_VIEW", os.path.join(FIN, "..", ".claude", "skills", "video-use", "helpers", "timeline_view.py"))
sys.path.insert(0, FIN)
os.chdir(FIN)
slug, module = sys.argv[1], sys.argv[2]
V = __import__(module).V
V.prepare()
video = os.path.join(FIN, "out", f"{slug}_16x9.mp4")
VER = os.path.join(FIN, "out", "edit", "verify", slug)
os.makedirs(VER, exist_ok=True)
rep = {"slug": slug}
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video], capture_output=True, text=True).stdout)
rep["duration"] = float(probe["format"]["duration"])
rep["expected"] = round(V.TOTAL, 3)
r = subprocess.run(["ffmpeg", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summ = r[r.rfind("Summary:"):]
rep["integrated_lufs"] = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
rep["true_peak_dbtp"] = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
rep["lra"] = float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1))
# decode the final mix once, measure RMS per section
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
a = np.frombuffer(pcm, np.float32)
sr = 16000
db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))
speech = np.concatenate([a[int(s * sr):int(e * sr)] for s, e in V.line_times])
gaps = np.concatenate([a[int((V.line_times[i][1] + 0.15) * sr):int((V.line_times[i + 1][0] - 0.05) * sr)]
                       for i in range(len(V.line_times) - 1) if V.line_times[i + 1][0] - V.line_times[i][1] > 0.5])
last = V.line_times[-1]
rep["rms_speech_db"] = round(db(speech), 1)
rep["rms_gaps_music_only_db"] = round(db(gaps), 1)
rep["rms_end_line_db"] = round(db(a[int(last[0] * sr):int(last[1] * sr)]), 1)
rep["rms_tail_after_voice_db"] = round(db(a[int((last[1] + 0.2) * sr):]), 1)
# cut boundaries: every scene change
cuts = [round(t, 2) for t in V.GSTART[1:]]
rep["n_cuts"] = len(cuts)
# boundary audio check: biggest sample jump within ±40 ms of each cut vs the local median (pop detector)
pops = []
for c in cuts:
    w = a[int((c - 0.04) * sr):int((c + 0.04) * sr)]
    if len(w) > 2:
        jump = float(np.max(np.abs(np.diff(w))))
        ctx = a[int((c - 1) * sr):int((c + 1) * sr)]
        typ = float(np.percentile(np.abs(np.diff(ctx)), 99.5)) + 1e-6
        if jump > 3 * typ and jump > 0.05:
            pops.append((c, round(jump, 3), round(typ, 3)))
rep["possible_pops"] = pops
if os.environ.get("AUDIO_ONLY"):
    print(json.dumps(rep, indent=1)); sys.exit(0)
pngs = []
spots = [("start", 0.0, 2.0), ("end", rep["duration"] - 2.2, rep["duration"] - 0.2)]
spots += [(f"mid{k}", rep["duration"] * f, rep["duration"] * f + 3) for k, f in enumerate((0.33, 0.5, 0.75))]
spots += [(f"cut{k:02d}", max(0, c - 1.5), min(rep["duration"] - 0.2, c + 1.5)) for k, c in enumerate(cuts)]
for name, s, e in spots:
    out = os.path.join(VER, f"{name}.png")
    subprocess.run(["python3", TV, video, f"{s:.2f}", f"{e:.2f}", "-o", out, "--n-frames", "6"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pngs.append(out)
ims = [Image.open(p).convert("RGB") for p in pngs]
w = 1200
ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
h = max(im.height for im in ims)
per = 6
for k in range(0, len(ims), per):
    group = ims[k:k + per]
    sheet = Image.new("RGB", (w * 2, h * ((len(group) + 1) // 2)), (40, 40, 40))
    for j, im in enumerate(group):
        sheet.paste(im, ((j % 2) * w, (j // 2) * h))
    sheet.save(os.path.join(VER, f"sheet_{k // per:02d}.jpg"), quality=80)
json.dump(rep, open(os.path.join(VER, "report.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))

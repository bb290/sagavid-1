#!/usr/bin/env python3
"""Music for a listing video: copy an approved track from the library, find its beat, cut to length.

Usage: python3 music.py <listing folder> <total beats> [--track house|acoustic]

- Library (assets/music/ in this skill), both approved by Brittany 2026-10-26:
    house.mp3     upbeat house, 120 BPM, for listing1 (Fast tour) and listing2 (Auto-slide)
    acoustic.mp3  calm acoustic, for listing3 (Editorial)
  Default: acoustic when shots.json says listing3, house otherwise.
- The track is copied to <folder>/assets/music/bed-v1.mp3 (kept if already there).
- Finds the beat period and phase from the kick drum (low-passed onset envelope; plain Python, no numpy)
  and where the music really ends, then starts on a beat so the last frame lands just after the final hit.
- assets/music/bed.wav: <total beats> x period long, starting on a beat, 0.4 s fade out.
- assets/music/beat.json: {"period": s, "offset": s, "bpm": n}. The build scripts time every cut on this grid.
"""
import array, json, shutil, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
proj, total_beats = Path(args[0]), int(args[1])
lib = Path(__file__).resolve().parents[1] / "assets/music"
if "--track" in args:
    track = args[args.index("--track") + 1]
else:
    spec = proj / "shots.json"
    style = json.loads(spec.read_text()).get("style") if spec.exists() else None
    track = "acoustic" if style == "listing3" else "house"
mdir = proj / "assets/music"
mdir.mkdir(parents=True, exist_ok=True)
bed = mdir / "bed-v1.mp3"
if not bed.exists():
    shutil.copy(lib / f"{track}.mp3", bed)
    print(f"music: {track}.mp3")

# Kick envelope: low-pass, 1 kHz mono, 10 ms frames, positive energy change.
SR, HOP = 1000, 10
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(bed), "-af", "lowpass=f=150,lowpass=f=150", "-ac", "1",
                      "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = array.array("h", pcm)
env = [sum(abs(v) for v in x[i:i + HOP]) for i in range(0, len(x) - HOP, HOP)]
onset = [max(0, env[i] - env[i - 1]) for i in range(1, len(env))]
fps = SR / HOP
bed_len = len(x) / SR


def score(period, phase):
    s, t = 0.0, phase
    while t * fps < len(onset) - 1:
        k = int(round(t * fps))
        s += max(onset[max(0, k - 1):k + 2])
        t += period
    return s


best = max(((score(p / 1000, ph / 100), p / 1000, ph / 100)
            for p in range(460, 541, 2) for ph in range(0, int(p / 10))), key=lambda r: r[0])
_, period, phase = best
# Refine the period to 1 ms around the coarse pick.
_, period, phase = max(((score(p / 1000, ph / 200), p / 1000, ph / 200)
                        for p in range(int(period * 1000) - 3, int(period * 1000) + 4)
                        for ph in range(0, int(p / 5))), key=lambda r: r[0])

# Generated tracks often stop early and pad with silence: find where the music really ends.
full = array.array("h", subprocess.run(["ffmpeg", "-v", "error", "-i", str(bed), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                                       capture_output=True, check=True).stdout)
rms = [(sum(v * v for v in full[i:i + 250]) / 250) ** .5 for i in range(0, len(full) - 250, 250)]
music_end = (max(k for k, r in enumerate(rms) if r > 0.1 * max(rms)) + 1) * 0.25

dur = total_beats * period
if dur > music_end:
    sys.exit(f"{total_beats} beats at {period:.3f}s = {dur:.2f}s, longer than the music ({music_end:.2f}s)")
# Start on the beat that puts the video's last frame just after the music's last hit.
n = int((music_end + 0.25 - dur - phase) // period)
offset = phase + n * period
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{offset:.3f}", "-t", f"{dur:.3f}", "-i", str(bed), "-af",
                f"afade=t=out:st={dur - 0.4:.3f}:d=0.4,aresample=48000,volume=0.85", "-ar", "48000",
                str(mdir / "bed.wav")], check=True)
(mdir / "beat.json").write_text(json.dumps({"period": round(period, 4), "offset": round(offset, 3),
                                           "bpm": round(60 / period, 1), "bed": bed.name}, indent=1))
print(f"{bed.name}: {bed_len:.2f}s, beat {period:.3f}s ({60 / period:.1f} BPM), phase {phase:.3f}s; "
      f"music ends {music_end:.2f}s; start {offset:.2f}s, {total_beats} beats = {dur:.2f}s, video ends {offset + dur:.2f}s")

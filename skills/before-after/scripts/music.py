#!/usr/bin/env python3
"""Music bed for a Property Management IRL episode: the style's own track (or a generated one), trimmed, ducked under the voice.

Usage: python3 music.py <episode_dir> <video_seconds> --style <style>      (the style's approved track, no key needed)
       python3 music.py <episode_dir> <video_seconds> [--prompt "..."] [--new]   (generate with ElevenLabs instead)

- --style before-after | standard | spot-it | photo-flip: assets/music/<style>.mp3 from this skill. Every style has its own track.

- assets/music/bed-v1.mp3: a 30 s instrumental from ElevenLabs music. Reused if present; --new makes bed-v2, v3, ... and uses the newest.
- assets/music/bed-ducked.wav: the bed trimmed from the front so its final chord lands on the last
  frame, then sidechain-ducked about 15 dB under assets/voice.wav. Play it at data-volume="1".
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import sagavid

DEFAULT_PROMPT = ("Warm, light, optimistic instrumental bed for a short real-estate social video. Soft muted electric "
                  "guitar plucks, gentle piano, light brushed percussion and a subtle low bass, 100 BPM, major key, clean "
                  "and modern, not cheesy, no vocals. Steady and understated so a spoken voice sits on top. Builds slightly "
                  "in the last 8 seconds and resolves on a clean final chord with a short natural tail.")
args = sys.argv[1:]
ep, dur = Path(args[0]), float(args[1])
prompt = args[args.index("--prompt") + 1] if "--prompt" in args else DEFAULT_PROMPT
mdir = ep / "assets/music"
mdir.mkdir(parents=True, exist_ok=True)
beds = sorted(mdir.glob("bed-v*.mp3"), key=lambda p: int(p.stem.split("v")[-1]))

style = args[args.index("--style") + 1] if "--style" in args else None
if style:
    bed = Path(__file__).resolve().parents[1] / "assets/music" / f"{style}.mp3"
    if not bed.exists():
        sys.exit(f"no track for style {style!r} in {bed.parent}")
elif not beds or "--new" in args:
    bed = mdir / f"bed-v{len(beds) + 1}.mp3"
    sagavid.music(prompt, bed)
    print(f"generated {bed.name}")
else:
    bed = beds[-1]

bed_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(bed)],
                               capture_output=True, text=True, check=True).stdout)
# ElevenLabs pads the end with silence: measure where the music really stops, so the last chord lands on the last frame.
sil = subprocess.run(["ffmpeg", "-i", str(bed), "-af", "silencedetect=n=-45dB:d=0.4", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(l.split("silence_start:")[1]) for l in sil.splitlines() if "silence_start:" in l]
music_end = starts[-1] + 0.25 if starts and starts[-1] > bed_len - 3 else bed_len
offset = max(0.0, music_end - dur)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bed), "-i", str(ep / "assets/voice.wav"), "-filter_complex",
                f"[0]atrim=start={offset:.2f},asetpts=PTS-STARTPTS,aresample=48000,volume=0.40[m];"
                "[1]aresample=48000,apad[sc];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=25:release=350[md]",
                "-map", "[md]", "-t", f"{dur}", "-ar", "48000", str(mdir / "bed-ducked.wav")], check=True)
print(f"{bed.name}: {bed_len:.2f}s, trimmed {offset:.2f}s from the front -> bed-ducked.wav ({dur}s)")

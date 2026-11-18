#!/usr/bin/env python3
"""Music bed for a before/after video: the style's own track, fitted to this video, ducked under the voice.

Usage: python3 music.py <project> <video_seconds> --style ba-junk | ba-trashed | ba-reno

- ba-junk: the track is trimmed from the front so its final chord lands on the last frame.
- ba-trashed, ba-reno: the track has one "drop" (where it lifts), written in assets/music/<style>.json with its tempo.
  The build script records this video's big moment in <project>/assets/music/sync.json (Trashed: the roll-up opening
  on the trash out; Reno: the first plank row). The track is rebuilt in whole bars so the drop lands exactly on that
  moment: bars before the drop are looped or trimmed to fit the run-up, bars after it are repeated or cut to fit the
  rest, and the end fades if it overruns. Run the build once first (it writes sync.json), then this, then build again.
- Writes assets/music/bed-ducked.wav: the fitted bed, sidechain-ducked about 15 dB under assets/voice.wav.
  Play it at data-volume="1". No ElevenLabs key needed.
"""
import json, math, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
ep, dur = Path(args[0]), float(args[1])
style = args[args.index("--style") + 1] if "--style" in args else sys.exit("--style is required (ba-junk, ba-trashed, ba-reno)")
lib = Path(__file__).resolve().parents[1] / "assets/music"
bed = lib / f"{style}.mp3"
if not bed.exists():
    sys.exit(f"no track for style {style!r} in {lib}")
mdir = ep / "assets/music"
mdir.mkdir(parents=True, exist_ok=True)

bed_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(bed)],
                               capture_output=True, text=True, check=True).stdout)
# ElevenLabs pads the end with silence: find where the music really stops.
sil = subprocess.run(["ffmpeg", "-i", str(bed), "-af", "silencedetect=n=-45dB:d=0.4", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(l.split("silence_start:")[1]) for l in sil.splitlines() if "silence_start:" in l]
music_end = starts[-1] + 0.25 if starts and starts[-1] > bed_len - 3 else bed_len

meta_f, sync_f = lib / f"{style}.json", mdir / "sync.json"
segs = None
if meta_f.exists():
    meta = json.loads(meta_f.read_text())
    if not sync_f.exists():
        sys.exit(f"{style} lines its drop up with the video: run the build script first (it writes {sync_f}).")
    K = float(json.loads(sync_f.read_text())["key"])
    D, b = float(meta["drop"]), 240.0 / float(meta["bpm"])   # drop time, one 4-beat bar in seconds
    if K <= D:                       # run-up shorter than the track's: start part-way in
        pre = [(D - K, D)]
    else:                            # run-up longer: loop whole bars from the start of the groove
        n = math.ceil((K - D) / b)
        pre = [(n * b - (K - D), b + n * b), (b, D)]
    P, Q = dur - K, music_end - D    # what the video needs after the drop, what the track has
    if P <= Q:                       # cut whole bars out of the middle of the lift
        c = math.floor((Q - P) / b) * b
        a = max(b, math.floor((P / 2) / b) * b)
        post = [(D, D + a), (D + a + c, music_end)] if c > 0 else [(D, music_end)]
    else:                            # repeat whole bars of the lift
        n = math.ceil((P - Q) / b)
        post = [(D, D + b + n * b), (D + b, music_end)]
    segs = [(s, e) for s, e in pre + post if e - s > 0.01]
    print(f"{style}: drop {D:.2f}s in the track -> {K:.2f}s in the video; {len(segs)} pieces, bar {b:.3f}s")

if segs:
    parts = "".join(f"[0]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (s, e) in enumerate(segs))
    joined = "".join(f"[p{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[cat];"
    head = parts + joined + f"[cat]atrim=end={dur:.3f},afade=t=out:st={max(0, dur - 0.6):.3f}:d=0.6,"
else:
    offset = max(0.0, music_end - dur)
    head = f"[0]atrim=start={offset:.2f},asetpts=PTS-STARTPTS,"
    print(f"{style}: {bed_len:.2f}s, trimmed {offset:.2f}s from the front")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bed), "-i", str(ep / "assets/voice.wav"), "-filter_complex",
                head + "aresample=48000,volume=0.40[m];"
                "[1]aresample=48000,apad[sc];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=25:release=350[md]",
                "-map", "[md]", "-t", f"{dur}", "-ar", "48000", str(mdir / "bed-ducked.wav")], check=True)
print(f"-> {mdir / 'bed-ducked.wav'} ({dur}s)")

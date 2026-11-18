#!/usr/bin/env python3
"""The voiceover for a before/after video: clean, transcribe, tighten.

Usage:
  python3 voice.py <episode_dir> <raw_audio> [--cut START-END ...] [--max-sent 0.42] [--max-gap 0.30]

Steps (each one is skipped when its output already exists, so a rerun spends no credits):
  1. assets/vo/raw.wav          the recording as mono WAV
  2. assets/vo/isolated.mp3     ElevenLabs voice isolation (shared key, see lib/sagavid.py)
  3. assets/vo/transcript.json  ElevenLabs Scribe word timings of the raw recording
  4. assets/vo/tight.wav/.json  pauses capped, --cut ranges removed (raw-recording seconds), words remapped
     assets/voice.wav           the copy the composition plays

Pauses are capped, never the speech: no speed change. Read the printed words and the
"possible stumbles" list, then rerun with --cut for each stumble you confirm on the waveform.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import sagavid

args = sys.argv[1:]
ep, raw_in = Path(args[0]), Path(args[1])
cuts = [tuple(map(float, args[i + 1].split("-"))) for i, a in enumerate(args) if a == "--cut"]
max_sent = float(args[args.index("--max-sent") + 1]) if "--max-sent" in args else 0.42
max_gap = float(args[args.index("--max-gap") + 1]) if "--max-gap" in args else 0.30
vo = ep / "assets/vo"
vo.mkdir(parents=True, exist_ok=True)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


# 1. Raw recording
raw_copy = vo / ("raw" + raw_in.suffix.lower())
if raw_in.resolve() != raw_copy.resolve():
    shutil.copy(raw_in, raw_copy)
if not (vo / "raw.wav").exists():
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_copy), "-ac", "1", "-ar", "44100", str(vo / "raw.wav")])

# 2. Voice isolation
if not (vo / "isolated.mp3").exists():
    sagavid.isolate(vo / "raw.wav", vo / "isolated.mp3")

# 3. Word timings
if not (vo / "transcript.json").exists():
    run(["ffmpeg", "-v", "error", "-y", "-i", str(vo / "raw.wav"), "-ac", "1", "-b:a", "128k", str(vo / "raw.mp3")])
    d = sagavid.transcribe(vo / "raw.mp3")
    (vo / "transcript.json").write_text(json.dumps(d, indent=1))

w = [x for x in json.loads((vo / "transcript.json").read_text())["words"] if x.get("type") == "word"]

# 4. Keep-segments: speech with long pauses capped, then the --cut ranges subtracted.
keep, start = [], w[0]["start"] - 0.25
for a, b in zip(w, w[1:]):
    lim = max_sent if a["text"][-1] in ".?!," else max_gap
    if b["start"] - a["end"] > lim:
        keep.append((start, a["end"] + lim / 2))
        start = b["start"] - lim / 2
keep.append((start, w[-1]["end"] + 0.45))
for cs, ce in cuts:
    nk = []
    for s, e in keep:
        if e <= cs or s >= ce:
            nk.append((s, e))
            continue
        if s < cs:
            nk.append((s, cs))
        if e > ce:
            nk.append((ce, e))
    keep = nk
keep = [(s, e) for s, e in keep if e - s > 0.05]


def remap(t):
    acc = 0.0
    for s, e in keep:
        if t < s:
            return acc
        if t <= e:
            return acc + (t - s)
        acc += e - s
    return acc


parts, labels = [], []
for i, (s, e) in enumerate(keep):
    parts.append(f"[0]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={e - s - 0.008:.3f}:d=0.008[s{i}]")
    labels.append(f"[s{i}]")
graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=0:a=1[o]"
run(["ffmpeg", "-v", "error", "-y", "-i", str(vo / "isolated.mp3"), "-filter_complex", graph, "-map", "[o]",
     "-ar", "48000", "-c:a", "pcm_s16le", str(vo / "tight.wav")])
shutil.copy(vo / "tight.wav", ep / "assets/voice.wav")

words = []
for x in w:
    s, text = x["start"], x["text"]
    for cs, ce in cuts:
        # A word inside a cut, straddling it, or starting right after it (Scribe often times the
        # stumbled word from its clean restart, just past the fragment you cut).
        if cs <= s < ce or (s < cs < x["end"]) or 0 <= s - ce <= 0.15:
            s = max(s, ce)
            # "re-refreshed" with the "re-" cut out reads "refreshed"
            head, _, tail = text.partition("-")
            if tail and tail.lower().startswith(head.lower()):
                text = tail
    words.append({"text": text, "start": round(remap(s), 3), "end": round(remap(x["end"]), 3)})
words = [x for x in words if x["end"] - x["start"] >= 0.03]   # words inside a cut collapse to zero length: drop them
(vo / "tight.json").write_text(json.dumps({"segments": keep, "cuts": cuts, "words": words}, indent=1))

total = sum(e - s for s, e in keep)
print(f"voice {total:.2f}s (speech was {w[-1]['end'] - w[0]['start']:.2f}s), {len(keep)} segments, cuts {cuts}")
print(" ".join(f"{x['text']}@{x['start']:.2f}" for x in words))
stumbles = [f"{x['text']}@{x['start']:.2f}-{x['end']:.2f}" for x in w
            if re.match(r"^(\w+)-\1", x["text"], re.I) or "--" in x["text"]]
stumbles += [f"{a['text']} {b['text']}@{a['start']:.2f}" for a, b in zip(w, w[1:])
             if a["text"].lower().strip(".,?!") == b["text"].lower().strip(".,?!")]
if stumbles:
    print("possible stumbles (raw seconds; confirm on the waveform before cutting):", "; ".join(stumbles))
if total > 27.0:
    print(f"WARNING: {total:.1f}s of voice leaves no room for the 3 s end card under 30 s. Cut words, never speed.")

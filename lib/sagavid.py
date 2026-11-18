"""Shared helpers for the sagavid scripts: where things live on a staff computer, and ElevenLabs calls.

Videos:   ~/Documents/Sagareus Videos/ (override with SAGAVID_HOME)
Drive:    the "Video Content" shared drive through Google Drive for desktop (override with SAGAVID_DRIVE)
Key:      ELEVENLABS_API_KEY from the environment, else ~/.sagavid/.env. Never printed, never on a command line.
"""
import glob, json, os, subprocess, sys
from pathlib import Path

API = "https://api.elevenlabs.io/v1"


def videos_home():
    return Path(os.environ.get("SAGAVID_HOME", Path.home() / "Documents/Sagareus Videos"))


def drive():
    """The Video Content shared drive folder (holds B-Roll/ and Finals/)."""
    if os.environ.get("SAGAVID_DRIVE"):
        return Path(os.environ["SAGAVID_DRIVE"])
    hits = glob.glob(str(Path.home() / "Library/CloudStorage/GoogleDrive-*/Shared drives/Video Content"))
    hits += [p for p in ("G:/Shared drives/Video Content", "G:/My Drive/../Shared drives/Video Content") if Path(p).exists()]
    if not hits:
        sys.exit("Can't find the Video Content shared drive. Open Google Drive for desktop and check it is signed in "
                 "with your Sagareus account, or set SAGAVID_DRIVE to the folder.")
    return Path(hits[0])


def broll():
    return drive() / "B-Roll"


def _key():
    k = os.environ.get("ELEVENLABS_API_KEY", "")
    env = Path.home() / ".sagavid/.env"
    if not k and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("ELEVENLABS_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("No ElevenLabs key. Put ELEVENLABS_API_KEY=... in ~/.sagavid/.env (ask Brittany for the key).")
    return k


def _post(path, args, out=None):
    """POST to ElevenLabs with curl. The key goes in on stdin as a header file, so it never shows in `ps`."""
    cmd = ["curl", "-sS", "--fail-with-body", "-X", "POST", "-H", "@-", *args, f"{API}{path}"]
    if out:
        cmd += ["-o", str(out)]
    r = subprocess.run(cmd, input=f"xi-api-key: {_key()}\n".encode(), capture_output=True)
    if r.returncode:
        body = Path(out).read_bytes()[:400] if out and Path(out).exists() else r.stdout[:400]
        if out and Path(out).exists():
            Path(out).unlink()
        sys.exit(f"ElevenLabs {path} failed: {body.decode(errors='replace')} {r.stderr.decode()[:300]}")
    return r.stdout


def isolate(src, dst):
    """Voice isolation: room noise and echo out. Writes an MP3 to dst."""
    _post("/audio-isolation", ["-F", f"audio=@{src}"], out=dst)


def transcribe(src):
    """Scribe word timings: {"words": [{"text", "start", "end", "type"}, ...], ...}."""
    return json.loads(_post("/speech-to-text", ["-F", "model_id=scribe_v2", "-F", f"file=@{src}",
                                                "-F", "timestamps_granularity=word", "-F", "tag_audio_events=false"]))


def music(prompt, dst, ms=30000):
    """A generated instrumental, MP3 to dst."""
    _post("/music?output_format=mp3_44100_192", ["-H", "content-type: application/json", "-d",
                                                 json.dumps({"prompt": prompt, "music_length_ms": ms,
                                                             "force_instrumental": True})], out=dst)

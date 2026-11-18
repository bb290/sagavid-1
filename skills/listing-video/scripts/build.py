#!/usr/bin/env python3
"""Build a listing video's HyperFrames project from shots.json, cut on the music's beat.

Styles (shots.json "style"): listing1 is the Fast tour (6 to 8 photos, rotating label entrances, no
facts strip). Other styles get their own build script when they exist (listing2, listing3, ...).

Usage: python3 build.py <listing folder>      (run music.py first: it writes assets/music/beat.json)

Reads <folder>/shots.json:
  {
    "style": "listing1",
    "strip": "",                                  # optional facts pill over the tour; listing1 leaves it out
    "title": {"photo": "p17.jpg", "x0": 0.45, "x1": 0.55, "beats": 4, "lines": ["FOR", "RENT"],
              "place": "NORTON GRAND · EVERETT", "facts": "2 BED · 1 BATH · 808 SQ FT"},
    "shots": [
      {"id": "walkin", "clip": "walkthrough.mov", "start": 3.0, "beats": 3, "lines": ["NEW", "FLOORS"]},
      {"id": "kitchen", "photo": "p01.jpg", "x0": 0.05, "x1": 0.35, "beats": 3, "lines": ["NEW", "DISHWASHER"]}
    ],
    "end": {"beats": 7, "lines": ["SCHEDULE", "YOUR TOUR", "TODAY."], "small": ["Managed by Sagareus Property Management."]}
  }
  photo: a file in source/photos/, full screen at 1.15x cover size, panning from x0 to x1 (0 = left edge,
         1 = right edge); optional "y" (0 to 1, default 0.5).
  clip:  a file in source/clips/, cut from start to assets/clips/<id>.mp4 (no audio).
  lines: the big stacked label, 1 to 3 short lines, uppercase. Font size shrinks to fit the longest line.
  anim:  optional label entrance: rise, wipe, slam, track, drop, slide, pop, or hold (no entrance: repeat the previous shot's lines to carry one label across several shots). Default rotates through ANIMS
         by shot order, so each slide's text moves differently.
Every scene length is beats x the beat period in assets/music/beat.json, so every cut lands on a beat.
No sound effects: the music carries it.
"""
import html, json, shutil, subprocess, sys
from pathlib import Path

proj = Path(sys.argv[1]).resolve()
skill = Path(__file__).resolve().parents[1]
spec = json.loads((proj / "shots.json").read_text())
if spec.get("style", "listing1") != "listing1":
    sys.exit(f"build.py makes listing1; style {spec['style']!r} needs its own build script")
beat_file = proj / "assets/music/beat.json"
period = json.loads(beat_file.read_text())["period"] if beat_file.exists() else 0.5
(proj / "compositions").mkdir(exist_ok=True)
for d in ("photos", "clips", "music"):
    (proj / "assets" / d).mkdir(parents=True, exist_ok=True)
for f in ("package.json", "hyperframes.json", "meta.json"):  # project scaffold, named after the folder
    if not (proj / f).exists():
        (proj / f).write_text((skill / "template" / f).read_text().replace("sagavid-project", f"listing-{proj.name}"))
for old in (proj / "compositions").glob("*.html"):
    old.unlink()
esc = html.escape


def size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
    return tuple(int(v) for v in out.split(","))


def media(pid, shot, dur):
    """Full-screen photo or clip in a wrapper that punches in on the cut (1.14 to 1.0)."""
    if "photo" in shot:
        src = proj / "source/photos" / shot["photo"]
        w, h = size(src)
        if min(w, h) < 1200:
            sys.exit(f"{shot['photo']} is {w}x{h}: too small for full screen. Pick another photo.")
        shutil.copy(src, proj / "assets/photos" / shot["photo"])
        s = max(1080 / w, 1920 / h) * 1.15
        W, H = round(w * s), round(h * s)
        y = -round((H - 1920) * shot.get("y", 0.5))
        x0, x1 = (-round((W - 1080) * shot.get(k, 0.5)) for k in ("x0", "x1"))
        inner = (f'<img id="{pid}-img" class="photo" src="assets/photos/{shot["photo"]}" alt="" '
                 f'style="width:{W}px;height:{H}px;top:{y}px" />')
        pan = f'tl.fromTo("#{pid}-img", {{ x: {x0} }}, {{ x: {x1}, duration: {dur:.3f}, ease: "none" }}, 0);'
    else:
        out = proj / "assets/clips" / f"{pid}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(shot["start"]), "-t", f"{dur + 0.2:.2f}",
                        "-i", str(proj / "source/clips" / shot["clip"]), "-an", "-vf",
                        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-movflags", "+faststart", str(out)], check=True)
        inner = (f'<video id="{pid}-vid" class="clip footage" src="assets/clips/{pid}.mp4" data-start="0" '
                 f'data-duration="{dur:.3f}" data-track-index="0" muted playsinline></video>')
        pan = ""
    layer = f'<div id="{pid}-media" class="media">{inner}</div>'
    tweens = (f'tl.fromTo("#{pid}-media", {{ scale: 1.14 }}, {{ scale: 1.04, duration: 0.32, ease: "expo.out" }}, 0);\n'
              f'    tl.to("#{pid}-media", {{ scale: 1.0, duration: {max(0.1, dur - 0.32):.3f}, ease: "none" }}, 0.32);')
    return layer, (pan + "\n    " if pan else "") + tweens


from labels import ANIMS, stack as _stack  # shared with the other listing styles


def stack(pid, lines, top, anim="pop", max_px=170):
    return _stack(pid, lines, top, anim, period, 0.0, max_px)


def scene(cid, body, tweens, style=""):
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
{style}  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {tweens}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


hosts, t = [], 0.0

# Title: on screen from frame 0 (the cover frame), settling in rather than entering.
ti = spec["title"]
dur = ti["beats"] * period
layer, mt = media("ti", ti, dur)
px = min(190, int(940 / (0.70 * max(len(l) for l in ti["lines"]))))
lines = "".join(f'<span class="ln">{esc(l)}</span>' for l in ti["lines"])
body = f"""    {layer}
    <div class="shade"></div>
    <div id="ti-stack" class="stack" style="top:300px;font-size:{px}px">{lines}<span id="ti-bar" class="bar"></span></div>
    <div id="ti-place" class="place">{esc(ti["place"])}</div>
    <div id="ti-facts" class="facts">{esc(ti["facts"])}</div>"""
tweens = f"""{mt}
    tl.fromTo("#ti-stack", {{ scale: 1.04 }}, {{ scale: 1, duration: 0.5, ease: "expo.out" }}, 0);
    tl.fromTo("#ti-bar", {{ scaleX: 0.4 }}, {{ scaleX: 1, duration: 0.4, ease: "expo.out" }}, 0.1);
    tl.fromTo("#ti-facts", {{ y: 18, opacity: 0.6 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }}, {period:.3f});"""
top = 300 + int(px * 0.92 * len(ti["lines"])) + 70
style = f"""    #ti-place {{ position: absolute; left: 64px; right: 140px; top: {top}px; }}
    #ti-facts {{ position: absolute; left: 64px; top: {top + 76}px; }}
"""
(proj / "compositions/title.html").write_text(scene("title", body, tweens, style))
hosts.append(("title", t, dur))
t += dur
tour_start = t

for i, shot in enumerate(spec["shots"]):
    pid, dur = shot["id"], shot["beats"] * period
    layer, mt = media(pid, shot, dur)
    sb, st = stack(pid, shot["lines"], 300, shot.get("anim", ANIMS[i % len(ANIMS)]))
    body = f"    {layer}\n    <div class=\"shade\"></div>\n    {sb}"
    (proj / "compositions" / f"{pid}.html").write_text(scene(pid, body, mt + "\n    " + st))
    hosts.append((pid, t, dur))
    t += dur
tour_end = t

# End card: Emerald, the lines land one per beat.
end = spec["end"]
dur = end["beats"] * period
px = min(150, int(940 / (0.70 * max(len(l) for l in end["lines"]))))
lines = "".join(f'<span id="ec-l{k}" class="ln">{esc(l)}</span>' for k, l in enumerate(end["lines"]))
small = "".join(f'<div class="ec-small" style="top:{1060 + 64 * k}px">{esc(s)}</div>' for k, s in enumerate(end.get("small", [])))
body = f"""    <div id="ec-panel"></div>
    <div id="ec-stack" class="stack" style="top:560px;font-size:{px}px">{lines}<span id="ec-bar" class="bar"></span></div>
    {small}"""
tweens = f"""tl.fromTo("#ec-panel", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.3, ease: "expo.out" }}, 0);
    tl.fromTo("#ec-stack .ln", {{ scale: 1.35, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.16, ease: "back.out(2.2)", stagger: {period:.3f} }}, 0.02);
    tl.fromTo("#ec-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "expo.out" }}, {period * len(end["lines"]):.3f});
    tl.fromTo(".ec-small", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, {period * (len(end["lines"]) - 0.5):.3f});"""
style = """    #ec-panel { position: absolute; inset: -60px; background: var(--emerald); }
    .ec-small { position: absolute; left: 64px; right: 64px; font-size: 40px; font-weight: 700; color: var(--cream); white-space: nowrap; }
"""
(proj / "compositions/endcard.html").write_text(scene("endcard", body, tweens, style))
hosts.append(("endcard", t, dur))
total = round(t + dur, 3)

host_tags = "\n".join(
    f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
    f'data-duration="{d:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    for cid, s, d in hosts)

# Optional facts strip over the tour. listing1 leaves it out (Brittany 2026-10-26): the title carries the facts.
if spec.get("strip"):
    strip_dur = tour_end - tour_start
    (proj / "compositions/strip.html").write_text(scene("strip", f'    <div id="sp-box">{esc(spec["strip"])}</div>',
        f'tl.fromTo("#sp-box", {{ x: -500 }}, {{ x: 0, duration: 0.3, ease: "expo.out" }}, 0);',
        """    #sp-box { position: absolute; left: 64px; top: 1220px; background: var(--emerald); color: var(--white); font-size: 40px; font-weight: 900; letter-spacing: .06em; padding: 14px 24px 16px; border-radius: 12px; }
"""))
    host_tags += (f'\n      <div id="strip" data-composition-id="strip" data-composition-src="compositions/strip.html" '
                  f'data-start="{tour_start:.3f}" data-duration="{strip_dur:.3f}" data-track-index="2" data-track-kind="graphics" '
                  f'data-width="1080" data-height="1920" style="z-index: 40"></div>')
audio = ""
if (proj / "assets/music/bed.wav").exists():
    audio = (f'      <audio id="music" class="clip" src="assets/music/bed.wav" data-start="0" data-duration="{total}" '
             f'data-track-index="3" data-volume="1"></audio>')

(proj / "index.html").write_text(f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* Sagareus external brand, listing "Fast tour" look: Emerald, warm Off-White, White, Inter. Never the internal comic style or warm gray. */
      :root {{ --emerald: #0B4F42; --cream: #F5F0E8; --white: #FFFFFF; --ink: #1a1a1a; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #111; }}
      body {{ font-family: Inter, sans-serif; color: var(--white); }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      #floor {{ position: absolute; inset: 0; background: #111; }}
      /* Shared parts the scenes use */
      .media {{ position: absolute; inset: 0; transform-origin: 50% 45%; }}
      .footage {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .photo {{ position: absolute; left: 0; max-width: none; }}
      .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,.25) 28%, rgba(0,0,0,0) 45%, rgba(0,0,0,0) 58%, rgba(0,0,0,.35) 75%, rgba(0,0,0,0) 90%); }}
      .stack {{ position: absolute; left: 64px; right: 140px; font-weight: 900; line-height: .92; letter-spacing: -.035em; text-transform: uppercase; color: var(--white); text-shadow: 0 4px 30px rgba(0,0,0,.35); }}
      .stack .ln {{ display: block; transform-origin: 0% 60%; white-space: nowrap; }}
      .stack .mk {{ display: inline-block; overflow: hidden; padding-bottom: .1em; margin-bottom: -.1em; vertical-align: top; }}
      .stack .ch {{ display: inline-block; }}
      .stack .bar {{ display: block; width: 220px; height: 18px; margin-top: 26px; background: var(--cream); border-radius: 4px; transform-origin: 0 50%; }}
      .place {{ font-size: 44px; font-weight: 800; letter-spacing: .1em; color: var(--cream); text-shadow: 0 2px 16px rgba(0,0,0,.5); }}
      .facts {{ display: inline-block; background: var(--emerald); font-size: 44px; font-weight: 900; letter-spacing: .05em; color: var(--white); padding: 14px 24px 16px; border-radius: 12px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      <div id="floor"></div>

{host_tags}

{audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
print(f"{len(hosts)} scenes, {total}s, beat {period}s")
for cid, s, d in hosts:
    print(f"  {cid:<10} {s:7.3f} -> {s + d:7.3f}")

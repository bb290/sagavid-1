#!/usr/bin/env python3
"""Build a listing2 video: the "auto-sliding carousel". One long Off-White canvas, a panel per room, photos
as framed cards that cross the panel seams, and a camera that holds on each panel and swipes to the next
on the beat. One vertical video, so every channel can post it.

Usage: python3 build_listing2.py <listing folder>      (run music.py first: it writes assets/music/beat.json)

Reads <folder>/shots.json:
  {
    "style": "listing2",
    "panels": [
      {"id": "cover", "hold": 4, "lines": ["FOR", "RENT"], "place": "NORTON GRAND · EVERETT",
       "facts": "2 BED · 1 BATH · 808 SQ FT",
       "cards": [{"photo": "p17.jpg", "x": 90, "y": 820, "w": 900, "h": 760, "rot": -1.5, "fx": 0.5}]},
      {"id": "living", "hold": 5, "lines": ["BRIGHT +", "OPEN"],
       "cards": [{"clip": "walkthrough.mov", "start": 3.0, "x": 140, "y": 700, "w": 860, "h": 484, "rot": 1.5}],
       "pills": [{"text": "NEW FLOORS", "x": 560, "y": 1150}]}
    ],
    "end": {"hold": 7, "lines": ["SCHEDULE", "YOUR TOUR", "TODAY."], "small": ["Managed by Sagareus Property Management."]}
  }
  hold:  beats the camera rests on the panel; every swipe to the next panel takes one beat.
  cards: x/y/w/h in px relative to the panel's left edge; x + w past 1080 crosses into the next panel
         (the peek). photo from source/photos (fx/fy = crop focus, 0 to 1); clip from source/clips,
         plays muted from `start` while its panel is in view, over a still of its first frame.
  pills: Emerald callouts laid over the cards.
  anim:  optional label entrance per panel; default rotates through labels.ANIMS. The cover stays still
         (it is the cover frame).
"""
import html, json, shutil, subprocess, sys
from pathlib import Path
from labels import ANIMS, stack

proj = Path(sys.argv[1]).resolve()
skill = Path(__file__).resolve().parents[1]
spec = json.loads((proj / "shots.json").read_text())
if spec.get("style") != "listing2":
    sys.exit(f"build_listing2.py makes listing2; shots.json says {spec.get('style')!r}")
period = json.loads((proj / "assets/music/beat.json").read_text())["period"]
W, H = 1080, 1920
esc = html.escape
(proj / "compositions").mkdir(exist_ok=True)
for d in ("photos", "clips", "music"):
    (proj / "assets" / d).mkdir(parents=True, exist_ok=True)
for f in ("package.json", "hyperframes.json", "meta.json"):
    if not (proj / f).exists():
        (proj / f).write_text((skill / "template" / f).read_text().replace("sagavid-project", f"listing-{proj.name}"))
for old in (proj / "compositions").glob("*.html"):
    old.unlink()

panels = spec["panels"] + [dict(spec["end"], id="end")]
# Timeline: panel i is in view from arrive[i] (camera settled) until leave[i] (swipe out starts).
arrive, leave, t = [], [], 0.0
for i, p in enumerate(panels):
    arrive.append(t)
    t += p["hold"] * period
    leave.append(t)
    if i < len(panels) - 1:
        t += period
total = round(t, 3)

markup, tweens = [], []
for i, p in enumerate(panels):
    ox = i * W
    parts = []
    if p["id"] == "end":
        parts.append('<div class="endpanel"></div>')
    for k, c in enumerate(p.get("cards", [])):
        cid = f'{p["id"]}-c{k}'
        box = f'left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px;height:{c["h"]}px;transform:rotate({c.get("rot", 0)}deg)'
        if "photo" in c:
            shutil.copy(proj / "source/photos" / c["photo"], proj / "assets/photos" / c["photo"])
            pos = f'{c.get("fx", 0.5) * 100:.0f}% {c.get("fy", 0.5) * 100:.0f}%'
            parts.append(f'<div id="{cid}" class="card" style="{box}"><img src="assets/photos/{c["photo"]}" alt="" '
                         f'style="object-position:{pos}" /></div>')
        else:
            # The clip plays while its panel is on screen: from the swipe in to the end of the swipe out.
            start = max(0.0, arrive[i] - period)
            dur = (leave[i] + period) - start
            out = proj / "assets/clips" / f"{cid}.mp4"
            poster = proj / "assets/clips" / f"{cid}.jpg"
            src = proj / "source/clips" / c["clip"]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["start"]), "-t", f"{dur + 0.2:.2f}", "-i", str(src),
                            "-an", "-vf", "scale=-2:1080,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                            "-movflags", "+faststart", str(out)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["start"]), "-i", str(src), "-frames:v", "1",
                            "-vf", "scale=-2:1080", "-q:v", "3", str(poster)], check=True)
            parts.append(f'<div id="{cid}" class="card" style="{box}"><img src="assets/clips/{cid}.jpg" alt="" />'
                         f'<video id="{cid}-v" class="clip" src="assets/clips/{cid}.mp4" data-start="{start:.3f}" '
                         f'data-duration="{dur:.3f}" muted playsinline></video></div>')
    for k, pl in enumerate(p.get("pills", [])):
        parts.append(f'<div id="{p["id"]}-p{k}" class="pill" style="left:{pl["x"]}px;top:{pl["y"]}px">{esc(pl["text"])}</div>')
        # Pills pop on as their panel arrives (the cover's are there from frame 0).
        if i:
            tweens.append(f'tl.fromTo("#{p["id"]}-p{k}", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, '
                          f'ease: "back.out(2)" }}, {arrive[i] + 0.35 + 0.12 * k:.3f});')
    if p["id"] == "cover":
        px = min(190, int(940 / (0.70 * max(len(l) for l in p["lines"]))))
        lines = "".join(f'<span class="ln">{esc(l)}</span>' for l in p["lines"])
        top = 200 + int(px * 0.92 * len(p["lines"])) + 60
        parts.append(f'<div id="cover-stack" class="stack" style="top:200px;font-size:{px}px">{lines}<span class="bar"></span></div>'
                     f'<div class="place" style="top:{top}px">{esc(p["place"])}</div>'
                     f'<div class="facts" style="top:{top + 76}px">{esc(p["facts"])}</div>')
    else:
        anim = p.get("anim", ANIMS[(i - 1) % len(ANIMS)])
        body, tw = stack(p["id"], p["lines"], 560 if p["id"] == "end" else 200, anim, period, at=arrive[i] - 0.05,
                         max_px=150 if p["id"] == "end" else 170)
        parts.append(body)
        tweens.append(tw)
        for k, s in enumerate(p.get("small", [])):
            parts.append(f'<div id="end-s{k}" class="small" style="top:{1060 + 64 * k}px">{esc(s)}</div>')
            tweens.append(f'tl.fromTo("#end-s{k}", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, '
                          f'ease: "power2.out" }}, {arrive[i] + period * len(p["lines"]):.3f});')
    markup.append(f'<div id="pn-{p["id"]}" class="panel{" dark" if p["id"] == "end" else ""}" style="left:{ox}px">\n      '
                  + "\n      ".join(parts) + "\n    </div>")

# Camera: drift a little while it holds, then swipe one panel on the beat.
cam = ['tl.set("#track", { x: 0 }, 0);']
for i in range(len(panels)):
    x0 = -i * W
    if i < len(panels) - 1:
        cam.append(f'tl.to("#track", {{ x: {x0 - 36}, duration: {leave[i] - arrive[i]:.3f}, ease: "none" }}, {arrive[i]:.3f});')
        cam.append(f'tl.to("#track", {{ x: {x0 - W}, duration: {period:.3f}, ease: "expo.inOut" }}, {leave[i]:.3f});')
    else:
        cam.append(f'tl.to("#track", {{ x: {x0 - 24}, duration: {leave[i] - arrive[i]:.3f}, ease: "none" }}, {arrive[i]:.3f});')

nl = "\n    "
(proj / "compositions/canvas.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: var(--cream); }}
    #track {{ position: absolute; left: 0; top: 0; width: {W * len(panels)}px; height: {H}px; }}
    .panel {{ position: absolute; top: 0; width: {W}px; height: {H}px; }}
    .endpanel {{ position: absolute; left: 0; top: -40px; width: {W + 400}px; height: {H + 80}px; background: var(--emerald); }}
    .card {{ position: absolute; background: var(--white); padding: 14px; border-radius: 18px;
      box-shadow: 0 28px 60px rgba(26,26,26,.22), 0 4px 12px rgba(26,26,26,.10); }}
    .card img, .card video {{ position: absolute; inset: 14px; width: calc(100% - 28px); height: calc(100% - 28px); object-fit: cover; border-radius: 8px; }}
    .pill {{ position: absolute; background: var(--emerald); color: var(--white); font-size: 36px; font-weight: 900; letter-spacing: .04em;
      text-transform: uppercase; padding: 14px 26px 16px; border-radius: 999px; white-space: nowrap; box-shadow: 0 10px 24px rgba(11,79,66,.3); }}
    .stack {{ position: absolute; left: 64px; right: 140px; font-weight: 900; line-height: .92; letter-spacing: -.035em; text-transform: uppercase; color: var(--emerald); }}
    .stack .ln {{ display: block; transform-origin: 0% 60%; white-space: nowrap; }}
    .stack .mk {{ display: inline-block; overflow: hidden; padding-bottom: .1em; margin-bottom: -.1em; vertical-align: top; }}
    .stack .ch {{ display: inline-block; }}
    .stack .bar {{ display: block; width: 220px; height: 18px; margin-top: 26px; background: var(--emerald); border-radius: 4px; transform-origin: 0 50%; }}
    .dark .stack {{ color: var(--white); }}
    .dark .stack .bar {{ background: var(--cream); }}
    .place {{ position: absolute; left: 64px; font-size: 44px; font-weight: 800; letter-spacing: .1em; color: var(--ink); }}
    .facts {{ position: absolute; left: 64px; background: var(--emerald); font-size: 44px; font-weight: 900; letter-spacing: .05em; color: var(--white); padding: 14px 24px 16px; border-radius: 12px; }}
    .small {{ position: absolute; left: 64px; right: 64px; font-size: 40px; font-weight: 700; color: var(--cream); white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="canvas" data-width="{W}" data-height="{H}" data-layout-allow-overlap data-layout-allow-overflow>
    <div id="track">
    {nl.join(markup)}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {nl.join(cam)}
    {nl.join(tweens)}
    window.__timelines["canvas"] = tl;
  </script>
</template>
""")

audio = ""
if (proj / "assets/music/bed.wav").exists():
    audio = (f'      <audio id="music" class="clip" src="assets/music/bed.wav" data-start="0" data-duration="{total}" '
             f'data-track-index="3" data-volume="1"></audio>')
(proj / "index.html").write_text(f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* Sagareus external brand, listing2 "auto-sliding carousel": Off-White canvas, white photo cards, Emerald type. */
      :root {{ --emerald: #0B4F42; --cream: #F5F0E8; --white: #FFFFFF; --ink: #1a1a1a; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #F5F0E8; }}
      body {{ font-family: Inter, sans-serif; color: var(--ink); }}
      #root {{ width: 100%; height: 100%; position: relative; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
      <div id="canvas" data-composition-id="canvas" data-composition-src="compositions/canvas.html" data-start="0" data-duration="{total}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>
{audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
print(f"{len(panels)} panels, {total}s, beat {period}s")
for i, p in enumerate(panels):
    print(f"  {p['id']:<9} in view {arrive[i]:6.2f} -> {leave[i]:6.2f}")

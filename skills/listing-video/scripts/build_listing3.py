#!/usr/bin/env python3
"""Build a listing3 video: "Editorial". Full-screen photos with a slow push-in and soft cross-fades, and
magazine-style type in the lower third on a soft dark-grey backing: a small spaced Inter kicker over a
Fraunces title in sentence case with an italic accent. Calm where listing1 is loud and listing2 is playful. One vertical video, every channel.

Usage: python3 build_listing3.py <listing folder>      (run music.py first; it picks the acoustic track for listing3)

Reads <folder>/shots.json:
  {
    "style": "listing3",
    "cover": {"photo": "p17.jpg", "x0": 0.45, "x1": 0.55, "beats": 4, "kicker": "NORTON GRAND · EVERETT",
              "title": ["For *rent*"], "facts": "2 bed · 1 bath · 808 sq ft"},
    "shots": [{"id": "kitchen", "photo": "p02.jpg", "x0": 0.2, "x1": 0.4, "beats": 4,
               "kicker": "THE KITCHEN", "title": ["New fridge, oven", "*+ dishwasher*"]}],
    "end": {"beats": 5, "title": ["Schedule your", "*tour today.*"], "small": ["Managed by Sagareus Property Management."]}
  }
  photo: full screen at 1.12x cover size, panning x0 to x1 (0 = left edge, 1 = right edge), optional "y".
  title: 1 or 2 lines, sentence case; *words* in asterisks set in Fraunces italic.
Each shot fades in over the one before it, landing fully on its first beat; titles rise out of a mask.
Fonts: Fraunces (SIL OFL, assets/fonts) for titles, Inter for kickers and small type.
"""
import html, json, re, shutil, subprocess, sys
from pathlib import Path

proj = Path(sys.argv[1]).resolve()
skill = Path(__file__).resolve().parents[1]
spec = json.loads((proj / "shots.json").read_text())
if spec.get("style") != "listing3":
    sys.exit(f"build_listing3.py makes listing3; shots.json says {spec.get('style')!r}")
period = json.loads((proj / "assets/music/beat.json").read_text())["period"]
W, H, XF = 1080, 1920, 0.6  # cross-fade length, seconds
esc = html.escape
(proj / "compositions").mkdir(exist_ok=True)
for d in ("photos", "music", "fonts"):
    (proj / "assets" / d).mkdir(parents=True, exist_ok=True)
for f in ("Fraunces.ttf", "Fraunces-Italic.ttf", "OFL-Fraunces.txt"):
    shutil.copy(skill / "assets/fonts" / f, proj / "assets/fonts" / f)
for f in ("package.json", "hyperframes.json", "meta.json"):
    if not (proj / f).exists():
        (proj / f).write_text((skill / "template" / f).read_text().replace("sagavid-project", f"listing-{proj.name}"))
for old in (proj / "compositions").glob("*.html"):
    old.unlink()


def size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
    return tuple(int(v) for v in out.split(","))


def title_html(sid, lines):
    """Masked title lines; *text* becomes Fraunces italic."""
    out = []
    for k, line in enumerate(lines):
        inner = re.sub(r"\*(.+?)\*", lambda m: f"<em>{m.group(1)}</em>", esc(line))
        out.append(f'<span class="tl"><span id="{sid}-t{k}" class="tm">{inner}</span></span>')
    return "".join(out)


def photo_layer(sid, shot, dur):
    src = proj / "source/photos" / shot["photo"]
    w, h = size(src)
    if min(w, h) < 1200:
        sys.exit(f"{shot['photo']} is {w}x{h}: too small for full screen. Pick another photo.")
    shutil.copy(src, proj / "assets/photos" / shot["photo"])
    s = max(W / w, H / h) * 1.12
    PW, PH = round(w * s), round(h * s)
    y = -round((PH - H) * shot.get("y", 0.5))
    x0, x1 = (-round((PW - W) * shot.get(k, 0.5)) for k in ("x0", "x1"))
    body = (f'<div id="{sid}-media" class="media"><img id="{sid}-img" class="photo" src="assets/photos/{shot["photo"]}" alt="" '
            f'style="width:{PW}px;height:{PH}px;top:{y}px" /></div><div class="shade"></div>')
    tw = (f'tl.fromTo("#{sid}-img", {{ x: {x0} }}, {{ x: {x1}, duration: {dur:.3f}, ease: "none" }}, 0);\n'
          f'    tl.fromTo("#{sid}-media", {{ scale: 1 }}, {{ scale: 1.06, duration: {dur:.3f}, ease: "none" }}, 0);')
    return body, tw


def scene(cid, body, tweens, fade):
    fade_tw = f'tl.fromTo("#{cid}-wrap", {{ opacity: 0 }}, {{ opacity: 1, duration: {XF}, ease: "power1.inOut" }}, 0);' if fade else ""
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    <div id="{cid}-wrap" class="wrap">
    {body}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {fade_tw}
    {tweens}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def text_block(sid, kicker, lines, top, at):
    body = (f'<div id="{sid}-txt" class="txt" style="top:{top}px"><div id="{sid}-bg" class="tbg"></div><div id="{sid}-k" class="kicker">{esc(kicker)}</div>'
            f'<div class="title">{title_html(sid, lines)}</div></div>')
    tw = (f'tl.fromTo("#{sid}-bg", {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }}, {at - 0.15:.3f});\n'
          f'    tl.fromTo("#{sid}-k", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }}, {at:.3f});\n'
          f'    tl.fromTo("#{sid}-txt .tm", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.9, ease: "power3.out", stagger: 0.14 }}, {at + 0.2:.3f});')
    return body, tw


hosts, t = [], 0.0
# Cover: on screen from frame 0 (the cover frame), so its text is already in place.
cv = spec["cover"]
dur = cv["beats"] * period
pb, pt = photo_layer("cover", cv, dur)
tb = (f'<div class="txt" style="top:1180px"><div class="tbg"></div><div class="kicker">{esc(cv["kicker"])}</div>'
      f'<div class="title big">{title_html("cover", cv["title"])}</div><div class="facts">{esc(cv["facts"])}</div></div>')
(proj / "compositions/cover.html").write_text(scene("cover", pb + "\n    " + tb, pt, fade=False))
hosts.append(("cover", 0.0, dur))
t = dur
for shot in spec["shots"]:
    sid, dur = shot["id"], shot["beats"] * period
    pb, pt = photo_layer(sid, shot, dur + XF)
    tb, tt = text_block(sid, shot["kicker"], shot["title"], 1240, XF * 0.7)
    (proj / "compositions" / f"{sid}.html").write_text(scene(sid, pb + "\n    " + tb, pt + "\n    " + tt, fade=True))
    hosts.append((sid, t - XF, dur + XF))
    t += dur
# End card: Off-White, Emerald Fraunces (listing1 and listing2 end on Emerald; this one stays light).
end = spec["end"]
dur = end["beats"] * period
small = "".join(f'<div id="end-s{k}" class="esmall" style="top:{1130 + 60 * k}px">{esc(s)}</div>' for k, s in enumerate(end.get("small", [])))
eb = (f'<div class="epanel"></div><div class="txt etxt" style="top:700px">'
      f'<div class="title big">{title_html("end", end["title"])}</div></div>{small}')
et = (f'tl.fromTo(".etxt .tm", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.9, ease: "power3.out", stagger: 0.16 }}, {XF * 0.8:.3f});\n'
      f'    tl.fromTo(".esmall", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, {XF + 0.9:.3f});')
(proj / "compositions/endcard.html").write_text(scene("endcard", eb, et, fade=True))
hosts.append(("endcard", t - XF, dur + XF))
total = round(t + dur, 3)

host_tags = "\n".join(
    f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
    f'data-duration="{d:.3f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{k + 1}"></div>'
    for k, (cid, s, d) in enumerate(hosts))
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
      /* Sagareus external brand, listing3 "Editorial": Emerald, Off-White, White; Fraunces titles (video only), Inter details. */
      @font-face {{ font-family: "Fraunces"; src: url("assets/fonts/Fraunces.ttf") format("truetype"); font-weight: 100 900; font-style: normal; }}
      @font-face {{ font-family: "Fraunces"; src: url("assets/fonts/Fraunces-Italic.ttf") format("truetype"); font-weight: 100 900; font-style: italic; }}
      :root {{ --emerald: #0B4F42; --cream: #F5F0E8; --white: #FFFFFF; --ink: #1a1a1a; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #111; }}
      body {{ font-family: Inter, sans-serif; color: var(--white); }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      .wrap {{ position: absolute; inset: 0; }}
      .media {{ position: absolute; inset: 0; transform-origin: 50% 40%; }}
      .photo {{ position: absolute; left: 0; max-width: none; }}
      .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,.35) 62%, rgba(0,0,0,.62) 82%, rgba(0,0,0,.5) 100%); }}
      .txt {{ position: absolute; left: 72px; max-width: 936px; isolation: isolate; }}
      /* Emerald backing, high opacity, feathered edges: keeps the type readable over a bright photo. */
      /* Dark grey, no visible edge, kept short (Brittany 2026-10-26): an oversized shape, heavily blurred, so it fades to nothing. */
      .tbg {{ position: absolute; left: -70px; right: -80px; top: -46px; bottom: -42px; z-index: -1; background: rgba(26,26,26,.72);
        border-radius: 100px; filter: blur(40px); }}
      .kicker {{ font-size: 30px; font-weight: 700; letter-spacing: .32em; text-transform: uppercase; color: var(--cream); margin-bottom: 14px; }}
      .title {{ font-family: "Fraunces", serif; font-weight: 420; font-size: 104px; line-height: 1.02; letter-spacing: -.01em;
        font-variation-settings: "opsz" 144, "SOFT" 50, "WONK" 0; color: var(--white); }}
      .title.big {{ font-size: 150px; }}
      .title em {{ font-style: italic; font-weight: 380; }}
      .tl {{ display: block; overflow: hidden; padding-bottom: .14em; margin-bottom: -.14em; }}
      .tm {{ display: inline-block; white-space: nowrap; }}
      .facts {{ margin-top: 30px; font-size: 38px; font-weight: 600; letter-spacing: .04em; color: var(--white); }}
      .epanel {{ position: absolute; inset: 0; background: var(--cream); }}
      .etxt .title {{ color: var(--emerald); text-shadow: none; }}
      .etxt {{ max-width: none; right: 72px; }}
      .esmall {{ position: absolute; left: 72px; right: 72px; font-size: 38px; font-weight: 600; color: var(--ink); white-space: nowrap; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
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
    print(f"  {cid:<9} {s:7.3f} -> {s + d:7.3f}")

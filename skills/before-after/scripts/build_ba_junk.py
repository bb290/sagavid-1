#!/usr/bin/env python3
"""Build a before/after video in the ba-junk template ("Left behind": a move-out where belongings were left).

Story (Brittany 2026-11-18): Part 1 shows only what was left, while the staff voiceover walks the SOP (nothing moves
until the resident confirms in writing). Part 2 is the cleanup: an Emerald squeegee bar ("the Sweep") wipes each
before shot to the same spot clean, back to back. Ends on the turnover standard, "Safe. Clean. Working. Warm." one
word at a time, then the Rent Ready stamp, then the Off-White Sagareus end card. Footage is always full screen; text,
stickers and captions sit on top. Voice is a real staff recording (never generated), from voice.py.

Usage: python3 build_ba_junk.py <project>     (after voice.py; music.py <project> <seconds> --style ba-junk after the
                                               first build prints the length; then rebuild to pick up the bed)

<project>/episode.json (times: seconds on the tightened voice, "word" = first match at or after the scene start,
"word@12.5" = first match at or after 12.5 s):
  {"style": "ba-junk", "end": 36.45, "caption_until": 32.4,
   "clips": {"hook": {"src": "moveout.mp4", "in": 1.8, "dur": 5.2, "speed": 1, "freeze": null}, ...},
   "scenes": [
     {"type": "shot", "start": 0, "clips": ["hook"], "tag": "Move-out",
      "items": [{"k": "big", "kicker": "Keys in the lockbox", "kicker_at": "Keys", "text": "Left behind.", "at": "look"},
                {"k": "sticker", "text": "Tarps", "x": 300, "y": 700, "at": "this", "ell": [x, y, w, h]},
                {"k": "snap", "at": "photos", "label": "Photo 1"},
                {"k": "pills", "y": 1200, "list": [["Call", "call"], ["Text", "text"], ["Email", "email"]]},
                {"k": "dim", "at": "Something"}, {"k": "bubble", "who": "Resident", "text": "...", "at": "Something", "out": 25.2},
                {"k": "done", "text": "In writing", "at": "left", "y": 1180},
                {"k": "big", "text": "Deep clean", "at": "deep", "pill": true},
                {"k": "words", "list": [["Safe.", "Safe"], ...]}, {"k": "line", "text": "Good to go.", "at": "Good"},
                {"k": "stamp", "text": "Rent Ready", "at": "Rent"}]},
     {"type": "sweeps", "start": "But", "pairs": [
        {"before": [["bagsB", "But"]], "after": "bagsA", "sweep": "trash", "done": "Cleared",
         "stickers": [{"text": "Bags", "x": 380, "y": 900}]}, ...]}]}
Clips are cut from <project>/source/clips/<src> into assets/clips/<name>.mp4 (1080x1920, 30 fps, no audio):
"speed" < 1 slows them, "freeze" holds the frame from that many output seconds on (the photo snap).
"""
import html, json, math, re, shutil, subprocess, sys
from pathlib import Path

ep = Path(sys.argv[1]).resolve()
skill = Path(__file__).resolve().parents[1]
spec = json.loads((ep / "episode.json").read_text())
if spec.get("style") != "ba-junk":
    sys.exit(f"build_ba_junk.py makes the ba-junk template; episode.json says {spec.get('style')!r}")
words = [w for w in json.loads((ep / "assets/vo/tight.json").read_text())["words"] if w["end"] - w["start"] >= 0.03]
W, H, FPS = 1080, 1920, 30
END, END_LEN = float(spec["end"]), float(spec.get("end_len", 3.0))
TOTAL = round(END + END_LEN, 3)
TILT, SWEEP = 4, 0.42              # squeegee tilt (degrees) and how long one Sweep takes
CAP_TOP = int(spec.get("caption_top", 1440))
esc = html.escape

(ep / "compositions").mkdir(exist_ok=True)
for old in (ep / "compositions").glob("*.html"):
    old.unlink()
for sub in ("sfx", "fonts"):
    shutil.copytree(skill / "template/assets" / sub, ep / "assets" / sub, dirs_exist_ok=True)
for f in ("package.json", "hyperframes.json", "meta.json"):
    if not (ep / f).exists():
        (ep / f).write_text((skill / "template" / f).read_text().replace("sagavid-project", f"ba-{ep.name}"))


def norm(s):
    return re.sub(r"[^a-z0-9']", "", s.lower())


def when(v, t0=0.0):
    """Absolute seconds: a number, a word (first at or after t0), or "word@seconds"."""
    if isinstance(v, (int, float)):
        return float(v)
    if "@" in v:
        v, t0 = v.split("@")[0], float(v.split("@")[1])
    for w in words:
        if w["start"] >= t0 - 0.05 and norm(w["text"]) == norm(v):
            return w["start"]
    sys.exit(f'word "{v}" not found after {t0:.2f}s in tight.json')


# ---- clips -------------------------------------------------------------------------------------------------
(ep / "assets/clips").mkdir(parents=True, exist_ok=True)
for name, c in spec["clips"].items():
    out = ep / "assets/clips" / f"{name}.mp4"
    sig = json.dumps({**c, "_v": 3}, sort_keys=True)
    sigf = out.with_suffix(".json")
    if out.exists() and sigf.exists() and sigf.read_text() == sig:
        continue
    speed, dur = float(c.get("speed", 1)), float(c["dur"])
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,setpts=PTS/{speed},fps={FPS},setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
    src_len = dur * speed
    if c.get("freeze") is not None:
        fz = float(c["freeze"])
        src_len = fz * speed
        vf += f",tpad=stop_mode=clone:stop_duration={dur - fz + 0.1:.2f}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['in']}", "-t", f"{src_len + 0.05:.3f}",
                    "-i", str(ep / "source/clips" / c["src"]), "-vf", vf, "-t", f"{dur:.3f}", "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", f"{FPS}",
                    # always SDR-tagged: phone HDR (HLG) tags make HyperFrames switch to HDR layered compositing,
                    # which dropped every overlay on the ba-trashed sample (2026-11-18)
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)],
                   check=True)
    sigf.write_text(sig)


def video(vid, name, start, dur, track=0, cls="footage"):
    return (f'<video id="{vid}" class="clip {cls}" src="assets/clips/{name}.mp4" data-start="{start:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="{track}" muted playsinline></video>')


class Tw(list):
    def add(self, s):
        self.append(s)


sfx = []          # (absolute time, file, volume, duration)

# ---- the Sweep: an Emerald bar with a white leading edge, tilted, crossing right to left -----------------------
D = 960 * math.tan(TILT * math.pi / 180)


def poly(cx):       # the region right of the bar's centre line (where the AFTER shows)
    a, b = cx + D, cx - D
    return f"polygon({a:.1f}px 0px, 1400px 0px, 1400px 1920px, {b:.1f}px 1920px)"


def sweep(sid, t, tw):
    """Bar from off the right edge to off the left edge between t and t + SWEEP; the AFTER wrapper follows it."""
    x0, x1 = W + D + 80, -D - 80
    f0, f1 = round(t * FPS), round((t + SWEEP) * FPS)
    tw.add(f'gsap.set("#{sid}-aw", {{ clipPath: "{poly(x0)}" }}); gsap.set("#{sid}-bar", {{ x: {x0:.1f}, rotation: {TILT} }});')
    for f in range(f0, f1 + 1):
        p = min(1.0, (f - f0) / max(1, f1 - f0))
        e = 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2
        c = x0 + (x1 - x0) * e
        tt = max(0, f / FPS - 0.002)
        tw.add(f'tl.set("#{sid}-aw", {{ clipPath: "{poly(c)}" }}, {tt:.3f}); tl.set("#{sid}-bar", {{ x: {c:.1f} }}, {tt:.3f});')
    tw.add(f'tl.set("#{sid}-aw", {{ clipPath: "none" }}, {t + SWEEP + 0.02:.3f});')
    return f'<div id="{sid}-bar" class="bar"></div>'


# ---- overlay items -----------------------------------------------------------------------------------------
FA = {"Call": "&#xf095;", "Text": "&#xf27a;", "Email": "&#xf0e0;", "check": "&#xf00c;", "camera": "&#xf030;"}


def sticker(sid, st, at, tw, out=None):
    rot = st.get("rot", -5)
    parts = []
    if st.get("ell"):
        x, y, w, h = st["ell"]
        parts.append(f'<svg id="{sid}-e" class="ell" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" viewBox="0 0 100 100" '
                     f'preserveAspectRatio="none"><path pathLength="1" d="M52 4 C80 3 97 24 96 50 C95 78 74 97 48 96 C22 95 4 76 5 49 '
                     f'C6 25 25 6 56 7"/></svg>')
        tw.add(f'tl.fromTo("#{sid}-e path", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.36, ease: "power2.out", immediateRender: false }}, {at - 0.3:.3f});')
        tw.add(f'tl.set("#{sid}-e", {{ opacity: 1 }}, {at - 0.3:.3f});')
    parts.append(f'<div id="{sid}" class="sticker" style="left:{st["x"]}px;top:{st["y"]}px">{esc(st["text"])}</div>')
    tw.add(f'tl.fromTo("#{sid}", {{ opacity: 0, scale: 1.5, rotation: {rot - 6} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.18, ease: "power3.out", immediateRender: false }}, {at:.3f});')
    sfx.append((at, "sfx-pop.mp3", 0.3, 0.72))
    if out is not None and st.get("out") is not None:      # a cut, not the Sweep: just gone
        tw.add(f'tl.set("#{sid}", {{ opacity: 0 }}, {out:.3f});')
    elif out is not None:      # knocked off by the Sweep
        tw.add(f'tl.to("#{sid}", {{ x: -420, y: 160, rotation: {rot - 38}, opacity: 0, duration: 0.34, ease: "power2.in" }}, {out:.3f});')
        if st.get("ell"):
            tw.add(f'tl.to("#{sid}-e", {{ opacity: 0, duration: 0.12 }}, {out:.3f});')
    return "".join(parts)


def item(sid, it, s0, tw, n):
    """One overlay; times converted to scene-relative seconds."""
    k = it["k"]
    rel = lambda v: when(v, s0) - s0
    iid = f"{sid}-i{n}"
    if k == "sticker":
        return sticker(iid, it, rel(it["at"]), tw, rel(it["out"]) if "out" in it else None)
    if k == "big":
        at = rel(it["at"])
        kick = ""
        if it.get("kicker"):
            ka = rel(it.get("kicker_at", it["at"]))
            kick = f'<div id="{iid}-k" class="kicker">{esc(it["kicker"])}</div>'
            tw.add(f'tl.fromTo("#{iid}-k", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {ka:.3f});')
        cls = "bigw pill" if it.get("pill") else "bigw"
        tw.add(f'tl.fromTo("#{iid}-w", {{ opacity: 0, scale: 1.45 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in", immediateRender: false }}, {at:.3f});')
        sfx.append((at + 0.18, "sfx-impact-bass-1.mp3", 0.28, 2.1))
        if "out" in it:
            tw.add(f'tl.to("#{iid}-w", {{ opacity: 0, duration: 0.15 }}, {rel(it["out"]):.3f});')
        top = it.get("y", 1150)
        return f'<div class="big" style="top:{top}px">{kick}<div id="{iid}-w" class="{cls}">{esc(it["text"])}</div></div>'
    if k == "snap":
        at = rel(it["at"])
        tw.add(f'tl.set("#{sid}-snapwrap", {{ scale: 0.86, rotation: -2.5 }}, {at:.3f}); tl.set("#{sid}-snapwrap", {{ className: "snapwrap on" }}, {at:.3f});')
        tw.add(f'tl.fromTo("#{iid}-fl", {{ opacity: 0.95 }}, {{ opacity: 0, duration: 0.32, ease: "power2.out", immediateRender: false }}, {at:.3f});')
        tw.add(f'tl.set("#{iid}-fl", {{ opacity: 0 }}, 0);')
        tw.add(f'tl.fromTo("#{iid}-c", {{ opacity: 0, y: -14 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at + 0.08:.3f});')
        sfx.append((at - 0.03, "sfx-shutter.mp3", 0.45, 0.6))
        return (f'<div id="{iid}-fl" class="flash"></div><div id="{iid}-c" class="chip cam"><span class="fa">{FA["camera"]}</span>'
                f'{esc(it.get("label", "Photo"))}</div>')
    if k == "pills":
        cells = []
        for j, (lbl, w) in enumerate(it["list"]):
            at = rel(w)
            cells.append(f'<div id="{iid}-p{j}" class="rpill"><span class="fa">{FA.get(lbl, FA["check"])}</span>{esc(lbl)}</div>')
            tw.add(f'tl.fromTo("#{iid}-p{j}", {{ opacity: 0, y: 26, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "power3.out", immediateRender: false }}, {at:.3f});')
            sfx.append((at, "sfx-click-soft.mp3", 0.4, 0.37))
        return f'<div class="reach" style="top:{it.get("y", 1200)}px">{"".join(cells)}</div>'
    if k == "dim":
        tw.add(f'tl.to("#{sid}-dim", {{ opacity: 1, duration: 0.3 }}, {rel(it["at"]):.3f});')
        return ""
    if k == "bubble":
        at = rel(it["at"])
        tw.add(f'tl.fromTo("#{iid}", {{ opacity: 0, y: 90, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {at:.3f});')
        if "out" in it:
            tw.add(f'tl.to("#{iid}", {{ opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }}, {rel(it["out"]):.3f});')
        sfx.append((at, "sfx-pop.mp3", 0.35, 0.72))
        return f'<div id="{iid}" class="bubble" style="top:{it.get("y", 560)}px"><small>{esc(it.get("who", ""))}</small>{esc(it["text"])}</div>'
    if k == "done":
        at = rel(it["at"])
        tw.add(f'tl.fromTo("#{iid}", {{ opacity: 0, scale: 1.6, rotation: -4 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.18, ease: "power4.in", immediateRender: false }}, {at:.3f});')
        if "out" in it:
            tw.add(f'tl.to("#{iid}", {{ opacity: 0, duration: 0.2 }}, {rel(it["out"]):.3f});')
        sfx.append((at + 0.16, "sfx-impact-bass-1.mp3", 0.3, 2.1))
        return (f'<div class="donewrap" style="top:{it.get("y", 1180)}px"><div id="{iid}" class="done big-done">'
                f'<span class="fa">{FA["check"]}</span>{esc(it["text"])}</div></div>')
    if k == "words":
        rows = []
        for j, (txt, w) in enumerate(it["list"]):
            at = rel(w)
            acc = " acc" if j == len(it["list"]) - 1 else ""
            rows.append(f'<div class="pw"><span id="{iid}-w{j}" class="pwi{acc}">{esc(txt)}</span></div>')
            tw.add(f'tl.fromTo("#{iid}-w{j}", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.26, ease: "power3.out", immediateRender: false }}, {at - 0.04:.3f});')
            tw.add(f'tl.set("#{iid}-w{j}", {{ yPercent: 110 }}, 0);')
            sfx.append((at, "sfx-click-soft.mp3", 0.35, 0.37))
        if it.get("dim_at"):
            tw.add(f'tl.to("#{iid}", {{ opacity: 0.16, duration: 0.2 }}, {rel(it["dim_at"]) - 0.05:.3f});')
        return f'<div id="{iid}" class="pwords" data-layout-allow-overlap style="top:{it.get("y", 860)}px">{"".join(rows)}</div>'
    if k == "line":
        at = rel(it["at"])
        tw.add(f'tl.fromTo("#{iid}", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power3.out", immediateRender: false }}, {at:.3f});')
        if "out" in it:
            tw.add(f'tl.to("#{iid}", {{ opacity: 0, duration: 0.15 }}, {rel(it["out"]):.3f});')
        return f'<div id="{iid}" class="pline" style="top:{it.get("y", 1500)}px">{esc(it["text"])}</div>'
    if k == "stamp":
        at = rel(it["at"])
        tw.add(f'tl.fromTo("#{iid}", {{ opacity: 0, scale: 1.8, rotation: -2 }}, {{ opacity: 1, scale: 1, rotation: -7, duration: 0.2, ease: "power4.in", immediateRender: false }}, {at:.3f});')
        sfx.append((at + 0.17, "sfx-impact-bass-1.mp3", 0.42, 2.1))
        return (f'<div class="stampwrap" style="top:{it.get("y", 640)}px"><div id="{iid}" class="stamp" data-layout-allow-overlap>'
                f'<span class="ink">{esc(it["text"])}</span></div></div>')
    sys.exit(f"unknown item kind {k!r}")


def scene_file(cid, body, tw):
    (ep / "compositions" / f"{cid}.html").write_text(f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    {body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + l for l in tw).strip()}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
""")


# ---- scenes ------------------------------------------------------------------------------------------------
scenes = spec["scenes"]
starts = [when(sc["start"]) for sc in scenes]
hosts = []
for i, sc in enumerate(scenes):
    sid = f"s{i + 1}"
    s0 = starts[i]
    s1 = starts[i + 1] if i + 1 < len(scenes) else END + 0.8      # the last shot runs under the end card's wipe
    dur = s1 - s0
    tw, parts = Tw(), []
    if sc["type"] == "shot":
        clips = sc["clips"]
        cuts = [0.0] + [when(c[1], s0) - s0 for c in clips[1:]] if clips and isinstance(clips[0], list) else None
        names = [c[0] if isinstance(c, list) else c for c in clips]
        if cuts is None:
            cuts = [dur * j / len(names) for j in range(len(names))]
        vids = []
        for j, nm in enumerate(names):
            a, b = cuts[j], cuts[j + 1] if j + 1 < len(names) else dur
            vids.append(video(f"{sid}-v{j}", nm, a, b - a))
            if j:
                sfx.append((s0 + a - 0.05, "sfx-whoosh-short.mp3", 0.18, 0.57))
        snap = any(it["k"] == "snap" for it in sc.get("items", []))
        parts.append(f'<div id="{sid}-snapwrap" class="snapwrap">{"".join(vids)}</div>' if snap else "".join(vids))
        parts.append('<div class="shade"></div>')
        parts.append(f'<div id="{sid}-dim" class="dim"></div>')
        if sc.get("tag"):
            cls = "after" if sc.get("tag_after") else "before"
            parts.append(f'<div id="{sid}-tag" class="tag {cls}">{esc(sc["tag"])}</div>')
        for n, it in enumerate(sc.get("items", [])):
            parts.append(item(sid, it, s0, tw, n))
    elif sc["type"] == "sweeps":
        pairs = sc["pairs"]
        p_starts = [when(p["before"][0][1], s0) - s0 for p in pairs]
        for j, p in enumerate(pairs):
            pid = f"{sid}p{j}"
            p0 = p_starts[j]
            p1 = p_starts[j + 1] if j + 1 < len(pairs) else dur
            sw = when(p["sweep"], s0) - s0
            bcuts = [when(b[1], s0) - s0 for b in p["before"]]
            for m, (bn, _) in enumerate(p["before"]):
                a = max(p0, bcuts[m])
                b = bcuts[m + 1] if m + 1 < len(bcuts) else sw + SWEEP + 0.05
                parts.append(video(f"{pid}-b{m}", bn, a, b - a))
                if m:
                    sfx.append((s0 + a - 0.03, "sfx-click-soft.mp3", 0.3, 0.37))
            parts.append(f'<div id="{pid}-aw" class="aw">{video(f"{pid}-a", p["after"], sw, p1 - sw, track=1)}</div>')
            parts.append(f'<div class="shade" style="opacity:.6"></div>')
            parts.append(f'<div id="{pid}-tb" class="tag before">Before</div>')
            tw.add(f'gsap.set("#{pid}-tb", {{ opacity: 0 }}); tl.set("#{pid}-tb", {{ opacity: 1 }}, {p0:.3f}); tl.set("#{pid}-tb", {{ opacity: 0 }}, {sw + SWEEP * 0.5:.3f});')
            for n, st in enumerate(p.get("stickers", [])):
                at = when(st["at"], s0) - s0 if "at" in st else p0 + 0.12
                parts.append(sticker(f"{pid}-s{n}", st, at, tw, out=(when(st["out"], s0) - s0) if "out" in st else sw + 0.1))
            parts.append(sweep(pid, sw, tw))
            sfx.append((s0 + sw - 0.04, "sfx-whoosh.mp3", 0.34, 0.57))
            if p.get("done"):
                parts.append(f'<div id="{pid}-ok" class="tag after"><span class="fa">{FA["check"]}</span>{esc(p["done"])}</div>')
                tw.add(f'gsap.set("#{pid}-ok", {{ opacity: 0 }}); tl.fromTo("#{pid}-ok", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "power3.out", immediateRender: false }}, {sw + SWEEP - 0.08:.3f});')
                if j + 1 < len(pairs):
                    tw.add(f'tl.set("#{pid}-ok", {{ opacity: 0 }}, {p1:.3f});')
            for n, it in enumerate(p.get("items", [])):
                parts.append(item(pid, it, s0, tw, n))
    else:
        sys.exit(f"unknown scene type {sc['type']!r}")
    if i:
        tw.insert(0, f'gsap.set("#root", {{ opacity: 1 }});')
    scene_file(sid, "\n    ".join(p for p in parts if p), tw)
    hosts.append((sid, s0, dur))

# ---- end card: one last Sweep brings in the Off-White card ---------------------------------------------------
tw = Tw()
bar = sweep("ec", 0.0, tw)
body = (f'<div id="ec-aw" class="aw"><div class="ecard"><div class="ec-title"><span class="ln">Sagareus</span>'
        f'<span class="ln">Property</span><span class="ln">Management</span></div><div class="ec-url">sagareus.com</div></div></div>{bar}')
tw.add('tl.fromTo(".ec-title .ln", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.36, ease: "power3.out", stagger: 0.11, immediateRender: false }, 0.4);')
tw.add('gsap.set([".ec-title .ln", ".ec-url"], { opacity: 0 });')
tw.add('tl.fromTo(".ec-url", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.36, ease: "power2.out", immediateRender: false }, 0.9);')
scene_file("endcard", body, tw)
hosts.append(("endcard", END, END_LEN))
sfx.append((END - 0.04, "sfx-whoosh.mp3", 0.3, 0.57))

# ---- captions ----------------------------------------------------------------------------------------------
subprocess.run([sys.executable, str(Path(__file__).with_name("captions.py")), str(ep), "--until", f"{spec.get('caption_until', END)}",
                "--top", f"{CAP_TOP}"], check=True, stdout=subprocess.DEVNULL)

host_tags = "\n".join(
    f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
    f'data-duration="{d:.3f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{k + 1}"></div>'
    for k, (cid, s, d) in enumerate(hosts))
cap_until = float(spec.get("caption_until", END))
over = (f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" '
        f'data-duration="{cap_until:.3f}" data-track-index="3" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:50"></div>')
audio = [f'      <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-track-index="4" data-volume="1"></audio>']
if (ep / "assets/music/bed-ducked.wav").exists():
    audio.append(f'      <audio id="music" class="clip" src="assets/music/bed-ducked.wav" data-start="0" data-duration="{TOTAL}" data-track-index="5" data-volume="1"></audio>')
for k, (t, f, v, d) in enumerate(sorted(sfx)):
    audio.append(f'      <audio id="sfx{k}" class="clip" src="assets/sfx/{f}" data-start="{max(0, t):.3f}" data-duration="{d}" data-track-index="{6 + k}" data-volume="{v}"></audio>')

STAMP_MASK = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='360' height='360'><filter id='n'>"
              "<feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='2' seed='7'/><feColorMatrix values='0 0 0 0 0  "
              "0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 2.05'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")
(ep / "index.html").write_text(f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* Sagareus Design System tokens (external): Emerald, Off-White, White, Ink; Inter. */
      :root {{ --emerald: #0B4F42; --cream: #F5F0E8; --white: #FFFFFF; --ink: #1a1a1a; }}
      @font-face {{ font-family: "FA"; src: url("assets/fonts/fa-solid-900.woff2") format("woff2"); font-weight: 900; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #111; }}
      body {{ font-family: Inter, sans-serif; color: var(--white); }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      .fa {{ font-family: "FA"; font-weight: 900; }}
      .footage {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      .aw {{ position: absolute; inset: 0; }}
      .snapwrap {{ position: absolute; inset: 0; transform-origin: 50% 46%; }}
      .snapwrap.on {{ outline: 26px solid var(--white); box-shadow: 0 30px 80px rgba(0,0,0,.6); }}
      .flash {{ position: absolute; inset: 0; background: var(--white); opacity: 0; }}
      .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 20%, rgba(0,0,0,0) 52%, rgba(0,0,0,.42) 78%, rgba(0,0,0,.2) 100%); }}
      .dim {{ position: absolute; inset: 0; background: rgba(0,0,0,.42); opacity: 0; }}
      .tag {{ position: absolute; top: 200px; left: 64px; font-size: 30px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase;
             padding: 12px 26px; border-radius: 9999px; display: flex; gap: 14px; align-items: center; }}
      .tag.before {{ background: rgba(26,26,26,.72); }}
      .tag.after {{ left: auto; right: 64px; background: var(--emerald); }}
      .tag .fa {{ font-size: 26px; }}
      .sticker {{ position: absolute; background: var(--white); color: var(--ink); border: 7px solid var(--ink); border-radius: 18px;
                 font-weight: 800; font-size: 62px; letter-spacing: .01em; padding: 6px 30px 12px; text-transform: uppercase;
                 white-space: nowrap; box-shadow: 0 12px 34px rgba(0,0,0,.4); opacity: 0; }}
      .ell {{ position: absolute; opacity: 0; overflow: visible; filter: drop-shadow(0 0 10px rgba(0,0,0,.45)); }}
      .ell path {{ fill: none; stroke: var(--white); stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; stroke-width: 1.5; }}
      .chip {{ position: absolute; top: 200px; right: 64px; background: var(--white); color: var(--ink); font-size: 30px; font-weight: 800;
              letter-spacing: .14em; text-transform: uppercase; padding: 12px 26px; border-radius: 9999px; display: flex; gap: 14px; align-items: center; opacity: 0; }}
      .big {{ position: absolute; left: 64px; right: 64px; }}
      .kicker {{ display: inline-block; font-size: 32px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--cream); margin-bottom: 18px;
                background: rgba(26,26,26,.72); padding: 10px 22px; border-radius: 9999px; opacity: 0; }}
      .bigw {{ font-size: 176px; font-weight: 800; line-height: .95; letter-spacing: -.045em; text-shadow: 0 6px 30px rgba(0,0,0,.5);
              transform-origin: 0 60%; opacity: 0; }}
      .bigw.pill {{ display: inline-block; font-size: 120px; background: var(--emerald); padding: 4px 40px 22px; border-radius: 28px; text-shadow: none; }}
      .reach {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; gap: 24px; }}
      .rpill {{ background: var(--emerald); border: 6px solid var(--white); border-radius: 9999px; padding: 14px 32px; display: flex; gap: 16px;
               align-items: center; font-weight: 800; font-size: 44px; box-shadow: 0 10px 30px rgba(0,0,0,.4); opacity: 0; }}
      .rpill .fa {{ font-size: 38px; }}
      .bubble {{ position: absolute; left: 96px; right: 96px; background: var(--white); color: var(--ink); border-radius: 54px 54px 54px 14px;
                padding: 40px 52px 46px; font-size: 60px; font-weight: 600; line-height: 1.22; box-shadow: 0 22px 60px rgba(0,0,0,.5); opacity: 0; }}
      .bubble small {{ display: block; font-size: 28px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: var(--emerald); margin-bottom: 14px; }}
      .donewrap {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; }}
      .done {{ background: var(--emerald); border: 6px solid var(--white); border-radius: 9999px; padding: 16px 40px 20px; display: flex; gap: 18px;
              align-items: center; font-weight: 800; font-size: 56px; box-shadow: 0 12px 34px rgba(0,0,0,.45); opacity: 0; }}
      .bar {{ position: absolute; left: -40px; top: -100px; width: 80px; height: 2120px; background: var(--emerald); border-left: 18px solid var(--white);
             transform-origin: 40px 1060px; box-shadow: 0 0 50px rgba(0,0,0,.5); }}
      .pwords {{ position: absolute; left: 64px; right: 64px; }}
      .pw {{ overflow: hidden; padding-bottom: .06em; }}
      .pwi {{ display: inline-block; font-size: 168px; font-weight: 800; line-height: 1; letter-spacing: -.045em; text-shadow: 0 6px 30px rgba(0,0,0,.45); }}
      .pwi.acc {{ background: var(--emerald); padding: 0 .14em .08em; border-radius: 26px; text-shadow: none; }}
      .pline {{ position: absolute; left: 64px; right: 64px; font-size: 64px; font-weight: 800; text-shadow: 0 4px 20px rgba(0,0,0,.5); opacity: 0; }}
      .stampwrap {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; }}
      .stamp {{ border: 14px solid var(--emerald); border-radius: 24px; padding: 14px; background: rgba(245,240,232,.95); opacity: 0;
               box-shadow: 0 14px 40px rgba(0,0,0,.35); -webkit-mask-image: {STAMP_MASK}; mask-image: {STAMP_MASK}; }}
      .stamp .ink {{ display: block; border: 5px solid var(--emerald); border-radius: 12px; padding: 22px 50px 30px; white-space: nowrap;
                    font-size: 132px; font-weight: 800; line-height: 1; letter-spacing: .03em; text-transform: uppercase; color: var(--emerald); }}
      .ecard {{ position: absolute; inset: 0; background: var(--cream); }}
      .ec-title {{ position: absolute; left: 110px; right: 64px; top: 640px; font-size: 140px; font-weight: 800; line-height: 1; letter-spacing: -.04em; color: var(--emerald); }}
      .ec-title .ln {{ display: block; }}
      .ec-url {{ position: absolute; left: 110px; top: 1120px; font-size: 48px; font-weight: 600; color: var(--ink); letter-spacing: .02em; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{host_tags}
{over}
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
print(f"{len(hosts)} scenes, {TOTAL}s, {len(sfx)} sound effects")
for cid, s, d in hosts:
    print(f"  {cid:<8} {s:7.3f} -> {s + d:7.3f}")

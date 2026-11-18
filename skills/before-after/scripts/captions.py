#!/usr/bin/env python3
"""Burned-in captions for a Property Management IRL episode.

Usage: python3 captions.py <episode_dir> [--until SECONDS] [--top PX]

Reads <episode>/assets/vo/tight.json (word timings after the voiceover edit) and writes
<episode>/compositions/captions.html: 2-4 word groups, one at a time, the spoken word
highlighted in Emerald on a dark scrim. Words at or after --until (the end card) are skipped.
"""
import html, json, sys
from pathlib import Path

ep = Path(sys.argv[1])
until = float(sys.argv[sys.argv.index("--until") + 1]) if "--until" in sys.argv else 1e9
top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 1150  # y of the caption line
words = [dict(x) for x in json.loads((ep / "assets/vo/tight.json").read_text())["words"] if x["start"] < until]

# "rent ready" is written "rent-ready" on screen.
merged, i = [], 0
while i < len(words):
    a = words[i]
    if a["text"].lower() == "rent" and i + 1 < len(words) and words[i + 1]["text"].lower().startswith("ready"):
        b = words[i + 1]
        merged.append({"text": f"{a['text']}-{b['text']}", "start": a["start"], "end": b["end"]})
        i += 2
    else:
        merged.append(a)
        i += 1
words = merged

# Groups: 2-4 words; break at a sentence end, a comma before a pause, or a pause of 150 ms.
groups, g = [], []
for i, x in enumerate(words):
    g.append(x)
    nxt = words[i + 1] if i + 1 < len(words) else None
    gap = (nxt["start"] - x["end"]) if nxt else 9
    if (nxt is None or x["text"][-1] in ".?!" or len(g) >= 4
            or (x["text"][-1] == "," and (len(g) >= 2 or gap >= 0.3))
            or (gap >= 0.15 and len(g) >= 2)):
        groups.append(g)
        g = []

lines, js = [], []
for gi, g in enumerate(groups):
    st = max(0.1, g[0]["start"] - 0.06)
    en = g[-1]["end"] + 0.12
    if gi + 1 < len(groups):
        en = min(en, groups[gi + 1][0]["start"] - 0.06)
    en = max(en, st + 0.3)
    spans = " ".join(f'<span class="cw" id="cap{gi}-{k}">{html.escape(x["text"])}</span>' for k, x in enumerate(g))
    lines.append(f'    <div id="cap{gi}" class="clip capgroup" data-start="{st:.2f}" data-duration="{en - st:.2f}"><div class="capbox">{spans}</div></div>')
    js.append(f'  tl.fromTo("#cap{gi} .capbox", {{scale: 0.94, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.12, ease: "power2.out"}}, {st:.2f});')
    for k, x in enumerate(g):
        js.append(f'  tl.set("#cap{gi}-{k}", {{backgroundColor: "#0B4F42"}}, {max(st, x["start"]):.2f});')
        if k + 1 < len(g):
            js.append(f'  tl.set("#cap{gi}-{k}", {{backgroundColor: "rgba(11,79,66,0)"}}, {g[k + 1]["start"]:.2f});')
    js.append(f'  tl.to("#cap{gi} .capbox", {{opacity: 0, duration: 0.08, ease: "power2.in"}}, {en - 0.08:.2f});')

nl = "\n"
(ep / "compositions/captions.html").write_text(f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .capgroup {{ position: absolute; left: 0; right: 0; top: {top}px; text-align: center; overflow: visible; }}
    .capbox {{ display: inline-block; max-width: 940px; background: rgba(0,0,0,.42); border-radius: 18px; padding: 10px 14px;
      font-family: Inter, sans-serif; font-weight: 900; font-size: 64px; line-height: 1.2; color: #FFFFFF; letter-spacing: -0.01em; }}
    .cw {{ display: inline-block; padding: 0 10px 4px; border-radius: 12px; background: rgba(11,79,66,0); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{nl.join(lines)}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{nl.join(js)}
  window.__timelines["captions"] = tl;
  </script>
</template>
''')
for g in groups:
    print(f"{g[0]['start']:6.2f}  " + " ".join(x["text"] for x in g))

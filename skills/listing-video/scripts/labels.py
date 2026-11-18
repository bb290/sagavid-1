"""Big stacked uppercase labels and their entrances, shared by every listing style.

stack(pid, lines, top, anim, period, at) returns (markup, GSAP tweens). Tweens start at `at` seconds on
the scene's timeline. Each style's index.html styles .stack/.ln/.bar/.mk/.ch (colour, shadow, bar).

Entrances, adapted from the HyperFrames registry: bottom-up-letters (rise), top-down-letters (drop),
tracking-in (track), caption-clip-wipe (wipe), line-by-line-slide (slide), caption-kinetic-slam (slam),
plus the pilot's pop. Styles rotate through ANIMS so no two neighbouring slides move alike.
"""
import html

esc = html.escape
ANIMS = ["rise", "wipe", "slam", "track", "drop", "slide"]
CHAR_ANIMS = {"rise", "drop"}


def stack(pid, lines, top, anim, period, at=0.0, max_px=170):
    """Big stacked uppercase label; `anim` picks how it enters, then the underline wipes."""
    px = min(max_px, int(940 / (0.70 * max(len(l) for l in lines))))
    def inner(l):
        if anim not in CHAR_ANIMS:
            return esc(l)
        chars = "".join(f'<span class="ch">{"&nbsp;" if c == " " else esc(c)}</span>' for c in l)
        return f'<span class="mk">{chars}</span>' if anim == "rise" else chars
    spans = "".join(f'<span id="{pid}-l{k}" class="ln">{inner(l)}</span>' for k, l in enumerate(lines))
    body = (f'<div id="{pid}-stack" class="stack" style="top:{top}px;font-size:{px}px">{spans}'
            f'<span id="{pid}-bar" class="bar"></span></div>')
    sel, n = f"#{pid}-stack", len(lines)
    nchars = sum(len(l) for l in lines)
    t0 = at + 0.04
    if anim == "hold":  # no entrance: carries the previous slide's identical label across the cut
        return body, f'tl.set("{sel} .ln", {{ opacity: 1 }}, {at:.3f});\n    tl.set("#{pid}-bar", {{ scaleX: 1 }}, {at:.3f});'
    if anim == "rise":
        tw = (f'tl.fromTo("{sel} .ch", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.48, ease: "back.out(1.7)", '
              f'stagger: 0.025 }}, {t0:.3f});')
        land = t0 + 0.025 * nchars + 0.3
    elif anim == "drop":
        tw = (f'tl.fromTo("{sel} .ch", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.22, ease: "power3.out", '
              f'stagger: 0.035 }}, {t0:.3f});')
        land = t0 + 0.035 * nchars + 0.1
    elif anim == "track":
        # scaleX, not letterSpacing: spacing snaps to whole pixels and stutters in the frame-by-frame render.
        tw = (f'tl.fromTo("{sel} .ln", {{ scaleX: 1.3, transformOrigin: "0% 50%", y: 14, opacity: 0 }}, {{ scaleX: 1, y: 0, '
              f'opacity: 1, duration: 0.9, ease: "power3.out", stagger: 0.1 }}, {t0:.3f});')
        land = t0 + 0.1 * n + 0.5
    elif anim == "wipe":
        tw = (f'tl.fromTo("{sel} .ln", {{ clipPath: "inset(-15% 100% -15% 0%)" }}, {{ clipPath: "inset(-15% 0% -15% 0%)", '
              f'duration: 0.3, ease: "power2.out", stagger: {period / 2:.3f} }}, {t0:.3f});')
        land = t0 + period / 2 * (n - 1) + 0.3
    elif anim == "slide":
        tw = (f'tl.fromTo("{sel} .ln", {{ x: -120, y: 18, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.34, '
              f'ease: "power3.out", stagger: 0.08 }}, {t0:.3f});')
        land = t0 + 0.08 * n + 0.25
    elif anim == "slam":  # alternating directions, line by line
        froms = ["x: -320", "x: 320", "y: 140"]
        tw = "\n    ".join(
            f'tl.fromTo("#{pid}-l{k}", {{ {froms[k % 3]}, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.22, '
            f'ease: "expo.out" }}, {t0 + period / 2 * k:.3f});' for k in range(n))
        land = t0 + period / 2 * (n - 1) + 0.2
    else:  # pop: the pilot's slam-in
        tw = (f'tl.fromTo("{sel} .ln", {{ scale: 1.35, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.16, '
              f'ease: "back.out(2.2)", stagger: {period / 4:.3f} }}, {t0:.3f});')
        land = at + 0.1 + period / 4 * n
    tweens = (f'{tw}\n'
              f'    tl.fromTo("#{pid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.22, ease: "expo.out" }}, {land:.3f});')
    return body, tweens

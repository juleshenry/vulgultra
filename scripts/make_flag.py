"""Generate the Vulgultra flag, site/static/img/flag.svg: a reverse prism.

A prism splits white light into colours; this runs it backwards with additive
light. The 36 lects of the Romance grid rise from the bottom edge as 36 hues
round the colour wheel. They merge six by six into the six tertiary colours,
two by two into the three pillars (red, green, blue), and the three into
white at the crown, which leaves the flag as one beam. The ten meeting points
are the ten spheres of the Tree of Life; the crown carries the three veils
above it. Behind, letters from the lexicon's spellings fall the other way,
the way Latin went.

    python3 scripts/make_flag.py
"""

import colorsys
import json
import math
import random
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEXICON = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "vulgultra_lexicon.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "site" / "static" / "img" / "flag.svg"
W, H = 1500, 1000
rng = random.Random(36)

f = lambda v: f"{v:.1f}"


def hexcol(h, l, s=1.0):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return f"#{round(r*255):02x}{round(g*255):02x}{round(b*255):02x}"


# ---- the tree ------------------------------------------------------------------
# A node is (x, y, hue, lightness, radius); a ribbon joins a child to its parent.
N = 36
Y0, Y1, Y2, Y3 = H + 30, 720, 470, 250
x_left, x_right = 70, W - 70
leaves = []
for i in range(N):
    x = x_left + (x_right - x_left) * i / (N - 1)
    hue = 305 + i * 10  # 36 hues round the wheel, magenta to magenta
    leaves.append({"x": x, "y": Y0, "hue": hue, "l": 0.58})


def parent_of(children, y, l, r):
    x = sum(c["x"] for c in children) / len(children)
    # mean hue of a run of neighbours on the wheel
    hue = sum(c["hue"] for c in children) / len(children)
    return {"x": x, "y": y, "hue": hue, "l": l, "r": r, "children": children}


tier1 = [parent_of(leaves[6 * j : 6 * j + 6], Y1, 0.64, 17) for j in range(6)]
tier2 = [parent_of(tier1[2 * j : 2 * j + 2], Y2, 0.72, 24) for j in range(3)]
crown = parent_of(tier2, Y3, 1.0, 32)

# ---- letters for the rain ---------------------------------------------------------
roots = json.load(open(LEXICON, encoding="utf-8"))["roots"].values()
letters = [
    ch
    for r in roots
    for ch in r["orthography"]
    if ch not in "⟨⟩ʲ" and not unicodedata.combining(ch)
]
words = "".join(letters)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


out = []
o = out.append
gid = 0

o(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
  'aria-label="Flag of Vulgultra: thirty-six coloured ribbons of light rise and merge through ten spheres into one white beam">')
o("<title>Flag of Vulgultra</title>")
o("<defs>")
o('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0" stop-color="#010006"/><stop offset=".45" stop-color="#0a0420"/>'
  '<stop offset=".8" stop-color="#160934"/><stop offset="1" stop-color="#1d0b3d"/></linearGradient>')
o(f'<radialGradient id="aura" cx="{crown["x"]}" cy="{Y3}" r="560" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#ffffff" stop-opacity=".16"/>'
  '<stop offset=".35" stop-color="#9d7bff" stop-opacity=".08"/>'
  '<stop offset="1" stop-color="#4b1f73" stop-opacity="0"/></radialGradient>')
o('<linearGradient id="rain" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0" stop-color="#46e8c8" stop-opacity="0"/>'
  '<stop offset=".85" stop-color="#46e8c8" stop-opacity=".75"/>'
  '<stop offset="1" stop-color="#eafff9"/></linearGradient>')
o(f'<linearGradient id="beam" x1="0" y1="{Y3}" x2="0" y2="0" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ffffff" stop-opacity=".85"/></linearGradient>')
o('<radialGradient id="glass" cx=".35" cy=".3" r=".75">'
  '<stop offset="0" stop-color="#ffffff" stop-opacity=".95"/>'
  '<stop offset=".35" stop-color="#ffffff" stop-opacity=".25"/>'
  '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>')
o('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
  '<feGaussianBlur stdDeviation="4" result="b"/>'
  '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
o('<filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>')
o('<filter id="haze" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>')
o('<pattern id="scan" width="5" height="5" patternUnits="userSpaceOnUse">'
  '<rect width="5" height="1.6" fill="#000" fill-opacity=".22"/></pattern>')
o('<pattern id="dots" width="30" height="30" patternUnits="userSpaceOnUse">'
  '<circle cx="15" cy="15" r="1.1" fill="#b7a6ff" fill-opacity=".16"/></pattern>')
o(f'<radialGradient id="vignette" cx="750" cy="430" r="950" gradientUnits="userSpaceOnUse">'
  '<stop offset=".55" stop-color="#000" stop-opacity="0"/>'
  '<stop offset="1" stop-color="#000" stop-opacity=".65"/></radialGradient>')


def ribbon_gradient(child, parent):
    """Colour runs from the child's hue into the parent's mix."""
    global gid
    gid += 1
    c0 = hexcol(child["hue"], child["l"])
    c1 = "#ffffff" if parent is crown else hexcol(parent["hue"], parent["l"])
    o(f'<linearGradient id="g{gid}" x1="0" y1="{f(child["y"])}" x2="0" y2="{f(parent["y"])}" gradientUnits="userSpaceOnUse">'
      f'<stop offset=".25" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>')
    return f"url(#g{gid})"


edges = []
for node, w_in, w_out in ((tier1, 9, 7), (tier2, 26, 15), ([crown], 30, 22)):
    for p in node:
        n = len(p["children"])
        for k, c in enumerate(p["children"]):
            # children land side by side across the sphere they feed
            land = p["x"] + (k - (n - 1) / 2) * w_out * 0.9
            edges.append((c, p, land, w_in, w_out, ribbon_gradient(c, p)))
o("</defs>")


def ribbon(c, p, land, w0, w1):
    x0, y0, x1, y1 = c["x"], c["y"], land, p["y"]
    k = (y0 - y1) * 0.6
    l0, r0, l1, r1 = x0 - w0 / 2, x0 + w0 / 2, x1 - w1 / 2, x1 + w1 / 2
    return (f"M{f(l0)},{f(y0)} C{f(l0)},{f(y0 - k)} {f(l1)},{f(y1 + k)} {f(l1)},{f(y1)} "
            f"L{f(r1)},{f(y1)} C{f(r1)},{f(y1 + k)} {f(r0)},{f(y0 - k)} {f(r0)},{f(y0)}Z")


def spine(c, p, land):
    x0, y0, x1, y1 = c["x"], c["y"], land, p["y"]
    k = (y0 - y1) * 0.6
    return f"M{f(x0)},{f(y0)} C{f(x0)},{f(y0 - k)} {f(x1)},{f(y1 + k)} {f(x1)},{f(y1)}"


# ---- ground -------------------------------------------------------------------------
o(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
o(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
o(f'<rect width="{W}" height="{H}" fill="url(#aura)"/>')
# the colours glow up from below the edge
o('<g filter="url(#haze)" opacity=".7">')
for c in leaves:
    o(f'<ellipse cx="{f(c["x"])}" cy="{H + 10}" rx="34" ry="120" fill="{hexcol(c["hue"], 0.5)}"/>')
o("</g>")

# ---- rain, falling the way Latin went -----------------------------------------------
STEP, FS, LH = 30, 19, 23
o('<g font-family="Menlo, \'SF Mono\', Consolas, \'DejaVu Sans Mono\', monospace" '
  f'font-size="{FS}" text-anchor="middle">')
for cx in range(15, W, STEP):
    for _ in range(rng.choice([1, 1, 2])):
        n = rng.randint(5, 18)
        y0 = rng.randint(-150, H - 120)
        i = rng.randrange(len(words) - n)
        s = words[i : i + n]
        op = rng.uniform(0.18, 0.5)
        spans = "".join(f'<tspan x="{cx}" y="{y0 + j * LH}">{esc(ch)}</tspan>' for j, ch in enumerate(s))
        o(f'<text fill="url(#rain)" opacity="{op:.2f}">{spans}</text>')
o("</g>")

# ---- the three veils ------------------------------------------------------------------
cx, cy = crown["x"], crown["y"]
for r, op in ((168, 0.05), (120, 0.07), (80, 0.1)):
    o(f'<circle cx="{f(cx)}" cy="{cy}" r="{r}" fill="#ffffff" fill-opacity="{op}"/>')
o(f'<g fill="none" transform="translate({f(cx)} {cy})">')
o('<circle r="168" stroke="#ffffff" stroke-opacity=".25" stroke-width="1.2"/>')
o('<circle r="120" stroke="#ffffff" stroke-opacity=".5" stroke-width="5" stroke-dasharray="1.4 7.6"/>')
o('<circle r="80" stroke="#ffffff" stroke-opacity=".35" stroke-width="1.2"/>')
for i in range(22):  # the 22 paths
    a = math.radians(-90 + i * 360 / 22)
    o(f'<line x1="{f(160*math.cos(a))}" y1="{f(160*math.sin(a))}" x2="{f(178*math.cos(a))}" y2="{f(178*math.sin(a))}" '
      'stroke="#ffffff" stroke-opacity=".5" stroke-width="2"/>')
o("</g>")

# ---- the beam -------------------------------------------------------------------------------
o(f'<rect x="{f(cx - 60)}" y="-40" width="120" height="{cy + 40}" fill="#ffffff" opacity=".35" filter="url(#bloom)"/>')
o(f'<rect x="{f(cx - 11)}" y="-10" width="22" height="{cy + 10}" fill="url(#beam)" filter="url(#glow)"/>')
# chromatic fringe
o(f'<rect x="{f(cx - 15)}" y="-10" width="2" height="{cy + 10}" fill="#00f0ff" opacity=".8"/>')
o(f'<rect x="{f(cx + 13)}" y="-10" width="2" height="{cy + 10}" fill="#ff2bd6" opacity=".8"/>')

# ---- ribbons ----------------------------------------------------------------------------------
o('<g filter="url(#bloom)" opacity=".75">')
for c, p, land, w0, w1, fill in edges:
    o(f'<path d="{ribbon(c, p, land, w0 * 1.6, w1 * 1.6)}" fill="{fill}"/>')
o("</g>")
o('<g filter="url(#glow)">')
for c, p, land, w0, w1, fill in edges:
    o(f'<path d="{ribbon(c, p, land, w0, w1)}" fill="{fill}"/>')
o("</g>")
# pulses of data climbing each ribbon
o('<g fill="none" stroke="#ffffff" stroke-linecap="round">')
for c, p, land, w0, w1, fill in edges:
    dash = rng.choice(["2 18", "6 26", "2 9 2 30", "10 40"])
    o(f'<path d="{spine(c, p, land)}" stroke-width="{2 if w0 < 20 else 3}" stroke-opacity=".6" '
      f'stroke-dasharray="{dash}" stroke-dashoffset="{rng.randint(0, 40)}"/>')
o("</g>")

# ---- the ten spheres ----------------------------------------------------------------------------
for p in tier1 + tier2 + [crown]:
    col = "#ffffff" if p is crown else hexcol(p["hue"], p["l"])
    r = p["r"]
    o(f'<circle cx="{f(p["x"])}" cy="{f(p["y"])}" r="{r * 2.2}" fill="{col}" opacity=".45" filter="url(#bloom)"/>')
    o(f'<circle cx="{f(p["x"])}" cy="{f(p["y"])}" r="{r}" fill="{col}"/>')
    o(f'<circle cx="{f(p["x"])}" cy="{f(p["y"])}" r="{r}" fill="url(#glass)"/>')
    o(f'<circle cx="{f(p["x"])}" cy="{f(p["y"])}" r="{r}" fill="none" stroke="#ffffff" stroke-opacity=".9" stroke-width="2"/>')
    o(f'<circle cx="{f(p["x"])}" cy="{f(p["y"])}" r="{r + 9}" fill="none" stroke="{col}" stroke-opacity=".7" '
      f'stroke-width="1.5" stroke-dasharray="{f(r * 0.5)} {f(r * 0.4)}"/>')

# ---- screen ---------------------------------------------------------------------------------------
o(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
o(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
o("</svg>")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(OUT, OUT.stat().st_size, "bytes")

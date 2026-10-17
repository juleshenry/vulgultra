"""Generate the Vulgultra flag, site/static/img/flag.svg: a reverse prism.

36 rays, one per lect of the Romance grid, converge on a prism and leave it
as one beam. Behind it, three rings (the veils above the Tree of Life) and a
rain of letters taken from the lexicon's spellings. The 22 ticks and 10 dots
on the rings are the paths and spheres of the Tree of Life.

    python3 scripts/make_flag.py
"""

import colorsys
import json
import math
import random
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data" / "vulgultra_lexicon.json"
OUT = ROOT / "site" / "static" / "img" / "flag.svg"
W, H = 1500, 1000
rng = random.Random(36)

# ---- letters for the rain -------------------------------------------------
roots = json.load(open(LEXICON, encoding="utf-8"))["roots"].values()
letters = []
for r in roots:
    for ch in r["orthography"]:
        if ch in "⟨⟩" or unicodedata.combining(ch) or ch == "ʲ":
            continue
        letters.append(ch)
words = "".join(letters)


def rain_run(n):
    i = rng.randrange(len(words) - n)
    return words[i : i + n]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


# ---- geometry ----------------------------------------------------------------
C = (750.0, 500.0)  # prism centroid
side = 400.0
h = side * math.sqrt(3) / 2
A = (C[0], C[1] - 2 * h / 3)
BL = (C[0] - side / 2, C[1] + h / 3)
BR = (C[0] + side / 2, C[1] + h / 3)


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


E = lerp(BL, A, 0.5)  # rays enter the left face here
X = lerp(BR, A, 0.56)  # the beam leaves the right face here
beam_end = (W + 20, X[1] - (W + 20 - X[0]) * math.tan(math.radians(5.5)))

f = lambda v: f"{v:.1f}"
pt = lambda p: f"{f(p[0])},{f(p[1])}"

out = []
o = out.append

o(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Flag of Vulgultra: thirty-six coloured rays converge through a prism into one beam of light">')
o("<title>Flag of Vulgultra</title>")
o("<defs>")
o('<radialGradient id="bg" cx="750" cy="480" r="900" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#2a0f4d"/><stop offset=".45" stop-color="#12062a"/>'
  '<stop offset="1" stop-color="#030108"/></radialGradient>')
o('<radialGradient id="veil" cx="750" cy="500" r="380" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#c9a6ff" stop-opacity=".22"/>'
  '<stop offset=".6" stop-color="#7b3fc4" stop-opacity=".10"/>'
  '<stop offset="1" stop-color="#4b1f73" stop-opacity="0"/></radialGradient>')
o('<linearGradient id="rain" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0" stop-color="#3dffb4" stop-opacity="0"/>'
  '<stop offset=".85" stop-color="#3dffb4" stop-opacity=".8"/>'
  '<stop offset="1" stop-color="#e9fff6" stop-opacity="1"/></linearGradient>')
o('<linearGradient id="rainGold" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0" stop-color="#f2c230" stop-opacity="0"/>'
  '<stop offset=".8" stop-color="#f2c230" stop-opacity=".85"/>'
  '<stop offset="1" stop-color="#fff7d6" stop-opacity="1"/></linearGradient>')
o('<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">'
  '<stop offset="0" stop-color="#ffffff" stop-opacity=".16"/>'
  '<stop offset=".55" stop-color="#b9e6ff" stop-opacity=".05"/>'
  '<stop offset="1" stop-color="#ffffff" stop-opacity=".12"/></linearGradient>')
o(f'<linearGradient id="beamFade" x1="{f(X[0])}" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fffdf0"/><stop offset=".55" stop-color="#ffe9a3"/>'
  '<stop offset="1" stop-color="#f2c230"/></linearGradient>')
# rays arrive as packets of data and become light near the prism
o('<linearGradient id="solidRamp" x1="0" y1="0" x2="1500" y2="0" gradientUnits="userSpaceOnUse">'
  '<stop offset=".12" stop-color="#000"/><stop offset=".3" stop-color="#fff"/></linearGradient>')
o('<linearGradient id="dashRamp" x1="0" y1="0" x2="1500" y2="0" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".14" stop-color="#fff"/>'
  '<stop offset=".3" stop-color="#000"/></linearGradient>')
o(f'<mask id="solidMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#solidRamp)"/></mask>')
o(f'<mask id="dashMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#dashRamp)"/></mask>')
# the rain turns gold inside the beam
o(f'<mask id="beamMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
  f'<polygon points="{pt((X[0], X[1] - 6))} {pt((W + 20, beam_end[1] - 90))} {pt((W + 20, beam_end[1] + 90))} {pt((X[0], X[1] + 6))}" fill="#fff" filter="url(#soft)"/></mask>')
o('<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>')
o('<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
  '<feGaussianBlur stdDeviation="5" result="b"/>'
  '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
o('<filter id="bloom" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="24"/></filter>')
o('<pattern id="scan" width="6" height="6" patternUnits="userSpaceOnUse">'
  '<rect width="6" height="2" fill="#000" fill-opacity=".18"/></pattern>')
o('<radialGradient id="vignette" cx="750" cy="500" r="920" gradientUnits="userSpaceOnUse">'
  '<stop offset=".55" stop-color="#000" stop-opacity="0"/>'
  '<stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>')
o("</defs>")

o(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

# ---- rain --------------------------------------------------------------------
STEP, FS, LH = 30, 21, 25
cols = []
for cx in range(15, W, STEP):
    for _ in range(rng.choice([1, 1, 2])):
        n = rng.randint(6, 22)
        y0 = rng.randint(-200, H - 80)
        op = rng.uniform(0.25, 0.7)
        cols.append((cx, y0, rain_run(n), op))


def rain_text(fill, xmin=0):
    o(f'<g font-family="Menlo, \'SF Mono\', Consolas, \'DejaVu Sans Mono\', monospace" font-size="{FS}" text-anchor="middle">')
    for cx, y0, s, op in cols:
        if cx < xmin:
            continue
        spans = "".join(f'<tspan x="{cx}" y="{y0 + i * LH}">{esc(c)}</tspan>' for i, c in enumerate(s))
        o(f'<text fill="url(#{fill})" opacity="{op:.2f}">{spans}</text>')
    o("</g>")


rain_text("rain")
o('<g mask="url(#beamMask)">')
rain_text("rainGold", X[0] - 40)
o("</g>")

# ---- the three veils ------------------------------------------------------------
o(f'<circle cx="{C[0]}" cy="{C[1]}" r="380" fill="url(#veil)"/>')
o(f'<g fill="none" transform="translate({C[0]} {C[1]})">')
o('<circle r="232" stroke="#f2c230" stroke-opacity=".45" stroke-width="1.6"/>')
o('<circle r="300" stroke="#5ef2ff" stroke-opacity=".45" stroke-width="7" stroke-dasharray="1.5 9"/>')
o('<circle r="372" stroke="#ffffff" stroke-opacity=".22" stroke-width="1.2"/>')
# 22 ticks for the 22 paths, 10 marks for the 10 spheres
for i in range(22):
    a = math.radians(-90 + i * 360 / 22)
    r1, r2 = 362, 384
    o(f'<line x1="{f(r1*math.cos(a))}" y1="{f(r1*math.sin(a))}" x2="{f(r2*math.cos(a))}" y2="{f(r2*math.sin(a))}" stroke="#ffffff" stroke-opacity=".45" stroke-width="2"/>')
for i in range(10):
    a = math.radians(-90 + i * 36)
    o(f'<circle cx="{f(232*math.cos(a))}" cy="{f(232*math.sin(a))}" r="4.5" fill="#f2c230" fill-opacity=".8"/>')
o("</g>")

# ---- 36 rays --------------------------------------------------------------------------
N = 36
y_top, y_bot = 150, 850
rays = []
for i in range(N):
    t = i / (N - 1)
    y = y_top + (y_bot - y_top) * t
    r, g, b = colorsys.hls_to_rgb(t * 0.80, 0.60, 1.0)
    col = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    rays.append(((-20.0, y), col))


def ray_poly(p0, w0, w1):
    dx, dy = E[0] - p0[0], E[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    pts = [
        (p0[0] + nx * w0, p0[1] + ny * w0),
        (E[0] + nx * w1, E[1] + ny * w1),
        (E[0] - nx * w1, E[1] - ny * w1),
        (p0[0] - nx * w0, p0[1] - ny * w0),
    ]
    return " ".join(pt(p) for p in pts)


# bloom under the fan
o('<g filter="url(#bloom)" opacity=".55" style="mix-blend-mode:screen">')
for p0, col in rays:
    o(f'<polygon points="{ray_poly(p0, 9, 2)}" fill="{col}"/>')
o("</g>")
# solid light near the prism
o('<g mask="url(#solidMask)" style="isolation:isolate">')
o('<g filter="url(#glow)" style="mix-blend-mode:screen">')
for p0, col in rays:
    o(f'<polygon points="{ray_poly(p0, 3.6, 0.7)}" fill="{col}" style="mix-blend-mode:screen"/>')
o("</g></g>")
# packets of data near the hoist
o('<g mask="url(#dashMask)" stroke-width="5" stroke-linecap="butt" fill="none">')
for i, (p0, col) in enumerate(rays):
    dash = rng.choice(["16 10", "8 8", "22 6 4 6", "4 6", "12 4"])
    off = rng.randint(0, 30)
    o(f'<line x1="{f(p0[0])}" y1="{f(p0[1])}" x2="{f(E[0])}" y2="{f(E[1])}" stroke="{col}" stroke-dasharray="{dash}" stroke-dashoffset="{off}"/>')
o("</g>")

# ---- the beam -------------------------------------------------------------------------------
def beam_poly(w0, w1):
    return f"{pt((X[0], X[1] - w0))} {pt((beam_end[0], beam_end[1] - w1))} {pt((beam_end[0], beam_end[1] + w1))} {pt((X[0], X[1] + w0))}"


o(f'<polygon points="{beam_poly(14, 70)}" fill="#f2c230" opacity=".55" filter="url(#bloom)"/>')
o(f'<polygon points="{beam_poly(9, 26)}" fill="#f2c230" opacity=".55" filter="url(#glow)"/>')
o(f'<polygon points="{beam_poly(4.5, 9)}" fill="url(#beamFade)" filter="url(#glow)"/>')

# ---- the prism ------------------------------------------------------------------------------
tri = f"{pt(A)} {pt(BR)} {pt(BL)}"
o(f'<polygon points="{tri}" fill="#05020c" fill-opacity=".8"/>')
o(f'<polygon points="{tri}" fill="url(#glass)"/>')
# the colours sum to white inside the glass
o(f'<polygon points="{pt((E[0], E[1] - 2.5))} {pt((X[0], X[1] - 4.5))} {pt((X[0], X[1] + 4.5))} {pt((E[0], E[1] + 2.5))}" fill="#ffffff" filter="url(#glow)"/>')
o(f'<circle cx="{f(E[0])}" cy="{f(E[1])}" r="9" fill="#ffffff" filter="url(#glow)"/>')
o(f'<circle cx="{f(X[0])}" cy="{f(X[1])}" r="8" fill="#fff7d6" filter="url(#glow)"/>')
# chromatic aberration on the edges
o('<g fill="none" stroke-width="3" stroke-linejoin="round" style="mix-blend-mode:screen">')
o(f'<polygon points="{tri}" stroke="#00f0ff" stroke-opacity=".8" transform="translate(-5 1)"/>')
o(f'<polygon points="{tri}" stroke="#ff2bd6" stroke-opacity=".8" transform="translate(5 -1)"/>')
o("</g>")
o(f'<polygon points="{tri}" fill="none" stroke="#f4fbff" stroke-width="3.5" stroke-linejoin="round" filter="url(#glow)"/>')

# ---- screen ---------------------------------------------------------------------------------
o(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
o(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
o("</svg>")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(OUT.relative_to(ROOT))

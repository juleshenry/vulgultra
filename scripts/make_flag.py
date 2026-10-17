"""Generate the Vulgultra flag, site/static/img/flag.svg: a reverse prism.

A prism splits white light into colours; this runs it backwards with additive
light. The 36 lects of the Romance grid rise from the bottom edge as 36 hues
round the colour wheel. They merge six by six into the six tertiary colours,
two by two into the three pillars (red, green, blue), and the three into
white at the crown, which leaves the flag as one beam. The ten meeting points
are the ten spheres of the Tree of Life; the crown sits in the three veils.

    python3 scripts/make_flag.py
"""

import colorsys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "static" / "img" / "flag.svg"
W, H = 1500, 1000

FIELD = "#1b0b3f"
VEILS = ("#2a1258", "#3b1b75", "#522a96")
INK = "#0e0424"  # outlines
WHITE = "#ffffff"

f = lambda v: f"{v:.1f}"


def hexcol(h, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, 1.0)
    return f"#{round(r*255):02x}{round(g*255):02x}{round(b*255):02x}"


# ---- the tree --------------------------------------------------------------------
N = 36
Y0, Y1, Y2, Y3 = H + 10, 700, 455, 245
leaves = []
for i in range(N):
    x = 72 + (W - 144) * i / (N - 1)
    leaves.append({"x": x, "y": Y0, "hue": 305 + i * 10, "l": 0.55})


def parent_of(children, y, l, r):
    return {
        "x": sum(c["x"] for c in children) / len(children),
        "y": y,
        # mean hue of a run of neighbours on the wheel
        "hue": sum(c["hue"] for c in children) / len(children),
        "l": l,
        "r": r,
        "children": children,
    }


tier1 = [parent_of(leaves[6 * j : 6 * j + 6], Y1, 0.58, 22) for j in range(6)]
tier2 = [parent_of(tier1[2 * j : 2 * j + 2], Y2, 0.6, 31) for j in range(3)]
crown = parent_of(tier2, Y3, 1.0, 44)


def colour(node):
    return WHITE if node is crown else hexcol(node["hue"], node["l"])


def ribbon(c, p, land, w0, w1, steps=32):
    """A band that leaves the child upright and lands upright on the parent,
    tapering from w0 to w1 measured across the band."""
    x0, y0, x1, y1 = c["x"], c["y"], land, p["y"]
    k = (y0 - y1) * 0.6
    P = ((x0, y0), (x0, y0 - k), (x1, y1 + k), (x1, y1))
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        bx = [u**3, 3 * u * u * t, 3 * u * t * t, t**3]
        dx = [-3 * u * u, 3 * u * u - 6 * u * t, 6 * u * t - 3 * t * t, 3 * t * t]
        x = sum(b * q[0] for b, q in zip(bx, P))
        y = sum(b * q[1] for b, q in zip(bx, P))
        tx = sum(d * q[0] for d, q in zip(dx, P))
        ty = sum(d * q[1] for d, q in zip(dx, P))
        n = math.hypot(tx, ty)
        half = (w0 + (w1 - w0) * t) / 2
        nx, ny = -ty / n * half, tx / n * half
        left.append(f"{f(x + nx)},{f(y + ny)}")
        right.append(f"{f(x - nx)},{f(y - ny)}")
    return "M" + " L".join(left + right[::-1]) + "Z"


# (parents, width leaving the child, width landing, spacing of landings)
TIERS = ((tier1, 24, 9, 6), (tier2, 34, 16, 14), ([crown], 44, 20, 26))

out = []
o = out.append
o(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
  'aria-label="Flag of Vulgultra: thirty-six coloured bands rise and merge through ten spheres into one white beam">')
o("<title>Flag of Vulgultra</title>")
o(f'<rect width="{W}" height="{H}" fill="{FIELD}"/>')

# the three veils round the crown
for r, col in zip((235, 172, 112), VEILS):
    o(f'<circle cx="{f(crown["x"])}" cy="{Y3}" r="{r}" fill="{col}"/>')

# the beam
o(f'<rect x="{f(crown["x"] - 25)}" y="-10" width="50" height="{Y3 + 10}" fill="{WHITE}" stroke="{INK}" stroke-width="6"/>')

# bands, lowest tier first so each tier lies over the one it came from
o(f'<g stroke="{INK}" stroke-width="5" stroke-linejoin="round">')
for parents, w0, w1, gap in TIERS:
    for p in parents:
        n = len(p["children"])
        for k, c in enumerate(p["children"]):
            land = p["x"] + (k - (n - 1) / 2) * gap
            o(f'<path d="{ribbon(c, p, land, w0, w1)}" fill="{colour(c)}"/>')
o("</g>")

# the ten spheres
for p in tier1 + tier2 + [crown]:
    x, y, r = f(p["x"]), f(p["y"]), p["r"]
    o(f'<circle cx="{x}" cy="{y}" r="{r + 11}" fill="{INK}"/>')
    o(f'<circle cx="{x}" cy="{y}" r="{r + 7}" fill="{WHITE}"/>')
    if p is not crown:
        o(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{colour(p)}"/>')

o("</svg>")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(OUT.relative_to(ROOT), OUT.stat().st_size, "bytes")

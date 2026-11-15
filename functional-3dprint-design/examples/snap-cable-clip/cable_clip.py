"""Snap-in cable clip (worked example - a small functional part, not an enclosure).

A flat base (stick it down with VHB tape or a screw) with a C-shaped ring. The cable
pushes through a narrow entry, the arms flex apart and spring back around it.

Print orientation: the profile lies flat on the bed and is extruded upward, so the arms
flex ALONG the layer lines (strong) instead of peeling them apart (weak).

Run:  python cable_clip.py      -> out/cable_clip.3mf, out/fit_cable_clip.3mf
Needs: pip install cadquery
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT))

from helpers.export_3mf import export_part  # noqa: E402
from helpers.fit_test import slice_test  # noqa: E402
from helpers.validate import assert_min, check_part  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"

MEASUREMENTS = {
    "cable_d": (6.0, "cable outer diameter, LARGEST of three readings", "example"),
    "screw_d": (3.5, "wood screw shank diameter (optional)", "example"),
}
M = {k: v[0] for k, v in MEASUREMENTS.items()}

PARAMS = {
    "clearance":   0.25,   # loose fit so the cable can slide
    "arm_t":       1.6,    # ring wall = flexing arm thickness (PLA 1.2-2.0)
    "entry_ratio": 0.75,   # entry gap as a fraction of cable_d (snap strength)
    "width":       10.0,   # clip width along the cable (print height)
    "base_w":      26.0,
    "base_t":      2.4,
    "screw_hole":  True,
}
P = PARAMS

ri = M["cable_d"] / 2 + P["clearance"]
ro = ri + P["arm_t"]
cy = P["base_t"] + ri                     # ring centre height above the bed
gap = M["cable_d"] * P["entry_ratio"]

assert_min(P["arm_t"], 1.2, "clip arm thickness")
assert_min(P["base_t"], 1.6, "base thickness")
assert gap < M["cable_d"], "entry gap must be smaller than the cable or it won't snap"


def box(x0, x1, y0, y1, z0, z1) -> cq.Shape:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=cq.Vector(x0, y0, z0))


def make_clip() -> cq.Shape:
    w = P["width"]
    base = box(-P["base_w"] / 2, P["base_w"] / 2, 0, P["base_t"], 0, w)
    ring = cq.Workplane("XY").circle(ro).circle(ri).extrude(w).val().translate(cq.Vector(0, cy, 0))
    bore = cq.Solid.makeCylinder(ri, w + 2, pnt=cq.Vector(0, cy, -1))
    clip = base.fuse(ring).cut(bore)

    # Entry gap at the top, with a funnel lead-in so the cable pushes the arms apart.
    clip = clip.cut(box(-gap / 2, gap / 2, cy, cy + ro + 1, -1, w + 1))
    funnel = (cq.Workplane("XY")
              .polyline([(0, cy + ri * 0.4), (-(gap / 2 + 1.4), cy + ro + 0.6),
                         (gap / 2 + 1.4, cy + ro + 0.6)])
              .close().extrude(w + 2).val().translate(cq.Vector(0, 0, -1)))
    clip = clip.cut(funnel)

    if P["screw_hole"]:
        # Holes go through the base (along Y), outside the ring footprint.
        x = (P["base_w"] / 2 + ro) / 2
        for sx in (-1, 1):
            clip = clip.cut(cq.Solid.makeCylinder(M["screw_d"] / 2 + 0.2, P["base_t"] + 2,
                                                  pnt=cq.Vector(sx * x, -1, w / 2),
                                                  dir=cq.Vector(0, 1, 0)))
    return clip.clean()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    clip = make_clip()
    print(check_part(clip, "cable_clip"))
    export_part(clip, str(OUT / "cable_clip"))
    # Fit test: a 4 mm-thick slice of the real clip - prints in a few minutes.
    fit = slice_test(clip, (-50, -50, 0), (50, 50, 4))
    export_part(fit, str(OUT / "fit_cable_clip"))
    print(f"Wrote files to {OUT}")


if __name__ == "__main__":
    main()

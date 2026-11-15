"""Fit-test generators (CadQuery).

Two kinds of test piece:

* slice_test   - cut a small region out of the real part, so the interface prints at full
                 scale in a few minutes with the exact geometry of the final model.
* clearance_gauge - a plate with holes and slots at increasing clearances plus a matching
                 key (peg + tab). Shows which clearance the user's printer actually needs.

Print fit tests with the SAME slicer profile as the final part.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import cadquery as cq


def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=cq.Vector(x0, y0, z0))


def slice_test(part: cq.Shape, lo: Tuple[float, float, float],
               hi: Tuple[float, float, float]) -> cq.Shape:
    """Return the portion of `part` inside the axis-aligned box lo..hi (mm).

    Keep the box just big enough to include the interface plus 2-3 mm of surrounding
    wall, so the piece is stiff enough to judge the fit but prints in minutes.
    """
    region = _box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    out = part.intersect(region)
    if out.Volume() <= 0:
        raise ValueError("slice_test box does not overlap the part")
    return out


def clearance_gauge(nominal_d: float = 5.0, tab_t: float = 2.0,
                    clearances: Sequence[float] = (0.10, 0.15, 0.20, 0.25, 0.30),
                    plate_t: float = 4.0, pitch: float = 11.0) -> Tuple[cq.Shape, cq.Shape]:
    """Return (gauge_plate, key).

    gauge_plate: one row of round holes (nominal_d + 2c) and one row of slots
                 (tab_t + 2c), tightest on the LEFT. A notch on the left edge marks the
                 tight end so the user can read it after printing.
    key:         a peg of exactly nominal_d and a tab of exactly tab_t on a handle.

    The user tries the key in each hole/slot and reports the first that gives the
    fit they want (press / snug / sliding / loose). Put that clearance into PARAMS.
    """
    n = len(clearances)
    w = pitch * n + 6
    h = 30.0
    plate = _box(0, w, 0, h, 0, plate_t)
    for i, c in enumerate(clearances):
        x = 3 + pitch * (i + 0.5)
        hole = cq.Solid.makeCylinder((nominal_d + 2 * c) / 2, plate_t + 2,
                                     pnt=cq.Vector(x, 21, -1))
        slot_w = tab_t + 2 * c
        slot = _box(x - slot_w / 2, x + slot_w / 2, 4, 12, -1, plate_t + 1)
        plate = plate.cut(hole).cut(slot)
    # Tight-end marker: a square notch on the left edge
    notch = _box(-1, 1.5, h / 2 - 1.5, h / 2 + 1.5, -1, plate_t + 1)
    plate = plate.cut(notch)

    handle = _box(0, 30, 0, 12, 0, 3)
    peg = cq.Solid.makeCylinder(nominal_d / 2, 10, pnt=cq.Vector(7, 6, 3))
    tab = _box(18, 18 + tab_t, 2, 10, 3, 13)
    key = handle.fuse(peg).fuse(tab).clean()
    return plate, key

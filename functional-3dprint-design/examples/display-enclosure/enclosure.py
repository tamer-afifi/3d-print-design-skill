"""Display + Raspberry Pi desk enclosure (worked example).

Based on the PitVista desk display: a touchscreen with a Raspberry Pi mounted on its back,
all Pi ports hidden inside, and a single panel-mount USB-C extension for power held in
place without screws (pegs + slide-in retainer).

Parts
-----
    shell      - front frame + walls. Screen drops in from the back and is held by clip posts.
    back_cover - closes the back; screws into heat-set inserts in four corner bosses.
    retainer   - slides down into grooves and traps the USB-C flange on its pegs.

Fit tests
---------
    fit_usbc   - slice of the bottom wall around the USB-C pocket (+ print a retainer).
    fit_clip   - slice of one side wall with a clip post and a bit of the front lip.
    gauge, key - clearance gauge (helpers/fit_test.py).

Every number below is an EXAMPLE. Replace MEASUREMENTS with your own caliper readings
before printing (see references/measurement.md).

Run:  python enclosure.py            -> writes out/*.3mf, out/*.stl
Needs: pip install cadquery
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT))

from helpers.export_3mf import export_part, export_plate  # noqa: E402
from helpers.fit_test import clearance_gauge, slice_test  # noqa: E402
from helpers.validate import assert_min, check_part  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"

# ============================================================================ MEASUREMENTS
# name: (value_mm, definition, source). EXAMPLE VALUES - replace with your own.
MEASUREMENTS = {
    # Screen module
    "screen_w":        (194.0, "screen module outer width, glass edge to glass edge", "example"),
    "screen_h":        (110.8, "screen module outer height", "example"),
    "screen_t":        (5.6,   "thickness at THICKEST point incl. FPC bulge (not datasheet)", "example"),
    "active_w":        (155.0, "visible/active area width", "example"),
    "active_h":        (87.0,  "visible/active area height", "example"),
    "active_off_x":    (0.0,   "active-area centre minus module centre, +x = right", "example"),
    "active_off_y":    (0.0,   "active-area centre minus module centre, +y = up", "example"),
    "stack_depth":     (24.0,  "back of screen glass to furthest point of Pi + cables", "example"),
    # Panel-mount USB-C extension (socket end)
    "usbc_body_w":     (9.2,   "socket body width (the part that goes through the wall)", "example"),
    "usbc_body_h":     (3.4,   "socket body height", "example"),
    "usbc_flange_w":   (28.0,  "flange width, ear tip to ear tip", "example"),
    "usbc_flange_h":   (9.0,   "flange height", "example"),
    "usbc_flange_t":   (2.5,   "flange thickness", "example"),
    "usbc_ear_span_outer": (25.0, "ear holes: OUTER edge to outer edge", "example"),
    "usbc_ear_hole_d": (3.0,   "ear hole diameter", "example"),
    "usbc_cable_d":    (4.5,   "cable diameter behind the flange", "example"),
    # Fasteners
    "insert_hole_d":   (4.0,   "heat-set insert (M3) recommended hole diameter", "insert datasheet"),
    "insert_len":      (5.7,   "heat-set insert length", "insert datasheet"),
    "screw_clear_d":   (3.4,   "M3 clearance hole", "standard"),
}
M = {k: v[0] for k, v in MEASUREMENTS.items()}

# ================================================================================= PARAMS
PARAMS = {
    "wall":         3.0,    # side walls (cosmetic, sanded): >= 2.4
    "lip_t":        2.0,    # front frame thickness
    "r_outer":      6.0,    # outer vertical corner radius
    "c_screen":     0.30,   # screen clearance per side (drop-in)
    "c_slide":      0.20,   # sliding fit (retainer in grooves)
    "c_flange":     0.25,   # USB-C flange in its pocket
    "c_peg":        0.15,   # peg in ear hole (radial)
    "c_back":       2.0,    # air gap behind the Pi stack
    # clip posts
    "post_t":       1.4,    # flexing thickness
    "post_w":       10.0,   # width along the wall
    "post_gap":     0.5,    # relief gap behind/around the post so it can flex
    "hook_d":       1.0,    # how far the hook reaches over the screen
    "hook_flat":    0.6,    # vertical flat on the hook face
    "posts_y":      (-30.0, 30.0),  # post positions along each side wall
    # USB-C placement (centre of socket)
    "usbc_x":       40.0,   # along the bottom wall, from centre (+ = right)
    "usbc_z_above_screen": 9.0,  # socket centre height above the back of the screen
    "rail_w":       3.2,    # retainer rail width
    "groove_d":     1.2,    # groove depth into each rail
    "retainer_t":   1.6,    # retainer plate thickness
    "rail_floor":   1.2,    # solid stop under the groove
    # corner bosses
    "boss_r":       4.5,
    "cover_t":      2.4,
    "bed":          (256, 256, 256),  # printer build volume
}
P = PARAMS

# ============================================================================== DERIVED
cav_w = M["screen_w"] + 2 * P["c_screen"]
cav_h = M["screen_h"] + 2 * P["c_screen"]
OW = cav_w + 2 * P["wall"]
OH = cav_h + 2 * P["wall"]
z_screen_back = P["lip_t"] + M["screen_t"] + P["c_screen"]     # back face of screen
D = P["lip_t"] + M["screen_t"] + M["stack_depth"] + P["c_back"]  # shell depth
ear_span = M["usbc_ear_span_outer"] - M["usbc_ear_hole_d"]       # centre-to-centre (lesson #1)
usbc_z = z_screen_back + P["usbc_z_above_screen"]
wall_in_y = -cav_h / 2                                           # inner face of bottom wall
rail_x_in = M["usbc_flange_w"] / 2 + P["c_flange"]                # rail inner edge, from usbc_x
z_rail0 = usbc_z - M["usbc_flange_h"] / 2 - P["c_flange"] - P["rail_floor"]
boss_xy = [(sx * (cav_w / 2 - P["boss_r"] * 0.5), sy * (cav_h / 2 - P["boss_r"] * 0.5))
           for sx in (-1, 1) for sy in (-1, 1)]

# Design-rule checks (references/design-rules.md)
assert_min(P["wall"] - P["post_t"] - P["post_gap"], 0.8, "wall left behind clip post")
assert_min(P["lip_t"], 1.2, "front lip")
assert_min(P["retainer_t"], 1.2, "retainer plate")
assert z_rail0 > z_screen_back, "USB-C rails would hit the screen: raise usbc_z_above_screen"
assert abs(P["usbc_x"]) + rail_x_in + P["rail_w"] < cav_w / 2 - 2 * P["boss_r"], \
    "USB-C rails collide with a corner boss: move usbc_x toward the centre"


# ============================================================================== helpers
def box(x0, x1, y0, y1, z0, z1) -> cq.Shape:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=cq.Vector(x0, y0, z0))


def rounded_box(w, h, z0, z1, r) -> cq.Shape:
    """Centred in XY, from z0 to z1, vertical edges filleted."""
    return (cq.Workplane("XY").box(w, h, z1 - z0, centered=(True, True, False))
            .edges("|Z").fillet(r).val().translate(cq.Vector(0, 0, z0)))


def clip_post_right(y_c: float):
    """Return (relief_cut, post) for a clip post on the +x wall centred at y_c."""
    x_in = cav_w / 2
    relief = box(x_in - 0.01, x_in + P["post_t"] + P["post_gap"],
                 y_c - P["post_w"] / 2 - P["post_gap"], y_c + P["post_w"] / 2 + P["post_gap"],
                 P["lip_t"], D + 1)
    z_hook = z_screen_back
    z_top = z_hook + P["hook_flat"] + P["hook_d"] * 1.5      # ~34 deg lead-in
    # Profile in (x, z); built in XY then rotated so local Y becomes world Z.
    pts = [
        (x_in + P["post_t"], P["lip_t"] - 0.01),
        (x_in, P["lip_t"] - 0.01),
        (x_in, z_hook),
        (x_in - P["hook_d"], z_hook),
        (x_in - P["hook_d"], z_hook + P["hook_flat"]),
        (x_in, z_top),
        (x_in + P["post_t"], z_top),
    ]
    post = (cq.Workplane("XY").polyline(pts).close().extrude(P["post_w"]).val()
            .rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)       # (x,y,z)->(x,-z,y)
            .translate(cq.Vector(0, y_c + P["post_w"] / 2, 0)))
    return relief, post


# ================================================================================ parts
def make_shell() -> cq.Shape:
    """Front frame down on the bed (Z = 0 is the visible front face)."""
    shell = rounded_box(OW, OH, 0, D, P["r_outer"])
    cavity = rounded_box(cav_w, cav_h, P["lip_t"], D + 1, 1.0)
    window = box(M["active_off_x"] - M["active_w"] / 2, M["active_off_x"] + M["active_w"] / 2,
                 M["active_off_y"] - M["active_h"] / 2, M["active_off_y"] + M["active_h"] / 2,
                 -1, P["lip_t"] + 1)
    shell = shell.cut(cavity).cut(window)

    # Clip posts on both side walls (lesson #3: sized from the MEASURED screen thickness)
    for y_c in P["posts_y"]:
        relief, post = clip_post_right(y_c)
        shell = shell.cut(relief).fuse(post)
        shell = shell.cut(relief.mirror("YZ")).fuse(post.mirror("YZ"))

    # Corner bosses with heat-set insert holes; 45-degree cone underneath so they print
    # without support and stay clear of the screen.
    z_cone0 = z_screen_back + 0.5
    for x, y in boss_xy:
        cone = cq.Solid.makeCone(0.5, P["boss_r"], P["boss_r"], pnt=cq.Vector(x, y, z_cone0))
        cyl = cq.Solid.makeCylinder(P["boss_r"], D - z_cone0 - P["boss_r"],
                                    pnt=cq.Vector(x, y, z_cone0 + P["boss_r"]))
        hole = cq.Solid.makeCylinder(M["insert_hole_d"] / 2, M["insert_len"] + 1,
                                     pnt=cq.Vector(x, y, D - M["insert_len"] - 1))
        shell = shell.fuse(cone).fuse(cyl).cut(hole)

    shell = add_usbc_mount(shell)
    return shell.clean()


def add_usbc_mount(shell: cq.Shape) -> cq.Shape:
    """Screwless USB-C panel mount on the bottom wall: socket cut-out, two pegs through the
    ear holes, and two grooved rails for the slide-in retainer."""
    ux = P["usbc_x"]
    bw = M["usbc_body_w"] + 2 * P["c_flange"]
    bh = M["usbc_body_h"] + 2 * P["c_flange"]
    socket = (cq.Workplane("XY").box(bw, P["wall"] * 3, bh)
              .edges("|Y").fillet(bh / 2 - 0.01).val()
              .translate(cq.Vector(ux, -OH / 2, usbc_z)))
    shell = shell.cut(socket)

    peg_d = M["usbc_ear_hole_d"] - 2 * P["c_peg"]
    peg_len = M["usbc_flange_t"] - 0.2       # stops short of the retainer
    for sx in (-1, 1):
        peg = cq.Solid.makeCylinder(peg_d / 2, peg_len + 0.5,
                                    pnt=cq.Vector(ux + sx * ear_span / 2, wall_in_y - 0.5, usbc_z),
                                    dir=cq.Vector(0, 1, 0))
        shell = shell.fuse(peg)

    y_groove0 = wall_in_y + M["usbc_flange_t"]
    y_groove1 = y_groove0 + P["retainer_t"] + P["c_slide"]
    y_rail1 = y_groove1 + 1.2
    for sx in (-1, 1):
        x_a = ux + sx * rail_x_in
        x_b = ux + sx * (rail_x_in + P["rail_w"])
        rail = box(min(x_a, x_b), max(x_a, x_b), wall_in_y - 0.01, y_rail1, z_rail0, D)
        x_g = ux + sx * (rail_x_in + P["groove_d"])
        groove = box(min(x_a, x_g) - (0.01 if sx > 0 else 0), max(x_a, x_g) + (0.01 if sx < 0 else 0),
                     y_groove0, y_groove1, z_rail0 + P["rail_floor"], D + 1)
        shell = shell.fuse(rail).cut(groove)
    return shell


def make_retainer() -> cq.Shape:
    """Flat plate, printed flat. Slides down into the grooves from the open back; the back
    cover then stops it lifting, so no detent is needed. U-slot at the leading (bottom)
    edge straddles the cable."""
    pw = 2 * (rail_x_in + P["groove_d"]) - 2 * P["c_slide"]
    z_bottom = z_rail0 + P["rail_floor"]
    ph = D - z_bottom - 0.5
    plate = box(-pw / 2, pw / 2, 0, ph, 0, P["retainer_t"])
    slot_w = M["usbc_cable_d"] + 1.0
    slot_len = (usbc_z - z_bottom)
    slot = box(-slot_w / 2, slot_w / 2, -1, slot_len, -1, P["retainer_t"] + 1)
    slot_end = cq.Solid.makeCylinder(slot_w / 2, P["retainer_t"] + 2,
                                     pnt=cq.Vector(0, slot_len, -1))
    return plate.cut(slot).cut(slot_end).clean()


def make_back_cover() -> cq.Shape:
    """Flat plate, printed flat (outside face down)."""
    cover = rounded_box(OW, OH, 0, P["cover_t"], P["r_outer"])
    for x, y in boss_xy:
        cover = cover.cut(cq.Solid.makeCylinder(M["screw_clear_d"] / 2, P["cover_t"] + 2,
                                                pnt=cq.Vector(x, y, -1)))
    # Vent slots over the Pi
    for i in range(-4, 5):
        cover = cover.cut(box(i * 8 - 1.25, i * 8 + 1.25, -20, 20, -1, P["cover_t"] + 1))
    return cover.clean()


# ============================================================================ fit tests
def make_fit_tests(shell: cq.Shape):
    ux = P["usbc_x"]
    half = rail_x_in + P["rail_w"] + 3
    fit_usbc = slice_test(shell, (ux - half, -OH / 2 - 1, z_rail0 - 3),
                          (ux + half, wall_in_y + 12, D + 1))
    y_c = P["posts_y"][1]
    fit_clip = slice_test(shell, (cav_w / 2 - 12, y_c - P["post_w"] / 2 - 4, -1),
                          (OW / 2 + 1, y_c + P["post_w"] / 2 + 4, z_screen_back + 6))
    gauge, key = clearance_gauge()
    return fit_usbc, fit_clip, gauge, key


# ================================================================================= main
def main() -> None:
    OUT.mkdir(exist_ok=True)
    shell = make_shell()
    parts = {"shell": shell, "back_cover": make_back_cover(), "retainer": make_retainer()}
    fit_usbc, fit_clip, gauge, key = make_fit_tests(shell)

    for name, shape in parts.items():
        print(check_part(shape, name, P["bed"]))
        export_part(shape, str(OUT / name))

    export_plate([("fit_usbc", fit_usbc), ("retainer", parts["retainer"]),
                  ("fit_clip", fit_clip), ("gauge", gauge), ("key", key)],
                 str(OUT / "fit_tests.3mf"))
    print(f"Shell outer size: {OW:.1f} x {OH:.1f} x {D:.1f} mm")
    print(f"Wrote files to {OUT}")


if __name__ == "__main__":
    main()

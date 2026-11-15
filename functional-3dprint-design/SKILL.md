---
name: functional-3dprint-design
description: Designs functional 3D-printed parts (enclosures, cases, mounts, brackets, clips, fixtures) from the user's own caliper measurements. Builds a parametric CadQuery or build123d model, prints small fit-test pieces before the full part, and delivers print-ready 3MF files with slicer settings and an optional finishing guide. Use when someone wants to design, model or print a part that has to fit real hardware or a real space.
license: MIT
---

# Functional 3D-Print Design

This skill turns "I need a case/mount/bracket for this thing" into print-ready files that fit
on the first full print. It is built around one principle:

> **Real parts beat spec sheets, and a 20-minute fit test beats a 10-hour reprint.**

Work through the phases in order. Do not skip the fit-test phase for any interface where
something has to fit, slide, clip or screw into something else.

## Phase 1 — Intake

Establish, in one short exchange:

1. **What the part does.** What it holds, protects, mounts, or connects. What it attaches to.
2. **Every interface.** List each place where the print meets something real: a board,
   a screen, a connector, a screw, a wall, another printed part. These become fit tests.
3. **Printer and material.** Printer model or bed size, nozzle size (assume 0.4 mm), material
   (recommend PLA unless heat >50 °C, outdoor UV, or flex is needed — see
   `references/print-settings.md`).
4. **Looks.** Is it cosmetic (visible, painted, wrapped) or purely functional? This decides
   layer height and whether to include the finishing guide.
5. **Fasteners on hand.** Screws, heat-set inserts, magnets — or screwless (preferred where
   practical; see snap-in mounts in `references/design-rules.md`).

## Phase 2 — Measurements

Read `references/measurement.md` before asking for numbers. Then:

- Give the user a **numbered measurement list**, one line per dimension, each with an exact
  definition ("hole spacing, **centre-to-centre**", "screen thickness at the **thickest** point
  including the FPC bulge").
- Ask for a **photo with the caliper in place** for any measurement that is easy to define two
  ways (hole spacing, port positions, offsets from an edge).
- Ask for each critical dimension to be measured **three times**; use the largest for clearances.
- Record every value in a `MEASUREMENTS` block at the top of the model script, with its
  definition and source (measured / datasheet / derived). Never silently use a datasheet value
  when the real part is available — datasheets are routinely wrong by 0.2–1 mm.
- If a number looks inconsistent with another (e.g. hole spacing larger than board width),
  **stop and ask**. Misread measurement definitions are the most common cause of failed prints.

## Phase 3 — Parametric model

Write one Python script per project using **CadQuery** (default) or **build123d** if the user
prefers it. Follow the template in `examples/display-enclosure/enclosure.py`:

1. `MEASUREMENTS` — raw numbers from the user, untouched.
2. `PARAMS` — design choices: wall thickness, clearances, fillet radii, tolerances.
3. Derived dimensions computed from the two blocks above. **No magic numbers** further down.
4. One function per printable part, returning a solid in its **print orientation**.
5. One function per fit test (Phase 4).
6. A `main()` that builds everything, validates it (`helpers/validate.py`), and exports
   3MF + STL + a preview SVG into `out/`.

Apply `references/design-rules.md` for wall thickness, clearances, snap-fits, pegs, heat-set
inserts, bridging and overhangs. Design for the print orientation from the start — orientation
decides where layer lines, supports and weak axes end up.

If CadQuery is not installed and cannot be, still write the script, tell the user exactly how
to install it (`pip install cadquery` or `pip install build123d`) and run it, and say plainly
that the geometry has not been executed.

## Phase 4 — Fit tests first

Before the full part, generate **small test pieces** that reproduce each interface at full
scale, using `helpers/fit_test.py`:

- **Slice tests** — a thin cut of the real part through the interface (e.g. a 15 mm ring of the
  enclosure wall around the USB-C cut-out, or one corner with its standoffs and clip post).
- **Clearance gauges** — a peg/hole comb that brackets the chosen clearance
  (e.g. 0.10 / 0.15 / 0.20 / 0.25 / 0.30 mm) so the user can pick what their printer needs.

Each fit test should print in under ~30 minutes and use the **same settings** as the final
part. Tell the user exactly what to check on each piece ("USB-C body slides in with light
pressure, retainer clicks home, no rattle"). Adjust `PARAMS` from their feedback and regenerate.
Only move to Phase 5 when every interface passes.

## Phase 5 — Deliverables

Deliver, per project:

- **`<part>.3mf`** for every printable part, already in print orientation, one object per file
  (use `helpers/export_3mf.py`; it works even if the CadQuery build lacks 3MF export).
- **STL** copies for slicers that need them.
- **The model script**, so the user can tweak parameters.
- **A print sheet** — per part: orientation, layer height, walls, infill, supports, brim, seam,
  estimated time if known (`references/print-settings.md`).
- **Assembly steps** in order, including what to fit before painting.
- **Finishing guide** if the part is cosmetic (`references/finishing.md`).

Check before delivering: every solid is valid, every part fits the user's build plate, and
every exported mesh is closed (`helpers/validate.py: check_part`). Wall thickness isn't
measured automatically. Assert each wall parameter against the minimums in
`references/design-rules.md` with `assert_min`, as the examples do.

Put fit tests in one 3MF with `export_plate`. It lays them out side by side on the bed, so they
open ready to slice. Bambu Studio shows a "3MF is not from Bambu Lab" notice for any file made
outside it. That's harmless, so tell the user to expect it.

## Phase 6 — Capture lessons

When the user reports a problem after printing, fix the model **and** record the cause in a
short "Lessons" note in the project README. Read `references/lessons-learned.md` at the start
of every project — it lists failures from real builds that are cheap to avoid.

## Files in this skill

| Path | Use |
|---|---|
| `references/measurement.md` | How to ask for, define and record measurements |
| `references/design-rules.md` | Clearances, walls, snap-fits, snap-in mounts, inserts, overhangs |
| `references/print-settings.md` | Material choice, orientation, slicer settings |
| `references/finishing.md` | Sand, prime, paint, clear, fabric wrap, bezel |
| `references/lessons-learned.md` | Failures from real builds and how to avoid them |
| `helpers/export_3mf.py` | Pure-Python 3MF writer + CadQuery/build123d adapters |
| `helpers/fit_test.py` | Slice tests and clearance gauges |
| `helpers/validate.py` | Validity, bed-fit and size checks before export |
| `examples/display-enclosure/` | Worked example: screen + Raspberry Pi enclosure, hidden ports, snap-in USB-C |
| `examples/snap-cable-clip/` | Worked example: small non-enclosure part with a cantilever snap-fit |

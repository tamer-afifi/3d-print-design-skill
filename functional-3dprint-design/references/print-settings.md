# Print settings

Write a print sheet for every part using the structure below. Values are starting points for a
0.4 mm nozzle; slicer names follow Bambu Studio / OrcaSlicer / PrusaSlicer.

## Material

| Material | Use when | Notes |
|---|---|---|
| **PLA** (default) | Indoor parts, enclosures, cosmetic parts | Easiest to print, sands and paints well. Softens around 55 °C — avoid hot cars and parts next to heat sources. |
| PETG | Snap-fits that flex a lot, mild heat, outdoor (out of direct sun) | Tougher, slightly stringy, harder to sand. |
| ASA | Outdoors, UV, heat up to ~90 °C | Needs an enclosed printer and ventilation. |
| TPU | Bumpers, feet, gaskets | Design with ≥ 1.2 mm walls; avoid bridges. |

## Orientation

- Choose orientation in the design phase, not in the slicer.
- Put the **best-looking face away from the bed** and away from supports.
- Put **load and flex directions in XY**. Layers are weakest when pulled apart in Z.
- For enclosure shells that will be painted, printing **upright** (opening facing up or
  sideways) usually gives the cleanest outer faces. This worked best on the PitVista
  display enclosure.

## Profiles

**Cosmetic parts** (visible, sanded, painted):

| Setting | Value |
|---|---|
| Layer height | **0.12 mm** |
| Walls | 3–4 |
| Top / bottom layers | 6 / 5 |
| Infill | 15–20 % gyroid |
| Supports | **Tree, build plate only** |
| Brim | **On** (5 mm) for tall or narrow parts |
| Seam | **Back** (or aligned to a hidden edge) |

**Functional parts** (brackets, clips, internal parts):

| Setting | Value |
|---|---|
| Layer height | 0.20 mm |
| Walls | 3–4 (more walls beat more infill for strength) |
| Infill | 20–40 % gyroid or cubic |
| Supports | Only where the model needs them |
| Brim | As needed |

**Fit tests:** use the **same** profile as the final part. A fit test printed at a different
layer height or speed doesn't tell you much.

## Print sheet template

```
Part: back_shell.3mf
Material: PLA (matte black)
Orientation: as exported (opening up)
Profile: cosmetic — 0.12 mm, 4 walls, 15 % gyroid
Supports: tree, build plate only
Brim: 5 mm
Seam: back
Check after print: USB-C pocket clean; no support scars on visible faces
```

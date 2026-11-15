# Design rules

Defaults for FDM printing with a 0.4 mm nozzle. Every one of these should be a named parameter
in the model script so it can be tuned after fit tests.

## Clearances (per side, i.e. radial / per face)

| Fit | Clearance | Example |
|---|---|---|
| Press fit | 0.00–0.05 mm | Locating peg that should not come out |
| Snug / friction | 0.10 mm | Lid that stays on by itself |
| Sliding | 0.15–0.20 mm | Board sliding into rails, retainer plate in a groove |
| Loose / drop-in | 0.25–0.40 mm | Component that must drop in without force |
| Moving parts printed in place | 0.40–0.50 mm | Print-in-place hinges |

Holes print undersize and pegs print oversize — especially small ones. Add clearance to both,
and always verify with a clearance gauge (`helpers/fit_test.py`) on the user's printer.

## Walls and features

- **Minimum wall:** 2 × nozzle (0.8 mm). Use **≥ 2.0 mm** for enclosure walls that get handled,
  **≥ 2.4 mm** where you'll sand and paint.
- **Minimum feature:** 1 × nozzle wide (0.4 mm); prefer ≥ 0.8 mm.
- **Floor / roof:** ≥ 4–5 layers (≈ 0.6–1.0 mm), more if the surface will be sanded.
- **Fillets:** fillet internal corners (≥ 1 mm) to reduce stress cracking; fillet outer vertical
  edges for looks and handling. Avoid fillets on edges touching the bed — use a 45° chamfer
  instead so the first layer stays sharp.
- **Text / embossing:** ≥ 0.6 mm deep/high, ≥ 1.5 mm stroke.

## Overhangs, bridges, holes

- Overhangs up to **45°** print without supports.
- Bridges up to ~**20 mm** print cleanly in PLA.
- Horizontal holes (axis parallel to the bed): use a **teardrop** or flat-topped hole to avoid
  support inside it.
- Vertical holes for screws: model at screw diameter + 0.2–0.3 mm, or the insert's specified
  hole size for heat-set inserts.

## Pegs and standoffs

- Locating pegs: chamfer the tip 0.3–0.5 mm so they find the hole.
- Pegs thinner than ~2.5 mm snap easily on the layer lines when printed vertically. Thicken
  them, or print the part so the peg lies flat, or use a metal pin.
- Standoffs: outer diameter ≥ 2.5 × hole diameter; add a fillet or gusset at the base.
- **If a hole will later get a heat-set threaded insert, any peg meant to locate in that hole
  must fit the insert's bore, not the original hole.** Make the peg thinner (see lessons-learned).

## Screwless snap-in mounts (preferred)

Instead of screws, hold components with **pegs + a slide-in retainer**:

1. A **pocket** shaped to the component (with sliding clearance).
2. **Pegs** that pass through the component's existing screw or mounting holes. These stop it
   moving sideways.
3. A **retainer plate** that slides into **grooves** on either side of the pocket and traps the
   component against the pegs. Add a small **detent bump** (0.3–0.4 mm) near the end of the
   groove so it clicks home and stays.

Typical use: panel-mount USB-C extension, small switches, round speakers, sensor boards.
See `examples/display-enclosure/` for a parametric version.

## Snap-fits (cantilever)

- Deflecting arm length ≥ 5 × its thickness.
- Thickness 1.2–2.0 mm in PLA; PETG tolerates more strain.
- Hook overhang (undercut) 0.6–1.2 mm, with a 30–45° lead-in.
- The arm must flex **across** layer lines, never so that layers peel apart. Orient the
  print so the arm's length lies in the XY plane.
- Fillet the root of the arm (≥ 0.5 mm).

## Heat-set inserts

- Use the insert maker's hole diameter (e.g. M3 × 5.7 mm inserts usually want ~4.0–4.2 mm).
- Boss outer diameter ≥ 2 × insert outer diameter; hole depth = insert length + 1 mm.
- Keep inserts ≥ 2 mm from outside walls you will sand or paint.

## Clips for screens and panels

- Size clip posts from the **measured** thickness of the panel at its thickest point,
  plus 0.2–0.3 mm. Never from the datasheet alone.
- Leave room for the flex cable / connector bulge on the back of displays.

## Big parts

- Check the bed size early. Split large parts with **alignment pegs** and a joint line where
  it's hidden or easy to finish.
- Keep long flat walls ≥ 2.4 mm or add ribs to stop warping.

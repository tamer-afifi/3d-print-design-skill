# Measurement guide

A printed part is only as good as the numbers it was built from. Most failed first prints come
from a measurement that was **taken correctly but defined differently** from how the model used it.

## Tools

- **Digital caliper** (0.01 mm resolution) for anything under ~150 mm. Zero it before each session.
- **Steel ruler or tape** for large spans; note the lower accuracy (±0.5 mm).
- **Radius / feeler gauges** are optional; a photo next to the caliper often does the same job.

## How to ask

Give the user a numbered list. Each line states **what**, **where**, and **how**:

```
1. Board width — outer edge to outer edge, along the long side.
2. Mounting hole spacing (long side) — CENTRE to centre.
   If easier, measure OUTER edge to outer edge of the two holes and the hole diameter;
   I'll subtract one diameter.
3. Mounting hole diameter.
4. Screen thickness — at the THICKEST point, including the ribbon-cable bulge on the back.
5. USB-C port: distance from the board's left edge to the CENTRE of the port.
6. USB-C port: height of the port's centre above the board's top surface.
```

Ask for:

- **Three readings** of each critical dimension. Use the **largest** for anything that must fit
  inside the print, the **smallest** for anything the print must fit inside.
- **A photo with the caliper jaws in place** for any measurement with two plausible definitions
  (spacing, offsets, positions). This catches edge-vs-centre mix-ups before they cost a print.
- **Component part numbers** (screen model, board model, connector) so you can cross-check
  against datasheets — but the user's measurement wins when they disagree.

## How to record

Put every value at the top of the model script, untouched, with its definition:

```python
MEASUREMENTS = {
    # name: (value_mm, definition, source)
    "hole_span_x_outer": (61.5, "outer edge to outer edge of the two holes, long side", "caliper x3"),
    "hole_d":            (2.75, "mounting hole diameter", "caliper x3"),
    "screen_t":          (5.6,  "thickest point incl. FPC bulge", "caliper x3, datasheet says 4.9"),
}
```

Then derive what the model needs, with the conversion visible:

```python
hole_span_x = M["hole_span_x_outer"] - M["hole_d"]   # centre-to-centre
```

## Sanity checks before modelling

- Hole spacing must be smaller than the board dimension it sits on.
- Port positions plus port widths must fit inside the board edge.
- A measured value more than ~0.5 mm away from the datasheet: ask the user to re-measure
  and confirm which one is real.
- Anything "about" or "roughly": treat it as unknown and cover it with a fit test.

## What not to measure

Don't ask for numbers you can get by fit-testing more cheaply — e.g. the exact clearance a
printer needs for a sliding fit. Pick a sensible default (`design-rules.md`) and print a
clearance gauge.

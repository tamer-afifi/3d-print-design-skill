# Example: snap-in cable clip

A small functional part, included to show that the workflow isn't only for enclosures.

- One measurement (cable diameter, largest of three readings) drives the whole part.
- The arms are **oriented so they flex along the layer lines**, which matters more than
  infill or wall count for anything that snaps.
- The fit test is a 4 mm slice of the real clip. Print it, push the cable in, and adjust
  `entry_ratio` (snap force) or `arm_t` (stiffness).

```bash
pip install cadquery
python cable_clip.py
```

Print with the functional profile: 0.2 mm layers, 4 walls, PLA or PETG. PETG survives more
cable changes.

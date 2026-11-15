"""Pre-export checks for printable parts.

Checks: the solid is valid, it has positive volume, it fits the build plate, and its
tessellated mesh is closed (every edge shared by exactly two triangles).

Wall thickness is NOT measured automatically. Keep walls as named PARAMS and assert
them against the minimums in references/design-rules.md (see `assert_min`).
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Sequence, Tuple

try:  # works both as a package import and when run from the helpers folder
    from .export_3mf import Mesh, mesh_from_shape, _unwrap
except ImportError:  # pragma: no cover
    from export_3mf import Mesh, mesh_from_shape, _unwrap


def mesh_is_closed(mesh: Mesh) -> Tuple[bool, int]:
    """Return (closed, bad_edge_count). A closed mesh has every edge used exactly twice."""
    edges = Counter()
    for a, b, c in mesh.triangles:
        for u, v in ((a, b), (b, c), (c, a)):
            edges[(u, v) if u < v else (v, u)] += 1
    bad = sum(1 for n in edges.values() if n != 2)
    return bad == 0, bad


def bbox_size(shape) -> Tuple[float, float, float]:
    bb = _unwrap(shape).BoundingBox()
    # CadQuery: xlen/ylen/zlen ; build123d: size.X/Y/Z
    if hasattr(bb, "xlen"):
        return (bb.xlen, bb.ylen, bb.zlen)
    return (bb.size.X, bb.size.Y, bb.size.Z)


def check_part(shape, name: str, bed: Sequence[float] = (256, 256, 256)) -> Dict[str, object]:
    """Run all checks on one part and return a report dict. Raises on hard failures."""
    s = _unwrap(shape)
    report: Dict[str, object] = {"part": name}

    valid = s.isValid() if hasattr(s, "isValid") else s.is_valid()
    report["valid"] = bool(valid)

    vol = s.Volume() if hasattr(s, "Volume") else s.volume
    report["volume_mm3"] = round(float(vol), 1)

    size = bbox_size(s)
    report["size_mm"] = tuple(round(v, 2) for v in size)
    # Allow rotation about Z on the bed: compare sorted XY footprints.
    fits = (all(a <= b for a, b in zip(sorted(size[:2]), sorted(bed[:2])))
            and size[2] <= bed[2])
    report["fits_bed"] = bool(fits)

    closed, bad = mesh_is_closed(mesh_from_shape(s, name))
    report["mesh_closed"] = closed
    report["open_edges"] = bad

    problems = []
    if not valid:
        problems.append("solid is not valid")
    if vol <= 0:
        problems.append("non-positive volume")
    if not fits:
        problems.append(f"does not fit bed {tuple(bed)}")
    if not closed:
        problems.append(f"mesh has {bad} open/non-manifold edges")
    report["ok"] = not problems
    if problems:
        raise ValueError(f"{name}: " + "; ".join(problems))
    return report


def assert_min(value: float, minimum: float, label: str) -> None:
    """Fail loudly when a design parameter drops below a rule from design-rules.md."""
    if value < minimum:
        raise ValueError(f"{label} = {value} mm is below the minimum of {minimum} mm")

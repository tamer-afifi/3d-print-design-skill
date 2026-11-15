"""Write print-ready 3MF (and binary STL) files without any third-party packages.

The writer itself is pure Python (zipfile + XML). Adapters turn CadQuery or build123d
shapes into triangle meshes using their built-in tessellation, so this works even when
the installed CadQuery build has no native 3MF exporter.

Usage
-----
    from helpers.export_3mf import export_part

    export_part(shape, "out/back_shell", name="back_shell")   # writes .3mf and .stl

    # Several objects in one 3MF (each stays a separate object in the slicer):
    write_3mf("out/fit_tests.3mf", [mesh_from_shape(a, "a"), mesh_from_shape(b, "b")])
"""

from __future__ import annotations

import os
import struct
import zipfile
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple
from xml.sax.saxutils import quoteattr

Vec3 = Tuple[float, float, float]
Tri = Tuple[int, int, int]


@dataclass
class Mesh:
    name: str
    vertices: List[Vec3]
    triangles: List[Tri]


# --------------------------------------------------------------------------- adapters

def _vec_xyz(v) -> Vec3:
    """Read x/y/z from a CadQuery Vector (x), build123d Vector (X) or a plain tuple."""
    if hasattr(v, "x"):
        return (float(v.x), float(v.y), float(v.z))
    if hasattr(v, "X"):
        return (float(v.X), float(v.Y), float(v.Z))
    return (float(v[0]), float(v[1]), float(v[2]))


def _unwrap(shape):
    """Accept a CadQuery Workplane, a CadQuery/build123d Shape, or a build123d builder."""
    # CadQuery Workplane -> combine everything on the stack into one shape
    if hasattr(shape, "vals") and hasattr(shape, "val"):
        vals = [v for v in shape.vals() if hasattr(v, "tessellate")]
        if not vals:
            raise ValueError("Workplane has no solids to export")
        if len(vals) == 1:
            return vals[0]
        import cadquery as cq  # only needed for multi-solid workplanes
        return cq.Compound.makeCompound(vals)
    # build123d BuildPart -> .part
    if hasattr(shape, "part") and not hasattr(shape, "tessellate"):
        return shape.part
    return shape


def mesh_from_shape(shape, name: str = "part", tolerance: float = 0.01,
                    angular_tolerance: float = 0.1) -> Mesh:
    """Tessellate a CadQuery or build123d shape into a Mesh.

    tolerance is the max chord deviation in mm. 0.01 mm is plenty for FDM; raise it for
    huge parts if files get large.
    """
    s = _unwrap(shape)
    verts, tris = s.tessellate(tolerance, angular_tolerance)
    return merge_vertices(Mesh(name=name,
                               vertices=[_vec_xyz(v) for v in verts],
                               triangles=[(int(a), int(b), int(c)) for a, b, c in tris]))


def merge_vertices(mesh: Mesh, decimals: int = 5) -> Mesh:
    """Weld coincident vertices.

    CadQuery and build123d tessellate face by face, so neighbouring faces get duplicate
    vertices along shared edges. Slicers want a single closed (manifold) mesh, so weld
    them and drop any triangles that collapse to a line.
    """
    index = {}
    verts: List[Vec3] = []
    remap = []
    for v in mesh.vertices:
        key = tuple(round(c, decimals) for c in v)
        if key not in index:
            index[key] = len(verts)
            verts.append(v)
        remap.append(index[key])
    tris = []
    for a, b, c in mesh.triangles:
        t = (remap[a], remap[b], remap[c])
        if len(set(t)) == 3:
            tris.append(t)
    return Mesh(mesh.name, verts, tris)


# --------------------------------------------------------------------------- writers

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" '
    'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="model" '
    'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
    '</Types>'
)

_RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
    'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
    '</Relationships>'
)


def _fmt(v: float) -> str:
    s = f"{v:.5f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def drop_to_bed(mesh: Mesh) -> Mesh:
    """Translate a mesh so its lowest point sits at Z = 0."""
    if not mesh.vertices:
        return mesh
    zmin = min(v[2] for v in mesh.vertices)
    return Mesh(mesh.name, [(x, y, z - zmin) for x, y, z in mesh.vertices], mesh.triangles)


def write_3mf(path: str, meshes: Sequence[Mesh], on_bed: bool = True) -> str:
    """Write one or more meshes to a 3MF file (units: millimetres). Returns the path."""
    if not path.lower().endswith(".3mf"):
        path += ".3mf"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    parts = ['<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<resources>']
    for i, m in enumerate(meshes, start=1):
        if on_bed:
            m = drop_to_bed(m)
        parts.append(f'<object id="{i}" type="model" name={quoteattr(m.name)}><mesh><vertices>')
        parts.extend(f'<vertex x="{_fmt(x)}" y="{_fmt(y)}" z="{_fmt(z)}"/>'
                     for x, y, z in m.vertices)
        parts.append('</vertices><triangles>')
        parts.extend(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.triangles)
        parts.append('</triangles></mesh></object>')
    parts.append('</resources><build>')
    parts.extend(f'<item objectid="{i}"/>' for i in range(1, len(meshes) + 1))
    parts.append('</build></model>')

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("3D/3dmodel.model", "".join(parts))
    return path


def write_stl(path: str, mesh: Mesh, on_bed: bool = True) -> str:
    """Write a binary STL. Returns the path."""
    if not path.lower().endswith(".stl"):
        path += ".stl"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if on_bed:
        mesh = drop_to_bed(mesh)
    v = mesh.vertices
    with open(path, "wb") as f:
        header = f"{mesh.name} - functional-3dprint-design".encode()[:80]
        f.write(header.ljust(80, b"\0"))
        f.write(struct.pack("<I", len(mesh.triangles)))
        for a, b, c in mesh.triangles:
            p, q, r = v[a], v[b], v[c]
            ux, uy, uz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
            wx, wy, wz = r[0] - p[0], r[1] - p[1], r[2] - p[2]
            nx, ny, nz = uy * wz - uz * wy, uz * wx - ux * wz, ux * wy - uy * wx
            ln = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
            f.write(struct.pack("<12fH", nx / ln, ny / ln, nz / ln, *p, *q, *r, 0))
    return path


def export_part(shape, basepath: str, name: str | None = None,
                tolerance: float = 0.01, stl: bool = True) -> List[str]:
    """Tessellate a shape and write <basepath>.3mf (and .stl). Returns written paths."""
    name = name or os.path.basename(basepath)
    mesh = mesh_from_shape(shape, name, tolerance)
    out = [write_3mf(basepath + ".3mf", [mesh])]
    if stl:
        out.append(write_stl(basepath + ".stl", mesh))
    return out


def export_plate(shapes: Iterable[Tuple[str, object]], path: str,
                 tolerance: float = 0.01) -> str:
    """Write several named shapes as separate objects in one 3MF (e.g. a fit-test set)."""
    return write_3mf(path, [mesh_from_shape(s, n, tolerance) for n, s in shapes])

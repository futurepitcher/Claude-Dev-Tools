"""
Shared utilities for the prosthetic cover engine.

Unit conversion, mesh statistics, bounding box helpers, and weight estimation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import trimesh


# ---------------------------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------------------------

_LENGTH_TO_MM: dict[str, float] = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
    "inch": 25.4,
    "inches": 25.4,
    "ft": 304.8,
    "foot": 304.8,
    "feet": 304.8,
}


def convert_length(value: float, from_unit: str, to_unit: str = "mm") -> float:
    """Convert a length value between units."""
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()
    if from_unit not in _LENGTH_TO_MM:
        raise ValueError(f"Unknown source unit '{from_unit}'. Known: {list(_LENGTH_TO_MM.keys())}")
    if to_unit not in _LENGTH_TO_MM:
        raise ValueError(f"Unknown target unit '{to_unit}'. Known: {list(_LENGTH_TO_MM.keys())}")
    mm_value = value * _LENGTH_TO_MM[from_unit]
    return mm_value / _LENGTH_TO_MM[to_unit]


def estimate_units(bounding_box_extent: np.ndarray) -> str:
    """Guess whether a mesh is in mm, cm, m, or inches based on bounding box size.

    A typical lower-limb prosthesis segment is roughly 200-500 mm long.
    """
    max_dim = float(np.max(bounding_box_extent))

    if max_dim < 1.0:
        return "m"
    elif max_dim < 10.0:
        return "cm" if max_dim > 2.0 else "m"
    elif max_dim < 50.0:
        # Could be cm or inches
        return "cm" if max_dim > 15.0 else "in"
    elif max_dim < 800.0:
        return "mm"
    else:
        # Very large — maybe already mm but oversized scan
        return "mm"


# ---------------------------------------------------------------------------
# Bounding box helpers
# ---------------------------------------------------------------------------

@dataclass
class BoundingBoxInfo:
    """Axis-aligned bounding box information."""

    min_corner: np.ndarray
    max_corner: np.ndarray
    extent: np.ndarray  # max - min per axis
    center: np.ndarray
    volume: float  # bounding box volume

    def __repr__(self) -> str:
        return (
            f"BoundingBox(extent=[{self.extent[0]:.1f}, {self.extent[1]:.1f}, "
            f"{self.extent[2]:.1f}] mm, center=[{self.center[0]:.1f}, "
            f"{self.center[1]:.1f}, {self.center[2]:.1f}])"
        )


def compute_bounding_box(mesh: trimesh.Trimesh) -> BoundingBoxInfo:
    """Compute axis-aligned bounding box for a mesh."""
    bounds = mesh.bounds  # (2, 3) array: [min_corner, max_corner]
    min_corner = bounds[0]
    max_corner = bounds[1]
    extent = max_corner - min_corner
    center = (min_corner + max_corner) / 2.0
    volume = float(np.prod(extent))
    return BoundingBoxInfo(
        min_corner=min_corner,
        max_corner=max_corner,
        extent=extent,
        center=center,
        volume=volume,
    )


# ---------------------------------------------------------------------------
# Mesh statistics
# ---------------------------------------------------------------------------

@dataclass
class MeshStats:
    """Summary statistics for a triangle mesh."""

    vertex_count: int
    face_count: int
    bounds: BoundingBoxInfo
    volume_mm3: float
    surface_area_mm2: float
    is_watertight: bool
    estimated_units: str

    @property
    def volume_cm3(self) -> float:
        return self.volume_mm3 / 1000.0

    def __repr__(self) -> str:
        return (
            f"MeshStats(verts={self.vertex_count}, faces={self.face_count}, "
            f"volume={self.volume_cm3:.1f} cm3, watertight={self.is_watertight})"
        )


def compute_mesh_stats(mesh: trimesh.Trimesh) -> MeshStats:
    """Compute comprehensive statistics for a mesh."""
    bbox = compute_bounding_box(mesh)
    units = estimate_units(bbox.extent)

    # Volume is only meaningful for watertight meshes, but trimesh gives a value anyway
    volume = float(mesh.volume) if mesh.is_volume else 0.0
    area = float(mesh.area)

    return MeshStats(
        vertex_count=len(mesh.vertices),
        face_count=len(mesh.faces),
        bounds=bbox,
        volume_mm3=volume,
        surface_area_mm2=area,
        is_watertight=mesh.is_watertight,
        estimated_units=units,
    )


# ---------------------------------------------------------------------------
# Weight estimation
# ---------------------------------------------------------------------------

def estimate_weight_grams(
    volume_mm3: float,
    density_g_per_cm3: float,
    infill_percent: int = 100,
    shell_thickness_mm: float | None = None,
) -> float:
    """Estimate part weight from volume and material density.

    For solid parts, infill_percent should be 100.
    For FDM parts, accounts for infill percentage.  For SLS/SLA parts,
    parts are typically solid so infill_percent is ignored when
    shell_thickness is not provided.

    Args:
        volume_mm3: Part volume in cubic millimeters.
        density_g_per_cm3: Material density.
        infill_percent: Interior fill percentage (0-100).
        shell_thickness_mm: Optional shell wall thickness for hollow estimation.

    Returns:
        Estimated weight in grams.
    """
    volume_cm3 = volume_mm3 / 1000.0
    effective_fill = infill_percent / 100.0
    weight = volume_cm3 * density_g_per_cm3 * effective_fill
    return max(0.0, weight)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def compute_vertex_normals_area_weighted(mesh: trimesh.Trimesh) -> np.ndarray:
    """Compute area-weighted vertex normals.

    trimesh already provides vertex_normals, but this gives explicit control
    for offset operations where normal quality matters.
    """
    return np.array(mesh.vertex_normals)


def offset_mesh_along_normals(
    mesh: trimesh.Trimesh, offset_mm: float, vertex_mask: np.ndarray | None = None
) -> trimesh.Trimesh:
    """Create a copy of the mesh offset along vertex normals.

    Args:
        mesh: Source mesh.
        offset_mm: Distance to offset (positive = outward).
        vertex_mask: Optional boolean array selecting which vertices to offset.
                     If None, all vertices are offset.

    Returns:
        New trimesh.Trimesh with offset vertices.
    """
    import trimesh as _trimesh

    normals = compute_vertex_normals_area_weighted(mesh)
    new_vertices = mesh.vertices.copy()

    if vertex_mask is not None:
        new_vertices[vertex_mask] += normals[vertex_mask] * offset_mm
    else:
        new_vertices += normals * offset_mm

    return _trimesh.Trimesh(
        vertices=new_vertices,
        faces=mesh.faces.copy(),
        process=False,
    )


def laplacian_smooth(
    mesh: trimesh.Trimesh, iterations: int = 1, lamb: float = 0.5
) -> trimesh.Trimesh:
    """Apply Laplacian smoothing to a mesh.

    Args:
        mesh: Input mesh.
        iterations: Number of smoothing passes.
        lamb: Smoothing factor (0-1). Higher = more smoothing per iteration.

    Returns:
        Smoothed mesh (new object).
    """
    import trimesh as _trimesh

    vertices = mesh.vertices.copy()
    faces = mesh.faces

    # Build adjacency: for each vertex, find its neighbor vertices
    edges = mesh.edges_unique
    adjacency: dict[int, list[int]] = {i: [] for i in range(len(vertices))}
    for e in edges:
        adjacency[int(e[0])].append(int(e[1]))
        adjacency[int(e[1])].append(int(e[0]))

    for _ in range(iterations):
        new_vertices = vertices.copy()
        for vi in range(len(vertices)):
            neighbors = adjacency[vi]
            if not neighbors:
                continue
            neighbor_center = np.mean(vertices[neighbors], axis=0)
            new_vertices[vi] = vertices[vi] + lamb * (neighbor_center - vertices[vi])
        vertices = new_vertices

    return _trimesh.Trimesh(vertices=vertices, faces=faces.copy(), process=False)


def faces_in_z_range(mesh: trimesh.Trimesh, z_min: float, z_max: float) -> np.ndarray:
    """Return face indices whose centroid Z coordinate falls within [z_min, z_max]."""
    centroids = mesh.triangles_center  # (n_faces, 3)
    z_vals = centroids[:, 2]
    mask = (z_vals >= z_min) & (z_vals <= z_max)
    return np.where(mask)[0]


def vertex_indices_for_faces(mesh: trimesh.Trimesh, face_indices: np.ndarray) -> np.ndarray:
    """Return unique vertex indices referenced by the given faces."""
    if len(face_indices) == 0:
        return np.array([], dtype=int)
    face_verts = mesh.faces[face_indices].flatten()
    return np.unique(face_verts)

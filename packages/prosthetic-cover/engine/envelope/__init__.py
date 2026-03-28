"""
Envelope generation module.

Offsets the scan mesh outward by the clearance distance to create the
inner boundary of the prosthetic cover.  Only the coverage zone is offset;
uncovered regions are left at their original position.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.regions import RegionMap
from engine.utils import (
    laplacian_smooth,
    offset_mesh_along_normals,
    vertex_indices_for_faces,
)

logger = logging.getLogger(__name__)


@dataclass
class EnvelopeReport:
    """Results from envelope generation."""

    offset_applied_mm: float
    coverage_vertex_count: int
    total_vertex_count: int
    coverage_area_mm2: float
    clearance_stats: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def _compute_coverage_area(mesh: trimesh.Trimesh, face_indices: set[int]) -> float:
    """Compute total surface area of the given faces."""
    if not face_indices:
        return 0.0
    face_list = np.array(list(face_indices))
    areas = mesh.area_faces[face_list]
    return float(np.sum(areas))


def _smooth_offset_boundary(
    mesh: trimesh.Trimesh,
    coverage_verts: np.ndarray,
    iterations: int = 2,
    lamb: float = 0.3,
) -> trimesh.Trimesh:
    """Smooth the boundary between offset and non-offset vertices.

    Applies localized Laplacian smoothing only to vertices near the
    coverage boundary to prevent sharp steps in the offset surface.
    """
    vertices = mesh.vertices.copy()
    faces = mesh.faces

    coverage_set = set(coverage_verts.tolist())
    all_verts = set(range(len(vertices)))
    non_coverage = all_verts - coverage_set

    # Find boundary vertices: coverage verts adjacent to non-coverage verts
    edges = mesh.edges_unique
    boundary_verts: set[int] = set()
    for e in edges:
        v0, v1 = int(e[0]), int(e[1])
        if (v0 in coverage_set) != (v1 in coverage_set):
            boundary_verts.add(v0)
            boundary_verts.add(v1)

    if not boundary_verts:
        return mesh

    # Expand the boundary band by one ring
    adjacency: dict[int, list[int]] = {i: [] for i in boundary_verts}
    for e in edges:
        v0, v1 = int(e[0]), int(e[1])
        if v0 in boundary_verts or v1 in boundary_verts:
            adjacency.setdefault(v0, []).append(v1)
            adjacency.setdefault(v1, []).append(v0)

    smooth_verts = set(boundary_verts)
    for v in boundary_verts:
        smooth_verts.update(adjacency.get(v, []))

    smooth_list = np.array(list(smooth_verts))

    # Build full adjacency for the smoothing region
    full_adj: dict[int, list[int]] = {}
    for e in edges:
        v0, v1 = int(e[0]), int(e[1])
        full_adj.setdefault(v0, []).append(v1)
        full_adj.setdefault(v1, []).append(v0)

    # Smooth only the boundary band
    for _ in range(iterations):
        new_vertices = vertices.copy()
        for vi in smooth_list:
            neighbors = full_adj.get(vi, [])
            if not neighbors:
                continue
            neighbor_center = np.mean(vertices[neighbors], axis=0)
            new_vertices[vi] = vertices[vi] + lamb * (neighbor_center - vertices[vi])
        vertices = new_vertices

    return trimesh.Trimesh(vertices=vertices, faces=faces.copy(), process=False)


def generate_envelope(
    mesh: trimesh.Trimesh,
    region_map: RegionMap,
    config: CoverConfig,
) -> tuple[trimesh.Trimesh, EnvelopeReport]:
    """Generate the clearance envelope by offsetting the coverage zone outward.

    The envelope represents the inner surface of the prosthetic cover.
    It is offset from the scan surface by ``config.clearance_offset_mm``
    along vertex normals, but only for vertices within the coverage zone.

    Args:
        mesh: Aligned, cleaned scan mesh.
        region_map: Region definitions.
        config: Pipeline configuration.

    Returns:
        Tuple of (envelope mesh, envelope report).
    """
    warnings: list[str] = []

    if not region_map.coverage:
        warnings.append("No coverage zone defined. Envelope will be identical to input.")
        report = EnvelopeReport(
            offset_applied_mm=0.0,
            coverage_vertex_count=0,
            total_vertex_count=len(mesh.vertices),
            coverage_area_mm2=0.0,
            warnings=warnings,
        )
        return mesh.copy(), report

    offset = config.clearance_offset_mm
    logger.info("Generating envelope with %.2f mm clearance offset", offset)

    # Get vertices belonging to coverage faces
    coverage_face_arr = np.array(list(region_map.coverage))
    coverage_verts = vertex_indices_for_faces(mesh, coverage_face_arr)

    # Build vertex mask
    vertex_mask = np.zeros(len(mesh.vertices), dtype=bool)
    vertex_mask[coverage_verts] = True

    # Offset along normals
    envelope = offset_mesh_along_normals(mesh, offset, vertex_mask=vertex_mask)

    # Smooth the boundary to avoid step artifacts
    envelope = _smooth_offset_boundary(envelope, coverage_verts, iterations=2)

    # Compute coverage area on the offset mesh
    coverage_area = _compute_coverage_area(envelope, region_map.coverage)

    # Clearance statistics: measure actual distances between original and offset
    original_coverage_pts = mesh.vertices[coverage_verts]
    offset_coverage_pts = envelope.vertices[coverage_verts]
    distances = np.linalg.norm(offset_coverage_pts - original_coverage_pts, axis=1)

    clearance_stats = {
        "min_mm": float(np.min(distances)) if len(distances) > 0 else 0.0,
        "max_mm": float(np.max(distances)) if len(distances) > 0 else 0.0,
        "mean_mm": float(np.mean(distances)) if len(distances) > 0 else 0.0,
        "std_mm": float(np.std(distances)) if len(distances) > 0 else 0.0,
    }

    report = EnvelopeReport(
        offset_applied_mm=offset,
        coverage_vertex_count=int(len(coverage_verts)),
        total_vertex_count=len(envelope.vertices),
        coverage_area_mm2=coverage_area,
        clearance_stats=clearance_stats,
        warnings=warnings,
    )

    logger.info(
        "Envelope generated: %d coverage vertices offset, area=%.1f mm2, "
        "clearance mean=%.2f mm",
        len(coverage_verts), coverage_area, clearance_stats["mean_mm"],
    )

    return envelope, report

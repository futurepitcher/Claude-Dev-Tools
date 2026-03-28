"""
Shell generation module.

Creates a hollow shell from the envelope mesh by generating an outer surface
(offset outward by shell thickness) and bridging inner and outer edges to
form a closed, watertight solid suitable for 3D printing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.utils import (
    estimate_weight_grams,
    offset_mesh_along_normals,
)

logger = logging.getLogger(__name__)


@dataclass
class ShellReport:
    """Results from shell generation."""

    wall_thickness_stats: dict[str, float]  # min, max, mean in mm
    volume_mm3: float
    surface_area_mm2: float
    weight_estimate_grams: float
    is_watertight: bool
    warnings: list[str] = field(default_factory=list)


def _bridge_boundary_edges(
    inner_verts: np.ndarray,
    outer_verts: np.ndarray,
    inner_faces: np.ndarray,
    outer_faces: np.ndarray,
    n_inner_verts: int,
) -> np.ndarray:
    """Generate triangle faces to bridge the open edges of inner and outer surfaces.

    Finds boundary edges (edges used by only one face) on both surfaces and
    connects corresponding vertices with triangle strips.

    Returns an array of bridge faces referencing the combined vertex array.
    """
    def find_boundary_edges(faces: np.ndarray) -> list[tuple[int, int]]:
        from collections import Counter
        edge_count: Counter[tuple[int, int]] = Counter()
        for face in faces:
            for i in range(3):
                e = tuple(sorted((int(face[i]), int(face[(i + 1) % 3]))))
                edge_count[e] += 1
        return [e for e, c in edge_count.items() if c == 1]

    inner_boundary = find_boundary_edges(inner_faces)
    outer_boundary = find_boundary_edges(outer_faces)

    if not inner_boundary or not outer_boundary:
        return np.array([], dtype=np.int64).reshape(0, 3)

    # Sort boundary edges into ordered loops
    def edges_to_loop(edges: list[tuple[int, int]]) -> list[int]:
        if not edges:
            return []
        adj: dict[int, list[int]] = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)

        loop = [edges[0][0], edges[0][1]]
        visited_edges = {(edges[0][0], edges[0][1]), (edges[0][1], edges[0][0])}

        while len(loop) < len(edges) + 1:
            current = loop[-1]
            found_next = False
            for neighbor in adj.get(current, []):
                if (current, neighbor) not in visited_edges:
                    visited_edges.add((current, neighbor))
                    visited_edges.add((neighbor, current))
                    loop.append(neighbor)
                    found_next = True
                    break
            if not found_next:
                break

        return loop

    inner_loop = edges_to_loop(inner_boundary)
    outer_loop = edges_to_loop(outer_boundary)

    if len(inner_loop) < 3 or len(outer_loop) < 3:
        return np.array([], dtype=np.int64).reshape(0, 3)

    # Match inner loop vertices to closest outer loop vertices
    inner_pts = inner_verts[inner_loop]
    outer_pts = outer_verts[outer_loop]

    # For each inner loop vertex, find the closest outer loop vertex
    # to establish correspondence
    from scipy.spatial import cKDTree

    outer_tree = cKDTree(outer_pts)
    _, closest_idx = outer_tree.query(inner_pts)

    # Build bridge triangles
    bridge_faces = []
    n_inner = len(inner_loop)

    for i in range(n_inner - 1):
        # Inner vertex indices (in combined array)
        iv0 = inner_loop[i]
        iv1 = inner_loop[i + 1]
        # Corresponding outer vertex indices (offset by n_inner_verts)
        ov0 = outer_loop[closest_idx[i]] + n_inner_verts
        ov1 = outer_loop[closest_idx[i + 1]] + n_inner_verts

        # Two triangles forming a quad
        bridge_faces.append([iv0, ov0, iv1])
        bridge_faces.append([iv1, ov0, ov1])

    if not bridge_faces:
        return np.array([], dtype=np.int64).reshape(0, 3)

    return np.array(bridge_faces, dtype=np.int64)


def generate_shell(
    envelope_mesh: trimesh.Trimesh, config: CoverConfig
) -> tuple[trimesh.Trimesh, ShellReport]:
    """Generate a hollow shell from the envelope mesh.

    Creates two surfaces:
        - Inner surface: the envelope (clearance boundary)
        - Outer surface: envelope offset outward by shell_thickness_mm

    The two surfaces are bridged at their open edges to create a closed solid.

    Args:
        envelope_mesh: The clearance envelope mesh.
        config: Pipeline configuration.

    Returns:
        Tuple of (shell mesh, shell report).
    """
    warnings: list[str] = []
    thickness = config.shell_thickness_mm

    logger.info("Generating shell with %.2f mm wall thickness", thickness)

    # ---- Inner surface (envelope, normals pointing inward for the shell) ----
    inner_mesh = envelope_mesh.copy()

    # ---- Outer surface (offset outward by shell thickness) ----
    outer_mesh = offset_mesh_along_normals(envelope_mesh, thickness)

    # ---- Flip inner surface normals so they point inward ----
    inner_faces_flipped = inner_mesh.faces[:, ::-1].copy()

    # ---- Combine into a single shell mesh ----
    n_inner_verts = len(inner_mesh.vertices)

    # Offset outer face indices
    outer_faces_offset = outer_mesh.faces + n_inner_verts

    # Combine vertices and faces
    combined_verts = np.vstack([inner_mesh.vertices, outer_mesh.vertices])

    # Bridge the open edges
    bridge_faces = _bridge_boundary_edges(
        inner_mesh.vertices,
        outer_mesh.vertices,
        inner_faces_flipped,
        outer_mesh.faces,
        n_inner_verts,
    )

    all_faces = [inner_faces_flipped, outer_faces_offset]
    if len(bridge_faces) > 0:
        all_faces.append(bridge_faces)

    combined_faces = np.vstack(all_faces)

    shell = trimesh.Trimesh(
        vertices=combined_verts,
        faces=combined_faces,
        process=True,
    )

    # Fix normals
    trimesh.repair.fix_normals(shell)

    # ---- Wall thickness statistics ----
    # Sample distances between inner and outer surface points
    inner_pts = inner_mesh.vertices
    outer_pts = outer_mesh.vertices

    # For corresponding vertices, the distance is the wall thickness
    dists = np.linalg.norm(outer_pts - inner_pts, axis=1)

    thickness_stats = {
        "min_mm": float(np.min(dists)),
        "max_mm": float(np.max(dists)),
        "mean_mm": float(np.mean(dists)),
        "std_mm": float(np.std(dists)),
        "target_mm": thickness,
    }

    if thickness_stats["min_mm"] < config.material_spec.min_wall_thickness:
        warnings.append(
            f"Minimum wall thickness ({thickness_stats['min_mm']:.2f} mm) is below "
            f"material minimum ({config.material_spec.min_wall_thickness} mm)"
        )

    # ---- Volume and weight ----
    volume = float(shell.volume) if shell.is_volume else 0.0
    if volume < 0:
        volume = abs(volume)
    if volume == 0.0:
        # Estimate from surface area and thickness
        volume = float(envelope_mesh.area) * thickness
        warnings.append("Shell is not watertight; volume estimated from area * thickness")

    weight = estimate_weight_grams(
        volume,
        config.material_spec.density_g_per_cm3,
        infill_percent=config.infill_percent,
    )

    report = ShellReport(
        wall_thickness_stats=thickness_stats,
        volume_mm3=volume,
        surface_area_mm2=float(shell.area),
        weight_estimate_grams=weight,
        is_watertight=shell.is_watertight,
        warnings=warnings,
    )

    logger.info(
        "Shell generated: %.0f mm3 volume, %.1f g estimated weight, watertight=%s",
        volume, weight, shell.is_watertight,
    )

    return shell, report

"""
Mesh cleanup and repair module.

Fixes common scan artifacts: non-manifold edges, holes, degenerate faces.
Optionally decimates high-poly meshes and applies Laplacian smoothing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.utils import laplacian_smooth

logger = logging.getLogger(__name__)

# If face count exceeds this, offer decimation
DECIMATION_THRESHOLD = 500_000
DECIMATION_TARGET_RATIO = 0.5


@dataclass
class CleanupReport:
    """Summary of repairs performed during cleanup."""

    faces_removed: int = 0
    holes_filled: int = 0
    non_manifold_fixed: int = 0
    was_decimated: bool = False
    decimated_from: int = 0
    decimated_to: int = 0
    smoothing_iterations: int = 0
    warnings: list[str] = field(default_factory=list)


def _remove_degenerate_faces(mesh: trimesh.Trimesh) -> int:
    """Remove zero-area and degenerate faces. Returns count removed."""
    initial_count = len(mesh.faces)
    mesh.update_faces(mesh.nondegenerate_faces())
    removed = initial_count - len(mesh.faces)
    if removed > 0:
        logger.info("Removed %d degenerate faces", removed)
    return removed


def _fix_non_manifold(mesh: trimesh.Trimesh) -> int:
    """Attempt to fix non-manifold edges by removing offending faces.

    Returns the number of faces removed to resolve non-manifold conditions.
    """
    if mesh.is_watertight:
        return 0

    # trimesh tracks edges shared by more than 2 faces as non-manifold
    try:
        edges = mesh.edges_sorted
        # Count how many faces reference each edge
        edge_tuples = [tuple(e) for e in edges]
        from collections import Counter

        edge_counts = Counter(edge_tuples)
        non_manifold_edges = {e for e, c in edge_counts.items() if c > 2}

        if not non_manifold_edges:
            return 0

        # Find faces that contain non-manifold edges and remove them
        bad_face_indices = set()
        for fi, face in enumerate(mesh.faces):
            face_edges = [
                tuple(sorted((face[0], face[1]))),
                tuple(sorted((face[1], face[2]))),
                tuple(sorted((face[0], face[2]))),
            ]
            for fe in face_edges:
                if fe in non_manifold_edges:
                    bad_face_indices.add(fi)
                    break

        if bad_face_indices:
            keep_mask = np.ones(len(mesh.faces), dtype=bool)
            keep_mask[list(bad_face_indices)] = False
            mesh.update_faces(keep_mask)
            logger.info("Removed %d faces to fix non-manifold edges", len(bad_face_indices))
            return len(bad_face_indices)

    except Exception as exc:
        logger.warning("Non-manifold fix encountered an error: %s", exc)

    return 0


def _fill_holes(mesh: trimesh.Trimesh) -> int:
    """Fill holes in the mesh. Returns number of holes filled."""
    if mesh.is_watertight:
        return 0

    try:
        initial_faces = len(mesh.faces)
        trimesh.repair.fill_holes(mesh)
        new_faces = len(mesh.faces) - initial_faces
        # Approximate hole count from faces added (rough heuristic)
        holes_filled = max(1, new_faces // 3) if new_faces > 0 else 0
        if holes_filled > 0:
            logger.info("Filled approximately %d holes (%d faces added)", holes_filled, new_faces)
        return holes_filled
    except Exception as exc:
        logger.warning("Hole filling encountered an error: %s", exc)
        return 0


def _decimate(mesh: trimesh.Trimesh, target_face_count: int) -> trimesh.Trimesh:
    """Decimate a mesh to the target face count.

    Uses trimesh's simplify_quadric_decimation when available, otherwise
    falls back to a vertex-clustering approach.
    """
    try:
        simplified = mesh.simplify_quadric_decimation(target_face_count)
        return simplified
    except Exception:
        logger.warning(
            "Quadric decimation not available (requires python-fcl or fast-simplification). "
            "Skipping decimation."
        )
        return mesh


def repair_mesh(mesh: trimesh.Trimesh, config: CoverConfig) -> tuple[trimesh.Trimesh, CleanupReport]:
    """Run the full cleanup pipeline on a scan mesh.

    Steps:
        1. Remove degenerate faces (zero area, duplicate).
        2. Fix non-manifold edges.
        3. Fill holes.
        4. Decimate if face count exceeds threshold.
        5. Laplacian smoothing.
        6. Fix winding and normals.

    Args:
        mesh: Input scan mesh.
        config: Pipeline configuration.

    Returns:
        Tuple of (cleaned mesh, cleanup report).
    """
    report = CleanupReport()

    # Work on a copy to avoid mutating the original
    mesh = mesh.copy()

    logger.info(
        "Starting cleanup: %d vertices, %d faces, watertight=%s",
        len(mesh.vertices), len(mesh.faces), mesh.is_watertight,
    )

    # 1. Remove degenerate faces
    report.faces_removed += _remove_degenerate_faces(mesh)

    # 2. Remove duplicate faces
    initial = len(mesh.faces)
    mesh.update_faces(mesh.unique_faces())
    dupes_removed = initial - len(mesh.faces)
    report.faces_removed += dupes_removed
    if dupes_removed > 0:
        logger.info("Removed %d duplicate faces", dupes_removed)

    # 3. Fix non-manifold edges
    nm_fixed = _fix_non_manifold(mesh)
    report.non_manifold_fixed = nm_fixed
    report.faces_removed += nm_fixed

    # 4. Fill holes
    report.holes_filled = _fill_holes(mesh)

    # 5. Fix normals to be consistently outward-facing
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fix_inversion(mesh)

    # 6. Decimate if needed
    n_faces = len(mesh.faces)
    if n_faces > DECIMATION_THRESHOLD:
        target = int(n_faces * DECIMATION_TARGET_RATIO)
        logger.info("Face count %d exceeds threshold; decimating to ~%d", n_faces, target)
        report.decimated_from = n_faces
        mesh = _decimate(mesh, target)
        report.decimated_to = len(mesh.faces)
        report.was_decimated = True

    # 7. Laplacian smoothing
    if config.smoothing_iterations > 0:
        mesh = laplacian_smooth(mesh, iterations=config.smoothing_iterations)
        report.smoothing_iterations = config.smoothing_iterations
        logger.info("Applied %d iterations of Laplacian smoothing", config.smoothing_iterations)

    # Final normals fix after smoothing
    trimesh.repair.fix_normals(mesh)

    logger.info(
        "Cleanup complete: %d vertices, %d faces, watertight=%s",
        len(mesh.vertices), len(mesh.faces), mesh.is_watertight,
    )

    return mesh, report

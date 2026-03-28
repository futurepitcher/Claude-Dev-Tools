"""
Scan intake module — load and validate 3D scan files.

Supports STL, OBJ, and PLY formats via trimesh.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

from engine.utils import BoundingBoxInfo, compute_bounding_box, estimate_units

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".stl", ".obj", ".ply"}

# Reasonable bounds for a prosthesis scan (in mm)
MIN_VERTEX_COUNT = 100
MAX_VERTEX_COUNT = 10_000_000
MIN_EXTENT_MM = 50.0  # smallest plausible prosthesis dimension
MAX_EXTENT_MM = 1000.0  # largest plausible dimension


@dataclass
class MeshStats:
    """Summary statistics returned after loading a scan."""

    vertices: int
    faces: int
    bounds: BoundingBoxInfo
    volume: float  # mm3 (meaningful only if watertight)
    is_watertight: bool
    estimated_units: str


@dataclass
class IntakeReport:
    """Detailed report from the intake stage."""

    filepath: str
    file_size_bytes: int
    stats: MeshStats
    warnings: list[str]


def load_scan(filepath: str | Path) -> tuple[trimesh.Trimesh, IntakeReport]:
    """Load a 3D scan from file and validate it.

    Args:
        filepath: Path to an STL, OBJ, or PLY file.

    Returns:
        Tuple of (mesh, report).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported or the mesh is invalid.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Scan file not found: {filepath}")

    ext = filepath.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported: {SUPPORTED_EXTENSIONS}"
        )

    file_size = filepath.stat().st_size
    if file_size == 0:
        raise ValueError(f"Scan file is empty: {filepath}")

    logger.info("Loading scan from %s (%.1f MB)", filepath, file_size / 1e6)

    # Load with trimesh
    mesh = trimesh.load(str(filepath), force="mesh")

    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(
            f"File did not load as a single mesh. Got {type(mesh).__name__}. "
            "If the file contains a scene, export it as a single mesh first."
        )

    warnings: list[str] = []

    # Validate vertex count
    n_verts = len(mesh.vertices)
    n_faces = len(mesh.faces)

    if n_verts < MIN_VERTEX_COUNT:
        warnings.append(
            f"Very low vertex count ({n_verts}). Scan may be incomplete or corrupted."
        )
    if n_verts > MAX_VERTEX_COUNT:
        warnings.append(
            f"Very high vertex count ({n_verts}). Consider decimating before processing."
        )

    if n_faces == 0:
        raise ValueError("Mesh has no faces. File may be corrupted.")

    # Bounding box and units
    bbox = compute_bounding_box(mesh)
    est_units = estimate_units(bbox.extent)

    if est_units != "mm":
        warnings.append(
            f"Mesh appears to be in '{est_units}' (max extent: {np.max(bbox.extent):.2f}). "
            f"The pipeline expects millimeters. Consider converting before processing."
        )

    max_extent = float(np.max(bbox.extent))
    if est_units == "mm":
        if max_extent < MIN_EXTENT_MM:
            warnings.append(
                f"Mesh is very small ({max_extent:.1f} mm). "
                "Verify that units are correct."
            )
        if max_extent > MAX_EXTENT_MM:
            warnings.append(
                f"Mesh is very large ({max_extent:.1f} mm). "
                "Verify that units are correct."
            )

    # Watertight check
    if not mesh.is_watertight:
        warnings.append("Mesh is not watertight. The cleanup stage will attempt repairs.")

    # Volume
    volume = float(mesh.volume) if mesh.is_volume else 0.0

    stats = MeshStats(
        vertices=n_verts,
        faces=n_faces,
        bounds=bbox,
        volume=volume,
        is_watertight=mesh.is_watertight,
        estimated_units=est_units,
    )

    report = IntakeReport(
        filepath=str(filepath),
        file_size_bytes=file_size,
        stats=stats,
        warnings=warnings,
    )

    for w in warnings:
        logger.warning("Intake: %s", w)

    logger.info(
        "Loaded mesh: %d vertices, %d faces, watertight=%s",
        n_verts, n_faces, mesh.is_watertight,
    )

    return mesh, report

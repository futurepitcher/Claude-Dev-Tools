"""
Anatomical alignment module.

Uses PCA to detect principal axes and orients the scan so the
proximal-distal axis aligns to Z, centered at the origin.
Optionally auto-detects left vs. right side from geometry asymmetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import trimesh

from engine.config import CoverConfig

logger = logging.getLogger(__name__)


@dataclass
class AlignmentReport:
    """Results from the alignment stage."""

    principal_axes: np.ndarray  # (3, 3) — rows are axis vectors
    center_of_mass: np.ndarray  # (3,)
    bounding_box_extent: np.ndarray  # (3,) in mm
    detected_side: str  # "left", "right", or "unknown"
    transform_applied: np.ndarray  # (4, 4) homogeneous transform


def _pca_axes(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute PCA on a vertex cloud.

    Returns:
        eigenvalues (descending), eigenvectors (columns correspond to eigenvalues),
        and the centroid.
    """
    centroid = np.mean(vertices, axis=0)
    centered = vertices - centroid
    cov = np.cov(centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # eigh returns ascending order; reverse to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    return eigenvalues, eigenvectors, centroid


def _ensure_right_handed(axes: np.ndarray) -> np.ndarray:
    """Ensure the 3x3 rotation matrix forms a right-handed coordinate system."""
    if np.linalg.det(axes) < 0:
        axes[:, 2] = -axes[:, 2]
    return axes


def _detect_side(mesh: trimesh.Trimesh) -> str:
    """Attempt to detect left vs. right side from geometric asymmetry.

    After PCA alignment (Z = long axis), the cross-section asymmetry along
    the X axis can indicate side.  The calf / shin profile is not symmetric
    about the sagittal plane, so the center of mass offset in X gives a hint.

    This is a heuristic and may be unreliable on highly symmetric scans.
    """
    vertices = mesh.vertices
    centroid = np.mean(vertices, axis=0)

    # Split vertices into +X and -X halves relative to centroid
    left_verts = vertices[vertices[:, 0] < centroid[0]]
    right_verts = vertices[vertices[:, 0] >= centroid[0]]

    if len(left_verts) == 0 or len(right_verts) == 0:
        return "unknown"

    # Compare surface area proxy (vertex density) on each side
    left_spread = np.std(left_verts[:, 1])  # Y spread on left
    right_spread = np.std(right_verts[:, 1])  # Y spread on right

    # The lateral side of the leg typically has more curvature / spread
    # For a right leg, lateral is on the right (+X after standard alignment)
    ratio = right_spread / left_spread if left_spread > 0 else 1.0

    if abs(ratio - 1.0) < 0.05:
        return "unknown"  # Too symmetric to tell
    elif ratio > 1.0:
        return "right"
    else:
        return "left"


def align_to_anatomical_frame(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> tuple[trimesh.Trimesh, AlignmentReport]:
    """Align a prosthesis scan to a canonical anatomical frame.

    The result has:
        - Z axis: proximal-distal (long axis of the limb segment)
        - X axis: medial-lateral
        - Y axis: anterior-posterior
        - Origin at the centroid of the mesh

    Args:
        mesh: Input mesh (cleaned scan).
        config: Pipeline configuration.

    Returns:
        Tuple of (aligned mesh, alignment report).
    """
    mesh = mesh.copy()

    # ---- PCA to find principal axes ----
    eigenvalues, eigenvectors, centroid = _pca_axes(mesh.vertices)

    logger.info(
        "PCA eigenvalues: [%.1f, %.1f, %.1f]",
        eigenvalues[0], eigenvalues[1], eigenvalues[2],
    )

    # The largest eigenvalue direction is the long (proximal-distal) axis.
    # We want that mapped to Z.
    # Second largest -> X, smallest -> Y
    # eigenvectors columns are already sorted descending by eigenvalue
    rotation = np.eye(3)
    rotation[:, 2] = eigenvectors[:, 0]  # long axis -> Z
    rotation[:, 0] = eigenvectors[:, 1]  # medium axis -> X
    rotation[:, 1] = eigenvectors[:, 2]  # short axis -> Y

    rotation = _ensure_right_handed(rotation)

    # Build 4x4 transform: translate to origin, then rotate
    transform = np.eye(4)
    # First center at origin
    mesh.vertices -= centroid

    # Then rotate so PCA axes align to XYZ
    # We want to rotate FROM the PCA frame TO the standard frame
    # rotation columns are PCA axes in the original frame
    # So the inverse rotation maps PCA axes to standard axes
    rot_matrix = rotation.T  # inverse of orthogonal matrix = transpose
    mesh.vertices = (rot_matrix @ mesh.vertices.T).T

    # Build the full transform for the report
    transform[:3, :3] = rot_matrix
    transform[:3, 3] = -rot_matrix @ centroid

    # Ensure Z points "up" (proximal end at +Z)
    # Heuristic: the proximal end of a prosthesis is typically wider
    z_coords = mesh.vertices[:, 2]
    z_mid = (z_coords.min() + z_coords.max()) / 2.0
    upper_verts = mesh.vertices[z_coords > z_mid]
    lower_verts = mesh.vertices[z_coords <= z_mid]

    if len(upper_verts) > 0 and len(lower_verts) > 0:
        upper_spread = np.std(upper_verts[:, :2], axis=0).mean()
        lower_spread = np.std(lower_verts[:, :2], axis=0).mean()

        if lower_spread > upper_spread:
            # Wider end is at bottom; flip so proximal (wider) is at +Z
            mesh.vertices[:, 2] = -mesh.vertices[:, 2]
            transform[:3, :3] = np.diag([1, 1, -1]) @ transform[:3, :3]
            logger.info("Flipped Z axis so proximal end is at +Z")

    # ---- Side detection ----
    if config.side == "auto":
        detected_side = _detect_side(mesh)
        logger.info("Auto-detected side: %s", detected_side)
    else:
        detected_side = config.side

    # ---- Compute final stats ----
    bounds = mesh.bounds
    extent = bounds[1] - bounds[0]

    report = AlignmentReport(
        principal_axes=eigenvectors.T,  # rows = axes
        center_of_mass=centroid,
        bounding_box_extent=extent,
        detected_side=detected_side,
        transform_applied=transform,
    )

    logger.info(
        "Alignment complete. Extent: [%.1f, %.1f, %.1f] mm, side: %s",
        extent[0], extent[1], extent[2], detected_side,
    )

    return mesh, report

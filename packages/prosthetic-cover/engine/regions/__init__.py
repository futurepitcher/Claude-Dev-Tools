"""
Region mapping module.

Divides the prosthesis surface into named zones that control where
aesthetic features, attachments, and clearances are applied.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.utils import faces_in_z_range

logger = logging.getLogger(__name__)


@dataclass
class RegionMap:
    """Named zones on the mesh surface, stored as sets of face indices.

    Zones:
        coverage:       Faces that will be covered by the shell.
        no_go:          Faces where no features may be placed (e.g., over joints, sensors).
        transition:     Faces at the boundary between covered and uncovered areas.
        joint:          Faces near articulation points (high curvature).
        service_access: Faces that must remain accessible (e.g., adjustment screws).
    """

    total_faces: int = 0
    coverage: set[int] = field(default_factory=set)
    no_go: set[int] = field(default_factory=set)
    transition: set[int] = field(default_factory=set)
    joint: set[int] = field(default_factory=set)
    service_access: set[int] = field(default_factory=set)

    @property
    def aesthetic_zone(self) -> set[int]:
        """Faces eligible for aesthetic features (coverage minus exclusions)."""
        return self.coverage - self.no_go - self.joint - self.service_access

    def all_zone_names(self) -> list[str]:
        return ["coverage", "no_go", "transition", "joint", "service_access"]


@dataclass
class RegionReport:
    """Summary of region marking results."""

    total_faces: int
    coverage_faces: int
    no_go_faces: int
    transition_faces: int
    joint_faces: int
    service_access_faces: int
    aesthetic_faces: int
    warnings: list[str] = field(default_factory=list)


def _detect_high_curvature_faces(
    mesh: trimesh.Trimesh, curvature_threshold: float = 0.15
) -> np.ndarray:
    """Detect faces in high-curvature regions using the angle between adjacent face normals.

    Returns an array of face indices where curvature exceeds the threshold.
    """
    face_normals = mesh.face_normals
    face_adjacency = mesh.face_adjacency  # (n, 2) pairs of adjacent face indices

    # Compute the angle between normals of adjacent faces
    n1 = face_normals[face_adjacency[:, 0]]
    n2 = face_normals[face_adjacency[:, 1]]

    # Dot product, clamped for numerical safety
    dots = np.clip(np.sum(n1 * n2, axis=1), -1.0, 1.0)
    angles = np.arccos(dots)  # radians

    # Mark faces that participate in a high-angle adjacency
    high_angle_mask = angles > curvature_threshold
    high_curv_pairs = face_adjacency[high_angle_mask]
    high_curv_faces = np.unique(high_curv_pairs.flatten())

    return high_curv_faces


def _detect_joint_zones(
    mesh: trimesh.Trimesh, config: CoverConfig, curvature_faces: np.ndarray
) -> set[int]:
    """Identify joint zones by combining curvature with expected anatomical locations.

    For transtibial prostheses, the knee region is near the proximal end (+Z).
    For transfemoral, the knee is roughly mid-shaft and the hip is proximal.
    """
    bounds = mesh.bounds
    z_min, z_max = bounds[0, 2], bounds[1, 2]
    z_range = z_max - z_min

    if z_range <= 0:
        return set()

    # Expected joint z-ranges (as fraction of total height)
    if config.prosthesis_type == "transtibial":
        # Knee region is in the top ~20% of the segment
        joint_z_min = z_min + 0.80 * z_range
        joint_z_max = z_max
    else:
        # Transfemoral: knee region at ~20-40% from distal, hip at top ~15%
        joint_z_min = z_min + 0.55 * z_range
        joint_z_max = z_max

    # Faces near expected joint locations
    positional_joint_faces = set(faces_in_z_range(mesh, joint_z_min, joint_z_max).tolist())

    # Combine with high-curvature faces that are near joint locations
    curvature_set = set(curvature_faces.tolist())
    joint_faces = positional_joint_faces & curvature_set

    # If very few curvature matches, use positional estimate alone
    if len(joint_faces) < 10 and len(positional_joint_faces) > 0:
        joint_faces = positional_joint_faces

    return joint_faces


def _compute_transition_faces(
    mesh: trimesh.Trimesh, coverage: set[int], band_width_mm: float = 5.0
) -> set[int]:
    """Find faces at the boundary of the coverage zone.

    Selects faces within `band_width_mm` of the coverage boundary.
    """
    if not coverage:
        return set()

    all_faces = set(range(len(mesh.faces)))
    non_coverage = all_faces - coverage

    if not non_coverage:
        return set()

    # Find faces adjacent to the boundary
    adjacency = mesh.face_adjacency
    coverage_arr = np.array(list(coverage))
    non_coverage_arr = np.array(list(non_coverage))

    # Build adjacency lookup
    is_coverage = np.zeros(len(mesh.faces), dtype=bool)
    is_coverage[coverage_arr] = True

    # Boundary faces: coverage faces adjacent to non-coverage faces
    boundary_faces = set()
    for pair in adjacency:
        f0, f1 = int(pair[0]), int(pair[1])
        if is_coverage[f0] != is_coverage[f1]:
            if is_coverage[f0]:
                boundary_faces.add(f0)
            else:
                boundary_faces.add(f1)

    # Expand boundary outward by one ring of adjacency for a smoother transition
    transition = set(boundary_faces)
    current_ring = boundary_faces
    for _ in range(2):  # 2 rings of expansion
        next_ring: set[int] = set()
        for pair in adjacency:
            f0, f1 = int(pair[0]), int(pair[1])
            if f0 in current_ring and f1 not in transition and is_coverage[f1]:
                next_ring.add(f1)
            elif f1 in current_ring and f0 not in transition and is_coverage[f0]:
                next_ring.add(f0)
        transition.update(next_ring)
        current_ring = next_ring

    return transition


def mark_regions(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> tuple[RegionMap, RegionReport]:
    """Automatically mark regions on the mesh surface.

    Args:
        mesh: Aligned, cleaned mesh.
        config: Pipeline configuration.

    Returns:
        Tuple of (region map, region report).
    """
    n_faces = len(mesh.faces)
    region_map = RegionMap(total_faces=n_faces)
    warnings: list[str] = []

    bounds = mesh.bounds
    z_min, z_max = bounds[0, 2], bounds[1, 2]
    z_range = z_max - z_min

    # ---- Coverage zone based on coverage_extent ----
    if config.coverage_extent == "full":
        coverage_z_min = z_min
        coverage_z_max = z_max
    elif config.coverage_extent == "partial":
        # Cover central 70% of the segment
        coverage_z_min = z_min + 0.15 * z_range
        coverage_z_max = z_max - 0.15 * z_range
    else:  # minimal
        # Cover central 40%
        coverage_z_min = z_min + 0.30 * z_range
        coverage_z_max = z_max - 0.30 * z_range

    coverage_indices = faces_in_z_range(mesh, coverage_z_min, coverage_z_max)
    region_map.coverage = set(coverage_indices.tolist())

    if len(region_map.coverage) == 0:
        warnings.append("No faces fall within the coverage zone. Check mesh alignment.")

    # ---- Joint zones ----
    high_curv_faces = _detect_high_curvature_faces(mesh)
    region_map.joint = _detect_joint_zones(mesh, config, high_curv_faces)
    logger.info("Detected %d joint-zone faces", len(region_map.joint))

    # ---- Transition zones ----
    region_map.transition = _compute_transition_faces(mesh, region_map.coverage)

    # ---- Log summary ----
    aesthetic_count = len(region_map.aesthetic_zone)
    logger.info(
        "Region marking complete: coverage=%d, joint=%d, transition=%d, aesthetic=%d",
        len(region_map.coverage),
        len(region_map.joint),
        len(region_map.transition),
        aesthetic_count,
    )

    report = RegionReport(
        total_faces=n_faces,
        coverage_faces=len(region_map.coverage),
        no_go_faces=len(region_map.no_go),
        transition_faces=len(region_map.transition),
        joint_faces=len(region_map.joint),
        service_access_faces=len(region_map.service_access),
        aesthetic_faces=aesthetic_count,
        warnings=warnings,
    )

    return region_map, report


def mark_no_go_zone(region_map: RegionMap, face_indices: set[int], zone_name: str = "") -> None:
    """Manually mark faces as no-go (excluded from aesthetic features).

    Args:
        region_map: Existing region map to modify in place.
        face_indices: Face indices to add to the no-go zone.
        zone_name: Optional label for logging.
    """
    region_map.no_go.update(face_indices)
    logger.info(
        "Added %d faces to no-go zone%s (total no-go: %d)",
        len(face_indices),
        f" ({zone_name})" if zone_name else "",
        len(region_map.no_go),
    )


def mark_coverage_zone(
    region_map: RegionMap, mesh: trimesh.Trimesh, z_min: float, z_max: float
) -> None:
    """Override the coverage zone to a specific Z range.

    Args:
        region_map: Existing region map to modify in place.
        mesh: The aligned mesh.
        z_min: Lower Z bound (mm).
        z_max: Upper Z bound (mm).
    """
    coverage_indices = faces_in_z_range(mesh, z_min, z_max)
    region_map.coverage = set(coverage_indices.tolist())
    logger.info(
        "Coverage zone overridden to Z=[%.1f, %.1f] mm: %d faces",
        z_min, z_max, len(region_map.coverage),
    )


def get_region_stats(region_map: RegionMap) -> dict[str, int]:
    """Return a dict of zone-name -> face-count."""
    return {
        "total_faces": region_map.total_faces,
        "coverage": len(region_map.coverage),
        "no_go": len(region_map.no_go),
        "transition": len(region_map.transition),
        "joint": len(region_map.joint),
        "service_access": len(region_map.service_access),
        "aesthetic": len(region_map.aesthetic_zone),
    }

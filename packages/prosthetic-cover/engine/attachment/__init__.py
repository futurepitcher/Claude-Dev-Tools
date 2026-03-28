"""
Attachment feature module.

Generates snap clips, split lines, and other mechanical attachment
geometry on the prosthetic cover shell.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.regions import RegionMap
from engine.utils import faces_in_z_range, vertex_indices_for_faces

logger = logging.getLogger(__name__)


@dataclass
class AttachmentPoint:
    """A single attachment feature location."""

    position: np.ndarray  # (3,) world coordinates
    normal: np.ndarray  # (3,) outward surface normal at this point
    attachment_type: str
    label: str = ""


@dataclass
class AttachmentReport:
    """Results from the attachment stage."""

    attachment_count: int
    attachment_positions: list[AttachmentPoint]
    split_lines: list[np.ndarray]  # list of (N, 3) polylines
    warnings: list[str] = field(default_factory=list)


def _find_attachment_candidates(
    mesh: trimesh.Trimesh,
    region_map: RegionMap,
    n_points: int = 4,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Find suitable positions for attachment features.

    Selects points in the coverage zone that are:
    - Not in no-go, joint, or service-access zones
    - Distributed around the circumference
    - Near the proximal and distal edges of coverage

    Returns list of (position, normal) tuples.
    """
    eligible_faces = region_map.coverage - region_map.no_go - region_map.joint - region_map.service_access

    if not eligible_faces:
        return []

    face_list = np.array(list(eligible_faces))
    centroids = mesh.triangles_center[face_list]
    face_normals = mesh.face_normals[face_list]

    # Split into proximal and distal bands
    z_vals = centroids[:, 2]
    z_min, z_max = z_vals.min(), z_vals.max()
    z_range = z_max - z_min

    if z_range < 1.0:
        return []

    # Proximal band (top 15%)
    proximal_mask = z_vals > (z_max - 0.15 * z_range)
    # Distal band (bottom 15%)
    distal_mask = z_vals < (z_min + 0.15 * z_range)

    candidates: list[tuple[np.ndarray, np.ndarray]] = []

    for band_mask, label in [(proximal_mask, "proximal"), (distal_mask, "distal")]:
        band_centroids = centroids[band_mask]
        band_normals = face_normals[band_mask]

        if len(band_centroids) < 2:
            continue

        # Distribute points around the circumference using angular sectors
        band_center = band_centroids.mean(axis=0)
        angles = np.arctan2(
            band_centroids[:, 1] - band_center[1],
            band_centroids[:, 0] - band_center[0],
        )

        n_per_band = max(1, n_points // 2)
        sector_size = 2.0 * np.pi / n_per_band

        for sector in range(n_per_band):
            sector_min = -np.pi + sector * sector_size
            sector_max = sector_min + sector_size
            in_sector = (angles >= sector_min) & (angles < sector_max)

            if not np.any(in_sector):
                continue

            sector_centroids = band_centroids[in_sector]
            sector_normals = band_normals[in_sector]

            # Pick the point with the most outward-facing normal (largest XY component)
            xy_magnitude = np.linalg.norm(sector_normals[:, :2], axis=1)
            best_idx = np.argmax(xy_magnitude)

            candidates.append((sector_centroids[best_idx], sector_normals[best_idx]))

    return candidates


def _create_snap_clip_geometry(
    position: np.ndarray,
    normal: np.ndarray,
    clip_width: float = 8.0,
    clip_height: float = 5.0,
    clip_depth: float = 3.0,
) -> trimesh.Trimesh:
    """Generate a simple snap-clip boss as a box primitive.

    The clip is oriented so that the depth direction aligns with the
    surface normal at the attachment point.

    Args:
        position: Attachment point in world coordinates.
        normal: Outward surface normal.
        clip_width: Width of the clip base (mm).
        clip_height: Height along the shell surface (mm).
        clip_depth: Depth protruding outward from the surface (mm).

    Returns:
        A trimesh box representing the clip boss.
    """
    # Create a box centered at origin
    clip = trimesh.creation.box(extents=[clip_width, clip_height, clip_depth])

    # Build a rotation that aligns Z+ with the surface normal
    z_axis = np.array([0.0, 0.0, 1.0])
    normal_unit = normal / (np.linalg.norm(normal) + 1e-12)

    # Rotation from z_axis to normal_unit
    v = np.cross(z_axis, normal_unit)
    s = np.linalg.norm(v)
    c = np.dot(z_axis, normal_unit)

    if s < 1e-8:
        # normal is parallel (or anti-parallel) to Z
        rotation = np.eye(4)
        if c < 0:
            rotation[:3, :3] = np.diag([1, -1, -1])
    else:
        vx = np.array([
            [0, -v[2], v[1]],
            [v[2], 0, -v[0]],
            [-v[1], v[0], 0],
        ])
        rot_3x3 = np.eye(3) + vx + (vx @ vx) * ((1 - c) / (s * s))
        rotation = np.eye(4)
        rotation[:3, :3] = rot_3x3

    # Translate so the inner face sits on the surface
    offset = normal_unit * (clip_depth / 2.0)
    translation = np.eye(4)
    translation[:3, 3] = position + offset

    clip.apply_transform(rotation)
    clip.apply_transform(translation)

    return clip


def _compute_split_line(
    mesh: trimesh.Trimesh,
    strategy: str,
) -> list[np.ndarray]:
    """Compute split-line polylines for the given strategy.

    Returns a list of polylines, each an (N, 3) array of points
    tracing the split on the mesh surface.
    """
    bounds = mesh.bounds
    center = (bounds[0] + bounds[1]) / 2.0
    z_min, z_max = bounds[0, 2], bounds[1, 2]

    split_lines: list[np.ndarray] = []

    if strategy == "medial_lateral":
        # Vertical split along the sagittal plane (Y-Z plane at x=center)
        origin = np.array([center[0], center[1], z_min])
        direction = np.array([1.0, 0.0, 0.0])
        normal = direction
        plane_origin = center.copy()

        try:
            path = mesh.section(plane_origin=plane_origin, plane_normal=normal)
            if path is not None:
                for entity in path.entities:
                    points = path.vertices[entity.points]
                    split_lines.append(points)
        except Exception as exc:
            logger.warning("Could not compute medial-lateral split: %s", exc)

    elif strategy == "anterior_posterior":
        # Vertical split along the coronal plane (X-Z plane at y=center)
        normal = np.array([0.0, 1.0, 0.0])
        try:
            path = mesh.section(plane_origin=center, plane_normal=normal)
            if path is not None:
                for entity in path.entities:
                    points = path.vertices[entity.points]
                    split_lines.append(points)
        except Exception as exc:
            logger.warning("Could not compute anterior-posterior split: %s", exc)

    elif strategy == "three_piece":
        # Three splits at 120-degree intervals around the Z axis
        for angle_deg in [0, 120, 240]:
            angle_rad = np.radians(angle_deg)
            normal = np.array([np.cos(angle_rad), np.sin(angle_rad), 0.0])
            try:
                path = mesh.section(plane_origin=center, plane_normal=normal)
                if path is not None:
                    for entity in path.entities:
                        points = path.vertices[entity.points]
                        split_lines.append(points)
            except Exception as exc:
                logger.warning("Could not compute split at %d deg: %s", angle_deg, exc)

    return split_lines


def add_attachments(
    shell_mesh: trimesh.Trimesh,
    config: CoverConfig,
    region_map: RegionMap,
) -> tuple[trimesh.Trimesh, AttachmentReport]:
    """Add attachment features and split lines to the shell.

    Args:
        shell_mesh: The styled shell mesh.
        config: Pipeline configuration.
        region_map: Region definitions.

    Returns:
        Tuple of (mesh with attachments, attachment report).
    """
    warnings: list[str] = []
    result = shell_mesh.copy()

    # ---- Attachment points ----
    candidates = _find_attachment_candidates(result, region_map)
    attachment_points: list[AttachmentPoint] = []

    if not candidates:
        warnings.append("No suitable attachment positions found. Check coverage and no-go zones.")
    else:
        clip_meshes: list[trimesh.Trimesh] = []

        for i, (pos, norm) in enumerate(candidates):
            ap = AttachmentPoint(
                position=pos,
                normal=norm,
                attachment_type=config.attachment_type,
                label=f"clip_{i}",
            )
            attachment_points.append(ap)

            if config.attachment_type == "snap_clip":
                clip = _create_snap_clip_geometry(pos, norm)
                clip_meshes.append(clip)

        # Merge clip geometry into the shell
        if clip_meshes:
            all_meshes = [result] + clip_meshes
            result = trimesh.util.concatenate(all_meshes)
            logger.info("Added %d snap clip features", len(clip_meshes))

    # ---- Split lines ----
    split_lines: list[np.ndarray] = []
    if config.split_strategy != "none":
        split_lines = _compute_split_line(shell_mesh, config.split_strategy)
        if not split_lines:
            warnings.append(
                f"Could not compute split lines for strategy '{config.split_strategy}'"
            )
        else:
            logger.info(
                "Computed %d split lines for strategy '%s'",
                len(split_lines), config.split_strategy,
            )

    report = AttachmentReport(
        attachment_count=len(attachment_points),
        attachment_positions=attachment_points,
        split_lines=split_lines,
        warnings=warnings,
    )

    logger.info("Attachment stage complete: %d attachments", len(attachment_points))

    return result, report

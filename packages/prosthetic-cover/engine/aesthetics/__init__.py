"""
Aesthetics module — apply visual style to the prosthetic cover shell.

Supports multiple style families: smooth, faceted, perforated, lattice,
organic, and panelized.  Each style modifies the shell geometry while
respecting no-go zones and minimum feature size constraints.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.regions import RegionMap
from engine.utils import laplacian_smooth, vertex_indices_for_faces

logger = logging.getLogger(__name__)


@dataclass
class AestheticsReport:
    """Results from the aesthetics stage."""

    style_applied: str
    features_count: int
    min_feature_size_actual_mm: float
    faces_modified: int
    warnings: list[str] = field(default_factory=list)


class StyleEngine:
    """Applies aesthetic treatments to a shell mesh.

    Each method receives the shell mesh and returns a modified copy.
    Region maps ensure features respect no-go zones.
    """

    def __init__(self, config: CoverConfig, region_map: RegionMap) -> None:
        self.config = config
        self.region_map = region_map

    def apply(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Dispatch to the correct style method based on config."""
        dispatch = {
            "smooth": self.smooth_style,
            "faceted": self.faceted_style,
            "perforated": self.perforated_style,
            "lattice": self.lattice_style,
            "organic": self.organic_style,
            "panelized": self.panelized_style,
        }

        style = self.config.style_family
        if style not in dispatch:
            raise ValueError(
                f"Unknown style_family '{style}'. Available: {list(dispatch.keys())}"
            )

        logger.info("Applying '%s' style", style)
        return dispatch[style](mesh)

    # ------------------------------------------------------------------
    # Smooth style
    # ------------------------------------------------------------------

    def smooth_style(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Laplacian smooth with subtle contour lines via vertex displacement.

        Creates gentle undulations along the Z axis for visual interest.
        """
        result = laplacian_smooth(mesh, iterations=2, lamb=0.3)

        # Add subtle contour-line displacement
        vertices = result.vertices.copy()
        z = vertices[:, 2]
        z_norm = (z - z.min()) / (z.max() - z.min() + 1e-8)

        # Sinusoidal radial displacement for contour effect
        frequency = 15.0  # number of contour bands
        amplitude = 0.15  # mm displacement
        normals = np.array(result.vertex_normals)
        displacement = amplitude * np.sin(2.0 * np.pi * frequency * z_norm)

        # Only apply to aesthetic zone vertices
        aesthetic_faces = self.region_map.aesthetic_zone
        if aesthetic_faces:
            aesthetic_verts = vertex_indices_for_faces(
                result, np.array(list(aesthetic_faces))
            )
            mask = np.zeros(len(vertices), dtype=bool)
            mask[aesthetic_verts] = True
            vertices[mask] += normals[mask] * displacement[mask, np.newaxis]

        result = trimesh.Trimesh(
            vertices=vertices, faces=result.faces.copy(), process=False
        )

        return result, AestheticsReport(
            style_applied="smooth",
            features_count=int(frequency),
            min_feature_size_actual_mm=amplitude * 2,
            faces_modified=len(aesthetic_faces),
        )

    # ------------------------------------------------------------------
    # Faceted style
    # ------------------------------------------------------------------

    def faceted_style(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Reduce face count in the aesthetic zone for a low-poly look."""
        target_faces = max(200, len(mesh.faces) // 8)

        try:
            result = mesh.simplify_quadric_decimation(target_faces)
        except Exception:
            logger.warning(
                "Quadric decimation unavailable; falling back to vertex clustering"
            )
            # Fallback: use a coarse voxel pitch to approximate faceting
            pitch = float(np.max(mesh.bounding_box.extents)) / 30.0
            result = mesh.voxelized(pitch).marching_cubes
            if not isinstance(result, trimesh.Trimesh):
                result = mesh.copy()

        return result, AestheticsReport(
            style_applied="faceted",
            features_count=len(result.faces),
            min_feature_size_actual_mm=float(
                np.sqrt(np.max(result.area_faces)) * 2
            ) if len(result.faces) > 0 else 0.0,
            faces_modified=len(result.faces),
        )

    # ------------------------------------------------------------------
    # Perforated style
    # ------------------------------------------------------------------

    def perforated_style(
        self, mesh: trimesh.Trimesh
    ) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Cut patterned holes through the shell surface.

        Supports circle, hex, diamond, voronoi, and organic patterns.
        Respects no-go zones and minimum bridge width.
        """
        config = self.config
        density = config.perforation_density
        shape = config.perforation_shape
        min_bridge = config.min_bridge_width_mm
        min_feature = config.min_feature_size_mm

        # Determine perforation placement grid in the aesthetic zone
        aesthetic_faces = self.region_map.aesthetic_zone
        if not aesthetic_faces:
            logger.warning("No aesthetic zone faces for perforation")
            return mesh.copy(), AestheticsReport(
                style_applied="perforated",
                features_count=0,
                min_feature_size_actual_mm=0.0,
                faces_modified=0,
                warnings=["No aesthetic zone available for perforations"],
            )

        face_list = np.array(list(aesthetic_faces))
        centroids = mesh.triangles_center[face_list]

        # Compute bounding box of aesthetic zone
        az_min = centroids.min(axis=0)
        az_max = centroids.max(axis=0)
        az_extent = az_max - az_min

        # Hole size scales with density: higher density = more holes, smaller spacing
        hole_radius = max(min_feature, 2.0 + (1.0 - density) * 4.0)
        spacing = hole_radius * 2 + min_bridge

        # Generate hole center grid
        hole_centers = _generate_pattern_centers(
            az_min, az_max, spacing, shape
        )

        if len(hole_centers) == 0:
            return mesh.copy(), AestheticsReport(
                style_applied="perforated",
                features_count=0,
                min_feature_size_actual_mm=0.0,
                faces_modified=0,
                warnings=["Aesthetic zone too small for perforations at current settings"],
            )

        # Remove faces whose centroid falls inside a hole
        faces_to_remove: set[int] = set()
        for center in hole_centers:
            if shape in ("circle", "voronoi", "organic"):
                dists = np.linalg.norm(centroids[:, :2] - center[:2], axis=1)
                mask = dists < hole_radius
            elif shape == "hex":
                # Hexagonal distance metric
                dx = np.abs(centroids[:, 0] - center[0])
                dy = np.abs(centroids[:, 1] - center[1])
                mask = (dx < hole_radius) & (dy < hole_radius * 0.866)
            elif shape == "diamond":
                dx = np.abs(centroids[:, 0] - center[0])
                dy = np.abs(centroids[:, 1] - center[1])
                mask = (dx + dy) < hole_radius * 1.2
            else:
                dists = np.linalg.norm(centroids[:, :2] - center[:2], axis=1)
                mask = dists < hole_radius

            hit_indices = face_list[mask]
            faces_to_remove.update(hit_indices.tolist())

        # Build a keep mask
        keep_mask = np.ones(len(mesh.faces), dtype=bool)
        if faces_to_remove:
            keep_mask[np.array(list(faces_to_remove))] = False

        result = mesh.copy()
        result.update_faces(keep_mask)
        result.remove_unreferenced_vertices()

        actual_min_feature = min_bridge  # approximate
        perf_count = len(hole_centers)

        logger.info(
            "Perforated style: %d holes (%s, r=%.1f mm), removed %d faces",
            perf_count, shape, hole_radius, len(faces_to_remove),
        )

        return result, AestheticsReport(
            style_applied="perforated",
            features_count=perf_count,
            min_feature_size_actual_mm=actual_min_feature,
            faces_modified=len(faces_to_remove),
        )

    # ------------------------------------------------------------------
    # Lattice style
    # ------------------------------------------------------------------

    def lattice_style(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Generate a lattice pattern by removing faces in a grid pattern.

        Keeps faces along grid lines, removes the rest in the aesthetic zone.
        """
        aesthetic_faces = self.region_map.aesthetic_zone
        if not aesthetic_faces:
            return mesh.copy(), AestheticsReport(
                style_applied="lattice",
                features_count=0,
                min_feature_size_actual_mm=0.0,
                faces_modified=0,
            )

        face_list = np.array(list(aesthetic_faces))
        centroids = mesh.triangles_center[face_list]

        beam_width = max(self.config.min_bridge_width_mm, 2.0)
        cell_size = beam_width * 3.0  # cell = beam + opening + beam

        # Keep faces that lie on lattice beams (within beam_width of grid lines)
        x_mod = np.mod(centroids[:, 0], cell_size)
        y_mod = np.mod(centroids[:, 1], cell_size)

        on_x_beam = x_mod < beam_width
        on_y_beam = y_mod < beam_width
        on_lattice = on_x_beam | on_y_beam

        faces_to_remove = face_list[~on_lattice]

        keep_mask = np.ones(len(mesh.faces), dtype=bool)
        keep_mask[faces_to_remove] = False

        result = mesh.copy()
        result.update_faces(keep_mask)
        result.remove_unreferenced_vertices()

        return result, AestheticsReport(
            style_applied="lattice",
            features_count=int(np.sum(~on_lattice)),
            min_feature_size_actual_mm=beam_width,
            faces_modified=len(faces_to_remove),
        )

    # ------------------------------------------------------------------
    # Organic style
    # ------------------------------------------------------------------

    def organic_style(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Displacement-based organic surface modulation.

        Applies Perlin-like noise displacement along vertex normals
        in the aesthetic zone to create an organic, flowing surface.
        """
        aesthetic_faces = self.region_map.aesthetic_zone
        if not aesthetic_faces:
            return mesh.copy(), AestheticsReport(
                style_applied="organic",
                features_count=0,
                min_feature_size_actual_mm=0.0,
                faces_modified=0,
            )

        aesthetic_verts = vertex_indices_for_faces(
            mesh, np.array(list(aesthetic_faces))
        )

        vertices = mesh.vertices.copy()
        normals = np.array(mesh.vertex_normals)

        # Multi-octave noise displacement using trigonometric approximation
        amplitude = 0.8  # mm
        frequency_base = 0.05  # cycles per mm

        displacement = np.zeros(len(vertices))
        for octave in range(3):
            freq = frequency_base * (2 ** octave)
            amp = amplitude / (2 ** octave)
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
            # Pseudo-noise from combining sin/cos at different frequencies
            noise = (
                np.sin(freq * x * 6.28 + 1.7)
                * np.cos(freq * y * 6.28 + 2.3)
                * np.sin(freq * z * 6.28 + 0.9)
            )
            displacement += amp * noise

        # Apply only to aesthetic zone vertices
        mask = np.zeros(len(vertices), dtype=bool)
        mask[aesthetic_verts] = True
        vertices[mask] += normals[mask] * displacement[mask, np.newaxis]

        result = trimesh.Trimesh(
            vertices=vertices, faces=mesh.faces.copy(), process=False
        )

        return result, AestheticsReport(
            style_applied="organic",
            features_count=3,  # octaves
            min_feature_size_actual_mm=amplitude,
            faces_modified=len(aesthetic_faces),
        )

    # ------------------------------------------------------------------
    # Panelized style
    # ------------------------------------------------------------------

    def panelized_style(
        self, mesh: trimesh.Trimesh
    ) -> tuple[trimesh.Trimesh, AestheticsReport]:
        """Split the surface into panels with reveal gaps.

        Creates visible seam lines by removing thin strips of faces
        along panel boundaries.
        """
        aesthetic_faces = self.region_map.aesthetic_zone
        if not aesthetic_faces:
            return mesh.copy(), AestheticsReport(
                style_applied="panelized",
                features_count=0,
                min_feature_size_actual_mm=0.0,
                faces_modified=0,
            )

        face_list = np.array(list(aesthetic_faces))
        centroids = mesh.triangles_center[face_list]

        # Panel layout: divide into horizontal and vertical bands
        bounds = mesh.bounds
        z_range = bounds[1, 2] - bounds[0, 2]
        n_horizontal_panels = max(2, int(z_range / 80.0))
        panel_height = z_range / n_horizontal_panels

        gap_width = max(self.config.min_feature_size_mm, 1.0)  # mm

        # Remove faces along panel boundary lines
        faces_to_remove: set[int] = set()
        panel_count = 0

        for i in range(1, n_horizontal_panels):
            z_line = bounds[0, 2] + i * panel_height
            z_dist = np.abs(centroids[:, 2] - z_line)
            in_gap = z_dist < (gap_width / 2.0)
            faces_to_remove.update(face_list[in_gap].tolist())
            panel_count += 1

        # Also add a vertical split
        x_mid = (bounds[0, 0] + bounds[1, 0]) / 2.0
        x_dist = np.abs(centroids[:, 0] - x_mid)
        in_gap = x_dist < (gap_width / 2.0)
        faces_to_remove.update(face_list[in_gap].tolist())
        panel_count += 1

        keep_mask = np.ones(len(mesh.faces), dtype=bool)
        if faces_to_remove:
            keep_mask[np.array(list(faces_to_remove))] = False

        result = mesh.copy()
        result.update_faces(keep_mask)
        result.remove_unreferenced_vertices()

        return result, AestheticsReport(
            style_applied="panelized",
            features_count=panel_count,
            min_feature_size_actual_mm=gap_width,
            faces_modified=len(faces_to_remove),
        )


def _generate_pattern_centers(
    bbox_min: np.ndarray,
    bbox_max: np.ndarray,
    spacing: float,
    shape: str,
) -> np.ndarray:
    """Generate a 2D grid of hole centers within a bounding box.

    For hex patterns, every other row is offset by half the spacing.
    For voronoi/organic, centers are jittered from a regular grid.
    """
    x_range = np.arange(bbox_min[0] + spacing, bbox_max[0], spacing)
    y_range = np.arange(bbox_min[1] + spacing, bbox_max[1], spacing)

    if len(x_range) == 0 or len(y_range) == 0:
        return np.array([]).reshape(0, 3)

    centers = []
    for i, y in enumerate(y_range):
        x_offset = (spacing * 0.5) if (shape == "hex" and i % 2 == 1) else 0.0
        for x in x_range:
            cx = x + x_offset
            cy = y
            cz = (bbox_min[2] + bbox_max[2]) / 2.0
            centers.append([cx, cy, cz])

    centers = np.array(centers)

    # Jitter for voronoi / organic patterns
    if shape in ("voronoi", "organic"):
        jitter_scale = spacing * 0.25
        rng = np.random.default_rng(42)  # deterministic for reproducibility
        centers[:, :2] += rng.uniform(-jitter_scale, jitter_scale, size=(len(centers), 2))

    return centers


def apply_style(
    shell_mesh: trimesh.Trimesh,
    config: CoverConfig,
    region_map: RegionMap,
) -> tuple[trimesh.Trimesh, AestheticsReport]:
    """Top-level function to apply the configured aesthetic style.

    Args:
        shell_mesh: The generated shell mesh.
        config: Pipeline configuration.
        region_map: Region definitions.

    Returns:
        Tuple of (styled mesh, aesthetics report).
    """
    engine = StyleEngine(config, region_map)
    return engine.apply(shell_mesh)

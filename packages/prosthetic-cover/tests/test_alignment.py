"""Tests for engine.alignment -- PCA alignment, centering, and side detection."""

import os
import sys

import numpy as np
import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.config import CoverConfig
from engine.alignment import align_to_anatomical_frame, AlignmentReport


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_elongated_cylinder(radius=40.0, height=350.0, sections=32):
    """Create an elongated cylinder mimicking a prosthesis pylon.

    The long axis (height) should be detected as the principal axis by PCA.
    """
    return trimesh.creation.cylinder(radius=radius, height=height, sections=sections)


def _make_tilted_cylinder(radius=40.0, height=350.0):
    """Create a cylinder tilted 45 degrees from the Z axis.

    This tests whether PCA alignment can recover the long axis.
    """
    mesh = _make_elongated_cylinder(radius=radius, height=height)
    # Rotate 45 degrees around the X axis
    angle = np.pi / 4
    rotation = trimesh.transformations.rotation_matrix(angle, [1, 0, 0])
    mesh.apply_transform(rotation)
    return mesh


def _make_offset_cylinder(radius=40.0, height=350.0):
    """Create a cylinder offset from the origin."""
    mesh = _make_elongated_cylinder(radius=radius, height=height)
    mesh.vertices += np.array([100.0, -50.0, 200.0])
    return mesh


def _make_asymmetric_mesh():
    """Create a mesh that is asymmetric about the X axis for side detection.

    A cylinder with an extra bulge on one side simulates the anatomical
    asymmetry of a leg (calf muscle is posterior, shin is anterior).
    """
    base = _make_elongated_cylinder(radius=40.0, height=350.0)

    # Add a sphere on the +X side to create asymmetry
    bulge = trimesh.creation.icosphere(radius=25.0, subdivisions=2)
    bulge.vertices += np.array([45.0, 0.0, 0.0])  # offset to +X side

    combined = trimesh.util.concatenate([base, bulge])
    return combined


# ---------------------------------------------------------------------------
# PCA alignment on elongated meshes
# ---------------------------------------------------------------------------

class TestPCAAlignment:
    def test_aligned_cylinder_long_axis_is_z(self):
        """After alignment, the long axis of the cylinder should be along Z."""
        mesh = _make_elongated_cylinder()
        config = CoverConfig()
        aligned, report = align_to_anatomical_frame(mesh, config)

        extent = aligned.bounding_box.extents
        # Z (index 2) should be the largest extent
        assert np.argmax(extent) == 2, (
            f"Expected Z to be longest axis, got extents {extent}"
        )

    def test_tilted_cylinder_recovers_alignment(self):
        """A tilted cylinder should be re-aligned so its long axis is Z."""
        mesh = _make_tilted_cylinder()
        config = CoverConfig()
        aligned, report = align_to_anatomical_frame(mesh, config)

        extent = aligned.bounding_box.extents
        assert np.argmax(extent) == 2, (
            f"Expected Z to be longest after alignment, got extents {extent}"
        )

    def test_alignment_preserves_vertex_count(self):
        mesh = _make_elongated_cylinder()
        original_count = len(mesh.vertices)
        config = CoverConfig()
        aligned, _ = align_to_anatomical_frame(mesh, config)
        assert len(aligned.vertices) == original_count

    def test_alignment_preserves_face_count(self):
        mesh = _make_elongated_cylinder()
        original_count = len(mesh.faces)
        config = CoverConfig()
        aligned, _ = align_to_anatomical_frame(mesh, config)
        assert len(aligned.faces) == original_count

    def test_alignment_preserves_volume(self):
        """Rigid transformation should preserve mesh volume."""
        mesh = _make_elongated_cylinder()
        original_volume = mesh.volume
        config = CoverConfig()
        aligned, _ = align_to_anatomical_frame(mesh, config)
        assert aligned.volume == pytest.approx(original_volume, rel=0.01)

    def test_report_contains_principal_axes(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig()
        _, report = align_to_anatomical_frame(mesh, config)
        assert isinstance(report, AlignmentReport)
        assert report.principal_axes.shape == (3, 3)

    def test_report_contains_transform(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig()
        _, report = align_to_anatomical_frame(mesh, config)
        assert report.transform_applied.shape == (4, 4)

    def test_does_not_mutate_original(self):
        """align_to_anatomical_frame should work on a copy."""
        mesh = _make_elongated_cylinder()
        original_verts = mesh.vertices.copy()
        config = CoverConfig()
        align_to_anatomical_frame(mesh, config)
        np.testing.assert_array_equal(mesh.vertices, original_verts)


# ---------------------------------------------------------------------------
# Centering
# ---------------------------------------------------------------------------

class TestCentering:
    def test_aligned_mesh_is_centered(self):
        """After alignment, the centroid should be near the origin."""
        mesh = _make_offset_cylinder()
        config = CoverConfig()
        aligned, _ = align_to_anatomical_frame(mesh, config)

        centroid = np.mean(aligned.vertices, axis=0)
        np.testing.assert_allclose(centroid, [0, 0, 0], atol=1.0)

    def test_offset_cylinder_starts_off_center(self):
        """Verify the test mesh is actually off-center before alignment."""
        mesh = _make_offset_cylinder()
        centroid = np.mean(mesh.vertices, axis=0)
        assert np.linalg.norm(centroid) > 50.0  # should be far from origin

    def test_bounding_box_centered(self):
        """Bounding box center should be near origin after alignment."""
        mesh = _make_offset_cylinder()
        config = CoverConfig()
        aligned, report = align_to_anatomical_frame(mesh, config)

        bounds = aligned.bounds
        center = (bounds[0] + bounds[1]) / 2.0
        # Center should be reasonably close to origin
        assert np.linalg.norm(center) < 10.0


# ---------------------------------------------------------------------------
# Side detection
# ---------------------------------------------------------------------------

class TestSideDetection:
    def test_auto_side_detection_returns_valid_value(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig(side="auto")
        _, report = align_to_anatomical_frame(mesh, config)
        assert report.detected_side in ("left", "right", "unknown")

    def test_symmetric_mesh_returns_unknown(self):
        """A perfectly symmetric cylinder cannot have its side determined."""
        mesh = _make_elongated_cylinder()
        config = CoverConfig(side="auto")
        _, report = align_to_anatomical_frame(mesh, config)
        # A symmetric cylinder should report unknown (too symmetric to tell)
        assert report.detected_side == "unknown"

    def test_manual_side_override(self):
        """When side is explicitly set, auto-detection should be skipped."""
        mesh = _make_elongated_cylinder()
        config = CoverConfig(side="left")
        _, report = align_to_anatomical_frame(mesh, config)
        assert report.detected_side == "left"

    def test_manual_side_right(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig(side="right")
        _, report = align_to_anatomical_frame(mesh, config)
        assert report.detected_side == "right"

    def test_asymmetric_mesh_detects_side(self):
        """An asymmetric mesh should detect left or right (not unknown)."""
        mesh = _make_asymmetric_mesh()
        config = CoverConfig(side="auto")
        _, report = align_to_anatomical_frame(mesh, config)
        # With a bulge on one side, the algorithm should pick a side
        assert report.detected_side in ("left", "right")

    def test_report_has_bounding_box_extent(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig()
        _, report = align_to_anatomical_frame(mesh, config)
        assert len(report.bounding_box_extent) == 3
        assert np.all(report.bounding_box_extent > 0)

    def test_report_has_center_of_mass(self):
        mesh = _make_elongated_cylinder()
        config = CoverConfig()
        _, report = align_to_anatomical_frame(mesh, config)
        assert len(report.center_of_mass) == 3

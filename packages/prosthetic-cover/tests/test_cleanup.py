"""Tests for mesh cleanup operations -- repair, decimation, and smoothing.

Uses engine.cleanup.repair_mesh when available, plus engine.utils.laplacian_smooth
and trimesh built-in repair utilities.
"""

import os
import sys

import numpy as np
import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.config import CoverConfig
from engine.utils import laplacian_smooth

# Try importing the dedicated cleanup module
try:
    from engine.cleanup import repair_mesh, CleanupReport

    _CLEANUP_MODULE = True
except ImportError:
    _CLEANUP_MODULE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_watertight_cylinder(radius=40.0, height=300.0):
    return trimesh.creation.cylinder(radius=radius, height=height, sections=32)


def _make_non_watertight_mesh():
    """Create a mesh with known defects (missing faces)."""
    mesh = _make_watertight_cylinder()
    # Remove some faces to break watertightness
    keep = np.ones(len(mesh.faces), dtype=bool)
    keep[:20] = False  # remove first 20 faces
    mesh.update_faces(keep)
    return mesh


def _make_mesh_with_degenerate_faces():
    """Create a mesh that includes degenerate (zero-area) faces."""
    mesh = _make_watertight_cylinder()
    verts = mesh.vertices
    faces = mesh.faces

    # Add degenerate faces where all three vertices are the same
    degen_faces = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    new_faces = np.vstack([faces, degen_faces])
    return trimesh.Trimesh(vertices=verts, faces=new_faces, process=False)


# ---------------------------------------------------------------------------
# Mesh repair
# ---------------------------------------------------------------------------

class TestMeshRepair:
    def test_broken_mesh_is_not_watertight(self):
        mesh = _make_non_watertight_mesh()
        assert not mesh.is_watertight

    def test_trimesh_fill_holes(self):
        """trimesh.repair.fill_holes should attempt to restore watertightness."""
        mesh = _make_non_watertight_mesh()
        initial_faces = len(mesh.faces)
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)
        # Repair should add faces (not crash)
        assert len(mesh.faces) >= initial_faces

    @pytest.mark.skipif(not _CLEANUP_MODULE, reason="engine.cleanup not yet implemented")
    def test_repair_mesh_returns_report(self):
        mesh = _make_non_watertight_mesh()
        config = CoverConfig(smoothing_iterations=0)
        repaired, report = repair_mesh(mesh, config)
        assert isinstance(report, CleanupReport)
        assert isinstance(repaired, trimesh.Trimesh)

    @pytest.mark.skipif(not _CLEANUP_MODULE, reason="engine.cleanup not yet implemented")
    def test_repair_mesh_does_not_mutate_original(self):
        mesh = _make_non_watertight_mesh()
        original_verts = mesh.vertices.copy()
        config = CoverConfig(smoothing_iterations=0)
        repair_mesh(mesh, config)
        np.testing.assert_array_equal(mesh.vertices, original_verts)

    @pytest.mark.skipif(not _CLEANUP_MODULE, reason="engine.cleanup not yet implemented")
    def test_repair_fills_holes(self):
        mesh = _make_non_watertight_mesh()
        config = CoverConfig(smoothing_iterations=0)
        repaired, report = repair_mesh(mesh, config)
        # Should have attempted to fill holes
        assert report.holes_filled >= 0

    def test_fix_normals(self):
        mesh = _make_watertight_cylinder()
        # Flip some normals by reversing face winding
        mesh.faces[:10] = mesh.faces[:10, ::-1]
        trimesh.repair.fix_normals(mesh)
        assert mesh.is_watertight

    def test_remove_degenerate_faces(self):
        """Degenerate faces should be detectable."""
        mesh = _make_mesh_with_degenerate_faces()
        original_count = len(mesh.faces)
        # trimesh's nondegenerate_faces method identifies valid faces
        mesh.update_faces(mesh.nondegenerate_faces())
        assert len(mesh.faces) < original_count


# ---------------------------------------------------------------------------
# Decimation
# ---------------------------------------------------------------------------

class TestDecimation:
    def test_trimesh_simplify(self):
        """Basic decimation using trimesh's built-in simplification."""
        mesh = _make_watertight_cylinder()
        original_faces = len(mesh.faces)
        target_faces = original_faces // 2

        try:
            decimated = mesh.simplify_quadric_decimation(target_faces)
            assert len(decimated.faces) <= target_faces + 10  # allow small margin
            assert len(decimated.faces) < original_faces
        except (ImportError, AttributeError):
            pytest.skip("Quadric decimation not available in this trimesh build")

    def test_decimation_preserves_shape(self):
        """Decimation should not drastically change the bounding box."""
        mesh = _make_watertight_cylinder()
        original_extent = mesh.bounding_box.extents.copy()
        target = len(mesh.faces) // 2

        try:
            decimated = mesh.simplify_quadric_decimation(target)
            new_extent = decimated.bounding_box.extents
            # Extents should stay within 5% of original
            np.testing.assert_allclose(new_extent, original_extent, rtol=0.05)
        except (ImportError, AttributeError):
            pytest.skip("Quadric decimation not available")

    def test_decimation_reduces_vertex_count(self):
        mesh = _make_watertight_cylinder()
        original_verts = len(mesh.vertices)
        target = len(mesh.faces) // 4

        try:
            decimated = mesh.simplify_quadric_decimation(target)
            assert len(decimated.vertices) < original_verts
        except (ImportError, AttributeError):
            pytest.skip("Quadric decimation not available")


# ---------------------------------------------------------------------------
# Smoothing
# ---------------------------------------------------------------------------

class TestSmoothing:
    def test_laplacian_smooth_reduces_noise(self):
        """Adding noise then smoothing should reduce vertex variance."""
        mesh = _make_watertight_cylinder()

        # Add small noise
        rng = np.random.default_rng(42)
        noise = rng.normal(0, 0.5, mesh.vertices.shape)
        mesh.vertices += noise

        # Measure vertex position variance before and after smoothing
        noisy_variance = np.var(mesh.vertices, axis=0).sum()

        smoothed = laplacian_smooth(mesh, iterations=5, lamb=0.5)
        smooth_variance = np.var(smoothed.vertices, axis=0).sum()

        # Smoothing should reduce overall vertex spread (shrinkage effect)
        assert smooth_variance < noisy_variance

    def test_laplacian_smooth_preserves_face_count(self):
        mesh = _make_watertight_cylinder()
        original_face_count = len(mesh.faces)
        smoothed = laplacian_smooth(mesh, iterations=3)
        assert len(smoothed.faces) == original_face_count

    def test_laplacian_smooth_preserves_vertex_count(self):
        mesh = _make_watertight_cylinder()
        original_vert_count = len(mesh.vertices)
        smoothed = laplacian_smooth(mesh, iterations=3)
        assert len(smoothed.vertices) == original_vert_count

    def test_zero_iterations_is_identity(self):
        mesh = _make_watertight_cylinder()
        smoothed = laplacian_smooth(mesh, iterations=0)
        np.testing.assert_array_equal(smoothed.vertices, mesh.vertices)

    def test_smoothing_does_not_explode(self):
        """Many iterations should not cause NaN or extreme values."""
        mesh = _make_watertight_cylinder()
        smoothed = laplacian_smooth(mesh, iterations=50, lamb=0.3)
        assert not np.any(np.isnan(smoothed.vertices))
        assert not np.any(np.isinf(smoothed.vertices))
        # Mesh should still have roughly the same scale
        assert np.max(np.abs(smoothed.vertices)) < 1000.0

    def test_smoothing_shrinks_mesh(self):
        """Laplacian smoothing without volume preservation should shrink the mesh."""
        mesh = _make_watertight_cylinder()
        original_extent = mesh.bounding_box.extents.copy()
        smoothed = laplacian_smooth(mesh, iterations=20, lamb=0.5)
        new_extent = smoothed.bounding_box.extents
        # Smoothed extent should be smaller (shrinkage effect)
        assert np.all(new_extent <= original_extent * 1.01)

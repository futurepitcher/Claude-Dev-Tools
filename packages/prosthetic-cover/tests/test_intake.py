"""Tests for engine.intake -- scan loading and validation."""

import os
import sys
import tempfile

import numpy as np
import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.intake import load_scan, MeshStats, SUPPORTED_EXTENSIONS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_cylinder_stl(path: str, radius: float = 40.0, height: float = 300.0):
    """Create and write a cylinder STL to *path*."""
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    mesh.export(path)
    return mesh


def _write_cylinder_obj(path: str):
    """Create and write a cylinder OBJ to *path*."""
    mesh = trimesh.creation.cylinder(radius=40.0, height=300.0, sections=32)
    mesh.export(path, file_type="obj")
    return mesh


# ---------------------------------------------------------------------------
# Loading valid files
# ---------------------------------------------------------------------------

class TestLoadValidFiles:
    def test_load_stl(self, tmp_path):
        stl_path = str(tmp_path / "prosthesis.stl")
        _write_cylinder_stl(stl_path)
        mesh, report = load_scan(stl_path)
        assert isinstance(mesh, trimesh.Trimesh)
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0

    def test_load_obj(self, tmp_path):
        obj_path = str(tmp_path / "prosthesis.obj")
        _write_cylinder_obj(obj_path)
        mesh, report = load_scan(obj_path)
        assert isinstance(mesh, trimesh.Trimesh)

    def test_report_has_filepath(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        _, report = load_scan(stl_path)
        assert report.filepath == stl_path

    def test_report_file_size(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        _, report = load_scan(stl_path)
        assert report.file_size_bytes > 0

    def test_load_returns_trimesh_instance(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        mesh, _ = load_scan(stl_path)
        assert hasattr(mesh, "vertices")
        assert hasattr(mesh, "faces")


# ---------------------------------------------------------------------------
# Mesh stats computation
# ---------------------------------------------------------------------------

class TestMeshStatsComputation:
    def test_vertex_and_face_counts(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        original = _write_cylinder_stl(stl_path)
        _, report = load_scan(stl_path)
        assert report.stats.vertices == len(original.vertices)
        assert report.stats.faces == len(original.faces)

    def test_watertight_cylinder(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        mesh, report = load_scan(stl_path)
        assert report.stats.is_watertight is True

    def test_volume_positive_for_watertight(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        _, report = load_scan(stl_path)
        assert report.stats.volume > 0

    def test_bounding_box_extent(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path, radius=40.0, height=300.0)
        _, report = load_scan(stl_path)
        extent = report.stats.bounds.extent
        # The longest axis (height=300) should be approximately 300 mm
        assert np.max(extent) == pytest.approx(300.0, abs=1.0)

    def test_estimated_units_for_mm_scale(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path, radius=40.0, height=300.0)
        _, report = load_scan(stl_path)
        assert report.stats.estimated_units == "mm"

    def test_bounding_box_center(self, tmp_path):
        stl_path = str(tmp_path / "test.stl")
        _write_cylinder_stl(stl_path)
        _, report = load_scan(stl_path)
        center = report.stats.bounds.center
        assert len(center) == 3


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestIntakeErrors:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_scan("/nonexistent/path/scan.stl")

    def test_unsupported_extension(self, tmp_path):
        bad_file = tmp_path / "scan.xyz"
        bad_file.write_text("not a mesh")
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_scan(str(bad_file))

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.stl"
        empty.write_bytes(b"")
        with pytest.raises(ValueError, match="empty"):
            load_scan(str(empty))

    def test_corrupt_file(self, tmp_path):
        corrupt = tmp_path / "corrupt.stl"
        corrupt.write_bytes(b"this is definitely not valid STL data at all" * 10)
        with pytest.raises(Exception):
            load_scan(str(corrupt))

    def test_supported_extensions_constant(self):
        """SUPPORTED_EXTENSIONS should contain at least .stl and .obj."""
        assert ".stl" in SUPPORTED_EXTENSIONS
        assert ".obj" in SUPPORTED_EXTENSIONS


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

class TestIntakeWarnings:
    def test_low_vertex_mesh_warning(self, tmp_path):
        """A tiny mesh with very few vertices should produce a warning."""
        # icosahedron has 12 vertices which is < MIN_VERTEX_COUNT=100
        mesh = trimesh.creation.icosahedron()
        # Scale to mm range so unit detection does not also warn
        mesh.apply_scale(100.0)
        stl_path = str(tmp_path / "tiny.stl")
        mesh.export(stl_path)
        _, report = load_scan(stl_path)
        assert any("low vertex count" in w.lower() or "vertex count" in w.lower()
                    for w in report.warnings)

    def test_non_watertight_mesh_warning(self, tmp_path):
        """A mesh with holes should get a watertight warning."""
        mesh = trimesh.creation.cylinder(radius=40.0, height=300.0, sections=32)
        # Remove faces to break watertightness
        keep = np.ones(len(mesh.faces), dtype=bool)
        keep[:20] = False
        mesh.update_faces(keep)
        stl_path = str(tmp_path / "broken.stl")
        mesh.export(stl_path)
        _, report = load_scan(stl_path)
        assert any("watertight" in w.lower() for w in report.warnings)

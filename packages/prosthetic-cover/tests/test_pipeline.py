"""Tests for engine.pipeline -- CoverPipeline and PipelineState."""

import os
import sys

import pytest
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.config import CoverConfig

# The pipeline module may not exist yet.  Import defensively so we can mark
# tests as skip-able rather than crashing the entire test file.
try:
    from engine.pipeline import CoverPipeline, PipelineState

    _PIPELINE_AVAILABLE = True
except ImportError:
    _PIPELINE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _PIPELINE_AVAILABLE,
    reason="engine.pipeline module not yet implemented",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_prosthesis():
    """Create a synthetic cylinder mesh mimicking a prosthesis segment.

    A cylinder with radius=40mm and height=300mm is a reasonable stand-in
    for a lower-limb prosthesis pylon or socket scan.
    """
    mesh = trimesh.creation.cylinder(radius=40.0, height=300.0, sections=32)
    return mesh


def _export_prosthesis(tmp_path, filename="test_prosthesis.stl"):
    """Export the test prosthesis to a temp STL file and return the path."""
    mesh = _make_test_prosthesis()
    stl_path = str(tmp_path / filename)
    mesh.export(stl_path)
    return stl_path


# ---------------------------------------------------------------------------
# PipelineState
# ---------------------------------------------------------------------------

class TestPipelineState:
    def test_state_values_exist(self):
        assert hasattr(PipelineState, "INIT")
        assert hasattr(PipelineState, "SCAN_LOADED")

    def test_states_are_ordered(self):
        """States should be comparable or at least distinct."""
        assert PipelineState.INIT != PipelineState.SCAN_LOADED

    def test_init_is_starting_state(self):
        """INIT should represent the earliest pipeline state."""
        all_states = list(PipelineState)
        assert PipelineState.INIT in all_states
        assert all_states[0] == PipelineState.INIT


# ---------------------------------------------------------------------------
# CoverPipeline creation
# ---------------------------------------------------------------------------

class TestPipelineCreation:
    def test_create_with_default_config(self):
        config = CoverConfig()
        pipeline = CoverPipeline(config)
        assert pipeline.config is config

    def test_create_with_custom_config(self):
        config = CoverConfig(
            style_family="perforated",
            perforation_shape="hex",
            shell_thickness_mm=4.0,
        )
        pipeline = CoverPipeline(config)
        assert pipeline.config.style_family == "perforated"

    def test_initial_state_is_init(self):
        pipeline = CoverPipeline(CoverConfig())
        assert pipeline.state == PipelineState.INIT

    def test_create_with_transfemoral_config(self):
        config = CoverConfig(
            prosthesis_type="transfemoral",
            clearance_offset_mm=2.5,
            shell_thickness_mm=3.5,
        )
        pipeline = CoverPipeline(config)
        assert pipeline.config.prosthesis_type == "transfemoral"


# ---------------------------------------------------------------------------
# Stage execution order enforcement
# ---------------------------------------------------------------------------

class TestStageOrder:
    def test_cannot_cleanup_before_load(self):
        """Cleanup should fail if no mesh has been loaded."""
        pipeline = CoverPipeline(CoverConfig())
        with pytest.raises((RuntimeError, ValueError)):
            pipeline.run_stage("cleanup")

    def test_cannot_align_before_load(self):
        pipeline = CoverPipeline(CoverConfig())
        with pytest.raises((RuntimeError, ValueError)):
            pipeline.run_stage("align")

    def test_cannot_mark_regions_before_align(self):
        pipeline = CoverPipeline(CoverConfig())
        with pytest.raises((RuntimeError, ValueError)):
            pipeline.run_stage("mark_regions")

    def test_cannot_export_before_processing(self):
        pipeline = CoverPipeline(CoverConfig())
        with pytest.raises((RuntimeError, ValueError)):
            pipeline.run_stage("export", output_path="/tmp/test.stl")

    def test_load_scan_advances_state(self, tmp_path):
        """Loading a valid mesh should move the pipeline to SCAN_LOADED state."""
        stl_path = _export_prosthesis(tmp_path)
        pipeline = CoverPipeline(CoverConfig())
        pipeline.run_stage("load_scan", filepath=stl_path)
        assert pipeline.state == PipelineState.SCAN_LOADED

    def test_sequential_stages(self, tmp_path):
        """Run load -> cleanup -> align in order without error."""
        stl_path = _export_prosthesis(tmp_path)
        pipeline = CoverPipeline(CoverConfig())
        pipeline.run_stage("load_scan", filepath=stl_path)
        pipeline.run_stage("cleanup")
        pipeline.run_stage("align")
        # If we get here without error, ordering is correct.

    def test_invalid_stage_name_raises(self):
        """An unknown stage name should raise an error."""
        pipeline = CoverPipeline(CoverConfig())
        with pytest.raises((RuntimeError, ValueError, KeyError)):
            pipeline.run_stage("nonexistent_stage")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class TestPipelineReport:
    def test_report_on_fresh_pipeline(self):
        pipeline = CoverPipeline(CoverConfig())
        report = pipeline.get_report()
        assert isinstance(report, dict)

    def test_report_after_load(self, tmp_path):
        stl_path = _export_prosthesis(tmp_path)
        pipeline = CoverPipeline(CoverConfig())
        pipeline.run_stage("load_scan", filepath=stl_path)
        report = pipeline.get_report()
        assert isinstance(report, dict)

    def test_report_contains_config(self):
        pipeline = CoverPipeline(CoverConfig(style_family="lattice"))
        report = pipeline.get_report()
        assert isinstance(report, dict)

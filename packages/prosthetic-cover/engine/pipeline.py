"""
CoverPipeline — main orchestrator for the prosthetic cover design pipeline.

Manages state progression through discrete stages, delegates to module
implementations, and tracks metadata, warnings, and intermediate meshes.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import trimesh

from engine.config import CoverConfig

logger = logging.getLogger(__name__)


class PipelineState(str, Enum):
    """Ordered states the pipeline can be in."""

    INIT = "INIT"
    SCAN_LOADED = "SCAN_LOADED"
    CLEANED = "CLEANED"
    ALIGNED = "ALIGNED"
    REGIONS_MARKED = "REGIONS_MARKED"
    ENVELOPE_GENERATED = "ENVELOPE_GENERATED"
    SHELL_GENERATED = "SHELL_GENERATED"
    AESTHETICS_APPLIED = "AESTHETICS_APPLIED"
    ATTACHMENTS_ADDED = "ATTACHMENTS_ADDED"
    VALIDATED = "VALIDATED"
    EXPORTED = "EXPORTED"


# Canonical ordering of states for progression checks
_STATE_ORDER: list[PipelineState] = list(PipelineState)

# Mapping from run_stage name to (required prior state, resulting state)
_STAGE_META: dict[str, tuple[PipelineState, PipelineState]] = {
    "load_scan": (PipelineState.INIT, PipelineState.SCAN_LOADED),
    "cleanup": (PipelineState.SCAN_LOADED, PipelineState.CLEANED),
    "align": (PipelineState.CLEANED, PipelineState.ALIGNED),
    "mark_regions": (PipelineState.ALIGNED, PipelineState.REGIONS_MARKED),
    "generate_envelope": (PipelineState.REGIONS_MARKED, PipelineState.ENVELOPE_GENERATED),
    "generate_shell": (PipelineState.ENVELOPE_GENERATED, PipelineState.SHELL_GENERATED),
    "apply_aesthetics": (PipelineState.SHELL_GENERATED, PipelineState.AESTHETICS_APPLIED),
    "add_attachments": (PipelineState.AESTHETICS_APPLIED, PipelineState.ATTACHMENTS_ADDED),
    "validate": (PipelineState.ATTACHMENTS_ADDED, PipelineState.VALIDATED),
    "export": (PipelineState.VALIDATED, PipelineState.EXPORTED),
}


@dataclass
class StageResult:
    """Bookkeeping for a completed stage."""

    stage_name: str
    elapsed_seconds: float
    report: Any  # stage-specific report dataclass
    warnings: list[str] = field(default_factory=list)


class CoverPipeline:
    """Orchestrates the full prosthetic cover design pipeline.

    Usage::

        pipeline = CoverPipeline(config)
        pipeline.run_stage("load_scan", filepath="scan.stl")
        pipeline.run_stage("cleanup")
        ...
        pipeline.run_stage("export", output_path="cover.stl")

    The pipeline enforces stage ordering — you cannot skip stages or run
    them out of sequence.
    """

    def __init__(self, config: CoverConfig) -> None:
        errors = config.validate()
        if errors:
            raise ValueError(
                f"Invalid config: {'; '.join(errors)}"
            )

        self.config = config
        self.state: PipelineState = PipelineState.INIT

        # Mesh at each stage (keyed by state name)
        self.meshes: dict[str, trimesh.Trimesh] = {}
        self.current_mesh: trimesh.Trimesh | None = None

        # Region map (set during mark_regions)
        self.region_map: Any = None  # engine.regions.RegionMap

        # Stage reports
        self.stage_results: dict[str, StageResult] = {}

        # Accumulated warnings from all stages
        self.warnings: list[str] = []

        # Validation report (set during validate)
        self.validation_report: Any = None

        logger.info("Pipeline initialized with config: %s", config.style_family)

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _state_index(self, state: PipelineState) -> int:
        return _STATE_ORDER.index(state)

    def _check_prerequisite(self, stage_name: str) -> None:
        if stage_name not in _STAGE_META:
            raise ValueError(
                f"Unknown stage '{stage_name}'. "
                f"Available: {list(_STAGE_META.keys())}"
            )
        required, _ = _STAGE_META[stage_name]
        if self._state_index(self.state) < self._state_index(required):
            raise RuntimeError(
                f"Cannot run '{stage_name}': pipeline is at state '{self.state.value}', "
                f"but this stage requires at least '{required.value}'. "
                f"Run prerequisite stages first."
            )

    def _record_result(
        self, stage_name: str, elapsed: float, report: Any, warnings: list[str]
    ) -> None:
        result = StageResult(
            stage_name=stage_name,
            elapsed_seconds=elapsed,
            report=report,
            warnings=warnings,
        )
        self.stage_results[stage_name] = result
        self.warnings.extend(warnings)

        _, next_state = _STAGE_META[stage_name]
        self.state = next_state

        logger.info(
            "Stage '%s' complete in %.2fs -> state '%s'",
            stage_name, elapsed, self.state.value,
        )

    # ------------------------------------------------------------------
    # Stage dispatch
    # ------------------------------------------------------------------

    def run_stage(self, stage_name: str, **kwargs: Any) -> Any:
        """Execute a pipeline stage by name.

        Args:
            stage_name: One of the registered stage names.
            **kwargs: Stage-specific arguments (e.g., filepath for load_scan,
                      output_path for export).

        Returns:
            The stage-specific report object.

        Raises:
            ValueError: If the stage name is unknown.
            RuntimeError: If prerequisites are not met.
        """
        self._check_prerequisite(stage_name)

        dispatch = {
            "load_scan": self._run_load_scan,
            "cleanup": self._run_cleanup,
            "align": self._run_align,
            "mark_regions": self._run_mark_regions,
            "generate_envelope": self._run_generate_envelope,
            "generate_shell": self._run_generate_shell,
            "apply_aesthetics": self._run_apply_aesthetics,
            "add_attachments": self._run_add_attachments,
            "validate": self._run_validate,
            "export": self._run_export,
        }

        return dispatch[stage_name](**kwargs)

    # ------------------------------------------------------------------
    # Individual stage runners
    # ------------------------------------------------------------------

    def _run_load_scan(self, filepath: str = "", **kwargs: Any) -> Any:
        if not filepath:
            raise ValueError("load_scan requires a 'filepath' argument")

        from engine.intake import load_scan

        t0 = time.monotonic()
        mesh, report = load_scan(filepath)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["scan"] = mesh
        self._record_result("load_scan", elapsed, report, report.warnings)
        return report

    def _run_cleanup(self, **kwargs: Any) -> Any:
        from engine.cleanup import repair_mesh

        t0 = time.monotonic()
        mesh, report = repair_mesh(self.current_mesh, self.config)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["cleaned"] = mesh
        self._record_result("cleanup", elapsed, report, report.warnings)
        return report

    def _run_align(self, **kwargs: Any) -> Any:
        from engine.alignment import align_to_anatomical_frame

        t0 = time.monotonic()
        mesh, report = align_to_anatomical_frame(self.current_mesh, self.config)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["aligned"] = mesh

        # Update config side if auto-detected
        if self.config.side == "auto" and report.detected_side != "unknown":
            self.config.side = report.detected_side

        self._record_result("align", elapsed, report, [])
        return report

    def _run_mark_regions(self, **kwargs: Any) -> Any:
        from engine.regions import mark_regions

        t0 = time.monotonic()
        region_map, report = mark_regions(self.current_mesh, self.config)
        elapsed = time.monotonic() - t0

        self.region_map = region_map
        self._record_result("mark_regions", elapsed, report, report.warnings)
        return report

    def _run_generate_envelope(self, **kwargs: Any) -> Any:
        from engine.envelope import generate_envelope

        t0 = time.monotonic()
        mesh, report = generate_envelope(self.current_mesh, self.region_map, self.config)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["envelope"] = mesh
        self._record_result("generate_envelope", elapsed, report, report.warnings)
        return report

    def _run_generate_shell(self, **kwargs: Any) -> Any:
        from engine.shell import generate_shell

        t0 = time.monotonic()
        mesh, report = generate_shell(self.current_mesh, self.config)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["shell"] = mesh
        self._record_result("generate_shell", elapsed, report, report.warnings)
        return report

    def _run_apply_aesthetics(self, **kwargs: Any) -> Any:
        from engine.aesthetics import apply_style

        t0 = time.monotonic()
        mesh, report = apply_style(self.current_mesh, self.config, self.region_map)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["styled"] = mesh
        self._record_result("apply_aesthetics", elapsed, report, report.warnings)
        return report

    def _run_add_attachments(self, **kwargs: Any) -> Any:
        from engine.attachment import add_attachments

        t0 = time.monotonic()
        mesh, report = add_attachments(self.current_mesh, self.config, self.region_map)
        elapsed = time.monotonic() - t0

        self.current_mesh = mesh
        self.meshes["attached"] = mesh
        self._record_result("add_attachments", elapsed, report, report.warnings)
        return report

    def _run_validate(self, **kwargs: Any) -> Any:
        from engine.validation import validate_cover

        t0 = time.monotonic()
        report = validate_cover(self.current_mesh, self.config)
        elapsed = time.monotonic() - t0

        self.validation_report = report
        warn_msgs = [f.message for f in report.findings if not f.passed]
        self._record_result("validate", elapsed, report, warn_msgs)
        return report

    def _run_export(self, output_path: str = "", **kwargs: Any) -> Any:
        if not output_path:
            raise ValueError("export requires an 'output_path' argument")

        from engine.export import export_stl

        t0 = time.monotonic()
        report = export_stl(
            self.current_mesh,
            output_path,
            self.config,
            warnings=self.warnings,
            pipeline_info=self._pipeline_info(),
        )
        elapsed = time.monotonic() - t0

        self._record_result("export", elapsed, report, report.warnings)
        return report

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def _pipeline_info(self) -> dict[str, Any]:
        """Collect pipeline metadata for export."""
        info: dict[str, Any] = {
            "stages_completed": list(self.stage_results.keys()),
            "total_warnings": len(self.warnings),
        }
        for name, result in self.stage_results.items():
            info[f"{name}_elapsed_s"] = round(result.elapsed_seconds, 3)
        return info

    def get_status(self) -> dict[str, Any]:
        """Return current pipeline state summary."""
        mesh_info = None
        if self.current_mesh is not None:
            mesh_info = {
                "vertices": len(self.current_mesh.vertices),
                "faces": len(self.current_mesh.faces),
                "is_watertight": self.current_mesh.is_watertight,
            }

        return {
            "state": self.state.value,
            "stages_completed": list(self.stage_results.keys()),
            "current_mesh": mesh_info,
            "warning_count": len(self.warnings),
            "warnings": list(self.warnings),
        }

    def get_report(self) -> dict[str, Any]:
        """Generate a comprehensive pipeline report.

        Includes config, stage results, mesh stats, and validation findings.
        """
        report: dict[str, Any] = {
            "state": self.state.value,
            "config": self.config.to_dict(),
            "stages": {},
            "warnings": list(self.warnings),
        }

        for name, result in self.stage_results.items():
            stage_entry: dict[str, Any] = {
                "elapsed_seconds": round(result.elapsed_seconds, 3),
                "warnings": result.warnings,
            }
            # Serialize the report if it has a to_dict or similar
            if hasattr(result.report, "__dict__"):
                # Dataclass — grab simple fields
                rdict: dict[str, Any] = {}
                for k, v in result.report.__dict__.items():
                    try:
                        # Skip non-serializable fields
                        if hasattr(v, "tolist"):
                            rdict[k] = v.tolist()
                        elif isinstance(v, (str, int, float, bool, list, dict, type(None))):
                            rdict[k] = v
                        elif isinstance(v, set):
                            rdict[k] = len(v)
                    except Exception:
                        pass
                stage_entry["report"] = rdict

            report["stages"][name] = stage_entry

        # Current mesh summary
        if self.current_mesh is not None:
            bounds = self.current_mesh.bounds
            extent = bounds[1] - bounds[0]
            report["final_mesh"] = {
                "vertices": len(self.current_mesh.vertices),
                "faces": len(self.current_mesh.faces),
                "is_watertight": self.current_mesh.is_watertight,
                "bounding_box_mm": extent.tolist(),
            }

        # Validation summary
        if self.validation_report is not None:
            report["validation_grade"] = self.validation_report.grade.value

        return report

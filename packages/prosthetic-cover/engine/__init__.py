"""
Prosthetic Cover Engine
=======================

A geometry processing pipeline for generating custom 3D-printed aesthetic
covers for lower-limb prostheses.

Usage::

    from engine import CoverPipeline, CoverConfig

    config = CoverConfig(
        shell_thickness_mm=3.0,
        style_family="perforated",
        perforation_shape="hex",
        print_material="PA12_nylon",
    )

    pipeline = CoverPipeline(config)
    pipeline.run_stage("load_scan", filepath="scan.stl")
    pipeline.run_stage("cleanup")
    pipeline.run_stage("align")
    pipeline.run_stage("mark_regions")
    pipeline.run_stage("generate_envelope")
    pipeline.run_stage("generate_shell")
    pipeline.run_stage("apply_aesthetics")
    pipeline.run_stage("add_attachments")
    pipeline.run_stage("validate")
    pipeline.run_stage("export", output_path="cover.stl")

    report = pipeline.get_report()
"""

__version__ = "0.1.0"

from engine.config import CoverConfig, MaterialSpec, MATERIAL_LIBRARY
from engine.pipeline import CoverPipeline, PipelineState

__all__ = [
    "__version__",
    "CoverConfig",
    "CoverPipeline",
    "MaterialSpec",
    "MATERIAL_LIBRARY",
    "PipelineState",
]

"""
Preview module — generate text-based design summaries and metrics.

Provides a designer-readable overview of the current pipeline state
without requiring a graphical renderer.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from engine.pipeline import CoverPipeline

logger = logging.getLogger(__name__)


def generate_preview_stats(pipeline: CoverPipeline) -> dict[str, Any]:
    """Compute key metrics from the current pipeline state.

    Returns a dictionary with bounding box, volume, weight estimate,
    face count, style info, and validation status — everything needed
    for a text-based design review.

    Args:
        pipeline: The active CoverPipeline instance.

    Returns:
        Dictionary of preview metrics.
    """
    stats: dict[str, Any] = {
        "pipeline_state": pipeline.state.value if pipeline.state else "INIT",
        "config": {
            "style_family": pipeline.config.style_family,
            "print_material": pipeline.config.print_material,
            "shell_thickness_mm": pipeline.config.shell_thickness_mm,
            "clearance_offset_mm": pipeline.config.clearance_offset_mm,
            "coverage_extent": pipeline.config.coverage_extent,
            "attachment_type": pipeline.config.attachment_type,
            "split_strategy": pipeline.config.split_strategy,
            "prosthesis_type": pipeline.config.prosthesis_type,
            "side": pipeline.config.side,
        },
    }

    # Current mesh stats
    mesh = pipeline.current_mesh
    if mesh is not None:
        from engine.utils import compute_bounding_box, compute_mesh_stats, estimate_weight_grams

        mesh_stats = compute_mesh_stats(mesh)
        bbox = mesh_stats.bounds

        mat = pipeline.config.material_spec
        weight = estimate_weight_grams(
            mesh_stats.volume_mm3,
            mat.density_g_per_cm3,
            infill_percent=pipeline.config.infill_percent,
        )

        stats["mesh"] = {
            "vertices": mesh_stats.vertex_count,
            "faces": mesh_stats.face_count,
            "volume_mm3": round(mesh_stats.volume_mm3, 1),
            "volume_cm3": round(mesh_stats.volume_cm3, 2),
            "surface_area_mm2": round(mesh_stats.surface_area_mm2, 1),
            "is_watertight": mesh_stats.is_watertight,
            "bounding_box_mm": {
                "width_x": round(float(bbox.extent[0]), 1),
                "depth_y": round(float(bbox.extent[1]), 1),
                "height_z": round(float(bbox.extent[2]), 1),
            },
        }
        stats["weight_estimate_grams"] = round(weight, 1)
        stats["material"] = {
            "name": mat.name,
            "density_g_per_cm3": mat.density_g_per_cm3,
            "min_wall_thickness_mm": mat.min_wall_thickness,
            "min_feature_size_mm": mat.min_feature_size,
        }
    else:
        stats["mesh"] = None
        stats["weight_estimate_grams"] = None

    # Region info
    if pipeline.region_map is not None:
        from engine.regions import get_region_stats

        stats["regions"] = get_region_stats(pipeline.region_map)
    else:
        stats["regions"] = None

    # Accumulated warnings
    stats["warnings"] = list(pipeline.warnings)
    stats["warning_count"] = len(pipeline.warnings)

    return stats


def format_preview_text(stats: dict[str, Any]) -> str:
    """Format preview stats as a human-readable text summary.

    Args:
        stats: Output from generate_preview_stats().

    Returns:
        Multi-line string suitable for terminal display.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  PROSTHETIC COVER — DESIGN PREVIEW")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"  Pipeline state:  {stats['pipeline_state']}")
    lines.append("")

    cfg = stats.get("config", {})
    lines.append("  CONFIGURATION")
    lines.append(f"    Style:           {cfg.get('style_family', '-')}")
    lines.append(f"    Material:        {cfg.get('print_material', '-')}")
    lines.append(f"    Shell thickness: {cfg.get('shell_thickness_mm', '-')} mm")
    lines.append(f"    Clearance:       {cfg.get('clearance_offset_mm', '-')} mm")
    lines.append(f"    Coverage:        {cfg.get('coverage_extent', '-')}")
    lines.append(f"    Attachments:     {cfg.get('attachment_type', '-')}")
    lines.append(f"    Split:           {cfg.get('split_strategy', '-')}")
    lines.append(f"    Prosthesis:      {cfg.get('prosthesis_type', '-')}")
    lines.append(f"    Side:            {cfg.get('side', '-')}")
    lines.append("")

    mesh = stats.get("mesh")
    if mesh:
        bb = mesh.get("bounding_box_mm", {})
        lines.append("  MESH")
        lines.append(f"    Vertices:        {mesh['vertices']:,}")
        lines.append(f"    Faces:           {mesh['faces']:,}")
        lines.append(f"    Volume:          {mesh['volume_cm3']} cm3")
        lines.append(f"    Surface area:    {mesh['surface_area_mm2']:,.0f} mm2")
        lines.append(f"    Watertight:      {'Yes' if mesh['is_watertight'] else 'No'}")
        lines.append(f"    Dimensions:      {bb.get('width_x', '-')} x "
                      f"{bb.get('depth_y', '-')} x {bb.get('height_z', '-')} mm")
        lines.append("")

    weight = stats.get("weight_estimate_grams")
    mat_info = stats.get("material")
    if weight is not None and mat_info:
        lines.append("  WEIGHT ESTIMATE")
        lines.append(f"    Material:        {mat_info['name']}")
        lines.append(f"    Density:         {mat_info['density_g_per_cm3']} g/cm3")
        lines.append(f"    Estimated:       {weight} g")
        lines.append("")

    regions = stats.get("regions")
    if regions:
        lines.append("  REGIONS")
        lines.append(f"    Total faces:     {regions.get('total_faces', 0):,}")
        lines.append(f"    Coverage:        {regions.get('coverage', 0):,}")
        lines.append(f"    Aesthetic:       {regions.get('aesthetic', 0):,}")
        lines.append(f"    Joint:           {regions.get('joint', 0):,}")
        lines.append(f"    No-go:           {regions.get('no_go', 0):,}")
        lines.append(f"    Transition:      {regions.get('transition', 0):,}")
        lines.append("")

    warn_count = stats.get("warning_count", 0)
    if warn_count > 0:
        lines.append(f"  WARNINGS ({warn_count})")
        for w in stats.get("warnings", []):
            lines.append(f"    - {w}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)

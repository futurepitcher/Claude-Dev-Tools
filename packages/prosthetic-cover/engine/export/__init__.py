"""
Export module — write final cover meshes and reports to disk.

Produces binary STL files, JSON metadata, and markdown summary reports.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh

from engine.config import CoverConfig
from engine.utils import compute_bounding_box, compute_mesh_stats, estimate_weight_grams

logger = logging.getLogger(__name__)


@dataclass
class ExportReport:
    """Results from the export stage."""

    stl_paths: list[str]
    metadata_path: str
    report_path: str
    total_file_size_bytes: int
    warnings: list[str] = field(default_factory=list)


def _write_binary_stl(mesh: trimesh.Trimesh, output_path: Path) -> int:
    """Write a mesh as binary STL. Returns file size in bytes."""
    mesh.export(str(output_path), file_type="stl")
    return output_path.stat().st_size


def _generate_metadata(
    mesh: trimesh.Trimesh,
    config: CoverConfig,
    output_dir: Path,
    stl_files: list[str],
    extra: dict | None = None,
) -> Path:
    """Write a JSON metadata file alongside the STL."""
    stats = compute_mesh_stats(mesh)
    weight = estimate_weight_grams(
        stats.volume_mm3,
        config.material_spec.density_g_per_cm3,
        infill_percent=config.infill_percent,
    )

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": "0.1.0",
        "config": config.to_dict(),
        "mesh": {
            "vertices": stats.vertex_count,
            "faces": stats.face_count,
            "volume_mm3": stats.volume_mm3,
            "volume_cm3": stats.volume_cm3,
            "surface_area_mm2": stats.surface_area_mm2,
            "is_watertight": stats.is_watertight,
            "bounding_box_mm": {
                "min": stats.bounds.min_corner.tolist(),
                "max": stats.bounds.max_corner.tolist(),
                "extent": stats.bounds.extent.tolist(),
            },
        },
        "weight_estimate_grams": weight,
        "stl_files": stl_files,
    }

    if extra:
        metadata["pipeline"] = extra

    meta_path = output_dir / "cover_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2, default=str))
    logger.info("Wrote metadata to %s", meta_path)
    return meta_path


def _generate_markdown_report(
    mesh: trimesh.Trimesh,
    config: CoverConfig,
    output_dir: Path,
    stl_files: list[str],
    warnings: list[str] | None = None,
    extra: dict | None = None,
) -> Path:
    """Write a human-readable markdown report."""
    stats = compute_mesh_stats(mesh)
    weight = estimate_weight_grams(
        stats.volume_mm3,
        config.material_spec.density_g_per_cm3,
        infill_percent=config.infill_percent,
    )
    bbox = stats.bounds

    lines = [
        "# Prosthetic Cover — Design Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Engine version:** 0.1.0",
        "",
        "## Configuration",
        "",
        f"- **Prosthesis type:** {config.prosthesis_type}",
        f"- **Side:** {config.side}",
        f"- **Coverage extent:** {config.coverage_extent}",
        f"- **Style:** {config.style_family}",
        f"- **Material:** {config.material_spec.name} ({config.print_material})",
        f"- **Shell thickness:** {config.shell_thickness_mm} mm",
        f"- **Clearance offset:** {config.clearance_offset_mm} mm",
        f"- **Attachment type:** {config.attachment_type}",
        f"- **Split strategy:** {config.split_strategy}",
        "",
        "## Mesh Summary",
        "",
        f"- **Vertices:** {stats.vertex_count:,}",
        f"- **Faces:** {stats.face_count:,}",
        f"- **Volume:** {stats.volume_cm3:.1f} cm3",
        f"- **Surface area:** {stats.surface_area_mm2:.0f} mm2",
        f"- **Watertight:** {'Yes' if stats.is_watertight else 'No'}",
        "",
        "## Dimensions",
        "",
        f"- **Width (X):** {bbox.extent[0]:.1f} mm",
        f"- **Depth (Y):** {bbox.extent[1]:.1f} mm",
        f"- **Height (Z):** {bbox.extent[2]:.1f} mm",
        "",
        "## Weight Estimate",
        "",
        f"- **Material density:** {config.material_spec.density_g_per_cm3} g/cm3",
        f"- **Infill:** {config.infill_percent}%",
        f"- **Estimated weight:** {weight:.0f} g",
        "",
        "## Print Settings",
        "",
        f"- **Layer height:** {config.layer_height_mm} mm",
        f"- **Infill:** {config.infill_percent}%",
        "",
        "## Output Files",
        "",
    ]

    for f in stl_files:
        lines.append(f"- `{f}`")

    if warnings:
        lines.extend(["", "## Warnings", ""])
        for w in warnings:
            lines.append(f"- {w}")

    if extra:
        lines.extend(["", "## Pipeline Details", ""])
        for k, v in extra.items():
            lines.append(f"- **{k}:** {v}")

    lines.append("")

    report_path = output_dir / "cover_report.md"
    report_path.write_text("\n".join(lines))
    logger.info("Wrote report to %s", report_path)
    return report_path


def export_stl(
    mesh: trimesh.Trimesh,
    output_path: str | Path,
    config: CoverConfig,
    panels: list[trimesh.Trimesh] | None = None,
    warnings: list[str] | None = None,
    pipeline_info: dict | None = None,
) -> ExportReport:
    """Export the final cover mesh to STL with accompanying metadata.

    Args:
        mesh: The final cover mesh.
        output_path: Path for the primary STL file.
        config: Pipeline configuration.
        panels: Optional list of panel meshes for panelized / split exports.
        warnings: Accumulated pipeline warnings.
        pipeline_info: Extra info to include in metadata.

    Returns:
        An ExportReport summarizing all written files.
    """
    output_path = Path(output_path)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    export_warnings: list[str] = list(warnings or [])
    stl_files: list[str] = []
    total_size = 0

    # ---- Write primary STL ----
    size = _write_binary_stl(mesh, output_path)
    stl_files.append(output_path.name)
    total_size += size
    logger.info("Wrote primary STL: %s (%.1f KB)", output_path, size / 1024.0)

    # ---- Write panel STLs if provided ----
    if panels:
        for i, panel_mesh in enumerate(panels):
            panel_path = output_dir / f"{output_path.stem}_panel_{i}.stl"
            psize = _write_binary_stl(panel_mesh, panel_path)
            stl_files.append(panel_path.name)
            total_size += psize
            logger.info("Wrote panel STL: %s (%.1f KB)", panel_path, psize / 1024.0)

    # ---- Metadata JSON ----
    meta_path = _generate_metadata(
        mesh, config, output_dir, stl_files, extra=pipeline_info
    )
    total_size += meta_path.stat().st_size

    # ---- Markdown report ----
    report_path = _generate_markdown_report(
        mesh, config, output_dir, stl_files,
        warnings=export_warnings, extra=pipeline_info,
    )
    total_size += report_path.stat().st_size

    return ExportReport(
        stl_paths=[str(output_dir / f) for f in stl_files],
        metadata_path=str(meta_path),
        report_path=str(report_path),
        total_file_size_bytes=total_size,
        warnings=export_warnings,
    )

"""
Validation module — check the final cover mesh for printability and correctness.

Runs a suite of checks against material specifications and common
3D-printing failure modes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import trimesh

from engine.config import CoverConfig

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    """Severity level for validation findings."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Grade(str, Enum):
    """Overall validation grade."""

    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    FAIL = "FAIL"


@dataclass
class ValidationFinding:
    """A single validation check result."""

    check_name: str
    passed: bool
    severity: Severity
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Complete validation results for a cover mesh."""

    findings: list[ValidationFinding] = field(default_factory=list)
    grade: Grade = Grade.PASS
    vertex_count: int = 0
    face_count: int = 0
    volume_mm3: float = 0.0

    @property
    def passed(self) -> bool:
        return self.grade == Grade.PASS

    @property
    def errors(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.severity in (Severity.ERROR, Severity.CRITICAL)]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [f for f in self.findings if f.severity == Severity.WARNING]

    def summary(self) -> str:
        lines = [f"Validation grade: {self.grade.value}"]
        for f in self.findings:
            status = "PASS" if f.passed else f.severity.value
            lines.append(f"  [{status}] {f.check_name}: {f.message}")
        return "\n".join(lines)


def _check_watertight(mesh: trimesh.Trimesh) -> ValidationFinding:
    """Check if the mesh is watertight (closed manifold)."""
    if mesh.is_watertight:
        return ValidationFinding(
            check_name="watertight",
            passed=True,
            severity=Severity.INFO,
            message="Mesh is watertight",
        )
    return ValidationFinding(
        check_name="watertight",
        passed=False,
        severity=Severity.ERROR,
        message="Mesh is not watertight. Most 3D printers require a closed manifold.",
    )


def _check_manifold(mesh: trimesh.Trimesh) -> ValidationFinding:
    """Check for non-manifold edges (shared by more than 2 faces)."""
    edges = mesh.edges_sorted
    from collections import Counter

    edge_counts = Counter(map(tuple, edges))
    non_manifold = sum(1 for c in edge_counts.values() if c > 2)

    if non_manifold == 0:
        return ValidationFinding(
            check_name="manifold_edges",
            passed=True,
            severity=Severity.INFO,
            message="All edges are manifold",
        )
    return ValidationFinding(
        check_name="manifold_edges",
        passed=False,
        severity=Severity.ERROR,
        message=f"{non_manifold} non-manifold edges detected",
        details={"non_manifold_count": non_manifold},
    )


def _check_wall_thickness(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> ValidationFinding:
    """Check wall thickness against material minimum.

    Uses ray-casting to estimate local wall thickness at sample points.
    """
    mat = config.material_spec
    min_wall = mat.min_wall_thickness

    # Sample face centroids and cast rays inward to estimate thickness
    n_samples = min(2000, len(mesh.faces))
    rng = np.random.default_rng(0)
    sample_indices = rng.choice(len(mesh.faces), size=n_samples, replace=False)

    origins = mesh.triangles_center[sample_indices]
    normals = mesh.face_normals[sample_indices]

    # Cast rays inward (opposite to face normal)
    ray_directions = -normals

    try:
        locations, index_ray, index_tri = mesh.ray.intersects_location(
            ray_origins=origins + ray_directions * 0.01,  # slight offset to avoid self-hit
            ray_directions=ray_directions,
        )

        if len(locations) == 0:
            return ValidationFinding(
                check_name="wall_thickness",
                passed=False,
                severity=Severity.WARNING,
                message="Could not measure wall thickness via ray casting",
            )

        # Compute distances from origin to hit point
        distances = np.linalg.norm(
            locations - (origins[index_ray] + ray_directions[index_ray] * 0.01), axis=1
        )

        min_measured = float(np.min(distances)) if len(distances) > 0 else 0.0
        mean_measured = float(np.mean(distances)) if len(distances) > 0 else 0.0
        thin_count = int(np.sum(distances < min_wall))

        details = {
            "min_thickness_mm": min_measured,
            "mean_thickness_mm": mean_measured,
            "samples_below_minimum": thin_count,
            "total_samples": len(distances),
            "material_minimum_mm": min_wall,
        }

        if thin_count > 0:
            pct = 100.0 * thin_count / len(distances)
            severity = Severity.ERROR if pct > 10.0 else Severity.WARNING
            return ValidationFinding(
                check_name="wall_thickness",
                passed=False,
                severity=severity,
                message=(
                    f"{thin_count}/{len(distances)} samples ({pct:.1f}%) below "
                    f"material minimum of {min_wall} mm (min measured: {min_measured:.2f} mm)"
                ),
                details=details,
            )

        return ValidationFinding(
            check_name="wall_thickness",
            passed=True,
            severity=Severity.INFO,
            message=f"Wall thickness OK (min: {min_measured:.2f} mm, material min: {min_wall} mm)",
            details=details,
        )

    except Exception as exc:
        return ValidationFinding(
            check_name="wall_thickness",
            passed=False,
            severity=Severity.WARNING,
            message=f"Wall thickness check failed: {exc}",
        )


def _check_min_feature_size(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> ValidationFinding:
    """Check that the smallest mesh features meet the minimum feature size."""
    mat = config.material_spec
    min_feat = mat.min_feature_size

    # Approximate: check shortest edge lengths
    edges = mesh.edges_unique
    edge_vectors = mesh.vertices[edges[:, 1]] - mesh.vertices[edges[:, 0]]
    edge_lengths = np.linalg.norm(edge_vectors, axis=1)

    shortest = float(np.min(edge_lengths)) if len(edge_lengths) > 0 else 0.0
    p5 = float(np.percentile(edge_lengths, 5)) if len(edge_lengths) > 0 else 0.0

    details = {
        "shortest_edge_mm": shortest,
        "p5_edge_mm": p5,
        "material_min_feature_mm": min_feat,
    }

    if p5 < min_feat:
        return ValidationFinding(
            check_name="min_feature_size",
            passed=False,
            severity=Severity.WARNING,
            message=(
                f"5th-percentile edge length ({p5:.3f} mm) is below "
                f"material minimum feature size ({min_feat} mm)"
            ),
            details=details,
        )

    return ValidationFinding(
        check_name="min_feature_size",
        passed=True,
        severity=Severity.INFO,
        message=f"Feature sizes OK (5th-percentile edge: {p5:.3f} mm, min allowed: {min_feat} mm)",
        details=details,
    )


def _check_self_intersections(mesh: trimesh.Trimesh) -> ValidationFinding:
    """Check for self-intersecting faces."""
    try:
        if mesh.is_volume:
            return ValidationFinding(
                check_name="self_intersections",
                passed=True,
                severity=Severity.INFO,
                message="Mesh is a valid volume (no self-intersections detected)",
            )

        # trimesh's is_volume check covers most self-intersection cases.
        # For a more thorough check, we rely on the boolean engine.
        return ValidationFinding(
            check_name="self_intersections",
            passed=False,
            severity=Severity.WARNING,
            message="Mesh is not a valid volume; possible self-intersections",
        )
    except Exception as exc:
        return ValidationFinding(
            check_name="self_intersections",
            passed=False,
            severity=Severity.WARNING,
            message=f"Self-intersection check inconclusive: {exc}",
        )


def _check_overhang_angles(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> ValidationFinding:
    """Check for faces with overhang angles exceeding material limits.

    Overhang angle is measured between the face normal and the build
    direction (assumed to be +Z).
    """
    mat = config.material_spec
    max_overhang = mat.max_overhang_angle_deg

    # SLS (max_overhang >= 90) supports all angles
    if max_overhang >= 90.0:
        return ValidationFinding(
            check_name="overhang_angles",
            passed=True,
            severity=Severity.INFO,
            message=f"Material supports all overhang angles (SLS/SLA: {max_overhang} deg)",
        )

    face_normals = mesh.face_normals
    build_dir = np.array([0.0, 0.0, 1.0])

    # Angle between face normal and build direction
    cos_angles = np.dot(face_normals, build_dir)
    angles_deg = np.degrees(np.arccos(np.clip(cos_angles, -1.0, 1.0)))

    # Overhang = faces pointing mostly downward (angle > 90 + threshold)
    # A face at 90 degrees is vertical; angles > 90 face downward
    overhang_threshold = 90.0 + (90.0 - max_overhang)
    overhanging = angles_deg > overhang_threshold
    overhang_count = int(np.sum(overhanging))

    if overhang_count == 0:
        return ValidationFinding(
            check_name="overhang_angles",
            passed=True,
            severity=Severity.INFO,
            message=f"No faces exceed overhang limit ({max_overhang} deg)",
        )

    pct = 100.0 * overhang_count / len(mesh.faces)
    severity = Severity.WARNING if pct < 5.0 else Severity.ERROR

    return ValidationFinding(
        check_name="overhang_angles",
        passed=False,
        severity=severity,
        message=(
            f"{overhang_count} faces ({pct:.1f}%) exceed max overhang angle "
            f"of {max_overhang} deg for {config.print_material}"
        ),
        details={
            "overhanging_faces": overhang_count,
            "total_faces": len(mesh.faces),
            "max_overhang_deg": max_overhang,
        },
    )


def _check_bridge_spans(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> ValidationFinding:
    """Check for bridge spans exceeding material limits."""
    mat = config.material_spec
    max_bridge = mat.max_bridge_span

    # Approximate: check for long edges in downward-facing regions
    face_normals = mesh.face_normals
    build_dir = np.array([0.0, 0.0, 1.0])
    cos_angles = np.dot(face_normals, build_dir)

    # Faces pointing somewhat downward (angle > 80 degrees from build dir)
    downward_mask = cos_angles < np.cos(np.radians(80.0))
    downward_faces = np.where(downward_mask)[0]

    if len(downward_faces) == 0:
        return ValidationFinding(
            check_name="bridge_spans",
            passed=True,
            severity=Severity.INFO,
            message="No downward-facing regions to check for bridge spans",
        )

    # Check edge lengths in downward-facing faces
    downward_tris = mesh.faces[downward_faces]
    all_edges = np.vstack([
        mesh.vertices[downward_tris[:, 1]] - mesh.vertices[downward_tris[:, 0]],
        mesh.vertices[downward_tris[:, 2]] - mesh.vertices[downward_tris[:, 1]],
        mesh.vertices[downward_tris[:, 0]] - mesh.vertices[downward_tris[:, 2]],
    ])
    edge_lengths = np.linalg.norm(all_edges, axis=1)
    # Project to horizontal plane for bridge span
    horizontal_lengths = np.linalg.norm(all_edges[:, :2], axis=1)

    max_span = float(np.max(horizontal_lengths)) if len(horizontal_lengths) > 0 else 0.0

    if max_span > max_bridge:
        return ValidationFinding(
            check_name="bridge_spans",
            passed=False,
            severity=Severity.WARNING,
            message=(
                f"Maximum horizontal bridge span ({max_span:.1f} mm) exceeds "
                f"material limit ({max_bridge} mm) for {config.print_material}"
            ),
            details={"max_span_mm": max_span, "material_limit_mm": max_bridge},
        )

    return ValidationFinding(
        check_name="bridge_spans",
        passed=True,
        severity=Severity.INFO,
        message=f"Bridge spans OK (max: {max_span:.1f} mm, limit: {max_bridge} mm)",
    )


def validate_cover(
    mesh: trimesh.Trimesh, config: CoverConfig
) -> ValidationReport:
    """Run all validation checks on the final cover mesh.

    Args:
        mesh: The final cover mesh (with attachments).
        config: Pipeline configuration.

    Returns:
        A ValidationReport with findings and an overall grade.
    """
    logger.info("Running validation checks on %d-face mesh", len(mesh.faces))

    findings: list[ValidationFinding] = []

    # Run all checks
    findings.append(_check_watertight(mesh))
    findings.append(_check_manifold(mesh))
    findings.append(_check_wall_thickness(mesh, config))
    findings.append(_check_min_feature_size(mesh, config))
    findings.append(_check_self_intersections(mesh))
    findings.append(_check_overhang_angles(mesh, config))
    findings.append(_check_bridge_spans(mesh, config))

    # Determine overall grade
    has_critical = any(f.severity == Severity.CRITICAL and not f.passed for f in findings)
    has_error = any(f.severity == Severity.ERROR and not f.passed for f in findings)
    has_warning = any(f.severity == Severity.WARNING and not f.passed for f in findings)

    if has_critical:
        grade = Grade.FAIL
    elif has_error:
        grade = Grade.FAIL
    elif has_warning:
        grade = Grade.CONDITIONAL
    else:
        grade = Grade.PASS

    volume = float(mesh.volume) if mesh.is_volume else 0.0

    report = ValidationReport(
        findings=findings,
        grade=grade,
        vertex_count=len(mesh.vertices),
        face_count=len(mesh.faces),
        volume_mm3=abs(volume),
    )

    logger.info("Validation complete: grade=%s (%d findings)", grade.value, len(findings))
    for f in findings:
        if not f.passed:
            logger.warning("  [%s] %s: %s", f.severity.value, f.check_name, f.message)

    return report

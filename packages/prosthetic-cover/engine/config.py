"""
Configuration dataclasses and material library for the prosthetic cover engine.

All measurements are in millimeters unless otherwise noted.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MaterialSpec:
    """Physical constraints for a given print material."""

    name: str
    min_wall_thickness: float  # mm
    min_feature_size: float  # mm
    max_bridge_span: float  # mm
    density_g_per_cm3: float
    max_overhang_angle_deg: float = 45.0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


MATERIAL_LIBRARY: dict[str, MaterialSpec] = {
    "PA12_nylon": MaterialSpec(
        name="PA12 Nylon (SLS)",
        min_wall_thickness=0.8,
        min_feature_size=0.5,
        max_bridge_span=50.0,
        density_g_per_cm3=1.01,
        max_overhang_angle_deg=90.0,  # SLS supports overhangs
        description="Standard SLS nylon, excellent for functional parts",
    ),
    "PA11_nylon": MaterialSpec(
        name="PA11 Nylon (SLS)",
        min_wall_thickness=0.8,
        min_feature_size=0.5,
        max_bridge_span=50.0,
        density_g_per_cm3=1.03,
        max_overhang_angle_deg=90.0,
        description="Bio-based nylon, slightly more flexible than PA12",
    ),
    "PLA": MaterialSpec(
        name="PLA (FDM)",
        min_wall_thickness=1.2,
        min_feature_size=1.0,
        max_bridge_span=10.0,
        density_g_per_cm3=1.24,
        max_overhang_angle_deg=45.0,
        description="Standard FDM material, good for prototyping",
    ),
    "PETG": MaterialSpec(
        name="PETG (FDM)",
        min_wall_thickness=1.2,
        min_feature_size=1.0,
        max_bridge_span=12.0,
        density_g_per_cm3=1.27,
        max_overhang_angle_deg=50.0,
        description="Tough FDM material with good chemical resistance",
    ),
    "TPU_95A": MaterialSpec(
        name="TPU 95A (FDM)",
        min_wall_thickness=1.5,
        min_feature_size=1.5,
        max_bridge_span=8.0,
        density_g_per_cm3=1.21,
        max_overhang_angle_deg=40.0,
        description="Flexible filament for comfort pads and gaskets",
    ),
    "resin_standard": MaterialSpec(
        name="Standard Resin (SLA)",
        min_wall_thickness=0.6,
        min_feature_size=0.3,
        max_bridge_span=15.0,
        density_g_per_cm3=1.18,
        max_overhang_angle_deg=35.0,
        description="High detail SLA resin",
    ),
    "resin_tough": MaterialSpec(
        name="Tough Resin (SLA)",
        min_wall_thickness=0.8,
        min_feature_size=0.4,
        max_bridge_span=15.0,
        density_g_per_cm3=1.15,
        max_overhang_angle_deg=35.0,
        description="Impact-resistant SLA resin",
    ),
}


@dataclass
class CoverConfig:
    """Complete configuration for a prosthetic cover design.

    All dimensional parameters are in millimeters.
    """

    # --- Geometry offsets ---
    clearance_offset_mm: float = 2.0
    shell_thickness_mm: float = 3.0
    min_feature_size_mm: float = 1.5
    min_bridge_width_mm: float = 2.0

    # --- Coverage ---
    coverage_extent: str = "full"  # full | partial | minimal

    # --- Aesthetics ---
    style_family: str = "smooth"  # smooth | faceted | perforated | lattice | organic | panelized
    perforation_density: float = 0.3  # 0.0 to 1.0
    perforation_shape: str = "circle"  # circle | hex | diamond | voronoi | organic

    # --- Attachment ---
    attachment_type: str = "snap_clip"  # snap_clip | magnet | screw | adhesive
    split_strategy: str = "none"  # none | medial_lateral | anterior_posterior | three_piece

    # --- Processing ---
    smoothing_iterations: int = 3

    # --- Anatomy ---
    prosthesis_type: str = "transtibial"  # transtibial | transfemoral
    side: str = "auto"  # auto | left | right

    # --- Print settings ---
    print_material: str = "PA12_nylon"
    layer_height_mm: float = 0.2
    infill_percent: int = 20

    def to_dict(self) -> dict[str, Any]:
        """Serialize config to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CoverConfig:
        """Deserialize config from a dictionary, ignoring unknown keys."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> CoverConfig:
        return cls.from_dict(json.loads(json_str))

    @property
    def material_spec(self) -> MaterialSpec:
        """Look up the active material specification."""
        if self.print_material not in MATERIAL_LIBRARY:
            raise ValueError(
                f"Unknown material '{self.print_material}'. "
                f"Available: {list(MATERIAL_LIBRARY.keys())}"
            )
        return MATERIAL_LIBRARY[self.print_material]

    def validate(self) -> list[str]:
        """Validate all config parameters. Returns a list of error messages (empty if valid)."""
        errors: list[str] = []

        # Dimensional checks
        if self.clearance_offset_mm < 0:
            errors.append("clearance_offset_mm must be non-negative")
        if self.clearance_offset_mm > 20.0:
            errors.append("clearance_offset_mm > 20 mm is unusually large")
        if self.shell_thickness_mm <= 0:
            errors.append("shell_thickness_mm must be positive")
        if self.shell_thickness_mm > 15.0:
            errors.append("shell_thickness_mm > 15 mm is unusually large")
        if self.min_feature_size_mm <= 0:
            errors.append("min_feature_size_mm must be positive")
        if self.min_bridge_width_mm <= 0:
            errors.append("min_bridge_width_mm must be positive")

        # Coverage
        if self.coverage_extent not in ("full", "partial", "minimal"):
            errors.append(
                f"coverage_extent must be 'full', 'partial', or 'minimal', got '{self.coverage_extent}'"
            )

        # Style
        valid_styles = ("smooth", "faceted", "perforated", "lattice", "organic", "panelized")
        if self.style_family not in valid_styles:
            errors.append(f"style_family must be one of {valid_styles}, got '{self.style_family}'")

        # Perforation
        if not 0.0 <= self.perforation_density <= 1.0:
            errors.append("perforation_density must be between 0.0 and 1.0")
        valid_perf_shapes = ("circle", "hex", "diamond", "voronoi", "organic")
        if self.perforation_shape not in valid_perf_shapes:
            errors.append(
                f"perforation_shape must be one of {valid_perf_shapes}, "
                f"got '{self.perforation_shape}'"
            )

        # Attachment
        valid_attach = ("snap_clip", "magnet", "screw", "adhesive")
        if self.attachment_type not in valid_attach:
            errors.append(
                f"attachment_type must be one of {valid_attach}, got '{self.attachment_type}'"
            )

        # Split
        valid_splits = ("none", "medial_lateral", "anterior_posterior", "three_piece")
        if self.split_strategy not in valid_splits:
            errors.append(
                f"split_strategy must be one of {valid_splits}, got '{self.split_strategy}'"
            )

        # Processing
        if self.smoothing_iterations < 0:
            errors.append("smoothing_iterations must be non-negative")

        # Anatomy
        if self.prosthesis_type not in ("transtibial", "transfemoral"):
            errors.append(
                f"prosthesis_type must be 'transtibial' or 'transfemoral', "
                f"got '{self.prosthesis_type}'"
            )
        if self.side not in ("auto", "left", "right"):
            errors.append(f"side must be 'auto', 'left', or 'right', got '{self.side}'")

        # Material
        if self.print_material not in MATERIAL_LIBRARY:
            errors.append(
                f"Unknown print_material '{self.print_material}'. "
                f"Available: {list(MATERIAL_LIBRARY.keys())}"
            )
        else:
            mat = self.material_spec
            if self.shell_thickness_mm < mat.min_wall_thickness:
                errors.append(
                    f"shell_thickness_mm ({self.shell_thickness_mm}) is below material minimum "
                    f"wall thickness ({mat.min_wall_thickness}) for {self.print_material}"
                )
            if self.min_feature_size_mm < mat.min_feature_size:
                errors.append(
                    f"min_feature_size_mm ({self.min_feature_size_mm}) is below material minimum "
                    f"feature size ({mat.min_feature_size}) for {self.print_material}"
                )

        # Print settings
        if self.layer_height_mm <= 0:
            errors.append("layer_height_mm must be positive")
        if not 0 <= self.infill_percent <= 100:
            errors.append("infill_percent must be between 0 and 100")

        return errors

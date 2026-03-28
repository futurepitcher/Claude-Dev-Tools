"""Tests for engine.config -- CoverConfig, MaterialSpec, and MATERIAL_LIBRARY."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.config import CoverConfig, MaterialSpec, MATERIAL_LIBRARY


# ---------------------------------------------------------------------------
# MaterialSpec
# ---------------------------------------------------------------------------

class TestMaterialSpec:
    def test_create_material(self):
        mat = MaterialSpec(
            name="TestMat",
            min_wall_thickness=1.0,
            min_feature_size=0.5,
            max_bridge_span=20.0,
            density_g_per_cm3=1.10,
        )
        assert mat.name == "TestMat"
        assert mat.min_wall_thickness == 1.0
        assert mat.max_overhang_angle_deg == 45.0  # default

    def test_to_dict(self):
        mat = MaterialSpec(
            name="X",
            min_wall_thickness=0.8,
            min_feature_size=0.4,
            max_bridge_span=10.0,
            density_g_per_cm3=1.0,
        )
        d = mat.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "X"
        assert d["density_g_per_cm3"] == 1.0

    def test_material_library_has_expected_keys(self):
        expected = {
            "PA12_nylon", "PA11_nylon", "PLA", "PETG",
            "TPU_95A", "resin_standard", "resin_tough",
        }
        assert expected.issubset(set(MATERIAL_LIBRARY.keys()))

    def test_all_materials_have_positive_wall_thickness(self):
        for key, mat in MATERIAL_LIBRARY.items():
            assert mat.min_wall_thickness > 0, f"{key} has invalid min_wall_thickness"

    def test_all_materials_have_positive_density(self):
        for key, mat in MATERIAL_LIBRARY.items():
            assert mat.density_g_per_cm3 > 0, f"{key} has invalid density"

    def test_all_materials_have_names(self):
        for key, mat in MATERIAL_LIBRARY.items():
            assert len(mat.name) > 0, f"{key} is missing a name"

    def test_material_to_dict_has_all_fields(self):
        mat = MATERIAL_LIBRARY["PA12_nylon"]
        d = mat.to_dict()
        assert "name" in d
        assert "min_wall_thickness" in d
        assert "min_feature_size" in d
        assert "max_bridge_span" in d
        assert "density_g_per_cm3" in d
        assert "max_overhang_angle_deg" in d
        assert "description" in d


# ---------------------------------------------------------------------------
# CoverConfig -- creation
# ---------------------------------------------------------------------------

class TestCoverConfigCreation:
    def test_defaults(self):
        cfg = CoverConfig()
        assert cfg.clearance_offset_mm == 2.0
        assert cfg.shell_thickness_mm == 3.0
        assert cfg.style_family == "smooth"
        assert cfg.prosthesis_type == "transtibial"
        assert cfg.side == "auto"
        assert cfg.print_material == "PA12_nylon"

    def test_custom_values(self):
        cfg = CoverConfig(
            clearance_offset_mm=3.0,
            shell_thickness_mm=4.0,
            style_family="perforated",
            perforation_shape="hex",
        )
        assert cfg.clearance_offset_mm == 3.0
        assert cfg.perforation_shape == "hex"

    def test_material_spec_property(self):
        cfg = CoverConfig(print_material="PLA")
        mat = cfg.material_spec
        assert mat.name == "PLA (FDM)"
        assert mat.min_wall_thickness == 1.2

    def test_unknown_material_raises(self):
        cfg = CoverConfig(print_material="unobtanium")
        with pytest.raises(ValueError, match="Unknown material"):
            _ = cfg.material_spec


# ---------------------------------------------------------------------------
# CoverConfig -- serialization
# ---------------------------------------------------------------------------

class TestCoverConfigSerialization:
    def test_to_dict_roundtrip(self):
        cfg = CoverConfig(shell_thickness_mm=5.0, style_family="lattice")
        d = cfg.to_dict()
        cfg2 = CoverConfig.from_dict(d)
        assert cfg2.shell_thickness_mm == 5.0
        assert cfg2.style_family == "lattice"

    def test_to_json_roundtrip(self):
        cfg = CoverConfig(perforation_density=0.6, side="left")
        json_str = cfg.to_json()
        cfg2 = CoverConfig.from_json(json_str)
        assert cfg2.perforation_density == 0.6
        assert cfg2.side == "left"

    def test_from_dict_ignores_unknown_keys(self):
        d = {"shell_thickness_mm": 4.0, "unknown_key": 999}
        cfg = CoverConfig.from_dict(d)
        assert cfg.shell_thickness_mm == 4.0
        assert not hasattr(cfg, "unknown_key")

    def test_json_is_valid(self):
        cfg = CoverConfig()
        parsed = json.loads(cfg.to_json())
        assert isinstance(parsed, dict)
        assert "clearance_offset_mm" in parsed

    def test_all_fields_present_in_dict(self):
        cfg = CoverConfig()
        d = cfg.to_dict()
        assert "clearance_offset_mm" in d
        assert "shell_thickness_mm" in d
        assert "style_family" in d
        assert "prosthesis_type" in d
        assert "print_material" in d
        assert "attachment_type" in d
        assert "split_strategy" in d

    def test_from_dict_preserves_all_defaults(self):
        """from_dict with empty dict should give all defaults."""
        cfg = CoverConfig.from_dict({})
        default = CoverConfig()
        assert cfg.to_dict() == default.to_dict()


# ---------------------------------------------------------------------------
# CoverConfig -- validation
# ---------------------------------------------------------------------------

class TestCoverConfigValidation:
    def test_valid_default_config(self):
        cfg = CoverConfig()
        errors = cfg.validate()
        assert errors == [], f"Default config should be valid but got: {errors}"

    def test_negative_clearance(self):
        cfg = CoverConfig(clearance_offset_mm=-1.0)
        errors = cfg.validate()
        assert any("clearance_offset_mm" in e for e in errors)

    def test_excessive_clearance(self):
        cfg = CoverConfig(clearance_offset_mm=25.0)
        errors = cfg.validate()
        assert any("unusually large" in e for e in errors)

    def test_zero_shell_thickness(self):
        cfg = CoverConfig(shell_thickness_mm=0.0)
        errors = cfg.validate()
        assert any("shell_thickness_mm must be positive" in e for e in errors)

    def test_excessive_shell_thickness(self):
        cfg = CoverConfig(shell_thickness_mm=20.0)
        errors = cfg.validate()
        assert any("unusually large" in e for e in errors)

    def test_invalid_style_family(self):
        cfg = CoverConfig(style_family="gothic")
        errors = cfg.validate()
        assert any("style_family" in e for e in errors)

    def test_invalid_coverage_extent(self):
        cfg = CoverConfig(coverage_extent="mega")
        errors = cfg.validate()
        assert any("coverage_extent" in e for e in errors)

    def test_perforation_density_out_of_range(self):
        cfg = CoverConfig(perforation_density=1.5)
        errors = cfg.validate()
        assert any("perforation_density" in e for e in errors)

    def test_perforation_density_negative(self):
        cfg = CoverConfig(perforation_density=-0.1)
        errors = cfg.validate()
        assert any("perforation_density" in e for e in errors)

    def test_invalid_perforation_shape(self):
        cfg = CoverConfig(perforation_shape="star")
        errors = cfg.validate()
        assert any("perforation_shape" in e for e in errors)

    def test_invalid_attachment_type(self):
        cfg = CoverConfig(attachment_type="glue_gun")
        errors = cfg.validate()
        assert any("attachment_type" in e for e in errors)

    def test_invalid_split_strategy(self):
        cfg = CoverConfig(split_strategy="random_cut")
        errors = cfg.validate()
        assert any("split_strategy" in e for e in errors)

    def test_invalid_prosthesis_type(self):
        cfg = CoverConfig(prosthesis_type="transhumeral")
        errors = cfg.validate()
        assert any("prosthesis_type" in e for e in errors)

    def test_invalid_side(self):
        cfg = CoverConfig(side="center")
        errors = cfg.validate()
        assert any("side" in e for e in errors)

    def test_shell_below_material_minimum(self):
        # PLA min wall thickness is 1.2
        cfg = CoverConfig(print_material="PLA", shell_thickness_mm=0.5)
        errors = cfg.validate()
        assert any("below material minimum" in e for e in errors)

    def test_feature_size_below_material_minimum(self):
        # PLA min feature size is 1.0
        cfg = CoverConfig(print_material="PLA", min_feature_size_mm=0.3)
        errors = cfg.validate()
        assert any("below material minimum" in e.lower() or "feature size" in e.lower()
                    for e in errors)

    def test_negative_smoothing_iterations(self):
        cfg = CoverConfig(smoothing_iterations=-1)
        errors = cfg.validate()
        assert any("smoothing_iterations" in e for e in errors)

    def test_invalid_infill(self):
        cfg = CoverConfig(infill_percent=150)
        errors = cfg.validate()
        assert any("infill_percent" in e for e in errors)

    def test_negative_layer_height(self):
        cfg = CoverConfig(layer_height_mm=-0.1)
        errors = cfg.validate()
        assert any("layer_height_mm" in e for e in errors)

    def test_unknown_material_in_validation(self):
        cfg = CoverConfig(print_material="moon_rock")
        errors = cfg.validate()
        assert any("Unknown" in e or "print_material" in e for e in errors)

    def test_multiple_errors_at_once(self):
        cfg = CoverConfig(
            clearance_offset_mm=-1.0,
            shell_thickness_mm=0.0,
            style_family="invalid",
            prosthesis_type="invalid",
        )
        errors = cfg.validate()
        assert len(errors) >= 4

    def test_valid_config_all_materials(self):
        """Every material in the library should produce a valid default config."""
        for mat_key in MATERIAL_LIBRARY:
            cfg = CoverConfig(print_material=mat_key)
            errors = cfg.validate()
            assert errors == [], f"Config with {mat_key} should be valid: {errors}"

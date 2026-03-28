# Prosthetic Cover Design System -- Workflow Guide

A complete reference for prosthetists, designers, and technicians using the
prosthetic cover engine to generate custom 3D-printed aesthetic covers for
lower-limb prostheses.

---

## Table of Contents

1. [Overview](#overview)
2. [Scan-to-STL Workflow](#scan-to-stl-workflow)
3. [Parameter Reference](#parameter-reference)
4. [Style Families](#style-families)
5. [Material Selection Guide](#material-selection-guide)
6. [Attachment Strategy Guide](#attachment-strategy-guide)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The prosthetic cover engine takes a 3D scan of an existing prosthesis (pylon,
socket, and/or componentry) and generates a printable aesthetic shell that fits
over it. The pipeline handles:

- Scan intake and validation
- Mesh cleanup and repair
- Anatomical alignment via PCA
- Region marking (coverage zones, joint areas, no-go zones)
- Envelope and shell generation
- Aesthetic feature application (perforations, lattice, faceting, etc.)
- Attachment point creation
- Print-readiness validation
- STL/OBJ export

---

## Scan-to-STL Workflow

### Step 1: Acquire the Scan

Scan the assembled prosthesis with the patient wearing it in their normal
standing alignment. Recommended scanning methods:

- **Structured-light scanner** (Artec Eva, EinScan): best accuracy, 0.1-0.3 mm
- **Photogrammetry** (smartphone-based): acceptable for prototyping, 0.5-1.0 mm
- **LiDAR** (iPad Pro, iPhone Pro): good for quick captures, 0.3-0.5 mm

Export the scan as STL (binary preferred for smaller file size), OBJ, or PLY.
Ensure the file is in **millimeters**.

### Step 2: Load the Configuration

Start with one of the default configurations:

```python
import json
from engine.config import CoverConfig

# Load a preset
with open("configs/default_transtibial.json") as f:
    config = CoverConfig.from_dict(json.load(f))

# Or create from scratch
config = CoverConfig(
    prosthesis_type="transtibial",
    shell_thickness_mm=3.0,
    style_family="perforated",
    perforation_shape="hex",
    print_material="PA12_nylon",
)

# Validate before proceeding
errors = config.validate()
if errors:
    print("Configuration errors:", errors)
```

### Step 3: Run the Pipeline

```python
from engine.pipeline import CoverPipeline

pipeline = CoverPipeline(config)

# Stage 1: Load scan
pipeline.run_stage("load_scan", filepath="patient_scan.stl")

# Stage 2: Clean up (repair holes, fix normals, decimate if needed)
pipeline.run_stage("cleanup")

# Stage 3: Align to anatomical frame (PCA-based)
pipeline.run_stage("align")

# Stage 4: Mark regions (coverage, joints, transitions)
pipeline.run_stage("mark_regions")

# Stage 5: Generate offset envelope
pipeline.run_stage("generate_envelope")

# Stage 6: Create shell from envelope
pipeline.run_stage("generate_shell")

# Stage 7: Apply aesthetic features
pipeline.run_stage("apply_aesthetics")

# Stage 8: Add attachment points
pipeline.run_stage("add_attachments")

# Stage 9: Validate for printability
pipeline.run_stage("validate")

# Stage 10: Export
pipeline.run_stage("export", output_path="cover_final.stl")
```

### Step 4: Review the Report

```python
report = pipeline.get_report()
print(f"Wall thickness check: {report.get('validation', {}).get('wall_ok')}")
print(f"Estimated weight: {report.get('weight_grams', 'N/A')} g")
print(f"Face count: {report.get('export', {}).get('face_count')}")
```

### Step 5: Print and Fit

- Slice the exported STL with your slicer of choice
- Use the material-specific print settings (see Material Selection Guide)
- After printing, verify fit on the prosthesis before delivery to the patient

---

## Parameter Reference

### Geometry Parameters

| Parameter              | Type   | Default | Range        | Description                                   |
|------------------------|--------|---------|--------------|-----------------------------------------------|
| clearance_offset_mm    | float  | 2.0     | 0.0 -- 20.0  | Gap between prosthesis surface and inner shell |
| shell_thickness_mm     | float  | 3.0     | 0.6 -- 15.0  | Wall thickness of the cover shell              |
| min_feature_size_mm    | float  | 1.5     | 0.3 -- 10.0  | Smallest geometric feature allowed             |
| min_bridge_width_mm    | float  | 2.0     | 1.0 -- 10.0  | Minimum width of material between perforations |

### Coverage Parameters

| Parameter        | Type   | Default | Options                   | Description                          |
|------------------|--------|---------|---------------------------|--------------------------------------|
| coverage_extent  | string | "full"  | full, partial, minimal    | How much of the prosthesis to cover  |
| prosthesis_type  | string | "transtibial" | transtibial, transfemoral | Type of amputation level       |
| side             | string | "auto"  | auto, left, right         | Which leg (auto-detected from scan)  |

### Aesthetic Parameters

| Parameter            | Type   | Default  | Options                                      | Description                       |
|----------------------|--------|----------|----------------------------------------------|-----------------------------------|
| style_family         | string | "smooth" | smooth, faceted, perforated, lattice, organic, panelized | Visual style preset   |
| perforation_density  | float  | 0.3      | 0.0 -- 1.0                                   | Fraction of surface to perforate  |
| perforation_shape    | string | "circle" | circle, hex, diamond, voronoi, organic        | Shape of perforation cutouts      |

### Attachment Parameters

| Parameter       | Type   | Default      | Options                                              | Description               |
|-----------------|--------|--------------|------------------------------------------------------|---------------------------|
| attachment_type | string | "snap_clip"  | snap_clip, magnet, screw, adhesive                   | How the cover attaches    |
| split_strategy  | string | "none"       | none, medial_lateral, anterior_posterior, three_piece | How the cover splits open |

### Processing Parameters

| Parameter            | Type | Default | Range      | Description                    |
|----------------------|------|---------|------------|--------------------------------|
| smoothing_iterations | int  | 3       | 0 -- 100   | Laplacian smoothing passes     |
| layer_height_mm      | float| 0.2     | 0.05 -- 0.5| Print layer height             |
| infill_percent       | int  | 20      | 0 -- 100   | Interior fill percentage       |
| print_material       | string| "PA12_nylon" | See materials | Target print material   |

---

## Style Families

### Smooth

A clean, anatomical shell that closely follows the body contour. No surface
features or cutouts. Best for users who prefer a discreet, natural appearance.

- **Best materials**: Any
- **Weight**: Heaviest (no material removal)
- **Ventilation**: None
- **Print difficulty**: Easy

### Perforated (Hexagonal)

A structured grid of hexagonal cutouts that reduce weight by 25-40% while
providing ventilation. The pattern can include a density gradient that
transitions from dense at the edges to open in the center.

- **Best materials**: PA12 Nylon (SLS), Tough Resin (SLA)
- **Weight**: Light (25-40% reduction)
- **Ventilation**: Good
- **Print difficulty**: Moderate (bridge widths must be respected)

### Lattice (Geometric)

An open lattice structure with repeating geometric cells (diamond, cubic, or
octet). Provides the maximum weight reduction and ventilation at the cost of
reduced structural rigidity.

- **Best materials**: PA12 Nylon (SLS) only
- **Weight**: Lightest (40-60% reduction)
- **Ventilation**: Excellent
- **Print difficulty**: Hard (requires SLS or SLA)

### Faceted (Low-Poly)

A geometric, angular aesthetic created by aggressive mesh decimation. The flat
triangular facets create a modern, digital-art appearance. No material is
removed, so structural integrity is maintained.

- **Best materials**: Any (especially good on FDM)
- **Weight**: Same as smooth
- **Ventilation**: None
- **Print difficulty**: Easy

### Organic (Flowing)

Nature-inspired forms with smooth undulating surfaces and Voronoi-based cutout
patterns reminiscent of bones, coral, or leaf veins. Features variable
thickness and flowing edges.

- **Best materials**: PA12 Nylon (SLS), Standard/Tough Resin (SLA)
- **Weight**: Moderate (20-35% reduction)
- **Ventilation**: Moderate
- **Print difficulty**: Hard (fine organic details)

### Panelized (Sport)

A dynamic, athletic aesthetic with defined panel lines, chamfered edges, and
angular vents. Inspired by automotive body panels and sportswear. Features
accent lines and directional air intakes.

- **Best materials**: Any
- **Weight**: Moderate (10-20% reduction from vents)
- **Ventilation**: Moderate (directional)
- **Print difficulty**: Moderate

---

## Material Selection Guide

### PA12 Nylon (SLS) -- Recommended

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 0.8 mm       |
| Min feature size       | 0.5 mm       |
| Max bridge span        | 50 mm        |
| Density                | 1.01 g/cm3   |
| Max overhang angle     | 90 deg (self-supporting) |

**Best for**: All style families. The gold standard for prosthetic covers.
Self-supporting powder bed allows complex geometries including lattice and
organic patterns. Excellent durability and slight flexibility.

### PA11 Nylon (SLS)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 0.8 mm       |
| Min feature size       | 0.5 mm       |
| Max bridge span        | 50 mm        |
| Density                | 1.03 g/cm3   |
| Max overhang angle     | 90 deg       |

**Best for**: Same applications as PA12 but with slightly more flexibility and
impact resistance. Bio-based feedstock. Good choice when the cover needs to
absorb minor impacts without cracking.

### PLA (FDM)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 1.2 mm       |
| Min feature size       | 1.0 mm       |
| Max bridge span        | 10 mm        |
| Density                | 1.24 g/cm3   |
| Max overhang angle     | 45 deg       |

**Best for**: Prototyping and low-cost production. Works well with smooth and
faceted styles. Avoid complex perforations or lattice due to bridging
limitations. Not recommended for daily wear due to brittleness.

### PETG (FDM)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 1.2 mm       |
| Min feature size       | 1.0 mm       |
| Max bridge span        | 12 mm        |
| Density                | 1.27 g/cm3   |
| Max overhang angle     | 50 deg       |

**Best for**: Functional FDM covers with better toughness than PLA. Good
chemical resistance (survives cleaning products). Suitable for smooth, faceted,
and panelized styles.

### TPU 95A (FDM)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 1.5 mm       |
| Min feature size       | 1.5 mm       |
| Max bridge span        | 8 mm         |
| Density                | 1.21 g/cm3   |
| Max overhang angle     | 40 deg       |

**Best for**: Flexible gaskets, comfort pads, and interface liners. Not
typically used for the main cover shell but excellent for inner cushioning
layers and edge seals.

### Standard Resin (SLA)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 0.6 mm       |
| Min feature size       | 0.3 mm       |
| Max bridge span        | 15 mm        |
| Density                | 1.18 g/cm3   |
| Max overhang angle     | 35 deg       |

**Best for**: High-detail organic and perforated patterns. Excellent surface
finish. Limited build volume may require splitting. Brittle under impact.

### Tough Resin (SLA)

| Property               | Value        |
|------------------------|--------------|
| Min wall thickness     | 0.8 mm       |
| Min feature size       | 0.4 mm       |
| Max bridge span        | 15 mm        |
| Density                | 1.15 g/cm3   |
| Max overhang angle     | 35 deg       |

**Best for**: When SLA detail is desired but more impact resistance is needed.
Good for organic and perforated styles. Better durability than standard resin.

---

## Attachment Strategy Guide

### Snap Clips (Default)

Integrated snap-fit clips that grip onto the prosthesis pylon or socket edge.

- **Pros**: No hardware needed, easy on/off, low cost
- **Cons**: Clips can fatigue over time, requires precise fit
- **Best split**: medial_lateral or anterior_posterior
- **Recommended material**: PA12 Nylon (flexibility for snap action)

### Magnets

Embedded magnet pockets in the cover and corresponding magnets on the prosthesis.

- **Pros**: Clean look, easy on/off, self-aligning
- **Cons**: Requires magnet installation, adds cost, potential MRI concerns
- **Best split**: medial_lateral
- **Recommended material**: Any (magnets are post-inserted)

### Screws

Threaded inserts in the cover that accept machine screws through mounting tabs.

- **Pros**: Most secure, adjustable, repairable
- **Cons**: Requires tools, visible hardware, risk of loosening
- **Best split**: any
- **Recommended material**: PA12 Nylon or PETG (good thread retention)

### Adhesive

Hook-and-loop (Velcro) or adhesive pads for semi-permanent attachment.

- **Pros**: Simple, no precision features needed, forgiving of fit errors
- **Cons**: Less secure, adhesive can degrade, adds thickness
- **Best split**: medial_lateral
- **Recommended material**: Any

---

## Troubleshooting

### Scan Issues

**Problem**: "Mesh is not watertight" warning during intake.
**Solution**: This is common with raw scans. The cleanup stage will attempt
automatic repair. If repair fails, try:
1. Re-scanning with more overlap between scan passes
2. Using the scanner's built-in mesh repair tools before export
3. Cleaning the mesh manually in MeshLab or Meshmixer

**Problem**: "Mesh appears to be in meters/centimeters" warning.
**Solution**: The pipeline expects millimeters. Either re-export from the
scanner in mm, or scale the mesh:
```python
mesh.apply_scale(1000.0)  # meters to mm
mesh.apply_scale(10.0)    # cm to mm
```

**Problem**: "Very high vertex count" warning.
**Solution**: The cleanup stage will decimate automatically if face count
exceeds 500,000. For very large scans (>5M faces), consider pre-decimating
in external software.

### Alignment Issues

**Problem**: Cover is oriented incorrectly after alignment.
**Solution**: PCA alignment depends on the mesh being roughly elongated along
one axis. If the scan includes the foot or extensive socket brim, the long
axis detection may fail. Try:
1. Trimming the scan to only the pylon/socket segment before loading
2. Manually specifying the side parameter instead of "auto"

**Problem**: Side auto-detection returns "unknown".
**Solution**: The auto-detection relies on geometric asymmetry. Perfectly
cylindrical pylons have no asymmetry to detect. Set `side="left"` or
`side="right"` manually in the config.

### Print Issues

**Problem**: Slicer reports thin wall errors.
**Solution**: Increase `shell_thickness_mm` to at least the material's
minimum wall thickness (see Material Selection Guide). Also check that
`min_bridge_width_mm` is sufficient for perforated/lattice styles.

**Problem**: Cover does not fit over the prosthesis.
**Solution**: Increase `clearance_offset_mm`. The default 2.0 mm works for
most cases, but rough surfaces, protruding screws, or thick socks may require
3.0-5.0 mm.

**Problem**: Cover is too heavy.
**Solution**: Options to reduce weight:
1. Switch to a perforated or lattice style
2. Reduce `shell_thickness_mm` (within material limits)
3. Use `coverage_extent: "partial"` to cover less area
4. Switch to a lighter material (PA12 is lighter than PLA/PETG)

**Problem**: Perforations or lattice struts break during printing.
**Solution**:
1. Increase `min_bridge_width_mm` (try 3.0-4.0 mm)
2. Reduce `perforation_density`
3. Switch to SLS (PA12) which handles fine features better than FDM
4. Increase `lattice_strut_diameter_mm` for lattice styles

### Pipeline Errors

**Problem**: "Cannot run stage X before stage Y" error.
**Solution**: Pipeline stages must run in order. The required sequence is:
load_scan -> cleanup -> align -> mark_regions -> generate_envelope ->
generate_shell -> apply_aesthetics -> add_attachments -> validate -> export.

**Problem**: Configuration validation errors.
**Solution**: Run `config.validate()` before starting the pipeline. The
returned error list describes each problem and how to fix it.

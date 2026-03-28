# Prosthetic Cover Design System

A profession-specific Claude Code skill and computational geometry engine for designing custom 3D-printed aesthetic covers for lower-limb prostheses.

## What This Is

This is not a generic CAD tool. It is a **scan-to-STL design pipeline** purpose-built for prosthetic cover designers who create custom aesthetic covers for below-knee (transtibial) and above-knee (transfemoral) prostheses.

The system turns this workflow:

```
3D scan of prosthesis
→ mesh cleanup and repair
→ anatomical alignment
→ region marking (coverage, no-go, joints)
→ clearance envelope generation
→ shell creation with wall thickness
→ aesthetic pattern application
→ attachment and split logic
→ printability validation
→ manufacturable STL export
```

into a guided, repeatable, designer-controlled pipeline.

## Components

### Claude Code Skill (`/prosthetic-cover`)

The skill provides an interactive design workflow within Claude Code:

```
/prosthetic-cover new --scan_path ./scan.stl --style perforated --prosthesis_type transtibial
/prosthetic-cover configure
/prosthetic-cover validate
/prosthetic-cover export
```

### Python Engine (`engine/`)

The computational geometry pipeline with modular stages:

| Module | Purpose |
|--------|---------|
| `intake` | Load and validate 3D scans (STL/OBJ/PLY) |
| `cleanup` | Repair non-manifold, fill holes, smooth, decimate |
| `alignment` | PCA-based anatomical frame alignment |
| `regions` | Coverage zone, no-go zone, joint detection |
| `envelope` | Clearance offset shell generation |
| `shell` | Wall thickness shell with edge bridging |
| `aesthetics` | Style system — smooth, faceted, perforated, lattice, organic, panelized |
| `attachment` | Snap clips, magnetic mounts, split lines |
| `validation` | Watertight, wall thickness, feature size, printability checks |
| `export` | Binary STL + metadata JSON + design report |
| `preview` | Text-based design state preview |

### Style System

Six aesthetic families with configurable parameters:

- **Smooth** — Clean anatomical silhouette, polished contours
- **Faceted** — Low-poly geometric aesthetic
- **Perforated** — Pattern cutouts (circle, hex, diamond, voronoi, organic)
- **Lattice** — Structural lattice patterns with configurable cell size
- **Organic** — Biomorphic flowing forms
- **Panelized** — Multi-panel construction with reveal gaps

### Configuration Presets

Pre-configured settings in `configs/`:

- `default_transtibial.json` — Below-knee defaults
- `default_transfemoral.json` — Above-knee defaults
- `styles/*.json` — Style family presets

## Installation

```bash
# Install the skill to your Claude Code configuration
cd /path/to/Claude-Dev-Tools
./install.sh --all --global

# Install Python dependencies for the engine
cd packages/prosthetic-cover
pip install -e .
```

## Requirements

- Python 3.10+
- trimesh
- numpy
- scipy

## Design Philosophy

1. **Designer control** — Never auto-advance without confirmation
2. **Fit first** — Clearance and comfort before aesthetics
3. **Print-ready** — Every output must be manufacturable
4. **Profession-specific** — Built for prosthetic designers, not generic CAD users
5. **Repeatable** — Same inputs, same outputs, configurable parameters

## Output

Each design produces:

- `cover.stl` — Watertight manifold mesh ready for slicing
- `cover_metadata.json` — Full parameter record, measurements, warnings
- `cover_report.md` — Human-readable design summary

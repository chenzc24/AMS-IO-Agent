# Shape-Specific Modules Index (03_Shape_Specifics)

This directory contains shape-specific knowledge modules for different capacitor structures.

## 📖 Shape Selection Guide

**NEW**: See `SHAPE_SELECTION_GUIDE.md` for guidance on choosing the appropriate capacitor shape based on:
- Finger count requirements (odd vs even)
- Via topology complexity
- **Low parasitic requirements** (use Sandwich for minimal ground parasitics)
- Application type (RF, ADC/DAC, general analog)
- Technology node constraints

## Available Shapes

### H-shape Capacitor
- **Directory**: `H_Shape/`
- **Structure module**: `03_01_H_Shape_Structure.md`
  - Geometry specification and drawing procedures
  - Applies to all technology nodes
- **Dummy module**: `03_02_H_Shape_Dummy_Generation.md`
  - Dummy capacitor generation rules
  - Geometric transformation specifications

### I-Type Capacitor
- **Directory**: `I_Type/`
- **Structure module**: `03_01_I_Type_Structure.md`
  - Geometry specification and drawing procedures (alternating finger heights; no middle bar; top/bottom via rows only)
  - Applies to all technology nodes
- **Dummy module**: `03_02_I_Type_Dummy_Generation.md`
  - Dummy capacitor generation rules derived from finalized I-Type parameters
  - Deterministic transforms; no vias/pins; single-pass rendering

### Sandwich Capacitor

Sandwich capacitor structures are organized into two variants:

#### Sandwich Standard (5-layer structure)
- **Directory**: `Sandwich/Standard/`
- **Structure module**: `03_01_Sandwich_Standard_Structure.md`
  - Five-layer structure: L_top (solid plate), L_top2 (I-Type with shield), L_mid (quadrant-interdigitated core), L_bot2 (I-Type with shield), L_bot (solid plate)
  - Geometry specification and drawing procedures (BOT vias only; no vias on TOP fingers)
  - Applies to all technology nodes

#### Sandwich Simplified H-Notch (3-layer structure)
- **Directory**: `Sandwich/Simplified_H_Notch/`
- **Structure module**: `03_02_Sandwich_Simplified_H_Notch.md`
  - Three-layer structure: L_top/L_bot (solid plates), L_mid (outer frame with vertical notches + H-shape finger structure)
  - Geometry specification and drawing procedures (BOT vias only; vertical frame notches for horizontal bar passage)
  - Applies to all technology nodes
- **Dummy module**: `03_03_Sandwich_Simplified_H_Notch_Dummy_Generation.md`
  - Dummy capacitor generation rules for Simplified H-Notch variant
  - Geometric transformation specifications

### Future Shapes (when available)
- **U_Shape/** - U-shape capacitor structure
  - `03_01_U_Shape_Structure.md`
  - `03_02_U_Shape_Dummy_Generation.md`
- **C_Shape/** - C-shape capacitor structure
  - `03_01_C_Shape_Structure.md`
  - `03_02_C_Shape_Dummy_Generation.md`

## File Naming Convention

For each shape directory, use:
- `03_01_[SHAPE]_Structure.md` - Geometry specification and drawing procedures
- `03_02_[SHAPE]_Dummy_Generation.md` - Dummy capacitor generation rules
- Optional: `03_03_[SHAPE]_Optimization.md` - Shape-specific optimization strategies
- Optional: `03_04_[SHAPE]_Constraints.md` - Shape-specific constraints

## Directory Structure

Each shape has its own subdirectory containing:
- `03_01_[SHAPE]_Structure.md` - Structure definition
- `03_02_[SHAPE]_Dummy_Generation.md` - Dummy generation rules
- Optional: Additional modules (Optimization, Constraints, etc.)

## Usage

Combine shape-specific modules with universal modules (00-02, 04) and technology configs. See `KB_INDEX.md` for complete module combination examples.

## Related Documents

- **KB_INDEX.md** - Main knowledge base index with module combinations

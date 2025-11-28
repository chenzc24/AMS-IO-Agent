# 180nm Technology Configuration - Process-specific parameters (DRC: ≥0.28µm, Metals: METAL1-METAL5, Via pitch: 0.52µm)

This document defines the 180nm process-specific parameters and constraints for capacitor design.

## Overview

This configuration applies to all capacitor designs targeting the 180nm technology node. Refer to the shape-specific structure documents under `03_Shape_Specifics/` for geometric definitions, and the generic workflow documents (e.g., `01_Workflow_Framework.md`) for execution procedures.

---

## DRC Rules

### Minimum Dimensions
- **Minimum spacing**: ≥ 0.28 µm
  - Applies to: finger_d, frame_to_finger_d, spacing, and all other spacing parameters
- **Minimum width**: ≥ 0.28 µm
  - Applies to: frame_vertical_width, finger_vertical_width, frame_horizontal_width, middle_horizontal_width, and all other width parameters

### Width Quantization
- **Horizontal widths**: Quantized as `0.38 + 0.52×n` (where n ∈ N)
  - Examples: 0.38 µm, 0.90 µm (0.38+0.52), 1.42 µm (0.38+2×0.52), etc.
  - Use quantized widths for clean via arrays and DRC compliance

---

## Via Parameters

### Via Array Sizing
- **Via pitch**: `pitch_cut ≈ 0.52` µm
- **Via margin**: `m ≈ 0.14` µm
- **Column count formula**: `cut_columns = max(1, floor((h_right_x - h_left_x + m) / pitch_cut))`
- **Row count formulas**:
  - Top/bottom: `cut_rows_topbot = max(1, floor((frame_horizontal_width + m)/pitch_cut))`
  - Middle: `cut_rows_mid = max(1, floor((middle_horizontal_width + m)/pitch_cut))`

### Width-to-Row Mapping
- With horizontal widths quantized as `0.38 + 0.52·n`, the via row count approximately follows: `rows ≈ floor((width + 0.14)/0.52)`
- Intuitive mapping: `rows ≈ n + 1` for the quantized sequence
- Examples:
  - 0.38 µm → 1 row
  - 0.90 µm (0.38+0.52) → 2 rows
  - 1.42 µm (0.38+2×0.52) → 3 rows
- Adjust based on actual DRC spacing/enclosure feedback

---

## Metal Layer Restrictions

### Allowed Metal Layers
- **Allowed**: METAL1, METAL2, METAL3, METAL4, METAL5
- **Forbidden**: METAL6 and above

### Low-Parasitic Mode (Optional)
- If low parasitic to ground is required:
  - **Forbidden**: METAL1 as capacitor plates
  - **Preferred**: METAL2–METAL5 within the allowed set
  - **Adjacency**: Prefer adjacent layer pairs for robust via definitions (e.g., METAL5↔METAL4, METAL4↔METAL3)
  - **Rationale**: Lower metals exhibit stronger coupling to substrate and routing congestion; mid–upper metals reduce parasitics

### Via Definition Naming
- Use `higher_lower` format (e.g., `METAL5_METAL4`, `METAL4_METAL3`)
- Ensure the viaDef exists in the technology file
- If non-adjacent layer choices are requested, verify that the required viaDef names exist in the tech

---

## Initial Parameters

Initial parameters are synthesized in Phase 1 from structure rules and these technology constraints

---

## Parameter Precision

- **Parameters**: Prefer two decimal places (e.g., 0.28, 2.00)
- **Coordinates**: Recommend 5 decimal places for geometric calculations (e.g., 1.23456)

---

## Constraint Validation

When validating parameters for 180nm technology, ensure:
- [ ] All spacings ≥ 0.28 µm
- [ ] All widths ≥ 0.28 µm
- [ ] Horizontal widths follow quantization: 0.38 + 0.52×n
- [ ] Metal layers restricted to METAL1–METAL5
- [ ] If low-parasitic mode: M1 excluded, layers are adjacent
- [ ] fingers is odd and ≥ 3
- [ ] If H_max is set: total height ≤ H_max (where height = h_height + 2·spacing + 2·frame_horizontal_width)

---

## Integration Notes

- This configuration is consumed by:
  - Shape-specific structure documents in `03_Shape_Specifics/` for geometric calculations
  - Workflow documents (e.g., `01_Workflow_Framework.md`) for validation checks
  - Python modules for constraint enforcement
- When designing for 180nm, always reference this document for process-specific values and rules.


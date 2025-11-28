# 28nm Technology Configuration - Process-specific parameters (DRC: ≥0.05µm, Metals: M1-M7, Via pitch: 0.13µm)

This document defines the 28nm process-specific parameters and constraints for capacitor design.

## Overview

This configuration applies to all capacitor designs targeting the 28nm technology node. Refer to the shape-specific structure documents under `03_Shape_Specifics/` for geometric definitions, and the generic workflow documents (e.g., `01_Workflow_Framework.md`) for execution procedures.

---

## DRC Rules

### Minimum Dimensions
- **Minimum spacing**: ≥ 0.05 µm
  - Applies to: finger_d and other internal spacing parameters within capacitor structures
- **Frame-to-finger spacing requirement**: ≥ 0.08 µm
  - **`frame_to_finger_d`**: The horizontal distance from outer frame vertical line to nearest finger must be ≥ 0.08 µm
  - This is stricter than the general minimum spacing (0.05 µm) to ensure proper clearance between the frame and internal fingers
- **Critical spacing requirement**: ≥ 0.1 µm
  - **CRITICAL**: The following spacing parameters must be ≥ 0.1 µm (stricter than general minimum):
    - **`spacing`** (H-shape/I-Type): Vertical gap from frame to active capacitor region (e.g., from bottom of top horizontal frame to top of H-shape region)
    - **Routing wire spacing**: Spacing from routing wire endpoints to other wires/lines/structures in CDAC arrays
    - **Any spacing involving connection points or endpoints**: Spacing between connection points (pins, vias, terminals) and adjacent structures
  - **Rationale**: These spacings involve connection points, endpoints, or critical structural boundaries that require extra clearance for DRC compliance and manufacturing robustness
  - This is stricter than the general minimum spacing (0.05 µm) to ensure proper clearance and DRC compliance
- **Minimum width**: ≥ 0.05 µm
  - Applies to: frame_vertical_width, finger_vertical_width, frame_horizontal_width, middle_horizontal_width, and all other width parameters
- **Minimum h_height requirement**: > 1 µm
  - **`h_height`**: The vertical length of the H-shape main plate (H-shape region) must be greater than 1 µm
  - This ensures sufficient capacitor plate area and proper structure formation

### Width Quantization
- **Horizontal widths**: Recommend ≥ 0.11 µm, commonly quantized as `0.11 + 0.13×n` (where n ∈ N)
  - Examples: 0.11 µm, 0.24 µm (0.11+0.13), 0.37 µm (0.11+2×0.13), etc.
  - Use quantized widths for clean via arrays and DRC compliance

### Finger Width Recommendation
- **Default finger_vertical_width**: Set to **0.05 µm** by default
  - Rationale: Keeps small-area designs compact and improves capacitance density
  - Only increase if required by DRC/EM/robustness or specific integration constraints
  - Note: Increasing `finger_vertical_width` typically reduces overall capacitance—avoid changing unless there is a clear, justified reason

### Minimum Area Rules
- If DRC flags minimum-area violations (e.g., per-polygon area < 0.017 µm²), these typically appear in the DRC report as `M?.A.1`
  - **First try (Phase 2 - Dummy capacitor)**: Consider reducing the outer frame shortening amount (`delta_x`)
    - Reduce the amount by which the outer frame is shortened in dummy capacitors
    - This increases the frame area and may resolve minimum area violations
    - Maintain all spacing constraints while adjusting frame shortening
  - **Second try (Phase 2 - Dummy capacitor)**: If frame shortening adjustment is insufficient, try conservative spacing reduction in Dummy geometry to merge/expand small polygons
    - **Note**: When reducing spacings, ensure all spacing constraints are maintained:
      - Critical spacings (≥0.1 µm) must be maintained
      - Frame-to-finger spacing (`frame_to_finger_d` ≥ 0.08 µm) must be maintained
      - Only internal spacings like `finger_d` (≥0.05 µm) can be reduced
  - **If fixes fail**: The root cause is likely the main capacitor geometry and a redesign is required
    - **Return to Phase 1** to adjust unit capacitor parameters with the minimum area issues elevated as constraints to be fixed

---

## Via Parameters

### Via Array Sizing
- **Via pitch**: `pitch_cut ≈ 0.13` µm
- **Via margin**: `m ≈ 0.02` µm
- **Column count formula**: `cut_columns = max(1, floor((h_right_x - h_left_x + m) / pitch_cut))`
- **Row count formulas**:
  - Top/bottom: `cut_rows_topbot = max(1, floor((frame_horizontal_width + m)/pitch_cut))`
  - Middle: `cut_rows_mid = max(1, floor((middle_horizontal_width + m)/pitch_cut))`

### Width-to-Row Mapping
- With horizontal widths quantized as `0.11 + 0.13·n`, the via row count approximately follows: `rows ≈ n+1`
- Examples:
  - 0.11 µm → 1 row
  - 0.24 µm (0.11+0.13) → 2 rows
  - 0.37 µm (0.11+2×0.13) → 3 rows
- Adjust based on actual DRC spacing/enclosure feedback

---

## Metal Layer Restrictions

### Allowed Metal Layers
- **Allowed**: M1, M2, M3, M4, M5, M6, M7
- **Forbidden**: M8 and above
- **Adjacency requirement**: Layers must be adjacent in pairs for robust via definitions

### Low-Parasitic Mode (Optional)
- If low parasitic to ground is required:
  - **Strictly forbidden**: M1 as capacitor plates
  - **Allowed**: M2, M3, M4, M5, M6, M7
  - **Adjacency**: Layers must be in adjacent pairs
  - **Rationale**: M1 (lowest) has much stronger parasitics to ground, can introduce coupling and congestion; prefer mid–upper layers (M2–M7)

### Layer Selection Guidance
- **General preference**: The lower the metal, the higher the parasitics; prefer higher metals first
- **Low-parasitic mode**: Prioritize M2–M7 over M1

### Via Definition Naming
- Use `higher_lower` format (e.g., `M7_M6`, `M6_M5`)
- Ensure the viaDef exists in the technology file
- Verify layers are adjacent; if non-adjacent choices are requested, verify that the required viaDef names exist in the tech

---

## Initial Parameters

Initial parameters are synthesized in Phase 1 from structure rules and these technology constraints

---

## Parameter Precision

- **Parameters**: Prefer two decimal places (e.g., 0.05, 0.75)
- **Coordinates**: Recommend 5 decimal places for geometric calculations (e.g., 0.12345)

---

## Constraint Validation

When validating parameters for 28nm technology, ensure:
- [ ] Internal spacings (finger_d) ≥ 0.05 µm
- [ ] Frame-to-finger spacing (`frame_to_finger_d`) ≥ 0.08 µm
- [ ] Critical spacings ≥ 0.1 µm:
  - [ ] `spacing` parameter (H-shape/I-Type: frame to active region gap) ≥ 0.1 µm
  - [ ] Routing wire spacing (endpoint to other wires/lines/structures) ≥ 0.1 µm
  - [ ] Any spacing involving connection points (pins, vias, terminals) ≥ 0.1 µm
- [ ] All widths ≥ 0.05 µm
- [ ] Horizontal widths follow quantization: 0.11 + 0.13×n (recommended)
- [ ] Metal layers restricted to M1–M7
- [ ] Layers are adjacent in pairs
- [ ] If low-parasitic mode: M1 excluded, layers are adjacent
- [ ] fingers is odd and ≥ 3
- [ ] `h_height` > 1 µm (vertical length of H-shape main plate)
- [ ] If H_max is set: total height ≤ H_max (where height = h_height + 2·spacing + 2·frame_horizontal_width)
- [ ] Minimum area rules satisfied (per-polygon area ≥ 0.017 µm² if applicable)

---

## Height Calculation Caution

- **Important**: `h_height` is NOT the same as `H_max`
  - `h_height`: Vertical length of the H-shape main plate (H-shape region)
  - `H_max`: Total height limit including frame and spacing
- **Conversion**: `height = h_height + 2·spacing + 2·frame_horizontal_width`
- When increasing capacitance via `h_height`, always recompute total height and ensure it stays ≤ H_max
- Before modifying any parameter that affects total height (`h_height`, `spacing`, `frame_horizontal_width`), compute height in advance

---

## Integration Notes

- This configuration is consumed by:
  - Shape-specific structure documents in `03_Shape_Specifics/` for geometric calculations
  - Workflow documents (e.g., `01_Workflow_Framework.md`) for validation checks
  - Python modules for constraint enforcement
- When designing for 28nm, always reference this document for process-specific values and rules.


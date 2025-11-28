# Sandwich Simplified H-Notch Dummy Capacitor Generation - Geometric transformation rules (Sandwich Simplified H-Notch specific, all technologies)

## Overview

This document describes the structural description and drawing rules for generating dummy unit capacitors used in capacitor arrays. The dummy capacitor is derived from the finalized Sandwich Simplified H-Notch unit capacitor design.

**Applicability**: This document is specific to Sandwich Simplified H-Notch capacitors. For other shapes, refer to their respective dummy generation rules.

---

## Key Points (Implementation Principles)

- **The Dummy capacitor must be generated only after** the unit capacitor iterative design is finalized (best iteration selected from Phase 1, Step 6).
- **No new explicit parameters**: The Dummy capacitor must share the exact same parameter set as the unit capacitor; do not add external flags such as `isDummy` or `dummyType`.
- **Dummy capacitor does not require iterative tuning**: Dummy geometry should be derived and rendered from the existing parameters in one pass; satisfying DRC is considered correct and no multi-round optimization (as for the unit capacitor) is required.

---

## Geometric Transforms and Drawing Rules

### General Principle

Only use derived quantities from the existing parameters (for example `half_width`, `half_height`, `outer_top`, `outer_bottom`, `h_top_y`, `h_bottom_y`, `upper_y`, `lower_y`, `notch_y1`, `notch_y2`); do not introduce new parameters. Create Dummy geometry by shortening or removing portions of these derived quantities.

---

### Top and Bottom Plate Handling

**Top and bottom plates are NOT shortened**: The top plate (`L_top`) and bottom plate (`L_bot`) maintain their full original dimensions in the dummy capacitor. Only the middle layer (frame and H-shape structure) is shortened to create visual distinction from the unit capacitor.

#### Drawing
- **Top plate** (`L_top`, BOT net): Draw rectangle with bbox `((-half_width, outer_bottom), (half_width, outer_top))` using `dbCreateRect` (same as unit capacitor).
- **Bottom plate** (`L_bot`, BOT net): Draw rectangle with the same bbox using `dbCreateRect` (same as unit capacitor).

---

### Finger Vertical Drawing — Dummy Behavior

#### Summary
The Dummy capacitor treats every finger identically (no odd/even distinction). Each finger is split into two segments (upper and lower) to avoid the middle horizontal bar. This is different from the unit capacitor where odd fingers span full height and even fingers are split.

#### Unit Capacitor (for reference)
- **Odd-index finger i**: One full segment from `(xi, h_bottom_y)` to `(xi, h_top_y)`.
- **Even-index finger i**: Two segments to avoid the middle bar:
  - Top segment: from `(xi, upper_y)` to `(xi, top_minus_frame)`
  - Bottom segment: from `(xi, bottom_minus_frame)` to `(xi, lower_y)`
- Where:
  - `upper_y = spacing + middle_horizontal_width/2`
  - `lower_y = -spacing - middle_horizontal_width/2`

#### Dummy Capacitor (MANDATORY Behavior)
For every finger index i (no parity):
- **Upper segment**: from `(xi, upper_y)` to `(xi, h_top_y)`
- **Lower segment**: from `(xi, h_bottom_y)` to `(xi, lower_y)`

That is, the Dummy uses `h_top_y` and `h_bottom_y` as the outer endpoints for the upper/lower segments respectively, and the inner cut positions are `upper_y` and `lower_y` (same formulas as MAIN). This produces equal-length, parallel trace arrays for all fingers.

#### Coordinate Ordering Validation (must hold numerically)
```
outer_top > top_minus_frame > h_top_y > upper_y > h_middle_y (0) > lower_y > h_bottom_y > bottom_minus_frame > outer_bottom
```

If this ordering does not hold for given parameters, the renderer must reject the Dummy generation and report a parameter violation.

#### SKILL Rendering Note
Compute and serialize all coordinates (`h_top_y`, `upper_y`, `lower_y`, `h_bottom_y`) as numeric literals (5 decimals) into the flattened SKILL; do NOT emit expressions or control flow to compute them in SKILL.

---

### Middle Horizontal Bar Handling

**Shorten the middle bar**: Shrink both left and right endpoints by:
```
delta_x_raw = min(0.15 · (half_width - (-half_width)), frame_to_finger_d)
delta_x = round(delta_x_raw / 0.005) * 0.005
```

Ensure the resulting delta is quantized to a multiple of `0.005` µm.

#### Derived Endpoints
```
dummy_bar_x_left  = -half_width + delta_x
dummy_bar_x_right = +half_width - delta_x
```

Ensure `dummy_bar_x_right > dummy_bar_x_left`.

#### Drawing
- Middle horizontal bar: draw path at `y = 0` from `x = dummy_bar_x_left` to `x = dummy_bar_x_right` with width `middle_horizontal_width`.
- The bar must still pass through the notch openings without touching the frame.

---

### Middle Frame Handling

The middle frame (`L_mid`, BOT net) is shortened to match the internal structure dimensions.

#### Frame Shortening
- **Horizontal frame bands**: Shortened to match the shortened middle bar width
  - Top horizontal band: from `(dummy_bar_x_left, outer_top - frame_width)` to `(dummy_bar_x_right, outer_top)`
  - Bottom horizontal band: from `(dummy_bar_x_left, outer_bottom)` to `(dummy_bar_x_right, outer_bottom + frame_width)`
- **Vertical frame bands**: Shortened to match the finger region height
  - Left vertical band with centered notch:
    - Bottom segment: from `(left_frame_x - frame_width/2, h_bottom_y)` to `(left_frame_x + frame_width/2, notch_y1)`
    - Top segment: from `(left_frame_x - frame_width/2, notch_y2)` to `(left_frame_x + frame_width/2, h_top_y)`
  - Right vertical band with centered notch (same pattern as left):
    - Bottom segment: from `(right_frame_x - frame_width/2, h_bottom_y)` to `(right_frame_x + frame_width/2, notch_y1)`
    - Top segment: from `(right_frame_x - frame_width/2, notch_y2)` to `(right_frame_x + frame_width/2, h_top_y)`

#### Key Points
- Vertical frames use the same Y range as the finger region (`h_bottom_y` to `h_top_y`), not the full device height
- Horizontal frames use the same X coordinates as the shortened middle bar (`dummy_bar_x_left` and `dummy_bar_x_right`)
- Notch openings remain centered at `y = 0` with height `notch_height = middle_horizontal_width + 2×spacing`
- This creates a smaller rectangular frame that aligns with the internal structure (fingers + middle bar), providing visual distinction while maintaining geometric consistency

---

### Dummy Horizontals Alignment — Required

1. Compute `delta_x_raw = min(0.15 · (half_width - (-half_width)), frame_to_finger_d)` and quantize `delta_x = round(delta_x_raw/0.005) * 0.005` (µm).

2. Derive unified endpoints once and reuse everywhere:
   - `dummy_bar_x_left  = -half_width + delta_x`
   - `dummy_bar_x_right = +half_width - delta_x` (ensure `dummy_bar_x_right > dummy_bar_x_left`)

3. Use the same pair `(dummy_bar_x_left, dummy_bar_x_right)` for:
   - Middle horizontal bar at y = 0
   - Top horizontal frame band
   - Bottom horizontal frame band

4. If the shortened length triggers DRC minimum width/area or conflicts:
   - Reduce `delta_x` conservatively (keeping 0.005 µm quantization)
   - If still failing, follow the Dummy DRC failure policy (treat MAIN as invalid and restart design)

---

### What NOT to Draw in Dummy Capacitor

- **Do not draw vias**
- **Do not draw pins**
- **Absolutely forbid changing the layer set** for Dummy generation

---

## Implementation Suggestions

The renderer may offer two independent paths:

1. **Unit capacitor path**: The existing multi-iteration optimization and rendering flow (Phase 1).
2. **Dummy capacitor path**: When generating Dummy capacitor (after unit capacitor final iteration):
   - Map unit capacitor parameters to Dummy geometry per this section
   - Emit a flattened SKILL script
   - Run DRC
   - If Dummy DRC fails, abort and treat the unit capacitor design as invalid
   - Restart the design process instead of tweaking Dummy-only knobs

**Remember**: Any Dummy capacitor transformation must not introduce new external parameters; all adjustments must be realized through derived quantities of the existing parameter set.

---

## Dummy Capacitor DRC Failure Policy (Strict)

### Principle
If the Dummy capacitor fails DRC, this indicates the unit capacitor design is not robust. Do NOT attempt to patch Dummy capacitor in isolation.

### Action
1. Abort downstream steps (including Array generation)
2. Mark the current unit capacitor parameters invalid
3. Restart from requirement analysis (Phase 1, Step 1) with the Dummy DRC issues elevated as constraints to be fixed

### Parameter Update Priorities on Restart
- Remain consistent with the optimization strategy (fingers, layers, h_height, spacings, widths)
- Strictly respect all global constraints:
  - Allowed metal layers (per technology config)
  - DRC minima (per technology config)
  - Height ≤ H_max (if provided)
  - Low-parasitic rules (if applicable, per technology config)

### No Dummy-Only Parameters
- The Dummy capacitor must share the exact same layer set and core parameters as the unit capacitor
- Introducing Dummy-only parameters is forbidden

---

## Python Helper Function Contract

### generate_sandwich_h_notch_dummy_skill(params, geometry, output_dir)

**Purpose**: Generate flattened SKILL script for Sandwich Simplified H-Notch Dummy capacitor

**Input**:
- `params`: Same parameter dict as unit Sandwich Simplified H-Notch capacitor (from best iteration)
- `geometry`: Derived geometry dict from `compute_sandwich_h_notch_geometry(params)`
- `output_dir`: Output directory for `.il` file

**Output**:
- Returns path to generated `sandwich_h_notch_dummy_{timestamp}.il` file

**Key steps**:
1. Validate parameters and geometry
2. Compute shortening deltas:
   - For middle bar and frame horizontals: `delta_x` only (plates are NOT shortened)
3. Compute shortened boundaries:
   - Middle bar: `dummy_bar_x_left`, `dummy_bar_x_right`
   - Frame horizontals: use same `dummy_bar_x_left` and `dummy_bar_x_right` as middle bar
   - Frame verticals: use `h_bottom_y` and `h_top_y` (same as finger region)
4. Draw top plate (`L_top`, BOT net) with full size: bbox `((-half_width, outer_bottom), (half_width, outer_top))`
5. Draw bottom plate (`L_bot`, BOT net) with full size: bbox `((-half_width, outer_bottom), (half_width, outer_top))`
6. Draw shortened middle frame on `L_mid` (BOT net):
   - Top horizontal band: shortened to `dummy_bar_x_left` to `dummy_bar_x_right`
   - Bottom horizontal band: shortened to `dummy_bar_x_left` to `dummy_bar_x_right`
   - Left vertical band: two segments separated by notch, from `h_bottom_y` to `notch_y1` and `notch_y2` to `h_top_y`
   - Right vertical band: same pattern as left
7. Draw H-shape structure on `L_mid` (TOP net):
   - All fingers uniformly: upper segment from `upper_y` to `h_top_y`, lower segment from `h_bottom_y` to `lower_y`
   - Middle horizontal bar: shortened from `dummy_bar_x_left` to `dummy_bar_x_right` at `y = 0`
8. NO vias
9. NO pins
10. Write flattened SKILL to file

---

## Verification Workflow

### DRC-Only Verification

**Standard flow for Dummy:**
1. Generate Dummy SKILL from best unit parameters
2. Run `run_drc()` to check compliance
3. If DRC violations exist:
   - Attempt conservative spacing reduction (respecting ≥0.05 µm minimum per technology config)
   - If violations persist, flag for unit capacitor redesign
4. If DRC passes: Dummy generation complete (no PEX required)

**No PEX for Dummy:**
- Dummy is non-functional fill; electrical verification not needed
- Focus on DRC compliance only

### DRC Violation Handling

If DRC flags minimum-area violations (e.g., `M?.A.1` - area < minimum per technology config):
- Refer to the technology configuration file for minimum area violation handling strategy
- The strategy includes: reducing outer frame shortening amount, conservative spacing reduction, and returning to Phase 1 if fixes fail

---

## Checklist Before Dummy Generation

- [ ] Unit Sandwich Simplified H-Notch capacitor optimization complete (5 rounds or ±1%)
- [ ] Best iteration parameters selected
- [ ] Parameters satisfy Sandwich Simplified H-Notch constraints (odd fingers recommended)
- [ ] All widths/spacings ≥ technology minima (see Technology_Configs/)
- [ ] Coordinate ordering validated
- [ ] No new parameters introduced
- [ ] Dummy generator uses same layer set as unit (`layer_top`, `layer_mid`, `layer_bot`)
- [ ] **Plates use full size**: Top and bottom plates maintain original dimensions (not shortened)
- [ ] **Middle bar shortening computed**: `delta_x` for middle horizontal bar
- [ ] **Frame shortening computed**: 
  - Horizontal frames: use `dummy_bar_x_left` and `dummy_bar_x_right` (same as middle bar)
  - Vertical frames: use `h_bottom_y` and `h_top_y` (same as finger region)
- [ ] **Finger uniform treatment**: All fingers split into upper and lower segments (no odd/even distinction)
- [ ] **Notch openings preserved**: Notch height and position remain unchanged
- [ ] **Vias and pins omitted**: Dummy does not draw vias or pins

---

## Summary: Sandwich Simplified H-Notch Dummy

### Key Features
1. **Top and bottom plates**: Full size (same as unit capacitor, NOT shortened)
2. **All fingers**: Uniform treatment with upper segment (`upper_y` to `h_top_y`) and lower segment (`h_bottom_y` to `lower_y`) - no odd/even distinction
3. **Middle horizontal bar**: Shortened using `delta_x` rule
4. **Middle frame**:
   - Horizontal bands: Shortened to match middle bar width (`dummy_bar_x_left` to `dummy_bar_x_right`)
   - Vertical bands: Shortened to finger region height (`h_bottom_y` to `h_top_y`)
   - Notch openings: Preserved at center with original height
5. **No vias or pins**: Dummy is fill structure, no electrical connections

### Geometric Consistency
- All coordinates inherit from unit capacitor geometry
- Frame shortening creates visual distinction while maintaining alignment
- Shortened frame dimensions match internal structure (fingers + middle bar)
- Notch openings remain functional to allow middle bar passage

---

## Related Documents

- **01_Workflow_Framework.md**: Phase 2 workflow context
- **03_02_Sandwich_Simplified_H_Notch.md**: Base Sandwich Simplified H-Notch structure definitions
- **Technology_Configs/**: Technology-specific DRC rules that apply to dummy capacitors


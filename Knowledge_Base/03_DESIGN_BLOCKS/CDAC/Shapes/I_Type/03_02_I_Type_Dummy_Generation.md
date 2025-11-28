# I-Type Dummy Capacitor Generation - Geometric transformation rules (I-Type specific, all technologies)

## Overview

This document describes the structural description and drawing rules for generating dummy unit capacitors used in capacitor arrays. The I-Type dummy capacitor is derived from the finalized I-Type unit capacitor design.

**Applicability**: This document is specific to I-Type capacitors. For other shapes, refer to their respective dummy generation rules.

---

## Key Points (Implementation Principles)

- **The Dummy capacitor must be generated only after** the unit capacitor iterative design is finalized (best iteration selected from Phase 1, Step 6).
- **No new explicit parameters**: The Dummy capacitor must share the exact same parameter set as the unit capacitor; do not add external flags such as `isDummy` or `dummyType`.
- **Dummy capacitor does not require iterative tuning**: Dummy geometry should be derived and rendered from the existing parameters in one pass; satisfying DRC is considered correct and no multi-round optimization (as for the unit capacitor) is required.

---

## Geometric Transforms and Drawing Rules

### General Principle

Only use derived quantities from the existing parameters (for example `x_left`/`x_right`, `h_top_y`/`h_bottom_y`, `h_left_x`/`h_right_x`, `via_top_y`, `via_bottom_y`, `strip_top_y`, `strip_bottom_y` for shield case); do not introduce new parameters. Create Dummy geometry by simplifying or shortening portions of these derived quantities.

**Shield configuration inheritance**: All geometry calculations (coordinates, strip positions, finger endpoints) must use the same formulas as the unit capacitor, depending on whether the unit has shield or not. The Dummy inherits the shield configuration and uses the corresponding geometry model.

### Finger Vertical Drawing — Dummy Behavior

#### I-Type Dummy Capacitor Finger Rule
For every finger index i (no parity distinction):
- **Single continuous segment**: `(x_i, h_bottom_y)` → `(x_i, h_top_y)`

The I-Type Dummy uses `h_top_y` and `h_bottom_y` as endpoints for all fingers uniformly. This produces equal-length, parallel trace arrays.

**Key point**: All fingers in Dummy are drawn identically, creating a uniform vertical trace pattern across the full finger region.

#### Coordinate Ordering Validation (must hold numerically)
```
outer_top > top_minus_frame > h_top_y > 0 > h_bottom_y > bottom_minus_frame > outer_bottom
```

If this ordering does not hold for given parameters, the renderer must reject the Dummy generation and report a parameter violation.

#### SKILL Rendering Note
Compute and serialize `h_top_y` and `h_bottom_y` as numeric literals (5 decimals) into the flattened SKILL; do NOT emit expressions or control flow to compute them in SKILL.

---

### Horizontal Trace Handling

**I-Type Dummy horizontal traces**: Draw shortened horizontal traces. The Y positions depend on whether the unit capacitor has a shield.

#### Shortening Calculation
```
delta_x_raw = min(0.15 · (x_right - x_left), frame_to_finger_d)
delta_x = round(delta_x_raw / 0.005) * 0.005
```

Ensure the resulting delta is quantized to a multiple of `0.005` µm.

#### Derived Endpoints
```
dummy_x_left  = x_left  + delta_x
dummy_x_right = x_right - delta_x
```

Ensure `dummy_x_right > dummy_x_left`.

#### Y Positions

**Without Shield** (unit capacitor has no shield):
- **Top horizontal trace Y**: `via_top_y = halfHeight - frame_horizontal_width/2`
- **Bottom horizontal trace Y**: `via_bottom_y = -halfHeight + frame_horizontal_width/2`

**With Shield** (unit capacitor has shield):
- **Top horizontal trace Y**: `strip_top_y = frame_inner_top - shield_to_strip_spacing - frame_horizontal_width/2` (same as unit capacitor top strip center)
- **Bottom horizontal trace Y**: `strip_bottom_y = frame_inner_bottom + shield_to_strip_spacing + frame_horizontal_width/2` (same as unit capacitor bottom strip center)

#### Drawing

**Without Shield**:
- **Top horizontal trace**: from `(dummy_x_left, via_top_y)` to `(dummy_x_right, via_top_y)` with width `frame_horizontal_width`
- **Bottom horizontal trace**: from `(dummy_x_left, via_bottom_y)` to `(dummy_x_right, via_bottom_y)` with width `frame_horizontal_width`

**With Shield**:
- **Top horizontal trace**: from `(dummy_x_left, strip_top_y)` to `(dummy_x_right, strip_top_y)` with width `frame_horizontal_width`
- **Bottom horizontal trace**: from `(dummy_x_left, strip_bottom_y)` to `(dummy_x_right, strip_bottom_y)` with width `frame_horizontal_width`

**Important**: 
- These traces maintain vertical alignment with the unit capacitor's strip/via positions while being slightly shortened to distinguish Dummy from unit structure
- The Y positions must match the unit capacitor's geometry (inherit from unit's shield configuration)
- All coordinates use the same formulas as the unit capacitor

**I-Type specific**: No middle horizontal trace (since I-Type has no middle bar or middle via row).

---

### Outer Frame (Shield) Handling

#### Shield Layer Inheritance from Unit Capacitor
- The Dummy capacitor must inherit the shield rendering decision from the unit capacitor
- If the unit capacitor includes an outer shield, the Dummy must apply the outer-frame handling rules described below
- If the unit capacitor does not include a shield, the Dummy must follow the "Without Shield" rules described below

#### With Shield (when unit capacitor has shield)
- **Draw outer frame with openings** (all four sides, but shortened to match internal structure)
- **Vertical frame lines** (shortened to match finger region height):
  - Left: from `(leftFrameX, h_bottom_y)` to `(leftFrameX, h_top_y)` with width `frame_vertical_width`
  - Right: from `(rightFrameX, h_bottom_y)` to `(rightFrameX, h_top_y)` with width `frame_vertical_width`
  - **Key**: Vertical frames use the same Y range as the finger region (`h_bottom_y` to `h_top_y`), not the full frame inner boundaries
- **Horizontal frame lines** (shortened to match internal strip length):
  - Top: centered at `y = top_frame_y = outer_top - frame_horizontal_width/2`, spanning from `(dummy_x_left, top_frame_y)` to `(dummy_x_right, top_frame_y)` with width `frame_horizontal_width`
  - Bottom: centered at `y = bottom_frame_y = outer_bottom + frame_horizontal_width/2`, spanning from `(dummy_x_left, bottom_frame_y)` to `(dummy_x_right, bottom_frame_y)` with width `frame_horizontal_width`
  - **Key**: Horizontal frames use the same X coordinates as the shortened internal strips (`dummy_x_left` and `dummy_x_right`), creating a smaller rectangle that aligns with the internal structure
- **Do NOT draw connection line** from bottom strip to bottom frame (Dummy is fill structure, no electrical connection needed)
- Use the same geometry calculations as the unit capacitor (with shield) for all coordinates
- Horizontal strips (top and bottom) are shortened using the same `delta_x` rule as described in "Horizontal Trace Handling" section
- Horizontal strip positions match unit capacitor: `strip_top_y` and `strip_bottom_y` (same formulas)
- **Result**: The outer frame forms a smaller rectangle that matches the dimensions of the internal structure (fingers + strips), creating openings at the corners and providing visual distinction from the unit capacitor

#### Without Shield (when unit capacitor has no shield)
- **Do NOT draw outer frame segments** (no vertical frame lines, no horizontal frame lines)
- **Draw only top and bottom horizontal Dummy traces** at shortened positions
- Use shortened endpoints: `dummy_x_left` and `dummy_x_right` (as described in "Horizontal Trace Handling" section)
- Y positions match unit capacitor via row positions: `via_top_y` and `via_bottom_y`
- All geometric calculations use the no-shield formulas from unit capacitor

#### Key Principle
- **Dummy inherits shield decision from unit capacitor** - if unit has shield, Dummy has shield; if unit has no shield, Dummy has no shield
- **Do NOT independently decide** to add or remove shield in Dummy generation
- All coordinates and geometry calculations must match the unit capacitor's shield configuration
- **Frame shortening**: When shield is present, the outer frame is shortened to match the internal structure dimensions:
  - Horizontal frames: same X coordinates as shortened internal strips (`dummy_x_left`, `dummy_x_right`)
  - Vertical frames: same Y coordinates as finger region (`h_bottom_y`, `h_top_y`)
- This creates a smaller rectangular frame that aligns with the internal structure, providing visual distinction while maintaining geometric consistency

---

### What NOT to Draw in Dummy Capacitor

- **Do not draw vias**
- **Do not draw pins**
- **Do not draw connection line** from bottom strip to bottom frame (even when shield is present) - Dummy is fill structure, no electrical connection needed
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
- Remain consistent with the optimization strategy (fingers (keep even), layers, h_height, spacings, widths)
- Strictly respect all global constraints:
  - Allowed metal layers (per technology config)
  - DRC minima (per technology config)
  - Height ≤ H_max (if provided)
  - Low-parasitic rules (if applicable, per technology config)
  - **I-Type specific**: Fingers must remain even (≥2)

### No Dummy-Only Parameters
- The Dummy capacitor must share the exact same layer set and core parameters as the unit capacitor
- Introducing Dummy-only parameters is forbidden

---

## Python Helper Function Contract

### generate_i_type_dummy_skill(params, geometry, output_dir)

**Purpose**: Generate flattened SKILL script for I-Type Dummy capacitor

**Input**:
- `params`: Same parameter dict as unit I-Type capacitor (from best iteration)
- `geometry`: Derived geometry dict from `compute_i_type_geometry(params)`
- `output_dir`: Output directory for `.il` file

**Output**:
- Returns path to generated `i_type_dummy_{timestamp}.il` file

**Key steps**:
1. Validate parameters and geometry
2. **Determine shield configuration**: Inherit from unit capacitor (check if unit has shield)
3. Compute shortening delta for horizontal traces (`delta_x`)
4. Compute shortened endpoints:
   - Internal strips: `dummy_x_left = x_left + delta_x`, `dummy_x_right = x_right - delta_x`
   - Frame horizontals: use same `dummy_x_left` and `dummy_x_right` as internal strips
   - Frame verticals: use `h_bottom_y` and `h_top_y` (same as finger region)
5. For each layer in layerList:
   - Draw all fingers uniformly (h_bottom_y → h_top_y)
   - Draw shortened top horizontal trace:
     - Without shield: at `via_top_y`
     - With shield: at `strip_top_y` (same as unit capacitor)
   - Draw shortened bottom horizontal trace:
     - Without shield: at `via_bottom_y`
     - With shield: at `strip_bottom_y` (same as unit capacitor)
   - **If shield is present**: Draw shortened outer frame (four sides):
     - Vertical frames: from `(leftFrameX, h_bottom_y)` to `(leftFrameX, h_top_y)` and `(rightFrameX, h_bottom_y)` to `(rightFrameX, h_top_y)`
     - Horizontal frames: from `(dummy_x_left, top_frame_y)` to `(dummy_x_right, top_frame_y)` and `(dummy_x_left, bottom_frame_y)` to `(dummy_x_right, bottom_frame_y)`
   - **Do NOT draw connection line** (even if shield is present)
6. NO vias
7. NO pins
8. Write flattened SKILL to file

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

- [ ] Unit I-Type capacitor optimization complete (5 rounds or ±1%)
- [ ] Best iteration parameters selected
- [ ] Parameters satisfy I-Type constraints (even fingers ≥2)
- [ ] All widths/spacings ≥ technology minima (see Technology_Configs/)
- [ ] Coordinate ordering validated
- [ ] No new parameters introduced
- [ ] Dummy generator uses same layerList as unit
- [ ] **Shield configuration determined**: Check if unit capacitor has shield and inherit the same configuration
- [ ] **Geometry calculations match unit**: Use same formulas (with shield or without shield) as unit capacitor
- [ ] **Frame shortening computed**: 
  - Horizontal frames: use `dummy_x_left` and `dummy_x_right` (same as internal strips)
  - Vertical frames: use `h_bottom_y` and `h_top_y` (same as finger region)
- [ ] **Connection line omitted**: Do not draw connection line in Dummy (even if unit has shield)
- [ ] **Frame openings**: When shield is present, frame is shortened to create openings that align with internal structure

---

## Summary: I-Type Dummy with Shield

### Key Features
1. **All fingers**: Continuous segments from `h_bottom_y` to `h_top_y` (no odd/even distinction)
2. **Horizontal strips**: Shortened using `delta_x` rule, positioned at `strip_top_y` and `strip_bottom_y` (same as unit)
3. **Outer frame** (when shield present):
   - Vertical frames: Shortened to finger region height (`h_bottom_y` to `h_top_y`)
   - Horizontal frames: Shortened to internal strip length (`dummy_x_left` to `dummy_x_right`)
   - Result: Smaller rectangular frame with openings, aligned with internal structure
4. **No connection line**: Dummy does not draw connection line from bottom strip to frame
5. **No vias or pins**: Dummy is fill structure, no electrical connections

### Geometric Consistency
- All coordinates inherit from unit capacitor geometry (with or without shield)
- Frame shortening creates visual distinction while maintaining alignment
- Shortened frame dimensions match internal structure (fingers + strips)

## Related Documents

- **01_Workflow_Framework.md**: Phase 2 workflow context
- **03_01_I_Type_Structure.md**: Base I-Type structure definitions (including shield layer selection)
- **Technology_Configs/**: Technology-specific DRC rules that apply to dummy capacitors


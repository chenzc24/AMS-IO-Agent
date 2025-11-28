# H-shape Dummy Capacitor Generation - Geometric transformation rules (H-shape specific, all technologies)

## Overview

This document describes the structural description and drawing rules for generating dummy unit capacitors used in capacitor arrays. The dummy capacitor is derived from the finalized unit capacitor design.

**Applicability**: This document is specific to H-shape capacitors. For other shapes, create shape-specific dummy generation rules.

---

## Key Points (Implementation Principles)

- **The Dummy capacitor must be generated only after** the unit capacitor iterative design is finalized (best iteration selected from Phase 1, Step 6).
- **No new explicit parameters**: The Dummy capacitor must share the exact same parameter set as the unit capacitor; do not add external flags such as `isDummy` or `dummyType`.
- **Dummy capacitor does not require iterative tuning**: Dummy geometry should be derived and rendered from the existing parameters in one pass; satisfying DRC is considered correct and no multi-round optimization (as for the unit capacitor) is required.

---

## ⚠️ CRITICAL RULES - MUST FOLLOW (Common Mistakes to Avoid)

### 1. **Fingers Must Be Equal Length - NO Interleaved Arrangement**
- **MANDATORY**: All fingers in Dummy capacitor must have **equal length** (upper and lower segments)
- **MANDATORY**: All fingers are treated **identically** - NO odd/even distinction, NO interleaved arrangement
- **Difference from Unit Capacitor**: Unit capacitor uses interleaved arrangement (odd fingers full-length, even fingers split); Dummy capacitor uses uniform equal-length segments for ALL fingers
- **Implementation**: Every finger i must be split into two equal segments:
  - Upper segment: `(x_i, h_top_y)` → `(x_i, upper_y)`
  - Lower segment: `(x_i, lower_y)` → `(x_i, h_bottom_y)`
- **Validation**: All upper segments must have the same length; all lower segments must have the same length

### 2. **Outer Frame MUST Exist - Only Shorten, NEVER Delete**
- **CRITICAL**: The outer frame (horizontal and/or vertical bars) **MUST be drawn** in Dummy capacitor
- **MANDATORY**: Outer frame elements are **shortened** (reduced in length), NOT deleted or removed
- **With Shield**: 
  - Horizontal frame bars: x-range shortened to match middle bar (after `delta_x` shortening)
  - Vertical frame bars: y-range shortened to match finger region (`h_top_y` to `h_bottom_y`)
  - **ALL frame elements must still be drawn** - they are just shorter than in unit capacitor
- **Without Shield**:
  - Top and bottom horizontal traces **MUST be drawn** (x-span equals shortened middle bar)
  - Vertical frame lines are not drawn (this is the only exception, per "Without Shield" rules)
- **Common Error**: Do NOT skip drawing frame elements - they must exist, just with reduced dimensions

### 3. **Vias and Pins Are FORBIDDEN - Must NOT Be Drawn**
- **ABSOLUTELY FORBIDDEN**: **NO vias** (`dbCreateVia`) in Dummy capacitor
- **ABSOLUTELY FORBIDDEN**: **NO pins** (`dbCreatePin`) in Dummy capacitor
- **Rationale**: Dummy capacitors are non-functional structures for edge matching; they do not need electrical connections
- **Validation**: The generated SKILL script must contain ZERO `dbCreateVia` calls and ZERO `dbCreatePin` calls for Dummy capacitor

---

## Geometric Transforms and Drawing Rules

### General Principle

Only use derived quantities from the existing parameters (for example `x_left`/`x_right`, `h_top_y`/`h_bottom_y`, `h_left_x`/`h_right_x`, `cut_rows_*`); do not introduce new parameters. Create Dummy geometry by shrinking or removing portions of these derived quantities.

### Finger Vertical Clipping — IMPORTANT Difference vs Unit Capacitor

#### ⚠️ CRITICAL: Equal-Length Fingers - NO Interleaved Arrangement
**MANDATORY RULE**: The Dummy capacitor **MUST** treat every finger identically (no odd/even distinction). Each finger is split into two segments (upper and lower) of **equal length**. This is fundamentally different from the unit capacitor where odd fingers can be full-length and even fingers are split to avoid the middle window (interleaved arrangement).

**Key Difference**:
- **Unit Capacitor**: Uses interleaved arrangement (odd fingers full-length, even fingers split)
- **Dummy Capacitor**: Uses uniform equal-length segments for ALL fingers (no interleaved arrangement)

#### Summary
The Dummy capacitor treats every finger identically (no odd/even distinction). Each finger is split into two segments (upper and lower). This is different from the unit capacitor where odd fingers can be full-length and even fingers are split to avoid the middle window.

#### Unit Capacitor (for reference)
- **Odd-index finger i**: One full segment from `(x_i, h_bottom_y)` to `(x_i, h_top_y)`.
- **Even-index finger i**: Two segments to avoid the middle bar window:
  - Top segment: `(x_i, top_minus_frame)` → `(x_i, upper_y)`
  - Bottom segment: `(x_i, lower_y)` → `(x_i, bottom_minus_frame)`
- Where:
  - `upper_y = h_middle_y + spacing + middle_horizontal_width/2`
  - `lower_y = h_middle_y - spacing - middle_horizontal_width/2`

#### Dummy Capacitor (MANDATORY Behavior)
**⚠️ CRITICAL**: For every finger index i (no parity - ALL fingers treated identically):
- **Upper segment**: `(x_i, h_top_y)` → `(x_i, upper_y)`
- **Lower segment**: `(x_i, lower_y)` → `(x_i, h_bottom_y)`

**MANDATORY**: The Dummy uses `h_top_y` and `h_bottom_y` as the outer endpoints for the upper/lower segments respectively, and the inner cut positions are `upper_y` and `lower_y` (same formulas as MAIN). This produces **equal-length, parallel trace arrays** for ALL fingers.

**Validation Requirements**:
- All upper segments must have identical length: `h_top_y - upper_y` (same for all fingers)
- All lower segments must have identical length: `lower_y - h_bottom_y` (same for all fingers)
- NO interleaved arrangement - every finger follows the same pattern

#### Coordinate Ordering Validation (must hold numerically)
```
top_minus_frame > h_top_y > upper_y > h_middle_y > lower_y > h_bottom_y > bottom_minus_frame
```

If this ordering does not hold for given parameters, the renderer must reject the Dummy generation and report a parameter violation.

#### SKILL Rendering Note
Compute and serialize all four coordinates (`h_top_y`, `upper_y`, `lower_y`, `h_bottom_y`) as numeric literals (5 decimals) into the flattened SKILL; do NOT emit expressions or control flow to compute them in SKILL.

---

### Middle Horizontal Bar Handling

**Shorten the middle bar**: Shrink both left and right endpoints by:
```
delta_x = min(0.15 · (x_right - x_left), frame_to_finger_d)
```

Ensure the resulting delta is quantized to a multiple of `0.005` µm:
```
delta_x_raw = min(0.15 · (x_right - x_left), frame_to_finger_d)
delta_x = round(delta_x_raw / 0.005) * 0.005
```

---

### Outer Frame Horizontal and Vertical Handling

**⚠️ CRITICAL: Outer Frame Drawing is MANDATORY - This is a Common Error Point**

The outer frame (or horizontal traces) **MUST be drawn** in Dummy capacitor. The frame is **shortened**, NOT deleted. This is one of the most common mistakes - skipping frame drawing entirely.

#### Shield Layer Inheritance from Unit Capacitor
- The Dummy capacitor must inherit the shield rendering decision from the unit capacitor
- If the unit capacitor includes an outer shield, the Dummy must apply the outer-frame handling rules described below
- If the unit capacitor does not include a shield, the Dummy must follow the "Without Shield" rules described below

#### With Shield (when unit capacitor has shield)
**⚠️ CRITICAL**: Outer frame elements **MUST be drawn** - they are shortened, NOT deleted.

**Drawing Steps**:
1. **Compute shortened endpoints**: Use `dummy_x_left = x_left + delta_x` and `dummy_x_right = x_right - delta_x` (see "Dummy Horizontals Alignment" section below)
2. **Draw Horizontal Frame Lines** (top and bottom):
   - **Top horizontal frame**: 
     - x-range: from `dummy_x_left` to `dummy_x_right` (shortened endpoints)
     - y-coordinate: `outer_top - frame_horizontal_width/2` (unchanged from unit capacitor)
     - width: `frame_horizontal_width` (unchanged)
     - **MANDATORY**: This line MUST be drawn using `dbCreatePath`
   - **Bottom horizontal frame**:
     - x-range: from `dummy_x_left` to `dummy_x_right` (shortened endpoints)
     - y-coordinate: `outer_bottom + frame_horizontal_width/2` (unchanged from unit capacitor)
     - width: `frame_horizontal_width` (unchanged)
     - **MANDATORY**: This line MUST be drawn using `dbCreatePath`
3. **Draw Vertical Frame Lines** (left and right):
   - **Left vertical frame**:
     - x-coordinate: `leftFrameX` (unchanged from unit capacitor)
     - y-range: from `h_bottom_y` to `h_top_y` (shortened to match finger region)
     - width: `frame_vertical_width` (unchanged)
     - **MANDATORY**: This line MUST be drawn using `dbCreatePath`
   - **Right vertical frame**:
     - x-coordinate: `rightFrameX` (unchanged from unit capacitor)
     - y-range: from `h_bottom_y` to `h_top_y` (shortened to match finger region)
     - width: `frame_vertical_width` (unchanged)
     - **MANDATORY**: This line MUST be drawn using `dbCreatePath`

**Validation Checklist**:
- [ ] Top horizontal frame line is drawn (x: `dummy_x_left` to `dummy_x_right`, y: `outer_top - frame_horizontal_width/2`)
- [ ] Bottom horizontal frame line is drawn (x: `dummy_x_left` to `dummy_x_right`, y: `outer_bottom + frame_horizontal_width/2`)
- [ ] Left vertical frame line is drawn (x: `leftFrameX`, y: `h_bottom_y` to `h_top_y`)
- [ ] Right vertical frame line is drawn (x: `rightFrameX`, y: `h_bottom_y` to `h_top_y`)
- [ ] All frame elements use `dbCreatePath` (NOT `dbCreateRect`)

**Common Error Prevention**: Do NOT skip drawing frame elements. The frame is shortened, not removed. All four frame lines (top, bottom, left, right) MUST be present in the generated SKILL script.

#### Without Shield (when unit capacitor has no shield)
**⚠️ CRITICAL**: Top and bottom horizontal traces **MUST be drawn** - they are shortened, NOT deleted.

**Drawing Steps**:
1. **Compute shortened endpoints**: Use `dummy_x_left = x_left + delta_x` and `dummy_x_right = x_right - delta_x` (see "Dummy Horizontals Alignment" section below)
2. **Draw Top Horizontal Trace**:
   - x-range: from `dummy_x_left` to `dummy_x_right` (shortened endpoints)
   - y-coordinate: `outer_top - frame_horizontal_width/2` (same as unit capacitor)
   - width: `frame_horizontal_width` (same as unit capacitor)
   - **MANDATORY**: This trace MUST be drawn using `dbCreatePath`
3. **Draw Bottom Horizontal Trace**:
   - x-range: from `dummy_x_left` to `dummy_x_right` (shortened endpoints)
   - y-coordinate: `outer_bottom + frame_horizontal_width/2` (same as unit capacitor)
   - width: `frame_horizontal_width` (same as unit capacitor)
   - **MANDATORY**: This trace MUST be drawn using `dbCreatePath`
4. **Do NOT draw vertical frame lines** (this is the only exception - vertical lines are not drawn when there is no shield)
5. **Do NOT draw full frame rectangles** (this is the only case where full rectangles are not drawn)

**Validation Checklist**:
- [ ] Top horizontal trace is drawn (x: `dummy_x_left` to `dummy_x_right`, y: `outer_top - frame_horizontal_width/2`)
- [ ] Bottom horizontal trace is drawn (x: `dummy_x_left` to `dummy_x_right`, y: `outer_bottom + frame_horizontal_width/2`)
- [ ] NO vertical frame lines are drawn (correct for "Without Shield" case)
- [ ] Both traces use `dbCreatePath` (NOT `dbCreateRect`)

**Common Error Prevention**: Even without shield, the top and bottom horizontal traces MUST be drawn (just shortened). Do NOT skip them. The absence of vertical lines is intentional for "Without Shield" case, but the horizontal traces are still required.

---

### Dummy Horizontals Alignment — Required

1. Compute `delta_x_raw = min(0.15 · (x_right - x_left), frame_to_finger_d)` and quantize `delta_x = round(delta_x_raw/0.005) * 0.005` (µm).

2. Derive unified endpoints once and reuse everywhere:
   - `dummy_x_left  = x_left  + delta_x`
   - `dummy_x_right = x_right - delta_x` (ensure `dummy_x_right > dummy_x_left`)

3. Use the same pair `(dummy_x_left, dummy_x_right)` for all three horizontals:
   - Middle bar at y = 0
   - Top outer frame horizontal at y = `outer_top - frame_horizontal_width/2`
   - Bottom outer frame horizontal at y = `outer_bottom + frame_horizontal_width/2`

4. If the shortened length triggers DRC minimum width/area or conflicts:
   - Refer to the technology configuration file for minimum area violation handling strategy
   - Follow the Dummy DRC failure policy if fixes fail (return to Phase 1)

---

### What NOT to Draw in Dummy Capacitor

**⚠️ CRITICAL - ABSOLUTELY FORBIDDEN**:

- **ABSOLUTELY FORBIDDEN: Do not draw vias**
  - **NO `dbCreateVia` calls** in Dummy capacitor SKILL script
  - **ZERO vias** must be generated
  - Dummy capacitors are non-functional structures and do not need electrical connections between layers

- **ABSOLUTELY FORBIDDEN: Do not draw pins**
  - **NO `dbCreatePin` calls** in Dummy capacitor SKILL script
  - **ZERO pins** must be generated
  - Dummy capacitors do not need external connection points

- **Absolutely forbid changing the layer set** for Dummy generation
  - Dummy capacitor must use the exact same layer set as the unit capacitor
  - Only geometric transformations (shortening, clipping) are allowed, NOT layer changes

**Validation**: Before generating SKILL script, verify that the code generation logic will produce ZERO `dbCreateVia` and ZERO `dbCreatePin` calls for Dummy capacitor.

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

### Exception: Routing Wire Minimum Area Violations
**⚠️ CRITICAL SPECIAL RULE - ONLY APPLIES TO DUMMY PHASE (Phase 2)**:

**MANDATORY ACTION**: If DRC flags minimum area violations for routing wires in the Dummy capacitor:
- **IMMEDIATELY delete the problematic routing wire(s)** that trigger the minimum area violation
- **This is the PRIMARY and PREFERRED solution** for routing wire area violations in Dummy capacitors
- **Do NOT attempt to fix by adjusting geometry or parameters** - simply delete the violating routing wires
- **Rationale**: Dummy capacitors are non-functional structures used only for edge matching; removing problematic routing wires does not affect functionality and maintains DRC compliance

**Scope and Limitations**:
- **This exception applies ONLY to Phase 2 (Dummy Capacitor Generation)**
- **FORBIDDEN in all other phases**: 
  - In Phase 1 (Unit Capacitor): Routing wires must NOT be deleted - fix by adjusting parameters
  - In Phase 3 (Array Generation): Routing wires must NOT be deleted - fix by adjusting routing geometry or parameters
- **Only applies to routing wires**: This exception does NOT apply to capacitor structure elements (fingers, frames, etc.) - those must follow the general DRC failure policy

### Action (General DRC Failures)
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

## Related Documents

- **01_Workflow_Framework.md**: Phase 2 workflow context
- **03_01_H_Shape_Structure.md**: Base H-shape structure definitions
- **Technology_Configs/**: Technology-specific DRC rules that apply to dummy capacitors


# I-Type Capacitor Structure - Geometry specification and drawing procedures (I-Type specific, all technologies)

## Overview

This document defines the **I-Type capacitor structure**, a variant of the standard H-shape with alternating finger heights and no middle bar. The structure consists of multiple vertical fingers at different heights, with only top and bottom horizontal connection strips.

**Applicability**: This structure specification applies to all I-Type capacitor designs across all technology nodes. Technology-specific parameters (DRC minima, via sizing, etc.) are defined in Technology_Configs/.

---

## Physical Structure

### Main Components
- **Vertical fingers**: Multiple fingers with alternating heights (no middle horizontal bar)
- **Horizontal via-matching strips**: Top and bottom strips only (no middle)
- **Outer frame (shield)**: Optional, controllable by design intent (see "Shield Layer Selection" section below)

### I-Type Arrangement
- **Even finger count required**: fingers must be even (≥2)
- **Odd-index fingers** (1, 3, 5, ...): Extend from `bottom_minus_frame` to `h_top_y`
- **Even-index fingers** (2, 4, 6, ...): Extend from `h_bottom_y` to `top_minus_frame`
- **Interdigitation**: Created by alternating finger heights
- **No middle horizontal bar**: Structure omits middle bar, using only top and bottom connection strips
- **Two via rows**: Only top and bottom via rows (no middle via row)
- **Outer frame (shield)**: Optional, determined by AI runtime decision based on user intent (see "Shield Layer Selection" section below)

---

## Cross-layer Connections (Vias)

- Automatically insert vias between every adjacent pair of metal layers
- **Via naming**: `higher_lower` (e.g., `M5_M4`, `M7_M6`)
- **I-Type specific**: Only two via rows (top and bottom), no middle via row
- Via columns should match the horizontal strip widths
- Via definition name must use `higher_lower` order; if input order is reversed, correct to high_low before generating

---

## Pins

- Insert **TOP and BOT pins only on the topmost layer**
- **TOP**: At top via row position `(0, via_top_y)`
- **BOT**: At bottom via row position `(0, via_bottom_y)`

---

## Key Geometric Quantities

All geometric quantities must be computed by the AI before generating SKILL and solidified as numbers (5 decimals).

### Coordinate System
- **Global coordinate system**: Origin at device center, +x to the right, +y up

### Total Dimensions

#### Without Shield (default for I-Type)
- **Total height**: `height = h_height + 2·spacing + 2·frame_horizontal_width`
- **Half height**: `halfHeight = height/2`
- **Total width**: `width = frame_vertical_width + frame_to_finger_d + fingers·finger_vertical_width + (fingers-1)·finger_d + frame_to_finger_d + frame_vertical_width`
- **Half width**: `halfWidth = width/2`

#### With Shield
- **Total height**: `height = frame_horizontal_width (top frame) + shield_to_strip_spacing + frame_horizontal_width (top strip) + spacing + h_height + spacing + frame_horizontal_width (bottom strip) + shield_to_strip_spacing + frame_horizontal_width (bottom frame)`
- **Half height**: `halfHeight = height/2`
- **Total width**: `width = frame_vertical_width + frame_to_finger_d + fingers·finger_vertical_width + (fingers-1)·finger_d + frame_to_finger_d + frame_vertical_width`
- **Half width**: `halfWidth = width/2`

*Note: When shield is present, all geometry calculations must account for the shield structure and `shield_to_strip_spacing` parameter.*

### Outer Frame Boundaries
- **Outer top**: `outer_top = +halfHeight`
- **Outer bottom**: `outer_bottom = -halfHeight`
- **Frame inner boundaries** (when shield is present):
  - **Frame inner top**: `frame_inner_top = outer_top - frame_horizontal_width`
  - **Frame inner bottom**: `frame_inner_bottom = outer_bottom + frame_horizontal_width`
- **Top minus frame**: `top_minus_frame = outer_top - frame_horizontal_width` (for no-shield case) or top strip bottom edge (for with-shield case)
- **Bottom minus frame**: `bottom_minus_frame = outer_bottom + frame_horizontal_width` (for no-shield case) or bottom strip top edge (for with-shield case)

### Finger Region Bounds

#### Without Shield
- **H-top Y**: `h_top_y = outer_top - frame_horizontal_width - spacing`
- **H-bottom Y**: `h_bottom_y = outer_bottom + frame_horizontal_width + spacing`

#### With Shield
- **Horizontal strip positions** (inside frame, with `shield_to_strip_spacing` from frame inner edge):
  - **Top strip center Y**: `strip_top_y = frame_inner_top - shield_to_strip_spacing - frame_horizontal_width/2`
  - **Bottom strip center Y**: `strip_bottom_y = frame_inner_bottom + shield_to_strip_spacing + frame_horizontal_width/2`
- **Finger region bounds**:
  - **H-top Y**: `h_top_y = strip_top_y - frame_horizontal_width/2 - spacing` (below top strip, with spacing)
  - **H-bottom Y**: `h_bottom_y = strip_bottom_y + frame_horizontal_width/2 + spacing` (above bottom strip, with spacing)
- **Strip edges** (for finger endpoints):
  - **Top strip bottom edge**: `top_minus_frame = strip_top_y - frame_horizontal_width/2`
  - **Bottom strip top edge**: `bottom_minus_frame = strip_bottom_y + frame_horizontal_width/2`
- **Frame horizontal coordinates** (for drawing frame):
  - **Frame x-left**: `frame_x_left = leftFrameX - frame_vertical_width/2`
  - **Frame x-right**: `frame_x_right = rightFrameX + frame_vertical_width/2`
  - **Top frame center Y**: `top_frame_y = outer_top - frame_horizontal_width/2`
  - **Bottom frame center Y**: `bottom_frame_y = outer_bottom + frame_horizontal_width/2`
- **Connection line coordinates** (for bottom strip to bottom frame connection):
  - **Bottom strip bottom edge**: `bottom_strip_bottom_edge = strip_bottom_y - frame_horizontal_width/2`
  - **Bottom frame top edge**: `bottom_frame_top_edge = bottom_frame_y + frame_horizontal_width/2`
  - **Connection line**: Vertical path at x = 0, from `(0, bottom_strip_bottom_edge)` to `(0, bottom_frame_top_edge)` with width `frame_horizontal_width`

*Note: No middle bar, so h_middle_y is not used for drawing in I-Type.*

### Coordinate Ordering Validation
```
outer_top > top_minus_frame > h_top_y > 0 > h_bottom_y > bottom_minus_frame > outer_bottom
```

### Vertical Frame Centers (if frame is drawn)
- **Left frame X**: `leftFrameX = -halfWidth + frame_vertical_width/2`
- **Right frame X**: `rightFrameX = +halfWidth - frame_vertical_width/2`

### Finger Center X Positions (1-based finger index i ∈ [1..fingers])
- **First finger center**: `x₁ = leftFrameX + frame_vertical_width/2 + frame_to_finger_d + finger_vertical_width/2`
- **Uniform pitch**: `pitch = finger_vertical_width + finger_d`
- **General**: `xᵢ = x₁ + (i-1)·pitch`

### Horizontal Strip Span
- **Left endpoint**: `x_left = h_left_x = x₁ - finger_vertical_width/2`
- **Right endpoint**: `x_right = h_right_x = x_fingers + finger_vertical_width/2`

### Via Placement Parameters
- **Via X-center**: `x_center = (h_left_x + h_right_x)/2`
- **Via top Y**: 
  - Without shield: `via_top_y = halfHeight - frame_horizontal_width/2`
  - With shield: `via_top_y = strip_top_y` (same as top strip center)
- **Via bottom Y**: 
  - Without shield: `via_bottom_y = -halfHeight + frame_horizontal_width/2`
  - With shield: `via_bottom_y = strip_bottom_y` (same as bottom strip center)

*Note: Via column and row counts are computed using technology-specific formulas (see Technology_Configs/ for pitch_cut and margin values).*

---

## Via Array Sizing (Technology-Dependent)

**Goal**: Pack as many via cuts as reasonably allowed by the metal widths without violating DRC, and keep the pattern centered for symmetry.

### Deterministic Sizing (Heuristic)

*Note: Actual `pitch_cut` and `margin` values are technology-specific. See Technology_Configs/ for specific values.*

- Use `pitch_cut` and small `margin` from technology config
- **Columns**: `cut_columns = max(1, floor((h_right_x - h_left_x + margin) / pitch_cut))`
- **Rows (top/bottom)**: `cut_rows_topbot = max(1, floor((frame_horizontal_width + margin) / pitch_cut))`

**I-Type specific**: No middle via row for I-Type capacitor.

### Centering and Symmetry
- All via rows share `x_center = (h_left_x + h_right_x)/2`
- Prefer odd counts (when feasible) to place one cut exactly on the centerline
- If even counts are required, they should be centered symmetrically around the centerline

### Ties to Width Quantization
- Horizontal widths are quantized per technology (see Technology_Configs/)
- Row counts roughly follow quantization: rows ≈ floor((width + margin) / pitch_cut)
- Adjust based on actual DRC spacing/enclosure feedback

### DRC Feedback Loop
- If DRC flags spacing/enclosure violations, reduce `cut_rows_topbot` or `cut_columns` first
- If still failing, slightly increase the corresponding metal widths (while respecting overall constraints such as H_max)
- Keep arrays reasonable; ensure the chosen `viaDef` supports the requested arrays

### Via Definition Name
- Use `higher_lower` (e.g., `M5_M4`, `M7_M6`)
- Ensure this `viaDef` exists in the tech
- If not, correct the order or choose the valid adjacent layer name

---

## Procedural Drawing Checklist

For each metal layer L in `layerList` (ordered top → bottom):

1. **Vertical fingers (alternating heights)**
   - For i = 1..fingers:
     - **If i is odd**: Draw one vertical path from `(xᵢ, bottom_minus_frame)` to `(xᵢ, h_top_y)` with width `finger_vertical_width`
     - **If i is even**: Draw one vertical path from `(xᵢ, h_bottom_y)` to `(xᵢ, top_minus_frame)` with width `finger_vertical_width`

2. **Horizontal via-matching strips**
   - Top strip at `via_top_y` (or `strip_top_y` if shield present): from `(x_left, via_top_y)` to `(x_right, via_top_y)` with width `frame_horizontal_width`
   - Bottom strip at `via_bottom_y` (or `strip_bottom_y` if shield present): from `(x_left, via_bottom_y)` to `(x_right, via_bottom_y)` with width `frame_horizontal_width`

3. **Connection line from bottom strip to bottom frame** (only if shield is present)
   - Draw vertical connection line at structure center (x = 0):
     - Start: `(0, bottom_strip_bottom_edge)` where `bottom_strip_bottom_edge = strip_bottom_y - frame_horizontal_width/2`
     - End: `(0, bottom_frame_top_edge)` where `bottom_frame_top_edge = bottom_frame_y + frame_horizontal_width/2`
     - Width: `frame_horizontal_width` (same as strip/frame width)

4. **Outer frame lines (shield)** (only if shield is present)
   - **Vertical frame lines**: 
     - Left: from `(leftFrameX, frame_inner_bottom)` to `(leftFrameX, frame_inner_top)` with width `frame_vertical_width`
     - Right: from `(rightFrameX, frame_inner_bottom)` to `(rightFrameX, frame_inner_top)` with width `frame_vertical_width`
   - **Horizontal frame lines**:
     - Top: centered at `y = top_frame_y = outer_top - frame_horizontal_width/2`, spanning from `(frame_x_left, top_frame_y)` to `(frame_x_right, top_frame_y)` with width `frame_horizontal_width`
     - Bottom: centered at `y = bottom_frame_y = outer_bottom + frame_horizontal_width/2`, spanning from `(frame_x_left, bottom_frame_y)` to `(frame_x_right, bottom_frame_y)` with width `frame_horizontal_width`
   - Where `frame_x_left = leftFrameX - frame_vertical_width/2` and `frame_x_right = rightFrameX + frame_vertical_width/2`

After metals for all layers are drawn:

5. **Vias between each adjacent pair (upper, lower) in layerList**
   - Use viaDef name `upper_lower`
   - Place two rows (centered at the same `x_center = (h_left_x + h_right_x)/2`):
     - Top row center: `(x_center, via_top_y)` with `cut_rows_topbot × cut_columns`
     - Bottom row center: `(x_center, via_bottom_y)` with `cut_rows_topbot × cut_columns`
   - **I-Type specific**: No middle via row

Finally on the top metal only:

6. **Pins**
   - `TOP` at `(0, via_top_y)`
   - `BOT` at `(0, via_bottom_y)`

---

## Indexing and Ordering Conventions

- **Finger indices**: In formulas are 1-based. Indices 1..fingers map to finger centers.
- **Layer list**: Must be ordered from top to bottom, e.g., `list("METAL5" "METAL4" "METAL3")` or `list("M7" "M6" "M5")`. Adjacent pairs become `(METAL5, METAL4)`, `(METAL4, METAL3)` for via insertion.
- **Via naming**: Uses `higher_lower` order (e.g., `M5_M4`). If input order is reversed, correct to high_low before generating.

---

## Parameter Definitions

### Key Parameters
- `h_height`: Vertical length of the finger region
- `frame_to_finger_d`: Horizontal distance from outer frame vertical line to nearest finger
- `finger_d`: Horizontal spacing between adjacent fingers
- `frame_vertical_width`: Width of outer frame verticals (if shield is drawn)
- `finger_vertical_width`: Width of finger verticals
- `frame_horizontal_width`: Width of horizontal strips (and frame horizontals if shield is drawn)
- `spacing`: Vertical gap from bottom of top horizontal strip to top of finger region
- `shield_to_strip_spacing`: **NEW parameter for I-Type with shield** - Distance from frame inner edge to horizontal strip center (only used when shield is present)
- `fingers`: Number of fingers (**even ≥ 2** for I-Type)
- `layerList`: Ordered list of metal layer names (top to bottom)

### Parameter Constraint (I-Type Specific)
- **fingers must be even (≥2)**: This is a mandatory constraint for I-Type capacitor
- If fingers is odd or < 2, validation must fail before generating

### Naming and Conversion
- **Relation between total height and h_height**:
  - Without shield: `height = h_height + 2·spacing + 2·frame_horizontal_width`
  - With shield: `height = frame_horizontal_width + shield_to_strip_spacing + frame_horizontal_width + spacing + h_height + spacing + frame_horizontal_width + shield_to_strip_spacing + frame_horizontal_width`
- Any total height limit must be converted to an `h_height` upper bound before tuning
- When shield is present, `shield_to_strip_spacing` must be considered in height calculations

---

## Shield Layer Selection (Outer Frame)

### Decision Principle
- **Whether to draw the outer shield (frame) is an AI runtime decision** inferred from user intent
- **Do NOT introduce any new explicit parameter** (for example `drawShield` or `shield=false`) to control this
- The renderer should inspect the user's request and decide
- **Default behavior for I-Type**: If the user gives no explicit instruction about the shield, the AI must default to **omitting the shield** (different from H-shape default)

### Rendering Behavior

#### With Shield
- Draw all four frame segments: left vertical, right vertical, top horizontal, bottom horizontal
- Draw top and bottom horizontal strips inside the frame, with `shield_to_strip_spacing` distance from frame inner edge to strip center
- Draw a vertical connection line from bottom strip to bottom frame (at structure center, x = 0)
  - Connection line starts at: `bottom_strip_bottom_edge = strip_bottom_y - frame_horizontal_width/2`
  - Connection line ends at: `bottom_frame_top_edge = bottom_frame_y + frame_horizontal_width/2`
  - Connection line width: `frame_horizontal_width` (same as strip/frame width)
- Use the full geometry calculations as specified in "Key Geometric Quantities" section (with shield)
- All coordinates are computed as if the shield exists

#### Without Shield (Default for I-Type)
- **Omit all four frame segments** (do not draw vertical frame lines or horizontal frame lines)
- Draw top and bottom horizontal strips at positions computed without shield
- **Do not draw connection line** (no frame to connect to)
- **All other geometry remains unchanged**:
  - Vertical fingers: draw as specified (alternating heights)
  - Horizontal strips: draw at computed positions
  - Via placement: place vias as specified (two rows: top, bottom)
  - Pins: place TOP and BOT pins as specified
  - Layer set: unchanged
  - All coordinate calculations: use formulas for no-shield case

### Geometric Computation Consistency
- **Always compute all geometry** based on whether shield is present or not
- When shield is present, use `shield_to_strip_spacing` in all calculations for strip positions
- When shield is omitted, use standard formulas without shield considerations
- Via positions and pin positions follow the chosen geometry model (with or without shield)

## Consistency Requirements

- All metal layers share identical parameters and strict alignment
- Via positions must match across all layers
- Use quantized horizontal widths for clean via arrays (per technology config)
- Shield rendering decision (draw or omit) affects geometric coordinate calculations for I-Type (unlike H-shape where calculations remain consistent)

---

## Capacitance scaling guidance (I-Type specific)

When increasing capacitance for I-Type under technology constraints:
- Priority order (respect DRC and adjacency):
  - Increase `fingers` (**keep count even** for I-Type)
  - Increase stacked metal layer count (use adjacent pairs only)
  - Increase `h_height` and recompute total height `height = h_height + 2·spacing + 2·frame_horizontal_width` to satisfy `≤ H_max`
  - Reduce spacings within minima (`finger_d`, `frame_to_finger_d`, `spacing`) when safe
- Caution on widths:
  - Increasing `finger_vertical_width` generally reduces effective plate overlap; avoid unless needed for DRC/EM
  - Horizontal widths (`frame_horizontal_width`) follow technology quantization; consider stepwise increases that also improve via rows
- Step sizing:
  - Far from target: use larger steps (e.g., `fingers` +2..+8 (keep even), layers +1..+3, `h_height` +10%..+30%) with validation each round
  - Near target (~20% error): switch to small-step tuning; prefer not to change `fingers`/layer count to avoid overshoot

These guidelines complement Phase 1 iteration rules in `01_Workflow_Framework.md`.

**Note**: Initial parameters should be synthesized by AI based on target capacitance, technology constraints, and shape requirements. Do not hardcode default values. Refer to Technology_Configs/ for technology-specific minima and quantization rules.

---

## Related Documents

- **02_Python_SKILL_Integration.md**: SKILL command patterns for implementing this structure
- **03_02_I_Type_Dummy_Generation.md**: Dummy capacitor generation based on this structure
- **Technology_Configs/**: Technology-specific DRC minima, via sizing parameters, and quantization rules
- **Technology_Configs/INTERFACE_SPEC.md**: Required interface contract for technology configurations


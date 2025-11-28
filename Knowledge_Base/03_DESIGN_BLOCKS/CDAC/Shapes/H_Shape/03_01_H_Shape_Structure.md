# H-shape Capacitor Structure - Geometry specification and drawing procedures (H-shape specific, all technologies)

## Overview

This document defines the **H-shape capacitor structure** used in all CDAC components (unit capacitor, dummy capacitor, and array elements). The structure consists of multiple vertical fingers with a middle horizontal bar, enclosed by an outer rectangular frame.

**Applicability**: This structure specification applies to all H-shape capacitor designs across all technology nodes. Technology-specific parameters (DRC minima, via sizing, etc.) are defined in Technology_Configs/.

---

## Physical Structure

### Main Components
- **H-shape main plate**: Multiple vertical fingers + one middle horizontal bar
- **Outer rectangle frame**: Two vertical frame bars + top/bottom horizontal frame bars

### H-shape Arrangement
- **3 fingers**: Standard H-shape
- **>3 fingers**: 
  - Odd-index fingers: complete-through (full length)
  - Even-index fingers: split into top/bottom segments to avoid the middle bar window

---

## Cross-layer Connections (Vias)

- Automatically insert vias between every adjacent pair of metal layers
- **Via naming**: `higher_lower` (e.g., `M5_M4`, `M7_M6`)
- Via columns/rows should match the middle bar width and horizontal bar widths
- Via definition name must use `higher_lower` order; if input order is reversed, correct to high_low before generating

### BOT Terminal Via Stack

**CRITICAL**: At the BOT terminal location `(0, 0)`, a **complete via stack** must be created to connect **ALL metal layers available in the technology** (not just the layers used in the unit cell).

**Key requirements**:
- **Location**: Same as middle row via and BOT pin: `(0, 0)`
- **Size**: Same as middle row via: `cut_rows_mid × cut_columns` (same via array size)
- **Layer scope**: **ALL adjacent metal layer pairs** from highest to lowest layer in the technology must be connected
  - Example for 28nm (M1-M7): Create `M7_M6`, `M6_M5`, `M5_M4`, `M4_M3`, `M3_M2`, `M2_M1` all at `(0, 0)` with `cut_rows_mid × cut_columns`
- **Via naming**: Use `higher_lower` convention for each adjacent pair
- **Purpose**: Ensures array routing can use **any metal layer** and will always have a connection path

**Important**: The BOT via stack uses the **same position and size** as the middle row via, but connects **all technology metal layers** (not just the layers in `layerList`).

---

## Pins

- Insert **TOP and BOT pins only on the topmost layer**
- **TOP**: Near the structure top at `(0, +halfHeight - frame_horizontal_width/2)`
- **BOT**: At the structure center at `(0, 0)`

---

## Key Geometric Quantities

All geometric quantities must be computed by the AI before generating SKILL and solidified as numbers (5 decimals).

### Coordinate System
- **Global coordinate system**: Origin at device center, +x to the right, +y up

### Total Dimensions
- **Total height**: `height = h_height + 2·spacing + 2·frame_horizontal_width`
- **Half height**: `halfHeight = height/2`
- **Total width**: `width = frame_vertical_width + frame_to_finger_d + fingers·finger_vertical_width + (fingers-1)·finger_d + frame_to_finger_d + frame_vertical_width`
- **Half width**: `halfWidth = width/2`

### Outer Frame Boundaries

**CRITICAL**: The outer frame defines the absolute boundaries of the entire structure. All calculations must be precise.

- **Outer top edge**: `outer_top = +halfHeight` (topmost edge of the entire structure)
- **Outer bottom edge**: `outer_bottom = -halfHeight` (bottommost edge of the entire structure)
- **Top minus frame**: `top_minus_frame = outer_top - frame_horizontal_width` (Y-coordinate where vertical frame lines end at the top)
- **Bottom minus frame**: `bottom_minus_frame = outer_bottom + frame_horizontal_width` (Y-coordinate where vertical frame lines end at the bottom)

**Key relationships**:
- The outer frame forms a complete rectangle: from `outer_bottom` to `outer_top` in Y, and from `-halfWidth` to `+halfWidth` in X
- The vertical frame lines connect the horizontal frame bars, so they span from `bottom_minus_frame` to `top_minus_frame` (NOT from `outer_bottom` to `outer_top`)
- The horizontal frame bars are centered at their respective Y positions, with width `frame_horizontal_width`, so their edges align with the outer boundaries

### Outer Frame Calculation Verification Checklist

**CRITICAL**: Before drawing, verify all calculations using these checks:

1. **Total dimensions**:
   - `height = h_height + 2·spacing + 2·frame_horizontal_width` ✓
   - `halfHeight = height / 2` ✓
   - `width = frame_vertical_width + frame_to_finger_d + fingers·finger_vertical_width + (fingers-1)·finger_d + frame_to_finger_d + frame_vertical_width` ✓
   - `halfWidth = width / 2` ✓

2. **Outer boundaries**:
   - `outer_top = +halfHeight` ✓ (must equal `height/2`)
   - `outer_bottom = -halfHeight` ✓ (must equal `-height/2`)
   - `outer_top - outer_bottom = height` ✓ (verification)

3. **Frame connection points**:
   - `top_minus_frame = outer_top - frame_horizontal_width = halfHeight - frame_horizontal_width` ✓
   - `bottom_minus_frame = outer_bottom + frame_horizontal_width = -halfHeight + frame_horizontal_width` ✓
   - Vertical frame length: `top_minus_frame - bottom_minus_frame = height - 2·frame_horizontal_width` ✓

4. **Vertical frame centers**:
   - `leftFrameX = -halfWidth + frame_vertical_width/2` ✓
   - `rightFrameX = +halfWidth - frame_vertical_width/2` ✓
   - Distance between centers: `rightFrameX - leftFrameX = width - frame_vertical_width` ✓

5. **Horizontal frame edges**:
   - Top frame left edge: `leftFrameX - frame_vertical_width/2 = -halfWidth` ✓
   - Top frame right edge: `rightFrameX + frame_vertical_width/2 = +halfWidth` ✓
   - Top frame center Y: `outer_top - frame_horizontal_width/2 = halfHeight - frame_horizontal_width/2` ✓
   - Top frame top edge: `outer_top = +halfHeight` ✓
   - Top frame bottom edge: `outer_top - frame_horizontal_width = halfHeight - frame_horizontal_width = top_minus_frame` ✓
   - Bottom frame center Y: `outer_bottom + frame_horizontal_width/2 = -halfHeight + frame_horizontal_width/2` ✓
   - Bottom frame bottom edge: `outer_bottom = -halfHeight` ✓
   - Bottom frame top edge: `outer_bottom + frame_horizontal_width = -halfHeight + frame_horizontal_width = bottom_minus_frame` ✓

**Common errors to avoid**:
- ❌ Using `outer_bottom` and `outer_top` directly for vertical frame endpoints (should use `bottom_minus_frame` and `top_minus_frame`)
- ❌ Using `leftFrameX` and `rightFrameX` directly as horizontal frame edges (should subtract/add `frame_vertical_width/2`)
- ❌ Miscalculating `halfWidth` or `halfHeight` (must divide total dimensions by 2)
- ❌ Forgetting that horizontal frame bars are centered, so their edges extend `±frame_horizontal_width/2` from center

### H-shape Region Bounds
- **H-top Y**: `h_top_y = outer_top - frame_horizontal_width - spacing`
- **H-bottom Y**: `h_bottom_y = -h_top_y`
- **H-middle Y**: `h_middle_y = 0`

### Vertical Frame Centers

**CRITICAL**: These are the X-coordinates of the **centerlines** of the vertical frame bars (not their edges).

- **Left frame center X**: `leftFrameX = -halfWidth + frame_vertical_width/2`
  - Explanation: Start from left edge `-halfWidth`, move inward by half the vertical frame width to reach the centerline
- **Right frame center X**: `rightFrameX = +halfWidth - frame_vertical_width/2`
  - Explanation: Start from right edge `+halfWidth`, move inward by half the vertical frame width to reach the centerline

**Verification**: The distance between left and right frame centerlines should be:
- `rightFrameX - leftFrameX = width - frame_vertical_width = 2·halfWidth - frame_vertical_width`

### Finger Center X Positions (1-based finger index i ∈ [1..fingers])
- **First finger center**: `x₁ = leftFrameX + frame_vertical_width/2 + frame_to_finger_d + finger_vertical_width/2`
- **Uniform pitch**: `pitch = finger_vertical_width + finger_d`
- **General**: `xᵢ = x₁ + (i-1)·pitch`

### Middle Horizontal Bar Endpoints (centered at y = 0)
- **Left endpoint**: `x_left = x₁ + finger_vertical_width/2`
- **Right endpoint**: `x_right = x_fingers - finger_vertical_width/2`
- Draw as: `dbCreatePath(... list(list(x_left 0.0) list(x_right 0.0)) middle_horizontal_width)`

### Vertical Finger Segment Definitions
For even-index fingers (to avoid middle bar window):
- **Upper Y**: `upper_y = h_middle_y + spacing + middle_horizontal_width/2`
- **Lower Y**: `lower_y = h_middle_y - spacing - middle_horizontal_width/2`

### Via Placement Parameters
- **H-left X**: `h_left_x = x₁ - finger_vertical_width/2`
- **H-right X**: `h_right_x = x_fingers + finger_vertical_width/2`
- **Via X-center**: `x_center = (h_left_x + h_right_x)/2`

*Note: Via column and row counts are computed using technology-specific formulas (see Technology_Configs/ for pitch_cut and margin values).*

---

## Via Array Sizing (Technology-Dependent)

**Goal**: Pack as many via cuts as reasonably allowed by the metal widths without violating DRC, and keep the pattern centered for symmetry.

### Deterministic Sizing (Heuristic)

*Note: Actual `pitch_cut` and `margin` values are technology-specific. See Technology_Configs/ for specific values.*

- Use `pitch_cut` and small `margin` from technology config
- **Columns**: `cut_columns = max(1, floor((h_right_x - h_left_x + margin) / pitch_cut))`
- **Rows (top/bottom)**: `cut_rows_topbot = max(1, floor((frame_horizontal_width + margin) / pitch_cut))`
- **Rows (middle)**: `cut_rows_mid = max(1, floor((middle_horizontal_width + margin) / pitch_cut))`

### Centering and Symmetry
- All via rows share `x_center = (h_left_x + h_right_x)/2`
- Prefer odd counts (when feasible) to place one cut exactly on the centerline
- If even counts are required, they should be centered symmetrically around the centerline

### Ties to Width Quantization
- Horizontal widths are quantized per technology (see Technology_Configs/)
- Row counts roughly follow quantization: rows ≈ floor((width + margin) / pitch_cut)
- Adjust based on actual DRC spacing/enclosure feedback

### DRC Feedback Loop
- If DRC flags spacing/enclosure violations, reduce `cut_rows_*` or `cut_columns` first
- If still failing, slightly increase the corresponding metal widths (while respecting overall constraints such as H_max)
- Keep arrays reasonable; ensure the chosen `viaDef` supports the requested arrays

### Via Definition Name
- Use `higher_lower` (e.g., `M5_M4`, `M7_M6`)
- Ensure this `viaDef` exists in the tech
- If not, correct the order or choose the valid adjacent layer name

---

## Procedural Drawing Checklist

For each metal layer L in `layerList` (ordered top → bottom):

1. **Vertical fingers**
   - For i = 1..fingers:
     - **If i is odd**: Draw one vertical path from `(xᵢ, h_bottom_y)` to `(xᵢ, h_top_y)` with width `finger_vertical_width`
     - **If i is even**: Draw two vertical paths to avoid the middle window:
       - Top segment: from `(xᵢ, top_minus_frame)` to `(xᵢ, upper_y)`
       - Bottom segment: from `(xᵢ, lower_y)` to `(xᵢ, bottom_minus_frame)`

2. **Middle horizontal bar**
   - One horizontal path at y = 0, from `(x_left, 0)` to `(x_right, 0)` with width `middle_horizontal_width`

3. **Vertical frame lines** (CRITICAL: Position and length)
   - **Left vertical frame**: 
     - Centerline X: `leftFrameX = -halfWidth + frame_vertical_width/2`
     - Start Y: `bottom_minus_frame = outer_bottom + frame_horizontal_width = -halfHeight + frame_horizontal_width`
     - End Y: `top_minus_frame = outer_top - frame_horizontal_width = +halfHeight - frame_horizontal_width`
     - Draw: from `(leftFrameX, bottom_minus_frame)` to `(leftFrameX, top_minus_frame)` with width `frame_vertical_width`
     - **Length verification**: `top_minus_frame - bottom_minus_frame = 2·halfHeight - 2·frame_horizontal_width = height - 2·frame_horizontal_width`
   - **Right vertical frame**: 
     - Centerline X: `rightFrameX = +halfWidth - frame_vertical_width/2`
     - Same Y coordinates as left frame
     - Draw: from `(rightFrameX, bottom_minus_frame)` to `(rightFrameX, top_minus_frame)` with width `frame_vertical_width`

4. **Horizontal frame lines** (CRITICAL: Position and span)
   - **Top horizontal frame**:
     - Center Y: `y_center_top = outer_top - frame_horizontal_width/2 = +halfHeight - frame_horizontal_width/2`
     - Left edge X: `x_left_edge = leftFrameX - frame_vertical_width/2 = -halfWidth`
     - Right edge X: `x_right_edge = rightFrameX + frame_vertical_width/2 = +halfWidth`
     - Draw: path from `(x_left_edge, y_center_top)` to `(x_right_edge, y_center_top)` with width `frame_horizontal_width`
     - **Verification**: The top edge of this bar should be at `y = outer_top = +halfHeight`, and the bottom edge at `y = outer_top - frame_horizontal_width`
   - **Bottom horizontal frame**:
     - Center Y: `y_center_bottom = outer_bottom + frame_horizontal_width/2 = -halfHeight + frame_horizontal_width/2`
     - Same X span as top frame: from `x_left_edge = -halfWidth` to `x_right_edge = +halfWidth`
     - Draw: path from `(x_left_edge, y_center_bottom)` to `(x_right_edge, y_center_bottom)` with width `frame_horizontal_width`
     - **Verification**: The bottom edge of this bar should be at `y = outer_bottom = -halfHeight`, and the top edge at `y = outer_bottom + frame_horizontal_width`

After metals for all layers are drawn:

5. **Vias between each adjacent pair (upper, lower) in layerList**
   - Use viaDef name `upper_lower`
   - Place three rows (centered at the same `x_center = (h_left_x + h_right_x)/2`):
     - Top row center: `(x_center, +halfHeight - frame_horizontal_width/2)` with `cut_rows_topbot × cut_columns`
     - Bottom row center: `(x_center, -halfHeight + frame_horizontal_width/2)` with `cut_rows_topbot × cut_columns`
     - Middle row center: `(x_center, 0)` with `cut_rows_mid × cut_columns`

6. **BOT Terminal Via Stack** (CRITICAL for array routing)
   - **Location**: BOT terminal center at `(0, 0)` - **same position as middle row via and BOT pin**
   - **Size**: **Same as middle row via**: `cut_rows_mid × cut_columns` (same via array size)
   - **Layer scope**: **CRITICAL** - Create via stack connecting **ALL adjacent metal layer pairs** from **highest to lowest layer available in the technology**
     - This includes **ALL technology metal layers**, not just the layers in `layerList`
     - Example for 28nm (M1-M7): Create `M7_M6`, `M6_M5`, `M5_M4`, `M4_M3`, `M3_M2`, `M2_M1` all at `(0, 0)` with `cut_rows_mid × cut_columns`
   - **Via naming**: Use `higher_lower` convention for each adjacent pair
   - **Purpose**: Ensures array routing can use **any metal layer** and will always have a connection path
   - **Key point**: Same position and size as middle row via, but connects **all technology layers** for universal connectivity

Finally on the top metal only:

7. **Pins**
   - `TOP` at `(0, +halfHeight - frame_horizontal_width/2)`
   - `BOT` at `(0, 0)`

---

## Indexing and Ordering Conventions

- **Finger indices**: In formulas are 1-based. Conceptually, index 0 in helper lists often maps to a frame center, indices 1..fingers map to finger centers, and the last index maps to the opposite frame center.
- **Layer list**: Must be ordered from top to bottom, e.g., `list("METAL5" "METAL4" "METAL3")` or `list("M7" "M6" "M5")`. Adjacent pairs become `(METAL5, METAL4)`, `(METAL4, METAL3)` for via insertion.
- **Via naming**: Uses `higher_lower` order (e.g., `M5_M4`). If input order is reversed, correct to high_low before generating.

---

## Parameter Definitions

### Key Parameters
- `h_height`: Vertical length of the H-shape main plate (H-shape region)
- `frame_to_finger_d`: Horizontal distance from outer frame vertical line to nearest finger
- `finger_d`: Horizontal spacing between adjacent fingers
- `frame_vertical_width`: Width of outer frame verticals
- `finger_vertical_width`: Width of finger verticals
- `frame_horizontal_width`: Width of outer frame horizontals
- `middle_horizontal_width`: Width of middle horizontal bar
- `spacing`: Vertical gap from bottom of top horizontal frame to top of H-shape region
- `fingers`: Number of fingers (odd ≥ 3)
- `layerList`: Ordered list of metal layer names (top to bottom)

### Naming and Conversion
- **Relation between total height and h_height**: `height = h_height + 2·spacing + 2·frame_horizontal_width`
- Any total height limit must be converted to an `h_height` upper bound before tuning

---

## Consistency Requirements

- All metal layers share identical parameters and strict alignment
- Via positions must match across all layers
- Use quantized horizontal widths for clean via arrays (per technology config)

---

## Capacitance scaling guidance (H-shape specific)

When increasing capacitance for H-shape under technology constraints:
- Priority order (respect DRC and adjacency):
  - Increase `fingers` (keep count odd)
  - Increase stacked metal layer count (use adjacent pairs only)
  - Increase `h_height` and recompute total height `height = h_height + 2·spacing + 2·frame_horizontal_width` to satisfy `≤ H_max`
  - Reduce spacings within minima (`finger_d`, `frame_to_finger_d`, `spacing`) when safe
- Caution on widths:
  - Increasing `finger_vertical_width` generally reduces effective plate overlap; avoid unless needed for DRC/EM
  - Horizontal widths (`frame_horizontal_width`, `middle_horizontal_width`) follow technology quantization; consider stepwise increases that also improve via rows
- Step sizing:
  - Far from target: use larger steps (e.g., `fingers` +2..+8, layers +1..+3, `h_height` +10%..+30%) with validation each round
  - Near target (~20% error): switch to small-step tuning; prefer not to change `fingers`/layer count to avoid overshoot

These guidelines complement Phase 1 iteration rules in `01_Workflow_Framework.md`.

---

## Related Documents

- **02_Python_SKILL_Integration.md**: SKILL command patterns for implementing this structure
- **03_02_H_Shape_Dummy_Generation.md**: Dummy capacitor generation based on this structure
- **Technology_Configs/**: Technology-specific DRC minima, via sizing parameters, and quantization rules
- **Technology_Configs/INTERFACE_SPEC.md**: Required interface contract for technology configurations


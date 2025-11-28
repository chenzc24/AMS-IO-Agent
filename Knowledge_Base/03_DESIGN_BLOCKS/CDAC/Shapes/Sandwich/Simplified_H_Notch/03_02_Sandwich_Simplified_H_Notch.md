# Sandwich Variant — H‑core with Vertical‑Frame Notch (top/bottom rectangular plates)

## Overview

This document defines the **Sandwich variant with H-core and vertical-frame notch** capacitor structure. The structure consists of solid rectangular plates on top and bottom layers, with a middle layer containing an outer rectangular frame (BOT net) and an H-shape finger structure (TOP net). The H-shape consists of multiple vertical fingers and a middle horizontal bar spanning the entire width. Vertical frame notches allow the horizontal bar to pass through without shorting to the frame.

**Key characteristics**:
- Top/bottom layers: solid rectangular plates (BOT net)
- Middle layer: outer rectangular frame (BOT net) with vertical notches + H-shape finger structure (TOP net)
- H-shape structure: multiple vertical fingers with a middle horizontal bar
- Vertical frame notches: centered at y=0 to allow horizontal bar passage

**Applicability**: This structure specification applies to all Sandwich H-core variant designs across all technology nodes. Technology-specific parameters (DRC minima, via sizing, etc.) are defined in Technology_Configs/.

---

## Physical Structure

### Main Components

- **Top/Bottom plates** (`L_top`, `L_bot`): Simple full rectangles, dimensions computed from finger layout and frame parameters (BOT net)
- **Middle layer** (`L_mid`):
  - **Outer rectangular frame** (BOT net): Width `frame_width` on all four sides, with centered notch openings on vertical sides to allow H-structure to pass through
  - **H-shape structure** (TOP net):
    - Multiple vertical fingers: odd-index fingers span full height; even-index fingers split into top/bottom segments to avoid middle bar
    - Middle horizontal bar at `y = 0` with width `middle_horizontal_width` spanning the full device width
- **Notch openings**: Vertical frame notches of height `notch_height = middle_horizontal_width + 2×spacing` centered at `y = 0`

### Layer Order

- Layers (top → bottom): `L_top`, `L_mid`, `L_bot`
- Nets:
  - `BOT = { L_top solid plate ∪ L_mid frame ∪ L_bot solid plate }`
  - `TOP = { L_mid vertical fingers ∪ L_mid middle horizontal bar }`

### Isolation Rules

- H-shape structure (TOP) must be isolated from the middle‑layer frame (BOT)
- No vias are allowed on the TOP fingers/bar; vias only on BOT (frame) to connect to plates
- Vertical fingers and horizontal bar form continuous H-shape in TOP net
- Notch height must accommodate horizontal bar with spacing clearance

---

## Cross-layer Connections (Vias)

### Via Placement Rules

**CRITICAL**: Vias are placed **ONLY on BOT net** (frame), **NOT on TOP net** (fingers or horizontal bar).

### Via Arrays on Horizontal Frame Bands

- **Location**: Top and bottom horizontal frame bands
- **Layer connections**:
  - `layer_top↔layer_mid`: via arrays on top and bottom horizontal frame bands
  - `layer_mid↔layer_bot`: via arrays at corresponding positions
- **Placement**: Centered at frame band midpoint to maximize coverage
- **Span**: Entire device width

### Via Array Sizing

- **Rows** (perpendicular to frame): `rows = 1` (single row is sufficient for frame width)
- **Columns** (along frame): `cols = max(1, floor((total_width + via_margin)/via_pitch_cut))`
- **Purpose**: Connect top/bottom plates to middle frame for BOT net connectivity

### Via Definition Requirements

- Use adjacent‑layer via definitions only
- Ensure viaDefs exist in techfile
- Via naming: `higher_lower` (e.g., `M5_M4`, `M7_M6`)

### Vertical Frame Notches

- **CRITICAL**: Do NOT place vias in notch areas (vertical frame openings)
- Notch areas must remain clear to allow horizontal bar passage
- If the process requires via belts on vertical frame sides, extend placement heuristics while keeping notch areas clear

---

## Pins

- **TOP pin**: Place at `(0,0)` on `layer_mid` using `dbCreateLabel`
- **BOT pin**: Place at `(0,0)` on `layer_top` using `dbCreateLabel`

**Coordinate system**: Origin `(0,0)` at device center

---

## Key Geometric Quantities

### Primary Parameters (user specifies)

- **Layers**: `layer_top`, `layer_mid`, `layer_bot`
- **Frame**: `frame_width` — width of outer frame on all sides
- **H-shape fingers**:
  - `fingers` — number of vertical fingers (odd recommended for symmetry)
  - `finger_vertical_width` — width of each vertical finger
  - `finger_d` — spacing between adjacent fingers
  - `middle_horizontal_width` — width of middle horizontal bar
  - `h_height` — vertical extent of H-shape (finger height)
- **Clearances**:
  - `spacing` — clearance between H-shape and frame
  - `frame_to_finger_d` — horizontal spacing from frame inner edge to fingers
- **Vias**: `via_pitch_cut`, `via_margin` (for BOT net only)

### Derived Dimensions

- `total_width = 2×frame_width + 2×frame_to_finger_d + fingers×finger_vertical_width + (fingers-1)×finger_d`
- `total_height = 2×frame_width + 2×spacing + h_height`
- `notch_height = middle_horizontal_width + 2×spacing` (exact)

### Coordinate Boundaries

- `half_width = total_width / 2`
- `half_height = total_height / 2`

### Frame Boundaries

- **Outer bounds**:
  - `outer_top = +half_height`
  - `outer_bottom = −half_height`
- **Inner bounds**:
  - `top_minus_frame = outer_top − frame_width`
  - `bottom_minus_frame = outer_bottom + frame_width`
- **Vertical frame x-centers**:
  - `left_frame_x = −half_width + frame_width/2`
  - `right_frame_x = +half_width − frame_width/2`

### Notch Boundaries

- `notch_y1 = −notch_height/2` (centered at y=0)
- `notch_y2 = +notch_height/2` (centered at y=0)

### H-shape Geometry

- **H region boundaries**:
  - `h_top_y = outer_top − frame_width − spacing`
  - `h_bottom_y = −h_top_y`
  - `h_middle_y = 0`
- **Finger positions**:
  - `pitch = finger_vertical_width + finger_d`
  - Fingers centered horizontally with spacing `frame_to_finger_d` from frame
- **Even finger segments** (split around middle bar):
  - `upper_y = spacing + middle_horizontal_width/2`
  - `lower_y = −spacing − middle_horizontal_width/2`
- **Horizontal bar**:
  - Spans from `x = −half_width` to `x = +half_width` at `y = 0`
  - Width: `middle_horizontal_width`

### Via Array Geometry

- **Rows**: `rows = 1` (single row sufficient for frame width)
- **Columns**: `cols = max(1, floor((total_width + via_margin)/via_pitch_cut))` (span entire width)
- **Placement**: Centered at frame band midpoint

### Constraints

- `notch_height = middle_horizontal_width + 2×spacing` (exact)
- `fingers` should be odd for symmetric layout (recommended)
- All dimensions (`total_width`, `total_height`) are computed from primary parameters; do not specify directly

---

## Procedural Drawing Checklist

### 1. Top Plate (`L_top`, BOT net)

- Draw rectangle with bbox `((-half_width, outer_bottom), (half_width, outer_top))` using `dbCreateRect`
- Assign to BOT net

### 2. Bottom Plate (`L_bot`, BOT net)

- Draw rectangle with the same bbox `((-half_width, outer_bottom), (half_width, outer_top))` using `dbCreateRect`
- Assign to BOT net

### 3. Middle Frame (`L_mid`, BOT net) with Notches

- **Top horizontal band**: Rectangle covering full width with thickness `frame_width` at top
  - Bbox: `((-half_width, top_minus_frame), (half_width, outer_top))`
- **Bottom horizontal band**: Rectangle covering full width with thickness `frame_width` at bottom
  - Bbox: `((-half_width, outer_bottom), (half_width, bottom_minus_frame))`
- **Left vertical band** with centered notch:
  - Bottom segment: from `outer_bottom` to `notch_y1`, width `frame_width`
    - Bbox: `((-half_width, outer_bottom), (left_frame_x + frame_width/2, notch_y1))`
  - Top segment: from `notch_y2` to `outer_top`, width `frame_width`
    - Bbox: `((-half_width, notch_y2), (left_frame_x + frame_width/2, outer_top))`
- **Right vertical band** with centered notch (same pattern as left):
  - Bottom segment: from `outer_bottom` to `notch_y1`, width `frame_width`
    - Bbox: `((right_frame_x - frame_width/2, outer_bottom), (half_width, notch_y1))`
  - Top segment: from `notch_y2` to `outer_top`, width `frame_width`
    - Bbox: `((right_frame_x - frame_width/2, notch_y2), (half_width, outer_top))`
- Assign all frame segments to BOT net

### 4. H-shape Fingers (`L_mid`, TOP net)

- **Vertical fingers**: For each finger i = 1..fingers:
  - Compute finger x-position: `xi = -half_width + frame_width + frame_to_finger_d + (i-1)×pitch + finger_vertical_width/2`
  - If i is **odd**: Draw vertical path from `(xi, h_bottom_y)` to `(xi, h_top_y)` with width `finger_vertical_width`
  - If i is **even**: Draw two vertical paths to avoid middle bar:
    - Top segment: from `(xi, upper_y)` to `(xi, top_minus_frame)` with width `finger_vertical_width`
    - Bottom segment: from `(xi, bottom_minus_frame)` to `(xi, lower_y)` with width `finger_vertical_width`
- **Middle horizontal bar**: Draw path at `y = 0` from `x = −half_width` to `x = +half_width` with width `middle_horizontal_width`
  - Bar must pass through notch openings without touching frame
- Assign all H-shape elements to TOP net

### 5. Vias (BOT net only)

- **Place via arrays on horizontal frame bands**:
  - `layer_top↔layer_mid`: via arrays on top and bottom horizontal frame bands
  - `layer_mid↔layer_bot`: via arrays at corresponding positions
- **Via array sizing**:
  - Rows: `rows = 1`
  - Columns: `cols = max(1, floor((total_width + via_margin)/via_pitch_cut))`
- **Placement**: Centered at frame band midpoint to maximize coverage
- **CRITICAL**: Do NOT place vias on TOP net (fingers or horizontal bar)
- **CRITICAL**: Do NOT place vias in notch areas

### 6. Pins

- **TOP pin**: Place at `(0,0)` on `layer_mid` using `dbCreateLabel`
- **BOT pin**: Place at `(0,0)` on `layer_top` using `dbCreateLabel`

---

## Function Contracts

### Input Parameters

**Primary inputs** (user provides):
- Layers: `layer_top`, `layer_mid`, `layer_bot`
- Frame: `frame_width`
- H-shape: `fingers`, `finger_vertical_width`, `finger_d`, `middle_horizontal_width`, `h_height`
- Clearances: `spacing`, `frame_to_finger_d`
- Vias: `via_pitch_cut`, `via_margin`

### Output Geometry

**Derived outputs** (computed):
- `total_width`, `total_height`, `notch_height`
- All coordinate boundaries (frame, notch, H-shape)
- Via array dimensions

### Execution Sequence

1. **Geometry Synthesis**: Compute all derived dimensions and coordinate boundaries from primary parameters
   - Validate required inputs are present
   - Compute `total_width`, `total_height`, `notch_height`
   - Compute all frame, notch, and H-shape boundaries
   - Compute via array sizing

2. **Layout Script Generation**: Generate flattened SKILL layout commands
   - Draw top plate (L_top, BOT net)
   - Draw bottom plate (L_bot, BOT net)
   - Draw middle frame with notches (L_mid, BOT net)
   - Draw H-shape structure (L_mid, TOP net)
   - Place via arrays on horizontal frame bands (BOT net only)
   - Place pins (TOP on L_mid, BOT on L_top)
   - See "Procedural Drawing Checklist" for detailed steps

### Validation Requirements

- **Isolation**: No metal contact between `L_mid` TOP bar and any `L_mid` BOT frame segment; check notch clearance
- **Adjacency**: Vias use adjacent metals only
- **Dimensions**: Plates and bar span `total_width`; frame thickness equals `frame_width` everywhere except centered notch openings
- **Numeric formatting**: 5 decimals in generated SKILL; consistent draw order; no duplicate plates
- **Notch height**: Must equal `middle_horizontal_width + 2×spacing` exactly

---

## Notes

- This structure combines Sandwich topology with H-shape finger design for higher capacitance density
- Vertical frame notches are the only interruptions in the frame; ensure notch height equals `middle_horizontal_width + 2×spacing` exactly
- Odd fingers span full H-region height (`h_bottom_y` to `h_top_y`); even fingers extend to frame inner edges (`bottom_minus_frame` to `lower_y` and `upper_y` to `top_minus_frame`) to maximize capacitance while avoiding the middle bar
- Via arrays on horizontal frame bands should span entire device width for maximum connectivity
- If the process requires via belts on vertical frame sides, extend placement heuristics while keeping notch areas clear
- All dimensions (`total_width`, `total_height`) are computed from primary parameters; do not specify directly

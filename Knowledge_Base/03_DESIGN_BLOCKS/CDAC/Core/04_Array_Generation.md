# CDAC Array Generation - Mosaic method for creating capacitor arrays

## Overview

This document defines rules for generating capacitor arrays using the mosaic method. These rules apply to all capacitor shapes.

**CRITICAL WORKFLOW**: Always **MERGE adjacent positions FIRST**, then generate mosaic commands. Never generate individual mosaics for each position.

---

## Critical Requirements

### Arrays (mosaic of an existing unit cell layout)
```skill
; IMPORTANT: Order note - first pitch is Y (row step), second is X (column step)
dbCreateParamSimpleMosaic(cv dbOpenCellView("LIB" "UNIT_CELL" "layout") "mosaic_RxC" list(x0 y0) "R0" rows cols pitch_y pitch_x nil)
```

### Pitch Calculation Rule

**MANDATORY FORMULA** (use SUBTRACTION, NOT addition):
- `pitch_x = unit_width - frame_vertical_width`
- `pitch_y = unit_height - frame_horizontal_width`

**VERIFICATION**: `pitch_x < unit_width` and `pitch_y < unit_height` (if not, you made an error)

**WHY**: Adjacent cells share a common frame boundary (zero gap). Adding spacing creates gaps and DRC violations.

### Routing and Pin Generation Requirements

**MANDATORY**:
- **Routing generation (Step 4)**: Generate routing wires for ALL connection groups - NO exceptions
- **Pin generation (Step 4.4)**: Generate pin labels when pin information exists - place pins ON routing wires
- **DO NOT skip routing or pin generation** - Array without routing/pins is incomplete and non-functional

### Dummy Capacitor Isolation

**MANDATORY**:
- **DO NOT connect dummy capacitors (value "0") to any routing net** - Dummy BOT terminals must remain floating
- **DO NOT connect dummy capacitors together** - Dummy capacitors must be isolated
- **DO NOT connect dummy capacitors to functional capacitors** - Dummy and functional must be completely isolated
- Connection groups contain ONLY functional capacitors - dummy positions are excluded from routing

### Verification Requirements

**MANDATORY**:
- **DRC verification (Step 6)**: MUST be performed after array generation and routing - MUST pass before PEX
- **PEX extraction and capacitance analysis (Step 7)**: MUST be performed after DRC passes
- Phase 3 is NOT complete without both DRC and PEX verification

### Mosaic Placement Strategy

**MANDATORY - CRITICAL WORKFLOW ORDER**:
- **STEP 1: MERGE FIRST** - **ALWAYS merge adjacent positions into continuous rectangular regions BEFORE generating any mosaic commands**
- **STEP 2: THEN GENERATE MOSAIC** - **ONLY AFTER merging**, generate `dbCreateParamSimpleMosaic` commands for each merged region
- **NEVER place capacitors one by one** - NEVER generate individual mosaics for each position
- **Separate functional and dummy placement**: Place functional capacitors first (skip dummy positions), then place dummy capacitors in separate mosaics
- **Generate ONE `dbCreateParamSimpleMosaic` per continuous region** - dimensions must be > 1×1 for merged regions
- **Workflow**: Identify regions → Merge adjacent positions → Generate mosaic commands (in that order)

---

## Prerequisites

**Before generating CDAC array**:
1. Unit cell layout must be completed (Phase 1)
2. Dummy cell layout must be completed (Phase 2)
3. Array analysis result must be available (from CDAC analysis agent)

**Array analysis result structure**:
- `array_structure`: Contains `array_data` (2D array of capacitor values) and `dimensions` (rows, cols)
- `connection_groups`: List of connection groups, each containing:
  - `value`: Capacitor value (e.g., "128", "64")
  - `positions`: List of `[row, col]` pairs (0-based array indices)
  - `pin_name`: Optional pin name if Excel contains pin assignments

**Save analysis result**: Save JSON to file (e.g., `{excel_filename}_cdac_layout.json`) and reuse for layout generation.

---

## Step-by-Step Implementation

### Step 1: Load Array Analysis Data

Load the structured analysis data from saved JSON file:
- Read `array_structure` (dimensions and array_data)
- Read `connection_groups` (connection relationships)
- Extract `rows` and `cols` from dimensions

**Required information**:
- Array dimensions (`rows`, `cols`)
- `array_data`: 2D array where "0" = dummy, non-zero = functional capacitor
- `connection_groups`: Groups of capacitors that must be connected together

### Step 2: Calculate Array Parameters

#### 2.1 Extract Unit Cell Dimensions

From unit cell geometry:
- `unit_width` = `geometry['total_width']` (or `geometry['unit_width']` or `geometry['width']`)
- `unit_height` = `geometry['total_height']` (or `geometry['unit_height']` or `geometry['height']`)

#### 2.2 Extract Frame Dimensions

From unit cell geometry:
- `frame_vertical_width` (or `geometry['frame_width']` for vertical frames)
- `frame_horizontal_width` (or `geometry['frame_width']` for horizontal frames)

#### 2.3 Calculate Pitch

**Formula**:
- `pitch_x = unit_width - frame_vertical_width`
- `pitch_y = unit_height - frame_horizontal_width`

**Verification**: `pitch_x < unit_width` and `pitch_y < unit_height` (if not, ERROR - you used addition instead of subtraction)

**Principle**: Adjacent cells share a common frame boundary (zero gap). The pitch is the distance between core regions, not between cell boundaries.

#### 2.4 Calculate Array Origins

For centered array at (0, 0):
- `x0 = -0.5 * (cols - 1) * pitch_x`
- `y0 = 0.5 * (rows - 1) * pitch_y`

**Coordinate System** (unified for both mosaic and routing):
- Formula: `y = y0 - row * pitch_y` where `y0 = 0.5 * (rows - 1) * pitch_y`
- Row 0 (Excel top) maps to maximum y-coordinate
- Both mosaic placement and routing use the SAME coordinate system to ensure alignment

#### 2.5 Get BOT Terminal Offset

BOT terminal position relative to unit cell origin (from actual unit cell design):
- `bot_offset_x`: BOT x-position in unit cell's local coordinate system
- `bot_offset_y`: BOT y-position in unit cell's local coordinate system

**Note**: Do NOT assume BOT is at center. Check actual unit cell design to determine offset.

### Step 3: Generate Array Mosaic Placement

#### 3.1 Strategy: Separate Functional and Dummy Capacitor Placement

**CRITICAL WORKFLOW - MUST FOLLOW THIS ORDER**:

1. **FIRST: MERGE ADJACENT POSITIONS** (DO NOT skip this step)
   - **MANDATORY**: Identify and merge ALL adjacent positions into continuous rectangular regions
   - **DO NOT** generate any mosaic commands until merging is complete
   - Combine adjacent rows/columns of the same cell type into single rectangular regions

2. **THEN: GENERATE MOSAIC COMMANDS** (only after merging)
   - **ONLY AFTER** merging is complete, generate `dbCreateParamSimpleMosaic` commands
   - One mosaic command per merged region
   - Minimize mosaic count: Use as few `dbCreateParamSimpleMosaic` commands as possible

**Placement order**:
- **First**: Place functional capacitors in continuous regions (skip dummy positions)
- **Then**: Place dummy capacitors in continuous regions (fill skipped positions)

**Key principle**: **MERGE FIRST, MOSAIC SECOND** - Never generate mosaics before merging adjacent positions

#### 3.2 Place Functional Capacitors (Main Array)

**Step 3.2.1: Identify and Merge Continuous Functional Regions**

**CRITICAL: This step MUST be completed BEFORE generating any mosaic commands.**

From `array_data`, identify and merge continuous rectangular regions of functional capacitors (non-zero values):
- Skip all positions with value "0" (dummy)
- **MANDATORY: Merge ALL adjacent functional positions** regardless of their values (1, 2, 4, 8, 16, 32, 64, 128, etc.)
- **DO NOT proceed to Step 3.2.2 until ALL adjacent positions are merged into regions**

**Algorithm** (two-pass):
1. **First pass**: Scan row by row, identify continuous column segments of functional capacitors (any non-zero value) within each row
2. **Second pass**: Merge adjacent rows that have the same column range

**Detailed algorithm**:
- Initialize an empty list of regions and a `visited` matrix
- For each row from top to bottom (row 0 to row N-1):
  - For each column from left to right (col 0 to col M-1):
    - If position `(row, col)` is not visited AND `array_data[row][col] != '0'`:
      - Find maximum horizontal extent: expand rightward while all positions have non-zero values
      - Find maximum vertical extent: expand upward and downward while all positions in the column range have non-zero values
      - Mark all positions in this rectangular region as visited
      - Add this region to the list with `start_row`, `end_row`, `start_col`, `end_col`, `rows`, `cols`

**FORBIDDEN**: 
- ❌ Placing each position individually with `dbCreateParamSimpleMosaic(..., "R0", 1, 1 ...)`
- ❌ Generating one mosaic per capacitor position
- ❌ Not checking for adjacent rows with same column range

**Step 3.2.2: Generate Main Array Mosaics**

**ONLY execute this step AFTER Step 3.2.1 merging is complete.**

For each continuous functional region identified in Step 3.2.1:
- Calculate origin: `mosaic_x = x0 + start_col * pitch_x`, `mosaic_y = y0 - start_row * pitch_y`
- Calculate dimensions: `region_rows = end_row - start_row + 1`, `region_cols = end_col - start_col + 1`
- **VERIFY**: `region_rows >= 1` and `region_cols >= 1`. For merged regions, typically `region_rows > 1` or `region_cols > 1`.
- Use `dbCreateParamSimpleMosaic` with unit cell master
- Parameters: origin `(mosaic_x, mosaic_y)`, dimensions `(region_rows, region_cols)`, pitches `(-pitch_y, pitch_x)` (negative pitch_y for correct row order)

**Example**: 
- If rows 2-9, columns 1-4 are all functional → **1 mosaic**: `dbCreateParamSimpleMosaic(..., "R0", 8, 4, -2.21000, 0.66000, nil)` (8 rows × 4 columns)
- **NOT**: 32 separate mosaics with `(1, 1)` dimensions

#### 3.3 Place Dummy Capacitors (Fill Skipped Positions)

**Step 3.3.1: Identify All Dummy Positions**

From `array_data`, find all positions with value "0" (dummy):
- These are the positions skipped in the main array mosaic
- Must be filled with dummy capacitors

**Step 3.3.2: Identify and Merge Continuous Dummy Regions**

**CRITICAL: This step MUST be completed BEFORE generating any dummy mosaic commands.**

Group dummy positions into continuous rectangular regions using the same two-pass algorithm as Step 3.2.1:
- **First pass**: Scan row by row, identify continuous column segments of dummy capacitors within each row
- **Second pass**: Merge adjacent rows that have the same column range
- **DO NOT proceed to Step 3.3.3 until ALL adjacent dummy positions are merged into regions**

**Step 3.3.3: Generate Dummy Mosaics**

**ONLY execute this step AFTER Step 3.3.2 merging is complete.**

For each continuous dummy region identified in Step 3.3.2:
- Calculate origin: `mosaic_x = x0 + start_col * pitch_x`, `mosaic_y = y0 - start_row * pitch_y`
- Calculate dimensions: `region_rows = end_row - start_row + 1`, `region_cols = end_col - start_col + 1`
- Use `dbCreateParamSimpleMosaic` with dummy cell master
- Parameters: origin `(mosaic_x, mosaic_y)`, dimensions `(region_rows, region_cols)`, pitches `(-pitch_y, pitch_x)` (negative pitch_y for correct row order)

**Example pattern** (12 rows × 6 columns with mixed array):
- Main array: Rows 2-9, columns 1-4 (functional) → 1 mosaic: 8 rows × 4 columns
- Dummy placement:
  - Top 2 rows (rows 0-1): all "0" → 1 mosaic: 2 rows × 6 columns
  - Rows 2-9, columns 0: all "0" → 1 mosaic: 8 rows × 1 column
  - Rows 2-9, column 5: all "0" → 1 mosaic: 8 rows × 1 column
  - Bottom 2 rows (rows 10-11): all "0" → 1 mosaic: 2 rows × 6 columns
- **Total**: 1 main array mosaic + 4 dummy mosaics = 5 mosaics total

### Step 4: Generate Routing Connections

**MANDATORY**: Generate routing wires for ALL connection groups. NO connection group should be left without routing.

**Important**: DO NOT connect dummy capacitors (value "0") to any routing wires - dummy BOT terminals must remain floating.

#### 4.1 Select Routing Layer and Width

- **Layer selection**: Use metal layer not already used in unit cell (typically M2 or M3)
- **Wire width**: MUST match BOT via width from unit cell design

#### 4.2 Calculate BOT Terminal Positions

For each array position `(row, col)`:
- `absBotX = x0 + col * pitch_x + bot_offset_x`
- `absBotY = y0 - row * pitch_y + bot_offset_y`

#### 4.3 Route Connection Groups

**MANDATORY**: Generate routing wires for ALL connection groups. Connection groups contain ONLY functional capacitors, NOT dummy capacitors.

For each connection group in `connection_groups`:
1. Get all positions from `connection_groups[value]` (list of `[row, col]` pairs)
2. Calculate absolute BOT coordinates for each position
3. Connect ALL capacitors in the group using nearest-neighbor grid connection
4. Generate `dbCreatePath` commands with precomputed coordinates

**Routing strategy**: Nearest-neighbor grid connection (connect adjacent cells in 4 directions: up, down, left, right)

**Algorithm**:
- For each position `(row, col)` in the connection group:
  - Calculate its BOT terminal position: `(absBotX, absBotY)`
  - Check if there are adjacent positions in the same group:
    - Up: `(row-1, col)` if exists in group
    - Down: `(row+1, col)` if exists in group
    - Left: `(row, col-1)` if exists in group
    - Right: `(row, col+1)` if exists in group
  - For each adjacent position found, generate a `dbCreatePath` command connecting the two BOT terminals
  - **DO NOT connect to dummy positions** - Skip any adjacent positions that are dummy (value "0" in array_data)
- **For single-capacitor groups**: If a connection group has only 1 capacitor, it still needs to be accessible. Consider if it needs connection to a pin or leave as isolated node (but still document it).

**SKILL command**: `dbCreatePath(cv list("M2" "drawing") list(list(x1 y1) list(x2 y2)) width "extendExtend")`

#### 4.4 Add Pin Labels

**MANDATORY**: Generate pin labels when pin information exists. Pin labels MUST be placed ON the routing wire, not at arbitrary positions.

For connection groups with `pin_name` field or json with `pin_assignments` field:
- Place pin label directly on the routing wire using `dbCreateLabel`
- Generate pin for EVERY pin specified in the pin assignments
- **Position calculation**: Pin coordinates `(pin_x, pin_y)` must be on one of the routing wires for this connection group
- **CRITICAL**: Pin coordinates MUST match a point on the routing wire - DO NOT offset pin positions away from the wire

**Coordinate calculation**:
  - Use the BOT terminal coordinates directly for the pin position
  - For each connection group, find one of the BOT terminal positions (e.g., the leftmost or topmost position)
  - Use that BOT terminal's coordinates directly: `pin_x = bot_x`, `pin_y = bot_y`
  - This ensures the pin is exactly on the routing wire (which connects to the BOT terminal)

**SKILL command**: `dbCreateLabel(cv list("M2" "pin") list(pin_x pin_y) "PIN_NAME" "centerCenter" "R0" "roman" 0.1)`

### Step 5: Handle Dummy Capacitors

**MANDATORY**: Leave ALL dummy BOT terminals floating. No routing wires should connect to dummy capacitors.

- Dummy positions are identified by value "0" in array_data
- These positions are excluded from routing
- Dummy capacitors must remain isolated - do not connect them to functional capacitors or to each other

### Step 6: DRC Verification

**MANDATORY**: DRC check MUST be performed after array generation and routing. DRC MUST pass before proceeding to PEX extraction.

**Execution steps**:
1. Call `run_drc()` on the generated array layout
2. **Print Full DRC Report Content**: Print the complete returned report content in full

**If DRC passes**: Proceed immediately to Step 7 (PEX extraction)

**If DRC fails**:
- Analyze the complete DRC report and identify violations
- Common issues:
  - Routing wire spacing violations (ensure spacing ≥ 0.1 µm for critical spacings)
  - Minimum area violations (check frame areas, routing wire widths)
  - Via placement issues (check via spacing and enclosure)
  - Frame boundary violations (check pitch calculations)
- Fix violations by adjusting routing wire spacing, wire widths, via placement, or array placement parameters
- Regenerate the array with adjusted parameters
- Re-run DRC and continue iterating until DRC passes
- **All fixes must be done within Phase 3** - do NOT return to Phase 1 or Phase 2

### Step 7: PEX Extraction and Capacitance Analysis

**MANDATORY**: PEX extraction MUST be performed after DRC passes. Capacitance values MUST be analyzed after PEX extraction.

#### 7.1 Run PEX Extraction

1. Call `run_pex()` on the generated array layout (only after DRC passes)
2. **Print Full PEX Report Content**: Print the complete returned report content in full

#### 7.2 Analyze Capacitance Values

**MANDATORY**: Before extracting capacitance values, you MUST first print the complete PEX report content to understand its format and structure.

**Required analysis steps**:
1. **Print and understand PEX report format**:
   - **First**: Print the complete PEX report content returned by `run_pex()` in full
   - **Then**: Carefully read and understand the PEX report format
   - Identify where capacitance values are located in the report (e.g., in "PEX main cell original content excerpt" section)
   - Understand the format of capacitance entries (e.g., `mr_pp 'c "c_X" '("PIN_NAME" "0") VALUEf` format)
   - **DO NOT hardcode regular expressions** - instead, understand the actual format from the printed report and extract values accordingly

2. **Extract capacitance values from PEX report**:
   - Based on the actual PEX report format you observed, extract capacitance values for each connection group
   - **Important**: Extract only `("PIN_NAME" "0")` format entries (useful capacitance) - ignore `("PIN_NAME1" "PIN_NAME2")` format entries (parasitic capacitance)
   - Match pin names (e.g., LSB1, LSB2, MSB1, MSB2) from connection groups to capacitance values in the PEX report
   - Extract the capacitance value associated with each pin name
   - **Verify extraction**: Print extracted values to confirm they match the PEX report content

3. **Compare with expected values**:
   - Compare extracted capacitance values with expected values from CDAC analysis/design
   - Expected values should match the connection group configuration:
     - 1C group: Should have capacitance ≈ 1 × unit_capacitance
     - 2C group: Should have capacitance ≈ 2 × unit_capacitance
     - 4C group: Should have capacitance ≈ 4 × unit_capacitance
     - And so on for larger groups (8C, 16C, 32C, 64C, 128C, etc.)

4. **Verify correctness**:
   - Verify that connection groups have correct capacitance values matching expected multiples
   - Verify that total array capacitance matches expected distribution
   - Verify that capacitance values are consistent with the array configuration

5. **Report analysis results**:
   - State whether capacitance values are correct or if there are discrepancies
   - Document the extracted capacitance values and their comparison with expected values

**If capacitance values are correct**: Proceed to IR update and final summary. Phase 3 is complete.

**If capacitance values are incorrect or show mismatch**:
- Analyze the complete PEX report to identify the issue
- Common issues:
  - Missing or incorrect routing connections (check Step 4 routing generation)
  - Incorrect connection group assignments
  - Array placement errors
  - Via connectivity issues
- Fix the issue:
  - If routing issue: Adjust array routing/connection parameters and regenerate routing
  - If placement issue: Check array mosaic placement and regenerate if needed
  - Regenerate the array with fixes
  - Re-run DRC (Step 6) to ensure DRC still passes
  - Re-run PEX (Step 7.1) and re-analyze capacitance values (Step 7.2)
  - Continue iterating until capacitance values match expected values
- **All fixes must be done within Phase 3** - do NOT return to Phase 1 or Phase 2

---

## Coordinate System Mapping

**Excel Row Index to Layout Y-Axis**:
- Excel row 0 (topmost) = maximum y-coordinate in layout
- Excel row N-1 (bottommost) = minimum y-coordinate in layout
- Excel rows increase downward, layout y-coordinates increase upward

**Unified Coordinate System** (for both mosaic placement and routing):
- Formula: `y = y0 - row * pitch_y` where `y0 = 0.5 * (rows - 1) * pitch_y`
- Row 0 is at maximum y (top of array, matching Excel)
- Both mosaic and routing use the same coordinate system to ensure alignment

---

## Cell Naming

- **Library**: Reuse library name from Phase 1
- **Cell name**: Must be explicitly provided by user (do NOT auto-generate)
- **Destination view**: Newly created `layout` view
- **Source masters**: Use `layout` view (not layout1..layout5) from unit and dummy cells

---

## Dummy Ring Strategy

**Default strategy**: Add 1-2 rings of dummy capacitors around core array:
- Small arrays (≤4×4): 2 rings
- Medium arrays (5×5 to 8×8): 1-2 rings
- Large arrays (>8×8): 1 ring minimum

**Excel array boundary check**: 
- Check if the outermost ring of the Excel array (first row, last row, first column, last column) contains functional capacitors (non-zero values)
- **If outermost ring has functional capacitors**: Consider adding 2 rings of dummy capacitors around the array for better matching and edge effects
- **If outermost ring is already dummy (value "0")**: May use 1 ring or no additional dummy ring depending on array size

**Aspect ratio**: Choose `rows` and `cols` to achieve near-square layout (length ≈ width) while meeting minimum count.

---

## SKILL Implementation Requirements

**All calculations in Python**:
- Pitch, origins, BOT positions, routing paths - all precomputed in Python
- SKILL only executes hard-coded drawing commands

**SKILL script structure**:
- Mosaic placement commands (`dbCreateParamSimpleMosaic`)
- Routing commands (`dbCreatePath` with `"extendExtend"` parameter) - for ALL connection groups
- Pin label commands (`dbCreateLabel` for connection groups with `pin_name`) - when pin information exists

**Complete routing generation**: No TODOs, no placeholders. If user specifies CDAC layout file, routing generation is mandatory.

---

## Related Documents

- **01_Workflow_Framework.md**: Phase 3 workflow context
- **02_Python_SKILL_Integration.md**: SKILL command patterns and Python-SKILL separation
- **Shape-specific modules**: Unit geometry definitions
- **Technology_Configs/**: Technology-specific constraints

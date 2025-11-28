# Python and SKILL Integration - Code generation policies and module contracts (universal)

## ⚠️ CRITICAL: SKILL Flattening Policy (READ FIRST)

**⚠️ MANDATORY: MUST Use Python to Generate SKILL Scripts**

**ABSOLUTELY REQUIRED**: All SKILL scripts MUST be generated using Python functions (`compute_geometry()` and `render_skill()`). Do NOT write SKILL scripts manually or directly. Python must compute all geometry and render the complete flattened SKILL script. All repetition and logic must be handled in Python, not in SKILL.

**ABSOLUTELY FORBIDDEN IN SKILL SCRIPTS:**
- ❌ `foreach`, `for`, `while`, `repeat` - NO LOOPS
- ❌ `when`, `unless`, `if`, `cond`, `case`, `prog` - NO CONDITIONALS  
- ❌ `procedure`, `defun`, `lambda` - NO FUNCTIONS
- ❌ `geGetEditCellView()` - NO EDIT WINDOW DEPENDENCY
- ❌ **ANY command NOT in the whitelist** - See "SKILL Command Whitelist" section below

**ONLY ALLOWED:**
- ✅ Commands from the whitelist ONLY: `dbCreatePath`, `dbCreateRect`, `dbCreateVia`, `dbCreateLabel`, `techGetTechFile`, `techFindViaDefByName`, `dbSave`, `dbClose`
- ✅ Simple variable assignments (no functions)
- ✅ Direct `cv` parameter (provided by run_il_with_screenshot)

**ENFORCEMENT:**
- If your SKILL code contains ANY forbidden constructs, **STOP and regenerate**
- **ONLY use commands from the whitelist below - if a command is not listed, DO NOT use it**
- All repetition must be unrolled in Python, NOT in SKILL
- Python generates the script; SKILL only executes hard-coded statements
- **⚠️ CRITICAL: DO NOT add code-based compliance checking** - Comments containing words like "for" (e.g., ";; Finger 1", ";; for 1.0 fF") will cause false positives
- **Instead, ensure compliance during code generation** - When generating SKILL scripts, carefully avoid using forbidden constructs in the actual SKILL code (not in comments)
- The agent must be responsible for generating compliant SKILL code from the start, without post-generation validation checks

---

## Overview

This document defines the integration patterns and contracts between Python, SKILL, and AI decision-making components. These patterns apply to all capacitor designs regardless of shape or technology.

---

## Purpose

The integration aims to:
- Reduce duplication and improve reliability
- Keep SKILL scripts simple and deterministic
- Maintain clear separation of responsibilities between AI, Python, and SKILL

---

## Python Module Contracts

### compute_geometry(params) → geom

**Purpose**: Compute all derived geometry deterministically from primary parameters.

**Inputs**: Dictionary with all primary params (shape-dependent):
- `fingers`: number of fingers (constraints vary by shape)
- `h_height`: vertical length of active capacitor region (universal parameter, used by all shapes)
- Widths and spacings (shape-dependent): `frame_vertical_width`, `finger_vertical_width`, `frame_horizontal_width`, `frame_to_finger_d`, `finger_d`, `spacing`
- Shape-specific width parameters as needed (refer to shape module for requirements)
- `layerList`: ordered list of metal layers (top to bottom)
- `max_height`: optional total height limit (technology- or design-constraint)
- Technology-specific constraints (refer to technology config)

**Outputs**: Derived coordinates and counts as numbers (shape-dependent):
- `halfWidth`, `halfHeight`
- X positions for fingers, frames (as required by shape)
- Y positions: Common coordinates like `h_top_y`, `h_bottom_y`, `outer_top`, `outer_bottom`, `top_minus_frame`, `bottom_minus_frame`
- Shape-specific Y coordinates as needed (refer to shape module for exact coordinates)
- Via counts and positions (shape-dependent, refer to shape module for via row requirements)
- All values ready to be serialized to SKILL literals (3 decimals, 0.005 grid)

**⚠️ CRITICAL: 3-Decimal Precision and 0.005 Grid Constraint**
- **ALL numeric values** (coordinates, widths, positions, etc.) **MUST** be formatted to exactly **3 decimal places**
- **ALL numeric values MUST be multiples of 0.005** (minimum grid resolution)
- This applies to ALL outputs from `compute_geometry()`: coordinates, dimensions, via positions, pin positions, etc.
- Format: First quantize to 0.005 grid using `round(value / 0.005) * 0.005`, then format with `{value:.3f}` in Python (e.g., `0.125`, `-1.235`, `10.000`, `0.005`)
- **NO exceptions**: Every numeric literal in the generated SKILL script must have exactly 3 decimal places and be a multiple of 0.005

**Responsibilities**:
- Compute derived geometry deterministically from current parameters
- Validate constraints: height ≤ max_height (if specified), finger count parity (shape-dependent), layers within allowed set, minima/quantization rules
- Raise/return violations if any constraint is violated
- **Do NOT** choose next parameters or implement decision logic

**⚠️ CRITICAL: Implementation Method - Define Function Directly, Do NOT Use Python Helper Tool**

When implementing `compute_geometry()` in Step 2 (Generate SKILL script), **define the function directly in the code execution block**. Do NOT use `create_python_helper()` tool:

```python
# ✅ CORRECT: Define function directly in code execution block
def compute_geometry(params):
    # Implementation here
    return geometry

# Use immediately in same code block
geom = compute_geometry(params=initial_params)
```

**Why not use Python helper tool?**
- `compute_geometry()` is needed immediately in the same code execution block
- Python helper tools cannot be used in the same code execution block where they are created
- Direct function definition is simpler and more reliable for this use case
- No need for tool registration overhead when the function is only used within the same code block

**⚠️ CRITICAL: REUSE Functions Across Iteration Rounds**

**MANDATORY Code Reuse Policy:**
- **Round 1**: Define `compute_geometry()` and `render_skill()` functions once in the code execution block
- **Round 2, 3, 4, 5**: **REUSE the same function definitions** - do NOT redefine them
- Only update the input parameters passed to these functions; keep the function logic unchanged
- This ensures consistency, reduces code duplication, and prevents errors from redefinition
- Cache and reuse the SKILL template structure across rounds - only update parameter values

**Example:**
```python
# Round 1: Define functions once
def compute_geometry(params):
    # ... implementation ...
    return geometry

def render_skill(params, geom):
    # ... implementation ...
    return skill_code

# Round 1: Use functions
geom1 = compute_geometry(params_round1)
skill1 = render_skill(params_round1, geom1)

# Round 2: REUSE same functions, only change parameters
geom2 = compute_geometry(params_round2)  # Same function, different params
skill2 = render_skill(params_round2, geom2)  # Same function, different params

# Round 3, 4, 5: Continue reusing the same functions
```

**DO NOT do this:**
```python
# ❌ WRONG: Redefining functions in each round
# Round 1
def compute_geometry(params): ...
# Round 2
def compute_geometry(params): ...  # ❌ Don't redefine!
# Round 3
def compute_geometry(params): ...  # ❌ Don't redefine!
```

**Note**: Parameter constraints (finger count parity, minimum values, etc.) are shape-dependent. Refer to shape-specific structure documents (in `03_Shape_Specifics/`) for exact requirements.

### render_skill(params, geom, template, anchors=None) → il_path

**Purpose**: Render a complete flattened SKILL script from parameters and geometry.

**Inputs**:
- `params`: Primary parameter dictionary
- `geom`: Geometry dictionary from `compute_geometry()`
- `template`: Stable SKILL template or template path
- `anchors`: Optional dictionary of anchored regions for incremental edits

**Outputs**:
- Path to generated `.il` file
- The generated file must be a single runnable script per round

**Responsibilities**:
- Render a complete `.il` file either by template substitution or by replacing only anchored blocks
- Always produce a single runnable script per round
- **MUST ensure ALL numeric values are formatted to exactly 3 decimal places and are multiples of 0.005** (e.g., `0.125`, `-1.235`, `10.000`, `0.005`)
- Keep ordering/grouping consistent with structure specifications
- **Do NOT** implement control flow or logic in SKILL
- **Do NOT** implement decision logic or parameter selection

---

## SKILL Flattening Policy (STRICT) - DETAILED

### ❌ FORBIDDEN Examples (DO NOT USE)

**Wrong - Using conditionals:**
```skill
if(cv == nil then
    cv = dbOpenCellViewByType(...)
)
```

**Wrong - Using loops:**
```skill
when(cv~>shapes
    foreach(shape cv~>shapes
        dbDeleteObject(shape)
    )
)
```

**Wrong - Using edit window:**
```skill
cv = geGetEditCellView()
```

### ✅ CORRECT Alternatives

**Correct - Direct cv usage (provided by run_il_with_screenshot):**
```skill
;; cv is provided automatically, do NOT call dbOpenCellView or geGetEditCellView
;; cv is already opened and ready to use
```

**Correct - No clearing needed (each iteration uses a new view):**
```skill
;; Do NOT clear - each iteration uses layout1, layout2, etc. (new views)
;; Just draw directly
```

**Correct - Unroll loops in Python:**
```python
# Python side: Generate all statements
for i in range(1, fingers+1):
    skill_content += f"dbCreatePath(cv list(\"{layer}\" \"drawing\") ...)\n"
# SKILL side: Only flat statements, no loops
```



## SKILL Command Whitelist (ONLY USE THESE)

**CRITICAL: Only use SKILL commands explicitly listed below. Do NOT use any other commands.**

### ✅ ALLOWED Commands (Whitelist)

**1. Tech File Operations:**
- `techGetTechFile(cv)` - Get technology file
- `techFindViaDefByName(tech "VIA_NAME")` - Find via definition

**2. Database Creation Commands:**
- `dbCreatePath(cv layer pointList width)` - Create metal paths
- `dbCreatePath(cv layer pointList width "extendExtend")` - Create metal paths with extend mode (for routing)
- `dbCreateRect(cv layerPurpose bbox)` - Create rectangles (plates only; see pattern below)
- `dbCreateVia(cv viaDefId point orientation viaParams)` - Create via arrays
- `dbCreateLabel(cv layer point text alignment orientation font size)` - Create labels/pins

**⚠️ CRITICAL RULE: Drawing Command Selection**
- **MUST use `dbCreatePath` for ALL capacitor structures** (fingers, frames, middle bars, connecting bars, etc.)
- **ONLY exception**: `dbCreateRect` is allowed **ONLY** for Sandwich capacitor's top and bottom solid plates (L_top and L_bot layers)
- **FORBIDDEN**: Using `dbCreateRect` for any other structures (fingers, frames, middle bars, etc.) - these MUST use `dbCreatePath`
- This rule applies to all capacitor shapes (H-shape, I-Type, Sandwich, etc.)

**3. Mosaic (Array Generation):**
- `dbCreateParamSimpleMosaic(cv masterCell name origin orientation rows cols pitch_y pitch_x params)`
- `dbOpenCellView("LIB" "CELL" "VIEW")` - Only for opening master cells, NOT destination

**4. Save/Close:**
- `dbSave(cv)` - Save cellview
- `dbClose(cv)` - Close cellview

**5. Variable Operations (use sparingly, only when necessary):**
- `tech = techGetTechFile(cv)` - Required for via definitions
- `viaDefId = techFindViaDefByName(tech "VIA_NAME")` - Required for dbCreateVia
- `viaParams = list(...)` - Required for dbCreateVia
- List creation: `list(...)`
- **Prefer direct numeric values in dbCreatePath/dbCreateLabel** - all coordinates should be pre-computed in Python
- **No intermediate coordinate variables needed** - Python generates final values directly

**6. Comments:**
- `;; comment text`

**CRITICAL RULE:**
- **ONLY** the commands listed above are allowed
- If a command is not in this whitelist, **DO NOT use it**


---

## SKILL Command Patterns (Syntax Only)

This section documents only allowed command signatures/examples. All placement rules (where/how to place shapes or vias, counts, segmentation, alignment) are defined by the active shape module under `03_Shape_Specifics/` and the Technology Configs.

**Key Syntax:**

**Vertical/horizontal metals:**
```skill
dbCreatePath(cv list("METAL_NAME" "drawing") list(list(x1 y1) list(x2 y2)) width)
; All coordinates (x1, y1, x2, y2) and width MUST be formatted to 3 decimals and be multiples of 0.005 (e.g., 0.125, 1.000, 0.005)
```

**Routing wires (with extend mode):**
```skill
dbCreatePath(cv list("METAL_NAME" "drawing") list(list(x1 y1) list(x2 y2)) width "extendExtend")
; All coordinates (x1, y1, x2, y2) and width MUST be formatted to 3 decimals and be multiples of 0.005 (e.g., 0.125, 1.000, 0.005)
```
Note: For CDAC array routing, always use `"extendExtend"` parameter to ensure proper wire extension at endpoints.

**Shield layer rendering:**
- When drawing the shield (default): Include all four frame segments (left vertical, right vertical, top horizontal, bottom horizontal) as specified in shape-specific structure documents
- When omitting the shield: Simply skip the frame drawing statements in the generated SKILL; all other geometry (fingers, middle bar, vias, pins) remains unchanged
- All coordinate calculations (outer_top, outer_bottom, leftFrameX, rightFrameX, via positions, pin positions) must be computed as if the shield exists, regardless of whether the shield is drawn

**Solid rectangle using dbCreateRect (ONLY for Sandwich L_top and L_bot plates):**
```skill
; ONLY allowed for Sandwich capacitor's top and bottom solid plates (L_top and L_bot)
; Top/Bottom solid plate rectangle
; Bounding box corners: lower-left (−HALF_WIDTH, OUTER_BOTTOM), upper-right (+HALF_WIDTH, OUTER_TOP)
dbCreateRect(cv list("LAYER" "drawing") list(list(-HALF_WIDTH OUTER_BOTTOM) list(HALF_WIDTH OUTER_TOP)))
```

**⚠️ IMPORTANT**: `dbCreateRect` is **ONLY** allowed for Sandwich capacitor's L_top and L_bot solid plates. For all other structures (including other Sandwich layers like L_top2, L_mid, L_bot2, and all H-shape/I-Type structures), **MUST use `dbCreatePath`** instead.

**Alternative: Solid rectangle via wide-path (for plates, if needed):**
```skill
; Render a full rectangular plate using one horizontal path centered at y=0
; width = total rectangle height; x-span = total rectangle width
; This is an alternative to dbCreateRect, but dbCreateRect is preferred for Sandwich L_top/L_bot
dbCreatePath(cv list("LAYER" "drawing") list(list(-HALF_WIDTH 0.000) list(HALF_WIDTH 0.000)) TOTAL_HEIGHT)
```

**Vias (MUST use techFindViaDefByName first):**

⚠️ **CRITICAL: Via Generation Format - MUST Follow This Pattern**

**REQUIRED THREE-STEP PROCESS (NO EXCEPTIONS):**

1. **First**: Define `viaDefId` variable using `techFindViaDefByName`
2. **Second**: Define `viaParams` variable with cutRows and cutColumns
3. **Third**: Call `dbCreateVia` using the defined variables

**Correct format:**
```skill
viaDefId = techFindViaDefByName(tech "HIGHER_LOWER")  ; e.g., "M7_M6"
viaParams = list(list("cutRows" r) list("cutColumns" c))
dbCreateVia(cv viaDefId list(x y) "R0" viaParams)
```

### dbCreateVia Usage (Signature)

- Allowed signature:
  - `dbCreateVia(cv viaDefId point "R0" viaParams)`
- Required `viaParams` content:
  - `viaParams = list(list("cutRows" r) list("cutColumns" c))` where `r` and `c` are positive integers

**⚠️ FORBIDDEN - DO NOT USE THESE FORMATS:**

❌ **WRONG - Nested function call (NOT ALLOWED):**
```skill
dbCreateVia(cv techFindViaDefByName(tech "M7_M6") list(0.0 0.0) "R0" ...)
```

❌ **WRONG - Direct numeric parameters (NOT ALLOWED):**
```skill
dbCreateVia(cv viaDefId list(0.0 0.0) "R0" 1 3 0.13 0.13)
```

❌ **WRONG - Missing viaDefId definition:**
```skill
viaParams = list(list("cutRows" 1) list("cutColumns" 3))
dbCreateVia(cv techFindViaDefByName(tech "M7_M6") list(0.0 0.0) "R0" viaParams)
```

**✅ CORRECT Examples:**
```skill
;; Example 1: Top row via
viaDefId_M7_M6 = techFindViaDefByName(tech "M7_M6")
viaParams_M7_M6_top = list(list("cutRows" 1) list("cutColumns" 3))
dbCreateVia(cv viaDefId_M7_M6 list(0.000 0.405) "R0" viaParams_M7_M6_top)

;; Example 2: Middle row via (same viaDefId, different params)
viaParams_M7_M6_mid = list(list("cutRows" 1) list("cutColumns" 3))
dbCreateVia(cv viaDefId_M7_M6 list(0.000 0.000) "R0" viaParams_M7_M6_mid)

;; Example 3: Different via type
viaDefId_M6_M5 = techFindViaDefByName(tech "M6_M5")
viaParams_M6_M5_top = list(list("cutRows" 1) list("cutColumns" 3))
dbCreateVia(cv viaDefId_M6_M5 list(0.000 0.405) "R0" viaParams_M6_M5_top)
```

**Key Points:**
- **MUST** define `viaDefId` as a separate variable before using it
- **MUST** define `viaParams` as a separate variable before using it
- **MUST** use the variable names in `dbCreateVia` call, NOT nested function calls
- **DO NOT** pass pitch values (0.13, etc.) to `dbCreateVia` - they are NOT parameters
- **DO NOT** pass numeric cutRows/cutColumns directly - they must be in `viaParams` list

**Via naming convention**: Use `higher_lower` order (e.g., `M7_M6`). If input order is reversed, correct to high_low before generating.

**Pins (use dbCreateLabel, NOT dbCreatePin):**
```skill
dbCreateLabel(cv list("LAYER" "pin") list(x y) "TOP" "centerCenter" "R0" "roman" 0.100)
dbCreateLabel(cv list("LAYER" "pin") list(x y) "BOT" "centerCenter" "R0" "roman" 0.100)
; All coordinates (x, y) and size values MUST be formatted to 3 decimals and be multiples of 0.005 (e.g., 0.125, 0.100, 0.005)
```

### Arrays (mosaic of an existing unit cell layout)
```skill
; IMPORTANT: Order note - first pitch is Y (row step), second is X (column step)
dbCreateParamSimpleMosaic(cv dbOpenCellView("LIB" "UNIT_CELL" "layout") "mosaic_RxC" list(x0 y0) "R0" rows cols pitch_y pitch_x nil)
```

**⚠️ TROUBLESHOOTING: SKILL File Too Long (JSONDecodeError)**

If you encounter `JSONDecodeError: Unterminated string starting at: line 1 column 11 (char 10)`, the generated SKILL file is too long. **Most common cause: Phase 3 not merging adjacent array positions.**

**Check Phase 3 array generation code:**
- Are you generating one `dbCreateParamSimpleMosaic` per capacitor position with `(1, 1)` dimensions? ❌ **WRONG**
- Are you merging adjacent positions into continuous rectangular regions using two-pass algorithm? ✅ **REQUIRED**
- For a 12×6 array, you should have ~5-10 mosaics, NOT 72 individual `(1, 1)` mosaics

**Fix**: Implement region merging algorithm in `render_skill()` as specified in `04_Array_Generation.md` Step 3.2.1 and Step 3.3.2.

---

## SKILL Generation Spec (Key Points)

- File head must contain: `tech = techGetTechFile(cv)`
- For each layer, draw metals (structure-specific), then insert vias between adjacent layers, and finally place TOP/BOT pins only on the top layer
- Via name uses `higher_lower` order (e.g., `M5_M4`); if input is reversed, correct to high_low before generating
- **⚠️ MANDATORY: All numeric values MUST use exactly 3 decimal places and be multiples of 0.005** (e.g., `0.125`, `-1.235`, `10.000`, `0.005`, `0.000`)
- Keep a consistent ordering and grouping as outlined in structure specifications to ease debugging.
- Placement (including via rows/cols, segmentation and alignment) is defined EXCLUSIVELY by the shape‑specific module and Technology Config; this document intentionally provides syntax only.
### ⚠️ 3-Decimal Precision and 0.005 Grid Constraint (MANDATORY)

**ALL numeric literals in generated SKILL scripts MUST have exactly 3 decimal places AND be multiples of 0.005:**

- ✅ **CORRECT**: `list(0.125 0.680)`, `1.000`, `-2.345`, `0.005`, `0.000` (all are multiples of 0.005)
- ❌ **WRONG**: `list(0.123 0.678)` (not multiples of 0.005)
- ❌ **WRONG**: `1.0` (only 1 decimal place, should be `1.000`)
- ❌ **WRONG**: `0` (should be `0.000`)
- ❌ **WRONG**: `list(0.1234 0.6789)` (4 decimals - too many, should be 3)
- ❌ **WRONG**: `list(0.12 0.67)` (2 decimals - too few, should be 3)
- ❌ **WRONG**: `0.127` (not a multiple of 0.005 - closest valid values are `0.125` or `0.130`)

**Applies to:**
- All coordinate values (x, y positions)
- All width and height values
- All spacing and dimension values
- All via positions
- All pin positions
- **Every numeric literal** in the SKILL script

**Enforcement:**
- Python `compute_geometry()` must quantize all values to 0.005 grid first: `round(value / 0.005) * 0.005`
- Python `compute_geometry()` must output all values with 3 decimals: `{value:.3f}`
- Python `render_skill()` must format all numeric values to 3 decimals when generating SKILL code
- **NO exceptions** - this is a strict requirement for SKILL script compatibility and grid alignment

### Complete generation policy

- The generated SKILL must be fully realized for the current round; avoid TODO/placeholder markers.
- Avoid deferring required geometry to later rounds. If a structure requires N elements this round, generate all N this round.
- Each iteration should emit a single SKILL file that contains all geometry and via features required by the active shape.
- For complex shapes like Sandwich: ensure all required components (frames, fingers, vias, etc.) are generated in the same script.
- Numeric formatting uses 3 decimals with 0.005 grid quantization; header contains `tech = techGetTechFile(cv)`; only whitelist commands appear.

---

## No Reliance on Edit Window (CRITICAL)

**FORBIDDEN:**
```skill
cv = geGetEditCellView()  ; ❌ WRONG - Do not use
if(cv == nil then        ; ❌ WRONG - No conditionals
    cv = dbOpenCellViewByType(...)
)
```

**CORRECT:**
```skill
;; cv is provided automatically by run_il_with_screenshot
;; Use cv directly - it's already opened and ready
;; Do NOT call dbOpenCellView for the destination view
;; Do NOT check if cv exists - it's guaranteed to exist
```

**Key Points:**
- The destination `cv` is **automatically provided** by `run_il_with_screenshot`
- Each iteration uses a new view (layout1, layout2, etc.) - **no clearing needed**
- Use `cv` directly as the first argument in all dbCreate* calls
- Only the master (source) layout should be opened explicitly via `dbOpenCellView` for mosaics

---

## Decision vs. Validation Boundary

### AI Responsibilities
- Decide initial parameters and all subsequent adjustments (fingers, layers, h_height, spacings, widths, step sizes)
- **Infer whether the outer shield (outer rectangle/frame) should be drawn from user intent** when generating layout code
  - Default behavior is to include the shield unless the user's request explicitly indicates otherwise
  - Do NOT introduce explicit parameters (e.g., `drawShield`) to control this; make the decision based on user intent
- Interpret DRC/PEX textual reports and plan next moves toward the ±1% goal
- Choose parameter update strategies based on measured results

### Python Responsibilities
- Compute derived geometry deterministically from the current parameters
- **Always compute all geometry as if the outer shield exists** (use frame widths in all coordinate calculations)
- When rendering, conditionally include or omit shield drawing statements based on AI decision (shield rendering decision)
- Validate constraints: height ≤ max_height (if specified), finger count (shape-dependent), layers within allowed set, minima/quantization rules; raise/return violations if any
- Render a fully flattened `.il` from a stable template; no control flow or logic in SKILL
- **Do NOT** choose next parameters or implement decision logic
- **Do NOT** change geometric coordinate calculations based on shield presence; only omit drawing statements

### SKILL Responsibilities
- Pure execution of hard-coded creation statements
- No loops, conditionals, or procedures
- No computation or logic - only literal geometry creation

---

## Report Interpretation Policy (Strict)

- **AI interprets DRC/PEX report text directly** and decides next actions
- **Absolutely forbid programmatic parsing** of DRC/PEX reports in SKILL or Python:
  - No regex
  - No substring search/split
  - No JSON/CSV extraction
  - No string manipulation for extracting values
- Generate and log human-readable plain-text reports only, then provide file paths
- The AI consumes these logs to plan parameter updates
- Only if explicitly requested may a machine-readable export be enabled; by default, keep SKILL and Python free of any report-parsing logic

---

## Implementation Notes

- **Report understanding and iteration planning** are performed by the AI directly based on the raw DRC/PEX reports
- Do not add separate parsing/decision modules unless explicitly requested
- Keep SKILL scripts free of parsing and complex logic
- Let Python handle computation and rendering; the AI will interpret DRC/PEX outputs directly
- Prefer regenerating from a template instead of brittle string edits
- Use anchors only for small, safe deltas
- Cache stable assets (templates) and memoize deterministic geometry to accelerate iterations

---

## Related Documents

- **01_Workflow_Framework.md**: Workflow steps that use this integration
- **03_Shape_Specifics/[SHAPE]/03_01_[SHAPE]_Structure.md**: Shape-specific geometry calculations and drawing procedures
- **Technology_Configs/**: Technology-specific constraints that affect validation
- **03_Shape_Specifics/SHAPE_SELECTION_GUIDE.md**: Guide for choosing appropriate capacitor shape


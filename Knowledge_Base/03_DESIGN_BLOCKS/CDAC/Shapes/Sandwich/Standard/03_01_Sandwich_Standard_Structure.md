# Sandwich Capacitor Structure — Geometry specification and drawing procedures (all technologies)

## Overview

The Sandwich Capacitor (SC) is a five-layer structure with the following layer stack (top to bottom):
1. **L_top**: Solid rectangular plate
2. **L_top2**: I-Type capacitor structure with shield (outer metal frame + alternating finger heights)
3. **L_mid**: Quadrant-interdigitated core (**NO metal frame** - only central cross + fingers + straps; shielding achieved by via belts on adjacent layers)
4. **L_bot2**: I-Type capacitor structure with shield (outer metal frame + alternating finger heights)
5. **L_bot**: Solid rectangular plate

**CRITICAL**: L_mid has **NO outer metal frame**. The "shield" function is achieved through via belts on L_top2↔L_mid and L_mid↔L_bot2 connections.

The BOT network is formed by the top plate (L_top), bottom plate (L_bot), the I-Type layers' BOT networks (L_top2, L_bot2), and the middle-layer BOT fingers. The TOP network includes the I-Type layers' TOP networks and the middle-layer TOP fingers only.

Applicability: all technology nodes. Adjacent metal pairing is required for via definitions. Combine with the Technology Configs for process-specific limits.

---

## Physical Structure

### Main Components
- **L_top, L_bot**: Solid rectangular plates
- **L_top2, L_bot2**: I-Type capacitor structures with shield (outer metal frame + alternating finger heights + horizontal strips)
- **L_mid**: Quadrant-interdigitated core with central cross, fingers, and straps (**NO metal frame** - shielding achieved by via belts)

### Physical Regions

**Solid plates (L_top, L_bot)**: Full rectangles; typically co-extensive with the outer frame footprint (optionally with a margin defined in tech configs)

**I-Type layers (L_top2, L_bot2)**: I-Type capacitor structure with shield
- Outer rectangular shield (frame) with four segments: left vertical, right vertical, top horizontal, bottom horizontal (BOT net)
- Top and bottom horizontal strips inside the frame (BOT net for bottom strip, TOP net for top strip connection)
- Vertical fingers with alternating heights: odd-index fingers extend from bottom to upper region, even-index fingers extend from lower region to top (interdigitated pattern)
- Connection line from bottom strip to bottom frame (at structure center, x = 0) for BOT net connectivity

**Middle layer (L_mid)**:
- **NO outer metal frame** - shielding achieved by via belts on adjacent layers
- Interdigitated core composed of alternating TOP/BOT fingers arranged in four quadrants around a central cross (vertical and horizontal bars)
- Internal straps: top strap (continuous), bottom straps (left and right segments split by vertical cross)

### ⚠️ MANDATORY: Complete Implementation in Every Round

**🚫 ABSOLUTE PROHIBITION - NO EXCEPTIONS - NO STAGED IMPLEMENTATION 🚫**

**⚠️ CRITICAL CLARIFICATION**: "Round" refers to parameter iteration (trying different parameter values to meet capacitance targets), NOT to incremental feature implementation. **EVERY round (Round 1, Round 2, etc.) MUST generate a COMPLETE, production-ready SKILL script with ALL geometry AND ALL via arrays.**

**NO STAGED IMPLEMENTATION ALLOWED**: All elements (5 layers + ALL via arrays) MUST be generated in a SINGLE SKILL script in EVERY round. Round 1 is NOT a "simplified" or "partial" implementation - it must be complete and functional. The following approaches are **STRICTLY FORBIDDEN** and will result in **IMMEDIATE REJECTION**:

- ❌ Generating "placeholder" or "TODO" via arrays with plans to add them later
- ❌ Implementing "basic" or "simplified" via placement first, then refining
- ❌ Creating a "minimal", "testing", or "preliminary" version before the full version
- ❌ Splitting implementation across multiple rounds/scripts
- ❌ **Generating geometry first, then generating via arrays in a separate function call or separate SKILL generation step**
- ❌ **Returning SKILL code with only geometry shapes, planning to add via arrays later**
- ❌ **ANY** comments containing forbidden language:
  - "TODO", "to be implemented", "placeholder", "initial implementation", "would be implemented"
  - "should be added", "will be generated later", "Additional via connections...", "For production..."
  - "simplified version", "basic version", "testing version", "In a full implementation..."
  - "SIMPLIFIED FOR INITIAL TESTING", "will be completed in subsequent rounds"
  - **"Additional via arrays for other layer pairs would be generated here"** ← **ABSOLUTELY FORBIDDEN**
  - **"Continue with remaining via arrays..."** ← **ABSOLUTELY FORBIDDEN**
  - **"would be generated here"**, **"will be generated here"**, **"should be generated"** ← **ABSOLUTELY FORBIDDEN**
  - **IF the comment suggests something is missing or incomplete, it is FORBIDDEN**
- ❌ **Generating only SOME via arrays (e.g., only L_top↔L_top2) and using comments to indicate others "would be generated"**
- ❌ **Generating via arrays for only 1 or 2 layer pairs out of the required 4 layer pairs**

**✅ ALLOWED APPROACH - Two-Step Generation Within Single Function Call:**

The `render_sandwich_skill` function **MAY** internally organize generation into two logical steps:
1. **Step 1**: Generate all geometry shapes (5 layers: L_top, L_top2, L_mid, L_bot2, L_bot)
2. **Step 2**: Generate all via arrays (all 4 adjacent layer pairs, ≥29 via arrays)

**CRITICAL REQUIREMENTS:**
- ✅ Both steps MUST be completed within the **SAME function call** to `render_sandwich_skill`
- ✅ The returned SKILL script MUST contain **BOTH** complete geometry AND complete via arrays
- ✅ The function MUST NOT return until both steps are complete
- ✅ The generated SKILL code MUST be complete and ready for execution (no missing via arrays)
- ❌ **FORBIDDEN**: Returning SKILL code with only geometry, then calling another function to add via arrays
- ❌ **FORBIDDEN**: Splitting into `render_geometry_skill()` and `render_via_skill()` functions that are called separately

**⚠️ CRITICAL SELF-CHECK BEFORE GENERATING CODE:**
- ❌ **WRONG THOUGHT**: "Let me generate a simplified version first for testing, then add all vias later"
- ❌ **WRONG THOUGHT**: "I'll generate geometry first, then add via arrays in the next step"
- ❌ **WRONG THOUGHT**: "I'll generate via arrays for L_top↔L_top2 first, then add comments for the other 3 layer pairs"
- ✅ **CORRECT THOUGHT**: "I must generate ALL ≥29 via arrays for ALL 4 layer pairs in this one complete script right now, even if I organize it as two steps within the same function"
- ❌ **WRONG APPROACH**: Only generate 5 vias for one layer pair (L_top↔L_top2), add comment "Additional via arrays for other layer pairs would be generated here"
- ❌ **WRONG APPROACH**: Generate via arrays for only 1 or 2 layer pairs, then use comments to indicate others
- ✅ **CORRECT APPROACH**: Generate ALL via arrays for ALL 4 layer pairs (L_top↔L_top2, L_top2↔L_mid, L_mid↔L_bot2, L_bot2↔L_bot) with complete specifications NOW, within the same function call
- ✅ **MANDATORY CHECKLIST**: Before returning, verify that the SKILL code contains `dbCreateVia` statements for:
  1. ✅ L_top ↔ L_top2 (I-Type frame vias + bottom strip vias)
  2. ✅ L_top2 ↔ L_mid (shield via belts + top strap vias)
  3. ✅ L_mid ↔ L_bot2 (shield via belts + top strap + bottom strap vias)
  4. ✅ L_bot2 ↔ L_bot (I-Type frame vias + bottom strip vias)

**REQUIRED APPROACH**: Complete, production-ready implementation with ALL via arrays computed and generated in EVERY round (Round 1, Round 2, etc.). Each round iterates on PARAMETER VALUES (finger counts, widths, dimensions), NOT on feature completeness. The function may internally organize work into geometry-first, via-second steps, but BOTH must be complete before the function returns.

**ABSOLUTE REJECTION CRITERIA:**
- Via count < 20 arrays → **IMMEDIATE REJECTION, must regenerate**
- Via arrays generated for fewer than 4 layer pairs → **IMMEDIATE REJECTION, must regenerate**
- Only generating via arrays for L_top↔L_top2 (or any single layer pair) → **IMMEDIATE REJECTION, must regenerate**
- Any forbidden language in comments (including "would be generated", "Continue with remaining", etc.) → **IMMEDIATE REJECTION, must regenerate**
- Any indication of staged/incremental implementation → **IMMEDIATE REJECTION, must regenerate**
- SKILL code missing `dbCreateVia` statements for any of the 4 required layer pairs → **IMMEDIATE REJECTION, must regenerate**
- Function returns SKILL code with only geometry shapes → **IMMEDIATE REJECTION, must regenerate**
- Comments indicating via arrays "would be generated" or "will be generated" instead of actual generation → **IMMEDIATE REJECTION, must regenerate**

---

### ⚠️ Critical: Via arrays determine whether the layout works

- Every inter-layer connection must be realized by **complete via arrays**; missing any required array renders the device unusable.
- Any 1×1 “placeholder” via, or omission of shield belts, straps, or frame strips, will immediately trigger 50+ DRC violations and invalidate PEX.
- **🚨🚨🚨 MANDATORY: VIA CALCULATION MUST FOLLOW KNOWLEDGE BASE STEPS EXACTLY 🚨🚨🚨**
  - **⚠️ CRITICAL**: Python code MUST follow the step-by-step procedure defined in the knowledge base for via calculations.
  - **⚠️ CRITICAL**: You MUST execute each step in the EXACT order: Step 0 → Step 1 → Step 2 → Step 3a → Step 3 → Step 4.
  - **⚠️ CRITICAL**: Do NOT skip steps, do NOT combine steps, do NOT use shortcuts or intuitive calculations.
  - **⚠️ CRITICAL**: Each step produces intermediate values that are REQUIRED by subsequent steps. Skipping steps will cause incorrect results.
  - **⚠️ CRITICAL**: Before calculating any via center, verify that you have completed all prerequisite steps and have all required intermediate values (segment lengths, grid extremes, anchors).
  - **⚠️ CRITICAL**: If you find yourself calculating via centers directly without first computing the required intermediate values, you are doing it WRONG. STOP and restart from Step 0.
- Python must compute valid `cutRows`/`cutColumns` and via centers before rendering SKILL; verify all required `dbCreateVia` statements before execution.
- If geometry produces `cutRows` or `cutColumns` < 1, adjust the geometry first and regenerate; temporary via omissions are forbidden.

---

## Layering and Nets

**Layers** (ordered top → bottom): `L_top`, `L_top2`, `L_mid`, `L_bot2`, `L_bot`

**Layer Order Guidance**:
- **Design principle**: Layers should be specified in **descending order** from top to bottom to ensure proper via definitions and layer stack connectivity
- **Typical examples**:
  - `M7 → M6 → M5 → M4 → M3` (numeric layers, descending)
  - `METAL7 → METAL6 → METAL5 → METAL4 → METAL3` (named layers, descending)
  - `M5 → M4 → M3 → M2 → M1` (descending order)
- **Preferred stack (low-parasitic mode)**: Whenever the technology offers ≥5 metals, **strongly prefer the highest five adjacent layers** (e.g., `M7 → M6 → M5 → M4 → M3`). Avoid using M1/M2 for capacitor plates because they couple heavily to the substrate and routing layers
- **Layer naming convention**: For numeric layer names (e.g., `M7`, `METAL5`), extract the numeric part and ensure the sequence decreases from top to bottom. For non-numeric layer names, follow the technology file's layer ordering convention
- **Note**: The actual layer order and via compatibility depend on the technology file specifications. Users should verify layer stack compatibility with their process technology before generating layouts
- Nets:
  - `BOT = { L_top solid plate ∪ L_top2 BOT network (shield frame + BOT fingers) ∪ L_mid BOT_fingers ∪ L_bot2 BOT network (shield frame + BOT fingers) ∪ L_bot solid plate }`
  - `TOP = { L_top2 TOP network (TOP fingers) ∪ L_mid TOP_fingers ∪ L_bot2 TOP network (TOP fingers) }`
  - **Note**: L_mid has NO metal frame; only fingers, central cross, and straps
- Isolation rules:
  - Middle TOP fingers must not touch any BOT conductor (BOT fingers, straps, plates, I-Type layers' BOT networks)
  - I-Type layers' TOP fingers must not touch any BOT conductor
  - Spacings satisfy technology minima and any width/quantization requirements

---

## Key Geometric Quantities

All geometric quantities must be computed by the AI before generating SKILL and solidified as numbers (5 decimals).

### Coordinate System
- **Global coordinate system**: Origin at device center, +x to the right, +y up
- Place `TOP` pin at `(0,0)` on `layer_mid`; place `BOT` pin at `(0,0)` on `layer_bot`

### Total Dimensions

**Overall dimensions** (shared by all layers, determined by middle layer):
- `total_height = h_height + 2*(spacing + strap_width + frame_to_core_d) + 2*frame_width`
- `outer_top = +total_height/2`, `outer_bottom = −total_height/2`
- `half_height = total_height/2`

### Middle Layer (L_mid) Geometry

**Vertical stack**:
- `top_minus_frame = outer_top − frame_width`
- `bottom_minus_frame = outer_bottom + frame_width`
- `top_strap_y = top_minus_frame − frame_to_core_d − strap_width/2`
- `bot_strap_y = bottom_minus_frame + frame_to_core_d + strap_width/2`
- `core_top_y = top_strap_y − strap_width/2 − spacing`
- `core_bottom_y = bot_strap_y + strap_width/2 + spacing`
- `upper_y = h_middle_y + spacing + middle_horizontal_width/2` (where `h_middle_y = 0`)
- `lower_y = h_middle_y − spacing − middle_horizontal_width/2`

**I-Type middle finger span calculation** (needed for alignment):
- Compute I-Type middle finger span: `i_type_middle_span_with_clearance = (i_type_fingers_middle − 1) * i_type_pitch + i_type_finger_vertical_width + 2 * i_type_finger_d`
- Compute `finger_to_cross_d` to align middle layer core: `finger_to_cross_d = (i_type_middle_span_with_clearance − middle_vertical_width) / 2`
- `i_type_pitch = i_type_finger_vertical_width + i_type_finger_d` (consistent spacing for all I-Type fingers)

**Horizontal width from columns**:
- `finger_keepout_center_dx = middle_vertical_width/2 + finger_to_cross_d + finger_vertical_width/2`
- `pitch = finger_vertical_width + finger_d`
- `cols_per_side = fingers`
- Required half‑width: `half_width = finger_keepout_center_dx + max(0, cols_per_side−1)*pitch + frame_width + frame_to_core_d + finger_vertical_width/2`
- `total_width = 2*half_width`
- `left_frame_x = −half_width + frame_width/2`, `right_frame_x = +half_width − frame_width/2`

**Finger centers** (⚠️ CRITICAL - TWO SEPARATE QUADRANTS):
- **CRITICAL**: Middle layer fingers are distributed in **TWO SEPARATE quadrants**, NOT continuously!
- **Algorithm** (CORRECT method):
  1. First compute I-Type finger centers (all fingers, see I-Type section below)
  2. Extract left quadrant centers: `left_centers = i_type_centers[0:fingers]` (first `fingers` positions)
  3. Extract right quadrant centers: `right_centers = i_type_centers[-fingers:]` (last `fingers` positions)
  4. Combine: `finger_centers = left_centers + right_centers`
- **Constraint validation**: Verify that `|finger_centers[i]| ≥ middle_vertical_width/2 + finger_to_cross_d + finger_vertical_width/2` for all i

**Strap spans per side**:
- `left_outer_edge = min(finger_centers) − finger_vertical_width/2`
- `left_inner_edge = finger_centers[fingers-1] + finger_vertical_width/2`
- `right_inner_edge = finger_centers[fingers] − finger_vertical_width/2`
- `right_outer_edge = max(finger_centers) + finger_vertical_width/2`

**Cross bars**:
- `vbar_top_y = top_minus_frame − frame_to_core_d`
- `vbar_bottom_y = bottom_minus_frame + frame_to_core_d`
- `hbar_left_x = (left_frame_x + frame_width/2) + frame_to_core_d`
- `hbar_right_x = (right_frame_x − frame_width/2) − frame_to_core_d`

### I-Type Layers (L_top2, L_bot2) Geometry

**Frame boundaries**:
- `i_type_leftFrameX = −half_width + i_type_frame_vertical_width/2`
- `i_type_rightFrameX = +half_width − i_type_frame_vertical_width/2`
- `i_type_frame_inner_top = outer_top − i_type_frame_horizontal_width`
- `i_type_frame_inner_bottom = outer_bottom + i_type_frame_horizontal_width`
- `i_type_frame_x_left = i_type_leftFrameX − i_type_frame_vertical_width/2`
- `i_type_frame_x_right = i_type_rightFrameX + i_type_frame_vertical_width/2`

**Strip positions** (aligned with middle layer straps):
- `i_type_strip_top_y = top_strap_y`
- `i_type_strip_bottom_y = bot_strap_y`
- `i_type_strip_width = strap_width`

**Finger region bounds**:
- `i_type_h_top_y = i_type_strip_top_y − i_type_strip_width/2 − i_type_spacing`
- `i_type_h_bottom_y = i_type_strip_bottom_y + i_type_strip_width/2 + i_type_spacing`

**Frame center positions**:
- `i_type_top_frame_y = outer_top − i_type_frame_horizontal_width/2`
- `i_type_bottom_frame_y = outer_bottom + i_type_frame_horizontal_width/2`

**Finger center x positions** (centered symmetrically):
- **CRITICAL**: All I-Type fingers must maintain consistent spacing `i_type_pitch = i_type_finger_vertical_width + i_type_finger_d`
- Total fingers: `total_i_type_fingers = 2 * i_type_fingers_per_side + i_type_fingers_middle`
- Total span: `total_span = (total_i_type_fingers - 1) * i_type_pitch`
- Start position: `x_start = -total_span / 2`
- Generate centers: `i_type_finger_centers[i] = x_start + i * i_type_pitch` for i = 0 to (total_i_type_fingers - 1)

**Strip x coordinates**:
- `i_type_strip_x_left = i_type_finger_centers[0] − i_type_finger_vertical_width/2`
- `i_type_strip_x_right = i_type_finger_centers[-1] + i_type_finger_vertical_width/2`

**Finger endpoints**:
- `i_type_top_minus_frame = i_type_strip_top_y − i_type_strip_width/2`
- `i_type_bottom_minus_frame = i_type_strip_bottom_y + i_type_strip_width/2`

**Connection line coordinates**:
- `i_type_bottom_strip_bottom_edge = i_type_strip_bottom_y − i_type_strip_width/2`
- `i_type_bottom_frame_top_edge = i_type_bottom_frame_y + i_type_frame_horizontal_width/2`

### Shield Via Belt Geometry (for 8-segment belts)

**Cross openings around bars**:
- `h_opening_x1 = −(middle_vertical_width/2 + frame_to_core_d)`
- `h_opening_x2 = +(middle_vertical_width/2 + frame_to_core_d)`
- `v_opening_y1 = −(middle_horizontal_width/2 + frame_to_core_d)`
- `v_opening_y2 = +(middle_horizontal_width/2 + frame_to_core_d)`

**Frame-band midlines for horizontal belt centers**:
- `y_top_mid = (outer_top + i_type_frame_inner_top)/2`
- `y_bot_mid = (outer_bottom + i_type_frame_inner_bottom)/2`

**Vertical belt column count**:
- `cols_v = floor((i_type_frame_vertical_width + via_margin)/via_pitch_cut)`

**Vertical grid extremes for aligning horizontal belt columns**:
- `left_vert_leftmost_x = i_type_leftFrameX − (cols_v−1)*0.5*via_pitch_cut`
- `right_vert_rightmost_x = i_type_rightFrameX + (cols_v−1)*0.5*via_pitch_cut`

**Vertical y-anchors** (edge-anchored centers for vertical belts):
- `y_anchor_top = outer_top − (via_pitch_cut − via_margin)/2`
- `y_anchor_bot = outer_bottom + (via_pitch_cut − via_margin)/2`

---

## Cross-layer Connections (Vias)

- Default rule: vias may land only on BOT-network conductors or explicitly designated straps; vias on TOP fingers are strictly forbidden.
- Required exceptions under this specification: the L_mid top strap and the L_top2/L_bot2 bottom strips are mandatory via targets and must follow the rules below.
- Adjacent layer pairs (all must use adjacent metals only):
  - `L_top ↔ L_top2`: Connect solid plate to I-Type layer's BOT network (shield frame and BOT fingers)
  - `L_top2 ↔ L_mid`: Connect I-Type layer's BOT network to middle-layer straps and BOT fingers (via shield via belts around perimeter)
  - `L_mid ↔ L_bot2`: Connect middle-layer BOT fingers and straps to I-Type layer's BOT network (via shield via belts around perimeter)
  - `L_bot2 ↔ L_bot`: Connect I-Type layer's BOT network to solid plate

### ⚠️⚠️⚠️ CRITICAL: VIA GRID ALIGNMENT REQUIREMENT (MOST COMMON ERROR) ⚠️⚠️⚠️

**🚫 ABSOLUTELY FORBIDDEN — REJECT IMMEDIATELY IF FOUND:**
- **❌ FORBIDDEN**: Using midpoint centering for via array centers:
  - `cx = (x_start + x_end)/2` or `cx = (-half_width + len/2)` or `cx = (h_opening_x2 + len/2)`
  - `cy = (y_start + y_end)/2` or `cy = (v_opening_y2 + len/2)` or `cy = (y_anchor_bot + len/2)` or `cy = 0`
- **❌ FORBIDDEN**: Using `half_width` for horizontal segment length calculations instead of `i_type_frame_x_left/right`

**✅ REQUIRED — MUST USE THESE FORMULAS:**
- **Horizontal belt centers**: 
  - Left segments: `cx = left_vert_leftmost_x + (cols−1)*0.5*via_pitch_cut`
  - Right segments: `cx = right_vert_rightmost_x − (cols−1)*0.5*via_pitch_cut`
- **Vertical belt centers**:
  - Top segments: `cy = y_anchor_top − (rows−1)*0.5*via_pitch_cut`
  - Bottom segments: `cy = y_anchor_bot + (rows−1)*0.5*via_pitch_cut`
- **Horizontal segment lengths**:
  - `len = h_opening_x1 − i_type_frame_x_left` (left segments)
  - `len = i_type_frame_x_right − h_opening_x2` (right segments)

**🚨🚨🚨 CRITICAL: VIA COUNT CALCULATION MUST BE CORRECT 🚨🚨🚨**
- **⚠️ CRITICAL**: Via counts (`cutRows` and `cutColumns`) MUST be calculated using the EXACT formula: `count = max(1, floor((dimension + via_margin) / via_pitch_cut))`
- **⚠️ CRITICAL**: You MUST use the actual dimensions from geometry calculations (segment lengths, frame widths, etc.), NOT `half_width` or other incorrect values.
- **⚠️ CRITICAL**: You MUST use `via_margin` and `via_pitch_cut` from the technology parameters, NOT hardcoded values.
- **❌ FORBIDDEN**: Hardcoding `cutRows=1` and `cutColumns=1` for all via arrays
- **❌ FORBIDDEN**: Using approximate values like `cutRows ≈ 5` or `cutColumns ≈ 2`
- **❌ FORBIDDEN**: Using `half_width` or other incorrect dimensions in count calculations
- **⚠️ CRITICAL**: Verify that all counts are >= 1 before using them in `dbCreateVia` statements. If any count is 0 or negative, check your dimension calculations.

### ⚠️ Critical Implementation Requirements

#### Finger Alignment Constraint (MUST ENFORCE)
- **`i_type_fingers_per_side` MUST EQUAL `fingers`** (middle layer fingers per side)
- **Rationale**: This ensures vertical alignment between I-Type side fingers and middle layer quadrant fingers
- **Example**: If `fingers=3`, then `i_type_fingers_per_side=3` (NOT 4, NOT 5)
- **Total I-Type fingers**: `2*fingers + i_type_fingers_middle` (e.g., 2×3 + 4 = 10)

#### Finger Symmetric Distribution (MUST ENFORCE)
- **ALL finger centers (both I-Type and middle layer) MUST be symmetrically distributed around x=0**
- **Algorithm**:
  ```
  total_fingers = (for I-Type: 2*i_type_fingers_per_side + i_type_fingers_middle)
                  (for middle: 2*fingers)
  total_span = (total_fingers - 1) * pitch
  x_start = -total_span / 2
  for i in range(total_fingers):
      x_center[i] = x_start + i * pitch
  ```

### Via Array Placement Requirements

**L_top ↔ L_top2** (e.g., M7 ↔ M6): **5 arrays total**
- **I-Type shield frame vias**: 4 segments ⚠️ CRITICAL POSITIONING:
  - **Left vertical frame**: Position `(i_type_leftFrameX, 0.0)` ← **y=0 (CENTER), NOT boundary!**
    - Size: `cutRows` ≈ (inner_top - inner_bottom)/via_pitch (e.g., 28), `cutColumns` ≈ frame_width/via_pitch (e.g., 1)
    - **CRITICAL**: Use inner frame height, NOT total_height
  - **Right vertical frame**: Position `(i_type_rightFrameX, 0.0)` ← **y=0 (CENTER), NOT boundary!**
    - Size: Same as left vertical frame
  - **Top horizontal frame**: Position `(0.0, i_type_top_frame_y)` ← at top boundary
    - Size: `cutRows` ≈ frame_height/via_pitch (e.g., 1), `cutColumns` ≈ total_width/via_pitch (e.g., 9)
  - **Bottom horizontal frame**: Position `(0.0, i_type_bottom_frame_y)` ← at bottom boundary
    - Size: Same as top horizontal frame
- ⚠️ **I-Type bottom strip via**: 1 array — REQUIRED, commonly missed
  - Position: `(strip_center_x, i_type_strip_bottom_y)`
  - Size: Fill entire strip width and length

**L_top2 ↔ L_mid** (e.g., M6 ↔ M5): **9 arrays total**
- ⚠️ **Shield via belts**: 8 segments around cross openings — MOST CRITICAL
  - (See detailed 8-segment specification below in Shield Via Belts section)
- **Top strap via**: 1 array ⚠️ MUST FILL ENTIRE STRAP:
  - Position: `(0.0, top_strap_y)`
  - Size: `cutRows` = strap_width/via_pitch, `cutColumns` = **(right_outer_edge - left_outer_edge)**/via_pitch
  - **Common error**: Using partial length instead of full outer-to-outer span

**L_mid ↔ L_bot2** (e.g., M5 ↔ M4): **11 arrays total**
- ⚠️ **Shield via belts**: 8 segments around cross openings — MOST CRITICAL
  - (See detailed 8-segment specification below in Shield Via Belts section)
- **Top strap via**: 1 array ⚠️ MUST FILL ENTIRE STRAP:
  - Position: `(0.0, top_strap_y)`
  - Size: `cutRows` = strap_width/via_pitch, `cutColumns` = **(right_outer_edge - left_outer_edge)**/via_pitch
- **Bottom strap vias**: 2 arrays (left and right segments split by vertical cross bar)
  - Left segment: Position `((left_outer_edge + cross_left_edge)/2, bot_strap_y)`
  - Right segment: Position `((cross_right_edge + right_outer_edge)/2, bot_strap_y)`
  - Each segment sized independently

**L_bot2 ↔ L_bot** (e.g., M4 ↔ M3): **5 arrays total**
- **I-Type shield frame vias**: 4 segments ⚠️ SAME CRITICAL POSITIONING AS L_top ↔ L_top2:
  - **Left/Right vertical frames**: Position `(±i_type_leftFrameX, 0.0)` ← **y=0 (CENTER)!**
  - **Top/Bottom horizontal frames**: Position `(0.0, ±i_type_top/bottom_frame_y)` ← at boundaries
- ⚠️ **I-Type bottom strip via**: 1 array — REQUIRED, commonly missed

**Total arrays**: **30 typical** (5+9+11+5) across all 4 layer pairs. Any implementation with <20 arrays is incomplete and MUST be rejected.

### Via Array Generation — ABSOLUTELY MANDATORY

**⚠️ CRITICAL REQUIREMENT**: Via arrays are **MANDATORY** and **MUST NOT BE OMITTED**. A Sandwich capacitor layout without via arrays is **INVALID** and **NON-FUNCTIONAL**.

**Consequences of missing vias**:
- All 5 layers remain electrically disconnected (no inter-layer connections)
- DRC violations will occur (typically 50+ violations: M2.S.2, M2.S.7, M3.S.7, M4.S.2, M4.S.7, M2.S.8, M3.S.8, M4.S.8)
- PEX extraction will fail or produce meaningless results
- Capacitor cannot function (no electrical connectivity between layers)
- The design is **completely unusable** without via arrays

**STRICT IMPLEMENTATION REQUIREMENTS** (follow this EXACT sequence):

**1. L_top ↔ L_top2 connection** (MUST implement):
- Via arrays on I-Type outer frame (4 segments): left vertical, right vertical, top horizontal, bottom horizontal
- ⚠️ **Via arrays on I-Type bottom strip** (fill the entire strip area)
- Via sizing: Compute `cutRows` and `cutColumns` from frame width/strip width and segment length using `via_pitch_cut` and `via_margin`
- **NO placeholders allowed** - compute and generate all arrays immediately

**2. L_top2 ↔ L_mid connection** (MUST implement):
- ⚠️ **Shield via belts (8 segments)**: top-left, top-right, bottom-left, bottom-right (horizontal), left-top, left-bottom, right-top, right-bottom (vertical)
  - **CRITICAL**: Use `viaDefId_{layer_top2}_{layer_mid}` (e.g., `viaDefId_M6_M5`)
  - **CRITICAL**: Each segment computed independently - **NEVER** hardcode to 1×2 or any fixed value
  - Horizontal segments: `cutRows = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))`, `cutColumns = max(1, floor((segment_x_length + via_margin) / via_pitch_cut))`
  - Vertical segments: `cutRows = max(1, floor((segment_y_length + via_margin) / via_pitch_cut))`, `cutColumns = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))`
- Via arrays on top strap
- Via arrays on bottom straps (left and right segments)
- **NO single full-span arrays** - must segment around cross openings
- **NO "simplified implementation" comments** - generate complete implementation immediately

**3. L_mid ↔ L_bot2 connection** (MUST implement):
- ⚠️ **Shield via belts (8 segments)**: Same segmentation pattern as L_top2↔L_mid, but **DIFFERENT via definition**
  - **CRITICAL**: Use `viaDefId_{layer_mid}_{layer_bot2}` (e.g., `viaDefId_M5_M4`) - **DO NOT reuse L_top2↔L_mid via params**
  - **CRITICAL**: Create NEW viaParams variables for THIS layer pair (e.g., `viaParams_M5_M4_belt_*`)
  - **CRITICAL**: Each segment computed independently - **NEVER** hardcode to 1×2 or any fixed value
  - Horizontal segments: `cutRows = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))`, `cutColumns = max(1, floor((segment_x_length + via_margin) / via_pitch_cut))`
  - Vertical segments: `cutRows = max(1, floor((segment_y_length + via_margin) / via_pitch_cut))`, `cutColumns = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))`
- Via arrays on top strap
- Via arrays on bottom straps (left and right segments)
- **NO single full-span arrays** - must segment around cross openings
- **NO reusing via params from step 2** - this is a different layer pair requiring different via definitions

**4. L_bot2 ↔ L_bot connection** (MUST implement):
- Via arrays on I-Type outer frame (4 segments): left vertical, right vertical, top horizontal, bottom horizontal
- ⚠️ **Via arrays on I-Type bottom strip** (fill the entire strip area)
- Via sizing: Compute `cutRows` and `cutColumns` from frame width/strip width and segment length using `via_pitch_cut` and `via_margin`
- **NO placeholders allowed** - compute and generate all arrays immediately

**Implementation rules**:
- Via naming: `HIGHER_LOWER` (e.g., `M7_M6`, `M6_M5`), adjacent layers only; ensure the viaDef exists in the tech file
- Via array syntax: Use `techFindViaDefByName(tech "HIGHER_LOWER")` to get via definitions, then `dbCreateVia(cv viaDefId list(x y) "R0" viaParams)` where `viaParams = list(list("cutRows" r) list("cutColumns" c))`
- All via arrays must be computed and flattened in Python (no loops in SKILL output)
- No vias on TOP fingers (in any layer)
- **Validation**: Before returning the SKILL script, verify that it contains `dbCreateVia` statements. If absent, the script is **INVALID** and must be rejected and regenerated.

### Shield Via Belts — 8-Segment Specification

**Critical requirement**: The middle layer frame MUST be implemented as 8 segmented via belts, NOT a single continuous frame or simplified variant.

**Why segmentation is required**: The middle layer has cross openings (vertical and horizontal bars). A single full-span via array would violate the cross openings and cause DRC errors.

**Segment breakdown** (8 DIFFERENT spatial positions):
- **4 horizontal segments** (around vertical bar opening):
  - **top-left**: at `y = y_top_mid`, left of vertical bar (`x < 0`)
  - **top-right**: at `y = y_top_mid`, right of vertical bar (`x > 0`)
  - **bottom-left**: at `y = y_bot_mid`, left of vertical bar (`x < 0`)
  - **bottom-right**: at `y = y_bot_mid`, right of vertical bar (`x > 0`)
- **4 vertical segments** (around horizontal bar opening):
  - **left-top**: at `x = i_type_leftFrameX`, above horizontal bar (`y > 0`)
  - **left-bottom**: at `x = i_type_leftFrameX`, below horizontal bar (`y < 0`)
  - **right-top**: at `x = i_type_rightFrameX`, above horizontal bar (`y > 0`)
  - **right-bottom**: at `x = i_type_rightFrameX`, below horizontal bar (`y < 0`)

**Stacking requirement**: Each segment requires TWO via array stacks:
- Stack 1: layer_top2↔layer_mid
- Stack 2: layer_mid↔layer_bot2
- Total: 8 segments × 2 stacks = 16 via arrays for shield belts alone

**Detailed geometry and sizing** (see "Shield via belts — enforcement and anti-patterns" section below for complete formulas):
- Segment lengths computed using cross openings: `h_opening_x1`, `h_opening_x2`, `v_opening_y1`, `v_opening_y2`
- Via sizing: `cutRows` and `cutColumns` computed from segment length/width using `via_pitch_cut` and `via_margin`
- Centers aligned between horizontal and vertical belts for corner connectivity
- Never use a single full-span array; never hardcode via sizing to 1×1

**⚠️ COMMON ERROR - DO NOT DO THIS**:
- ❌ **Placing multiple via arrays at the same corner position** with different orientations (e.g., 1×2 and 2×1 at same point)
- ❌ **Using frame corner coordinates** `(±frame_x, ±frame_y)` directly as via centers without proper segment calculation
- ❌ **Example of WRONG approach**:
  ```skill
  dbCreateVia(cv viaDefId list(-0.58 0.515) "R0" list(list("cutRows" 1) list("cutColumns" 2)))  ; horizontal at corner
  dbCreateVia(cv viaDefId list(-0.58 0.515) "R0" list(list("cutRows" 2) list("cutColumns" 1)))  ; vertical at SAME corner ← WRONG!
  ```
  This creates **position overlap**, not 8 different segments!
  
- ✅ **CORRECT approach**: 
  - Each of the 8 segments has its **OWN unique center position**
  - Horizontal segments use `y = y_top_mid` or `y_bot_mid` (NOT frame corner y-coordinate)
  - Vertical segments use calculated `cy` with anchor alignment (NOT frame corner y-coordinate)
  - x-coordinates calculated using segment length and alignment formulas (Lines 818-829)

**Example: Expected Coordinates** (for typical parameters):
```
Assume: i_type_leftFrameX = -0.58, i_type_rightFrameX = 0.58
        y_top_mid = 0.48, y_bot_mid = -0.48
        y_anchor_top = 0.46, y_anchor_bot = -0.46

Then the 8 segment centers would be approximately:
  Horizontal segments:
    top-left:     cx ≈ -0.52, cy = 0.48  (y = y_top_mid)
    top-right:    cx ≈ +0.52, cy = 0.48  (y = y_top_mid)
    bottom-left:  cx ≈ -0.52, cy = -0.48 (y = y_bot_mid)
    bottom-right: cx ≈ +0.52, cy = -0.48 (y = y_bot_mid)
  
  Vertical segments:
    left-top:     cx = -0.58, cy ≈ 0.40  (above horizontal bar)
    left-bottom:  cx = -0.58, cy ≈ -0.40 (below horizontal bar)
    right-top:    cx = +0.58, cy ≈ 0.40  (above horizontal bar)
    right-bottom: cx = +0.58, cy ≈ -0.40 (below horizontal bar)

Note: These are 8 DIFFERENT positions! Not 4 corner positions with 2 vias each!
```

### I-Type Bottom Strip Vias — Implementation Details

**Critical requirement**: In addition to I-Type frame vias (4 segments), MUST place via arrays on bottom strip areas.

**For L_top ↔ L_top2 connection**:
- Via array center: spans the bottom strip at `y = i_type_strip_bottom_y`
- Via sizing: `cutRows` from strip width, `cutColumns` from strip length (using `via_pitch_cut` and `via_margin`)
- Purpose: Connect top plate to I-Type BOT network through bottom strip

**For L_bot2 ↔ L_bot connection**:
- Same specification as above
- Purpose: Connect I-Type BOT network to bottom plate

**Common error**: Only generating frame vias (4 segments) and forgetting strip vias. This leaves the I-Type layer partially disconnected.

---

## Pins

- `TOP` pin: on the L_mid TOP finger region (typically at or near the center `(0,0)`)
- `BOT` pin: on L_top and/or L_bot solid plate (typically at `(0,0)`); optionally one probe label on the L_mid BOT finger region for convenience

---

## Procedural Drawing Checklist (flattened SKILL)

1) L_top (solid plate)
- Create a solid rectangle equal to `total_width × total_height` using `dbCreateRect` with bounding box `((-half_width, outer_bottom), (half_width, outer_top))` on `layer_top`.

2) L_top2 (I-Type with shield)
- Draw shield frame: four segments (left vertical, right vertical, top horizontal, bottom horizontal) on BOT net
  - **Vertical frames**: Draw from `i_type_frame_inner_bottom` to `i_type_frame_inner_top` (NOT from outer_bottom to outer_top) to avoid overlap with horizontal frames
  - **Horizontal frames**: Draw from `-half_width` to `+half_width` at their respective y-positions
- Draw top strip: horizontal path at `y = i_type_strip_top_y`, from `(i_type_strip_x_left, i_type_strip_top_y)` to `(i_type_strip_x_right, i_type_strip_top_y)`, width `i_type_strip_width` (equals `strap_width`), TOP net
- Draw bottom strip: horizontal path at `y = i_type_strip_bottom_y`, from `(i_type_strip_x_left, i_type_strip_bottom_y)` to `(i_type_strip_x_right, i_type_strip_bottom_y)`, width `i_type_strip_width` (equals `strap_width`), BOT net
- Draw vertical fingers with alternating heights:
  - For i = 1 to total fingers (i_type_fingers_per_side + i_type_fingers_middle + i_type_fingers_per_side):
    - If i is odd: draw vertical path from `(i_type_finger_centers[i], i_type_bottom_minus_frame)` to `(i_type_finger_centers[i], i_type_h_top_y)`, width `i_type_finger_vertical_width`, BOT net
    - If i is even: draw vertical path from `(i_type_finger_centers[i], i_type_h_bottom_y)` to `(i_type_finger_centers[i], i_type_top_minus_frame)`, width `i_type_finger_vertical_width`, TOP net
- Draw connection line: vertical path from `(0, i_type_bottom_strip_bottom_edge)` to `(0, i_type_bottom_frame_top_edge)`, width `middle_vertical_width`, BOT net

3) L_mid (quadrant-interdigitated core)
- **⚠️ CRITICAL**: L_mid has **NO metal shield frame**. Do NOT draw any outer frame rectangles or paths on `layer_mid`.
- **ONLY draw these elements on L_mid**:
  - Central cross (vertical bar + horizontal bar)
  - Finger columns (four quadrants in two separate sides)
  - Straps (top strap + bottom straps)
- **Shield function**: Achieved by via belts placed at perimeter (see via section below); these vias connect L_top2↔L_mid and L_mid↔L_bot2
- Draw middle cross:
  - Vertical bar: from `(0, vbar_bottom_y)` to `(0, vbar_top_y)`, width `middle_vertical_width`, TOP net
  - Horizontal bar: from `(hbar_left_x, 0)` to `(hbar_right_x, 0)`, width `middle_horizontal_width`, TOP net
- Draw finger columns by quadrant and parity (render ALL four quadrants; two passes per side). Endpoints:
  - TOP‑bar fingers terminate at core boundaries to keep spacing from straps: top quadrants end at `core_top_y`, bottom quadrants start at `core_bottom_y`.
  - Strap‑connected fingers land on strap centerlines and stop at the clearance to the horizontal bar: top quadrants end at `upper_y`, bottom quadrants start at `lower_y`.
  - Left side (use `left_centers[]`, indices outer→inner, 1‑based j):
    - Top‑left quadrant: odd → from `top_strap_y` to `upper_y`; even → from `0` to `core_top_y`.
    - Bottom‑left quadrant: odd → from `core_bottom_y` to `0`; even → from `lower_y` to `bot_strap_y`.
  - Right side (use `right_centers[]`, indices inner→outer, 1‑based j):
    - Top‑right quadrant: odd → from `top_strap_y` to `upper_y`; even → from `0` to `core_top_y`.
    - Bottom‑right quadrant: odd → from `core_bottom_y` to `0`; even → from `lower_y` to `bot_strap_y`.
- Draw straps:
  - Top strap: one continuous path on `layer_mid`, `x: left_outer_edge → right_outer_edge`, `y = top_strap_y`, width `strap_width`, TOP net
  - Bottom straps: left `[left_outer_edge, left_inner_edge]`, right `[right_inner_edge, right_outer_edge]`, `y = bot_strap_y`, width `strap_width`, BOT net

4) L_bot2 (I-Type with shield)
- Same structure as L_top2: draw outer shield frame, horizontal strips, alternating-height fingers, and connection line
- Assign nets: BOT net (shield frame, bottom strip, odd-index fingers), TOP net (top strip, even-index fingers)
- Maintain I-Type geometry parameters and technology minima

5) L_bot (solid plate)
- Same as L_top: use `dbCreateRect` with bounding box `((-half_width, outer_bottom), (half_width, outer_top))` on `layer_bot`.

6) **Vias (BOT net only, all adjacent layer pairs) — ABSOLUTELY MANDATORY, CANNOT BE OMITTED**

**⚠️ CRITICAL REQUIREMENT**: Via arrays are **MANDATORY** and **MUST NOT BE OMITTED**. A Sandwich capacitor layout without via arrays is **INVALID** and **NON-FUNCTIONAL**.

**Consequences of missing vias**:
- All 5 layers remain electrically disconnected (no inter-layer connections)
- DRC violations will occur (typically 50+ violations: M2.S.2, M2.S.7, M3.S.7, M4.S.2, M4.S.7, M2.S.8, M3.S.8, M4.S.8)
- PEX extraction will fail or produce meaningless results
- Capacitor cannot function (no electrical connectivity between layers)
- The design is **completely unusable** without via arrays

**MUST generate via arrays for ALL 4 adjacent layer pairs**:

- `L_top ↔ L_top2`: 
  - Via arrays on I-Type shield frame (4 segments: left/right vertical, top/bottom horizontal)
  - ⚠️ **Via arrays on I-Type bottom strip** (DO NOT FORGET)

- `L_top2 ↔ L_mid`: 
  - ⚠️ **Shield via belts (8 segments)** — MOST CRITICAL, see Shield Via Belts section for details
  - Via arrays on top strap
  - Via arrays on I-Type bottom strip (if implementing bottom strip vias for this connection)

- `L_mid ↔ L_bot2`: 
  - ⚠️ **Shield via belts (8 segments)** — MOST CRITICAL, see Shield Via Belts section for details
  - Via arrays on top strap
  - Via arrays on bottom straps (left and right segments)

- `L_bot2 ↔ L_bot`: 
  - Via arrays on I-Type shield frame (4 segments: left/right vertical, top/bottom horizontal)
  - ⚠️ **Via arrays on I-Type bottom strip** (DO NOT FORGET)

**Via count validation**: A complete implementation should have approximately:
- Shield belts: 16 arrays (8 segments × 2 stacks)
- I-Type frames: 8 arrays (4 segments × 2 layers)
- I-Type strips: 2 arrays minimum (bottom strips on both I-Type layers)
- Straps: 3 arrays minimum (top strap shared, bottom straps left/right)
- **Total: ≥29 via arrays**

**Implementation rules**:
- Do not place vias on TOP fingers (in any layer)
- All via arrays must use computed `cutRows`/`cutColumns` from geometry (never hardcode to 1×1 unless calculation truly results in 1×1)
- **Validation**: Before running SKILL script, verify that the file contains `dbCreateVia` statements. If `dbCreateVia` is absent, the script is **INVALID** and must be rejected and regenerated.

7) Pins
- Place `TOP` pin at `(0,0)` on `layer_mid`; place `BOT` pin at `(0,0)` on `layer_bot` (optional probe label on the mid shield if required by PDK)

---

## Validation Notes

- Adjacency: All via pairs use adjacent metals only
- Spacing/widths: Respect technology minima and quantization rules
- Isolation: No unintended shorts between TOP fingers and any BOT conductor
- Numeric formatting in generated SKILL: use 5 decimals; ordering/grouping should follow the above checklist

### ⚠️ CRITICAL: Via Array Generation is MANDATORY

**Via arrays are ABSOLUTELY REQUIRED and CANNOT BE OMITTED under any circumstances.**

**Mandatory requirement**: Generated SKILL file MUST contain `dbCreateVia` statements for all 4 adjacent layer pairs plus shield via belts (minimum ≥29 via arrays, may vary based on geometry)

**Pre-execution validation checklist (MANDATORY)**:
1. ✓ Check for presence of `dbCreateVia` statements in the generated SKILL file
2. ✓ Verify via count: Should have ≥29 arrays (16 shield belts + 8 I-Type frames + 2 I-Type strips + 3 straps minimum)
3. ✓ Verify shield via belts: Must have 16 arrays (8 segments × 2 stacks)
4. ✓ Verify I-Type bottom strip vias: Must have 2 arrays (one for L_top↔L_top2, one for L_bot2↔L_bot)
5. ✓ Verify via sizing: No hardcoded cutRows=1 AND cutColumns=1 for all vias
6. ✓ **CRITICAL**: Verify that both geometry shapes AND via arrays are present in the same SKILL file - the function MUST NOT return SKILL code with only geometry
7. ✓ **CRITICAL**: Verify that the function completed both steps (geometry + via) in a single call - no separate function calls for via generation
8. ✓ If `dbCreateVia` is absent or count < 20, the script is **INVALID** and **MUST BE REJECTED**
9. ✓ Check for forbidden language (TODO, placeholder, simplified, "subsequent rounds", "SIMPLIFIED FOR INITIAL TESTING", etc.) in SKILL comments
10. ✓ Do NOT proceed with DRC/PEX if via arrays are missing
11. ✓ Regenerate the SKILL script with complete via array generation if validation fails

**Consequences of missing via arrays**:
- All 5 layers remain electrically disconnected (no inter-layer connections)
- DRC violations will occur (typically 50+ violations: M2.S.2, M2.S.7, M3.S.7, M4.S.2, M4.S.7, M2.S.8, M3.S.8, M4.S.8)
- PEX extraction will fail or produce meaningless results
- Capacitor cannot function (no electrical connectivity between layers)
- The design is **completely unusable** without via arrays

**Implementation requirement**: The `render_sandwich_skill` function MUST generate all via arrays. Omitting via generation is a **CRITICAL ERROR** that makes the layout non-functional.

---

### Explicit via array requirements (unambiguous)

For avoidance of doubt, the required via arrays for each adjacent layer pair are:

**L_top ↔ L_top2** (Expected: 5 arrays minimum):
- Fill via arrays on I-Type outer frame (4 segments: left vertical, right vertical, top horizontal, bottom horizontal)
- ⚠️ Fill via arrays on I-Type bottom strip (1 array, commonly missed)

**L_top2 ↔ L_mid** (Expected: 9-10 arrays minimum):
- ⚠️ Shield via belts (8 segments, one stack for this layer pair)
- Top strap via arrays (1 array)
- Bottom strap via arrays (if implementing, 2 arrays for left/right)

**L_mid ↔ L_bot2** (Expected: 11 arrays minimum):
- ⚠️ Shield via belts (8 segments, one stack for this layer pair)
- Top strap via arrays (1 array)
- Bottom strap via arrays (2 arrays: left segment and right segment)

**L_bot2 ↔ L_bot** (Expected: 5 arrays minimum):
- Fill via arrays on I-Type outer frame (4 segments: left vertical, right vertical, top horizontal, bottom horizontal)
- ⚠️ Fill via arrays on I-Type bottom strip (1 array, commonly missed)

**Implementation notes**:
- "Fill via arrays" means: size rows/columns to maximally populate the legal area using `via_pitch_cut` and `via_margin`, respecting keepouts and segment lengths.
- Shield via belts are segmented; do not emit a single full-span array. For every segment, emit both stacks for `L_top2↔L_mid` and `L_mid↔L_bot2`.
- **No shortcuts allowed**:
  - Never fix `cutRows`/`cutColumns` to 1 unless the formula-driven, rule-compliant value truly equals 1 (and document why).
  - When any computed value is < 1, adjust the relevant geometry (width/length/spacing) until a legal array exists, then regenerate the script.
  - Any omission, reduction, or "add later" plan for required via arrays renders the layout unusable.

## Variant: 5-Layer Quadrant-Interdigitated Sandwich (via-shield + internal straps + I-Type layers) — Final Implementation Guide

### High-level idea

- **5-layer structure**: L_top (solid rectangle) → L_top2 (I-Type with shield) → L_mid (quadrant-interdigitated) → L_bot2 (I-Type with shield) → L_bot (solid rectangle)
- Keep top/bottom plates (L_top, L_bot) as solid rectangles.
- **I-Type layers (L_top2, L_bot2)**: I-Type capacitor structure with shield frame, alternating-height fingers, and top/bottom strips. BOT network includes shield frame, bottom strip, and odd-index fingers. TOP network includes top strip and even-index fingers.
- **Middle layer (L_mid)**: **NO metal shield frame** - only central cross (vertical + horizontal bars), interdigitated fingers (four quadrants), and internal straps. Shield function is achieved by via belts on adjacent layers (L_top2↔L_mid and L_mid↔L_bot2).
- Split the interdigitated core into four quadrants around a central cross (vertical and horizontal mid-bars). Each quadrant draws its own fingers and net assignment independently and symmetrically.

### Required parameters (geometry-level)

- Layers: `layer_top`, `layer_top2`, `layer_mid`, `layer_bot2`, `layer_bot` (5 layers total).
- **Middle layer (L_mid) parameters**:
  - Frame width: unified `frame_width` (applies both vertical and horizontal frame lines for sizing/clearance math).
  - Core spacing to frame: `spacing` (vertical clearance between core and straps/outer frame).
  - Cross bars: `middle_vertical_width`, `middle_horizontal_width`.
  - Fingering:
    - `fingers` — total number of fingers per quadrant (odd+even together; no parity restriction).
    - `finger_vertical_width`, `finger_d` — finger width and finger pitch component.
    - Note: `finger_to_cross_d` is computed (not an input) to align middle layer core with I-Type middle fingers.
  - Internal straps (on L_mid):
    - `strap_width` — REQUIRED; width of both top and bottom internal straps.
    - Note: `strap_to_frame_d` is unified with `frame_to_core_d` (same parameter used for both).
  - Frame-to-core horizontal clearance: `frame_to_core_d` (used for overall width math, keepouts, and strap-to-frame spacing).
- **I-Type layers (L_top2, L_bot2) parameters**:
  - `i_type_fingers_per_side` — number of fingers on each side (typically 3).
  - `i_type_fingers_middle` — number of fingers in the middle (typically 4).
  - `i_type_finger_vertical_width`, `i_type_finger_d` — finger width and spacing.
  - `i_type_frame_horizontal_width`, `i_type_frame_vertical_width` — shield frame widths.
  - `i_type_spacing` — vertical gap from strip to finger region.
  - **CRITICAL CONSTRAINT**: `i_type_fingers_per_side` MUST EQUAL `fingers` (middle layer fingers per side) to ensure proper vertical alignment between I-Type and middle layer fingers.
  - Note: Strip positions align with middle layer straps (`top_strap_y`, `bot_strap_y`); strip width equals `strap_width`.
  - Note: I-Type side fingers align perfectly with middle layer quadrant fingers when `i_type_fingers_per_side == fingers`; middle fingers fill the core region.
- Via tech: `via_pitch_cut`, `via_margin` (array sizing heuristics; adjacent-layer via definitions must exist in the techfile for all 4 adjacent layer pairs).

### Derived quantities (key)

- Total height: `h_height + 2*(spacing + strap_width + frame_to_core_d) + 2*frame_width`.
- Strap centerlines: `top_strap_y`, `bot_strap_y`.
- Core bounds: `core_top_y = top_strap_y - strap_width/2 - spacing`, `core_bottom_y = bot_strap_y + strap_width/2 + spacing`.
- `finger_to_cross_d`: Computed from I-Type middle finger span to align with middle layer core: `finger_to_cross_d = (i_type_middle_span_with_clearance - middle_vertical_width) / 2`, where `i_type_middle_span_with_clearance = (i_type_fingers_middle - 1) * i_type_pitch + i_type_finger_vertical_width + 2 * i_type_finger_d`.
- **Middle layer finger centers**: **CRITICAL - TWO SEPARATE QUADRANTS, NOT CONTINUOUS**:
  - **Total fingers**: `2 * fingers` (e.g., 2×3 = 6), but distributed in **TWO SEPARATE quadrants**
  - **Spatial layout**: Left quadrant (`fingers` fingers) + **GAP (vertical bar)** + Right quadrant (`fingers` fingers)
  - **Algorithm** (CORRECT - generates two separate groups):
    - **Left quadrant fingers**: Place `fingers` fingers starting from outer edge, moving inward
      - Compute with I-Type left side centers: Use first `fingers` positions from I-Type centers
      - Example: If I-Type centers are `[-0.45, -0.35, -0.25, ...]`, take first 3: `[-0.45, -0.35, -0.25]`
    - **Right quadrant fingers**: Place `fingers` fingers starting from inner edge, moving outward
      - Compute with I-Type right side centers: Use last `fingers` positions from I-Type centers
      - Example: If I-Type centers are `[..., 0.25, 0.35, 0.45]`, take last 3: `[0.25, 0.35, 0.45]`
  - **Constraint**: All fingers must satisfy keepout `|x| ≥ middle_vertical_width/2 + finger_to_cross_d + finger_vertical_width/2`
  - **Critical requirement**: Middle layer fingers MUST align with I-Type side fingers (left `fingers` and right `fingers`)
  - **WRONG APPROACH** ❌: Generating continuous span like `[-0.25, -0.15, -0.05, 0.05, 0.15, 0.25]` - this ignores the vertical bar gap!
- I-Type finger centers: **centered symmetrically** and aligned with middle layer, with consistent spacing:
  - **Total fingers**: `i_type_fingers_per_side * 2 + i_type_fingers_middle` (e.g., 3+3+4=10)
  - **Symmetric distribution**: Fingers distributed symmetrically around x=0
  - **Alignment strategy**: 
    - Compute total span: `(total_fingers - 1) * i_type_pitch`
    - Start from: `x_start = -total_span / 2`
    - Generate centers: `x_i = x_start + i * i_type_pitch` for i = 0 to (total_fingers-1)
  - **Critical requirement**: All I-Type fingers must maintain consistent `i_type_pitch` spacing and be **centered symmetrically**

### Quadrant rules (net mapping and extents)

- Within each quadrant, columns are indexed locally; odd/even alternate to realize interdigitation.
- Net mapping:
  - Top quadrants: odd → internal TOP strap (upper strap), even → central TOP horizontal bar.
  - Bottom quadrants: odd → central TOP horizontal bar, even → internal BOT strap (lower strap).
- Vertical extents:
  - Fingers to TOP bar must extend all the way to `core_top_y` (top quadrants) or `core_bottom_y` (bottom quadrants), guaranteeing the strap↔TOP finger edge-to-edge spacing equals `spacing`.
  - Fingers to straps land directly on the corresponding strap centerlines (`top_strap_y` / `bot_strap_y`).

### Straps and vias (middle layer L_mid)

- Top strap: one continuous path on L_mid across left and right finger spans (no separation between quadrants). Electrical connection to TOP is established by the central TOP bar; no extra treatment needed unless required by PDK.
- Bottom straps: two quadrant-spanning paths on L_mid (left and right). Place via arrays `layer_mid ↔ layer_bot2` centered on each bottom strap with cuts sized by `(strap_width, strap_length)` and `via_pitch_cut/margin`.

#### Bottom strap via arrays — implementation details (MUST)

- Strap segment spans (per side):
  - Left span length: `len_left = left_inner_edge − left_outer_edge` (require `len_left > 0`).
  - Right span length: `len_right = right_outer_edge − right_inner_edge` (require `len_right > 0`).
- Centers for via arrays:
  - `cx_left = (left_outer_edge + left_inner_edge)/2`, `cy_left = bot_strap_y`.
  - `cx_right = (right_inner_edge + right_outer_edge)/2`, `cy_right = bot_strap_y`.
- Row/column sizing (use via tech params):
  - Rows along strap width (Y): `rows_s = floor((strap_width + via_margin)/via_pitch_cut)`, enforce `rows_s ≥ 1`.
  - Columns along strap length (X): `cols_left = floor((len_left + via_margin)/via_pitch_cut)`, `cols_right = floor((len_right + via_margin)/via_pitch_cut)`, enforce `cols_* ≥ 1`.
- Placement and stacks:
  - Emit both `layer_mid↔layer_bot2` and `layer_top2↔layer_mid` via arrays for the top strap and both bottom straps (left and right), using the above centers and counts.
  - If any `len_* ≤ 0` or computed rows/cols < 1, treat generation as invalid and adjust parameters (increase strap length/width or geometry) before proceeding.
- Shield (via-only frame around core): Do not draw continuous metal for the outer frame on `layer_mid`. Instead, realize the shield as segmented stacked via belts that avoid the cross openings and align between horizontal and vertical segments for natural corner connectivity:
  - Define cross openings (keepouts) using cross widths and `frame_to_core_d`:
    - Horizontal openings around the vertical bar: `h_opening_x1 = −(middle_vertical_width/2 + frame_to_core_d)`, `h_opening_x2 = +(middle_vertical_width/2 + frame_to_core_d)`.
    - Vertical openings around the horizontal bar: `v_opening_y1 = −(middle_horizontal_width/2 + frame_to_core_d)`, `v_opening_y2 = +(middle_horizontal_width/2 + frame_to_core_d)`.
  - Segment the frame into 8 segments (using I-Type frame boundaries for alignment):
    - Top horizontal: `[i_type_frame_x_left, h_opening_x1]` and `[h_opening_x2, i_type_frame_x_right]` at the top frame band.
    - Bottom horizontal: `[i_type_frame_x_left, h_opening_x1]` and `[h_opening_x2, i_type_frame_x_right]` at the bottom frame band.
    - Left vertical: bottom segment `[y_anchor_bot, v_opening_y1]` and top segment `[v_opening_y2, y_anchor_top]` at `x = i_type_leftFrameX`.
    - Right vertical: bottom segment `[y_anchor_bot, v_opening_y1]` and top segment `[v_opening_y2, y_anchor_top]` at `x = i_type_rightFrameX`.
  - Segment length formulas (must be POSITIVE by construction; otherwise skip the segment):
    - **⚠️⚠️⚠️ MANDATORY EXECUTION ORDER FOR SHIELD VIA BELTS ⚠️⚠️⚠️**
      - **🚨 CRITICAL**: You MUST execute these steps in the EXACT order shown below. Do NOT skip steps, do NOT change the order, do NOT combine steps.
      - **🚨 CRITICAL**: Each step produces values that are REQUIRED by subsequent steps. Skipping or reordering will cause incorrect calculations.
      - **🚨 CRITICAL**: If you find yourself using midpoint calculations `(x1+x2)/2` or `(y1+y2)/2`, you have skipped required steps. STOP and restart from Step 0.
    
    - **Step 0: Compute horizontal segment lengths** — **MUST be done FIRST, before any center calculations**:
      - **⚠️ CRITICAL**: This is the FIRST step. Do NOT calculate via centers before completing this step.
      - **Calculation sequence** (MUST follow this order):
        1. Identify I-Type frame boundaries: `i_type_frame_x_left` and `i_type_frame_x_right` (from geometry dict)
        2. Identify horizontal openings: `h_opening_x1` and `h_opening_x2` (from geometry dict)
        3. Compute segment lengths:
           - Top-left: `len_tl = h_opening_x1 − i_type_frame_x_left`
           - Top-right: `len_tr = i_type_frame_x_right − h_opening_x2`
           - Bottom-left: `len_bl = len_tl` (same as top-left)
           - Bottom-right: `len_br = len_tr` (same as top-right)
      - **❌ FORBIDDEN**: `len = h_opening_x1 − (-half_width)` or `len = half_width − h_opening_x2`
      - **❌ FORBIDDEN**: Using `half_width` instead of `i_type_frame_x_left/right`
      - **⚠️ CRITICAL**: These lengths are REQUIRED for Step 2. Do NOT proceed to Step 2 without completing Step 0.
      - **Rationale**: Segment lengths must be computed from actual I-Type frame boundaries, not from overall device half_width, to ensure correct via array placement.
    - Verticals (use openings around horizontal bar, anchored to frame edges):
      - Left-bottom: `len = v_opening_y1 − y_anchor_bot`
      - Left-top: `len = y_anchor_top − v_opening_y2`
      - Right-bottom: `len = v_opening_y1 − y_anchor_bot`
      - Right-top: `len = y_anchor_top − v_opening_y2`
    - Guard: if `len ≤ 0`, do NOT emit a via array for that segment.
  - **🚨🚨🚨 CRITICAL: VIA COUNT CALCULATION — MUST BE CORRECT 🚨🚨🚨**
    - **⚠️ CRITICAL**: Via counts (`cutRows` and `cutColumns`) are CRITICAL for proper via array generation. Incorrect counts will cause DRC violations or missing connections.
    - **⚠️ CRITICAL**: You MUST use the EXACT formulas below. Do NOT hardcode, do NOT guess, do NOT use approximate values.
    - **⚠️ CRITICAL**: The formula is ALWAYS: `count = max(1, floor((dimension + via_margin) / via_pitch_cut))`
    - **⚠️ CRITICAL**: You MUST use the actual dimensions from geometry calculations, NOT `half_width` or other incorrect values.
    - **⚠️ CRITICAL**: You MUST use `via_margin` and `via_pitch_cut` from the technology parameters, NOT hardcoded values.
    - **❌ FORBIDDEN**: Hardcoding `cutRows=1` and `cutColumns=1` for all via arrays
    - **❌ FORBIDDEN**: Using approximate values like `cutRows ≈ 5` or `cutColumns ≈ 2`
    - **❌ FORBIDDEN**: Using `half_width` or other incorrect dimensions in count calculations
    - **❌ FORBIDDEN**: Skipping the `max(1, ...)` safeguard (counts must be at least 1)
  
  - Sizing (use technology via pitch/margin and I-Type frame widths):
    - **Horizontal rows** (for horizontal belt via arrays): `rows_v = max(1, floor((i_type_frame_horizontal_width + via_margin) / via_pitch_cut))` ← **MUST use `i_type_frame_horizontal_width`, NOT `half_width`**
    - **Vertical columns** (for vertical belt via arrays): `cols_v = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))` ← **MUST use `i_type_frame_vertical_width`, NOT `half_width`**
    - **Horizontal columns per segment**: `cols = max(1, floor((segment_length + via_margin) / via_pitch_cut))` ← **MUST use segment length from Step 0, NOT `half_width`**
    - **Vertical rows per segment**: `rows = max(1, floor((segment_length + via_margin) / via_pitch_cut))` ← **MUST use segment length from Step 3, NOT approximate values**
    - **⚠️ CRITICAL**: All counts MUST be calculated using the exact formulas above. Verify that all counts are >= 1 before using them in `dbCreateVia` statements.
  - **⚠️⚠️⚠️ CRITICAL: GRID ALIGNMENT REQUIREMENT ⚠️⚠️⚠️**
    - **ABSOLUTELY MANDATORY**: All via arrays MUST be aligned to a consistent via pitch grid. This is NOT optional.
    - **FORBIDDEN**: Using midpoint centering (e.g., `cx = (x1 + x2)/2` or `cy = (y1 + y2)/2`) — this breaks grid alignment and causes DRC errors.
    - **REQUIRED**: All via centers must be computed from grid anchors using via pitch calculations.

  - **🚨🚨🚨 MANDATORY: VIA CALCULATION MUST FOLLOW THESE STEPS IN EXACT ORDER 🚨🚨🚨**
    - **⚠️ CRITICAL**: You MUST follow these steps sequentially. Do NOT skip steps, do NOT combine steps, do NOT use shortcuts or intuitive calculations.
    - **⚠️ CRITICAL**: Each step depends on the previous step's results. Skipping or changing the order will produce incorrect results.
    - **⚠️ CRITICAL**: If you find yourself calculating via centers using midpoint formulas `(x1+x2)/2` or `(y1+y2)/2`, STOP IMMEDIATELY and restart from Step 0.

  - Alignment between horizontal and vertical belts (using I-Type frame positions):
    - **Step 0: Compute horizontal segment lengths** — **MUST be done FIRST, before any center calculations**:
      - **❌ FORBIDDEN**: `len = h_opening_x1 − (-half_width)` or `len = half_width − h_opening_x2`
      - **✅ REQUIRED**: 
        - Top-left: `len_tl = h_opening_x1 − i_type_frame_x_left`
        - Top-right: `len_tr = i_type_frame_x_right − h_opening_x2`
        - Bottom-left: `len_bl = len_tl` (same as top-left)
        - Bottom-right: `len_br = len_tr` (same as top-right)
      - **⚠️ CRITICAL**: These lengths are used in Step 2. Do NOT proceed to Step 2 without completing Step 0.
    
    - **Step 1: Compute vertical grid extremes** — **MUST be done BEFORE Step 2**:
      - **⚠️ CRITICAL**: This step MUST be completed before calculating horizontal belt centers.
      - **Required calculations**:
        - First, compute `cols_v = floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut)`
        - Then compute: `left_vert_leftmost_x = i_type_leftFrameX − (cols_v−1)*0.5*via_pitch_cut`
        - Then compute: `right_vert_rightmost_x = i_type_rightFrameX + (cols_v−1)*0.5*via_pitch_cut`
      - **⚠️ CRITICAL**: These values define the leftmost and rightmost x-positions of the vertical via grids. They are REQUIRED for Step 2.
      - **❌ FORBIDDEN**: Skipping this step and using `half_width` or other values for horizontal belt centers.
    
    - **Step 2: Compute horizontal belt centers** — **MUST use Step 1 results, NOT midpoint**:
      - **⚠️ CRITICAL**: This step REQUIRES `left_vert_leftmost_x` and `right_vert_rightmost_x` from Step 1.
      - **⚠️ CRITICAL**: This step REQUIRES segment lengths from Step 0.
      - **🚨🚨🚨 CRITICAL: VIA COUNT CALCULATION MUST BE CORRECT 🚨🚨🚨**
        - **⚠️ CRITICAL**: Via counts (`cutRows` and `cutColumns`) MUST be calculated using the EXACT formulas below. Do NOT hardcode, do NOT guess, do NOT use approximate values.
        - **⚠️ CRITICAL**: The formula is: `count = max(1, floor((length + via_margin) / via_pitch_cut))`
        - **⚠️ CRITICAL**: You MUST use the segment length from Step 0, NOT `half_width` or any other value.
        - **⚠️ CRITICAL**: You MUST use `via_margin` and `via_pitch_cut` from the technology parameters, NOT hardcoded values.
        - **❌ FORBIDDEN**: Hardcoding `cutRows=1` and `cutColumns=1` for all segments
        - **❌ FORBIDDEN**: Using approximate values like `cutColumns ≈ 2` or `cutRows ≈ 5`
        - **❌ FORBIDDEN**: Using `half_width` or other incorrect values in the count calculation
        - **❌ FORBIDDEN**: Using `geometry['cols_v']` for horizontal belt `cutRows` (should use `i_type_frame_horizontal_width`)
        - **❌ FORBIDDEN**: Using hardcoded `cutColumns=1` for horizontal belts (should use calculated segment lengths)
      - **🚨🚨🚨 CRITICAL: EACH SEGMENT MUST BE CALCULATED SEPARATELY 🚨🚨🚨**
        - **⚠️ CRITICAL**: Each of the 4 horizontal segments (top-left, top-right, bottom-left, bottom-right) has a DIFFERENT length and therefore requires a DIFFERENT `cutColumns` value.
        - **⚠️ CRITICAL**: You MUST calculate via counts and centers for EACH segment separately. Do NOT use the same viaParams for all segments.
        - **⚠️ CRITICAL**: You MUST use the calculated values (`cutColumns_tl`, `cutColumns_tr`, etc.) in the generated SKILL code. Do NOT calculate them and then ignore them.
      - **Calculation sequence** (MUST follow this order):
        1. **Compute via counts FIRST** (using segment lengths from Step 0):
           - `cutRows_horiz = max(1, floor((i_type_frame_horizontal_width + via_margin) / via_pitch_cut))` ← **MUST use `i_type_frame_horizontal_width`, NOT `cols_v`**
           - `cutColumns_tl = max(1, floor((len_tl + via_margin) / via_pitch_cut))` ← **MUST use `len_tl` from Step 0**
           - `cutColumns_tr = max(1, floor((len_tr + via_margin) / via_pitch_cut))` ← **MUST use `len_tr` from Step 0**
           - `cutColumns_bl = max(1, floor((len_bl + via_margin) / via_pitch_cut))` ← **MUST use `len_bl` from Step 0**
           - `cutColumns_br = max(1, floor((len_br + via_margin) / via_pitch_cut))` ← **MUST use `len_br` from Step 0**
           - **⚠️ CRITICAL**: Verify that `cutColumns_* >= 1` for all segments. If any is 0 or negative, check your segment length calculation in Step 0.
        2. **THEN** compute centers using Step 1 results and the calculated via counts:
           - Top-left: `cx_tl = left_vert_leftmost_x + (cutColumns_tl−1)*0.5*via_pitch_cut` ← **MUST use `cutColumns_tl`**
           - Top-right: `cx_tr = right_vert_rightmost_x − (cutColumns_tr−1)*0.5*via_pitch_cut` ← **MUST use `cutColumns_tr`**
           - Bottom-left: `cx_bl = left_vert_leftmost_x + (cutColumns_bl−1)*0.5*via_pitch_cut` ← **MUST use `cutColumns_bl`**
           - Bottom-right: `cx_br = right_vert_rightmost_x − (cutColumns_br−1)*0.5*via_pitch_cut` ← **MUST use `cutColumns_br`**
        3. **THEN** generate separate viaParams for EACH segment:
           - `viaParams_tl = list(list("cutRows" cutRows_horiz) list("cutColumns" cutColumns_tl))`
           - `viaParams_tr = list(list("cutRows" cutRows_horiz) list("cutColumns" cutColumns_tr))`
           - `viaParams_bl = list(list("cutRows" cutRows_horiz) list("cutColumns" cutColumns_bl))`
           - `viaParams_br = list(list("cutRows" cutRows_horiz) list("cutColumns" cutColumns_br))`
        4. **THEN** generate separate `dbCreateVia` statements for EACH segment using the corresponding viaParams and center coordinates.
      - **❌ FORBIDDEN**: `cx = (x_start + x_end)/2` or `cx = (-half_width + len/2)` or `cx = (h_opening_x2 + len/2)`
      - **❌ FORBIDDEN**: Calculating centers before completing Steps 0 and 1.
      - **❌ FORBIDDEN**: Using the same viaParams for all 4 horizontal segments.
      - **❌ FORBIDDEN**: Calculating via counts but then not using them in the generated SKILL code.
      - **Rationale**: Horizontal belts must align with the vertical via grids to ensure proper corner connectivity and avoid DRC violations. Each segment has different dimensions and requires separate calculations.
  - Belt centers (using I-Type frame parameters for alignment):
    - Horizontal belt y-centers at the mid of the frame bands: `y_top_mid = (outer_top + i_type_frame_inner_top)/2`, `y_bot_mid = (outer_bottom + i_type_frame_inner_bottom)/2`.
    - Vertical belt x-centers at `x = i_type_leftFrameX` and `x = i_type_rightFrameX`.
    - Vertical belt column count from I-Type frame width: `cols_v = floor((i_type_frame_vertical_width + via_margin)/via_pitch_cut)`.
    - Vertical grid extremes for aligning horizontal belt columns: `left_vert_leftmost_x = i_type_leftFrameX − (cols_v−1)*0.5*via_pitch_cut`, `right_vert_rightmost_x = i_type_rightFrameX + (cols_v−1)*0.5*via_pitch_cut`.
    - **Step 3: Compute vertical segment lengths** — **MUST be done BEFORE Step 4**:
      - **⚠️ CRITICAL**: This step MUST be completed before calculating vertical belt centers.
      - **Required calculations**:
        - Left-top: `len_lt = y_anchor_top − v_opening_y2`
        - Left-bottom: `len_lb = v_opening_y1 − y_anchor_bot`
        - Right-top: `len_rt = len_lt` (same as left-top)
        - Right-bottom: `len_rb = len_lb` (same as left-bottom)
      - **⚠️ CRITICAL**: These lengths are used in Step 4. Do NOT proceed to Step 4 without completing Step 3.
      - **⚠️ CRITICAL**: This step REQUIRES `y_anchor_top` and `y_anchor_bot` which are computed in Step 3a below.
    
    - **Step 3a: Compute frame edge anchors** — **MUST be done BEFORE Step 3 and Step 4**:
      - **⚠️ CRITICAL**: These anchors MUST be computed before calculating vertical segment lengths and centers.
      - **Required calculations** (MUST be done in this order):
        1. `y_anchor_top = outer_top − (via_pitch_cut − via_margin)/2`
        2. `y_anchor_bot = outer_bottom + (via_pitch_cut − via_margin)/2`
      - **⚠️ CRITICAL**: These values are REQUIRED for Step 3 (segment lengths) and Step 4 (centers).
      - **❌ FORBIDDEN**: Using `cy = 0` or other values instead of computing these anchors.
    
    - **Step 4: Compute vertical belt y-centers** — **MUST use Step 3a anchors and Step 3 lengths, NOT midpoint**:
      - **⚠️ CRITICAL**: This step REQUIRES `y_anchor_top` and `y_anchor_bot` from Step 3a.
      - **⚠️ CRITICAL**: This step REQUIRES segment lengths from Step 3.
      - **🚨🚨🚨 CRITICAL: VIA COUNT CALCULATION MUST BE CORRECT 🚨🚨🚨**
        - **⚠️ CRITICAL**: Via counts (`cutRows` and `cutColumns`) MUST be calculated using the EXACT formulas below. Do NOT hardcode, do NOT guess, do NOT use approximate values.
        - **⚠️ CRITICAL**: The formula is: `count = max(1, floor((length + via_margin) / via_pitch_cut))`
        - **⚠️ CRITICAL**: You MUST use the segment length from Step 3, NOT approximate values or hardcoded numbers.
        - **⚠️ CRITICAL**: You MUST use `via_margin` and `via_pitch_cut` from the technology parameters, NOT hardcoded values.
        - **❌ FORBIDDEN**: Hardcoding `cutRows=1` and `cutColumns=1` for all segments
        - **❌ FORBIDDEN**: Using approximate values like `cutRows ≈ 5` or `cutColumns ≈ 2`
        - **❌ FORBIDDEN**: Using incorrect segment lengths in the count calculation
        - **❌ FORBIDDEN**: Using hardcoded `cutRows=1` for vertical belts (should use calculated segment lengths)
        - **❌ FORBIDDEN**: Using `geometry['cols_v']` for vertical belt `cutColumns` without proper calculation
      - **🚨🚨🚨 CRITICAL: EACH SEGMENT MUST BE CALCULATED SEPARATELY 🚨🚨🚨**
        - **⚠️ CRITICAL**: Each of the 4 vertical segments (left-top, left-bottom, right-top, right-bottom) has a DIFFERENT length and therefore requires a DIFFERENT `cutRows` value.
        - **⚠️ CRITICAL**: You MUST calculate via counts and centers for EACH segment separately. Do NOT use the same viaParams for all segments.
        - **⚠️ CRITICAL**: You MUST use the calculated values (`cutRows_lt`, `cutRows_lb`, etc.) in the generated SKILL code. Do NOT calculate them and then ignore them.
      - **Calculation sequence** (MUST follow this order):
        1. **Compute via counts FIRST** (using segment lengths from Step 3):
           - `cutColumns_vert = max(1, floor((i_type_frame_vertical_width + via_margin) / via_pitch_cut))` ← **MUST use `i_type_frame_vertical_width`**
           - `cutRows_lt = max(1, floor((len_lt + via_margin) / via_pitch_cut))` ← **MUST use `len_lt` from Step 3**
           - `cutRows_lb = max(1, floor((len_lb + via_margin) / via_pitch_cut))` ← **MUST use `len_lb` from Step 3**
           - `cutRows_rt = max(1, floor((len_rt + via_margin) / via_pitch_cut))` ← **MUST use `len_rt` from Step 3**
           - `cutRows_rb = max(1, floor((len_rb + via_margin) / via_pitch_cut))` ← **MUST use `len_rb` from Step 3**
           - **⚠️ CRITICAL**: Verify that `cutRows_* >= 1` for all segments. If any is 0 or negative, check your segment length calculation in Step 3.
        2. **THEN** compute centers using Step 3a results and the calculated via counts:
           - Left-top: `cy_lt = y_anchor_top − (cutRows_lt−1)*0.5*via_pitch_cut` ← **MUST use `cutRows_lt`**
           - Left-bottom: `cy_lb = y_anchor_bot + (cutRows_lb−1)*0.5*via_pitch_cut` ← **MUST use `cutRows_lb`**
           - Right-top: `cy_rt = y_anchor_top − (cutRows_rt−1)*0.5*via_pitch_cut` ← **MUST use `cutRows_rt`**
           - Right-bottom: `cy_rb = y_anchor_bot + (cutRows_rb−1)*0.5*via_pitch_cut` ← **MUST use `cutRows_rb`**
        3. **THEN** generate separate viaParams for EACH segment:
           - `viaParams_lt = list(list("cutRows" cutRows_lt) list("cutColumns" cutColumns_vert))`
           - `viaParams_lb = list(list("cutRows" cutRows_lb) list("cutColumns" cutColumns_vert))`
           - `viaParams_rt = list(list("cutRows" cutRows_rt) list("cutColumns" cutColumns_vert))`
           - `viaParams_rb = list(list("cutRows" cutRows_rb) list("cutColumns" cutColumns_vert))`
        4. **THEN** generate separate `dbCreateVia` statements for EACH segment using the corresponding viaParams and center coordinates.
      - **❌ FORBIDDEN**: `cy = (y_start + y_end)/2` or `cy = (v_opening_y2 + len/2)` or `cy = (y_anchor_bot + len/2)` or `cy = 0`
      - **❌ FORBIDDEN**: Calculating centers before completing Steps 3a and 3.
      - **❌ FORBIDDEN**: Using the same viaParams for all 4 vertical segments.
      - **❌ FORBIDDEN**: Calculating via counts but then not using them in the generated SKILL code.
      - **Rationale**: Vertical belts must be anchored to frame edges with via pitch alignment to ensure proper connectivity and avoid DRC violations. Each segment has different dimensions and requires separate calculations.
  - **🚨🚨🚨 CRITICAL: EACH LAYER PAIR MUST HAVE ITS OWN VIA PARAMETERS 🚨🚨🚨**
    - **⚠️ CRITICAL**: `(layer_top2 ↔ layer_mid)` and `(layer_mid ↔ layer_bot2)` are DIFFERENT layer pairs and MUST have SEPARATE via parameters.
    - **⚠️ CRITICAL**: You MUST generate separate viaParams for each layer pair. Do NOT reuse viaParams from one layer pair for another.
    - **⚠️ CRITICAL**: For `(layer_top2 ↔ layer_mid)`, use viaDefId and viaParams with names like `viaDefId_{layer_top2}_{layer_mid}` and `viaParams_{layer_top2}_{layer_mid}_*`.
    - **⚠️ CRITICAL**: For `(layer_mid ↔ layer_bot2)`, use viaDefId and viaParams with names like `viaDefId_{layer_mid}_{layer_bot2}` and `viaParams_{layer_mid}_{layer_bot2}_*`.
    - **❌ FORBIDDEN**: Using `viaParams_{layer_top2}_{layer_mid}_*` for `(layer_mid ↔ layer_bot2)` via arrays.
    - **❌ FORBIDDEN**: Reusing via parameters across different layer pairs.
  - Place stacked belts for both adjacent-layer pairs: iterate `(layer_top2 ↔ layer_mid)` and `(layer_mid ↔ layer_bot2)` using the same segment centers and counts (but with SEPARATE via parameters for each layer pair). Do not add explicit corner via arrays; corner connectivity is achieved by the aligned segment arrays.

#### I-Type layers (L_top2, L_bot2) — implementation details (MUST)

- **Shield frame**: Draw all four frame segments (left vertical, right vertical, top horizontal, bottom horizontal) on BOT net.
- **Horizontal strips**: Draw top and bottom strips aligned with middle layer straps.
  - Strip positions: `i_type_strip_top_y = top_strap_y`, `i_type_strip_bottom_y = bot_strap_y` (aligned with middle layer straps)
  - Strip width: `i_type_strip_width = strap_width` (same as middle layer strap width)
  - Strip x coordinates: from `i_type_strip_x_left` to `i_type_strip_x_right` (from first finger left edge to last finger right edge)
  - Top strip: TOP net
  - Bottom strip: BOT net
- **Vertical fingers**: Draw with alternating heights, aligned with middle layer fingers.
  - Finger centers: aligned with middle layer fingers with consistent spacing:
    - **Left side**: Start from `left_centers[0]`, place `i_type_fingers_per_side` fingers with `i_type_pitch` spacing (aligned with middle layer's left side)
    - **Middle**: Continue from last left finger, place `i_type_fingers_middle` fingers with `i_type_pitch` spacing (span matches middle layer core width via `finger_to_cross_d` adjustment)
    - **Right side**: Continue from last middle finger, place `i_type_fingers_per_side` fingers with `i_type_pitch` spacing
    - **Critical**: All fingers (left + middle + right) must maintain consistent `i_type_pitch` spacing throughout
  - Finger spacing: consistent `i_type_pitch = i_type_finger_vertical_width + i_type_finger_d` across all fingers (left side + middle + right side)
  - Odd-index fingers (1, 3, 5, ...): from `i_type_bottom_minus_frame` to `i_type_h_top_y` (BOT net)
  - Even-index fingers (2, 4, 6, ...): from `i_type_h_bottom_y` to `i_type_top_minus_frame` (TOP net)
- **Connection line**: Draw vertical connection line from bottom strip to bottom frame (at x = 0) for BOT net connectivity. Width equals `middle_vertical_width`.
- **Via arrays**: Place via arrays for inter-layer connections.
  - `L_top ↔ L_top2`: Fill via arrays on I-Type outer frame (all four frame segments) and on I-Type bottom strip
  - `L_top2 ↔ L_mid`: Place via arrays on shield via belts (8 segments around middle layer perimeter), top strap, and bottom straps (left/right)
  - `L_mid ↔ L_bot2`: Place via arrays on shield via belts (8 segments around middle layer perimeter), top strap, and bottom straps (left/right)
  - `L_bot2 ↔ L_bot`: Fill via arrays on I-Type outer frame (all four frame segments) and on I-Type bottom strip
  - **Note**: Shield via belts for L_top2↔L_mid and L_mid↔L_bot2 are placed at the perimeter (aligned with I-Type frame positions), but L_mid itself has NO metal frame
- **Geometry alignment**: I-Type layers must align with overall device boundaries (`outer_top`, `outer_bottom`, `half_width`). Strip positions and width align with middle layer straps. Finger positions align with middle layer fingers.

#### Atomic co‑generation (MUST — same round, same script)

- **⚠️ CRITICAL**: "Per round" means for EACH parameter iteration round (Round 1, Round 2, etc.). Every round must generate a COMPLETE SKILL script. Round 1 is NOT a simplified version - it must include ALL elements listed below.
- The following elements MUST be generated together in a single SKILL script per round (no staging across files/rounds): 
  - **L_top plate**: solid rectangle
  - **L_top2**: I-Type structure (shield frame, strips, fingers, connection line)
  - **L_mid**: central cross (vertical + horizontal bars), all fingers (four quadrants in two separate sides), top strap, both bottom straps (**NO metal shield frame on L_mid**)
  - **L_bot2**: I-Type structure (shield frame, strips, fingers, connection line)
  - **L_bot plate**: solid rectangle
  - **All via arrays**: for all 4 adjacent layer pairs (top↔top2, top2↔mid, mid↔bot2, bot2↔bot), including 8-segment shield via belts for top2↔mid and mid↔bot2
- If any required element above is missing from the script, treat the round as invalid; do not run; regenerate to include all elements in the same script.

#### Shield via belts — enforcement and anti‑patterns

- Enforcement:
  - Mandatory segmentation into 8 frame segments (top/bottom left+right, left/right bottom+top). Never emit one full‑span via array across a frame edge.
  - Horizontal segments: rows `= floor((frame_width + via_margin)/via_pitch_cut)`; columns per segment `= floor((segment_length + via_margin)/via_pitch_cut)`.
  - Vertical segments: columns `= floor((frame_width + via_margin)/via_pitch_cut)`; rows per segment `= floor((segment_length + via_margin)/via_pitch_cut)`.
  - **⚠️⚠️⚠️ CRITICAL: VIA CENTER CALCULATION — GRID ALIGNMENT MANDATORY ⚠️⚠️⚠️**:
    - Horizontal belt `cx`: **MUST** use `y_top_mid`, `y_bot_mid` for y-coordinates; **MUST** align `cx` to vertical grids:
      - **❌ FORBIDDEN**: `cx = (x_start + x_end)/2` or `cx = (-half_width + len/2)` or `cx = (h_opening_x2 + len/2)`
      - **✅ REQUIRED**: For top‑left/bottom-left horizontals: `cx = left_vert_leftmost_x + (cols−1)*0.5*via_pitch_cut`
      - **✅ REQUIRED**: For top‑right/bottom-right horizontals: `cx = right_vert_rightmost_x − (cols−1)*0.5*via_pitch_cut`
    - Vertical belt `cy`: **MUST** use `x = i_type_leftFrameX/i_type_rightFrameX` for x-coordinates; **MUST** anchor to frame edges:
      - **❌ FORBIDDEN**: `cy = (y_start + y_end)/2` or `cy = 0` or `cy = (v_opening_y2 + len/2)`
      - **✅ REQUIRED**: `cy = y_anchor_top − (rows−1)*0.5*pitch_cut` (top segments) or `cy = y_anchor_bot + (rows−1)*0.5*pitch_cut` (bottom segments)
  - For each segment, create two stacked arrays: `layer_top2↔layer_mid` and `layer_mid↔layer_bot2` with identical centers and counts.
  - Do not place extra corner arrays.
  - Generation requirement (every round): Always emit the complete 8‑segment shield via belts with both stacks (e.g., `M6↔M5` and `M5↔M4` for layers M7/M6/M5/M4/M3)—no simplification or omission. **This applies to Round 1, Round 2, and ALL subsequent rounds - every round must be complete.**
  - Guidance: Do not output simplified variants (e.g., only bottom‑strap vias or a single full‑span array) and avoid placeholders such as “TODO/to be implemented”. If the belts were not generated, regenerate with the complete belts per the formulas above.

- **🚫🚫🚫 ABSOLUTE FORBIDDEN ANTI-PATTERNS (observed in logs) — REJECT IMMEDIATELY 🚫🚫🚫**:
  - **❌ FORBIDDEN #1**: Midpoint-centering horizontal belts (e.g., `cx = (x1 + x2)/2` or `cx = (-half_width + len/2)` or `cx = (h_opening_x2 + len/2)`) — **THIS BREAKS ALIGNMENT WITH VERTICAL GRIDS AND CAUSES DRC ERRORS**.
  - **❌ FORBIDDEN #2**: Midpoint-centering vertical belts (e.g., `cy = (y1 + y2)/2` or `cy = (v_opening_y2 + len/2)` or `cy = (y_anchor_bot + len/2)`) — **THIS BREAKS FRAME EDGE ANCHORING AND VIA PITCH ALIGNMENT**.
  - **❌ FORBIDDEN #3**: Using `half_width` for horizontal segment length calculations instead of `i_type_frame_x_left/right` — **THIS GIVES WRONG SEGMENT LENGTHS**.
  - **❌ FORBIDDEN #4**: Placing vertical belts with `cy=0` instead of anchored to frame edges via `y_anchor_top/bot` — **THIS BREAKS VIA PITCH ALIGNMENT**.
  - **❌ FORBIDDEN #5**: A single via array centered at `x=0` for the entire top/bottom edge (violates openings; wrong columns).
  - **❌ FORBIDDEN #6**: Using `cols_v` (derived from frame width) as the column count for horizontal belts (should use segment length).
  - **❌ FORBIDDEN #7**: Missing underscore in via names (must be `HIGHER_LOWER`, e.g., `M7_M6`).
  
  **⚠️ VALIDATION CHECK**: Before generating SKILL code, verify that:
  - ✅ All horizontal belt `cx` values use `left_vert_leftmost_x` or `right_vert_rightmost_x` with via pitch calculations
  - ✅ All vertical belt `cy` values use `y_anchor_top` or `y_anchor_bot` with via pitch calculations
  - ✅ No midpoint calculations (`(x1+x2)/2` or `(y1+y2)/2`) are used for via centers
  - ✅ All segment lengths use `i_type_frame_x_left/right`, not `half_width`

#### Validation Gate (MUST)

The generator MUST validate these conditions before running SKILL. Failure of any item requires rejecting and regenerating this round:

**1. Production-ready output**:
- [ ] SKILL text must be complete and production-ready
- [ ] No simplification language, placeholders, TODOs, or incomplete implementation indicators
- [ ] If any such content is detected, output must be rejected immediately

**2. Shield via belts completeness** (CRITICAL):
- [ ] Exactly 8 frame segments materialized as via arrays around cross openings
- [ ] Each segment has BOTH stacks (`L_top2↔L_mid` AND `L_mid↔L_bot2`)
- [ ] Total shield-belt via arrays = 16 (8 segments × 2 stacks)

**3. ⚠️⚠️⚠️ VIA GRID ALIGNMENT VALIDATION (CRITICAL — MOST COMMON ERROR) ⚠️⚠️⚠️**:
- [ ] **ALL horizontal belt `cx` values use `left_vert_leftmost_x` or `right_vert_rightmost_x` with via pitch calculations** — **NO midpoint centering** (`cx = (x1+x2)/2` is FORBIDDEN)
- [ ] **ALL vertical belt `cy` values use `y_anchor_top` or `y_anchor_bot` with via pitch calculations** — **NO midpoint centering** (`cy = (y1+y2)/2` is FORBIDDEN)
- [ ] **ALL horizontal segment lengths use `i_type_frame_x_left/right`** — **NOT `half_width`** (`len = h_opening_x1 - (-half_width)` is FORBIDDEN)
- [ ] **NO midpoint calculations** (`(x1+x2)/2` or `(y1+y2)/2`) are used anywhere for via centers
- [ ] **All via centers are computed from grid anchors** using via pitch calculations, ensuring proper alignment

**3. I-Type layer vias completeness** (CRITICAL):
- [ ] L_top↔L_top2: 4 frame segments + 1 bottom strip = 5 arrays
- [ ] L_bot2↔L_bot: 4 frame segments + 1 bottom strip = 5 arrays
- [ ] Bottom strip vias MUST be present (commonly missed)

**4. Strap vias completeness**:
- [ ] Top strap: via arrays for both layer pairs (L_top2↔L_mid and L_mid↔L_bot2)
- [ ] Bottom straps: left and right `layer_mid↔layer_bot2` strap vias with `rows_s ≥ 1` and `cols_* ≥ 1`

**5. Via count sanity check**:
- [ ] Total via arrays ≥ 29 (16 shield belts + 10 I-Type + 3 straps minimum)
- [ ] If count < 20, implementation is incomplete

**6. Via sizing validation**:
- [ ] No hardcoded cutRows=1 AND cutColumns=1 for all vias
- [ ] Via parameters computed from geometry using `via_pitch_cut` and `via_margin`

**7. Shield via belts alignment**:
- [ ] Horizontal belt centers (`cx`) aligned to vertical grids using `left_vert_leftmost_x`/`right_vert_rightmost_x`
- [ ] Vertical `cy` anchored to `y_anchor_top/bot` with `(rows−1)*0.5*pitch_cut` offsets
- [ ] No extra corner arrays (connectivity from aligned segments only)

**8. Geometry completeness**:
- [ ] All 5 layers present: L_top plate, L_top2 I-Type, L_mid cross/fingers/straps, L_bot2 I-Type, L_bot plate
- [ ] I-Type layers: complete structures (shield frame, strips, fingers, connection line) with proper net assignments
- [ ] Draw order respected, no duplication of plates (emitted exactly once at beginning)

**9. Atomic co-generation**:
- [ ] All elements in THIS script (same round), no staging across files/rounds
- [ ] All via arrays for all 4 adjacent layer pairs present

**10. Pins and labels**:
- [ ] TOP pin at (0,0) on layer_mid
- [ ] BOT pin at (0,0) on layer_bot

**REJECTION CRITERIA** (if ANY of these is true, REJECT and REGENERATE):
- ❌ **Forbidden language detected**: Any occurrence of "TODO", "placeholder", "to be implemented", "initial implementation", "for now", "simplified", "basic version", "will add later" in SKILL output or code comments
- ❌ **Shield belts absent or incomplete**: Any of the 8 segments missing, or any segment missing one of two stacks (must have exactly 16 shield belt via arrays)
- ❌ **I-Type bottom strip vias missing**: BOTH L_top↔L_top2 and L_bot2↔L_bot must have bottom strip vias
- ❌ **Insufficient via count**: Total via count < 20 (expected ≥29)
- ❌ **Hardcoded via sizing**: All vias have cutRows=1 AND cutColumns=1 (indicates no computation was done)
- ❌ **Missing geometry elements**: Any required element missing (plates, I-Type structures, cross, fingers, straps, vias, or pins)
- ❌ **No dbCreateVia statements**: SKILL file does not contain any via generation code

### Centering and pins

- Place the `TOP` pin at the geometric center `(0, 0)` on L_mid (middle layer).
- Place the `BOT` pin at the geometric center `(0, 0)` on L_bot (bottom plate).
- All layers must share the same geometric center and overall dimensions for proper alignment.

### Notes

- Numeric alignment: place the innermost finger centers exactly at the horizontal keepout boundary to realize the precise `finger_to_cross_d` edge clearance (the formula already accounts for finger width and vertical-bar width).
- Per-quadrant `fingers` controls the number of columns in that quadrant; total can be odd or even; geometry expands width accordingly.

---

## Appendix: Parameter Simplification Summary

The following parameters have been removed or consolidated to simplify the codebase while maintaining full functionality:

### Removed Parameters (no longer required as inputs):
- `i_type_frame_to_finger_d`: Not used in current implementation
- `i_type_shield_to_strip_spacing`: Not used; strip positions are computed from middle layer strap alignment
- `i_type_h_height`: Not used; finger region bounds are computed from strip positions and `i_type_spacing`
- `i_type_fingers`: Replaced by `i_type_fingers_per_side` and `i_type_fingers_middle` for better clarity
- `finger_to_cross_d`: This is a computed value (not an input), derived from I-Type middle finger span to align with middle layer core
- `strap_to_frame_d`: Unified with `frame_to_core_d` (same parameter used for both purposes)

### Key Simplifications:
1. **I-Type finger specification**: Uses `i_type_fingers_per_side` (typically 3) and `i_type_fingers_middle` (typically 4) instead of total `i_type_fingers`
2. **Strip alignment**: I-Type strip positions and width directly align with middle layer straps (computed, not input parameters)
3. **Finger alignment**: I-Type finger centers are computed from alignment with middle layer fingers (side fingers align with quadrant side fingers; middle 4 fingers span matches middle layer core width)
4. **Parameter consolidation**: `frame_to_core_d` is used for both frame-to-core spacing and strap-to-frame spacing
5. **Via array computation**: Via arrays are computed on-the-fly during rendering; Python MUST calculate `cutRows`/`cutColumns` from geometry + pitch (never hardcode them to 1×1 or any constant)

### Code Structure Improvements:
- Extracted reusable helper function for I-Type frame via arrays generation
- Removed redundant intermediate calculations from geometry dictionary
- Simplified parameter list from 19 to 14 core parameters

---

## Related Modules

- `02_Python_SKILL_Integration.md` — SKILL generation rules (flattened scripts, whitelist)
- `Technology_Configs/` — DRC minima, via sizing, quantization, and allowed layers


---

## Machine Contract (Concise)

- Inputs (required): 
  - **Layers**: `layer_top`, `layer_top2`, `layer_mid`, `layer_bot2`, `layer_bot` (5 layers)
    - **Layer order guidance**: Typically specified in descending order from top to bottom (e.g., `M7 → M6 → M5 → M4 → M3`) to match physical layer stack
    - **Low-parasitic recommendation**: When the PDK provides ≥5 metals, choose the **highest five adjacent layers** (e.g., `M7 → M6 → M5 → M4 → M3`) and avoid M1/M2 for capacitor plates
    - Layer compatibility and via definitions depend on technology file specifications
    - Users should verify layer stack compatibility with their process technology
  - **Middle layer (L_mid)**: `frame_width`, `spacing`, `middle_horizontal_width`, `middle_vertical_width`, `fingers` (per‑quadrant total), `finger_vertical_width`, `finger_d`, `strap_width`, `frame_to_core_d`, `h_height`
    - Note: `finger_to_cross_d` is computed from I-Type middle finger span (not an input).
    - Note: `strap_to_frame_d` is unified with `frame_to_core_d` (same parameter).
  - **I-Type layers (L_top2, L_bot2)**: `i_type_fingers_per_side`, `i_type_fingers_middle`, `i_type_finger_vertical_width`, `i_type_finger_d`, `i_type_frame_horizontal_width`, `i_type_frame_vertical_width`, `i_type_spacing`
    - Note: Strip positions and width align with middle layer straps (computed, not input).
    - Note: I-Type finger positions align with middle layer fingers (computed from alignment requirements).
  - **Via tech**: `via_pitch_cut`, `via_margin`
- Coordinates: origin `(0,0)` at cross center; place `TOP` pin at `(0,0)` on `layer_mid`; place `BOT` pin at `(0,0)` on `layer_bot`.
- Semantic note: `left_frame_x`/`right_frame_x` are the centerlines of the vertical frame paths (width = `frame_width`) for middle layer. Plates must use `±half_width` for their x‑extents; do not use `left_frame_x/right_frame_x` for plate rectangles. I-Type layers align with overall device boundaries.
- **Middle layer keepout**: `|x| ≥ middle_vertical_width/2 + finger_to_cross_d + finger_vertical_width/2`.
- **Middle layer columns**: `cols_per_side = fingers`; `pitch = finger_vertical_width + finger_d`; left centers `x_i = x_end − (cols_per_side−1−i)*pitch`, with `x_end = −keepout_dx_center`; right centers mirror.
- Indexing convention for rendering: left side indices iterate outer→inner; right side indices iterate inner→outer.
- **Total height**: Determined by middle layer: `h_height + 2*(spacing + strap_width + frame_to_core_d) + 2*frame_width`. All 5 layers must share the same `total_height`.
- **Middle layer straps**: `top_strap_y = top_minus_frame − frame_to_core_d − strap_width/2`; `bot_strap_y = bottom_minus_frame + frame_to_core_d + strap_width/2`.
- **Middle layer core**: `core_top_y = top_strap_y − strap_width/2 − spacing`; `core_bottom_y = bot_strap_y + strap_width/2 + spacing`.
- **Quadrant nets**: Top(odd→top strap, even→TOP bar to `core_top_y`); Bottom(odd→TOP bar to `core_bottom_y`, even→bot strap).
- **I-Type layers geometry**: Frame boundaries align with device boundaries. Strip positions align with middle layer straps (`top_strap_y`, `bot_strap_y`); strip width equals `strap_width`. Finger centers computed with consistent spacing:
  - **Left side**: Start from `left_centers[0]`, place `i_type_fingers_per_side` fingers with `i_type_pitch` spacing
  - **Middle**: Continue from last left finger, place `i_type_fingers_middle` fingers with `i_type_pitch` spacing (span matches middle layer core width via `finger_to_cross_d` adjustment)
  - **Right side**: Continue from last middle finger, place `i_type_fingers_per_side` fingers with `i_type_pitch` spacing
  - **Critical**: All fingers must maintain consistent `i_type_pitch` spacing throughout. Via positions at top/bottom strip centers and on shield frame.
- **Bottom straps via arrays**: At `(cx, bot_strap_y)` sized by `strap_width × segment_length` using `via_pitch_cut/margin` for `layer_mid ↔ layer_bot2`.
- **Shield via belts (middle layer, via‑only frame)**:
  - Split into 8 segments using `h_opening_x1/x2` and `v_opening_y1/y2` as defined above. For each segment s:
    - If s is horizontal: `rows_s = floor((i_type_frame_horizontal_width + via_margin)/via_pitch_cut)`, `cols_s = floor((length(s) + via_margin)/via_pitch_cut)`, `cy_s = y_top_mid or y_bot_mid`, and choose `cx_s` so that the column grid matches the adjacent vertical grid (`left_vert_leftmost_x/right_vert_rightmost_x`).
    - If s is vertical: `cols_s = floor((i_type_frame_vertical_width + via_margin)/via_pitch_cut)`, `rows_s = floor((length(s) + via_margin)/via_pitch_cut)`, `cx_s = i_type_leftFrameX/i_type_rightFrameX`, and **⚠️ CRITICAL**: 
      - **❌ FORBIDDEN**: `cy_s = (y_start + y_end)/2` or `cy_s = 0` or any midpoint calculation
      - **✅ REQUIRED**: 
        - Top segments: `cy_s = y_anchor_top − (rows_s−1)*0.5*pitch_cut`
        - Bottom segments: `cy_s = y_anchor_bot + (rows_s−1)*0.5*pitch_cut`
  - For each segment, emit two arrays with identical centers/counts: `layer_top2↔layer_mid` and `layer_mid↔layer_bot2`.
  - Do not emit any corner via arrays; connectivity results from the aligned segment arrays.
    - Segment length definitions (positive):
    - Horizontal segments use I-Type frame boundaries: `left_x_outer = i_type_frame_x_left`, `right_x_outer = i_type_frame_x_right`.
    - Horizontal lengths: `len_tl = h_opening_x1 − i_type_frame_x_left`, `len_tr = i_type_frame_x_right − h_opening_x2`, `len_bl = h_opening_x1 − i_type_frame_x_left`, `len_br = i_type_frame_x_right − h_opening_x2`.
    - Vertical lengths: `len_lb = v_opening_y1 − y_anchor_bot`, `len_lt = y_anchor_top − v_opening_y2`, `len_rb = v_opening_y1 − y_anchor_bot`, `len_rt = y_anchor_top − v_opening_y2`.
    - Guard: if `len_* ≤ 0`, skip that segment (no via array emitted).
  - Horizontal center formulas (alignment to vertical extremes):
    - Left segments: `cx = left_vert_leftmost_x + (cols−1)*0.5*via_pitch_cut`.
    - Right segments: `cx = right_vert_rightmost_x − (cols−1)*0.5*via_pitch_cut`.
- **Via arrays (all 4 adjacent layer pairs)**:
  - `L_top ↔ L_top2`: Connect to I-Type shield frame and bottom strip areas
  - `L_top2 ↔ L_mid`: Connect I-Type BOT network to middle-layer straps/fingers via 8-segment shield via belts (positioned at perimeter)
  - `L_mid ↔ L_bot2`: Connect middle-layer BOT network to I-Type BOT network via 8-segment shield via belts (positioned at perimeter)
  - `L_bot2 ↔ L_bot`: Connect I-Type BOT network to bottom plate
  - **Note**: Shield via belts create a "virtual shield" at the perimeter; L_mid itself has NO metal frame
- Draw order: L_top plate → L_top2 (I-Type) → L_mid (quadrant-interdigitated) → L_bot2 (I-Type) → L_bot plate → all vias → labels.
- No‑duplication: emit all plates and structures exactly once; do not re‑emit geometry later in the script.

---

## Function Contracts for Automatic Code Synthesis

This section specifies two helper components so an agent can implement them directly from the KB (no prior code dependency), mirroring the H‑shape module style.

**Note**: All geometric formulas are defined in the "Key Geometric Quantities" section above. This section provides the function interface and execution sequence.

### A) Geometry Synthesis (pure function)

- Purpose: From primary parameters, compute all derived numeric geometry needed to render the layout, independent of any CAD API.

- Required inputs (µm unless noted):
  - **Layers**: `layer_top`, `layer_top2`, `layer_mid`, `layer_bot2`, `layer_bot` (strings; used downstream only)
  - **Middle layer (L_mid)**:
    - `frame_width`
    - `spacing`
    - `middle_horizontal_width`, `middle_vertical_width`
    - `fingers` (per‑quadrant total columns; integer ≥ 1)
    - `finger_vertical_width`, `finger_d`
    - `strap_width` (required)
    - `frame_to_core_d` (used for both frame-to-core spacing and strap-to-frame spacing)
    - `h_height` (core vertical length inside straps)
    - Note: `finger_to_cross_d` is computed (not input) from I-Type middle finger span
  - **I-Type layers (L_top2, L_bot2)**:
    - `i_type_fingers_per_side` (number of fingers on each side, typically 3)
    - `i_type_fingers_middle` (number of fingers in the middle, typically 4)
    - `i_type_finger_vertical_width`, `i_type_finger_d`
    - `i_type_frame_horizontal_width`, `i_type_frame_vertical_width`
    - `i_type_spacing`
    - Note: Strip positions and width align with middle layer straps (computed from `top_strap_y`, `bot_strap_y`, `strap_width`)
    - Note: Finger centers computed from alignment with middle layer fingers
  - **Via tech**: `via_pitch_cut`, `via_margin`

- Outputs (all numbers rounded at rendering time only; geometry should keep full precision):
  - **Overall**: `total_width`, `total_height`, `half_width`, `half_height` (shared by all 5 layers)
  - **Middle layer (L_mid)**:
    - Frame/shield: `outer_top`, `outer_bottom`, `top_minus_frame`, `bottom_minus_frame`, `left_frame_x`, `right_frame_x`
    - Cross bars: `h_middle_y = 0`, `vbar_top_y`, `vbar_bottom_y`, `hbar_left_x`, `hbar_right_x`
    - Strap centers: `top_strap_y`, `bot_strap_y`
    - Core bounds: `core_top_y`, `core_bottom_y`
    - Horizontal bar clearance targets: `upper_y = h_middle_y + spacing + middle_horizontal_width/2`, `lower_y = h_middle_y − spacing − middle_horizontal_width/2`
    - Keepout: `finger_keepout_center_dx = middle_vertical_width/2 + finger_to_cross_d + finger_vertical_width/2`
    - Columns per side: `cols_per_side = fingers`, `pitch = finger_vertical_width + finger_d`
    - Finger x centers: `left_centers[]` (outer→inner), `right_centers[]` (inner→outer, mirrored — computed in a second pass)
    - Strap spans (per side): `left_outer_edge`, `left_inner_edge`, `right_inner_edge`, `right_outer_edge`
    - Via arrays (heuristic counts): `rows_h`, `cols_v`, bottom‑strap `rows_s`, `cols_s` (can be refined by the generator)
    - Shield via belt anchors and openings (MUST provide for rendering):
      - Cross openings: `h_opening_x1`, `h_opening_x2`, `v_opening_y1`, `v_opening_y2`
      - Frame-band midlines: `y_top_mid`, `y_bot_mid`
      - Vertical belt column count: `cols_v = floor((i_type_frame_vertical_width + via_margin)/via_pitch_cut)`
      - Vertical grid extremes for alignment: `left_vert_leftmost_x`, `right_vert_rightmost_x`
      - Vertical y‑anchors for pitch alignment: `y_anchor_top`, `y_anchor_bot`
  - **I-Type layers (L_top2, L_bot2)**:
    - Frame boundaries: `i_type_leftFrameX`, `i_type_rightFrameX`, `i_type_frame_inner_top`, `i_type_frame_inner_bottom`, `i_type_frame_x_left`, `i_type_frame_x_right`
    - Strip positions: `i_type_strip_top_y`, `i_type_strip_bottom_y`, `i_type_strip_width`, `i_type_strip_x_left`, `i_type_strip_x_right`
    - Finger region bounds: `i_type_h_top_y`, `i_type_h_bottom_y`
    - Frame center positions: `i_type_top_frame_y`, `i_type_bottom_frame_y`
    - Finger center x positions: `i_type_finger_centers[]` (all finger centers in order: left side + middle + right side)
    - Finger endpoints: `i_type_top_minus_frame`, `i_type_bottom_minus_frame`
    - Connection line coordinates: `i_type_bottom_strip_bottom_edge`, `i_type_bottom_frame_top_edge`
    - Note: Via arrays are computed on-the-fly during rendering (not stored in geometry dict)
  - **Computed intermediate values** (required for rendering):
    - `finger_to_cross_d` (computed from I-Type middle finger span alignment)
    - `i_type_pitch = i_type_finger_vertical_width + i_type_finger_d` (consistent spacing for all I-Type fingers)
    - Via technology parameters: `via_pitch_cut`, `via_margin` (passed through from params for via array calculations)

- **Execution sequence**: Follow the formulas in "Key Geometric Quantities" section in this order:
  1) Overall dimensions
  2) Middle layer (L_mid) vertical stack
  3) I-Type middle finger span calculation
  4) Middle layer horizontal width from columns
  5) Middle layer finger centers (⚠️ CRITICAL - TWO SEPARATE QUADRANTS - see "Key Geometric Quantities" for algorithm)
  6) Middle layer strap spans per side
  7) Middle layer cross bars
  8) I-Type layers geometry (compute before shield via belts to use I-Type frame boundaries)
  9) Middle layer shield via openings and anchors (for 8-segment belts)
  
  **Note**: All detailed formulas are provided in the "Key Geometric Quantities" section above. Refer to that section for complete calculation details.

### B) Layout Script Generation (pure rendering)

- Purpose: From the geometry dictionary and parameters, emit flattened layout commands (e.g., SKILL `dbCreatePath`/`dbCreateVia`).

- Required inputs: `params`, `geom`, `numeric_format = 5` decimals, and via naming `upper_lower` (adjacent only).

- **Drawing order and details**: Follow the "Procedural Drawing Checklist" section above for complete step-by-step instructions.

- **⚠️ CRITICAL: Via Calculation Requirements**:
  - **MANDATORY**: Via calculation MUST follow the step-by-step procedure defined in the "Shield Via Belts" section (Step 0 → Step 1 → Step 2 → Step 3a → Step 3 → Step 4).
  - **MANDATORY**: You MUST use the calculated via counts in the generated SKILL code. Do NOT calculate and then ignore them.
  - **MANDATORY**: Each segment MUST have its own viaParams. Each layer pair MUST have its own via parameters.
  - See "Cross-layer Connections (Vias)" section above for complete via requirements and warnings.

- **Production-Ready Output Requirement**:
  - Generated SKILL scripts must be complete, production-ready implementations with ALL via arrays computed and generated.
  - **ABSOLUTELY FORBIDDEN language**: "TODO", "placeholder", "to be implemented", "simplified", "will add later", "would be generated", etc.
  - **MANDATORY**: Both geometry shapes AND via arrays must be generated in the same function call.
  - See "Procedural Drawing Checklist" and "Validation Notes" sections for complete requirements.

With the above contracts and formulas, an agent can implement both functions without referencing any pre-existing code and produce the exact Sandwich capacitor specified in this module.


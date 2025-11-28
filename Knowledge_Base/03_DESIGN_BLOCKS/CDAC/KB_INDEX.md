# [IMPORTANT] Capacitor Knowledge Base Module Index — load this index first (domain: `Capacitor_KB_KB_INDEX`)

Modularized knowledge base for capacitor design automation. This index guides AI agents on how to combine knowledge modules for specific design tasks (shape type + technology node).

## Knowledge Base Architecture

**⚠️ CRITICAL: Lazy Loading Policy (Step-by-Step Loading)**

**DO NOT preload all modules at once!** Follow this loading strategy:

1. **Initial Load (Universal Modules Only)**:
   - Load the knowledge base index first
   - **⚠️ CRITICAL: Load ALL three core universal modules (00, 01, 02) - NONE can be skipped:**
     - `00_Core_Principles.md` - **REQUIRED** (core execution rules)
     - `01_Workflow_Framework.md` - **REQUIRED** (three-phase workflow)
     - `02_Python_SKILL_Integration.md` - **REQUIRED** (code generation policies)
   - These three modules are foundational and **MUST** be loaded together - they form an inseparable core
   - `04_Array_Generation.md` is also universal but only needed for Phase 3 (array generation)
   - **⚠️ CRITICAL: DO NOT load Phase 2 or Phase 3 modules during initial load**
     - **FORBIDDEN**: Loading `03_02_[SHAPE]_Dummy_Generation.md` in Phase 1
     - **FORBIDDEN**: Loading `04_Array_Generation.md` in Phase 1
     - Phase 2 and Phase 3 modules must be loaded ONLY when transitioning to their respective phases

2. **Phase 1 - Load when starting Phase 1**:
   - Structure definition modules required for this phase
   - Technology configuration modules required for this phase
   - **DO NOT load** Phase 2 or Phase 3 modules yet

3. **Phase 2 - Load when starting Phase 2**:
   - Phase 2-specific modules required for this phase
   - **DO NOT load** Phase 3 modules yet

4. **Phase 3 - Load when starting Phase 3**:
   - Phase 3-specific modules required for this phase

**Key Principle**: Load modules incrementally as you progress through the workflow steps, NOT all at once at the beginning.

```
KB_Capacitor/
│
├── 📋 Index & Guides
│   └── KB_INDEX.md                      (this file - start here)
│
├── 🔷 Universal Modules (00-02, 04)
│   ├── 00_Core_Principles.md            ┐
│   ├── 01_Workflow_Framework.md         ├─ ⚠️ ALL THREE (00, 01, 02) ARE REQUIRED
│   ├── 02_Python_SKILL_Integration.md   │   Apply to ALL shapes & technologies
│   └── 04_Array_Generation.md            ┘   (04 is optional, only for Phase 3)
│
├── 🔶 Shape-Specific Modules (03_Shape_Specifics/)
│   ├── README.md
│   └── H_Shape/
│       ├── 03_01_H_Shape_Structure.md      ┐
│       └── 03_02_H_Shape_Dummy_Generation.md ┴─ H-shape specific
│   └── [Future: U_Shape/, C_Shape/, etc.]
│
└── ⚙️  Technology Configurations (Technology_Configs/)
    ├── README.md
    ├── 180nm_Technology.md              ┐
    └── 28nm_Technology.md               ┴─ Process-specific parameters

```

### Module Dependency Flow

```
                    ┌─────────────────────────────────────┐
                    │   Technology_Configs/               │
                    │   (DRC rules, via params, metals)  │
                    └──────────────┬──────────────────────┘
                                   │
                                   ↓
┌──────────────────────────────────────────────────────────────────┐
│                   00_Core_Principles                             │
│              (Universal execution rules)                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────────────────────┐
│               01_Workflow_Framework                              │
│        (Three-phase: Unit → Dummy → Array)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────────────────────┐
│           02_Python_SKILL_Integration                           │
│        (Code generation policies & contracts)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ├──────────────────────────────────┐
                      │                                  │
                      ↓                                  ↓
        ┌────────────────────────────┐    ┌────────────────────────┐
        │ 03_Shape_Specifics/         │    │ Technology_Configs/    │
        │ [SHAPE]/                    │    │ [TECHNOLOGY]nm_        │
        │  03_01_[SHAPE]_Structure.md │◄───┤ Technology.md          │
        │        ↓                    │    └────────────────────────┘
        │  03_02_[SHAPE]_Dummy.md     │
        └────────────┬────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │  04_Array_Generation.md    │
        │  (Mosaic method)            │
        └────────────────────────────┘
```

### Module Combination Example

To design an **H-shape capacitor on 180nm**, combine:

```
┌──────────────────────────────────────────────────────────────┐
│  Universal (00-02, 04)  │  Shape (03)  │  Tech Config        │
├──────────────────────────┼──────────────┼─────────────────────┤
│ 00_Core_Principles       │              │                     │
│ 01_Workflow_Framework    │ 03_Shape_    │ Technology_180nm_   │
│ 02_Python_SKILL_Integration│ H_Shape/   │ Technology          │
│ 04_Array_Generation      │ 03_01_H_     │                     │
│                          │ Shape_       │                     │
│                          │ Structure    │                     │
│                          │ 03_02_H_     │                     │
│                          │ Shape_Dummy  │                     │
└──────────────────────────┴──────────────┴─────────────────────┘
```

## Overview

This knowledge base is organized into four main categories:
1. **Universal modules** (00-02, 04) - Apply to all capacitor shapes and technologies
2. **Shape-specific modules** (03_Shape_Specifics/) - Specific to each capacitor shape
3. **Technology configurations** (Technology_Configs/) - Process-specific parameters


## Module Combinations

To design a capacitor, combine modules based on your needs:

### For H-shape CDAC on 180nm:
```
00_Core_Principles.md
01_Workflow_Framework.md  
02_Python_SKILL_Integration.md
03_Shape_Specifics/H_Shape/03_01_H_Shape_Structure.md
03_Shape_Specifics/H_Shape/03_02_H_Shape_Dummy_Generation.md
04_Array_Generation.md
Technology_Configs/180nm_Technology.md
 
```

### For I-Type CDAC on 180nm:
```
00_Core_Principles.md
01_Workflow_Framework.md  
02_Python_SKILL_Integration.md
03_Shape_Specifics/I_Type/03_01_I_Type_Structure.md
03_Shape_Specifics/I_Type/03_02_I_Type_Dummy_Generation.md
04_Array_Generation.md
Technology_Configs/180nm_Technology.md
 
```

### For H-shape CDAC on 28nm:
```
00_Core_Principles.md
01_Workflow_Framework.md
02_Python_SKILL_Integration.md
03_Shape_Specifics/H_Shape/03_01_H_Shape_Structure.md
03_Shape_Specifics/H_Shape/03_02_H_Shape_Dummy_Generation.md
04_Array_Generation.md
Technology_Configs/28nm_Technology.md
 
```

### For I-Type CDAC on 28nm:
```
00_Core_Principles.md
01_Workflow_Framework.md
02_Python_SKILL_Integration.md
03_Shape_Specifics/I_Type/03_01_I_Type_Structure.md
03_Shape_Specifics/I_Type/03_02_I_Type_Dummy_Generation.md
04_Array_Generation.md
Technology_Configs/28nm_Technology.md
 
```

### For U-shape CDAC (example, when available):
```
00_Core_Principles.md
01_Workflow_Framework.md
02_Python_SKILL_Integration.md
03_Shape_Specifics/U_Shape/03_01_U_Shape_Structure.md
03_Shape_Specifics/U_Shape/03_02_U_Shape_Dummy_Generation.md
04_Array_Generation.md
Technology_Configs/[TECHNOLOGY]_Technology.md
 
```

## Module Structure

### Universal Modules (00-02, 04)

**⚠️ CRITICAL: Core Universal Modules (00, 01, 02) - ALL THREE ARE MANDATORY**

These three modules form an **inseparable core foundation** and **MUST be loaded together** for any capacitor design task. **NONE of them can be skipped or omitted.**

- `00_Core_Principles.md` - **REQUIRED** - Core execution rules that must be strictly enforced
- `01_Workflow_Framework.md` - **REQUIRED** - Three-phase automation workflow (Unit → Dummy → Array)
- `02_Python_SKILL_Integration.md` - **REQUIRED** - Python/SKILL integration and code generation policies

**Optional Universal Module:**
- `04_Array_Generation.md` - CDAC array generation using mosaic method (only needed for Phase 3)

**Loading Rule**: When loading universal modules, **ALWAYS load 00, 01, and 02 together**. They have interdependencies and must be present as a complete set.

### Shape-Specific Modules (03_Shape_Specifics/)
Each capacitor shape has its own subdirectory. See `03_Shape_Specifics/INDEX.md` for details.

Current shapes:
- **H_Shape/** - H-shape capacitor structure
  - `03_01_H_Shape_Structure.md` - Geometry specification and drawing procedures
  - `03_02_H_Shape_Dummy_Generation.md` - Dummy capacitor generation rules
- **I_Type/** - I-Type capacitor structure (alternating finger heights, no middle bar)
  - `03_01_I_Type_Structure.md` - Geometry specification and drawing procedures
  - `03_02_I_Type_Dummy_Generation.md` - Dummy capacitor generation rules
- **Sandwich/** - Sandwich capacitor structures (organized into two variants)
  - **Standard/** - 5-layer structure (L_top, L_top2, L_mid, L_bot2, L_bot)
    - `03_01_Sandwich_Standard_Structure.md` - Geometry specification and drawing procedures
  - **Simplified_H_Notch/** - 3-layer structure (L_top, L_mid, L_bot with H-core and vertical-frame notch)
    - `03_02_Sandwich_Simplified_H_Notch.md` - Geometry specification and drawing procedures
    - `03_03_Sandwich_Simplified_H_Notch_Dummy_Generation.md` - Dummy capacitor generation rules

Future shapes (when available):
- **U_Shape/** - U-shape capacitor structure
  - `03_01_U_Shape_Structure.md`
  - `03_02_U_Shape_Dummy_Generation.md`
- **C_Shape/** - C-shape capacitor structure
  - `03_01_C_Shape_Structure.md`
  - `03_02_C_Shape_Dummy_Generation.md`

### Technology Configurations (Technology_Configs/)
Process-specific parameters for different technology nodes. See `Technology_Configs/INDEX.md` for details.

Available technologies:
- `180nm_Technology.md` - 180nm process parameters
- `28nm_Technology.md` - 28nm process parameters

### Initial Parameters
Phase 1 cold-starts by synthesizing initial parameters from structure rules and technology constraints.

## Module Dependencies

**⚠️ CRITICAL: The core universal modules (00, 01, 02) form a mandatory dependency chain:**

```
00 (Core Principles) → 01 (Workflow) → 02 (Python/SKILL)
   ⚠️ ALL THREE MUST BE LOADED TOGETHER - NONE CAN BE SKIPPED
                                    ↓
                    03_Shape_Specifics/[SHAPE]/03_01_[SHAPE]_Structure.md ← Technology Config
                                    ↓
                    03_Shape_Specifics/[SHAPE]/03_02_[SHAPE]_Dummy_Generation.md
                                    ↓
                        04 (Array Generation) - Optional, only for Phase 3
```

**Key Points:**
- `00_Core_Principles.md` provides the foundational execution rules
- `01_Workflow_Framework.md` depends on 00 and defines the three-phase workflow
- `02_Python_SKILL_Integration.md` depends on both 00 and 01 for code generation policies
- **All three (00, 01, 02) must be loaded together** - they are interdependent and form a complete foundation
- Shape-specific modules (03) and technology configs depend on the complete 00-01-02 foundation

## Related Documents

- **03_Shape_Specifics/INDEX.md** - Index of available capacitor shapes
- **Technology_Configs/INDEX.md** - Index of available technology configurations
- **Technology_Configs/INTERFACE_SPEC.md** - Technology configuration interface contract (defines required parameters for shape-tech decoupling)

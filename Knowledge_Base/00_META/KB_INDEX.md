# Knowledge Base Index - AMS-IO-Agent

Comprehensive index of all knowledge files with detailed summaries.

---

## Knowledge Base Structure

The knowledge base is organized into the following top-level directories:

- **00_META/** - Knowledge base metadata and index files
- **01_CORE/** - Core design principles, system prompts, and SKILL programming reference
- **02_TECHNOLOGY/** - Technology-specific parameters (28nm, 180nm)
- **03_DESIGN_BLOCKS/** - Design-specific knowledge (IO Ring)
- **04_ERRORS/** - Error documentation and troubleshooting guides

---

## KB_IO_Ring - IO Pad Ring Generation

**Location:** `Knowledge_Base/03_DESIGN_BLOCKS/IO_Ring/`

### Core Documentation

**Core/structured_T28.md**
- Complete instructions for IO ring generation on 28nm process
- Intent graph file creation, device type selection, voltage domain handling
- Rules: corner device selection (PCORNER_G for digital, PCORNERA_G for analog)
- Device suffix rules (V for top/bottom, H for left/right)
- Six-step workflow: requirement analysis → intent graph validation → IO-editor confirmed build + schematic/layout SKILL generation → SKILL execution with screenshots → DRC → LVS
- Signal type mapping examples: analog IO (PDB3AC_H_G/V_G), analog power (PVDD1AC or PVDD3AC for voltage domain), analog ground (PVSS1AC or PVSS3AC)
- Available tools: validate_intent_graph, build_io_ring_confirmed_config, generate_io_ring_schematic, generate_io_ring_layout, run_il_with_screenshot, run_drc, run_lvs

**Core/structured_T180.md**
- Complete instructions for IO ring generation on 180nm process
- Similar structure to T28 version but with 180nm-specific parameters and design rules
- Technology-specific device selection and voltage domain handling

**README.md**
- Overview of IO Ring design knowledge base organization
- Directory structure and purpose

---

## KB_System - System-Level Knowledge

**Location:** `Knowledge_Base/01_CORE/KB_Agent/`

### System Prompts

**system_prompt.md**
- Main AI system prompt defining communication rules and error handling policies
- Minimize user interruption, auto-infer non-blocking information, only ask for truly blocking requirements
- Error knowledge base usage: read `04_ERRORS/` at startup, document new errors when encountered with context/cause/solution/prevention
- Focused on direct task execution and communication guidelines

---

## KB_Errors - Error Documentation

**Location:** `Knowledge_Base/04_ERRORS/`

### Error Documentation

**README.md**
- Guidelines for error documentation: file naming conventions, required content structure
- Each error document should include: description, context, root cause, solution, prevention strategies
- Purpose: enable agent to learn from past errors and avoid repeating mistakes across sessions

**import_json_error.md**
- Documents JSON import errors encountered during configuration loading
- Root cause: JSON parsing failures, incorrect file paths, malformed JSON structure
- Solutions: validate JSON syntax, check file encoding, verify path correctness

---

## KB_Technology - Technology-Specific DRC Rules

**Location:** `Knowledge_Base/02_TECHNOLOGY/`

### Technology Configurations

**T28/T28_Technology.md**
- 28nm process DRC rules
- Minimum spacing: ≥ 0.05 µm
- Minimum width: ≥ 0.05 µm
- Critical spacing: ≥ 0.1 µm (for connection points)
- Minimum area: ≥ 0.017 µm² (if applicable)
- Allowed metal layers: M1-M7
- Parameter precision guidelines

**T180/T180_Technology.md**
- 180nm process DRC rules
- Minimum spacing: ≥ 0.28 µm
- Minimum width: ≥ 0.28 µm
- Allowed metal layers: METAL1-METAL5
- Parameter precision guidelines

**README.md**
- Overview of technology-specific DRC rules
- Usage guidelines for different process nodes

---

## KB_Skill - SKILL Programming Reference

**Location:** `Knowledge_Base/01_CORE/KB_SKILL/`

**skill_knowledge.md**
- SKILL programming basics: syntax, variables, comments, data types (numbers, strings, lists)
- Essential commands for Virtuoso automation: geometry creation (dbCreatePath, dbCreateRect, dbCreateVia), cellview operations
- Code examples showing proper SKILL syntax for layout generation tasks
- Best practices for SKILL script generation and execution

---

## Summary Statistics

| Category | Location | Files | Purpose |
|----------|----------|-------|---------|
| **KB_IO_Ring** | `03_DESIGN_BLOCKS/IO_Ring/` | 3 | IO pad ring generation with JSON-based configuration and automated schematic/layout generation |
| **KB_Technology** | `02_TECHNOLOGY/` | 3 | Technology-specific DRC rules for 28nm and 180nm process nodes |
| **KB_System** | `01_CORE/KB_Agent/` | 1 | System-level prompts, communication rules, and workflow guidelines |
| **KB_Errors** | `04_ERRORS/` | 2 | Error documentation and troubleshooting guides |
| **KB_Skill** | `01_CORE/KB_SKILL/` | 1 | SKILL programming language reference for Virtuoso automation scripting |
| **Total** | - | **10 files** | Complete knowledge base for IO ring design automation |

---

## Quick Reference by Task

### For IO Ring Design

1. **Choose technology node:**
   - 28nm: Read `03_DESIGN_BLOCKS/IO_Ring/Core/structured_T28.md`
   - 180nm: Read `03_DESIGN_BLOCKS/IO_Ring/Core/structured_T180.md`

2. **Generate intent graph** based on requirements

3. **Use IO ring tools:**
   - `validate_intent_graph` - Validate configuration
   - `build_io_ring_confirmed_config` - Build `*_confirmed.json` via IO-editor confirmation flow
   - `generate_io_ring_schematic` - Generate schematic SKILL code
   - `generate_io_ring_layout` - Generate layout SKILL code
   - `run_il_with_screenshot` - Execute SKILL in Virtuoso
   - `run_drc` - Design rule check
   - `run_lvs` - Layout vs schematic verification

4. **For T28 flow, run in order:**
   - `validate_intent_graph` → `build_io_ring_confirmed_config` (`process_node="T28"`) → `generate_io_ring_schematic`/`generate_io_ring_layout` (`consume_confirmed_only=True`)

### For Technology-Specific DRC Rules

1. **Choose technology node:**
   - 28nm: Load `02_TECHNOLOGY/T28/T28_Technology.md`
   - 180nm: Load `02_TECHNOLOGY/T180/T180_Technology.md`

2. **Validate designs:**
   - Check minimum spacing requirements
   - Check minimum width requirements
   - Verify metal layer usage
   - Ensure DRC compliance before finalizing layouts

### For SKILL Programming

1. Consult `01_CORE/KB_SKILL/skill_knowledge.md` for basic syntax
2. Use geometry creation commands for Virtuoso automation
3. Follow established patterns for layout generation
4. Reference technology-specific DRC rules from `02_TECHNOLOGY/`

### For Error Resolution

1. Read `04_ERRORS/README.md` for documentation guidelines
2. Search `04_ERRORS/` for similar past errors
3. Document new errors with context, cause, solution, prevention
4. Use error knowledge to avoid repeating past mistakes

### For System Configuration

1. Review `01_CORE/KB_Agent/system_prompt.md` for communication rules
2. Understand error handling policies
3. Follow workflow guidelines for task execution

---

## Knowledge Base Loading Strategy

When using the knowledge loader tool:

1. **Load by category:**
   - `IO_Ring` - Load IO ring design knowledge
   - `KB_Agent` - Load system prompts and communication rules
   - `KB_SKILL` - Load SKILL programming reference
   - `Errors` - Load error documentation

2. **Load by technology:**
   - `Tech_28nm` - 28nm process DRC rules
   - `Tech_180nm` - 180nm process DRC rules

3. **Load specific modules:**
   - Use knowledge loader tool to load specific markdown files as needed
   - Files are loaded on-demand for efficient memory usage

---

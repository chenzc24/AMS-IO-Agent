# Error: Failed to open destination cellView for CDAC array - C_CDAC_6fF_gpt_8bit_1/layout

**Context**: Phase 3 CDAC array generation, SKILL script execution using run_il_with_screenshot.
**Root cause**: Error message indicates destination cellView 'LLM_Layout_Design/C_CDAC_6fF_gpt_8bit_1/layout' could not be opened.
Likely causes:
- Library 'LLM_Layout_Design' does not exist in Virtuoso
- Master cell 'C_DUMMY_6fF' or 'C_MAIN_6fF' does not exist or lacks a valid 'layout' view
- Master layout views may be missing due to skipping unit/dummy generation

**Solution**:
- Ensure library and all master cells ('C_MAIN_6fF', 'C_DUMMY_6fF') with 'layout' views exist and are valid before attempting array generation using mosaic.
- Do not skip master cell creation if array execution is required.

**Prevention**:
- When skipping unit/dummy generation, always verify or explicitly create the required master layout views as a precondition.
- Add a pre-check before array SKILL execution to confirm the existence of source library and master cell views.

**Error log timestamp**: 20251118_213858

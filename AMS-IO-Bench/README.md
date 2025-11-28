# AMS-IO-Bench: IO Ring Generation Benchmark

A comprehensive benchmark dataset for automated IC IO ring generation using LLMs in Cadence Virtuoso.

## Quick Stats

| **Metric** | **Value** |
|------------|-----------|
| **Total Cases** | 60 |
| **Tech Nodes** | 28nm, 180nm |
| **Pad Configs** | 3×3 to 18×18 |
| **Ring Types** | Single, Double |
| **Signal Types** | Digital, Analog, Mixed, Multi-Domain |

## Structure

```
AMS-IO-Bench/
├── 28nm_wirebonding/       # 30 test cases for 28nm
├── 180nm_wirebonding/      # 30 test cases for 180nm
└── README.md
```

## Test Categories

### Basic (3×3 to 7×7)
- **Single Ring Digital** (5 cases): Digital IO only
- **Single Ring Analog** (5 cases): Analog signals only
- **Single Ring Mixed** (5 cases): Analog + Digital

### Advanced (8×8 to 18×18)
- **Double Ring** (4 cases): Inner ring pads for power/signal isolation
- **Multi-Voltage Domain** (11 cases): Multiple independent power domains

## File Naming

```
IO_[tech]_[config].txt

Examples:
- IO_28nm_3x3_single_ring_digital.txt
- IO_180nm_8x8_double_ring_mixed.txt
- IO_28nm_12x12_double_ring_multi_voltage_domain_1.txt
```

## File Format

Each file contains structured prompt with clear sections:

```
IO_28nm_3x3_single_ring_analog: |
Task: Generate IO ring schematic and layout design for Cadence Virtuoso.

  Design requirements:
  3 pads per side. Single ring layout. Counterclockwise ordering.

  ======================================================================
  SIGNAL CONFIGURATION
  ======================================================================
  Signal names: [pin list]

  ======================================================================
  VOLTAGE DOMAIN CONFIGURATION
  ======================================================================
  Voltage domain requirements: [domain mappings]

  ======================================================================
  DESIGN CONFIGURATION
  ======================================================================
  Configuration:
  - Technology: 28nm process node
  - Library: LLM_Layout_Design
  - Cell name: IO_RING_3x3_single_ring_analog
  - View: schematic and layout
```

## Usage

```bash
# Single test case
python src/main.py --prompt-file AMS-IO-Bench/28nm_wirebonding/IO_28nm_3x3_single_ring_digital.txt

# Batch experiments
python run_io_ring_batch.py --tech-node 28nm --model claude
python run_io_ring_batch.py --tech-node 180nm --model gpt4
```

## Complexity Levels

| **Level** | **Pads** | **Ring** | **Domains** | **Example** |
|-----------|----------|----------|-------------|-------------|
| Basic | 3×3-5×5 | Single | 1 | IO_28nm_3x3_single_ring_digital |
| Intermediate | 6×6-8×8 | Single/Double | 2-3 | IO_28nm_8x8_double_ring_mixed |
| Advanced | 10×10-12×12 | Double | 4-6 | IO_28nm_12x12_double_ring_multi_voltage_domain_1 |
| Expert | 12×18-18×18 | Double | 6+ | IO_28nm_18x18_double_ring_multi_voltage_domain |

## Voltage Domains

| **Domain** | **Purpose** |
|------------|-------------|
| VIOL/GIOL/VIOH/GIOH | Digital IO |
| AVDD/AVSS | Analog power |
| VDDIB/VSSIB | Analog bias |
| VDD_CKB/VSS_CKB | Clock domain |
| VDD_DAT/VSS_DAT | Data path |
| VREFH/VREFN | Reference voltage |
| VDD_ADC/VSS_ADC | ADC domain |
| VDD_DAC/VSS_DAC | DAC domain |

## Benchmark Metrics

Evaluate LLM performance on:
1. **Correctness** - Accurate generation
2. **Completeness** - All signals connected
3. **DRC/LVS Clean** - No violations
4. **Domain Isolation** - Proper separation
5. **Pad Ordering** - Correct sequence
6. **Efficiency** - Time and iterations

## Design Features

- **Pad Order:** Counterclockwise (Left → Bottom → Right → Top)
- **Inner Ring Pads:** Power/bias/signal distribution (double ring only)
- **Special Pads:** VREF_CORE, VAMP_CORE, IBIAS_CORE, D[n]_CORE

## Version

**v1.0** (2025-11-22) - Initial release with 60 test cases

---

**Dataset:** 60 cases | **Tech:** 28nm/180nm | **License:** AMS-IO-Agent Project

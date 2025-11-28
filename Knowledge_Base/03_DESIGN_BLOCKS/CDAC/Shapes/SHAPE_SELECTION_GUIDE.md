# Capacitor Shape Selection Guide

## Overview

This guide helps select the appropriate capacitor shape based on design requirements and constraints. Each shape has distinct characteristics that make it suitable for specific applications.

---

## Available Shapes

### H-Shape Capacitor
**Structure**: Vertical fingers + middle horizontal bar + outer frame  
**Finger count**: Odd (≥3)  
**Via topology**: 3 rows (top, middle, bottom)

**Best for:**
- Traditional interdigitated structures
- When odd finger counts are required or preferred
- Applications requiring middle bar connection for electrical symmetry
- Standard multi-layer capacitor designs

**Characteristics:**
- ✅ Well-established structure with predictable behavior
- ✅ Good mechanical symmetry with middle connection
- ✅ Three via rows provide robust connections
- ⚠️  More complex via structure than I-Type
- ⚠️  Requires odd finger count (less flexible)

---

### I-Type Capacitor
**Structure**: Alternating-height vertical fingers (no middle bar) + top/bottom strips  
**Finger count**: Even (≥2)  
**Via topology**: 2 rows (top, bottom only)

**Best for:**
- Simpler via topology requirements
- When even finger counts are needed
- Minimal metal usage designs
- Applications where middle bar is unnecessary

**Characteristics:**
- ✅ Simpler via structure (2 rows vs 3)
- ✅ More flexible finger counts (accepts even)
- ✅ Reduced metal usage (no middle bar)
- ✅ Interdigitation through alternating finger heights
- ⚠️  No middle horizontal connection
- ⚠️  Different field distribution compared to H-shape

**When to choose I-Type over H-Shape:**
- Need even finger counts
- Prefer simpler via arrangement
- Want to minimize metal layers/usage
- Middle bar connection not required

---

### Sandwich Capacitor
**Structure**: Tri-layer structure with solid plates on top/bottom + middle layer with frame and interdigitated core  
**Finger count**: Flexible (depends on middle layer core structure)  
**Via topology**: BOT vias only (no vias on TOP fingers)

**Best for:**
- **Low parasitic to ground** (PRIMARY USE CASE)
- Applications requiring minimal substrate coupling
- High-frequency designs where ground parasitics matter
- Designs where parasitic capacitance must be tightly controlled

**Characteristics:**
- ✅ **Significantly reduced parasitic capacitance to substrate**
- ✅ Solid top/bottom plates provide shielding
- ✅ Better isolation from substrate noise
- ✅ Improved Q-factor in RF applications
- ✅ More predictable parasitic behavior
- ⚠️  More complex structure (three distinct layers)
- ⚠️  Requires careful layer assignment
- ⚠️  Different via arrangement (BOT only)

**When to choose Sandwich:**
- **Low parasitic to ground is critical**
- High-frequency RF applications
- ADC/DAC designs requiring precise capacitance
- Substrate noise isolation needed
- Ground coupling must be minimized

**Technology considerations:**
- Avoid using M1 as capacitor plates (high ground parasitics)
- Prefer mid-to-upper metal layers (M2-M7)
- Ensure layers are adjacent pairs

---

## Selection Decision Tree

```
START: What is your primary requirement?

├─ Low parasitic to ground?
│  └─ YES → **Sandwich Capacitor**
│
├─ Odd finger count required?
│  └─ YES → **H-Shape Capacitor**
│
├─ Even finger count preferred?
│  └─ YES → **I-Type Capacitor**
│
├─ Simplest via topology?
│  └─ YES → **I-Type Capacitor**
│
└─ Standard/traditional structure?
   └─ YES → **H-Shape Capacitor**
```

---

## Comparison Table

| Criterion | H-Shape | I-Type | Sandwich |
|-----------|---------|--------|----------|
| **Finger count** | Odd (≥3) | Even (≥2) | Flexible |
| **Via rows** | 3 (T+M+B) | 2 (T+B) | BOT only |
| **Middle bar** | Yes | No | Frame only |
| **Parasitic to ground** | Standard | Standard | **Lowest** |
| **Structural complexity** | Medium | Low | **High** |
| **Metal usage** | Higher | Lower | Highest |
| **Best for RF** | Good | Good | **Excellent** |
| **Design maturity** | ✅ Established | ✅ Established | ✅ Established |

---

## Technology-Specific Considerations

### For 28nm and Advanced Nodes
- Metal layer restrictions more stringent
- DRC minima tighter (≥0.05 µm typical)
- Via pitch smaller (~0.13 µm)
- **Low-parasitic requirement → strongly prefer Sandwich or avoid M1**

### For 180nm and Larger Nodes
- More relaxed DRC rules
- Larger via pitch
- All shapes viable
- **Sandwich still preferred for low-parasitic applications**

---

## Common Use Cases

### ADC/DAC Capacitor Arrays (CDAC)
**Recommended**: **Sandwich** (for low parasitics) or **H-Shape** (traditional)  
**Why**: Parasitic matching critical; Sandwich provides best isolation

### RF Tuning Capacitors
**Recommended**: **Sandwich** (best Q-factor) or **I-Type** (simpler)  
**Why**: Low substrate coupling improves Q; simpler structures easier to model

### General Analog Capacitors
**Recommended**: **H-Shape** (standard) or **I-Type** (flexible)  
**Why**: Well-established; easier to integrate

### High-Density Arrays
**Recommended**: **I-Type**  
**Why**: Lower metal usage; simpler via structure aids dense packing

---

## Migration Path

If you need to switch shapes during design:

**H-Shape ↔ I-Type**:
- Adjust finger count parity
- Remove/add middle bar
- Update via row count

**Any Shape → Sandwich**:
- Significant structure change
- Re-evaluate all parameters
- Expect different capacitance per unit area

---

## Key Takeaways

1. **For low parasitic to ground**: Use **Sandwich Capacitor** (primary advantage)
2. **For odd finger counts**: Use **H-Shape**
3. **For even finger counts**: Use **I-Type**
4. **For simplest via topology**: Use **I-Type**
5. **For RF/high-frequency**: Prefer **Sandwich** (lowest parasitics, best Q)
6. **For standard applications**: **H-Shape** is well-established and reliable

---

## Related Documents

- **H_Shape/03_01_H_Shape_Structure.md** - H-shape structure specification
- **I_Type/03_01_I_Type_Structure.md** - I-Type structure specification
- **Sandwich/Standard/03_01_Sandwich_Standard_Structure.md** - Sandwich standard structure (5-layer)
- **Sandwich/Simplified_H_Notch/03_02_Sandwich_Simplified_H_Notch.md** - Sandwich simplified H-Notch variant (3-layer)
- **Technology_Configs/** - Technology-specific constraints for each shape



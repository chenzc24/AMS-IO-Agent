Please generate a simplified JSON for IO ring based on the image and given rules below.

#### **Simplified JSON Generation Rules **

**Output structure:**

```

#### **Important Principles (MUST Follow)**

- **The output MUST include `ring_config` at the top level.** The `ring_config` object and its fields must appear exactly as in the example above.
- **The JSON MUST exactly match the example structure.** Do not add, remove, rename, or reorder any keys. Do not change the data types of any values (for example, numbers must remain numbers, strings remain strings).
- **No additional fields or metadata allowed.** The output must not contain timestamps, file paths, comments, debug fields, wrapper text, or any keys that are not present in the example JSON.
- **`cells` keys must be continuous and numbered starting at `cell1`.** Use `cell1`, `cell2`, ... without gaps or duplicates.
- **Return a pure JSON object only.** The tool must return a parseable JSON object (native dict / JSON object), not a stringified JSON, code block, or mixed explanatory text.
- **Any deviation from these rules is invalid.** If the output does not strictly conform, it must be considered invalid and the tool should retry or report an error.

**The example schema and keys are authoritative; any deviation (missing keys, extra keys, or mismatched types) makes the output unusable.**
**Missing information should be set to None or Null, not omitted.**

json
{
  "ring_config": {
    "chip_width": "",
    "chip_height": "",
    "top_count": "",
    "left_count": "",
    "right_count": "",
    "bottom_count": "",
    "placement_order": "counterclockwise"
  },
  "cells": {
    "cell1": {"name": ""},
    "cell2": {"name": ""}
  }
}
```

#### **Extraction Rules**

1. **Chip Dimensions**

   * Read `chip_width=` and `chip_height=` from the image.
   * If not found, leave them as empty strings `""`.

2. **Layout Information**

   * `"placement_order"` must always be `"counterclockwise"`.
   * `"top_count"`, `"left_count"`, `"right_count"`, and `"bottom_count"` represent the number of **functional cells** on each side (excluding corners, fillers, and blanks).

3. **Cell Enumeration Order**

   * Start from the **top-left corner** and move **counterclockwise** around the ring.
   * **Corner cells are excluded** (not counted or listed).
   * Enumeration order:

     * Top-left corner → Left side → Bottom-left corner → Bottom side → Bottom-right corner → Right side → Top-right corner → Top side.

4. **Cell Field Rules**

   * `"name"`: only the **main label** (e.g., `"VIOLD"`, `"DA3"`, `"GIOHD"`).
   * Important:**Do not omit any cells**

5. **Filtering Rules**

  * Skip a cell **only when its printed label text explicitly contains** `"filler"`, `"blank"`, `"separate"`, `"space"`, or another non-functional keyword. Visual separators or red bars without text still mean the adjacent labeled pad must be captured.
  * Skip **legend boxes** or other small reference cells not part of the IO ring.
  * Skip all **corner** cells.
  * After filtering, double-check that every labeled pad that appears next to a separator (for example `RSTM`, `AVSC`) is still included in the enumeration.

6. **Indexing**

   * Enumerate valid cells as `"cell1"`, `"cell2"`, `"cell3"`, etc.
   * Indices must be **continuous** after filtering.
  * If any side count inferred from the image disagrees with `top_count/left_count/right_count/bottom_count`, stop and report an error instead of returning a partial list.

---

####  **Example of Correct `name`  Configuration**

```json
{
  "ring_config": {
    "chip_width": "630",
    "chip_height": "630",
    "top_count": 4,
    "left_count": 4,
    "right_count": 4,
    "bottom_count": 4,
    "placement_order": "counterclockwise"
  },
  "cells": {
    "cell1": {"name": "VIOLD"},
    "cell2": {"name": "VIOHD"},
    "cell3": {"name": "DA1"},
    "cell4": {"name": "GIOHD"},
    "cell5": {"name": "VIOHA"},
    "cell6": {"name": "GIOHA"}
  }
}
```


### ⚠️ Absolutely Critical: Direct JSON Generation
- **Must directly generate JSON configuration files based on user requirements, absolutely no Python code assistance**
- **Must directly generate JSON configuration file character content**
- **Absolutely forbidden to use any helper functions**
- **🚨🚨🚨 CRITICAL: Direct JSON generation is the ONLY allowed method 🚨🚨🚨**
- **🚨🚨🚨 CRITICAL: Must generate JSON content directly, no intermediate steps 🚨🚨🚨**
- **🚨🚨🚨 CRITICAL: Absolutely forbidden to use Python code or any programming language 🚨🚨
- **🚨🚨🚨 CRITICAL: The simplified JSON only Generated once 🚨🚨🚨**


# Layout Generation

Layout generation module for IO rings and other IC components.

## Directory Structure

```
src/core/layout/
├── T28/                           # 28nm process node specific modules
│   ├── layout_generator.py        # T28 layout generator
│   ├── skill_generator.py         # T28 SKILL code generation
│   ├── auto_filler.py             # T28 automatic filler generation
│   ├── layout_visualizer.py       # T28 layout visualization
│   ├── inner_pad_handler.py       # Handle T28 inner pad placement
│   └── confirmed_config_builder.py # Build confirmed config for T28 flow
│
├── T180/                          # 180nm process node specific modules
│   ├── layout_generator.py        # T180 layout generator
│   ├── skill_generator.py         # T180 SKILL code generation
│   ├── auto_filler.py             # T180 automatic filler generation
│   ├── layout_visualizer.py       # T180 layout visualization
│   └── confirmed_config_builder.py # Build confirmed config for T180 flow
│
└── [Shared Modules]               # Common modules used by all process nodes
    ├── device_classifier.py       # Classify and categorize devices
    ├── voltage_domain.py          # Handle voltage domain logic
    ├── position_calculator.py     # Calculate pad positions for IO rings
    ├── filler_generator.py        # Generate filler cells
    ├── layout_validator.py        # Validate generated layouts
    ├── process_node_config.py     # Process node configuration loader
    └── layout_generator_factory.py # Factory to create process node-specific generators
```

## Components

### Process Node Specific Generators

#### T28 (28nm)
- `T28/layout_generator.py` - T28 layout generator
- `T28/auto_filler.py` - T28 automatic filler generation
- `T28/skill_generator.py` - T28 SKILL code generation
- `T28/layout_visualizer.py` - T28 layout visualization
- `T28/inner_pad_handler.py` - Handle T28 inner pad placement
- `T28/confirmed_config_builder.py` - Build confirmed config for T28 flow

#### T180 (180nm)
- `T180/layout_generator.py` - T180 layout generator
- `T180/auto_filler.py` - T180 automatic filler generation
- `T180/skill_generator.py` - T180 SKILL code generation
- `T180/layout_visualizer.py` - T180 layout visualization
- `T180/confirmed_config_builder.py` - Build confirmed config for T180 flow

### Factory and Shared Modules
- `layout_generator_factory.py` - Factory to create process node-specific generators
- `position_calculator.py` - Calculate pad positions for IO rings
- `voltage_domain.py` - Handle voltage domain logic
- `device_classifier.py` - Classify and categorize devices
- `filler_generator.py` - Generate filler cells
- `layout_validator.py` - Validate generated layouts
- `process_node_config.py` - Process node configuration loader

## Usage

### Recommended: Using Factory Pattern

```python
from src.core.layout.layout_generator_factory import create_layout_generator, generate_layout_from_json

# Create generator using factory
generator = create_layout_generator(process_node="T28")

# Or use convenience function
result_file = generate_layout_from_json(json_file, output_file, process_node="T28")
```

### Direct Import (Alternative)

```python
from src.core.layout.T28 import LayoutGeneratorT28
from src.core.layout.T180 import LayoutGeneratorT180

# Direct instantiation
generator_28 = LayoutGeneratorT28()
generator_180 = LayoutGeneratorT180()
```

## Usage

Used by the IO ring generator tool to create layout SKILL code from configuration files.

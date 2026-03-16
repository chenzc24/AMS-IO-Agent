# Skills Migration Plan: MCP/RAG to Modern Advanced Skills Paradigm

**Date:** 2026-03-14
**Project:** AMS-IO-Agent
**Author:** Claude (assisted)

---

## Executive Summary

This document outlines a comprehensive migration strategy to transform the AMS-IO-Agent's current MCP/RAG-based knowledge system into a modern advanced skills paradigm compatible with contemporary AI agent frameworks (e.g., Agent SDK, MCP servers).

---

## Current Architecture Analysis

### Existing Components

| Component | Technology | Purpose | Status |
|-----------|------------|---------|---------|
| **Knowledge_Base/** | Markdown files | RAG-based knowledge storage |
| **knowledge_loader_tool.py** | Dynamic knowledge loading | On-demand file discovery |
| **tools_config.yaml** | Tool configuration | YAML-based tool registration |
| **src/tools/** | 20+ Python tools | EDA and workflow tools |
| **smolagents** | Hugging Face framework | Agent orchestration |
| **Custom Tool System** | @tool decorator | Tool registration mechanism |

### Knowledge Base Structure

```
Knowledge_Base/
├── 00_META/           # Metadata and index
├── 01_CORE/           # Core principles, SKILL reference
├── 02_TECHNOLOGY/    # T28 (28nm), T180 (180nm) specs
├── 03_DESIGN_BLOCKS/  # IO Ring design knowledge
└── 04_ERRORS/          # Error documentation
```

### Key Limitations of Current Approach

1. **Tight Coupling**: Knowledge loading is tightly coupled to the smolagents framework
2. **Limited Tool Discovery**: Manual tool registration in `tools_config.yaml`
3. **No Skill Versioning**: Knowledge files lack version control
4. **Static Knowledge Base**: No dynamic knowledge updates during runtime
5. **No MCP Integration**: Not compatible with Model Context Protocol servers
6. **Limited Composability**: Tools cannot be easily combined or chained

---

## Target Architecture: Modern Advanced Skills Paradigm

### Vision

Transform the system into a **skill-based architecture** where:

1. **Skills are composable, versioned, and independently deployable**
2. **Knowledge is embedded within skills** (self-contained packages)
3. **MCP-compatible** for cross-framework interoperability
4. **Tool Runner integration** for automatic orchestration
5. **Structured outputs** for reliable AI interaction

### Key Changes

| Aspect | Current | Target |
|---------|----------|---------|
| **Knowledge Storage** | Markdown files in Knowledge_Base/ | Embedded in skill packages (Python modules + docs) |
| **Tool Registration** | Manual YAML config | Auto-discovery via decorators/folder scanning |
| **Loading Mechanism** | knowledge_loader_tool | Skill registry with dependency resolution |
| **Versioning** | None | Semantic versioning per skill |
| **Runtime Updates** | Refresh index only | Hot-reload of skill packages |
| **Interoperability** | smolagents-only | MCP + Agent SDK + others |

---

## Migration Roadmap

### Phase 1: Foundation (Week 1-2)

#### 1.1 Design Skill Package Structure

```
skills/
├── core/                      # Core infrastructure skills
│   ├── __init__.py
│   ├── base_skill.py          # Base skill class
│   ├── skill_registry.py       # Skill discovery & loading
│   └── skill_metadata.py       # Skill metadata schema
├── io_ring/                    # IO Ring design skills
│   ├── __init__.py
│   ├── t180_designer.py        # T180 IO ring generation
│   ├── t28_designer.py         # T28 IO ring generation
│   ├── validator.py             # Configuration validation
│   ├── metadata.yaml            # Skill metadata
│   └── knowledge/              # Embedded knowledge
│       ├── core_principles.md
│       ├── device_tables.md
│       └── workflows.md
├── virtuoso/                  # Virtuoso integration skills
│   ├── __init__.py
│   ├── skill_runner.py         # SKILL execution
│   ├── screenshot_tool.py       # Window capture
│   └── metadata.yaml
├── verification/                # DRC/LVS/PEX verification
│   ├── __init__.py
│   ├── drc_runner.py
│   ├── lvs_runner.py
│   ├── pex_runner.py
│   └── metadata.yaml
└── utils/                      # Utility skills
    ├── knowledge_search.py
    ├── health_check.py
    └── error_recovery.py
```

#### 1.2 Implement Base Skill Class

**File:** `skills/core/base_skill.py`

```python
"""
Base skill class for all AMS-IO skills.
Provides common functionality: metadata, versioning, validation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import importlib.metadata

class SkillVersion(Enum):
    """Semantic versioning for skills"""
    MAJOR = "major"    # Breaking changes
    MINOR = "minor"    # New features, backward compatible
    PATCH = "patch"    # Bug fixes only

@dataclass
class SkillMetadata:
    """Metadata schema for all skills"""
    name: str                           # Skill identifier
    display_name: str                     # Human-readable name
    version: str                          # Semantic version (e.g., "1.2.0")
    description: str                       # What the skill does
    author: str                           # Creator/maintainer
    dependencies: List[str]                 # Other skills required
    category: str                          # Category: "io_ring", "virtuoso", etc.
    tags: List[str]                        # Search tags
    compatible_frameworks: List[str]          # "mcp", "agent_sdk", "smolagents"
    knowledge_files: List[str]               # Embedded knowledge file paths

class BaseSkill(ABC):
    """
    Abstract base class for all skills.

    Provides:
    - Metadata discovery
    - Tool registration
    - Knowledge embedding
    - Validation hooks
    """

    def __init__(self):
        self._tools = {}
        self._knowledge = {}
        self._metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """Return skill metadata"""
        pass

    @abstractmethod
    def register_tools(self) -> Dict[str, callable]:
        """Register all tools provided by this skill"""
        pass

    def load_knowledge(self) -> Dict[str, str]:
        """Load embedded knowledge files"""
        knowledge = {}
        for file_path in self._metadata.knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    name = Path(file_path).stem
                    knowledge[name] = content
            except FileNotFoundError:
                continue
        return knowledge

    def validate_dependencies(self, available_skills: Dict[str, 'BaseSkill']) -> bool:
        """Check if all dependencies are available"""
        for dep in self._metadata.dependencies:
            if dep not in available_skills:
                return False
        return True

    def initialize(self, available_skills: Dict[str, 'BaseSkill']) -> bool:
        """Initialize the skill"""
        if not self.validate_dependencies(available_skills):
            raise RuntimeError(f"Missing dependencies: {self._metadata.dependencies}")

        self._tools = self.register_tools()
        self._knowledge = self.load_knowledge()
        return True
```

#### 1.3 Create Skill Registry

**File:** `skills/core/skill_registry.py`

```python
"""
Skill registry for dynamic discovery and loading.
Supports hot-reload and dependency resolution.
"""
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional
from core.base_skill import BaseSkill, SkillMetadata

class SkillRegistry:
    """
    Registry for all loaded skills.

    Features:
    - Auto-discovery from skills/ directory
    - Dependency resolution
    - Hot-reload support
    - Version conflict detection
    """

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self._skills: Dict[str, BaseSkill] = {}
        self._metadata: Dict[str, SkillMetadata] = {}

    def discover_skills(self) -> List[SkillMetadata]:
        """Discover all skills in skills directory"""
        discovered = []

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue

            # Look for metadata.yaml
            metadata_file = skill_dir / "metadata.yaml"
            if metadata_file.exists():
                import yaml
                with open(metadata_file) as f:
                    metadata = SkillMetadata(**yaml.safe_load(f))
                discovered.append(metadata)

        return discovered

    def load_skill(self, skill_name: str) -> BaseSkill:
        """Load a specific skill by name"""
        if skill_name in self._skills:
            return self._skills[skill_name]

        # Dynamic import
        skill_module = importlib.import_module(f"skills.{skill_name}")
        skill_class = getattr(skill_module, "Skill", None)

        if skill_class is None:
            raise ImportError(f"Skill {skill_name} not found")

        skill = skill_class()
        self._skills[skill_name] = skill
        self._metadata[skill_name] = skill.get_metadata()
        return skill

    def load_all(self) -> Dict[str, BaseSkill]:
        """Load all discoverable skills with dependency resolution"""
        discovered = self.discover_skills()

        # Topological sort by dependencies
        sorted_skills = self._resolve_dependencies(discovered)

        # Load in dependency order
        for skill_name in sorted_skills:
            try:
                self.load_skill(skill_name)
            except Exception as e:
                print(f"Failed to load skill {skill_name}: {e}")

        return self._skills

    def _resolve_dependencies(self, skills_metadata: List[SkillMetadata]) -> List[str]:
        """Topological sort for dependency resolution"""
        # Build dependency graph
        graph = {m.name: m.dependencies for m in skills_metadata}

        # Topological sort (Kahn's algorithm)
        result = []
        in_degree = {m.name: len(m.dependencies) for m in skills_metadata}
        queue = [name for name, deps in in_degree.items() if deps == 0]

        while queue:
            node = queue.pop(0)
            result.append(node)

            for dependent, deps in graph.items():
                if node in deps:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        if len(result) != len(skills_metadata):
            raise RuntimeError("Circular dependency detected in skills")

        return result

    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Get loaded skill by name"""
        return self._skills.get(skill_name)

    def list_skills(self) -> Dict[str, SkillMetadata]:
        """List all loaded skills with metadata"""
        return self._metadata

    def reload_skill(self, skill_name: str):
        """Hot-reload a specific skill"""
        if skill_name not in self._skills:
            return False

        # Remove from registry
        del self._skills[skill_name]
        del self._metadata[skill_name]

        # Re-import and load
        import importlib
        module_name = f"skills.{skill_name}"
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])

        return self.load_skill(skill_name)
```

---

### Phase 2: Core Skills Migration (Week 3-4)

#### 2.1 IO Ring Designer Skill

**File:** `skills/io_ring/t180_designer.py`

```python
"""
T180 IO Ring Design Skill
Migrates from Knowledge_Base/03_DESIGN_BLOCKS/IO_Ring/Core/structured_T180.md
"""
from core.base_skill import BaseSkill, SkillMetadata, SkillVersion
from typing import Dict, Any, Optional
import json
from pathlib import Path

class T180IO_RingDesignerSkill(BaseSkill):
    """
    T180 IO Ring generation skill.

    Migrates functionality from structured_T180.md knowledge base.
    Provides tool-based access to IO ring configuration,
    schematic generation, and layout generation.
    """

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="t180_io_ring_designer",
            display_name="T180 IO Ring Designer",
            version="1.0.0",
            description="Generate IO pad ring schematics and layouts for T180 process",
            author="AMS-IO-Agent Team",
            dependencies=[],
            category="io_ring",
            tags=["io_ring", "t180", "180nm", "schematic", "layout"],
            compatible_frameworks=["mcp", "agent_sdk", "smolagents"],
            knowledge_files=[
                "knowledge/core_principles.md",
                "knowledge/device_tables.md",
                "knowledge/workflows.md"
            ]
        )

    def register_tools(self) -> Dict[str, callable]:
        """Register all IO ring tools"""
        return {
            "analyze_t180_requirements": self.analyze_requirements,
            "generate_t180_config": self.generate_config,
            "validate_t180_config": self.validate_config,
            "build_t180_confirmed_config": self.build_confirmed_config,
            "generate_t180_schematic": self.generate_schematic,
            "generate_t180_layout": self.generate_layout,
        }

    def analyze_requirements(self, user_input: str, image_path: Optional[str] = None) -> str:
        """Analyze user requirements for IO ring design"""
        # Implementation migrated from structured_T180.md Step 1
        if image_path:
            # Call image analysis skill
            from skills.virtuoso import ImageAnalysisSkill
            analyzer = ImageAnalysisSkill()
            return analyzer.analyze_layout(image_path)

        # Text-based analysis
        return self._parse_text_requirements(user_input)

    def generate_config(self, requirements: Dict[str, Any]) -> str:
        """Generate JSON configuration from requirements"""
        # Implementation migrated from structured_T180.md Step 2
        pass

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against T180 rules"""
        # Implementation migrated from structured_T180.md Step 3
        pass

    def build_confirmed_config(self, config_path: str) -> str:
        """Build confirmed config with editor review"""
        # Implementation migrated from structured_T180.md Step 4
        pass

    def generate_schematic(self, config: Dict[str, Any]) -> str:
        """Generate T180 schematic SKILL code"""
        # Implementation migrated from structured_T180.md Step 5
        pass

    def generate_layout(self, config: Dict[str, Any]) -> str:
        """Generate T180 layout SKILL code"""
        # Implementation migrated from structured_T180.md Step 5
        pass

    def _parse_text_requirements(self, text: str) -> Dict[str, Any]:
        """Parse text-based user requirements"""
        # Extract signals, domains, constraints
        pass
```

#### 2.2 Virtuoso Integration Skill

**File:** `skills/virtuoso/skill_runner.py`

```python
"""
Virtuoso SKILL Execution Skill
Migrates from bridge_utils.py and il_runner_tool.py
"""
from core.base_skill import BaseSkill, SkillMetadata
from typing import Dict, Any, Optional
import subprocess
import os

class VirtuosoSkillRunnerSkill(BaseSkill):
    """
    Virtuoso SKILL execution skill.

    Provides:
    - SKILL file execution
    - Screenshot capture
    - Connection health checks
    - Output parsing
    """

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="virtuoso_skill_runner",
            display_name="Virtuoso SKILL Runner",
            version="1.0.0",
            description="Execute SKILL scripts in Cadence Virtuoso environment",
            author="AMS-IO-Agent Team",
            dependencies=[],
            category="virtuoso",
            tags=["virtuoso", "skill", "execution", "screenshot"],
            compatible_frameworks=["mcp", "agent_sdk", "smolagents"],
            knowledge_files=[
                "knowledge/skill_basics.md",
                "knowledge/execution_patterns.md"
            ]
        )

    def register_tools(self) -> Dict[str, callable]:
        return {
            "run_skill_file": self.run_file,
            "run_skill_with_screenshot": self.run_with_screenshot,
            "check_virtuoso_connection": self.check_connection,
            "screenshot_window": self.screenshot_window,
            "list_skill_files": self.list_files,
        }

    def run_file(self, skill_path: str, timeout: int = 300) -> str:
        """Execute a SKILL file in Virtuoso"""
        # Implementation migrated from il_runner_tool.py
        pass

    def run_with_screenshot(self, skill_path: str, output_path: str) -> str:
        """Execute SKILL and capture screenshot"""
        # Implementation
        pass

    def check_connection(self) -> Dict[str, Any]:
        """Check Virtuoso bridge connection"""
        # Implementation migrated from health_check_tool.py
        pass

    def screenshot_window(self, window_name: str, output_path: str) -> str:
        """Capture Virtuoso window screenshot"""
        # Implementation
        pass

    def list_files(self, directory: str = None) -> str:
        """List available SKILL files"""
        # Implementation
        pass
```

#### 2.3 Verification Skills

**File:** `skills/verification/drc_runner.py`

```python
"""
DRC Verification Skill
Migrates from drc_runner_tool.py
"""
from core.base_skill import BaseSkill, SkillMetadata

class DRCRunnerSkill(BaseSkill):
    """Design Rule Check execution skill"""

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="drc_runner",
            display_name="DRC Runner",
            version="1.0.0",
            description="Run Design Rule Check verification",
            author="AMS-IO-Agent Team",
            dependencies=["virtuoso_skill_runner"],
            category="verification",
            tags=["drc", "verification", "design_rules"],
            compatible_frameworks=["mcp", "agent_sdk", "smolagents"],
            knowledge_files=[
                "knowledge/drc_rules.md"
            ]
        )

    def register_tools(self) -> Dict[str, callable]:
        return {
            "run_drc": self.run,
            "parse_drc_output": self.parse_output,
            "check_drc_errors": self.check_errors,
        }
```

**File:** `skills/verification/lvs_runner.py`

```python
"""
LVS Verification Skill
Migrates from lvs_runner_tool.py
"""
from core.base_skill import BaseSkill, SkillMetadata

class LVSRunnerSkill(BaseSkill):
    """Layout vs Schematic verification skill"""

    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="lvs_runner",
            display_name="LVS Runner",
            version="1.0.0",
            description="Run Layout vs Schematic verification",
            author="AMS-IO-Agent Team",
            dependencies=["virtuoso_skill_runner"],
            category="verification",
            tags=["lvs", "verification", "schematic", "layout"],
            compatible_frameworks=["mcp", "agent_sdk", "smolagents"],
            knowledge_files=[
                "knowledge/lvs_rules.md"
            ]
        )

    def register_tools(self) -> Dict[str, callable]:
        return {
            "run_lvs": self.run,
            "parse_lvs_output": self.parse_output,
            "check_lvs_mismatches": self.check_mismatches,
        }
```

---

### Phase 3: MCP Integration (Week 5-6)

#### 3.1 MCP Server Implementation

**File:** `skills/mcp_server/__init__.py`

```python
"""
MCP Server for AMS-IO Skills
Enables skills to be used via Model Context Protocol
"""
from mcp.server import Server, FastAPI
from mcp.types import Tool, TextContent
import json

# Import skill registry
from core.skill_registry import SkillRegistry

class AMS_IO_MCP_Server(Server):
    """
    MCP server exposing AMS-IO Agent skills.

    Provides:
    - Tool discovery
    - Skill tool invocation
    - Skill metadata query
    """

    def __init__(self):
        super().__init__(name="ams-io-agent")
        self.registry = SkillRegistry(skills_dir="skills")
        self.registry.load_all()

    async def list_tools(self) -> list[Tool]:
        """List all available tools from all loaded skills"""
        tools = []

        for skill_name, skill in self.registry._skills.items():
            for tool_name, tool_func in skill._tools.items():
                # Register as MCP tool
                tool = Tool(
                    name=f"{skill_name}.{tool_name}",
                    description=f"Tool from {skill._metadata.display_name}",
                    inputSchema=self._get_tool_schema(tool_func)
                )
                tools.append(tool)

        return tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a specific skill tool"""
        # Parse skill_name.tool_name
        parts = name.split(".", 1)
        if len(parts) != 2:
            return f"Invalid tool name: {name}"

        skill_name, tool_name = parts

        skill = self.registry.get_skill(skill_name)
        if skill is None:
            return f"Skill not found: {skill_name}"

        tool_func = skill._tools.get(tool_name)
        if tool_func is None:
            return f"Tool not found: {tool_name}"

        # Execute tool
        try:
            result = tool_func(**arguments)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _get_tool_schema(self, func: callable) -> dict:
        """Extract tool schema from function signature"""
        # Use inspect to build JSON schema
        pass

# Create FastAPI wrapper
mcp_server = AMS_IO_MCP_Server()
app = FastAPI()

@app.get("/tools")
async def get_tools():
    """MCP endpoint for tool discovery"""
    return await mcp_server.list_tools()

@app.post("/tools/{name}/call")
async def call_tool(name: str, arguments: dict):
    """MCP endpoint for tool invocation"""
    return await mcp_server.call_tool(name, arguments)
```

#### 3.2 Agent SDK Integration

**File:** `skills/agent_sdk_integration.py`

```python
"""
Agent SDK Integration for AMS-IO Skills
Enables skills to be used with Claude Agent SDK
"""
from claude_agent_sdk import query, ClaudeAgentOptions, tool
from core.skill_registry import SkillRegistry
from typing import Optional, List

class AgentSDKIntegration:
    """
    Integration layer for Claude Agent SDK.

    Maps AMS-IO skills to Agent SDK tools.
    """

    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def convert_skill_to_tool(self, skill_name: str, tool_name: str) -> tool:
        """Convert a skill tool to Agent SDK tool decorator"""
        skill = self.registry.get_skill(skill_name)
        if skill is None:
            raise ValueError(f"Skill not found: {skill_name}")

        tool_func = skill._tools.get(tool_name)
        if tool_func is None:
            raise ValueError(f"Tool not found: {tool_name}")

        # Create Agent SDK tool
        @tool
        def converted_tool(**kwargs):
            return tool_func(**kwargs)

        return converted_tool

    def get_all_tools(self) -> List[tool]:
        """Get all skill tools as Agent SDK tools"""
        all_tools = []

        for skill_name, skill in self.registry._skills.items():
            for tool_name in skill._tools:
                try:
                    sdk_tool = self.convert_skill_to_tool(skill_name, tool_name)
                    all_tools.append(sdk_tool)
                except Exception:
                    continue

        return all_tools

    async def query_with_skills(
        self,
        prompt: str,
        allowed_tools: Optional[List[str]] = None,
        **options
    ):
        """Query Claude with AMS-IO skills"""
        sdk_tools = self.get_all_tools()

        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=allowed_tools or [t.name for t in sdk_tools],
                **options
            )
        ):
            if message.type == "result":
                return message.result
```

---

### Phase 4: Knowledge Base Migration (Week 7-8)

#### 4.1 Convert Markdown to Embedded Knowledge

**Strategy:** Extract knowledge from Knowledge_Base and embed within skill packages

**Migration Script:** `tools/migrate_knowledge.py`

```python
#!/usr/bin/env python3
"""
Migrate Knowledge_Base markdown files to skill-embedded knowledge.
"""
import shutil
from pathlib import Path
import yaml

# Source knowledge base
KB_SOURCE = Path("Knowledge_Base")

# Destination skills directory
SKILLS_DEST = Path("skills")

# Knowledge mapping
KNOWLEDGE_MAPPING = {
    # IO Ring knowledge
    "03_DESIGN_BLOCKS/IO_Ring/Core/structured_T180.md": {
        "dest": "skills/io_ring/knowledge/t180_core_principles.md",
        "skill": "io_ring"
    },
    "03_DESIGN_BLOCKS/IO_Ring/Core/structured_T28.md": {
        "dest": "skills/io_ring/knowledge/t28_core_principles.md",
        "skill": "io_ring"
    },

    # Technology knowledge
    "02_TECHNOLOGY/T180/T180_Technology.md": {
        "dest": "skills/io_ring/knowledge/t180_drc_rules.md",
        "skill": "io_ring"
    },
    "02_TECHNOLOGY/T28/T28_Technology.md": {
        "dest": "skills/io_ring/knowledge/t28_drc_rules.md",
        "skill": "io_ring"
    },

    # Core knowledge
    "01_CORE/KB_SKILL/skill_knowledge.md": {
        "dest": "skills/virtuoso/knowledge/skill_basics.md",
        "skill": "virtuoso"
    },
    "01_CORE/KB_Agent/system_prompt.md": {
        "dest": "skills/core/knowledge/agent_principles.md",
        "skill": "core"
    },

    # Error knowledge
    "04_ERRORS/README.md": {
        "dest": "skills/utils/knowledge/error_handling.md",
        "skill": "utils"
    },
}

def migrate_knowledge():
    """Migrate all knowledge files to skills"""
    print("🚀 Starting knowledge migration...")

    for source_path, mapping in KNOWLEDGE_MAPPING.items():
        source_file = KB_SOURCE / source_path
        dest_file = mapping["dest"]
        skill_name = mapping["skill"]

        if not source_file.exists():
            print(f"⚠️  Source not found: {source_path}")
            continue

        # Ensure destination directory exists
        dest_file = Path(dest_file)
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source_file, dest_file)
        print(f"✅ Copied: {source_path} -> {dest_file}")

    print("✅ Knowledge migration complete!")

def update_skill_metadata():
    """Update skill metadata files to reference migrated knowledge"""
    print("\n📝 Updating skill metadata...")

    # For each skill, update metadata.yaml to include knowledge_files
    skill_configs = {
        "io_ring": {
            "file": "skills/io_ring/metadata.yaml",
            "knowledge": [
                "knowledge/t180_core_principles.md",
                "knowledge/t28_core_principles.md",
                "knowledge/t180_drc_rules.md",
                "knowledge/t28_drc_rules.md",
            ]
        },
        "virtuoso": {
            "file": "skills/virtuoso/metadata.yaml",
            "knowledge": [
                "knowledge/skill_basics.md"
            ]
        },
        "core": {
            "file": "skills/core/metadata.yaml",
            "knowledge": [
                "knowledge/agent_principles.md"
            ]
        },
        "utils": {
            "file": "skills/utils/metadata.yaml",
            "knowledge": [
                "knowledge/error_handling.md"
            ]
        },
    }

    for skill_name, config in skill_configs.items():
        metadata_file = Path(config["file"])
        if not metadata_file.exists():
            print(f"⚠️  Metadata file not found: {metadata_file}")
            continue

        # Read and update metadata
        with open(metadata_file) as f:
            data = yaml.safe_load(f)

        data["knowledge_files"] = config["knowledge"]

        # Write back
        with open(metadata_file, 'w') as f:
            yaml.dump(data, f, sort_keys=False)

        print(f"✅ Updated: {metadata_file}")

    print("✅ Skill metadata update complete!")

if __name__ == "__main__":
    migrate_knowledge()
    update_skill_metadata()
    print("\n🎉 Migration complete! Run 'python setup_skills.py' to initialize.")
```

---

### Phase 5: Testing & Validation (Week 9-10)

#### 5.1 Unit Tests

**File:** `tests/test_skills_migration.py`

```python
"""
Unit tests for migrated skills.
Validates:
- Skill discovery and loading
- Tool registration
- Knowledge embedding
- MCP integration
- Agent SDK integration
"""

import pytest
from core.skill_registry import SkillRegistry
from skills.io_ring.t180_designer import T180IO_RingDesignerSkill

def test_skill_discovery():
    """Test that skills are discovered correctly"""
    registry = SkillRegistry(skills_dir="skills")
    discovered = registry.discover_skills()

    assert len(discovered) >= 3, "Should discover at least 3 skills"

    skill_names = [s.name for s in discovered]
    assert "t180_io_ring_designer" in skill_names
    assert "virtuoso_skill_runner" in skill_names

def test_tool_registration():
    """Test that skills register tools correctly"""
    skill = T180IO_RingDesignerSkill()
    tools = skill.register_tools()

    assert "generate_t180_config" in tools
    assert "validate_t180_config" in tools
    assert "generate_t180_schematic" in tools

def test_knowledge_loading():
    """Test that embedded knowledge is loaded"""
    skill = T180IO_RingDesignerSkill()
    knowledge = skill.load_knowledge()

    assert len(knowledge) > 0, "Should load embedded knowledge"

def test_dependency_resolution():
    """Test that dependencies are resolved correctly"""
    registry = SkillRegistry(skills_dir="skills")
    registry.load_all()

    # Check that skills with dependencies load after dependencies
    drc_skill = registry.get_skill("drc_runner")
    assert drc_skill is not None

def test_mcp_integration():
    """Test MCP server tool discovery"""
    from skills.mcp_server import AMS_IO_MCP_Server
    import asyncio

    server = AMS_IO_MCP_Server()
    tools = asyncio.run(server.list_tools())

    assert len(tools) > 0, "MCP should expose tools"

def test_agent_sdk_integration():
    """Test Agent SDK tool conversion"""
    from skills.agent_sdk_integration import AgentSDKIntegration
    from core.skill_registry import SkillRegistry

    registry = SkillRegistry(skills_dir="skills")
    integration = AgentSDKIntegration(registry)

    sdk_tools = integration.get_all_tools()
    assert len(sdk_tools) > 0, "Should convert skills to SDK tools"
```

#### 5.2 Integration Tests

**File:** `tests/test_io_ring_workflow.py`

```python
"""
Integration test for complete IO Ring workflow.
Tests end-to-end T180 IO ring generation.
"""

import pytest
import asyncio
from skills.agent_sdk_integration import AgentSDKIntegration
from core.skill_registry import SkillRegistry

@pytest.fixture
async def agent_integration():
    """Setup agent integration for testing"""
    registry = SkillRegistry(skills_dir="skills")
    registry.load_all()
    return AgentSDKIntegration(registry)

@pytest.mark.asyncio
async def test_t180_io_ring_generation(agent_integration):
    """Test complete T180 IO ring generation workflow"""

    prompt = """
    Generate a T180 IO ring with the following:
    - 8 digital pads: DA0, DA1, DA2, DA3, DA4, DA5, DA6, DA7
    - 4 analog pads: MCLK, CDCKB, VDCKB, GDCK
    - Digital pads are outputs
    - Clockwise placement
    - Use regular power/ground
    """

    result = await agent_integration.query_with_skills(
        prompt=prompt,
        allowed_tools=["io_ring.analyze_t180_requirements", "io_ring.generate_t180_config"]
    )

    assert "config" in result, "Should generate configuration"

    # Continue with schematic and layout generation
    # ...
```

---

### Phase 6: Documentation & Deployment (Week 11-12)

#### 6.1 Skill Documentation

**File:** `docs/SKILL_DEVELOPMENT_GUIDE.md`

```markdown
# Skill Development Guide

This guide explains how to develop new skills for AMS-IO Agent.

## Skill Structure

A skill is a self-contained package that provides:
- Metadata (version, dependencies, capabilities)
- Tools (callable functions)
- Embedded knowledge (markdown documentation)
- Validation rules

## Creating a New Skill

1. **Create skill directory:**
   ```
   mkdir skills/my_skill
   cd skills/my_skill
   ```

2. **Create skill class:**
   ```python
   from core.base_skill import BaseSkill, SkillMetadata

   class MySkill(BaseSkill):
       def get_metadata(self) -> SkillMetadata:
           return SkillMetadata(
               name="my_skill",
               display_name="My Skill",
               version="1.0.0",
               description="What my skill does",
               author="Your Name",
               dependencies=[],
               category="custom",
               tags=["tag1", "tag2"],
               compatible_frameworks=["mcp", "agent_sdk", "smolagents"],
               knowledge_files=[
                   "knowledge/my_knowledge.md"
               ]
           )

       def register_tools(self) -> Dict[str, callable]:
           return {
               "my_tool": self.my_tool,
           }

       def my_tool(self, arg1: str, arg2: int) -> str:
           # Tool implementation
           pass
   ```

3. **Create metadata.yaml:**
   ```yaml
   name: my_skill
   display_name: My Skill
   version: 1.0.0
   description: What my skill does
   author: Your Name
   dependencies: []
   category: custom
   tags:
     - tag1
     - tag2
   compatible_frameworks:
     - mcp
     - agent_sdk
     - smolagents
   knowledge_files:
     - knowledge/my_knowledge.md
   ```

4. **Add embedded knowledge:**
   ```bash
   mkdir knowledge
   # Copy or create markdown knowledge files
   ```

5. **Register skill:**
   Skills are auto-discovered. Just place in `skills/` directory.

## Tool Development

Tools must follow these conventions:

- **Type hints:** Use Python type hints for parameters
- **Docstrings:** Include docstrings with Args and Returns
- **Error handling:** Return error messages as strings
- **Output format:** Return structured data (dict/list) when possible

## Testing Skills

```bash
# Run all skill tests
pytest tests/test_skills_migration.py

# Run specific skill tests
pytest tests/test_io_ring_workflow.py
```

## MCP Deployment

To deploy skills via MCP:

1. Start MCP server:
   ```bash
   python -m skills.mcp_server
   ```

2. Configure client to use MCP server:
   ```json
   {
     "mcpServers": {
       "ams-io-agent": {
         "command": "python",
         "args": ["-m", "skills.mcp_server"]
       }
     }
   }
   ```

## Agent SDK Usage

To use skills with Agent SDK:

```python
from skills.agent_sdk_integration import AgentSDKIntegration
from core.skill_registry import SkillRegistry

# Load skills
registry = SkillRegistry(skills_dir="skills")
registry.load_all()

# Create integration
integration = AgentSDKIntegration(registry)

# Query with skills
async for message in query(
    prompt="Your prompt here",
    options=ClaudeAgentOptions(
        allowed_tools=integration.get_all_tools()
    )
):
    if message.type == "result":
        print(message.result)
```
```

#### 6.2 Migration Guide

**File:** `docs/MIGRATION_GUIDE.md`

```markdown
# Migration Guide: From Knowledge_Base to Skills

This guide helps users migrate from the old MCP/RAG system to the new skills paradigm.

## What's Changing?

| Old System | New System |
|------------|------------|
| `Knowledge_Base/` markdown files | `skills/` packages with embedded knowledge |
| Manual tool registration | Auto-discovery via skill registry |
| `knowledge_loader_tool.py` | `skill_registry.py` with hot-reload |
| `tools_config.yaml` | `skills/*/metadata.yaml` |
| Tight coupling to smolagents | Framework-agnostic (MCP + Agent SDK) |

## Migration Steps

### Step 1: Backup Current System

```bash
# Backup your current setup
cp -r Knowledge_Base Knowledge_Base.backup
cp config.yaml config.yaml.backup
```

### Step 2: Run Migration Script

```bash
# Migrate knowledge files to skills
python tools/migrate_knowledge.py
```

### Step 3: Verify Migration

```bash
# Check that skills were created
ls skills/

# Verify skill metadata
cat skills/io_ring/metadata.yaml

# Run tests
pytest tests/test_skills_migration.py
```

### Step 4: Update Configuration

**New config.yaml:**
```yaml
model:
  active: "claude"
  temperature: 1.0

interface:
  mode: "webui"  # or "cli"
  logging: true
  show_code: false

skills:
  # New skills configuration
  directory: "skills"  # Path to skills directory
  auto_load: true     # Auto-load all skills on startup
  hot_reload: true     # Enable hot-reload of skills

  # Skill-specific configuration
  enabled_skills:
    - io_ring
    - virtuoso
    - verification

  # Framework selection
  use_mcp: false        # Use MCP server
  use_agent_sdk: true   # Use Agent SDK integration
  use_smolagents: false  # Legacy (will be deprecated)
```

### Step 5: Start System

```bash
# Start with new skills system
python main.py
```

## Breaking Changes

- **Tool names changed:** Prefix with skill name (e.g., `io_ring.generate_t180_config`)
- **Knowledge loading:** Use `SkillRegistry` instead of `knowledge_loader_tool`
- **Configuration:** New `skills` section in config.yaml
- **API:** New MCP server endpoint available

## Migration Support

If you encounter issues during migration:

1. Check logs in `logs/` directory
2. Review migration script output
3. Consult `docs/SKILL_DEVELOPMENT_GUIDE.md`
4. Open issue on GitHub with migration details

## Rollback

If you need to rollback:

```bash
# Restore backup
rm -rf skills/
cp -r Knowledge_Base.backup Knowledge_Base/
cp config.yaml.backup config.yaml
```
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create `skills/` directory structure
- [ ] Implement `BaseSkill` class
- [ ] Implement `SkillRegistry` class
- [ ] Define skill metadata schema
- [ ] Create skill metadata template

### Phase 2: Core Skills
- [ ] Migrate T180 IO Ring designer skill
- [ ] Migrate T28 IO Ring designer skill
- [ ] Migrate Virtuoso skill runner
- [ ] Migrate DRC runner skill
- [ ] Migrate LVS runner skill
- [ ] Migrate PEX runner skill
- [ ] Create utility skills (health check, error recovery)

### Phase 3: MCP Integration
- [ ] Implement MCP server
- [ ] Add tool discovery endpoint
- [ ] Add tool invocation endpoint
- [ ] Add metadata query endpoint
- [ ] Test MCP with Claude Desktop

### Phase 4: Knowledge Migration
- [ ] Create migration script
- [ ] Migrate IO Ring knowledge
- [ ] Migrate technology knowledge
- [ ] Migrate core knowledge
- [ ] Migrate error knowledge
- [ ] Update skill metadata files

### Phase 5: Testing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Run all tests
- [ ] Fix discovered issues
- [ ] Validate with real workflows

### Phase 6: Documentation
- [ ] Write skill development guide
- [ ] Write migration guide
- [ ] Update main README
- [ ] Create examples
- [ ] Document API endpoints

---

## Success Criteria

The migration is considered complete when:

1. **All skills are discoverable and loadable** via `SkillRegistry`
2. **Knowledge is embedded** within skill packages
3. **MCP server is functional** and exposes all tools
4. **Agent SDK integration works** with all skills
5. **Unit tests pass** for all components
6. **Integration tests validate** complete workflows
7. **Documentation is complete** for developers and users
8. **Performance is comparable** to or better than legacy system

---

## Next Steps

1. **Review this plan** with your team
2. **Prioritize phases** based on resources and timeline
3. **Create development branches** for each phase
4. **Implement incrementally** with regular testing
5. **Gather feedback** from early adopters
6. **Iterate and improve** based on real-world usage

---

**Document Status:** Draft
**Last Updated:** 2026-03-14
**Version:** 1.0.0

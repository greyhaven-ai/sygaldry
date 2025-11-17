#!/usr/bin/env python3
"""
Guided Agent Schema Fixer

This script provides detailed, line-by-line guidance for fixing agent schemas
for Mirascope v2 and OpenAI compatibility.

It shows you:
- Exact lines that need changing
- Before/after examples
- Step-by-step instructions

Usage:
    python scripts/guided_agent_fixer.py sentiment_analysis
    python scripts/guided_agent_fixer.py --all  # Guide through all agents
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple


class AgentGuidedFixer:
    """Provides guided fixing instructions for an agent."""

    def __init__(self, agent_path: Path):
        self.agent_path = agent_path
        self.agent_name = agent_path.parent.name
        self.content = agent_path.read_text()
        self.lines = self.content.split('\n')

    def analyze_and_guide(self):
        """Provide detailed guidance for fixing this agent."""
        print("\n" + "=" * 80)
        print(f"FIXING AGENT: {self.agent_name}")
        print("=" * 80)
        print(f"File: {self.agent_path}")
        print()

        fixes_needed = []

        # Check 1: Lilypad import
        if not self._has_lilypad_import():
            fixes_needed.append(self._guide_lilypad_import())

        # Check 2: Fields with defaults in BaseModel classes
        fields_with_defaults = self._find_fields_with_defaults_detailed()
        if fields_with_defaults:
            fixes_needed.append(self._guide_field_defaults(fields_with_defaults))

        # Check 3: Nested models with Field() wrapper
        nested_with_wrapper = self._find_real_nested_models_with_wrapper()
        if nested_with_wrapper:
            fixes_needed.append(self._guide_nested_wrappers(nested_with_wrapper))

        # Check 4: Wrapper functions
        llm_functions = self._find_llm_functions()
        if llm_functions:
            fixes_needed.append(self._guide_wrapper_functions(llm_functions))

        if not fixes_needed:
            print("✅ This agent appears to be correctly configured!")
            print("No fixes needed based on the established pattern.")
            return

        # Print all fixes
        print(f"Found {len(fixes_needed)} categories of fixes needed:\n")
        for i, fix in enumerate(fixes_needed, 1):
            print(f"\n{'─' * 80}")
            print(f"FIX #{i}")
            print('─' * 80)
            print(fix)

        print("\n" + "=" * 80)
        print(f"Summary: {len(fixes_needed)} fix categories for {self.agent_name}")
        print("=" * 80)

    def _has_lilypad_import(self) -> bool:
        """Check if Lilypad import exists."""
        return 'from lilypad import trace' in self.content or 'LILYPAD_AVAILABLE' in self.content

    def _guide_lilypad_import(self) -> str:
        """Guide for adding Lilypad import."""
        # Find where to insert
        last_import_line = 0
        for i, line in enumerate(self.lines):
            if line.strip().startswith('from') or line.strip().startswith('import'):
                last_import_line = i

        guide = f"""
📋 ADD LILYPAD IMPORT

Location: After line {last_import_line}

Add this code block:

```python
try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False
```

This provides the @trace() decorator with a fallback if Lilypad isn't installed.
"""
        return guide

    def _find_fields_with_defaults_detailed(self) -> List[Tuple[int, str, str]]:
        """Find fields with default values and their line numbers."""
        results = []
        in_class = False
        current_class = None

        for i, line in enumerate(self.lines, 1):
            # Track which class we're in
            if line.strip().startswith('class ') and 'BaseModel' in line:
                match = re.match(r'\s*class\s+(\w+)', line)
                if match:
                    current_class = match.group(1)
                    in_class = True
            elif line.strip().startswith('class ') and not 'BaseModel' in line:
                in_class = False
                current_class = None

            # Check for fields with defaults in BaseModel classes
            if in_class and current_class and ':' in line and '=' in line:
                # Look for Field(default=...) or Field(default_factory=...)
                if 'Field(' in line and ('default=' in line or 'default_factory=' in line):
                    # Extract field name
                    match = re.match(r'\s*(\w+):', line)
                    if match:
                        field_name = match.group(1)
                        results.append((i, f"{current_class}.{field_name}", line.strip()))

        return results

    def _guide_field_defaults(self, fields: List[Tuple[int, str, str]]) -> str:
        """Guide for fixing fields with defaults."""
        guide = f"""
📋 MAKE FIELDS REQUIRED (Remove Defaults)

OpenAI's strict schema validation requires ALL fields to be in the 'required' array.
Fields with default values are excluded from 'required', causing schema errors.

Found {len(fields)} fields with defaults:
"""
        for line_num, field_path, current_line in fields:
            guide += f"\n  Line {line_num}: {field_path}"
            guide += f"\n  Current: {current_line}"

            # Suggest fix
            if 'default_factory=list' in current_line or 'default=[]' in current_line:
                guide += "\n  Fix: Replace with ... and note 'empty list if no items' in description"
            elif 'default_factory=dict' in current_line or 'default={}' in current_line:
                guide += "\n  Fix: Replace with ... and note 'empty dict if no data' in description"
            elif 'default=None' in current_line:
                guide += "\n  Fix: Replace with ... or make the field required with empty string"
            else:
                guide += "\n  Fix: Replace default value with ..."

            guide += "\n"

        guide += """
Pattern:
  ❌ BAD:  sources: list[str] = Field(default=[], description="Sources")
  ✅ GOOD: sources: list[str] = Field(..., description="Sources (empty list if no sources)")

  ❌ BAD:  metadata: dict = Field(default_factory=dict, description="Metadata")
  ✅ GOOD: metadata: dict = Field(..., description="Metadata (empty dict if no data)")
"""
        return guide

    def _find_real_nested_models_with_wrapper(self) -> List[Tuple[int, str, str, str]]:
        """Find actual nested model references (not list[str] etc) with Field() wrapper."""
        results = []
        in_class = False
        current_class = None

        # First, collect all BaseModel class names
        model_classes = set()
        for line in self.lines:
            if 'class ' in line and 'BaseModel' in line:
                match = re.match(r'\s*class\s+(\w+)', line)
                if match:
                    model_classes.add(match.group(1))

        for i, line in enumerate(self.lines, 1):
            # Track which class we're in
            if line.strip().startswith('class ') and 'BaseModel' in line:
                match = re.match(r'\s*class\s+(\w+)', line)
                if match:
                    current_class = match.group(1)
                    in_class = True
            elif line.strip().startswith('class '):
                in_class = False
                current_class = None

            # Check for nested model fields
            if in_class and current_class and ':' in line and 'Field(' in line:
                # Extract field name and type annotation
                match = re.match(r'\s*(\w+):\s*([^=]+?)\s*=\s*Field\(', line)
                if match:
                    field_name = match.group(1)
                    type_annotation = match.group(2).strip()

                    # Check if type is a known model class
                    # Simple check: does the type start with an uppercase letter and is in our models?
                    base_type = type_annotation.split('[')[0].strip()
                    if base_type in model_classes:
                        results.append((i, f"{current_class}.{field_name}", type_annotation, line.strip()))

        return results

    def _guide_nested_wrappers(self, fields: List[Tuple[int, str, str, str]]) -> str:
        """Guide for removing Field() wrappers from nested models."""
        guide = f"""
📋 REMOVE Field() FROM NESTED MODELS

OpenAI's schema generator creates `$ref` references for nested models.
When Field() wrapper is present, it adds extra keywords to $ref, which OpenAI rejects.

Found {len(fields)} nested model fields with Field() wrapper:
"""
        for line_num, field_path, type_annotation, current_line in fields:
            guide += f"\n  Line {line_num}: {field_path}"
            guide += f"\n  Type: {type_annotation}"
            guide += f"\n  Current: {current_line}"

            field_name = field_path.split('.')[-1]
            guide += f"\n  Fix: {field_name}: {type_annotation}  # No Field() wrapper"
            guide += "\n"

        guide += """
Pattern:
  ❌ BAD:  emotions: EmotionScore = Field(..., description="Detected emotions")
  ✅ GOOD: emotions: EmotionScore  # No Field() wrapper on nested model

  ❌ BAD:  items: list[Item] = Field(..., description="List of items")
  ✅ GOOD: items: list[Item]  # No Field() wrapper on nested model

Note: Add a comment explaining why:
  # Note: No Field() wrapper on nested model to avoid OpenAI schema error
  # OpenAI rejects $ref with additional keywords like 'description'
"""
        return guide

    def _find_llm_functions(self) -> List[Tuple[int, str]]:
        """Find @llm.call decorated functions."""
        results = []
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            # Look for @llm.call decorator
            if '@llm.call' in line:
                # Find the function name
                j = i + 1
                while j < len(self.lines):
                    func_line = self.lines[j]
                    if 'async def ' in func_line or 'def ' in func_line:
                        match = re.search(r'def\s+(\w+)\(', func_line)
                        if match:
                            func_name = match.group(1)
                            # Only include if it doesn't start with _
                            if not func_name.startswith('_'):
                                results.append((i + 1, func_name))  # +1 for 1-based line numbers
                        break
                    j += 1
            i += 1
        return results

    def _guide_wrapper_functions(self, functions: List[Tuple[int, str]]) -> str:
        """Guide for creating wrapper functions."""
        guide = f"""
📋 CREATE WRAPPER FUNCTIONS WITH .parse()

Mirascope v2 changed how responses work:
- @llm.call decorated functions return AsyncResponse objects
- Must call .parse() to get the formatted Pydantic model

Found {len(functions)} @llm.call functions that need wrappers:
"""
        for line_num, func_name in functions:
            guide += f"\n  Line {line_num}: {func_name}()"
            guide += f"\n  Steps:"
            guide += f"\n    1. Rename to _{func_name}_call"
            guide += f"\n    2. Create public wrapper {func_name}() with @trace()"
            guide += f"\n    3. Wrapper calls _{func_name}_call() and returns .parse()"
            guide += "\n"

        guide += f"""
Pattern (for function 'analyze'):

STEP 1: Rename @llm.call function to _analyze_call:

  # Internal LLM call function - returns AsyncResponse
  @llm.call(
      provider="openai:completions",
      model_id="gpt-4o-mini",
      format=ResponseModel,
  )
  async def _analyze_call(input: str) -> str:
      return f"Your prompt here"

STEP 2: Create public wrapper:

  # Public API wrapper - returns parsed ResponseModel
  @trace()
  async def analyze(input: str) -> ResponseModel:
      '''
      Main public API function.

      Args:
          input: The input to analyze

      Returns:
          ResponseModel with analysis results
      '''
      response = await _analyze_call(input=input)
      return response.parse()

STEP 3: Update any convenience functions to call the public wrapper.
"""
        return guide


def main():
    parser = argparse.ArgumentParser(description="Get guided fixing instructions for agents")
    parser.add_argument(
        'agent',
        nargs='?',
        help='Agent name to fix (e.g., sentiment_analysis)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Guide through all agents (interactive)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all agents that need fixes'
    )

    args = parser.parse_args()

    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    registry_path = repo_root / "packages" / "sygaldry_registry"
    agents_dir = registry_path / "components" / "agents"

    if args.list:
        # List all agents
        agent_paths = sorted(agents_dir.glob("*/agent.py"))
        print(f"Found {len(agent_paths)} agents:\n")
        for agent_path in agent_paths:
            agent_name = agent_path.parent.name
            print(f"  - {agent_name}")
        print(f"\nTo fix an agent: python {Path(__file__).name} <agent_name>")
        return

    if args.agent:
        # Fix specific agent
        agent_path = agents_dir / args.agent / "agent.py"
        if not agent_path.exists():
            print(f"❌ Agent not found: {args.agent}")
            print(f"\nTry: python {Path(__file__).name} --list")
            return

        fixer = AgentGuidedFixer(agent_path)
        fixer.analyze_and_guide()

    elif args.all:
        # Interactive mode - guide through all agents
        agent_paths = sorted(agents_dir.glob("*/agent.py"))
        print(f"Found {len(agent_paths)} agents to review\n")

        for agent_path in agent_paths:
            fixer = AgentGuidedFixer(agent_path)
            fixer.analyze_and_guide()

            print("\n" + "=" * 80)
            response = input("\nPress ENTER for next agent, or 'q' to quit: ")
            if response.lower() == 'q':
                break

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

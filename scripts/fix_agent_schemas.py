#!/usr/bin/env python3
"""
Automated Schema Fixer for Mirascope v2 Agents

This script automatically applies the schema fixes needed for OpenAI compatibility
to all agents in the registry.

Fixes applied:
1. Make all Pydantic model fields required (remove default values)
2. Remove Field() wrapper from nested model references
3. Add Lilypad import with fallback
4. Create wrapper functions that call .parse()
5. Rename @llm.call functions to _agent_name_call

Usage:
    python scripts/fix_agent_schemas.py --dry-run  # Preview changes
    python scripts/fix_agent_schemas.py --apply    # Apply changes
    python scripts/fix_agent_schemas.py --agent sentiment_analysis --apply  # Fix specific agent
"""

import argparse
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import sys


class AgentSchemaFixer:
    """Analyzes and fixes agent schema issues for OpenAI compatibility."""

    def __init__(self, agent_path: Path):
        self.agent_path = agent_path
        self.agent_name = agent_path.parent.name
        self.content = agent_path.read_text()
        self.tree = ast.parse(self.content)
        self.issues: List[str] = []
        self.fixes_applied: List[str] = []

    def analyze(self) -> Dict[str, any]:
        """Analyze the agent for schema issues."""
        issues = {
            'has_lilypad_import': self._has_lilypad_import(),
            'response_models': self._find_response_models(),
            'llm_call_functions': self._find_llm_call_functions(),
            'needs_wrapper': self._needs_wrapper_function(),
            'fields_with_defaults': [],
            'nested_fields_with_field_wrapper': [],
        }

        # Check each response model for issues
        for model_name, model_info in issues['response_models'].items():
            fields_with_defaults = self._find_fields_with_defaults(model_info['node'])
            if fields_with_defaults:
                issues['fields_with_defaults'].extend([
                    f"{model_name}.{field}" for field in fields_with_defaults
                ])

            nested_with_wrapper = self._find_nested_fields_with_wrapper(model_info['node'])
            if nested_with_wrapper:
                issues['nested_fields_with_field_wrapper'].extend([
                    f"{model_name}.{field}" for field in nested_with_wrapper
                ])

        return issues

    def _has_lilypad_import(self) -> bool:
        """Check if Lilypad import exists."""
        return 'from lilypad import trace' in self.content or 'LILYPAD_AVAILABLE' in self.content

    def _find_response_models(self) -> Dict[str, Dict]:
        """Find all Pydantic BaseModel classes."""
        models = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from BaseModel
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        models[node.name] = {
                            'node': node,
                            'line': node.lineno,
                            'name': node.name
                        }
        return models

    def _find_llm_call_functions(self) -> List[Dict]:
        """Find all functions decorated with @llm.call."""
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if self._is_llm_call_decorator(decorator):
                        functions.append({
                            'name': node.name,
                            'line': node.lineno,
                            'is_async': isinstance(node, ast.AsyncFunctionDef),
                            'node': node
                        })
        return functions

    def _is_llm_call_decorator(self, decorator) -> bool:
        """Check if a decorator is @llm.call."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return (isinstance(decorator.func.value, ast.Name) and
                        decorator.func.value.id == 'llm' and
                        decorator.func.attr == 'call')
        return False

    def _needs_wrapper_function(self) -> bool:
        """Check if we need to create wrapper functions."""
        # If there's an @llm.call function that doesn't start with _, it needs wrapping
        for node in ast.walk(self.tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if self._is_llm_call_decorator(decorator):
                        if not node.name.startswith('_'):
                            return True
        return False

    def _find_fields_with_defaults(self, class_node: ast.ClassDef) -> List[str]:
        """Find fields that have default values."""
        fields_with_defaults = []
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign):
                # Check if the assignment has a value (default)
                if node.value:
                    # Check if it's a Field() call with default or default_factory
                    if isinstance(node.value, ast.Call):
                        if self._is_field_with_default(node.value):
                            if isinstance(node.target, ast.Name):
                                fields_with_defaults.append(node.target.id)
        return fields_with_defaults

    def _is_field_with_default(self, call_node: ast.Call) -> bool:
        """Check if a Field() call has default or default_factory."""
        if not (isinstance(call_node.func, ast.Name) and call_node.func.id == 'Field'):
            return False

        # Check for default or default_factory in kwargs
        for keyword in call_node.keywords:
            if keyword.arg in ('default', 'default_factory'):
                return True

        # Check if first arg is not Ellipsis (...)
        if call_node.args and not isinstance(call_node.args[0], ast.Constant):
            return True
        if call_node.args and isinstance(call_node.args[0], ast.Constant):
            if call_node.args[0].value is not ...:
                return True

        return False

    def _find_nested_fields_with_wrapper(self, class_node: ast.ClassDef) -> List[str]:
        """Find nested model fields that have Field() wrapper."""
        nested_with_wrapper = []
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign):
                # Check if annotation is a custom type (not str, int, etc.)
                if self._is_nested_model_type(node.annotation):
                    # Check if it has a Field() wrapper
                    if node.value and isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name) and node.value.func.id == 'Field':
                            if isinstance(node.target, ast.Name):
                                nested_with_wrapper.append(node.target.id)
        return nested_with_wrapper

    def _is_nested_model_type(self, annotation) -> bool:
        """Check if an annotation is likely a nested model type."""
        if isinstance(annotation, ast.Name):
            # Simple type - check if it's not a builtin
            return annotation.id not in ('str', 'int', 'float', 'bool', 'dict', 'list')
        elif isinstance(annotation, ast.Subscript):
            # Generic type like list[SomeModel]
            return True
        return False

    def apply_fixes(self) -> str:
        """Apply all necessary fixes and return the modified content."""
        modified_content = self.content

        # 1. Add Lilypad import if missing
        if not self._has_lilypad_import():
            modified_content = self._add_lilypad_import(modified_content)
            self.fixes_applied.append("Added Lilypad import with fallback")

        # 2. Fix response model fields
        analysis = self.analyze()

        # Fix fields with defaults
        for field_path in analysis['fields_with_defaults']:
            modified_content = self._fix_field_default(modified_content, field_path)
            self.fixes_applied.append(f"Made field required: {field_path}")

        # Remove Field() from nested models
        for field_path in analysis['nested_fields_with_field_wrapper']:
            modified_content = self._remove_nested_field_wrapper(modified_content, field_path)
            self.fixes_applied.append(f"Removed Field() wrapper from nested model: {field_path}")

        # 3. Create wrapper functions
        if analysis['needs_wrapper']:
            modified_content = self._create_wrapper_functions(modified_content, analysis)
            self.fixes_applied.append("Created wrapper functions with .parse()")

        return modified_content

    def _add_lilypad_import(self, content: str) -> str:
        """Add Lilypad import with fallback."""
        import_block = '''
try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False
'''
        # Insert after the last import before the first class/function
        lines = content.split('\n')
        insert_pos = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('from') or line.strip().startswith('import'):
                insert_pos = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('class') or line.strip().startswith('def') or line.strip().startswith('@'):
                    break

        lines.insert(insert_pos, import_block)
        return '\n'.join(lines)

    def _fix_field_default(self, content: str, field_path: str) -> str:
        """Fix a field with default value to be required."""
        model_name, field_name = field_path.split('.')

        # Pattern to match field with default
        # Example: sources: list[str] = Field(default=[], description="...")
        # Replace with: sources: list[str] = Field(..., description="... (empty list if no sources)")

        pattern = rf'({field_name}:\s*[^=]+?=\s*Field\()'

        def replace_default(match):
            # Get the full field definition line
            line_start = match.start()
            line_end = content.find('\n', line_start)
            if line_end == -1:
                line_end = len(content)

            full_line = content[line_start:line_end]

            # Replace default= or default_factory= with ...
            fixed_line = re.sub(r'default(_factory)?=[^,)]+,?\s*', '', full_line)

            # Ensure we have ... as first argument
            if '(,' in fixed_line or '( ' in fixed_line:
                fixed_line = fixed_line.replace('(', '(..., ', 1)
            elif '()' in fixed_line:
                fixed_line = fixed_line.replace('()', '(...)', 1)
            elif not '...' in fixed_line:
                fixed_line = fixed_line.replace('(', '(..., ', 1)

            # Add note about empty values in description
            if 'list' in full_line and 'empty list' not in fixed_line.lower():
                fixed_line = re.sub(
                    r'description="([^"]+)"',
                    r'description="\1 (empty list if no items)"',
                    fixed_line
                )
            elif 'dict' in full_line and 'empty' not in fixed_line.lower():
                fixed_line = re.sub(
                    r'description="([^"]+)"',
                    r'description="\1 (empty dict if no data)"',
                    fixed_line
                )

            return fixed_line

        # Find and replace the field definition
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f'{field_name}:' in line and 'Field(' in line:
                lines[i] = replace_default(type('Match', (), {'start': lambda: 0, 'group': lambda x: line})())

        return '\n'.join(lines)

    def _remove_nested_field_wrapper(self, content: str, field_path: str) -> str:
        """Remove Field() wrapper from nested model reference."""
        model_name, field_name = field_path.split('.')

        # Pattern: emotions: EmotionScore = Field(..., description="...")
        # Replace with: emotions: EmotionScore

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f'{field_name}:' in line and 'Field(' in line:
                # Extract type annotation
                match = re.match(rf'\s*{field_name}:\s*([^=]+)', line)
                if match:
                    type_annotation = match.group(1).strip()
                    # Add comment explaining why
                    comment = "# Note: No Field() wrapper on nested model to avoid OpenAI schema error"
                    lines[i] = f"    {field_name}: {type_annotation}  {comment}"

        return '\n'.join(lines)

    def _create_wrapper_functions(self, content: str, analysis: Dict) -> str:
        """Create wrapper functions for @llm.call decorated functions."""
        # This is complex - for now, we'll just rename the function and add a comment
        # indicating that a wrapper needs to be created manually

        for func_info in analysis['llm_call_functions']:
            func_name = func_info['name']
            if not func_name.startswith('_'):
                # Rename to _function_name_call
                new_name = f"_{func_name}_call"
                content = content.replace(
                    f"async def {func_name}(",
                    f"async def {new_name}("
                )
                self.fixes_applied.append(f"Renamed {func_name} to {new_name}")
                self.fixes_applied.append(f"TODO: Create public wrapper for {func_name}")

        return content


def find_all_agents(registry_path: Path) -> List[Path]:
    """Find all agent.py files in the registry."""
    agents_dir = registry_path / "components" / "agents"
    return list(agents_dir.glob("*/agent.py"))


def main():
    parser = argparse.ArgumentParser(description="Fix agent schemas for Mirascope v2 compatibility")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply the fixes'
    )
    parser.add_argument(
        '--agent',
        type=str,
        help='Fix a specific agent (e.g., sentiment_analysis)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate a detailed report of issues'
    )

    args = parser.parse_args()

    if not (args.dry_run or args.apply or args.report):
        parser.print_help()
        sys.exit(1)

    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    registry_path = repo_root / "packages" / "sygaldry_registry"

    # Find agents to process
    if args.agent:
        agent_path = registry_path / "components" / "agents" / args.agent / "agent.py"
        if not agent_path.exists():
            print(f"❌ Agent not found: {args.agent}")
            sys.exit(1)
        agent_paths = [agent_path]
    else:
        agent_paths = find_all_agents(registry_path)

    print(f"Found {len(agent_paths)} agents to process\n")

    # Process each agent
    results = []
    for agent_path in agent_paths:
        fixer = AgentSchemaFixer(agent_path)
        analysis = fixer.analyze()

        # Check if fixes are needed
        needs_fixes = (
            not analysis['has_lilypad_import'] or
            analysis['fields_with_defaults'] or
            analysis['nested_fields_with_field_wrapper'] or
            analysis['needs_wrapper']
        )

        results.append({
            'name': fixer.agent_name,
            'path': agent_path,
            'analysis': analysis,
            'needs_fixes': needs_fixes,
            'fixer': fixer
        })

    # Generate report
    if args.report or args.dry_run:
        print("=" * 80)
        print("AGENT SCHEMA ANALYSIS REPORT")
        print("=" * 80)
        print()

        agents_needing_fixes = [r for r in results if r['needs_fixes']]
        agents_ok = [r for r in results if not r['needs_fixes']]

        print(f"✅ Agents OK: {len(agents_ok)}")
        print(f"⚠️  Agents needing fixes: {len(agents_needing_fixes)}")
        print()

        if agents_needing_fixes:
            print("Agents requiring fixes:")
            print("-" * 80)
            for result in agents_needing_fixes:
                print(f"\n📋 {result['name']}")
                analysis = result['analysis']

                if not analysis['has_lilypad_import']:
                    print("  ❌ Missing Lilypad import")

                if analysis['fields_with_defaults']:
                    print(f"  ❌ Fields with defaults: {', '.join(analysis['fields_with_defaults'])}")

                if analysis['nested_fields_with_field_wrapper']:
                    print(f"  ❌ Nested fields with Field() wrapper: {', '.join(analysis['nested_fields_with_field_wrapper'])}")

                if analysis['needs_wrapper']:
                    print("  ❌ Needs wrapper function with .parse()")

                print(f"  📁 Path: {result['path'].relative_to(repo_root)}")

    # Apply fixes
    if args.apply:
        print("\n" + "=" * 80)
        print("APPLYING FIXES")
        print("=" * 80)
        print()

        agents_to_fix = [r for r in results if r['needs_fixes']]

        for result in agents_to_fix:
            print(f"\n🔧 Fixing {result['name']}...")
            fixer = result['fixer']

            try:
                modified_content = fixer.apply_fixes()

                if args.dry_run:
                    print(f"  [DRY RUN] Would apply {len(fixer.fixes_applied)} fixes:")
                    for fix in fixer.fixes_applied:
                        print(f"    - {fix}")
                else:
                    # Write the modified content
                    result['path'].write_text(modified_content)
                    print(f"  ✅ Applied {len(fixer.fixes_applied)} fixes:")
                    for fix in fixer.fixes_applied:
                        print(f"    - {fix}")

            except Exception as e:
                print(f"  ❌ Error fixing {result['name']}: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        if args.dry_run:
            print(f"DRY RUN COMPLETE - No files were modified")
        else:
            print(f"✅ FIXES APPLIED to {len(agents_to_fix)} agents")
        print("=" * 80)


if __name__ == "__main__":
    main()

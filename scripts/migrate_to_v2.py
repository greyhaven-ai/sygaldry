#!/usr/bin/env python3
"""
Mirascope v2 Migration Script

This script automates the migration from Mirascope v1 to v2 by:
1. Updating imports
2. Converting @prompt_template decorators to functional prompts
3. Updating @llm.call decorator parameters
4. Converting BaseTool classes to @llm.tool functions
5. Replacing BaseDynamicConfig pattern

Usage:
    python migrate_to_v2.py --file path/to/file.py
    python migrate_to_v2.py --dir path/to/directory
    python migrate_to_v2.py --all  # Migrate all component files
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class MirascopeV2Migrator:
    """Automated migrator for Mirascope v1 to v2."""

    def __init__(self):
        self.changes = []

    def migrate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Migrate a single file to v2."""
        print(f"\n📄 Migrating: {file_path}")

        if not file_path.exists():
            return False, [f"File not found: {file_path}"]

        content = file_path.read_text()
        original_content = content
        changes = []

        # Step 1: Update imports
        content, import_changes = self._update_imports(content)
        changes.extend(import_changes)

        # Step 2: Convert @llm.call decorators
        content, call_changes = self._convert_llm_calls(content)
        changes.extend(call_changes)

        # Step 3: Convert @prompt_template decorators (remove them)
        content, template_changes = self._convert_prompt_templates(content)
        changes.extend(template_changes)

        # Step 4: Convert BaseTool classes (manual review recommended)
        tool_classes = self._find_basetool_classes(content)
        if tool_classes:
            changes.append(f"⚠️  Found {len(tool_classes)} BaseTool classes - manual conversion recommended")
            for tool_name in tool_classes:
                changes.append(f"   - {tool_name}")

        # Step 5: Find BaseDynamicConfig usage
        dynamic_config_usage = self._find_dynamic_config(content)
        if dynamic_config_usage:
            changes.append(f"⚠️  Found {len(dynamic_config_usage)} BaseDynamicConfig usages - manual conversion required")

        if changes:
            # Write changes
            file_path.write_text(content)
            print(f"✅ Migrated {file_path}")
            for change in changes:
                print(f"  {change}")
            return True, changes
        else:
            print(f"⏭️  No changes needed for {file_path}")
            return False, []

    def _update_imports(self, content: str) -> Tuple[str, List[str]]:
        """Update imports to v2 style."""
        changes = []

        # Pattern: from mirascope import [anything]
        pattern = r'from mirascope import (.+)'
        matches = re.findall(pattern, content)

        if matches:
            for match in matches:
                imports = [i.strip() for i in match.split(',')]
                # Check what we're importing
                keeps = ['llm']
                removes = []

                for imp in imports:
                    if imp in ['prompt_template', 'BaseTool', 'BaseDynamicConfig']:
                        removes.append(imp)
                    elif 'llm' not in imp:
                        keeps.append(imp)

                if removes:
                    # Replace the import line
                    old_import = f'from mirascope import {match}'
                    new_import = 'from mirascope import llm'
                    content = content.replace(old_import, new_import)
                    changes.append(f"✓ Updated imports: removed {', '.join(removes)}")

        return content, changes

    def _convert_llm_calls(self, content: str) -> Tuple[str, List[str]]:
        """Convert @llm.call decorator parameters."""
        changes = []

        # Pattern: @llm.call(...) with various parameters
        pattern = r'@llm\.call\(([\s\S]*?)\)'

        def replace_call(match):
            params = match.group(1)

            # Update provider: "openai" -> "openai:completions"
            if 'provider="openai"' in params and ':' not in params:
                params = params.replace('provider="openai"', 'provider="openai:completions"')
                changes.append("✓ Updated provider: openai -> openai:completions")

            # Update model -> model_id
            params = re.sub(r'\bmodel\s*=', 'model_id=', params)
            if 'model_id' in params and 'model=' in match.group(0):
                changes.append("✓ Updated parameter: model -> model_id")

            # Update response_model -> format
            params = re.sub(r'\bresponse_model\s*=', 'format=', params)
            if 'format=' in params and 'response_model' in match.group(0):
                changes.append("✓ Updated parameter: response_model -> format")

            return f'@llm.call({params})'

        content = re.sub(pattern, replace_call, content)

        return content, changes

    def _convert_prompt_templates(self, content: str) -> Tuple[str, List[str]]:
        """Remove @prompt_template decorators and convert to functional prompts."""
        changes = []

        # Find @prompt_template decorators
        pattern = r'@prompt_template\(([\s\S]*?)\)\s*\n'
        matches = list(re.finditer(pattern, content))

        if matches:
            changes.append(f"⚠️  Found {len(matches)} @prompt_template decorators")
            changes.append("   Manual conversion required:")
            changes.append("   1. Remove @prompt_template decorator")
            changes.append("   2. Convert function to return f-string")
            changes.append("   3. Replace {var} with {var} in f-string")

        return content, changes

    def _find_basetool_classes(self, content: str) -> List[str]:
        """Find BaseTool class definitions."""
        pattern = r'class\s+(\w+)\(BaseTool\):'
        matches = re.findall(pattern, content)
        return matches

    def _find_dynamic_config(self, content: str) -> List[str]:
        """Find BaseDynamicConfig usage."""
        pattern = r'BaseDynamicConfig|"computed_fields"'
        matches = re.findall(pattern, content)
        return matches


def main():
    parser = argparse.ArgumentParser(description="Migrate Mirascope v1 code to v2")
    parser.add_argument("--file", type=Path, help="Migrate a single file")
    parser.add_argument("--dir", type=Path, help="Migrate all Python files in directory")
    parser.add_argument("--all", action="store_true", help="Migrate all component files")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")

    args = parser.parse_args()

    migrator = MirascopeV2Migrator()

    if args.file:
        files = [args.file]
    elif args.dir:
        files = list(args.dir.rglob("*.py"))
    elif args.all:
        base = Path("packages/sygaldry_registry/components")
        files = list(base.rglob("agent.py"))
    else:
        parser.print_help()
        return

    print(f"\n🚀 Starting Mirascope v2 migration...")
    print(f"   Files to process: {len(files)}\n")

    total_migrated = 0
    total_changes = 0

    for file_path in files:
        migrated, changes = migrator.migrate_file(file_path)
        if migrated:
            total_migrated += 1
            total_changes += len(changes)

    print(f"\n✨ Migration complete!")
    print(f"   Files migrated: {total_migrated}/{len(files)}")
    print(f"   Total changes: {total_changes}")

    if total_migrated > 0:
        print(f"\n⚠️  Next steps:")
        print(f"   1. Review all changes carefully")
        print(f"   2. Manually convert @prompt_template decorators")
        print(f"   3. Convert BaseTool classes to @llm.tool functions")
        print(f"   4. Replace BaseDynamicConfig with Context or f-strings")
        print(f"   5. Run tests to verify functionality")
        print(f"   6. Commit changes")


if __name__ == "__main__":
    main()

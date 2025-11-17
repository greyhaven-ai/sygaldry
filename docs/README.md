# Documentation Directory

This directory contains documentation that doesn't need to be at the project root.

## Contents

### Active Documentation

- **[AGENT_DEPENDENCIES.md](AGENT_DEPENDENCIES.md)** - Optional dependencies required for each agent
- **[README_PYPI.md](README_PYPI.md)** - PyPI-specific README for package distribution
- **[TEST_STATUS_REPORT.md](TEST_STATUS_REPORT.md)** - Test suite status and issues

### Archived Documentation

The **[archive/](archive/)** directory contains historical documentation:

- **Migration documentation** - Mirascope v1 to v2 migration docs (completed Nov 2024)
- **PR descriptions** - Historical pull request descriptions

## Root Documentation Files

These files remain at the project root for accessibility:

- **README.md** - Main project README (for GitHub, PyPI, etc.)
- **CLAUDE.md** - Comprehensive development guide and context for Claude Code
- **CONTRIBUTING.md** - Contributing guidelines for open source contributors
- **AGENT.md** - Generated docs for Amp Code editor (via `sygaldry docs generate --editor amp_code`)
- **AGENTS.md** - Generated docs for OpenAI Codex (via `sygaldry docs generate --editor openai_codex`)

## Generating Documentation

Use the Sygaldry CLI to generate editor-specific documentation:

```bash
# Generate documentation for different editors
sygaldry docs generate --editor cursor       # Creates .cursor/rules/sygaldry.mdc
sygaldry docs generate --editor claude       # Updates CLAUDE.md
sygaldry docs generate --editor windsurf     # Creates .windsurfrules
sygaldry docs generate --editor openai_codex # Updates AGENTS.md
sygaldry docs generate --editor amp_code     # Updates AGENT.md

# Generate documentation for specific component types
sygaldry docs generate --type agent
sygaldry docs generate --type tool

# Generate template for new component
sygaldry docs template my_component_name
```

## Documentation Standards

All documentation should:

1. Use clear, concise language
2. Include code examples where appropriate
3. Be kept up to date with code changes
4. Follow markdown best practices
5. Link to related documentation

## Contributing to Documentation

When adding new documentation:

1. Place general docs in this `docs/` directory
2. Place examples in `examples/` directory
3. Keep only essential files at root (README, CLAUDE, CONTRIBUTING)
4. Update this README to list new documentation
5. Ensure cross-links work correctly

---

**Need help?** See the main [README](../README.md) or [CONTRIBUTING](../CONTRIBUTING.md) guide.
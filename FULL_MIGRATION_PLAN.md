# Complete Mirascope v2 Migration Plan

## Executive Summary

**Current Status**: Ready to begin full migration
**Estimated Effort**: 40-60 hours
**Risk Level**: HIGH (v2 is alpha, may have breaking changes)
**Recommendation**: Proceed only if timeline permits and alpha stability is acceptable

## What We've Accomplished

✅ Created migration branch: `claude/mirascope-v2-migration-011CV4jd43t5GGpWW86BfEa1`
✅ Updated `pyproject.toml` to `mirascope>=2.0.0a1`
✅ Installed Mirascope v2.0.0-alpha.1
✅ Tested and verified v2 API patterns work
✅ Documented all breaking changes
✅ Cataloged all files requiring updates

## Migration Scope

### Files to Migrate
- **45 files** with mirascope imports
- **247 usages** of `@prompt_template`
- **8 usages** of `BaseTool` classes
- **97 usages** of `BaseDynamicConfig`

### Breakdown by Component
- **20+ agent files** in `packages/sygaldry_registry/components/agents/`
- **10+ prompt template files** in `packages/sygaldry_registry/components/prompt_templates/`
- **20+ test files** in `tests/unit/agents/` and `tests/integration/`
- **1 test helper file**: `tests/utils/mirascope_test_helpers.py`

## What Needs to Be Done

### 1. Import Changes (45 files, ~2-3 hours)

**Before:**
```python
from mirascope import BaseDynamicConfig, BaseTool, llm, prompt_template
```

**After:**
```python
from mirascope import llm
```

### 2. Decorator Changes (247+ instances, ~12-16 hours)

#### Prompt Templates
**Before:**
```python
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Analysis)
@prompt_template(
    """
    Analyze this text:
    {text}

    Consider: {focus_areas}
    """
)
async def analyze_text(text: str, focus_areas: str):
    pass
```

**After:**
```python
@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=Analysis)
async def analyze_text(text: str, focus_areas: str) -> str:
    return f"""Analyze this text:
{text}

Consider: {focus_areas}
"""
```

**Changes:**
- Remove `@prompt_template` decorator entirely
- Function must return string (the prompt)
- Change `{variable}` → use f-strings directly
- Update `@llm.call` parameters (see below)

#### LLM Call Decorator
**Before:**
```python
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=MyModel
)
```

**After:**
```python
@llm.call(
    provider="openai:completions",  # Add :completions or :responses
    model_id="gpt-4o-mini",          # model → model_id
    format=MyModel                    # response_model → format
)
```

### 3. Tool Conversions (7 tools in POC alone, ~4-6 hours)

**Before (Class-based):**
```python
class WebSearchTool(BaseTool):
    """Search the web for information."""

    query: str = Field(..., description="Search query")
    max_results: int = Field(default=5, description="Max results")

    def call(self) -> str:
        """Execute search."""
        results = []
        # Search logic here
        return "\n\n".join(results)
```

**After (Function-based):**
```python
@llm.tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information.

    Args:
        query: Search query
        max_results: Max results

    Returns:
        Search results
    """
    results = []
    # Search logic here (same as before)
    return "\n\n".join(results)
```

**Changes:**
- Convert class → function
- `BaseTool` → `@llm.tool`
- Pydantic fields → function parameters
- `.call()` method → function body
- Field descriptions → docstring Args section

### 4. BaseDynamicConfig Pattern (97 usages, ~8-12 hours)

**Before:**
```python
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Result)
@prompt_template("Process {data} with {context}")
def process_data(data: str, context: dict) -> BaseDynamicConfig:
    computed_context = f"Context: {context['key']}"
    return {
        "computed_fields": {
            "data": data,
            "context": computed_context
        }
    }
```

**After (Two Options):**

**Option A - Simple (no context needed):**
```python
@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=Result)
def process_data(data: str, context: dict) -> str:
    computed_context = f"Context: {context['key']}"
    return f"Process {data} with {computed_context}"
```

**Option B - With Context:**
```python
from dataclasses import dataclass

@dataclass
class ProcessingContext:
    key: str

@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=Result)
def process_data(ctx: llm.Context[ProcessingContext], data: str) -> str:
    return f"Process {data} with Context: {ctx.deps.key}"

# Usage:
ctx = llm.Context(deps=ProcessingContext(key="value"))
result = process_data(ctx, "my data")
```

### 5. Test Infrastructure Updates (~8-12 hours)

**Files:**
- `tests/utils/mirascope_test_helpers.py`
- All test files using Mirascope mocks

**Required Changes:**
- Update mock patterns for v2 API
- Change decorator assertions
- Update import checks
- Modify response model validations

### 6. Documentation Updates (~2-4 hours)

**Files:**
- `CLAUDE.md`
- Component `README.md` files
- Example files
- Migration guides

## Detailed Migration Steps (TDD Approach)

### Phase 1: POC - multi_source_news_verification Agent (6-8 hours)

1. **Write Tests First**
   - Create v2-compatible tests for the agent
   - Mock v2 API responses
   - Test each tool function

2. **Migrate Code**
   - Update imports
   - Convert 7 BaseTool classes → @llm.tool functions
   - Convert all @llm.call decorators
   - Convert all @prompt_template decorators
   - Handle BaseDynamicConfig usages

3. **Run Tests**
   - Fix failures iteratively
   - Verify all functionality works
   - Document any issues

4. **Validate POC**
   - If successful → proceed to remaining agents
   - If problematic → reassess approach

### Phase 2: Remaining Agents (16-24 hours)

Apply POC pattern to 19+ remaining agent files:
- text_summarization
- knowledge_graph
- hallucination_detector
- web_search
- code_generation_execution
- pii_scrubbing
- document_segmentation
- ... and 12+ more

### Phase 3: Prompt Templates (4-6 hours)

Migrate standalone prompt template files:
- `packages/sygaldry_registry/components/prompt_templates/text_based/`
- Convert 247 @prompt_template usages

### Phase 4: Test Infrastructure (8-12 hours)

- Update `mirascope_test_helpers.py`
- Fix all unit tests
- Fix all integration tests
- Add new v2-specific test patterns

### Phase 5: Documentation & Cleanup (2-4 hours)

- Update CLAUDE.md
- Update component READMEs
- Update examples
- Final verification

### Phase 6: E2E Testing (4-8 hours)

- Run full test suite
- Manual testing of key agents
- Performance validation
- Edge case testing

## Risk Assessment

### HIGH RISKS
- ⚠️ **Alpha Stability**: v2.0.0-alpha.1 may have bugs
- ⚠️ **Breaking Changes**: Further changes possible before stable
- ⚠️ **Incomplete Features**: Template parameter not implemented
- ⚠️ **Documentation**: Limited v2 documentation available

### MEDIUM RISKS
- ⚙️ **Effort Underestimation**: Could take longer than 60 hours
- ⚙️ **Testing Gaps**: May miss edge cases in migration
- ⚙️ **Integration Issues**: Components may interact unexpectedly

### LOW RISKS
- ✓ **API Changes Documented**: We understand the changes
- ✓ **Test Coverage**: Good existing test coverage
- ✓ **Rollback Option**: Can revert to v1 if needed

## Recommendations

### Recommendation 1: WAIT FOR STABLE v2
**Best for**: Production stability, minimal risk

- Stay on Mirascope v1.24.0+ (current stable)
- Monitor v2 progress toward stable release
- Migrate when v2 reaches beta or stable
- **Timeline**: Wait 3-6 months for v2 stable

### Recommendation 2: PROCEED WITH ALPHA MIGRATION
**Best for**: Early adoption, feature exploration

- Full migration to v2.0.0-alpha.1
- Estimated effort: 40-60 hours
- High risk of additional changes needed
- **Timeline**: Start immediately

### Recommendation 3: HYBRID APPROACH
**Best for**: Balanced risk/reward

- Create compatibility layer wrapping v2 API
- Gradual migration of components
- Maintain v1 compatibility temporarily
- **Timeline**: 2-4 weeks with gradual rollout

## Decision Points

**To proceed with full migration, I need your confirmation on:**

1. ✅ **Accept alpha risk**: Understand v2 may have bugs and changes
2. ✅ **Allocate time**: 40-60 hours of development time available
3. ✅ **Testing commitment**: Comprehensive testing after migration
4. ✅ **Rollback plan**: Prepared to revert if critical issues arise

**OR**

❌ **Wait for stable v2**: Postpone migration until v2 is production-ready

## Next Immediate Steps (If Proceeding)

1. Start POC with `multi_source_news_verification` agent
2. Write v2-compatible tests
3. Migrate agent code
4. Validate tests pass
5. If successful, proceed to remaining agents

**Should I proceed with the migration? Please confirm:**
- [ ] Yes, proceed with full v2 migration
- [ ] No, wait for stable v2
- [ ] Yes, but start with POC only and pause for review

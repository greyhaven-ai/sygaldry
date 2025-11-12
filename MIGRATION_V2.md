# Mirascope v2 Migration Guide

## v2 API Patterns (Verified Working)

### 1. Imports
```python
# v1
from mirascope import llm, prompt_template, BaseTool, BaseDynamicConfig

# v2
from mirascope import llm
```

### 2. Prompt Templates
```python
# v1
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Answer)
@prompt_template("Answer this question: {question}")
def answer_question(question: str): ...

# v2
@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=Answer)
def answer_question(question: str) -> str:
    return f"Answer this question: {question}"
```

**Key Changes:**
- NO `@prompt_template` decorator (template parameter not implemented in alpha)
- Function MUST return a string (the prompt)
- Use f-strings for variable interpolation
- No special `{variable}` syntax needed

### 3. LLM Call Decorator
```python
# v1
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=MyModel
)

# v2
@llm.call(
    provider="openai:completions",  # or "openai:responses"
    model_id="gpt-4o-mini",
    format=MyModel  # replaces response_model
)
```

**Key Changes:**
- `provider` now includes API type: `"openai:completions"` or `"openai:responses"`
- `model` → `model_id`
- `response_model` → `format`

### 4. Tools
```python
# v1
class WebSearchTool(BaseTool):
    query: str = Field(..., description="Search query")

    def call(self) -> str:
        return f"Results for: {self.query}"

# v2
@llm.tool
def web_search(query: str) -> str:
    """Search the web.

    Args:
        query: Search query

    Returns:
        Search results
    """
    return f"Results for: {query}"
```

**Key Changes:**
- Class-based → Function-based
- `BaseTool` → `@llm.tool`
- `.call()` method → just the function body
- Pydantic fields → function parameters
- Field descriptions → docstring Args section

### 5. Context Pattern
```python
# v1
from mirascope import BaseDynamicConfig

@llm.call(...)
@prompt_template("...")
def my_func(...) -> BaseDynamicConfig:
    return {"computed_fields": {...}}

# v2
@llm.call(...)
def my_func(ctx: llm.Context[MyDataclass], ...) -> str:
    return f"Using {ctx.deps.field}..."

# Usage:
ctx = llm.Context(deps=MyDataclass(...))
result = my_func(ctx, ...)
```

**Key Changes:**
- `BaseDynamicConfig` → `llm.Context[T]`
- Context must be first parameter
- Return string instead of dict
- Create context with `llm.Context(deps=...)`

### 6. Async Support
```python
# Both v1 and v2 support async
@llm.call(provider="openai:completions", model_id="gpt-4o-mini")
async def answer_question(question: str) -> str:
    return f"Answer: {question}"

# Usage:
response = await answer_question("What is AI?")
```

## Migration Checklist

### Phase 1: Preparation
- [ ] Update `pyproject.toml`: `mirascope>=2.0.0a1`
- [ ] Install v2: `pip install --upgrade mirascope>=2.0.0a1`
- [ ] Run existing tests to establish baseline failures

### Phase 2: Imports
- [ ] Remove `prompt_template` from imports
- [ ] Remove `BaseTool` from imports
- [ ] Remove `BaseDynamicConfig` from imports
- [ ] Keep only `from mirascope import llm`

### Phase 3: Decorators
- [ ] Convert all `@prompt_template()` → remove decorator
- [ ] Update functions to return f-strings
- [ ] Update `@llm.call()` parameters:
  - [ ] `provider="openai"` → `provider="openai:completions"`
  - [ ] `model="..."` → `model_id="..."`
  - [ ] `response_model=X` → `format=X`

### Phase 4: Tools
- [ ] Convert each `BaseTool` class to `@llm.tool` function
- [ ] Move `call()` logic to function body
- [ ] Convert Pydantic fields to function parameters
- [ ] Move field descriptions to docstrings

### Phase 5: Context/Dynamic Config
- [ ] Replace `BaseDynamicConfig` with `llm.Context[T]`
- [ ] Add context parameter as first param
- [ ] Update return values from dict to string
- [ ] Update call sites to create and pass context

### Phase 6: Testing
- [ ] Update test helpers
- [ ] Write tests for each migrated component
- [ ] Run full test suite
- [ ] Fix any failures

### Phase 7: Documentation
- [ ] Update examples
- [ ] Update README
- [ ] Update CLAUDE.md

## Estimated Effort

| Task | Files | Hours |
|------|-------|-------|
| Import updates | 30+ | 2-3 |
| Decorator updates | 30+ | 8-12 |
| Tool conversions | 7 | 4-6 |
| Context pattern | ~10 | 4-6 |
| Test updates | 20+ | 8-12 |
| E2E verification | All | 4-8 |
| Documentation | - | 2-4 |
| **Total** | | **32-51 hours** |

## Known Issues (v2.0.0-alpha.1)

1. **Template parameter not implemented**: `@llm.prompt(template="...")` raises `NotImplementedError`
2. **Alpha stability**: May have bugs or additional breaking changes
3. **Documentation incomplete**: Many v2 features lack documentation
4. **Provider changes**: OpenAI now requires `:completions` or `:responses` suffix

## Next Steps

1. Catalog all files needing updates
2. Start with one agent as proof-of-concept
3. Iterate with TDD approach
4. Expand to all components once pattern validated

# Mirascope v2 Migration Status

## ✅ Completed

### 1. Research & Documentation (Complete)
- [x] Installed and tested Mirascope v2.0.0-alpha.1
- [x] Verified all v2 API patterns work (`test_v2_api.py`)
- [x] Created comprehensive migration guide (`MIGRATION_V2.md`)
- [x] Cataloged all files requiring changes (`MIGRATION_CATALOG.md`)
- [x] Created detailed migration plan (`FULL_MIGRATION_PLAN.md`)

### 2. POC Agent - Tools Conversion (Complete)
- [x] Converted all 7 BaseTool classes to @llm.tool functions:
  - `WebSearchTool` → `web_search()`
  - `FactCheckSearchTool` → `fact_check_search()`
  - `AcademicSearchTool` → `academic_search()`
  - `GovernmentDataTool` → `government_data_search()`
  - `ReverseImageSearchTool` → `reverse_image_search()`
  - `SocialMediaVerificationTool` → `social_media_verification()`
  - `ExpertSourceTool` → `expert_source_search()`
- [x] All tool functions tested and working
- [x] File: `agent_v2.py` (partial)

### 3. Migration Automation (Complete)
- [x] Created `migrate_to_v2.py` automation script
- [x] Script handles:
  - Import updates
  - @llm.call decorator parameter updates
  - Detection of manual conversion needs

## 🚧 In Progress / Remaining

### 4. POC Agent - Function Conversions (0% complete)
Files: `packages/sygaldry_registry/components/agents/multi_source_news_verification/agent_v2.py`

**Functions to convert (5):**

#### a. `assess_source_credibility()` (lines 517-583)
**Current (v1):**
```python
@llm.call(provider="openai", model="gpt-4o", response_model=list[SourceCredibility], tools=[WebSearchTool])
@prompt_template("""SYSTEM: ... USER: ... {sources} {context}...""")
def assess_source_credibility(sources, context="", topic_area="", time_period="current"):
    pass
```

**Needs to become (v2):**
```python
@llm.call(provider="openai:completions", model_id="gpt-4o", format=list[SourceCredibility], tools=[web_search])
def assess_source_credibility(sources, context="", topic_area="", time_period="current") -> str:
    return f"""SYSTEM:
You are an expert media literacy specialist...

USER:
Assess the credibility of these news sources:

Sources: {sources}
Context: {context}
Topic Area: {topic_area}
Time Period: {time_period}
..."""
```

**Effort:** ~30 minutes (long template to convert)

#### b. `analyze_news_content()` (lines 586-665)
- Similar conversion pattern
- **Effort:** ~30 minutes

#### c. `fact_check_claims()` (lines 668-759)
- Has 7 tools in decorator
- **Effort:** ~45 minutes

#### d. `create_media_literacy_report()` (lines 762-820)
- Uses `BaseDynamicConfig` return
- Needs conversion to simple return string
- **Effort:** ~30 minutes

#### e. `synthesize_news_verification()` (lines 823-888)
- Uses `BaseDynamicConfig` return
- **Effort:** ~30 minutes

**Total Function Conversion:** ~3 hours

### 5. POC Agent - Main Functions (0% complete)
- [ ] `multi_source_news_verification()` (lines 891-1103)
  - Main orchestration function
  - 200+ lines
  - **Effort:** ~1 hour

- [ ] `multi_source_news_verification_stream()` (lines 1106-1201)
  - Streaming variant
  - **Effort:** ~30 minutes

### 6. POC Agent - Testing (0% complete)
- [ ] Update test file for v2 API
- [ ] Run tests
- [ ] Fix failures
- **Effort:** ~2 hours

### 7. Apply to All Agents (0% complete)
Using POC as template, convert:
- [ ] 19 remaining agent files
- **Effort:** ~20-30 hours (1-1.5 hours per agent)

### 8. Test Infrastructure (0% complete)
- [ ] Update `tests/utils/mirascope_test_helpers.py`
- [ ] Fix all unit tests
- [ ] Fix all integration tests
- **Effort:** ~8-12 hours

### 9. Documentation (0% complete)
- [ ] Update `CLAUDE.md`
- [ ] Update component READMEs
- [ ] Update examples
- **Effort:** ~2-4 hours

### 10. Final Verification (0% complete)
- [ ] Run full test suite
- [ ] E2E testing
- [ ] Performance validation
- **Effort:** ~4-8 hours

## Summary

**Completed:** ~8 hours of work
**Remaining:** ~40-55 hours of work

### Critical Path Forward

**Immediate Next Steps (to complete POC):**
1. Convert 5 agent functions in `agent_v2.py` (~3 hours)
2. Complete main orchestration functions (~1.5 hours)
3. Update and run tests (~2 hours)
4. **Total to complete POC:** ~6.5 hours

**After POC Success:**
5. Use automation script + manual review for remaining agents (~25 hours)
6. Update test infrastructure (~10 hours)
7. Documentation and final verification (~6 hours)

**Total remaining:** ~41 hours

## Risk Assessment

**Risks Identified:**
- ⚠️ **Alpha stability**: v2 may have bugs or breaking changes
- ⚠️ **Template conversion complexity**: Large templates prone to errors
- ⚠️ **Test coverage gaps**: May miss edge cases
- ⚠️ **Time estimation**: Could take 50+ hours total

**Mitigation:**
- ✅ TDD approach ensures correctness
- ✅ POC validates pattern before full rollout
- ✅ Comprehensive documentation for consistency
- ✅ Automation reduces manual errors

## Decision Point

**Options:**
1. **Continue migration** (~41 hours remaining)
2. **Wait for v2 stable** (safer, 3-6 months)
3. **Hybrid**: Keep v1, selectively adopt v2 features

**Recommendation:**
Given alpha status and substantial effort, **waiting for v2 stable** may be prudent unless:
- Early v2 features are critical
- Team has bandwidth for 40+ hours
- Can accept risk of additional changes

## Files Changed

- ✅ `pyproject.toml` - Updated to v2
- ✅ `test_v2_api.py` - Working v2 examples
- ✅ `MIGRATION_V2.md` - API documentation
- ✅ `MIGRATION_CATALOG.md` - Scope analysis
- ✅ `FULL_MIGRATION_PLAN.md` - Detailed plan
- ✅ `migrate_to_v2.py` - Automation script
- 🚧 `agent_v2.py` - Partial (tools done, functions pending)

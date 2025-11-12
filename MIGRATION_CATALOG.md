# Migration Catalog

## Summary Statistics
- **Files with mirascope imports**: 45
- **prompt_template usages**: 247
- **BaseTool usages**: 8
- **BaseDynamicConfig usages**: 97

## Total Estimated Effort: 40-60 hours

## Migration Strategy

### Approach: Incremental with Proof-of-Concept

1. **POC Agent** (4-6 hours): `multi_source_news_verification`
   - Has BaseTool classes (7 tools)
   - Complex agent with multiple patterns
   - Good test coverage
   - If POC succeeds, apply pattern to remaining agents

2. **Core Agents** (12-16 hours): Migrate remaining 19 agent files
3. **Prompt Templates** (8-12 hours): Migrate 10+ template files
4. **Test Infrastructure** (8-12 hours): Update test helpers and all tests
5. **Documentation** (4-8 hours): Update examples and docs
6. **E2E Verification** (4-8 hours): Full regression testing

## Files Requiring Migration

### Phase 1: POC - multi_source_news_verification
- `packages/sygaldry_registry/components/agents/multi_source_news_verification/agent.py`
  - 7 BaseTool classes → @llm.tool functions
  - Multiple @llm.call decorators
  - Complex prompt patterns

### Phase 2: Agents with BaseDynamicConfig
Files using BaseDynamicConfig (high complexity):
- `multi_agent_coordinator/agent.py`
- `prompt_templates/text_based/chain_of_thought.py`
- `prompt_templates/text_based/structured_output.py`
- And ~94 other usages

### Phase 3: All Other Agents
Agent files (20+ files):
- `text_summarization/agent.py`
- `knowledge_graph/agent.py`
- `hallucination_detector/agent.py`
- `web_search/agent.py`
- `code_generation_execution/agent.py`
- `pii_scrubbing/agent.py`
- `document_segmentation/agent.py`
- ... (15+ more)

### Phase 4: Test Infrastructure
- `tests/utils/mirascope_test_helpers.py`
- All test files in `tests/unit/agents/`
- All test files in `tests/integration/`

## Next Steps

1. Start with POC: multi_source_news_verification agent
2. Create tests for v2 version
3. Migrate code with TDD
4. Verify tests pass
5. If successful, apply pattern to remaining agents

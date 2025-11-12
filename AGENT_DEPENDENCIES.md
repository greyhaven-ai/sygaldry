# Agent Dependency Requirements

This document lists the optional dependencies required for each agent in the Sygaldry registry.

## Installation Guide

### Core Installation
```bash
pip install sygaldry-cli
```

### Install with Agent Support
```bash
# For basic agent support
pip install sygaldry-cli[agents]

# For specific agent categories
pip install sygaldry-cli[agents,search]
pip install sygaldry-cli[agents,search,observability]

# For all agent dependencies
pip install sygaldry-cli[all-agents]
```

## Dependency Categories

### Available Extras

| Extra | Purpose | Packages |
|-------|---------|----------|
| `agents` | Core agent support (required for any agent) | mirascope>=2.0.0a1 |
| `observability` | LLM call observability | lilypad-sdk |
| `async-io` | Async file operations | aiofiles |
| `search` | Web and AI search | duckduckgo-search, exa-py |
| `database` | Database support | sqlalchemy, asyncpg, psycopg2-binary, alembic |
| `web` | Web scraping/parsing | beautifulsoup4, firecrawl-py, lxml |
| `documents` | Document processing | PyPDF2, python-docx, markdown, python-frontmatter |
| `git` | Git/GitHub integration | GitPython, PyGithub |
| `data` | Data processing | pandas, jsonpath-ng, pyyaml |
| `fuzzy` | Fuzzy string matching | fuzzywuzzy, python-Levenshtein |
| `youtube` | YouTube tools | youtube-transcript-api |
| `all-agents` | All agent dependencies | All of the above |

## Agent Requirements

### Simple Agents (Basic Dependencies Only)

#### sales_intelligence
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Find targeted sales prospects using Exa websets

#### market_intelligence
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Track investment opportunities and market trends

#### recruiting_assistant
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Find qualified candidates using Exa websets

#### sourcing_assistant
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Find suppliers and manufacturers

#### academic_research
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Find academic papers and research

#### web_search
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Unified web search across multiple providers

### Medium Complexity Agents

#### pii_scrubbing
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Detect and remove PII from text

### Standard Agents

#### hallucination_detector
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Verify factual claims using web search

#### research_assistant
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Conduct comprehensive research

#### knowledge_graph
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Extract entities and relationships from text

#### code_generation_execution
**Install**: `pip install sygaldry-cli[agents,async-io]`
- **Required**: `agents`, `async-io`
- **Purpose**: Generate and safely execute Python code

#### document_segmentation
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Segment documents into logical parts

#### game_playing_dnd
**Install**: `pip install sygaldry-cli[agents,database]`
- **Required**: `agents`, `database`
- **Purpose**: D&D 5e game master with persistent state

### Complex Agents

#### dataset_builder
**Install**: `pip install sygaldry-cli[agents,search]`
- **Required**: `agents`, `search`
- **Purpose**: Create curated datasets using Exa Websets

#### enhanced_knowledge_graph
**Install**: `pip install sygaldry-cli[agents,observability]`
- **Required**: `agents`, `observability`
- **Purpose**: Advanced knowledge graph extraction

#### text_summarization
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Multi-style text summarization

### Advanced Agents

#### dynamic_learning_path
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Generate personalized learning paths

#### game_playing_catan
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Settlers of Catan game agent

#### game_playing_diplomacy
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Diplomacy game agent

#### game_theory_analysis
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Analyze strategic situations

#### multi_agent_coordinator
**Install**: `pip install sygaldry-cli[agents,observability]`
- **Required**: `agents`, `observability`
- **Purpose**: Orchestrate multiple specialized agents

#### prompt_engineering_optimizer
**Install**: `pip install sygaldry-cli[agents,observability]`
- **Required**: `agents`, `observability`
- **Purpose**: Optimize prompts through A/B testing

### Most Complex Agents

#### decision_quality_assessor
**Install**: `pip install sygaldry-cli[agents,observability]`
- **Required**: `agents`, `observability`
- **Purpose**: Assess decision quality and detect biases

#### multi_platform_social_media_manager
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`
- **Purpose**: Multi-platform social media campaign management

#### multi_source_news_verification
**Install**: `pip install sygaldry-cli[agents,search,observability]`
- **Required**: `agents`, `search`, `observability`
- **Purpose**: Comprehensive news verification with fact-checking

## Tool Requirements

### Search Tools

#### duckduckgo_search_tool
**Install**: `pip install sygaldry-cli[search]`
- **Required**: `search`

#### exa_search_tools
**Install**: `pip install sygaldry-cli[search]`
- **Required**: `search`

#### qwant_search_tool
**Install**: `pip install sygaldry-cli[search]`
- **Required**: `search`

#### nimble_search_tool
**Install**: `pip install sygaldry-cli[search]`
- **Required**: `search`

#### exa_websets_tool
**Install**: `pip install sygaldry-cli[search]`
- **Required**: `search`

### Document Tools

#### pdf_search_tool
**Install**: `pip install sygaldry-cli[documents]`
- **Required**: `documents`

#### docx_search_tool
**Install**: `pip install sygaldry-cli[documents]`
- **Required**: `documents`

#### mdx_search_tool
**Install**: `pip install sygaldry-cli[documents,web]`
- **Required**: `documents`, `web`

#### csv_search_tool
**Install**: `pip install sygaldry-cli[data]`
- **Required**: `data`

#### json_search_tool
**Install**: `pip install sygaldry-cli[data]`
- **Required**: `data`

#### xml_search_tool
**Install**: `pip install sygaldry-cli[web]`
- **Required**: `web`

### Database Tools

#### sqlalchemy_db
**Install**: `pip install sygaldry-cli[database]`
- **Required**: `database`

#### sqlite_db
**Install**: `pip install sygaldry-cli[database]`
- **Required**: `database`

#### pg_search_tool
**Install**: `pip install sygaldry-cli[database]`
- **Required**: `database`

### Web Tools

#### firecrawl_scrape_tool
**Install**: `pip install sygaldry-cli[web]`
- **Required**: `web`

#### url_content_parser_tool
**Install**: `pip install sygaldry-cli[web]`
- **Required**: `web`

### Git Tools

#### git_repo_search_tool
**Install**: `pip install sygaldry-cli[git]`
- **Required**: `git`

### Specialized Tools

#### code_interpreter_tool
**Install**: `pip install sygaldry-cli[async-io]`
- **Required**: `async-io`

#### youtube_video_search_tool
**Install**: `pip install sygaldry-cli[youtube]`
- **Required**: `youtube`

#### dice_roller
**Install**: `pip install sygaldry-cli[agents]`
- **Required**: `agents`

#### dnd_5e_api
**Install**: `pip install sygaldry-cli`
- **Required**: (no extras needed)

## Common Installation Patterns

### For Search-Based Agents
Most agents that do web research or intelligence gathering:
```bash
pip install sygaldry-cli[agents,search]
```

### For Game Agents
Agents that need state persistence:
```bash
pip install sygaldry-cli[agents,database]
```

### For Advanced Monitoring
Agents with observability requirements:
```bash
pip install sygaldry-cli[agents,observability]
```

### For Full Development
Install everything for development:
```bash
pip install sygaldry-cli[dev]
```

## Troubleshooting

### ImportError: No module named 'lilypad'
Install observability support:
```bash
pip install sygaldry-cli[observability]
```

### ImportError: No module named 'aiofiles'
Install async I/O support:
```bash
pip install sygaldry-cli[async-io]
```

### ImportError: No module named 'duckduckgo_search'
Install search tools:
```bash
pip install sygaldry-cli[search]
```

### ImportError: No module named 'exa_py'
Install search tools:
```bash
pip install sygaldry-cli[search]
```

## Migration from v1

After the Mirascope v2 migration, all agents now use:
- `@llm.call` decorator with `provider="openai:completions"`, `model_id=`, and `format=`
- Functional prompts (return f-strings) instead of `@prompt_template` decorators
- `@llm.tool` functions instead of `BaseTool` classes

The dependency structure has been reorganized to allow granular installation of only what you need.

## See Also

- [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md) - Complete v2 migration details
- [CLAUDE.md](./CLAUDE.md) - Development best practices and patterns
- [pyproject.toml](./pyproject.toml) - Full dependency specifications

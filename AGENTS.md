# Sygaldry Development Guidelines

## Context

Sygaldry is an AI framework for building LLM-powered applications with reusable components.

## Core Technologies

- Python 3.12+ with type hints
- Mirascope for LLM integration
- Pydantic for data validation
- Component-based architecture

## Development Standards

### Mirascope Integration

- Use `@prompt_template` decorators
- Define Pydantic response models
- Implement async/await patterns
- Support multiple LLM providers

### Component Structure

- component.json manifest required
- Registry dependencies managed
- Documentation in sygaldry.md format
- Comprehensive examples included

## Available Components

- **text_summarization_agent** (agent): Advanced text summarization agent using chain-of-thought reasoning, few-shot learning, and iterative refinement. Supports multiple styles (technical, executive, simple, academic, journalistic) and progressive summarization with validation.
- **multi_source_news_verification** (agent): Advanced multi-source news verification agent with comprehensive fact-checking tools including academic search, government data verification, social media verification, and expert source validation for combating misinformation
- **multi_agent_coordinator** (agent): Orchestrates multiple specialized agents to solve complex tasks through intelligent task decomposition, agent selection, and result synthesis
- **recruiting_assistant_agent** (agent): Recruiting assistant for finding qualified candidates using Exa websets. Helps with technical recruiting, sales hiring, and executive search.
- **game_theory_analysis** (agent): Analyzes complex strategic situations using game theory principles, identifying equilibria, predicting outcomes, and providing actionable recommendations
- **enhanced_knowledge_graph_agent** (agent): Enhanced knowledge graph extraction using advanced prompt engineering. Features meta-reasoning for strategy planning, chain-of-thought entity extraction with detailed reasoning, multi-pass relationship detection, and self-consistency validation for high-accuracy results.
- **document_segmentation_agent** (agent): Agent for intelligently segmenting documents into logical parts. Supports multiple strategies including semantic, structural, hybrid, and fixed-size segmentation. Features document structure analysis, segment summarization, and optimized chunking for vector embeddings.
- **knowledge_graph_agent** (agent): Agent for extracting structured knowledge from text by identifying entities and their relationships. Builds comprehensive knowledge graph representations with support for hierarchical relationships, graph enrichment, and visualization-ready outputs.
- **prompt_engineering_optimizer** (agent): Advanced prompt optimization agent that analyzes, generates variants, performs A/B testing, and delivers production-ready optimized prompts with comprehensive documentation
- **academic_research_agent** (agent): Academic research agent for finding research papers using Exa websets. Perfect for academics, researchers, and anyone needing to discover scholarly publications.
- **game_playing_catan** (agent): Multi-model turn-based Settlers of Catan game agent supporting AI vs AI, human vs AI, or mixed gameplay with resource management, trading, and strategic building
- **research_assistant_agent** (agent): AI-powered research agent that conducts comprehensive research using Exa search
- **pii_scrubbing_agent** (agent): Agent for detecting and removing Personally Identifiable Information (PII) from text. Combines regex patterns and LLM analysis for comprehensive PII detection. Supports multiple scrubbing methods including masking, redaction, generalization, and synthetic data replacement.
- **dataset_builder_agent** (agent): AI-powered dataset builder that creates curated data collections using Exa Websets with custom criteria and enrichments
- **dnd_game_master** (agent): A comprehensive D&D 5e game master agent with full rules enforcement and persistent campaign state. Features SQLite-based state persistence for multi-session campaigns, fair dice rolling with modifiers, complete D&D 5e API integration, multi-model orchestration, turn-based combat with positioning, spell slot tracking, condition management, death saves, XP/leveling, exhaustion, skill proficiencies, inventory management, and dynamic roleplay with human-in-the-loop support.
- **multi_platform_social_media_manager** (agent): Enhanced multi-platform social media campaign manager with trend analysis, engagement prediction, and real-time adaptation capabilities for comprehensive campaign orchestration
- **decision_quality_assessor** (agent): Comprehensive decision quality assessment agent that analyzes context, evaluates alternatives, detects cognitive biases, and provides actionable recommendations for better decision-making
- **sales_intelligence_agent** (agent): Sales intelligence agent for finding targeted business contacts and companies using Exa websets. Perfect for sales prospecting, lead generation, and market intelligence.
- **market_intelligence_agent** (agent): Market intelligence agent for tracking investment opportunities and market trends using Exa websets. Perfect for VCs, analysts, and business development professionals.
- **web_search_agent** (agent): Unified web search agent supporting multiple providers (DuckDuckGo, Qwant, Exa, Nimble) with configurable search strategies. Features privacy-focused, AI-powered semantic search, structured data extraction, comprehensive, and auto-selection modes.
- **game_playing_diplomacy** (agent): Multi-model turn-based Diplomacy game agent supporting AI vs AI, human vs AI, or mixed gameplay with sophisticated diplomatic negotiation and strategic planning
- **hallucination_detector_agent** (agent): AI-powered hallucination detection agent that verifies factual claims using Exa search
- **dynamic_learning_path** (agent): Generates personalized, adaptive learning paths based on individual skills, goals, and learning preferences with comprehensive resource curation
- **sourcing_assistant_agent** (agent): Sourcing assistant for finding suppliers, manufacturers, and solutions using Exa websets. Perfect for procurement, supply chain management, and technology sourcing.
- **code_generation_execution_agent** (agent): Agent for generating and safely executing Python code. Analyzes code for safety, supports multiple safety levels, and provides recommendations for improvement. Features sandboxed execution environment and comprehensive code analysis.
- **docx_search_tool** (tool): Microsoft Word document search and content extraction tool with advanced text search, regex support, and metadata extraction
- **directory_search_tool** (tool): Advanced file system navigation and search tool with pattern matching, content search, and filtering capabilities
- **sqlalchemy_db** (tool): SQLAlchemy ORM tool for advanced database operations and agent state management
- **firecrawl_scrape_tool** (tool): Firecrawl-powered web scraping tool that extracts clean, structured content from websites. Handles JavaScript-rendered pages and provides multiple output formats including Markdown, HTML, and screenshots.
- **git_repo_search_tool** (tool): Git repository search tool for searching code, files, and commits in both local Git repositories and GitHub. Supports pattern matching, file filtering, and commit history search.
- **code_interpreter_tool** (tool): Safe Python code execution tool with sandboxing, timeout controls, and variable capture
- **pg_search_tool** (tool): PostgreSQL database search and query tool with full-text search, connection pooling, and schema introspection
- **dice_roller** (tool): A fair and transparent dice rolling tool for tabletop RPGs. Supports all standard dice types (d4-d100), modifiers, advantage/disadvantage, and provides detailed roll results with timestamps.
- **mdx_search_tool** (tool): MDX documentation search tool with JSX component parsing, frontmatter support, and section extraction
- **csv_search_tool** (tool): CSV search tool for searching and filtering structured data within CSV files. Supports column-specific searches, data filtering, and both exact and fuzzy matching capabilities.
- **code_docs_search_tool** (tool): Technical documentation search tool for API docs, README files, code comments, docstrings, and code examples
- **json_search_tool** (tool): JSON search tool for searching and querying within JSON files and data structures. Supports JSONPath expressions, fuzzy matching, and searching in both keys and values.
- **pdf_search_tool** (tool): PDF search tool that enables searching for text within PDF documents using fuzzy matching. Extracts text from PDFs and provides context-aware search results with page numbers and match scores.
- **exa_websets_tool** (tool): Advanced web data collection tools using Exa Websets. Create curated collections of web data with search criteria and structured enrichments for building datasets.
- **dnd_5e_api** (tool): A comprehensive tool for accessing official D&D 5th Edition content via the D&D 5e API. Provides detailed information about spells, classes, monsters, equipment, races, feats, skills, conditions, magic items, and more. Includes advanced search with filters and support for all SRD content types.
- **url_content_parser_tool** (tool): URL content parsing tool that extracts clean text content from web pages. Removes scripts, styles, and other noise to provide readable text content.
- **sqlite_db** (tool): SQLite database tool for persistent agent state storage
- **nimble_search_tool** (tool): Multi-API search tool using Nimble's Web, SERP, and Maps APIs for comprehensive search capabilities
- **qwant_search_tool** (tool): Privacy-focused web search tools using Qwant search engine. Provides structured search results with no user tracking, using unified models compatible with other search providers.
- **duckduckgo_search_tool** (tool): DuckDuckGo web search tools with clean, structured results. Provides comprehensive search coverage using the duckduckgo-search library.
- **exa_search_tools** (tool): AI-powered search tools using Exa. Features neural search, direct Q&A, and similarity search with advanced filtering and relevance scoring.
- **youtube_video_search_tool** (tool): YouTube video search and transcript extraction tool for content analysis and research
- **xml_search_tool** (tool): XML data processing tool with XPath queries, namespace support, validation, and advanced search capabilities

## Environment Setup

- ANTHROPIC_API_KEY: API key for Anthropic services (if using Anthropic provider).
- ANTHROPIC_API_KEY: Anthropic API key for Claude models
- ANTHROPIC_API_KEY: Anthropic API key for Claude-based players
- DATABASE_URL: Database connection URL
- DATABASE_URL: PostgreSQL connection string
- EXA_API_KEY: API key for Exa AI search services (if using Exa provider).
- EXA_API_KEY: API key for Exa services
- EXA_API_KEY: API key for Exa services. Get it from https://exa.ai
- EXA_API_KEY: Exa API key for advanced web search (optional, enhances real-time verification)
- FIRECRAWL_API_KEY: API key for Firecrawl services
- GITHUB_TOKEN: GitHub personal access token for searching GitHub repositories
- GOOGLE_API_KEY: API key for Google services (if using Google provider).
- GOOGLE_API_KEY: Google API key for Gemini models
- GOOGLE_API_KEY: Google API key for Gemini-based players
- MISTRAL_API_KEY: Mistral API key for Mistral models
- NIMBLE_API_KEY: API key for Nimble search services (Web API, SERP API, Maps API) (if using Nimble provider).
- NIMBLE_API_KEY: API key for Nimble services
- OPENAI_API_KEY: API key for OpenAI services
- OPENAI_API_KEY: API key for OpenAI services (if using OpenAI provider).
- OPENAI_API_KEY: OpenAI API key for DM and AI players
- OPENAI_API_KEY: OpenAI API key for GPT models
- OPENAI_API_KEY: OpenAI API key for LLM calls
- YOUTUBE_API_KEY: YouTube Data API v3 key

## Best Practices

- Type all function signatures
- Use async for LLM calls
- Include error handling
- Write comprehensive tests

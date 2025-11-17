# Interactive Agent Testing Guide for Sygaldry

This guide helps you interactively test and explore the Sygaldry agents in a hands-on manner.

## Quick Start

### 1. Prerequisites

Ensure you have Python 3.8+ installed:
```bash
python3 --version
```

### 2. Set Up Virtual Environment (Recommended)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Install core requirements
pip install mirascope>=2.0.0a1 pydantic>=2.0.0 rich>=13.0.0

# Or use the requirements file
pip install -r examples/requirements-interactive.txt

# Optional: Install lilypad for observability
pip install lilypad
```

### 4. Set API Keys

You need at least one LLM API key:

```bash
# Option 1: OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Option 2: Anthropic (Claude)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Option 3: Google (Gemini)
export GOOGLE_API_KEY="your-google-api-key"

# For specific agents that use web search:
export EXA_API_KEY="your-exa-api-key"  # For Exa-powered agents
```

## Running the Interactive Tests

### Option 1: Simple Demo (Recommended for First-Time Users)

The simple demo showcases 4 core agents with predefined examples:

```bash
python3 examples/simple_agent_demo.py
```

This will demo:
- Text Summarization Agent
- Sentiment Analysis Agent
- PII Scrubbing Agent
- Code Review Agent

### Option 2: Full Interactive Tester

The full interactive tester allows you to test any agent with custom inputs:

```bash
python3 examples/interactive_agent_tester.py
```

Features:
- Browse all 30+ available agents
- Custom input for any agent function
- View example usage
- Test history tracking
- Rich terminal UI

## Available Agents

### Text Processing Agents
- **Text Summarization**: Multiple summarization styles (technical, executive, simple)
- **Sentiment Analysis**: Emotion detection and polarity analysis
- **PII Scrubbing**: Remove personally identifiable information
- **Document Segmentation**: Smart document chunking

### Code & Development Agents
- **Code Review**: Security and best practice analysis
- **Code Generation & Execution**: Safe code execution with sandboxing
- **Bug Triage**: Classify and prioritize bug reports

### Business & Analysis Agents
- **Contract Analysis**: Legal document review
- **Financial Statement Analyzer**: Financial metrics and insights
- **Task Prioritization**: Eisenhower matrix-based prioritization
- **Content Moderation**: Harmful content detection

### Research & Knowledge Agents
- **Academic Research**: Find scholarly papers
- **Hallucination Detector**: Fact-checking with web verification
- **Knowledge Graph**: Extract entities and relationships
- **Market Intelligence**: Investment and market trends

### Game & Entertainment Agents
- **D&D Game Master**: Full D&D 5e campaign management
- **Settlers of Catan**: Strategic board game AI
- **Diplomacy**: Negotiation and strategy game

### Specialized Agents
- **Multi-Platform Social Media Manager**: Campaign orchestration
- **Decision Quality Assessor**: Bias detection and decision analysis
- **Dynamic Learning Path**: Personalized education planning
- **Customer Support**: Multi-turn conversational support

## Testing Individual Agents Programmatically

You can also test agents directly in Python:

```python
# Example: Test Text Summarization
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages" / "sygaldry_registry"))

from components.agents.text_summarization import summarize_text

result = summarize_text(
    text="Your long text here...",
    style="executive",
    max_length=100
)

print(f"Summary: {result.summary}")
print(f"Confidence: {result.confidence_score}")
```

## Troubleshooting

### ModuleNotFoundError
If you get import errors, ensure:
1. You're in the project root directory
2. Dependencies are installed: `pip install mirascope pydantic rich`
3. The virtual environment is activated

### API Key Errors
If agents fail with API errors:
1. Verify your API keys are set: `echo $OPENAI_API_KEY`
2. Check the key is valid and has credits
3. Some agents require specific provider keys (check agent documentation)

### Rate Limiting
If you hit rate limits:
1. Add delays between tests
2. Use a different API key
3. Switch to a different provider

## Advanced Usage

### Custom Agent Testing

Create your own test script for specific agents:

```python
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages" / "sygaldry_registry"))

async def test_my_agent():
    from components.agents.your_agent import your_function

    # Your test code here
    result = await your_function(param1="value1", param2="value2")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_my_agent())
```

### Batch Testing

Test multiple agents in sequence:

```python
# See simple_agent_demo.py for an example of batch testing
```

### Integration Testing

Test agents with real tools:

```python
from components.tools.github_issues import GitHubIssuesTool
from components.agents.bug_triage import triage_bug

# Combine tools and agents for integration testing
```

## Next Steps

1. Start with `simple_agent_demo.py` to see agents in action
2. Use `interactive_agent_tester.py` to explore all agents
3. Check individual agent documentation in `packages/sygaldry_registry/components/agents/*/README.md`
4. Create custom test scripts for your specific use cases
5. Integrate agents into your applications

## Support

- Check agent-specific READMEs for detailed documentation
- Review the main [README.md](README.md) for project overview
- See [CLAUDE.md](CLAUDE.md) for development guidelines
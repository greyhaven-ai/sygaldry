# Sygaldry Examples

This directory contains interactive examples and testing tools for exploring Sygaldry agents.

## 📁 Files

### Interactive Testing Tools

1. **[simple_agent_demo.py](simple_agent_demo.py)** - Quick Start Demo
   - Pre-configured demos of 4 core agents
   - Easy to run, great for beginners
   - Showcases: Text Summarization, Sentiment Analysis, PII Scrubbing, Code Review

2. **[interactive_agent_tester.py](interactive_agent_tester.py)** - Full Interactive Tester
   - Test all 30+ agents with custom inputs
   - Rich terminal UI with menus
   - Test history tracking
   - Example parameters for each agent

3. **[agent_testing_notebook.ipynb](agent_testing_notebook.ipynb)** - Jupyter Notebook
   - Interactive notebook environment
   - Step-by-step testing walkthrough
   - Visual output formatting
   - Perfect for data scientists

### Production Testing with Logging & Auditing

4. **[agent_runner_with_logging.py](agent_runner_with_logging.py)** - Full Audit Logging
   - Run agents with comprehensive audit trails
   - JSONL structured logs + human-readable text logs
   - Session tracking with unique IDs
   - Performance metrics and error tracking
   - **Perfect for production testing and compliance**

5. **[run_scenarios.py](run_scenarios.py)** - Scenario-Based Testing
   - Run predefined realistic test scenarios
   - Automatic logging for all interactions
   - Categories: text processing, security, business, conversational
   - **Quick way to validate all agents**

6. **[view_logs.py](view_logs.py)** - Log Viewer & Analyzer
   - Browse and analyze audit logs
   - Session statistics and performance metrics
   - Filter by event type
   - Error analysis

7. **[test_scenarios.json](test_scenarios.json)** - Test Scenario Library
   - Realistic test cases for all agent types
   - Easily extensible for custom scenarios
   - Production-ready examples

8. **[AGENT_TESTING_WITH_LOGGING.md](AGENT_TESTING_WITH_LOGGING.md)** - Logging Guide
   - Complete logging and auditing documentation
   - Compliance and audit requirements
   - Log analysis techniques
   - Best practices

### Configuration & Documentation

9. **[ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md)** - Environment Variables Guide
   - Complete list of all API keys
   - What each key is used for
   - Where to get each key
   - Cost information and free tiers
   - **Start here for API key setup**

10. **[.env.example](.env.example)** - Environment Template
    - Copy to `.env` and fill in your keys
    - Organized by required vs optional
    - Comments for each variable

11. **[requirements-interactive.txt](requirements-interactive.txt)** - Python Dependencies
    - All packages needed for interactive testing
    - Install with: `pip install -r examples/requirements-interactive.txt`

12. **[INTERACTIVE_TESTING.md](INTERACTIVE_TESTING.md)** - Complete Guide
    - Detailed setup instructions
    - API key configuration
    - Troubleshooting tips
    - Advanced usage examples

### Other Examples

11. **[agent_with_persistent_state.py](agent_with_persistent_state.py)** - Stateful Agent Example
    - Demonstrates persistent state management
    - SQLite database integration

12. **[configuration_flow.md](configuration_flow.md)** - Configuration Guide
    - How to configure Sygaldry agents

## 🚀 Quick Start

### 1. Install Dependencies

From the project root:

```bash
pip install -r examples/requirements-interactive.txt
```

### 2. Set API Keys

```bash
export OPENAI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

### 3. Run a Demo

**Simple Demo** (recommended for first-time users):
```bash
python3 examples/simple_agent_demo.py
```

**Full Interactive Tester**:
```bash
python3 examples/interactive_agent_tester.py
```

**Scenario-Based Testing with Logging** (recommended for production testing):
```bash
# Run all predefined scenarios with full audit logging
python3 examples/run_scenarios.py

# Then view the audit logs
python3 examples/view_logs.py
```

**Jupyter Notebook**:
```bash
cd examples
jupyter notebook agent_testing_notebook.ipynb
```

### 4. Testing with Audit Logging

For production-ready testing with compliance-ready audit trails:

```bash
# Run realistic scenarios with full logging
python3 examples/run_scenarios.py

# View and analyze the logs
python3 examples/view_logs.py

# Or use the interactive runner
python3 examples/agent_runner_with_logging.py
```

All logs are saved to `logs/audit/` with:
- **JSONL format** - Structured, machine-readable logs
- **Text format** - Human-readable logs for quick review
- **Session tracking** - Unique IDs for each test session
- **Performance metrics** - Duration, success rates, error counts

📖 **See [AGENT_TESTING_WITH_LOGGING.md](AGENT_TESTING_WITH_LOGGING.md)** for complete logging documentation.

## 📚 What You Can Test

### Text Processing
- Text Summarization (multiple styles)
- Sentiment Analysis
- PII Scrubbing

### Code & Development
- Code Review
- Bug Triage
- Code Generation & Execution

### Business & Analysis
- Contract Analysis
- Financial Statement Analysis
- Task Prioritization
- Content Moderation

### Research & Knowledge
- Academic Research
- Hallucination Detection
- Knowledge Graph Extraction
- Multi-Source News Verification

### Customer Support
- Multi-turn Conversational Support
- Ticket Classification

### Games
- D&D Game Master (full 5e support)
- Settlers of Catan
- Diplomacy

...and 20+ more agents!

## 💡 Usage Tips

### Interactive Tester Features
- **Menu-driven interface** - Easy navigation through agents
- **Custom or example inputs** - Test with your data or use examples
- **Real-time results** - See agent responses immediately
- **Error handling** - Helpful error messages and debugging

### Simple Demo Features
- **Pre-configured examples** - No setup needed
- **Sequential demos** - Run all or pick specific ones
- **Formatted output** - Beautiful terminal display

### Jupyter Notebook Features
- **Visual output** - Formatted results with colors
- **Interactive cells** - Modify and re-run easily
- **Educational** - Step-by-step walkthroughs
- **Shareable** - Export results and share

## 🔧 Troubleshooting

### Import Errors
If you get module import errors:
```bash
# Make sure you're running from the project root
cd /path/to/sygaldry
python3 examples/simple_agent_demo.py
```

### API Key Issues
If agents fail with API errors:
```bash
# Verify your key is set
echo $OPENAI_API_KEY

# Set it if needed
export OPENAI_API_KEY="your-key"
```

### Missing Dependencies
```bash
# Install all required packages
pip install -r examples/requirements-interactive.txt
```

## 📖 Learn More

- **Full Testing Guide**: See [INTERACTIVE_TESTING.md](INTERACTIVE_TESTING.md)
- **Agent Documentation**: Check `packages/sygaldry_registry/components/agents/*/README.md`
- **Main README**: See [../README.md](../README.md)
- **Development Guide**: See [../CLAUDE.md](../CLAUDE.md)

## 🎯 Next Steps

1. Start with `simple_agent_demo.py` to see agents in action
2. Try `interactive_agent_tester.py` to explore all agents
3. Open `agent_testing_notebook.ipynb` for an interactive experience
4. Read individual agent READMEs for detailed documentation
5. Integrate agents into your own applications!

## 🤝 Contributing

Found a bug or want to add more examples? Contributions welcome!

1. Add new example scripts to this directory
2. Update this README with your example
3. Submit a pull request

---

**Need help?** Check [INTERACTIVE_TESTING.md](INTERACTIVE_TESTING.md) for detailed documentation.
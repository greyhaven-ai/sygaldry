# Environment Variables Setup Guide

This guide explains all environment variables needed to test and use Sygaldry agents.

## 📋 Quick Reference

Copy [`examples/.env.example`](.env.example) to `.env` and fill in your API keys:

```bash
cp examples/.env.example .env
# Edit .env with your API keys
```

## 🔑 Required Keys (Choose at least ONE)

You need **at least one LLM provider** API key to run agents:

### OpenAI (Recommended for most agents)
```bash
export OPENAI_API_KEY="sk-..."
```

- **What it's for**: GPT-4, GPT-3.5, and other OpenAI models
- **Used by**: Most agents (default provider)
- **Get it from**: https://platform.openai.com/api-keys
- **Cost**: Pay-as-you-go, ~$0.01-0.06 per 1K tokens depending on model

### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

- **What it's for**: Claude 3.5 Sonnet, Claude 3 Opus/Haiku
- **Used by**: All agents (when configured with `provider="anthropic"`)
- **Get it from**: https://console.anthropic.com/
- **Cost**: Pay-as-you-go, ~$0.003-0.015 per 1K tokens

### Google Gemini
```bash
export GOOGLE_API_KEY="..."
```

- **What it's for**: Gemini Pro, Gemini 1.5 models
- **Used by**: All agents (when configured with `provider="google"`)
- **Get it from**: https://makersuite.google.com/app/apikey
- **Cost**: Free tier available, then pay-as-you-go

### Mistral AI
```bash
export MISTRAL_API_KEY="..."
```

- **What it's for**: Mistral Large, Mistral Medium models
- **Used by**: All agents (when configured with `provider="mistral"`)
- **Get it from**: https://console.mistral.ai/
- **Cost**: Pay-as-you-go

## 🌐 Optional Keys (Enhance Specific Agents)

### Web Search & Research

#### Exa AI (Highly Recommended)
```bash
export EXA_API_KEY="..."
```

- **What it's for**: Neural web search with semantic understanding
- **Used by**:
  - `academic_research` - Find research papers
  - `research_assistant` - Web research
  - `hallucination_detector` - Fact verification
  - `dataset_builder` - Data collection
  - `recruiting_assistant` - Candidate search
  - `sourcing_assistant` - Supplier discovery
  - `sales_intelligence` - Lead generation
  - `market_intelligence` - Market trends
  - `web_search_agent` - Advanced search
- **Get it from**: https://exa.ai (sign up for API access)
- **Cost**: Free tier available, then pay-per-search
- **Notes**: Provides much better search quality than DuckDuckGo/Qwant

#### Nimble Web API
```bash
export NIMBLE_API_KEY="..."
```

- **What it's for**: Web scraping, SERP data, maps API
- **Used by**:
  - `web_search_agent` (nimble mode)
  - `nimble_search_tool`
- **Get it from**: https://nimble.com
- **Cost**: Paid service with various plans

#### Firecrawl
```bash
export FIRECRAWL_API_KEY="..."
```

- **What it's for**: Advanced web scraping with JavaScript rendering
- **Used by**: `firecrawl_scrape_tool`
- **Get it from**: https://firecrawl.dev
- **Cost**: Free tier available, then pay-per-scrape

### Developer Tools

#### GitHub Token
```bash
export GITHUB_TOKEN="ghp_..."
```

- **What it's for**: Search code, access repositories, manage issues
- **Used by**:
  - `git_repo_search_tool` - Search GitHub repos
  - `github_issues` - Manage GitHub issues
- **Get it from**: https://github.com/settings/tokens
  - Classic token: Select scopes: `repo`, `read:org`
  - Fine-grained token: Select repositories and permissions needed
- **Cost**: Free

#### YouTube API
```bash
export YOUTUBE_API_KEY="..."
```

- **What it's for**: Search videos, extract transcripts
- **Used by**: `youtube_video_search_tool`
- **Get it from**:
  1. Go to https://console.cloud.google.com/
  2. Create a project
  3. Enable YouTube Data API v3
  4. Create credentials (API key)
- **Cost**: Free (10,000 quota units per day)

### Database & Storage

#### PostgreSQL
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

- **What it's for**: Database operations, agent state storage
- **Used by**:
  - `pg_search_tool` - PostgreSQL full-text search
  - `sqlalchemy_db` - ORM-based database operations
  - Agents with persistent state
- **Format**: `postgresql://username:password@localhost:5432/dbname`
- **Cost**: Free (self-hosted) or varies by provider

### Customer Support

#### Zendesk
```bash
export ZENDESK_API_TOKEN="..."
export ZENDESK_SUBDOMAIN="your-company"
export ZENDESK_EMAIL="admin@yourcompany.com"
```

- **What it's for**: Helpdesk ticket management
- **Used by**: `helpdesk_integration` tool, `customer_support` agent
- **Get it from**:
  1. Go to Zendesk Admin Center
  2. Apps and integrations → APIs → Zendesk API
  3. Enable token access and create a token
- **Cost**: Requires Zendesk subscription

### Observability

#### Lilypad (Recommended for Production)
```bash
export LILYPAD_API_KEY="..."
```

- **What it's for**: LLM observability, tracing, monitoring
- **Used by**: All agents (optional integration)
- **Get it from**: https://lilypad.so
- **Cost**: Free tier available
- **Benefits**: Track token usage, latency, errors across all agents

## 🚀 Quick Start Configurations

### Minimal Setup (Basic Testing)
```bash
# Just OpenAI - can test most agents
export OPENAI_API_KEY="sk-..."
```

### Recommended Setup (Most Features)
```bash
# LLM provider
export OPENAI_API_KEY="sk-..."

# Web search (highly recommended)
export EXA_API_KEY="..."

# Observability (recommended for production)
export LILYPAD_API_KEY="..."
```

### Full Setup (All Features)
```bash
# LLM providers (choose one or more)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."

# Web search & research
export EXA_API_KEY="..."
export FIRECRAWL_API_KEY="..."
export NIMBLE_API_KEY="..."

# Developer tools
export GITHUB_TOKEN="ghp_..."
export YOUTUBE_API_KEY="..."

# Database
export DATABASE_URL="postgresql://..."

# Customer support
export ZENDESK_API_TOKEN="..."
export ZENDESK_SUBDOMAIN="..."
export ZENDESK_EMAIL="..."

# Observability
export LILYPAD_API_KEY="..."
```

## 📊 What You Can Test With Each Setup

### With ONLY OPENAI_API_KEY
✅ Can test (30+ agents):
- Text Summarization
- Sentiment Analysis
- Code Review
- Bug Triage
- Contract Analysis
- Financial Analysis
- Task Prioritization
- Content Moderation
- Customer Support
- PII Scrubbing
- Document Segmentation
- Knowledge Graph
- Prompt Engineering
- Code Generation
- D&D Game Master
- Game Playing (Catan, Diplomacy)
- Decision Quality Assessment
- Dynamic Learning Path
- Social Media Manager
- And 10+ more...

❌ Cannot test (agents requiring additional keys):
- Academic Research (needs EXA_API_KEY)
- Hallucination Detector (needs EXA_API_KEY)
- Dataset Builder (needs EXA_API_KEY)
- Recruiting Assistant (needs EXA_API_KEY)
- Sales Intelligence (needs EXA_API_KEY)
- Market Intelligence (needs EXA_API_KEY)
- Multi-Source News Verification (works better with EXA_API_KEY)

### With OPENAI_API_KEY + EXA_API_KEY
✅ Can test: **ALL 33+ agents** with full functionality

### With OPENAI_API_KEY + All Optional Keys
✅ Can test: **ALL agents + ALL tools** with complete feature sets

## 🔧 Setup Methods

### Method 1: Environment Variables (Recommended)
```bash
# Add to your ~/.bashrc, ~/.zshrc, or ~/.bash_profile
export OPENAI_API_KEY="sk-..."
export EXA_API_KEY="..."

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

### Method 2: .env File (For Projects)
```bash
# Create .env file
cp examples/.env.example .env

# Edit .env with your keys
nano .env

# Load with python-dotenv (automatic in most scripts)
```

### Method 3: Inline (For Testing)
```bash
# Set for current session only
export OPENAI_API_KEY="sk-..."

# Or run with env vars inline
OPENAI_API_KEY="sk-..." python3 examples/simple_agent_demo.py
```

## ✅ Verify Setup

Run this to check which keys are configured:

```bash
python3 -c "
import os
keys = {
    'OpenAI': 'OPENAI_API_KEY',
    'Anthropic': 'ANTHROPIC_API_KEY',
    'Google': 'GOOGLE_API_KEY',
    'Exa': 'EXA_API_KEY',
    'Firecrawl': 'FIRECRAWL_API_KEY',
    'GitHub': 'GITHUB_TOKEN',
    'YouTube': 'YOUTUBE_API_KEY',
    'Nimble': 'NIMBLE_API_KEY',
    'Database': 'DATABASE_URL',
    'Lilypad': 'LILYPAD_API_KEY',
}

print('Environment Variable Status:')
print('=' * 40)
for name, var in keys.items():
    status = '✅' if os.getenv(var) else '❌'
    print(f'{status} {name:15} ({var})')
"
```

## 🛡️ Security Best Practices

1. **Never commit API keys** - Add `.env` to `.gitignore`
2. **Use environment variables** - Don't hardcode keys in scripts
3. **Rotate keys regularly** - Especially if they might be compromised
4. **Use minimal permissions** - Grant only necessary scopes
5. **Monitor usage** - Track API costs and set up billing alerts
6. **Use separate keys** - Different keys for dev/staging/production

## 💰 Cost Optimization

### Free Tier Options
- **Google Gemini**: Generous free tier
- **YouTube API**: 10,000 quota units/day free
- **GitHub**: Unlimited for public repos
- **DuckDuckGo/Qwant**: Free web search (no API key needed)
- **Lilypad**: Free tier available

### Paid But Worth It
- **OpenAI**: Industry standard, reliable, good pricing
- **Exa**: Best semantic search quality, reasonable pricing
- **Anthropic**: Excellent for long context, competitive pricing

### Cost Management Tips
1. Start with **OpenAI + Exa** only
2. Use cheaper models for testing (e.g., `gpt-3.5-turbo` instead of `gpt-4`)
3. Set usage limits in provider dashboards
4. Monitor costs with observability tools (Lilypad)
5. Cache results when possible

## 🆘 Troubleshooting

### "No API keys found" Error
```bash
# Check if keys are set
echo $OPENAI_API_KEY
# If empty, set it:
export OPENAI_API_KEY="sk-..."
```

### "Invalid API key" Error
- Verify the key is correct (no extra spaces)
- Check if key is active in provider dashboard
- Ensure billing is set up
- Try generating a new key

### "Rate limit exceeded" Error
- You've hit the provider's rate limit
- Wait a few minutes and try again
- Upgrade to higher tier if needed
- Use a different model/provider

### Agent Not Working
1. Check if agent requires specific API keys (see agent README)
2. Verify keys are set: `env | grep API_KEY`
3. Check agent logs for specific errors
4. Try with a simpler test case first

## 📚 Next Steps

1. **Set up minimal keys**: Just `OPENAI_API_KEY` to start
2. **Run test**: `./test_agents.sh`
3. **Add more keys**: As you need specific features
4. **Monitor usage**: Set up billing alerts
5. **Go to production**: Add observability (Lilypad)

---

**Need specific agents?** Check individual agent READMEs in `packages/sygaldry_registry/components/agents/*/README.md` for exact requirements.

**Ready to test?** Run `./test_agents.sh` and follow the prompts!

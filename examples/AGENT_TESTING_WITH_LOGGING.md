# Agent Testing with Comprehensive Logging & Auditing

This guide explains how to test Sygaldry agents in realistic scenarios with full audit trails for compliance and debugging.

## Overview

The logging and audit system provides:

- **📝 Comprehensive Audit Trails** - Every agent interaction is logged with timestamps
- **📊 Structured Logs** - JSON Lines format for easy parsing and analysis
- **👁️ Human-Readable Logs** - Text logs for quick review
- **🔍 Session Tracking** - Each test session gets a unique ID
- **📈 Performance Metrics** - Duration, success rates, and custom metrics
- **🗂️ Organized Storage** - All logs saved to `logs/audit/` directory
- **🔒 Compliance Ready** - Full audit trails for regulatory requirements

## Quick Start

### 1. Run Predefined Scenarios

The fastest way to test agents with logging:

```bash
# Run all predefined scenarios
python3 examples/run_scenarios.py
```

This will:
- Load scenarios from `test_scenarios.json`
- Run each scenario with full logging
- Generate audit trails for every interaction
- Show summary of results

### 2. Run Custom Tests

For more control, use the interactive runner:

```bash
# Interactive agent testing with logging
python3 examples/agent_runner_with_logging.py
```

Features:
- Choose which agent to test
- Provide custom inputs
- Run conversational (multi-turn) tests
- View test history
- All interactions logged automatically

### 3. View Logs

Analyze your audit logs:

```bash
# View and analyze logs
python3 examples/view_logs.py
```

This lets you:
- Browse all log files
- View session statistics
- Filter by event type
- Analyze errors
- Track performance metrics

## Log Structure

### Directory Layout

```
logs/
└── audit/
    ├── text_summarization_single_20241114_153045.jsonl
    ├── text_summarization_single_20241114_153045.txt
    ├── sentiment_analysis_single_20241114_153128.jsonl
    └── sentiment_analysis_single_20241114_153128.txt
```

### JSONL Format (Structured Logs)

Each line is a JSON object representing an event:

```json
{"event": "session_start", "timestamp": "2024-11-14T15:30:45.123456", "agent_name": "text_summarization", "session_id": "single_20241114153045"}
{"event": "agent_input", "timestamp": "2024-11-14T15:30:45.234567", "function": "summarize_text", "parameters": {"text": "...", "style": "technical"}}
{"event": "agent_output", "timestamp": "2024-11-14T15:30:47.345678", "duration_seconds": 2.11, "result": {"summary": "...", "confidence_score": 0.95}}
{"event": "session_end", "timestamp": "2024-11-14T15:30:47.456789", "duration_seconds": 2.33, "total_entries": 4}
```

### Text Format (Human-Readable)

```
=== SESSION START: text_summarization ===
Session ID: single_20241114153045
Start Time: 2024-11-14 15:30:45.123456
============================================================

[15:30:45] AGENT INPUT
Function: summarize_text
Parameters: {
  "text": "...",
  "style": "technical",
  "max_length": 100
}

[15:30:47] AGENT OUTPUT
Duration: 2.11s
Result: {
  "summary": "...",
  "confidence_score": 0.95,
  "word_count": 87
}

============================================================
=== SESSION END ===
End Time: 2024-11-14 15:30:47.456789
Total Duration: 2.33s
Total Log Entries: 4
============================================================
```

## Event Types

### session_start
Marks the beginning of a test session.

**Fields:**
- `timestamp` - ISO 8601 timestamp
- `agent_name` - Name of the agent being tested
- `session_id` - Unique session identifier
- `environment` - API keys status, Python version

### agent_input
Logs the input parameters to an agent function.

**Fields:**
- `timestamp` - When the agent was called
- `function` - Function name being executed
- `parameters` - Dict of all input parameters

### agent_output
Logs the result from an agent function.

**Fields:**
- `timestamp` - When the agent returned
- `duration_seconds` - How long the agent took
- `result` - The output from the agent (dict or model dump)

### error
Logs any errors that occurred.

**Fields:**
- `timestamp` - When the error occurred
- `error_type` - Exception class name
- `error_message` - Error message
- `traceback` - Full stack trace

### conversation_turn
Logs a single turn in a multi-turn conversation.

**Fields:**
- `timestamp` - When the turn occurred
- `turn_number` - Turn sequence number
- `user_input` - What the user said
- `agent_response` - How the agent responded

### metric
Logs custom metrics.

**Fields:**
- `timestamp` - When the metric was logged
- `metric_name` - Name of the metric
- `value` - Metric value (any type)

### session_end
Marks the end of a test session with summary statistics.

**Fields:**
- `timestamp` - Session end time
- `duration_seconds` - Total session duration
- `total_entries` - Number of log entries
- `summary` - Statistics dict with event counts, durations, errors

## Test Scenarios

### Predefined Scenarios

The `test_scenarios.json` file contains realistic test cases:

**Categories:**
- `text_processing_scenarios` - Summarization, sentiment analysis
- `security_scenarios` - PII scrubbing, code review for vulnerabilities
- `business_scenarios` - Contract analysis, bug triage, task prioritization
- `conversational_scenarios` - Multi-turn customer support interactions
- `research_scenarios` - Hallucination detection, fact-checking

### Adding Custom Scenarios

Edit `test_scenarios.json`:

```json
{
  "your_category_scenarios": [
    {
      "name": "Your Test Name",
      "agent": "agent_name",
      "function": "function_name",
      "params": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
```

For conversational scenarios:

```json
{
  "conversational_scenarios": [
    {
      "name": "Your Conversation Test",
      "agent": "your_agent",
      "function": "your_function",
      "turns": [
        {
          "user": "First message",
          "params": {"message": "First message", "context": {}}
        },
        {
          "user": "Follow-up message",
          "params": {"message": "Follow-up", "context": {"previous": "data"}}
        }
      ]
    }
  ]
}
```

## Programmatic Usage

### Basic Logging

```python
from agent_runner_with_logging import AgentAuditLogger

# Create logger
logger = AgentAuditLogger("my_agent", "my_session")

# Log events
logger.log_input("my_function", {"param": "value"})
logger.log_output(result, duration_seconds=1.5)
logger.log_error(exception)

# Finalize
logger.finalize()

# Get log file paths
files = logger.get_log_files()
print(f"JSONL: {files['jsonl']}")
print(f"Text: {files['text']}")
```

### Custom Metrics

```python
logger.log_metric("tokens_used", 1234)
logger.log_metric("cache_hit_rate", 0.85)
logger.log_metric("custom_score", {"precision": 0.92, "recall": 0.88})
```

### Conversational Logging

```python
logger.log_conversation_turn(
    turn_number=1,
    user_input="What's the weather?",
    agent_response="The weather is sunny, 72°F"
)
```

## Log Analysis

### Using the Log Viewer

```bash
python3 examples/view_logs.py
```

Features:
- **Session Summary** - Duration, call count, success rate
- **Event Breakdown** - Count of each event type
- **Error Details** - All errors with stack traces
- **Performance Metrics** - Average call duration, total time
- **Event Filtering** - View only inputs, outputs, errors, etc.

### Programmatic Analysis

```python
import json
from pathlib import Path

# Load log file
log_file = Path("logs/audit/agent_session_timestamp.jsonl")
entries = []

with open(log_file, "r") as f:
    for line in f:
        entries.append(json.loads(line))

# Analyze
errors = [e for e in entries if e["event"] == "error"]
outputs = [e for e in entries if e["event"] == "agent_output"]

avg_duration = sum(e["duration_seconds"] for e in outputs) / len(outputs)
print(f"Average duration: {avg_duration:.2f}s")
print(f"Total errors: {len(errors)}")
```

### Exporting for Analysis

JSONL format is perfect for:

- **jq** - Command-line JSON processor
- **pandas** - Python data analysis
- **Elasticsearch** - Log aggregation
- **Splunk** - Enterprise log management

Example with jq:

```bash
# Get all errors
cat logs/audit/*.jsonl | jq 'select(.event == "error")'

# Average duration
cat logs/audit/*.jsonl | jq 'select(.event == "agent_output") | .duration_seconds' | jq -s 'add/length'

# Success rate
cat logs/audit/*.jsonl | jq -s 'map(select(.event == "agent_output")) | length'
```

## Compliance & Auditing

### What Gets Logged

✅ **Logged:**
- All agent inputs and outputs
- Timestamps for every event
- Durations and performance metrics
- Errors with full stack traces
- Session metadata
- Environment information

❌ **NOT Logged by Default:**
- Raw LLM API responses (can be added via custom metrics)
- API keys or secrets
- User authentication tokens

### Log Retention

Logs are stored in `logs/audit/` and are never automatically deleted.

Recommended retention policies:
- **Development**: 7-30 days
- **Production**: 90 days to 7 years (depending on compliance requirements)
- **High-compliance**: Indefinite with archival

### GDPR Compliance

If processing personal data:
1. Ensure PII is scrubbed before logging (use `pii_scrubbing` agent)
2. Implement log retention policies
3. Provide log deletion mechanisms
4. Document data processing purposes

### SOC 2 / Audit Requirements

The logging system provides:
- **Immutable audit trail** - Append-only JSONL files
- **Unique session IDs** - Track all related events
- **Timestamps** - Precise event ordering
- **Error tracking** - All failures logged
- **Performance metrics** - SLA compliance tracking

## Best Practices

### 1. Always Use Unique Session IDs

```python
import uuid

session_id = str(uuid.uuid4())
logger = AgentAuditLogger(agent_name, session_id)
```

### 2. Log Context Information

```python
logger.log_metric("user_id", "USER-12345")
logger.log_metric("request_id", "REQ-67890")
logger.log_metric("environment", "production")
```

### 3. Handle Sensitive Data

```python
# Don't log sensitive data directly
from pii_scrubbing import scrub_pii

cleaned_params = {
    "text": scrub_pii(params["text"]),
    "user_email": "[REDACTED]"
}
logger.log_input("function", cleaned_params)
```

### 4. Monitor Log File Sizes

```bash
# Check log directory size
du -sh logs/audit/

# Find large log files
find logs/audit/ -size +10M
```

### 5. Regular Log Review

Set up cron jobs or scheduled tasks to:
- Archive old logs
- Generate weekly summaries
- Alert on error spikes
- Monitor performance degradation

## Troubleshooting

### Logs Not Being Created

Check:
1. Logs directory exists: `mkdir -p logs/audit`
2. Write permissions: `ls -la logs/`
3. Disk space: `df -h`

### Parsing Errors in JSONL

```python
# Validate JSONL file
with open("logfile.jsonl", "r") as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Line {i}: {e}")
```

### Performance Impact

Logging overhead is minimal:
- **Disk I/O**: ~1-5ms per event
- **JSON serialization**: <1ms for typical payloads
- **Total overhead**: <1% of agent execution time

For high-throughput scenarios:
- Use async logging
- Batch write operations
- Compress old logs

## Advanced Features

### Custom Event Types

```python
logger._write_jsonl({
    "event": "custom_event",
    "timestamp": datetime.now().isoformat(),
    "your_field": "your_value"
})
```

### Real-time Log Streaming

```bash
# Tail logs in real-time
tail -f logs/audit/*.jsonl | jq '.'
```

### Integration with Observability Tools

```python
# Send to external logging service
import requests

def send_to_external_logger(entry):
    requests.post("https://your-log-service.com/ingest", json=entry)

# After each log entry
logger._write_jsonl(entry)
send_to_external_logger(entry)
```

## Next Steps

1. **Run your first test**: `python3 examples/run_scenarios.py`
2. **View the logs**: `python3 examples/view_logs.py`
3. **Create custom scenarios**: Edit `test_scenarios.json`
4. **Integrate with CI/CD**: Run scenarios in your pipeline
5. **Set up monitoring**: Track errors and performance over time

---

**Need Help?**
- Check the [examples README](README.md) for more information
- Review the source code in `agent_runner_with_logging.py`
- See main project [README](../README.md)
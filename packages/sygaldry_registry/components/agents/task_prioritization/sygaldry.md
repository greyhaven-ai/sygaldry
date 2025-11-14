# task_prioritization_agent
> Task prioritization agent using Eisenhower matrix to assess urgency, importance, effort, and impact. Provides optimal task ordering, time allocation, and strategic recommendations for maximum productivity.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

The Task Prioritization Agent helps you organize your workload using the proven Eisenhower Matrix framework. It analyzes each task across multiple dimensions including urgency, importance, effort level, and expected impact, then provides comprehensive recommendations for optimal task ordering and time allocation.

This agent integrates seamlessly with the Mirascope v2 framework and follows AI agent best practices for production deployment.

## Features

- **Eisenhower Matrix Analysis**: Automatically categorizes tasks into four quadrants (Urgent-Important, Not Urgent-Important, Urgent-Not Important, Not Urgent-Not Important)
- **Multi-Dimensional Assessment**: Evaluates tasks on urgency, importance, effort, and impact
- **Smart Time Allocation**: Creates optimal time blocks considering energy levels and focus requirements
- **Strategy Recommendations**: Suggests best prioritization strategies (Eat the Frog, Quick Wins, Time Blocking, etc.)
- **Quick Wins Identification**: Highlights high-impact, low-effort tasks for momentum building
- **Delegation Analysis**: Identifies tasks suitable for delegation
- **Capacity Assessment**: Evaluates workload against available time
- **Streaming Support**: Real-time progress updates during analysis

## Quick Start

### Installation

```bash
sygaldry add task_prioritization_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- None

**Python Dependencies:**

- `mirascope>=2.0.0-alpha.1`
- `pydantic>=2.0.0`
- `asyncio`

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for LLM calls (**Required**)

### Basic Usage

```python
from task_prioritization import task_prioritization_agent, task_prioritization_agent_stream

# Example 1: Prioritize daily tasks
result = await task_prioritization_agent(
    tasks=[
        "Fix critical production bug affecting 20% of users",
        "Write Q4 strategy document for leadership review",
        "Review 5 pull requests from team members",
        "Attend daily standup meeting (15 min)",
        "Update API documentation",
        "Research new database optimization techniques",
        "Respond to Slack messages",
        "Plan team offsite event"
    ],
    context="Software engineering team lead, product launch scheduled for next week",
    goals="Ensure stable product launch, maintain team velocity, strategic planning for Q4",
    available_hours=8.0
)

print(f"Recommended Strategy: {result.strategy.strategy_name}")
print(f"Quick Wins: {len(result.quick_wins)} tasks")
print(f"\nPriority Order:")
for i, task_id in enumerate(result.prioritized_order[:5], 1):
    task = next(ta for ta in result.task_analyses if ta.task_id == task_id)
    print(f"{i}. {task.task_description} ({task.priority.value})")

# Example 2: Stream prioritization for project tasks
async for update in task_prioritization_agent_stream(
    tasks=[
        "Complete client proposal",
        "Update project timeline",
        "Review budget allocation",
        "Schedule team meetings",
        "Respond to client emails"
    ],
    context="Project manager with tight deadline",
    goals="Deliver proposal by Friday, maintain client relationship",
    available_hours=6.0,
    constraints="Must attend mandatory all-hands meeting 2-3pm"
):
    print(update, end='')

# Example 3: Prioritize with specific constraints
result = await task_prioritization_agent(
    tasks=[
        "Prepare presentation for board meeting",
        "Interview 3 candidates for senior role",
        "Approve department budgets",
        "One-on-one meetings with direct reports",
        "Strategic planning session prep",
        "Review quarterly OKRs"
    ],
    context="Executive leader, board meeting in 2 days",
    goals="Successful board meeting, hire top talent, maintain team morale",
    available_hours=10.0,
    constraints="Board meeting Wednesday 9am, cannot reschedule interviews"
)
```

## Understanding the Eisenhower Matrix

The agent categorizes tasks into four quadrants:

### Quadrant 1: Urgent & Important (Do First)
- Critical deadlines
- Crisis situations
- Pressing problems
- **Action**: Do these tasks immediately

### Quadrant 2: Not Urgent & Important (Schedule)
- Long-term strategy
- Relationship building
- Professional development
- **Action**: Schedule dedicated time for these tasks

### Quadrant 3: Urgent & Not Important (Delegate)
- Interruptions
- Some meetings
- Some emails
- **Action**: Delegate if possible or batch process

### Quadrant 4: Not Urgent & Not Important (Eliminate)
- Time wasters
- Busy work
- Trivial activities
- **Action**: Eliminate or minimize these tasks

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Multi-Stage Analysis**: Breaks down prioritization into task analysis, strategy recommendation, time allocation, and synthesis
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- **Optional Lilypad Integration**: Instrumented with Lilypad for observability and tracing when available
- **Mirascope v2**: Uses latest Mirascope v2 API with `format=` parameter for structured outputs

## API Reference

### Main Functions

#### `task_prioritization_agent(tasks, context="", goals="", available_hours=8.0, constraints="", llm_provider="openai", model="gpt-4o")`

Main agent function for task prioritization.

**Parameters:**
- `tasks` (list[str]): List of task descriptions to prioritize
- `context` (str): Context about the tasks and current situation
- `goals` (str): Your goals and objectives
- `available_hours` (float): Available hours for work (default: 8.0)
- `constraints` (str): Any constraints on task execution
- `llm_provider` (str): LLM provider to use (default: "openai")
- `model` (str): Model to use for analysis (default: "gpt-4o")

**Returns:**
- `TaskPrioritization`: Complete prioritization analysis with recommendations

#### `task_prioritization_agent_stream(tasks, context="", goals="", **kwargs)`

Streaming version that yields progress updates.

**Parameters:**
- Same as `task_prioritization_agent`

**Yields:**
- str: Formatted progress updates and results

### Data Models

#### `TaskAnalysis`
Analysis of individual tasks with urgency, importance, effort, impact scores.

#### `TimeBlock`
Recommended time allocation blocks with task assignments.

#### `PrioritizationStrategy`
Recommended strategy with principles and success metrics.

#### `TaskPrioritization`
Complete prioritization result with all analyses and recommendations.

## Advanced Examples

### Example 1: Software Development Team

```python
result = await task_prioritization_agent(
    tasks=[
        "Fix login bug reported by 10 customers",
        "Code review for junior developer",
        "Update technical documentation",
        "Attend sprint planning meeting",
        "Research new testing framework",
        "Refactor legacy authentication module",
        "Respond to customer support tickets",
        "Write unit tests for new feature"
    ],
    context="Senior software engineer, sprint ends Friday",
    goals="Ship stable release, mentor team, reduce technical debt",
    available_hours=8.0,
    constraints="Sprint planning meeting 10-11am, code freeze Thursday 5pm"
)

# View quick wins
print("\nQuick Wins to Start:")
for task_id in result.quick_wins[:3]:
    task = next(ta for ta in result.task_analyses if ta.task_id == task_id)
    print(f"- {task.task_description} ({task.estimated_duration})")

# View time blocks
print("\nRecommended Schedule:")
for block in result.time_allocation:
    print(f"\n{block.time_slot} - {block.duration}")
    print(f"Energy: {block.energy_level_required} | Focus: {block.focus_type}")
    for task_id in block.task_ids:
        task = next(ta for ta in result.task_analyses if ta.task_id == task_id)
        print(f"  - {task.task_description}")
```

### Example 2: Executive Leadership

```python
result = await task_prioritization_agent(
    tasks=[
        "Finalize merger acquisition paperwork",
        "Quarterly board presentation",
        "Interview C-suite candidates",
        "Review department OKRs",
        "Employee town hall preparation",
        "Budget approval for 3 departments",
        "One-on-ones with direct reports",
        "Industry conference keynote prep"
    ],
    context="CEO of mid-size tech company, board meeting next week",
    goals="Complete acquisition, hire strong leadership, maintain company culture",
    available_hours=12.0,
    constraints="Board meeting Monday 9am, town hall Thursday 3pm"
)

print(f"\nCapacity Assessment: {result.capacity_assessment}")
print(f"Strategy: {result.strategy.strategy_name}")
print(f"Rationale: {result.strategy.rationale}")
```

### Example 3: Personal Productivity

```python
result = await task_prioritization_agent(
    tasks=[
        "Finish project proposal for client",
        "Gym workout",
        "Grocery shopping",
        "Call mom for birthday",
        "Read industry newsletter",
        "Update resume and LinkedIn",
        "File taxes",
        "Plan weekend trip"
    ],
    context="Freelance consultant, working from home",
    goals="Grow business, maintain health, stay connected with family",
    available_hours=6.0,
    constraints="Client call at 2pm, gym closes at 8pm"
)

# Check for tasks to eliminate
if result.elimination_candidates:
    print("\nConsider Eliminating:")
    for task_id in result.elimination_candidates:
        task = next(ta for ta in result.task_analyses if ta.task_id == task_id)
        print(f"- {task.task_description}")
```

## Prioritization Strategies

The agent can recommend different strategies based on your task portfolio:

### Eat the Frog
Tackle the hardest, most important task first thing in the morning.
- **Best for**: High-urgency situations, avoiding procrastination
- **When to use**: Many urgent tasks, need to build momentum

### Quick Wins First
Build momentum with easy high-impact tasks before tackling bigger challenges.
- **Best for**: Low motivation, need for visible progress
- **When to use**: Feeling overwhelmed, need confidence boost

### Time Blocking
Allocate specific time slots for different types of tasks.
- **Best for**: Many different task types, preventing context switching
- **When to use**: Varied workload, need for structure

### Energy Management
Match task difficulty to energy levels throughout the day.
- **Best for**: Maximizing cognitive performance
- **When to use**: High-value strategic work, complex problems

### Batch Processing
Group similar tasks to minimize context switching.
- **Best for**: Many similar tasks (emails, calls, reviews)
- **When to use**: Efficiency is priority, routine tasks dominate

### MIT (Most Important Tasks)
Identify and complete 1-3 most important tasks per day.
- **Best for**: Focus on high-impact work
- **When to use**: Clear priorities, strategic work matters most

## Best Practices

### 1. Provide Clear Context
Include information about deadlines, stakeholders, and dependencies:
```python
context = "Software team lead, product launch Friday, 2 engineers out sick, CEO monitoring progress"
```

### 2. Define Specific Goals
Be explicit about what success looks like:
```python
goals = "Ship stable release on time, maintain team morale, no critical bugs in production"
```

### 3. Include Constraints
Specify any limitations or fixed commitments:
```python
constraints = "All-hands meeting 2-3pm, code freeze Thursday 5pm, can't work weekends"
```

### 4. Be Realistic with Available Hours
Account for meetings, breaks, and context switching:
```python
available_hours = 6.0  # 8 hours minus meetings and breaks
```

### 5. Describe Tasks Clearly
Include enough detail for accurate assessment:
```python
tasks = [
    "Fix critical authentication bug affecting 500 users (reported 2 hours ago)",
    "Write Q4 strategy document for board review (due next Monday)",
    # Not just: "Fix bug", "Write document"
]
```

## Integration with Mirascope v2

This agent follows Mirascope v2 best practices:

- Uses `from mirascope import llm` for decorators
- Implements `format=` parameter for structured outputs (replaces `response_model=`)
- Uses `provider="openai:completions"` syntax
- Uses `model_id=` parameter (replaces `model=`)
- Implements Pydantic models for all responses
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling

## LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope v2:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models (default)
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models

Configure the provider and model using function parameters:

```python
# Using OpenAI (default)
result = await task_prioritization_agent(
    tasks=my_tasks,
    llm_provider="openai",
    model="gpt-4o"
)

# Using Anthropic
result = await task_prioritization_agent(
    tasks=my_tasks,
    llm_provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

## Troubleshooting

### Common Issues

**Issue**: Tasks receive similar priority scores
- **Solution**: Provide more context about deadlines, impact, and stakeholders

**Issue**: Time allocation doesn't match my schedule
- **Solution**: Use the `constraints` parameter to specify fixed commitments

**Issue**: Quick wins not identified
- **Solution**: Include task details about effort and expected outcomes

**Issue**: Strategy recommendation doesn't fit my work style
- **Solution**: Provide clearer goals and context about your preferences

**Issue**: Capacity assessment shows overcommitment
- **Solution**: Be realistic with `available_hours` and consider delegation

### API Key Issues
Ensure your OpenAI API key is set correctly:
```bash
export OPENAI_API_KEY=your-key-here
```

### Dependency Conflicts
Run `sygaldry add task_prioritization_agent` to reinstall dependencies.

## Performance Tips

1. **Batch Similar Tasks**: Group similar tasks for more accurate effort estimation
2. **Include Deadlines**: Explicit deadlines improve urgency assessment
3. **Specify Dependencies**: Mention task dependencies for better ordering
4. **Update Context**: Re-run prioritization as situations change
5. **Use Streaming**: Use `task_prioritization_agent_stream` for long task lists

## Related Components

- **decision_quality_assessor**: For analyzing decision quality and biases
- **multi_agent_coordinator**: For complex multi-agent task orchestration
- **prompt_engineering_optimizer**: For optimizing agent prompts

## References

- [Eisenhower Matrix](https://en.wikipedia.org/wiki/Time_management#The_Eisenhower_Method)
- [Mirascope v2 Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

---

**Key Benefits:**

- Task prioritization using proven Eisenhower Matrix framework
- Multi-dimensional assessment (urgency, importance, effort, impact)
- Smart time allocation with energy management
- Quick wins identification for momentum
- Delegation and elimination recommendations
- Multiple prioritization strategy options
- Real-time streaming support

**Tags:** task-management, prioritization, productivity, eisenhower-matrix, time-management, planning

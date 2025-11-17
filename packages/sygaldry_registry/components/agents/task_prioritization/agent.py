from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import llm
from pydantic import BaseModel, Field
from typing import Optional

try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    LILYPAD_AVAILABLE = False
    def trace():
        """Decorator fallback when lilypad is not available."""
        def decorator(func):
            return func
        return decorator


class EisenhowerQuadrant(str, Enum):
    """Eisenhower Matrix quadrants for task prioritization."""

    URGENT_IMPORTANT = "urgent_important"  # Do First
    NOT_URGENT_IMPORTANT = "not_urgent_important"  # Schedule
    URGENT_NOT_IMPORTANT = "urgent_not_important"  # Delegate
    NOT_URGENT_NOT_IMPORTANT = "not_urgent_not_important"  # Eliminate


class TaskPriority(str, Enum):
    """Task priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class EffortLevel(str, Enum):
    """Task effort estimation levels."""

    MINIMAL = "minimal"  # < 1 hour
    LOW = "low"  # 1-4 hours
    MEDIUM = "medium"  # 4-8 hours / 1 day
    HIGH = "high"  # 1-3 days
    VERY_HIGH = "very_high"  # 3+ days


class ImpactLevel(str, Enum):
    """Task impact assessment levels."""

    TRANSFORMATIONAL = "transformational"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


class TaskAnalysis(BaseModel):
    """Analysis of a single task for prioritization."""

    task_id: str = Field(..., description="Unique identifier for the task")
    task_description: str = Field(..., description="Description of the task")
    urgency_score: float = Field(..., description="Urgency score (0-1)")
    importance_score: float = Field(..., description="Importance score (0-1)")
    effort_level: EffortLevel = Field(..., description="Estimated effort level")
    impact_level: ImpactLevel = Field(..., description="Expected impact level")
    eisenhower_quadrant: EisenhowerQuadrant = Field(..., description="Eisenhower matrix quadrant")
    priority: TaskPriority = Field(..., description="Overall priority level")
    urgency_factors: list[str] = Field(..., description="Factors contributing to urgency")
    importance_factors: list[str] = Field(..., description="Factors contributing to importance")
    effort_breakdown: list[str] = Field(..., description="Breakdown of effort requirements")
    expected_impact: list[str] = Field(..., description="Expected outcomes and impact")
    dependencies: list[str] = Field(..., description="Task dependencies")
    blockers: list[str] = Field(..., description="Potential blockers or obstacles")
    quick_wins_potential: bool = Field(..., description="Whether this is a quick win")
    delegation_potential: bool = Field(..., description="Whether this can be delegated")
    # Note: All fields must be required for OpenAI schema validation
    deadline: str | None = Field(..., description="Deadline if applicable (null if no deadline)")
    estimated_duration: str = Field(..., description="Estimated time to complete")


class TimeBlock(BaseModel):
    """Recommended time block for tasks."""

    time_slot: str = Field(..., description="Recommended time slot")
    duration: str = Field(..., description="Recommended duration")
    task_ids: list[str] = Field(..., description="Task IDs to work on")
    rationale: str = Field(..., description="Rationale for this time allocation")
    energy_level_required: str = Field(..., description="Energy level required (high/medium/low)")
    focus_type: str = Field(..., description="Type of focus required (deep/shallow/collaborative)")


class PrioritizationStrategy(BaseModel):
    """Overall prioritization strategy recommendations."""

    strategy_name: str = Field(..., description="Name of the prioritization strategy")
    rationale: str = Field(..., description="Why this strategy is recommended")
    key_principles: list[str] = Field(..., description="Key principles to follow")
    success_metrics: list[str] = Field(..., description="How to measure success")
    potential_challenges: list[str] = Field(..., description="Potential challenges to watch for")
    mitigation_strategies: list[str] = Field(..., description="How to overcome challenges")


class TaskPrioritization(BaseModel):
    """Complete task prioritization analysis."""

    analysis_timestamp: str = Field(..., description="When this analysis was performed")
    total_tasks: int = Field(..., description="Total number of tasks analyzed")
    # Note: Field(...) without description for nested models to avoid OpenAI schema error
    # OpenAI rejects $ref with additional keywords like 'description'
    task_analyses: list[TaskAnalysis] = Field(...)
    prioritized_order: list[str] = Field(..., description="Recommended task order by ID")
    time_allocation: list[TimeBlock] = Field(...)
    strategy: PrioritizationStrategy = Field(...)
    urgent_important_count: int = Field(..., description="Count of urgent & important tasks")
    quick_wins: list[str] = Field(..., description="Task IDs identified as quick wins")
    delegation_candidates: list[str] = Field(..., description="Task IDs that can be delegated")
    elimination_candidates: list[str] = Field(..., description="Task IDs to consider eliminating")
    total_estimated_hours: str = Field(..., description="Total estimated time for all tasks")
    capacity_assessment: str = Field(..., description="Assessment of capacity vs. workload")
    recommendations: list[str] = Field(..., description="Key recommendations")
    confidence_score: float = Field(..., description="Confidence in prioritization (0-1)")


# Rebuild models to resolve forward references
TaskAnalysis.model_rebuild()
TimeBlock.model_rebuild()
PrioritizationStrategy.model_rebuild()
TaskPrioritization.model_rebuild()


def _get_analyze_tasks_prompt(tasks: list[str], context: str = "") -> str:
    """Get the prompt for analyzing individual tasks."""
    return f"""
    SYSTEM:
    You are an expert in productivity, task management, and time optimization.
    Your role is to analyze tasks using the Eisenhower Matrix framework and provide
    comprehensive prioritization analysis.

    Eisenhower Matrix Framework:
    1. URGENT & IMPORTANT (Do First): Critical tasks with deadlines, crises, pressing problems
    2. NOT URGENT & IMPORTANT (Schedule): Long-term development, strategic planning, relationship building
    3. URGENT & NOT IMPORTANT (Delegate): Interruptions, some meetings, some emails
    4. NOT URGENT & NOT IMPORTANT (Eliminate): Time wasters, busy work, trivial activities

    Assessment Criteria:

    URGENCY (0-1):
    - 0.9-1.0: Immediate crisis, missed deadline consequences
    - 0.7-0.9: Due within 24-48 hours, blocking others
    - 0.5-0.7: Due this week, time-sensitive
    - 0.3-0.5: Due within 2 weeks
    - 0.0-0.3: Flexible timing, no immediate pressure

    IMPORTANCE (0-1):
    - 0.9-1.0: Critical to core goals, high strategic value
    - 0.7-0.9: Significant impact on key objectives
    - 0.5-0.7: Moderate impact, supports goals
    - 0.3-0.5: Minor impact, nice to have
    - 0.0-0.3: Low value, questionable benefit

    EFFORT LEVELS:
    - MINIMAL: < 1 hour
    - LOW: 1-4 hours
    - MEDIUM: 4-8 hours / 1 day
    - HIGH: 1-3 days
    - VERY_HIGH: 3+ days

    IMPACT LEVELS:
    - TRANSFORMATIONAL: Game-changing results
    - HIGH: Significant measurable improvement
    - MODERATE: Noticeable positive effect
    - LOW: Minor improvement
    - MINIMAL: Negligible effect

    Consider:
    - Dependencies between tasks
    - Potential blockers
    - Quick win opportunities (high impact, low effort)
    - Delegation potential
    - Deadlines and time constraints
    - Long-term vs. short-term value
    - Energy and focus requirements

    USER:
    Analyze these tasks for prioritization:

    Context: {context}

    Tasks:
    {chr(10).join(f"{i+1}. {task}" for i, task in enumerate(tasks))}

    Provide comprehensive analysis for each task including urgency, importance, effort, impact,
    Eisenhower quadrant placement, and prioritization recommendations.
    """


# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o",
    format=list[TaskAnalysis],
)
async def _analyze_tasks_call(tasks: list[str], context: str = "") -> str:
    """Internal LLM call for task analysis."""
    return _get_analyze_tasks_prompt(tasks, context)


# Public wrapper - returns parsed list[TaskAnalysis]
async def analyze_tasks(tasks: list[str], context: str = "") -> list[TaskAnalysis]:
    """Analyze individual tasks for prioritization."""
    response = await _analyze_tasks_call(tasks=tasks, context=context)
    return response.parse()


def _get_create_time_allocation_prompt(
    task_analyses: list[TaskAnalysis], available_hours: float = 8.0, constraints: str = ""
) -> str:
    """Get the prompt for creating time allocation."""
    return f"""
    SYSTEM:
    You are an expert in time management and productivity optimization.
    Your role is to create an optimal time allocation schedule based on task
    priorities, energy levels, and cognitive performance patterns.

    Time Management Principles:
    1. Deep work for high-priority tasks during peak energy hours
    2. Batch similar tasks to minimize context switching
    3. Include buffer time for unexpected issues (15-20%)
    4. Schedule quick wins early for momentum
    5. Protect time for important but not urgent tasks
    6. Consider energy levels and focus requirements
    7. Build in breaks for sustained productivity

    Energy and Focus Patterns:
    - HIGH ENERGY (morning): Complex problem-solving, strategic thinking, creative work
    - MEDIUM ENERGY (early afternoon): Meetings, collaboration, moderate complexity tasks
    - LOW ENERGY (late afternoon): Administrative tasks, email, routine work

    Focus Types:
    - DEEP FOCUS: Uninterrupted time for complex work (90-120 min blocks)
    - SHALLOW FOCUS: Routine tasks, can handle interruptions (30-60 min blocks)
    - COLLABORATIVE: Meetings, teamwork, communication (variable duration)

    Time Blocking Best Practices:
    - Schedule most important work first
    - Batch similar tasks together
    - Include transition time between different task types
    - Protect time for deep work
    - Build in flexibility for unexpected issues
    - Schedule breaks (Pomodoro or 90-minute cycles)

    USER:
    Create optimal time allocation for these tasks:

    Available Hours: {available_hours}
    Constraints: {constraints}

    Task Analyses:
    {chr(10).join(f"Task {i+1} ({ta.task_id}): {ta.task_description} - Priority: {ta.priority.value}, Effort: {ta.effort_level.value}, Quadrant: {ta.eisenhower_quadrant.value}" for i, ta in enumerate(task_analyses))}

    Provide realistic time blocks with task assignments, considering energy levels,
    focus requirements, and prioritization principles.
    """


# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o",
    format=list[TimeBlock],
)
async def _create_time_allocation_call(
    task_analyses: list[TaskAnalysis], available_hours: float = 8.0, constraints: str = ""
) -> str:
    """Internal LLM call for time allocation."""
    return _get_create_time_allocation_prompt(task_analyses, available_hours, constraints)


# Public wrapper - returns parsed list[TimeBlock]
async def create_time_allocation(
    task_analyses: list[TaskAnalysis], available_hours: float = 8.0, constraints: str = ""
) -> list[TimeBlock]:
    """Create optimal time allocation for prioritized tasks."""
    response = await _create_time_allocation_call(
        task_analyses=task_analyses, available_hours=available_hours, constraints=constraints
    )
    return response.parse()


def _get_recommend_strategy_prompt(task_analyses: list[TaskAnalysis], goals: str = "", context: str = "") -> str:
    """Get the prompt for recommending prioritization strategy."""
    return f"""
    SYSTEM:
    You are an expert in productivity systems and strategic task management.
    Your role is to recommend the most appropriate prioritization strategy based
    on the task portfolio, goals, and constraints.

    Available Strategies:
    1. **Eat the Frog**: Tackle the hardest, most important task first thing
    2. **Quick Wins First**: Build momentum with easy high-impact tasks
    3. **Time Blocking**: Allocate specific time slots for different task types
    4. **Energy Management**: Match task difficulty to energy levels throughout day
    5. **Batch Processing**: Group similar tasks to minimize context switching
    6. **Pareto Principle**: Focus on 20% of tasks that yield 80% of results
    7. **Warren Buffett 5/25**: Focus on top 5 tasks, avoid the rest
    8. **Ivy Lee Method**: Choose 6 most important tasks, do them in order
    9. **ABCDE Method**: Categorize tasks by consequences of not doing them
    10. **MIT (Most Important Tasks)**: Identify and complete 1-3 MITs per day

    Consider:
    - Distribution of tasks across Eisenhower quadrants
    - Balance of quick wins vs. deep work
    - Urgency vs. importance trade-offs
    - Total workload vs. capacity
    - Energy and focus requirements
    - Dependencies and blockers
    - Long-term goals and strategic objectives

    Strategy Selection Factors:
    - If many urgent tasks → Eat the Frog or Triage approach
    - If low motivation → Quick Wins First
    - If many different task types → Batch Processing or Time Blocking
    - If high-value strategic work → Energy Management + MIT
    - If overwhelmed → Warren Buffett 5/25 or ABCDE Method
    - If clear priorities → Ivy Lee Method

    USER:
    Recommend the best prioritization strategy for:

    Goals: {goals}
    Context: {context}

    Task Portfolio Summary:
    Total Tasks: {len(task_analyses)}
    Urgent & Important: {sum(1 for ta in task_analyses if ta.eisenhower_quadrant == EisenhowerQuadrant.URGENT_IMPORTANT)}
    Not Urgent & Important: {sum(1 for ta in task_analyses if ta.eisenhower_quadrant == EisenhowerQuadrant.NOT_URGENT_IMPORTANT)}
    Urgent & Not Important: {sum(1 for ta in task_analyses if ta.eisenhower_quadrant == EisenhowerQuadrant.URGENT_NOT_IMPORTANT)}
    Not Urgent & Not Important: {sum(1 for ta in task_analyses if ta.eisenhower_quadrant == EisenhowerQuadrant.NOT_URGENT_NOT_IMPORTANT)}
    Quick Wins Available: {sum(1 for ta in task_analyses if ta.quick_wins_potential)}

    Provide a comprehensive strategy recommendation with implementation guidance.
    """


# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o",
    format=PrioritizationStrategy,
)
async def _recommend_strategy_call(task_analyses: list[TaskAnalysis], goals: str = "", context: str = "") -> str:
    """Internal LLM call for strategy recommendation."""
    return _get_recommend_strategy_prompt(task_analyses, goals, context)


# Public wrapper - returns parsed PrioritizationStrategy
async def recommend_strategy(task_analyses: list[TaskAnalysis], goals: str = "", context: str = "") -> PrioritizationStrategy:
    """Recommend optimal prioritization strategy."""
    response = await _recommend_strategy_call(task_analyses=task_analyses, goals=goals, context=context)
    return response.parse()


def _get_synthesize_prioritization_prompt(
    tasks: list[str],
    task_analyses: list[TaskAnalysis],
    time_allocation: list[TimeBlock],
    strategy: PrioritizationStrategy,
    available_hours: float,
) -> str:
    """Get the prompt for synthesizing complete prioritization."""
    return f"""
    SYSTEM:
    You are a senior productivity consultant and strategic planning expert.
    Your role is to synthesize task analysis into a comprehensive, actionable
    prioritization plan with clear recommendations and next steps.

    Consider:
    1. Overall task portfolio composition
    2. Capacity vs. workload balance
    3. Quick wins for momentum
    4. Strategic important work protection
    5. Delegation opportunities
    6. Elimination candidates
    7. Risk of overcommitment
    8. Need for buffer time
    9. Balance of urgent vs. important
    10. Long-term sustainability

    Provide:
    - Clear prioritized task order with rationale
    - Realistic capacity assessment
    - Quick wins to start with
    - Tasks to delegate or eliminate
    - Total time estimation
    - Workload balance assessment
    - Actionable recommendations
    - Confidence in the prioritization

    Focus on:
    - Actionable insights over theory
    - Realistic time estimates with buffer
    - Clear next steps
    - Sustainable workload
    - Strategic alignment
    - Flexibility for unexpected issues

    USER:
    Synthesize complete prioritization for:

    Available Hours: {available_hours}
    Total Tasks: {len(tasks)}

    Task Analyses:
    {chr(10).join(f"{i+1}. {ta.task_description} (Priority: {ta.priority.value}, Quadrant: {ta.eisenhower_quadrant.value})" for i, ta in enumerate(task_analyses))}

    Time Allocation:
    {chr(10).join(f"{i+1}. {tb.time_slot} ({tb.duration}): {len(tb.task_ids)} tasks - {tb.rationale}" for i, tb in enumerate(time_allocation))}

    Strategy: {strategy.strategy_name}

    Provide comprehensive prioritization with clear recommendations and action items.
    """


# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o",
    format=TaskPrioritization,
)
async def _synthesize_prioritization_call(
    tasks: list[str],
    task_analyses: list[TaskAnalysis],
    time_allocation: list[TimeBlock],
    strategy: PrioritizationStrategy,
    available_hours: float,
) -> str:
    """Internal LLM call for prioritization synthesis."""
    return _get_synthesize_prioritization_prompt(tasks, task_analyses, time_allocation, strategy, available_hours)


# Public wrapper - returns parsed TaskPrioritization
async def synthesize_prioritization(
    tasks: list[str],
    task_analyses: list[TaskAnalysis],
    time_allocation: list[TimeBlock],
    strategy: PrioritizationStrategy,
    available_hours: float,
) -> TaskPrioritization:
    """Synthesize complete task prioritization."""
    response = await _synthesize_prioritization_call(
        tasks=tasks,
        task_analyses=task_analyses,
        time_allocation=time_allocation,
        strategy=strategy,
        available_hours=available_hours,
    )
    return response.parse()


@trace()
async def task_prioritization_agent(
    tasks: list[str],
    context: str = "",
    goals: str = "",
    available_hours: float = 8.0,
    constraints: str = "",
    llm_provider: str = "openai",
    model: str = "gpt-4o",
) -> TaskPrioritization:
    """
    Prioritize tasks using the Eisenhower Matrix and comprehensive analysis.

    This agent analyzes tasks across multiple dimensions (urgency, importance, effort,
    impact), assigns them to Eisenhower Matrix quadrants, recommends optimal prioritization
    strategies, and provides time allocation recommendations.

    Args:
        tasks: List of task descriptions to prioritize
        context: Context about the tasks and current situation
        goals: Your goals and objectives
        available_hours: Available hours for work (default: 8.0)
        constraints: Any constraints on task execution
        llm_provider: LLM provider to use
        model: Model to use for analysis

    Returns:
        TaskPrioritization with comprehensive analysis and recommendations

    Example:
        >>> result = await task_prioritization_agent(
        ...     tasks=[
        ...         "Fix critical production bug",
        ...         "Write Q4 strategy document",
        ...         "Review team PRs",
        ...         "Attend standup meeting",
        ...         "Update documentation"
        ...     ],
        ...     context="Software engineering team lead, product launch next week",
        ...     goals="Ensure stable launch, maintain team velocity, strategic planning"
        ... )
        >>> print(f"Priority Order: {result.prioritized_order}")
        >>> print(f"Quick Wins: {result.quick_wins}")
    """

    # Step 1: Analyze individual tasks
    print("Analyzing tasks...")
    task_analyses = await analyze_tasks(tasks=tasks, context=context)
    print(f"Analyzed {len(task_analyses)} tasks")

    # Step 2: Recommend prioritization strategy
    print("Recommending prioritization strategy...")
    strategy = await recommend_strategy(task_analyses=task_analyses, goals=goals, context=context)
    print(f"Recommended strategy: {strategy.strategy_name}")

    # Step 3: Create time allocation
    print("Creating time allocation...")
    time_allocation = await create_time_allocation(
        task_analyses=task_analyses, available_hours=available_hours, constraints=constraints
    )
    print(f"Created {len(time_allocation)} time blocks")

    # Step 4: Synthesize complete prioritization
    print("Synthesizing prioritization...")
    prioritization = await synthesize_prioritization(
        tasks=tasks,
        task_analyses=task_analyses,
        time_allocation=time_allocation,
        strategy=strategy,
        available_hours=available_hours,
    )

    # Add timestamp
    prioritization.analysis_timestamp = datetime.now().isoformat()

    print("Task prioritization complete!")
    return prioritization


async def task_prioritization_agent_stream(
    tasks: list[str], context: str = "", goals: str = "", **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the task prioritization process."""

    yield "Starting task prioritization analysis...\n\n"
    yield f"**Total Tasks:** {len(tasks)}\n"
    yield f"**Context:** {context or 'Not specified'}\n"
    yield f"**Goals:** {goals or 'Not specified'}\n\n"

    # Perform prioritization
    prioritization = await task_prioritization_agent(tasks, context, goals, **kwargs)

    yield "## Overview\n\n"
    yield f"**Total Tasks:** {prioritization.total_tasks}\n"
    yield f"**Total Estimated Time:** {prioritization.total_estimated_hours}\n"
    yield f"**Confidence Score:** {prioritization.confidence_score:.2f}/1.0\n"
    yield f"**Strategy:** {prioritization.strategy.strategy_name}\n\n"

    yield "## Capacity Assessment\n\n"
    yield f"{prioritization.capacity_assessment}\n\n"

    yield "## Eisenhower Matrix Distribution\n\n"
    yield f"- **Urgent & Important (Do First):** {prioritization.urgent_important_count} tasks\n"
    yield f"- **Quick Wins Identified:** {len(prioritization.quick_wins)} tasks\n"
    yield f"- **Delegation Candidates:** {len(prioritization.delegation_candidates)} tasks\n"
    yield f"- **Elimination Candidates:** {len(prioritization.elimination_candidates)} tasks\n\n"

    if prioritization.quick_wins:
        yield "## Quick Wins (Start Here!)\n\n"
        for task_id in prioritization.quick_wins[:3]:
            task = next((ta for ta in prioritization.task_analyses if ta.task_id == task_id), None)
            if task:
                yield f"- **{task.task_description}** (Est: {task.estimated_duration})\n"
        yield "\n"

    yield "## Prioritized Task Order\n\n"
    for i, task_id in enumerate(prioritization.prioritized_order[:10], 1):
        task = next((ta for ta in prioritization.task_analyses if ta.task_id == task_id), None)
        if task:
            yield f"{i}. **{task.task_description}**\n"
            yield f"   - Priority: {task.priority.value} | Quadrant: {task.eisenhower_quadrant.value}\n"
            yield f"   - Effort: {task.effort_level.value} | Impact: {task.impact_level.value}\n"
            yield f"   - Estimated Duration: {task.estimated_duration}\n\n"

    yield "## Recommended Time Blocks\n\n"
    for i, block in enumerate(prioritization.time_allocation, 1):
        yield f"### {block.time_slot} ({block.duration})\n"
        yield f"**Energy Level:** {block.energy_level_required} | **Focus Type:** {block.focus_type}\n"
        yield f"**Tasks:** {len(block.task_ids)}\n"
        yield f"**Rationale:** {block.rationale}\n\n"

    yield "## Strategy Recommendation\n\n"
    yield f"**{prioritization.strategy.strategy_name}**\n\n"
    yield f"{prioritization.strategy.rationale}\n\n"
    yield "**Key Principles:**\n"
    for principle in prioritization.strategy.key_principles:
        yield f"- {principle}\n"
    yield "\n"

    yield "## Top Recommendations\n\n"
    for i, rec in enumerate(prioritization.recommendations[:5], 1):
        yield f"{i}. {rec}\n"

    if prioritization.delegation_candidates:
        yield "\n## Consider Delegating\n\n"
        for task_id in prioritization.delegation_candidates[:3]:
            task = next((ta for ta in prioritization.task_analyses if ta.task_id == task_id), None)
            if task:
                yield f"- {task.task_description}\n"

    if prioritization.elimination_candidates:
        yield "\n## Consider Eliminating\n\n"
        for task_id in prioritization.elimination_candidates[:3]:
            task = next((ta for ta in prioritization.task_analyses if ta.task_id == task_id), None)
            if task:
                yield f"- {task.task_description}\n"

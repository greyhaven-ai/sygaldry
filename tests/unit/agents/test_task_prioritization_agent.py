"""Test suite for task_prioritization_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestTaskPrioritizationAgent(BaseAgentTest):
    """Test cases for Task Prioritization agent."""

    component_name = "task_prioritization_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/task_prioritization")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.task_prioritization_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "tasks": [
                    "Fix critical production bug",
                    "Write Q4 strategy document",
                    "Review team PRs",
                    "Attend standup meeting"
                ],
                "context": "Software engineering team lead",
                "goals": "Ensure stable launch, maintain team velocity",
                "available_hours": 8.0,
            },
            {
                "tasks": [
                    "Complete client proposal",
                    "Update project timeline",
                    "Review budget allocation"
                ],
                "context": "Project manager with tight deadline",
                "goals": "Deliver proposal by Friday",
                "available_hours": 6.0,
                "constraints": "Must attend all-hands meeting 2-3pm",
            },
            {
                "tasks": [
                    "Prepare board presentation",
                    "Interview candidates",
                    "Approve budgets",
                    "One-on-one meetings"
                ],
                "context": "Executive leader",
                "goals": "Successful board meeting, hire top talent",
                "available_hours": 10.0,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'task_prioritization_agent')
        assert callable(module.task_prioritization_agent)
        assert hasattr(module, 'task_prioritization_agent_stream')
        assert callable(module.task_prioritization_agent_stream)
        assert hasattr(module, 'analyze_tasks')
        assert callable(module.analyze_tasks)
        assert hasattr(module, 'create_time_allocation')
        assert callable(module.create_time_allocation)
        assert hasattr(module, 'recommend_strategy')
        assert callable(module.recommend_strategy)
        assert hasattr(module, 'synthesize_prioritization')
        assert callable(module.synthesize_prioritization)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'TaskAnalysis')
        assert hasattr(module, 'TaskPrioritization')
        assert hasattr(module, 'TimeBlock')
        assert hasattr(module, 'PrioritizationStrategy')
        assert hasattr(module, 'EisenhowerQuadrant')
        assert hasattr(module, 'TaskPriority')
        assert hasattr(module, 'EffortLevel')
        assert hasattr(module, 'ImpactLevel')

        # Test basic model instantiation
        TaskAnalysis = module.TaskAnalysis
        EisenhowerQuadrant = module.EisenhowerQuadrant
        TaskPriority = module.TaskPriority
        EffortLevel = module.EffortLevel
        ImpactLevel = module.ImpactLevel

        task = TaskAnalysis(
            task_id="task_1",
            task_description="Fix critical bug",
            urgency_score=0.95,
            importance_score=0.90,
            effort_level=EffortLevel.MEDIUM,
            impact_level=ImpactLevel.HIGH,
            eisenhower_quadrant=EisenhowerQuadrant.URGENT_IMPORTANT,
            priority=TaskPriority.CRITICAL,
            urgency_factors=["Blocking users"],
            importance_factors=["Core functionality"],
            effort_breakdown=["Debug", "Fix", "Test"],
            expected_impact=["Restore service"],
            dependencies=[],
            blockers=[],
            quick_wins_potential=False,
            delegation_potential=False,
            estimated_duration="4 hours"
        )
        assert task.task_id == "task_1"
        assert task.urgency_score == 0.95
        assert task.eisenhower_quadrant == EisenhowerQuadrant.URGENT_IMPORTANT

        # Test TimeBlock model
        TimeBlock = module.TimeBlock
        block = TimeBlock(
            time_slot="9:00 AM - 11:00 AM",
            duration="2 hours",
            task_ids=["task_1"],
            rationale="Critical work during high energy",
            energy_level_required="high",
            focus_type="deep"
        )
        assert len(block.task_ids) == 1
        assert block.energy_level_required == "high"

    @pytest.mark.unit
    def test_task_prioritization_agent_structure(self):
        """Test basic structure of task_prioritization_agent function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'tasks' in params
        assert 'context' in params
        assert 'goals' in params
        assert 'available_hours' in params
        assert 'constraints' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        TaskPrioritization = module.TaskPrioritization

        # Task prioritization should return a TaskPrioritization
        assert isinstance(output, TaskPrioritization)
        assert hasattr(output, "analysis_timestamp")
        assert hasattr(output, "total_tasks")
        assert hasattr(output, "task_analyses")
        assert hasattr(output, "prioritized_order")
        assert hasattr(output, "time_allocation")
        assert hasattr(output, "strategy")
        assert hasattr(output, "quick_wins")
        assert hasattr(output, "delegation_candidates")
        assert hasattr(output, "elimination_candidates")
        assert hasattr(output, "recommendations")
        assert hasattr(output, "confidence_score")
        assert isinstance(output.task_analyses, list)
        assert isinstance(output.prioritized_order, list)
        assert isinstance(output.time_allocation, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test analyze_tasks
        func = module.analyze_tasks
        assert callable(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'tasks' in params
        assert 'context' in params

        # Test create_time_allocation
        func = module.create_time_allocation
        assert callable(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task_analyses' in params
        assert 'available_hours' in params

        # Test recommend_strategy
        func = module.recommend_strategy
        assert callable(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task_analyses' in params

        # Test synthesize_prioritization
        func = module.synthesize_prioritization
        assert callable(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'tasks' in params
        assert 'task_analyses' in params
        assert 'time_allocation' in params
        assert 'strategy' in params

    @pytest.mark.unit
    def test_eisenhower_quadrants(self):
        """Test that Eisenhower matrix quadrants are defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check Eisenhower quadrants exist
        assert hasattr(module, 'EisenhowerQuadrant')
        EisenhowerQuadrant = module.EisenhowerQuadrant

        # Test quadrant values
        assert hasattr(EisenhowerQuadrant, 'URGENT_IMPORTANT')
        assert hasattr(EisenhowerQuadrant, 'NOT_URGENT_IMPORTANT')
        assert hasattr(EisenhowerQuadrant, 'URGENT_NOT_IMPORTANT')
        assert hasattr(EisenhowerQuadrant, 'NOT_URGENT_NOT_IMPORTANT')

    @pytest.mark.unit
    def test_priority_levels(self):
        """Test that priority levels are defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check priority levels exist
        assert hasattr(module, 'TaskPriority')
        TaskPriority = module.TaskPriority

        # Test priority values
        assert hasattr(TaskPriority, 'CRITICAL')
        assert hasattr(TaskPriority, 'HIGH')
        assert hasattr(TaskPriority, 'MEDIUM')
        assert hasattr(TaskPriority, 'LOW')
        assert hasattr(TaskPriority, 'DEFERRED')

    @pytest.mark.unit
    def test_effort_levels(self):
        """Test that effort levels are defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check effort levels exist
        assert hasattr(module, 'EffortLevel')
        EffortLevel = module.EffortLevel

        # Test effort values
        assert hasattr(EffortLevel, 'MINIMAL')
        assert hasattr(EffortLevel, 'LOW')
        assert hasattr(EffortLevel, 'MEDIUM')
        assert hasattr(EffortLevel, 'HIGH')
        assert hasattr(EffortLevel, 'VERY_HIGH')

    @pytest.mark.unit
    def test_impact_levels(self):
        """Test that impact levels are defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check impact levels exist
        assert hasattr(module, 'ImpactLevel')
        ImpactLevel = module.ImpactLevel

        # Test impact values
        assert hasattr(ImpactLevel, 'TRANSFORMATIONAL')
        assert hasattr(ImpactLevel, 'HIGH')
        assert hasattr(ImpactLevel, 'MODERATE')
        assert hasattr(ImpactLevel, 'LOW')
        assert hasattr(ImpactLevel, 'MINIMAL')

    @pytest.mark.unit
    def test_prompt_functions_exist(self):
        """Test that prompt generation functions exist."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for prompt functions
        source = inspect.getsource(module)
        assert '_get_analyze_tasks_prompt' in source
        assert '_get_create_time_allocation_prompt' in source
        assert '_get_recommend_strategy_prompt' in source
        assert '_get_synthesize_prioritization_prompt' in source

    @pytest.mark.unit
    def test_key_concepts(self):
        """Test that key prioritization concepts are mentioned in code."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for key concepts in source
        source = inspect.getsource(module)
        assert 'eisenhower' in source.lower()
        assert 'urgency' in source.lower()
        assert 'importance' in source.lower()
        assert 'effort' in source.lower()
        assert 'impact' in source.lower()
        assert 'delegate' in source.lower()
        assert 'quick win' in source.lower() or 'quick_win' in source.lower()
        assert 'time block' in source.lower() or 'time_block' in source.lower()

    @pytest.mark.unit
    def test_lilypad_optional(self):
        """Test that lilypad import is optional."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for try/except for lilypad import
        source = inspect.getsource(module)
        assert 'try:' in source
        assert 'from lilypad import' in source
        assert 'except ImportError:' in source
        assert 'LILYPAD_AVAILABLE' in source

    @pytest.mark.unit
    def test_mirascope_v2_usage(self):
        """Test that Mirascope v2 API is used correctly."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "task_prioritization_agent", "packages/sygaldry_registry/components/agents/task_prioritization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for Mirascope v2 patterns
        source = inspect.getsource(module)
        assert 'from mirascope import llm' in source
        assert '@llm.call' in source
        assert 'format=' in source  # v2 uses format= instead of response_model=
        assert 'model_id=' in source  # v2 uses model_id= instead of model=
        assert 'provider=' in source

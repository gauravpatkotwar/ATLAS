import pytest
from typing import Dict, Any
from atlas.workflow.engine import WorkflowStep, WorkflowContext, WorkflowEngine


class MockIncrementStep(WorkflowStep):
    """Step that increments counter by 1."""

    def __init__(self):
        super().__init__("IncrementStep")
        self.executed = False
        self.rolled_back = False

    async def execute(self, context: Dict[str, Any]) -> None:
        self.executed = True
        context["counter"] = context.get("counter", 0) + 1

    async def rollback(self, context: Dict[str, Any]) -> None:
        self.rolled_back = True
        context["counter"] = context.get("counter", 0) - 1


class MockFailStep(WorkflowStep):
    """Step designed to trigger a failure."""

    def __init__(self, failure_type: str = "permanent"):
        super().__init__("FailStep")
        self.failure_type = failure_type
        self.attempts = 0

    async def execute(self, context: Dict[str, Any]) -> None:
        self.attempts += 1
        if self.failure_type == "permanent":
            raise RuntimeError("Permanent failure")
        elif self.failure_type == "transient":
            if self.attempts < 2:
                raise ValueError("Transient network glitch")
            context["transient_status"] = "success"

    async def rollback(self, context: Dict[str, Any]) -> None:
        pass


@pytest.mark.asyncio
async def test_workflow_successful_execution():
    """Verifies that all steps succeed sequentially."""
    step = MockIncrementStep()
    engine = WorkflowEngine([step])
    context = WorkflowContext({"counter": 5})

    success = await engine.execute(context)
    assert success is True
    assert step.executed is True
    assert step.rolled_back is False
    assert context.data["counter"] == 6


@pytest.mark.asyncio
async def test_workflow_transactional_rollback():
    """Verifies that a failure triggers rollback of completed steps in reverse order."""
    step1 = MockIncrementStep()
    step2 = MockFailStep(failure_type="permanent")

    engine = WorkflowEngine([step1, step2])
    context = WorkflowContext({"counter": 10})

    success = await engine.execute(context, max_retries=1)

    assert success is False
    assert step1.executed is True
    assert step1.rolled_back is True  # Preceding step rolled back
    assert context.data["counter"] == 10  # Counter value restored back to initial
    assert len(context.errors) >= 1
    assert "Permanent failure" in context.errors[0]


@pytest.mark.asyncio
async def test_workflow_retry_handling():
    """Verifies that transient errors recover within max_retries limit."""
    step1 = MockIncrementStep()
    step2 = MockFailStep(failure_type="transient")

    engine = WorkflowEngine([step1, step2])
    context = WorkflowContext({"counter": 10})

    # Executes with retry delay set low for rapid testing
    success = await engine.execute(context, max_retries=3, retry_delay=0.01)

    assert success is True
    assert step2.attempts == 2  # Recovered on second attempt
    assert context.data["counter"] == 11
    assert context.data["transient_status"] == "success"

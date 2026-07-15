import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class WorkflowStep(ABC):
    """Abstract base step for transactional workflows."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> None:
        """Run execution logic and append outputs directly to the context dict."""
        pass

    @abstractmethod
    async def rollback(self, context: Dict[str, Any]) -> None:
        """Reverse changes made during execution in case of subsequent failures."""
        pass


class WorkflowContext:
    """Carries transactional state, inputs, outputs, logs, and error stacks."""

    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        self.data: Dict[str, Any] = initial_data or {}
        self.logs: List[str] = []
        self.errors: List[str] = []
        self.executed_steps: List[str] = []


class WorkflowEngine:
    """Sequentially executes steps with retries, rolling back all completed steps upon failure."""

    def __init__(self, steps: List[WorkflowStep]):
        self.steps = steps

    async def execute(
        self, context: WorkflowContext, max_retries: int = 3, retry_delay: float = 1.0
    ) -> bool:
        """Synchronously executes sequential workflow steps with retries and rollback."""
        completed_steps: List[WorkflowStep] = []

        for step in self.steps:
            attempts = 0
            success = False

            while attempts < max_retries:
                attempts += 1
                try:
                    logger.info(
                        f"Executing step: {step.name} (Attempt {attempts}/{max_retries})"
                    )
                    context.logs.append(f"Executing {step.name} (Attempt {attempts})")

                    await step.execute(context.data)

                    context.executed_steps.append(step.name)
                    completed_steps.append(step)
                    success = True
                    break
                except Exception as e:
                    logger.warning(
                        f"Step {step.name} failed on attempt {attempts}: {e}"
                    )
                    context.logs.append(
                        f"Step {step.name} failed (Attempt {attempts}): {e}"
                    )
                    if attempts < max_retries:
                        await asyncio.sleep(
                            retry_delay * attempts
                        )  # Linear backoff multiplier
                    else:
                        context.errors.append(
                            f"Step {step.name} failed after {max_retries} attempts: {e}"
                        )

            if not success:
                logger.error(
                    f"Workflow execution aborted at step: {step.name}. Rolling back..."
                )
                context.logs.append(
                    f"Workflow aborted at {step.name}. Initializing rollback."
                )
                await self._rollback(completed_steps, context)
                return False

        context.logs.append("Workflow completed successfully.")
        return True

    async def _rollback(
        self, completed_steps: List[WorkflowStep], context: WorkflowContext
    ) -> None:
        """Rolls back executed steps in exact reverse order of execution."""
        for step in reversed(completed_steps):
            try:
                logger.info(f"Rolling back step: {step.name}")
                context.logs.append(f"Rolling back {step.name}")
                await step.rollback(context.data)
            except Exception as e:
                err_msg = f"Critical error during rollback of step {step.name}: {e}"
                logger.critical(err_msg)
                context.errors.append(err_msg)

    @classmethod
    def execute_background(
        cls,
        steps: List[WorkflowStep],
        context: WorkflowContext,
        on_complete: Optional[Callable[[bool, WorkflowContext], Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> asyncio.Task:
        """Runs the workflow inside a fire-and-forget background asyncio Task."""

        async def run():
            engine = cls(steps)
            success = await engine.execute(
                context, max_retries=max_retries, retry_delay=retry_delay
            )
            if on_complete:
                if asyncio.iscoroutinefunction(on_complete):
                    await on_complete(success, context)
                else:
                    on_complete(success, context)
            return success

        return asyncio.create_task(run())

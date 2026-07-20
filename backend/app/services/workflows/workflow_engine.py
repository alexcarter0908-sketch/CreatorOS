from dataclasses import dataclass, field
from enum import StrEnum
from time import perf_counter
from typing import Any

from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse


class WorkflowStage(StrEnum):
    PROMPT = "prompt"
    ASSET = "asset"
    PROVIDER = "provider"
    EXPORT = "export"
    PUBLISH = "publish"


@dataclass(slots=True)
class WorkflowContext:
    """
    Runtime context shared across the workflow.
    """

    request: AIRequest
    metadata: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowResult:
    """
    Final workflow execution result.
    """

    success: bool

    workflow: str

    stages: list[str] = field(default_factory=list)

    execution_time: float = 0.0

    response: AIResponse | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)


class WorkflowEngine:
    """
    CreatorOS Workflow Engine.

    Responsibilities
    ----------------
    - Track execution lifecycle
    - Record workflow stages
    - Store runtime metadata
    - Wrap final AIResponse

    This engine NEVER:
    - Detect assets
    - Optimize prompts
    - Call providers directly

    Those responsibilities belong to:
        PromptEngine
        AssetIntelligence
        ProviderManager
    """

    async def execute(
        self,
        workflow: str,
        context: WorkflowContext,
        executor,
    ) -> WorkflowResult:

        started = perf_counter()

        result = WorkflowResult(
            success=False,
            workflow=workflow,
        )

        try:

            result.stages.append(
                WorkflowStage.PROMPT.value,
            )

            result.stages.append(
                WorkflowStage.ASSET.value,
            )

            result.stages.append(
                WorkflowStage.PROVIDER.value,
            )

            response = await executor(
                context.request,
            )

            result.success = response.success

            result.response = response

            result.metadata.update(
                context.metadata,
            )

        except Exception as exc:

            result.success = False

            result.warnings.append(
                str(exc),
            )

        finally:

            result.execution_time = (
                perf_counter() - started
            )

        return result
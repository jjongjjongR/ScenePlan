# src/schemas/execution_schema.py

# 2026-04-29 신규: symbolic execution 결과를 표현하기 위한 dataclass입니다.
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class StepExecutionResult:
    """작업 계획의 한 step을 실행한 결과입니다."""

    step_id: int
    action: str
    success: bool
    reason: Optional[str]


@dataclass
class ExecutionResult:
    """작업 계획 전체를 symbolic하게 실행한 결과입니다."""

    success: bool
    step_results: List[StepExecutionResult]
    final_state: Dict[str, Any]
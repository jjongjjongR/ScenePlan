# src/schemas/plan_schema.py

# 2026-04-29 신규: 로봇 작업 계획을 표현하기 위한 dataclass입니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PlanStep:
    """작업 계획 안의 한 단계를 표현합니다."""

    step_id: int
    action: str
    target: str
    destination: Optional[str] = None


@dataclass
class TaskPlan:
    """여러 PlanStep으로 구성된 전체 작업 계획입니다."""

    plan_id: str
    instruction: str
    steps: List[PlanStep]
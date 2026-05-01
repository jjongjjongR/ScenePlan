# src/schemas/validation_schema.py

# 2026-05-02 수정: symbolic validation 결과와 geometric feasibility 결과를 함께 표현할 수 있도록 확장했습니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationIssue:
    """작업 계획에서 발견된 symbolic 문제를 표현합니다."""

    failure_type: str
    failed_step_id: int
    reason: str
    suggested_fix: Optional[str]


@dataclass
class ValidationResult:
    """작업 계획 전체에 대한 symbolic 검증 결과입니다."""

    valid: bool
    issues: List[ValidationIssue]


@dataclass
class FeasibilityIssue:
    """Skill Path에서 발견된 geometric feasibility 문제를 표현합니다."""

    failure_type: str
    failed_step_id: int
    waypoint_index: Optional[int]
    reason: str
    suggested_fix: Optional[str]


@dataclass
class FeasibilityResult:
    """Skill Path 전체에 대한 geometric feasibility 검증 결과입니다."""

    feasible: bool
    issues: List[FeasibilityIssue]
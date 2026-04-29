# src/schemas/validation_schema.py

# 2026-04-29 신규: plan 검증 결과를 표현하기 위한 dataclass입니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationIssue:
    """작업 계획에서 발견된 하나의 문제를 표현합니다."""

    failure_type: str
    failed_step_id: int
    reason: str
    suggested_fix: Optional[str]


@dataclass
class ValidationResult:
    """작업 계획 전체에 대한 검증 결과입니다."""

    valid: bool
    issues: List[ValidationIssue]
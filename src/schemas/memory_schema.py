# src/schemas/memory_schema.py

# 2026-04-29 신규: 실패 사례 memory를 표현하기 위한 dataclass입니다.
from dataclasses import dataclass
from typing import List


@dataclass
class FailureMemoryRecord:
    """실패한 plan과 수정된 plan, 그리고 lesson을 저장하는 memory record입니다."""

    memory_id: str
    instruction_text: str
    failure_type: str
    bad_plan: List[str]
    corrected_plan: List[str]
    lesson: str
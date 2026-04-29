# src/schemas/instruction_schema.py

# 2026-04-29 신규: 한국어 명령을 파싱한 결과를 담는 dataclass입니다.
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedInstruction:
    """사람의 자연어 명령에서 뽑아낸 핵심 정보를 표현합니다."""

    raw_text: str
    intent: str
    target_category: Optional[str]
    target_color: Optional[str]
    source_relation: Optional[str]
    source_place_type: Optional[str]
    destination_type: Optional[str]
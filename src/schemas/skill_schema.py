# src/schemas/skill_schema.py

# 2026-04-29 신규: 로봇 skill library 데이터를 표현하기 위한 dataclass입니다.
from dataclasses import dataclass
from typing import List


@dataclass
class Skill:
    """OPEN, PICK, PLACE 같은 로봇의 추상 행동 skill을 표현합니다."""

    skill_id: str
    action: str
    description: str
    target_type: str
    required_conditions: List[str]
    effects: List[str]


@dataclass
class SkillLibrary:
    """여러 Skill을 담는 skill library입니다."""

    skills: List[Skill]
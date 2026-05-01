# src/schemas/skill_path_schema.py

# 2026-05-02 신규: Task Plan을 실행 후보 경로로 확장한 Skill Path dataclass입니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Waypoint:
    """하나의 skill이 접근해야 하는 3D waypoint입니다."""

    index: int
    position: List[float]
    orientation: List[float]
    description: Optional[str] = None


@dataclass
class SkillPathStep:
    """Task Plan의 한 step에 대응되는 skill path step입니다."""

    step_id: int
    action: str
    target: str
    waypoints: List[Waypoint]
    destination: Optional[str] = None


@dataclass
class SkillPath:
    """여러 skill path step을 묶은 전체 실행 후보 경로입니다."""

    path_id: str
    plan_id: str
    base_pose_id: str
    skills: List[SkillPathStep]
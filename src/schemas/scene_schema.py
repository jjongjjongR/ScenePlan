# src/schemas/scene_schema.py

# 2026-04-29 신규: scene JSON 데이터를 Python 객체로 표현하기 위한 dataclass 모음입니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Place:
    """테이블, 서랍처럼 물체가 놓이거나 열릴 수 있는 장소/구조물입니다."""

    place_id: str
    type: str
    name: str
    state: Optional[str]
    visible: bool
    reachable: bool


@dataclass
class SceneObject:
    """컵, 그릇처럼 로봇이 집거나 옮길 수 있는 물체입니다."""

    object_id: str
    category: str
    name: str
    color: Optional[str]
    location: str
    visible: bool
    reachable: bool
    graspable: bool


@dataclass
class Relation:
    """물체와 장소 사이의 관계를 표현합니다. 예: cup_red_1 inside drawer_1"""

    subject: str
    relation: str
    object: str


@dataclass
class RobotState:
    """현재 로봇의 상태를 표현합니다."""

    holding: Optional[str]
    gripper_state: str
    current_location: str


@dataclass
class SemanticScene:
    """하나의 장면 전체를 표현합니다."""

    scene_id: str
    description: str
    places: List[Place]
    objects: List[SceneObject]
    relations: List[Relation]
    robot_state: RobotState
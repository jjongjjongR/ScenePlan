# src/schemas/scene_schema.py

# 2026-05-02 수정: 기존 symbolic scene schema에 MVP용 3D scene field를 추가했습니다.
from dataclasses import dataclass, field
from typing import List, Optional

from src.schemas.geometry_schema import BasePoseCandidate, Box3D, Pose3D


@dataclass
class Place:
    """테이블, 서랍처럼 물체가 놓이거나 열릴 수 있는 장소/구조물입니다."""

    place_id: str
    type: str
    name: str
    state: Optional[str]
    visible: bool
    reachable: bool

    # 2026-05-02 신규: 3D 위치, 크기, handle/place waypoint 정보를 저장합니다.
    pose: Optional[Pose3D] = None
    bbox_3d: Optional[Box3D] = None
    handle_pose: Optional[Pose3D] = None
    place_pose: Optional[Pose3D] = None


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

    # 2026-05-02 신규: hidden object 정보 출처와 3D grasp 정보를 저장합니다.
    known_from: Optional[str] = None
    pose: Optional[Pose3D] = None
    bbox_3d: Optional[Box3D] = None
    grasp_pose: Optional[Pose3D] = None


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

    # 2026-05-02 신규: simplified geometric feasibility 검증에 필요한 로봇 상태입니다.
    base_pose: Optional[List[float]] = None
    current_base_pose_id: Optional[str] = None
    arm_reach_radius: Optional[float] = None
    min_clearance: Optional[float] = None


@dataclass
class SemanticScene:
    """하나의 장면 전체를 표현합니다."""

    scene_id: str
    description: str
    places: List[Place]
    objects: List[SceneObject]
    relations: List[Relation]
    robot_state: RobotState

    # 2026-05-02 신규: local repair에서 사용할 base pose 후보 목록입니다.
    base_pose_candidates: List[BasePoseCandidate] = field(default_factory=list)
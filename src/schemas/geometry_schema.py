# src/schemas/geometry_schema.py

# 2026-05-02 신규: 3D scene 정보를 표현하기 위한 geometry dataclass 모음입니다.
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pose3D:
    """
    3D 위치와 방향을 표현합니다.

    position:
        [x, y, z]

    orientation:
        quaternion 형식 [x, y, z, w]
    """

    position: List[float]
    orientation: List[float]


@dataclass
class Box3D:
    """
    3D bounding box를 표현합니다.

    bbox_3d 배열 순서:
        [center_x, center_y, center_z, size_x, size_y, size_z]
    """

    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float


@dataclass
class BasePoseCandidate:
    """
    로봇 base pose 후보를 표현합니다.

    pose:
        [x, y, theta]
    """

    base_pose_id: str
    pose: List[float]
    description: Optional[str] = None
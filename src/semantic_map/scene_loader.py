# src/semantic_map/scene_loader.py

# 2026-05-02 수정: scene JSON의 symbolic field와 MVP용 3D field를 함께 읽도록 확장했습니다.
from typing import Any, Dict, List, Optional

from src.schemas.geometry_schema import BasePoseCandidate, Box3D, Pose3D
from src.schemas.scene_schema import (
    Place,
    Relation,
    RobotState,
    SceneObject,
    SemanticScene,
)
from src.utils.io import read_json


def load_scene(path: str) -> SemanticScene:
    """
    scene JSON 파일을 읽어 SemanticScene 객체로 변환합니다.

    Args:
        path: scene JSON 파일 경로

    Returns:
        SemanticScene 객체

    Raises:
        ValueError: 필수 데이터가 비어 있거나 잘못된 경우
    """

    data = read_json(path)

    _validate_scene_data(data)

    places = _parse_places(data.get("places", []))
    objects = _parse_objects(data.get("objects", []))
    relations = _parse_relations(data.get("relations", []))
    robot_state = _parse_robot_state(data.get("robot_state", {}))
    base_pose_candidates = _parse_base_pose_candidates(
        data.get("base_pose_candidates", [])
    )

    return SemanticScene(
        scene_id=data["scene_id"],
        description=data.get("description", ""),
        places=places,
        objects=objects,
        relations=relations,
        robot_state=robot_state,
        base_pose_candidates=base_pose_candidates,
    )


def _validate_scene_data(data: Dict[str, Any]) -> None:
    """
    scene JSON의 가장 기본적인 필수값을 검사합니다.
    """

    if not data.get("scene_id"):
        raise ValueError("scene_id is required.")

    if not data.get("places"):
        raise ValueError("places must not be empty.")

    if not data.get("objects"):
        raise ValueError("objects must not be empty.")

    if "robot_state" not in data:
        raise ValueError("robot_state is required.")


def _parse_places(place_items: List[Dict[str, Any]]) -> List[Place]:
    """
    JSON의 places 배열을 Place 객체 리스트로 변환합니다.
    """

    places = []

    for item in place_items:
        place = Place(
            place_id=item["place_id"],
            type=item["type"],
            name=item.get("name", item["type"]),
            state=item.get("state"),
            visible=item["visible"],
            reachable=item["reachable"],
            pose=_parse_pose_3d(item.get("pose")),
            bbox_3d=_parse_bbox_3d(item.get("bbox_3d")),
            handle_pose=_parse_pose_3d(item.get("handle_pose")),
            place_pose=_parse_pose_3d(item.get("place_pose")),
        )
        places.append(place)

    return places


def _parse_objects(object_items: List[Dict[str, Any]]) -> List[SceneObject]:
    """
    JSON의 objects 배열을 SceneObject 객체 리스트로 변환합니다.
    """

    objects = []

    for item in object_items:
        scene_object = SceneObject(
            object_id=item["object_id"],
            category=item["category"],
            name=item.get("name", item["category"]),
            color=item.get("color"),
            location=item["location"],
            visible=item["visible"],
            reachable=item["reachable"],
            graspable=item["graspable"],
            known_from=item.get("known_from"),
            pose=_parse_pose_3d(item.get("pose")),
            bbox_3d=_parse_bbox_3d(item.get("bbox_3d")),
            grasp_pose=_parse_pose_3d(item.get("grasp_pose")),
        )
        objects.append(scene_object)

    return objects


def _parse_relations(relation_items: List[Dict[str, Any]]) -> List[Relation]:
    """
    JSON의 relations 배열을 Relation 객체 리스트로 변환합니다.
    """

    relations = []

    for item in relation_items:
        relation = Relation(
            subject=item["subject"],
            relation=item["relation"],
            object=item["object"],
        )
        relations.append(relation)

    return relations


def _parse_robot_state(item: Dict[str, Any]) -> RobotState:
    """
    JSON의 robot_state 객체를 RobotState 객체로 변환합니다.
    """

    return RobotState(
        holding=item.get("holding"),
        gripper_state=item["gripper_state"],
        current_location=item["current_location"],
        base_pose=item.get("base_pose"),
        current_base_pose_id=item.get("current_base_pose_id"),
        arm_reach_radius=item.get("arm_reach_radius"),
        min_clearance=item.get("min_clearance"),
    )


def _parse_base_pose_candidates(
    candidate_items: List[Dict[str, Any]]
) -> List[BasePoseCandidate]:
    """
    JSON의 base_pose_candidates 배열을 BasePoseCandidate 객체 리스트로 변환합니다.
    """

    candidates = []

    for item in candidate_items:
        candidate = BasePoseCandidate(
            base_pose_id=item["base_pose_id"],
            pose=item["pose"],
            description=item.get("description"),
        )
        candidates.append(candidate)

    return candidates


def _parse_pose_3d(item: Optional[Dict[str, Any]]) -> Optional[Pose3D]:
    """
    JSON의 pose 객체를 Pose3D로 변환합니다.
    """

    if item is None:
        return None

    position = item.get("position")
    orientation = item.get("orientation")

    if not isinstance(position, list) or len(position) != 3:
        raise ValueError("Pose3D position must be a list of 3 floats.")

    if not isinstance(orientation, list) or len(orientation) != 4:
        raise ValueError("Pose3D orientation must be a list of 4 floats.")

    return Pose3D(
        position=position,
        orientation=orientation,
    )


def _parse_bbox_3d(item: Optional[List[float]]) -> Optional[Box3D]:
    """
    JSON의 bbox_3d 배열을 Box3D로 변환합니다.

    bbox_3d 순서:
    [center_x, center_y, center_z, size_x, size_y, size_z]
    """

    if item is None:
        return None

    if not isinstance(item, list) or len(item) != 6:
        raise ValueError("bbox_3d must be a list of 6 floats.")

    return Box3D(
        center_x=item[0],
        center_y=item[1],
        center_z=item[2],
        size_x=item[3],
        size_y=item[4],
        size_z=item[5],
    )
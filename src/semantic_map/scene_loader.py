# src/semantic_map/scene_loader.py

# 2026-04-29 신규: scene JSON 파일을 SemanticScene dataclass 객체로 변환합니다.
from typing import Any, Dict, List

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

    return SemanticScene(
        scene_id=data["scene_id"],
        description=data.get("description", ""),
        places=places,
        objects=objects,
        relations=relations,
        robot_state=robot_state,
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
    )
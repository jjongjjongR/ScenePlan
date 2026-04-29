# src/semantic_map/object_finder.py

# 2026-04-29 신규: SemanticScene 안에서 object와 place를 찾는 함수 모음입니다.
from typing import List, Optional

from src.schemas.scene_schema import Place, SceneObject, SemanticScene


def find_object_by_id(scene: SemanticScene, object_id: str) -> Optional[SceneObject]:
    """
    object_id로 scene 안의 물체를 찾습니다.

    Args:
        scene: SemanticScene 객체
        object_id: 찾고 싶은 object_id

    Returns:
        찾으면 SceneObject, 없으면 None
    """

    for scene_object in scene.objects:
        if scene_object.object_id == object_id:
            return scene_object

    return None


def find_place_by_id(scene: SemanticScene, place_id: str) -> Optional[Place]:
    """
    place_id로 scene 안의 장소/구조물을 찾습니다.

    Args:
        scene: SemanticScene 객체
        place_id: 찾고 싶은 place_id

    Returns:
        찾으면 Place, 없으면 None
    """

    for place in scene.places:
        if place.place_id == place_id:
            return place

    return None


def find_place_by_type(scene: SemanticScene, place_type: Optional[str]) -> Optional[Place]:
    """
    type으로 scene 안의 장소/구조물을 찾습니다.
    예: table, drawer

    Args:
        scene: SemanticScene 객체
        place_type: 찾고 싶은 place type

    Returns:
        찾으면 Place, 없으면 None
    """

    if place_type is None:
        return None

    for place in scene.places:
        if place.type == place_type:
            return place

    return None


def find_object_by_attributes(
    scene: SemanticScene,
    category: Optional[str],
    color: Optional[str],
) -> Optional[SceneObject]:
    """
    category와 color 조건으로 scene 안의 물체를 찾습니다.

    Args:
        scene: SemanticScene 객체
        category: 물체 종류. 예: cup
        color: 물체 색상. 예: red

    Returns:
        조건에 맞는 SceneObject. 없으면 None

    우선순위:
        1. category가 일치해야 합니다.
        2. color가 주어졌다면 color도 일치해야 합니다.
        3. 후보가 여러 개면 visible=True인 물체를 우선합니다.
        4. 그래도 여러 개면 첫 번째 후보를 반환합니다.
    """

    candidates = _filter_objects_by_category(scene.objects, category)
    candidates = _filter_objects_by_color(candidates, color)

    if not candidates:
        return None

    visible_candidates = []

    for candidate in candidates:
        if candidate.visible:
            visible_candidates.append(candidate)

    if visible_candidates:
        return visible_candidates[0]

    return candidates[0]


def _filter_objects_by_category(
    objects: List[SceneObject],
    category: Optional[str],
) -> List[SceneObject]:
    """
    category 조건에 맞는 object만 남깁니다.
    """

    if category is None:
        return objects

    matched_objects = []

    for scene_object in objects:
        if scene_object.category == category:
            matched_objects.append(scene_object)

    return matched_objects


def _filter_objects_by_color(
    objects: List[SceneObject],
    color: Optional[str],
) -> List[SceneObject]:
    """
    color 조건에 맞는 object만 남깁니다.
    """

    if color is None:
        return objects

    matched_objects = []

    for scene_object in objects:
        if scene_object.color == color:
            matched_objects.append(scene_object)

    return matched_objects
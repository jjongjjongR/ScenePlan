# src/semantic_map/relation_finder.py

# 2026-04-29 신규: SemanticScene 안에서 object-place 관계를 찾는 함수 모음입니다.
from typing import List, Optional
from src.schemas.scene_schema import Relation, SceneObject, SemanticScene


def find_relation(
    scene: SemanticScene,
    subject_id: str,
    relation_name: str,
) -> Optional[Relation]:
    """
    특정 subject가 가진 특정 relation을 찾습니다.

    Args:
        scene: SemanticScene 객체
        subject_id: 관계의 주체. 예: cup_red_1
        relation_name: 찾을 관계 이름. 예: inside

    Returns:
        찾으면 Relation, 없으면 None
    """

    for relation in scene.relations:
        if relation.subject == subject_id and relation.relation == relation_name:
            return relation

    return None


def get_container_of_object(scene: SemanticScene, object_id: str) -> Optional[str]:
    """
    object가 inside 관계로 들어 있는 container를 찾습니다.

    Args:
        scene: SemanticScene 객체
        object_id: 확인할 object_id

    Returns:
        container_id. 없으면 None

    예:
        cup_red_1 inside drawer_1
        → drawer_1
    """

    inside_relation = find_relation(
        scene=scene,
        subject_id=object_id,
        relation_name="inside",
    )

    if inside_relation is not None:
        return inside_relation.object

    target_object = _find_object_by_id(scene, object_id)

    if target_object is None:
        return None

    if target_object.location.startswith("inside:"):
        return target_object.location.replace("inside:", "")

    return None


def get_objects_inside(scene: SemanticScene, container_id: str) -> List[SceneObject]:
    """
    특정 container 안에 들어 있는 object들을 찾습니다.

    Args:
        scene: SemanticScene 객체
        container_id: drawer_1 같은 container id

    Returns:
        container 안에 있는 SceneObject 리스트
    """

    objects_inside = []

    for scene_object in scene.objects:
        object_container_id = get_container_of_object(scene, scene_object.object_id)

        if object_container_id == container_id:
            objects_inside.append(scene_object)

    return objects_inside


def _find_object_by_id(scene: SemanticScene, object_id: str) -> Optional[SceneObject]:
    """
    relation_finder 내부에서만 사용하는 간단한 object 검색 함수입니다.
    """

    for scene_object in scene.objects:
        if scene_object.object_id == object_id:
            return scene_object

    return None
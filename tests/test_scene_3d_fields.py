# tests/test_scene_3d_fields.py

# 2026-05-02 신규: scene_loader가 3D scene field를 올바르게 읽는지 확인합니다.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.semantic_map.object_finder import find_object_by_id, find_place_by_id
from src.semantic_map.scene_loader import load_scene


def test_load_3d_scene_fields() -> None:
    scene = load_scene("data/scenes/scene_001.json")

    drawer = find_place_by_id(scene, "drawer_1")
    red_cup = find_object_by_id(scene, "cup_red_1")

    assert drawer is not None
    assert red_cup is not None

    assert drawer.pose is not None
    assert drawer.bbox_3d is not None
    assert drawer.handle_pose is not None

    assert red_cup.pose is not None
    assert red_cup.bbox_3d is not None
    assert red_cup.grasp_pose is not None

    assert scene.robot_state.base_pose is not None
    assert scene.robot_state.arm_reach_radius is not None
    assert len(scene.base_pose_candidates) >= 2


def test_symbolic_fields_still_work_after_3d_extension() -> None:
    scene = load_scene("data/scenes/scene_001.json")

    red_cup = find_object_by_id(scene, "cup_red_1")

    assert red_cup is not None
    assert red_cup.location == "inside:drawer_1"
    assert red_cup.visible is False
    assert red_cup.reachable is False
    assert red_cup.graspable is True


if __name__ == "__main__":
    test_load_3d_scene_fields()
    test_symbolic_fields_still_work_after_3d_extension()
    print("scene 3d field tests passed")
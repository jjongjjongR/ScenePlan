# tests/test_geometry_and_skill_path_schema.py

# 2026-05-02 신규: geometry schema와 skill path schema가 정상적으로 생성되는지 확인합니다.
import sys
from pathlib import Path

# 2026-05-02 신규: 테스트 파일을 직접 실행해도 프로젝트 루트의 src 패키지를 찾을 수 있도록 경로를 추가합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.schemas.geometry_schema import BasePoseCandidate, Box3D, Pose3D
from src.schemas.skill_path_schema import SkillPath, SkillPathStep, Waypoint


def test_create_pose_3d() -> None:
    pose = Pose3D(
        position=[0.50, 0.05, 0.68],
        orientation=[0, 0, 0, 1],
    )

    assert pose.position == [0.50, 0.05, 0.68]
    assert pose.orientation == [0, 0, 0, 1]


def test_create_box_3d() -> None:
    box = Box3D(
        center_x=0.50,
        center_y=0.20,
        center_z=0.65,
        size_x=0.40,
        size_y=0.30,
        size_z=0.25,
    )

    assert box.center_x == 0.50
    assert box.center_y == 0.20
    assert box.center_z == 0.65
    assert box.size_x == 0.40
    assert box.size_y == 0.30
    assert box.size_z == 0.25


def test_create_base_pose_candidate() -> None:
    candidate = BasePoseCandidate(
        base_pose_id="base_good_1",
        pose=[0.45, -0.20, 1.57],
        description="Better base pose for opening drawer and grasping cup.",
    )

    assert candidate.base_pose_id == "base_good_1"
    assert candidate.pose == [0.45, -0.20, 1.57]
    assert candidate.description == "Better base pose for opening drawer and grasping cup."


def test_create_skill_path() -> None:
    pick_waypoint = Waypoint(
        index=0,
        position=[0.50, 0.22, 0.72],
        orientation=[0, 0, 0, 1],
        description="Grasp pose for cup_red_1",
    )

    place_waypoint = Waypoint(
        index=0,
        position=[0.70, 0.00, 0.75],
        orientation=[0, 0, 0, 1],
        description="Place pose on table_1",
    )

    pick_step = SkillPathStep(
        step_id=1,
        action="PICK",
        target="cup_red_1",
        waypoints=[pick_waypoint],
    )

    place_step = SkillPathStep(
        step_id=2,
        action="PLACE",
        target="cup_red_1",
        destination="table_1",
        waypoints=[place_waypoint],
    )

    skill_path = SkillPath(
        path_id="raw_skill_path_001",
        plan_id="raw_plan_001",
        base_pose_id="base_bad_1",
        skills=[pick_step, place_step],
    )

    assert skill_path.path_id == "raw_skill_path_001"
    assert skill_path.plan_id == "raw_plan_001"
    assert skill_path.base_pose_id == "base_bad_1"
    assert len(skill_path.skills) == 2

    assert skill_path.skills[0].action == "PICK"
    assert skill_path.skills[0].target == "cup_red_1"
    assert skill_path.skills[0].waypoints[0].position == [0.50, 0.22, 0.72]

    assert skill_path.skills[1].action == "PLACE"
    assert skill_path.skills[1].target == "cup_red_1"
    assert skill_path.skills[1].destination == "table_1"
    assert skill_path.skills[1].waypoints[0].position == [0.70, 0.00, 0.75]


if __name__ == "__main__":
    test_create_pose_3d()
    test_create_box_3d()
    test_create_base_pose_candidate()
    test_create_skill_path()
    print("geometry and skill path schema tests passed")
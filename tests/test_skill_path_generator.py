# tests/test_skill_path_generator.py

# 2026-05-02 신규: raw task plan을 skill path candidate로 변환하는지 확인합니다.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.schemas.plan_schema import PlanStep, TaskPlan
from src.skills.skill_path_generator import create_skill_path
from src.semantic_map.scene_loader import load_scene


def test_create_skill_path_from_raw_plan() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")

    raw_plan = create_raw_plan(
        instruction=instruction,
        scene=scene,
    )

    skill_path = create_skill_path(
        plan=raw_plan,
        scene=scene,
    )

    assert skill_path.path_id == "raw_skill_path_001"
    assert skill_path.plan_id == "raw_plan_001"
    assert skill_path.base_pose_id == "base_bad_1"
    assert len(skill_path.skills) == 2

    pick_step = skill_path.skills[0]
    place_step = skill_path.skills[1]

    assert pick_step.step_id == 1
    assert pick_step.action == "PICK"
    assert pick_step.target == "cup_red_1"
    assert pick_step.destination is None
    assert len(pick_step.waypoints) == 1
    assert pick_step.waypoints[0].position == [0.50, 0.22, 0.72]

    assert place_step.step_id == 2
    assert place_step.action == "PLACE"
    assert place_step.target == "cup_red_1"
    assert place_step.destination == "table_1"
    assert len(place_step.waypoints) == 1
    assert place_step.waypoints[0].position == [0.70, 0.00, 0.75]


def test_create_skill_path_with_open_step() -> None:
    scene = load_scene("data/scenes/scene_001.json")

    corrected_plan = TaskPlan(
        plan_id="corrected_plan_001",
        instruction="서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.",
        steps=[
            PlanStep(
                step_id=1,
                action="OPEN",
                target="drawer_1",
            ),
            PlanStep(
                step_id=2,
                action="PICK",
                target="cup_red_1",
            ),
            PlanStep(
                step_id=3,
                action="PLACE",
                target="cup_red_1",
                destination="table_1",
            ),
        ],
    )

    skill_path = create_skill_path(
        plan=corrected_plan,
        scene=scene,
        path_id="corrected_skill_path_001",
    )

    assert skill_path.path_id == "corrected_skill_path_001"
    assert skill_path.plan_id == "corrected_plan_001"
    assert skill_path.base_pose_id == "base_bad_1"
    assert len(skill_path.skills) == 3

    open_step = skill_path.skills[0]
    pick_step = skill_path.skills[1]
    place_step = skill_path.skills[2]

    assert open_step.action == "OPEN"
    assert open_step.target == "drawer_1"
    assert open_step.waypoints[0].position == [0.50, 0.05, 0.68]

    assert pick_step.action == "PICK"
    assert pick_step.target == "cup_red_1"
    assert pick_step.waypoints[0].position == [0.50, 0.22, 0.72]

    assert place_step.action == "PLACE"
    assert place_step.destination == "table_1"
    assert place_step.waypoints[0].position == [0.70, 0.00, 0.75]


if __name__ == "__main__":
    test_create_skill_path_from_raw_plan()
    test_create_skill_path_with_open_step()
    print("skill path generator tests passed")
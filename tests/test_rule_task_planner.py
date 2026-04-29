# 2026-04-29 신규: rule_task_planner가 ParsedInstruction과 SemanticScene으로 raw plan을 만드는지 확인합니다.

import sys
from pathlib import Path

# 2026-04-29 신규: 테스트 파일을 직접 실행해도 프로젝트 루트의 src 패키지를 찾을 수 있도록 경로를 추가합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.semantic_map.scene_loader import load_scene


def test_create_retrieve_and_place_raw_plan() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")

    raw_plan = create_raw_plan(
        instruction=instruction,
        scene=scene,
    )

    assert raw_plan.plan_id == "raw_plan_001"
    assert raw_plan.instruction == "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘."
    assert len(raw_plan.steps) == 2

    first_step = raw_plan.steps[0]
    second_step = raw_plan.steps[1]

    assert first_step.step_id == 1
    assert first_step.action == "PICK"
    assert first_step.target == "cup_red_1"
    assert first_step.destination is None

    assert second_step.step_id == 2
    assert second_step.action == "PLACE"
    assert second_step.target == "cup_red_1"
    assert second_step.destination == "table_1"


def test_raw_plan_does_not_include_open_step() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")

    raw_plan = create_raw_plan(
        instruction=instruction,
        scene=scene,
    )

    actions = []

    for step in raw_plan.steps:
        actions.append(step.action)

    assert "OPEN" not in actions


def test_create_simple_retrieve_raw_plan() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("파란 컵을 집어줘.")

    raw_plan = create_raw_plan(
        instruction=instruction,
        scene=scene,
    )

    assert len(raw_plan.steps) == 1
    assert raw_plan.steps[0].step_id == 1
    assert raw_plan.steps[0].action == "PICK"
    assert raw_plan.steps[0].target == "cup_blue_1"
    assert raw_plan.steps[0].destination is None


if __name__ == "__main__":
    test_create_retrieve_and_place_raw_plan()
    test_raw_plan_does_not_include_open_step()
    test_create_simple_retrieve_raw_plan()
    print("rule_task_planner tests passed")
# tests/test_repair.py

# 2026-05-02 신규: symbolic_repair와 base_pose_repair 로직을 테스트합니다.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.correction.base_pose_repair import find_feasible_base_pose
from src.correction.symbolic_repair import repair_symbolic_plan
from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.semantic_map.scene_loader import load_scene
from src.skills.skill_path_generator import create_skill_path
from src.verifier.reachability_checker import check_reachability
from src.verifier.symbolic_verifier import verify_symbolic_plan


def test_symbolic_repair() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")
    
    raw_plan = create_raw_plan(instruction, scene)
    validation_result = verify_symbolic_plan(raw_plan, scene)
    
    assert validation_result.valid is False
    
    # Repair
    repaired_plan = repair_symbolic_plan(raw_plan, validation_result)
    
    assert repaired_plan.plan_id == "raw_plan_001_repaired"
    assert len(repaired_plan.steps) == 3
    
    # 1. OPEN drawer_1
    # 2. PICK cup_red_1
    # 3. PLACE cup_red_1 -> table_1
    assert repaired_plan.steps[0].action == "OPEN"
    assert repaired_plan.steps[0].target == "drawer_1"
    assert repaired_plan.steps[0].step_id == 1
    
    assert repaired_plan.steps[1].action == "PICK"
    assert repaired_plan.steps[1].target == "cup_red_1"
    assert repaired_plan.steps[1].step_id == 2
    
    assert repaired_plan.steps[2].action == "PLACE"
    assert repaired_plan.steps[2].step_id == 3

    # 검증을 다시 하면 통과해야 함
    # (단, MVP 수준에서 OPEN을 추가하면 이후 step 검증에서 scene state 변경을 추적하지는 않으므로 
    # 완벽한 재검증은 생략하고 구조가 잘 바뀌었는지만 확인합니다.)


def test_base_pose_repair() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")
    raw_plan = create_raw_plan(instruction, scene)
    skill_path = create_skill_path(raw_plan, scene)
    
    # 현재 bad pose
    feasibility_result = check_reachability(skill_path, scene)
    assert feasibility_result.feasible is False
    
    # Repair
    feasible_base_pose_id = find_feasible_base_pose(skill_path, scene)
    
    assert feasible_base_pose_id == "base_good_1"


if __name__ == "__main__":
    test_symbolic_repair()
    test_base_pose_repair()
    print("repair tests passed")

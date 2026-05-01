# tests/test_verifier.py

# 2026-05-02 신규: symbolic verifier와 reachability checker가 제대로 동작하는지 테스트합니다.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.semantic_map.scene_loader import load_scene
from src.skills.skill_path_generator import create_skill_path
from src.verifier.reachability_checker import check_reachability
from src.verifier.symbolic_verifier import verify_symbolic_plan


def test_symbolic_verifier() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")
    
    # 1. 닫힌 서랍 안의 컵을 바로 PICK하려고 하는 계획
    raw_plan = create_raw_plan(instruction, scene)
    
    validation_result = verify_symbolic_plan(raw_plan, scene)
    
    assert validation_result.valid is False
    assert len(validation_result.issues) == 1
    
    issue = validation_result.issues[0]
    assert issue.failure_type == "missing_precondition"
    assert "closed drawer_1" in issue.reason
    assert issue.suggested_fix == "OPEN drawer_1 before PICK cup_red_1"


def test_reachability_checker_bad_pose() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")
    raw_plan = create_raw_plan(instruction, scene)
    
    # 현재 scene.robot_state.base_pose 는 base_bad_1 이며,
    # distance가 arm_reach_radius(0.6)를 넘어서 실패해야 함.
    skill_path = create_skill_path(raw_plan, scene)
    
    feasibility_result = check_reachability(skill_path, scene)
    
    assert feasibility_result.feasible is False
    assert len(feasibility_result.issues) > 0
    assert feasibility_result.issues[0].failure_type == "arm_reachability_failure"


def test_reachability_checker_good_pose() -> None:
    scene = load_scene("data/scenes/scene_001.json")
    
    # scene의 현재 base pose를 수동으로 좋은 위치로 변경
    good_pose = None
    for candidate in scene.base_pose_candidates:
        if candidate.base_pose_id == "base_good_1":
            good_pose = candidate.pose
            break
            
    assert good_pose is not None
    scene.robot_state.base_pose = good_pose
    scene.robot_state.current_base_pose_id = "base_good_1"
    
    instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")
    raw_plan = create_raw_plan(instruction, scene)
    skill_path = create_skill_path(raw_plan, scene)
    
    feasibility_result = check_reachability(skill_path, scene)
    
    # 좋은 base pose에서는 닿아야 함
    assert feasibility_result.feasible is True
    assert len(feasibility_result.issues) == 0


if __name__ == "__main__":
    test_symbolic_verifier()
    test_reachability_checker_bad_pose()
    test_reachability_checker_good_pose()
    print("verifier tests passed")

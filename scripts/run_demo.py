# scripts/run_demo.py

# 2026-05-02 신규: ScenePlan MVP의 전체 흐름을 보여주는 통합 데모 스크립트입니다.
import sys
from pathlib import Path

# 프로젝트 루트를 PATH에 추가
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.semantic_map.scene_loader import load_scene
from src.skills.skill_path_generator import create_skill_path
from src.verifier.symbolic_verifier import verify_symbolic_plan
from src.correction.symbolic_repair import repair_symbolic_plan
from src.verifier.reachability_checker import check_reachability
from src.correction.base_pose_repair import find_feasible_base_pose


def run_integrated_demo() -> None:
    print("=" * 60)
    print("🤖 ScenePlan MVP: Integrated Demo 🤖")
    print("=" * 60)

    # 1. Scene 로드
    scene_path = "data/scenes/scene_001.json"
    scene = load_scene(scene_path)
    print(f"\n[1] Scene Loaded: {scene.scene_id}")
    print(f"    - Places: {len(scene.places)}")
    print(f"    - Objects: {len(scene.objects)}")
    print(f"    - Current Base Pose ID: {scene.robot_state.current_base_pose_id}")

    # 2. Instruction 입력
    instruction_text = "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘."
    print(f"\n[2] Human Instruction:\n    > {instruction_text}")
    parsed_inst = parse_instruction(instruction_text)

    # 3. Raw Task Planning
    raw_plan = create_raw_plan(parsed_inst, scene)
    print("\n[3] Raw Task Plan Generated:")
    for step in raw_plan.steps:
        dest = f" -> {step.destination}" if step.destination else ""
        print(f"    {step.step_id}. {step.action} {step.target}{dest}")

    # 4. Symbolic Verification & Repair
    print("\n[4] Symbolic Verification...")
    val_result = verify_symbolic_plan(raw_plan, scene)
    current_plan = raw_plan

    if not val_result.valid:
        print("    ❌ Symbolic Issue Detected:")
        for issue in val_result.issues:
            print(f"       - {issue.reason}")
            print(f"       - Suggested Fix: {issue.suggested_fix}")
        
        print("\n    🔧 Applying Symbolic Repair...")
        current_plan = repair_symbolic_plan(raw_plan, val_result)
        print("    ✅ Repaired Task Plan:")
        for step in current_plan.steps:
            dest = f" -> {step.destination}" if step.destination else ""
            print(f"       {step.step_id}. {step.action} {step.target}{dest}")
    else:
        print("    ✅ Plan is symbolically valid.")

    # 5. Skill Path Candidate Generation
    print("\n[5] Skill Path Generation...")
    skill_path = create_skill_path(current_plan, scene)
    print(f"    - Path ID: {skill_path.path_id}")
    print(f"    - Base Pose: {skill_path.base_pose_id}")
    print(f"    - Waypoints count: {sum(len(step.waypoints) for step in skill_path.skills)}")

    # 6. Reachability Verification & Repair
    print("\n[6] Reachability Verification...")
    feas_result = check_reachability(skill_path, scene)
    
    if not feas_result.feasible:
        print("    ❌ Feasibility Issue Detected:")
        for issue in feas_result.issues:
            print(f"       - {issue.reason}")
            print(f"       - Suggested Fix: {issue.suggested_fix}")
            
        print("\n    🔧 Applying Base Pose Repair...")
        feasible_base_id = find_feasible_base_pose(skill_path, scene)
        if feasible_base_id:
            print(f"    ✅ Found feasible base pose: {feasible_base_id}")
            # 업데이트
            scene.robot_state.current_base_pose_id = feasible_base_id
            for candidate in scene.base_pose_candidates:
                if candidate.base_pose_id == feasible_base_id:
                    scene.robot_state.base_pose = candidate.pose
                    break
            
            # 다시 검증
            print("    - Re-checking reachability...")
            skill_path.base_pose_id = feasible_base_id
            new_feas_result = check_reachability(skill_path, scene)
            if new_feas_result.feasible:
                print("    ✅ Reachability Check Passed with new base pose!")
        else:
            print("    🚨 Could not find any feasible base pose in candidates.")
    else:
        print("    ✅ Path is geometrically feasible.")

    print("\n" + "=" * 60)
    print("✨ Demo Completed Successfully! ✨")
    print("=" * 60)


if __name__ == "__main__":
    run_integrated_demo()

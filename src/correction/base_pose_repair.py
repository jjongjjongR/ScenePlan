# src/correction/base_pose_repair.py

# 2026-05-02 신규: Reachability 검증 실패 시 대안이 될 Base Pose를 찾습니다.
import copy
from typing import Optional

from src.schemas.scene_schema import SemanticScene
from src.schemas.skill_path_schema import SkillPath
from src.verifier.reachability_checker import check_reachability


def find_feasible_base_pose(skill_path: SkillPath, scene: SemanticScene) -> Optional[str]:
    """
    scene에 정의된 base_pose_candidates를 순회하며
    skill_path를 실행 가능한(Reachability 통과) base pose id를 반환합니다.
    """
    original_base_pose = copy.deepcopy(scene.robot_state.base_pose)
    original_base_pose_id = scene.robot_state.current_base_pose_id

    feasible_id = None

    for candidate in scene.base_pose_candidates:
        # 로봇 상태를 후보 base pose로 임시 변경
        scene.robot_state.base_pose = candidate.pose
        scene.robot_state.current_base_pose_id = candidate.base_pose_id

        # 검증
        feasibility_result = check_reachability(skill_path, scene)

        if feasibility_result.feasible:
            feasible_id = candidate.base_pose_id
            break

    # 로봇 상태 원복
    scene.robot_state.base_pose = original_base_pose
    scene.robot_state.current_base_pose_id = original_base_pose_id

    return feasible_id

# src/verifier/reachability_checker.py

# 2026-05-02 신규: SkillPath Candidate가 현재 로봇 위치에서 기하학적으로 도달 가능한지(Reachability) 검증합니다.
import math
from typing import List

from src.schemas.scene_schema import SemanticScene
from src.schemas.skill_path_schema import SkillPath
from src.schemas.validation_schema import FeasibilityIssue, FeasibilityResult


def check_reachability(skill_path: SkillPath, scene: SemanticScene) -> FeasibilityResult:
    """
    로봇의 현재 base pose와 arm_reach_radius를 기준으로 waypoint 도달 가능성을 검사합니다.

    참고: MVP 용도로 단순 2D (x, y) Euclidean Distance를 기반으로 계산합니다.

    Args:
        skill_path: 검증할 SkillPath 객체
        scene: 로봇 상태와 장면 정보가 포함된 SemanticScene

    Returns:
        FeasibilityResult: 도달 가능 여부 및 실패 원인 정보
    """

    issues = []
    
    base_pose = scene.robot_state.base_pose
    arm_reach_radius = scene.robot_state.arm_reach_radius
    
    if base_pose is None or arm_reach_radius is None:
        return FeasibilityResult(
            feasible=False,
            issues=[
                FeasibilityIssue(
                    failure_type="missing_robot_state",
                    failed_step_id=-1,
                    waypoint_index=None,
                    reason="Robot base pose or arm_reach_radius is missing in the scene.",
                    suggested_fix=None,
                )
            ],
        )
    
    # base_pose: [x, y, theta]
    base_x, base_y = base_pose[0], base_pose[1]

    for step in skill_path.skills:
        for idx, waypoint in enumerate(step.waypoints):
            # waypoint position: [x, y, z]
            wp_x, wp_y = waypoint.position[0], waypoint.position[1]
            
            # 2D Euclidean distance
            distance = math.sqrt((wp_x - base_x) ** 2 + (wp_y - base_y) ** 2)
            
            if distance > arm_reach_radius:
                issues.append(
                    FeasibilityIssue(
                        failure_type="arm_reachability_failure",
                        failed_step_id=step.step_id,
                        waypoint_index=idx,
                        reason=f"Waypoint distance ({distance:.2f}) exceeds arm_reach_radius ({arm_reach_radius:.2f}).",
                        suggested_fix="Try a different base pose closer to the target.",
                    )
                )

    return FeasibilityResult(
        feasible=len(issues) == 0,
        issues=issues,
    )

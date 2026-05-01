# src/verifier/symbolic_verifier.py

# 2026-05-02 신규: TaskPlan이 현재 SemanticScene에서 기호적(Symbolic)으로 실행 가능한지 검증합니다.
from src.schemas.plan_schema import TaskPlan
from src.schemas.scene_schema import SemanticScene
from src.schemas.validation_schema import ValidationIssue, ValidationResult
from src.semantic_map.object_finder import find_object_by_id, find_place_by_id


def verify_symbolic_plan(plan: TaskPlan, scene: SemanticScene) -> ValidationResult:
    """
    작업 계획이 현재 장면에서 의미적으로 실행 가능한지 확인합니다.

    현재는 '닫힌 컨테이너 안에 있는 물체를 PICK 하려고 하는지'만 검사합니다.

    Args:
        plan: 검증할 TaskPlan
        scene: 현재 장면 데이터

    Returns:
        ValidationResult: 검증 결과 (valid 여부 및 이슈 목록)
    """

    issues = []

    for step in plan.steps:
        if step.action == "PICK":
            target_obj = find_object_by_id(scene, step.target)
            
            if target_obj is None:
                issues.append(
                    ValidationIssue(
                        failure_type="object_not_found",
                        failed_step_id=step.step_id,
                        reason=f"Target object '{step.target}' not found in the scene.",
                        suggested_fix=None,
                    )
                )
                continue

            if target_obj.location.startswith("inside:"):
                container_id = target_obj.location.split(":")[1]
                container = find_place_by_id(scene, container_id)

                if container is not None and container.state == "closed":
                    issues.append(
                        ValidationIssue(
                            failure_type="missing_precondition",
                            failed_step_id=step.step_id,
                            reason=f"{step.action} {step.target} cannot be executed because {step.target} is inside closed {container_id}.",
                            suggested_fix=f"OPEN {container_id} before PICK {step.target}",
                        )
                    )

    return ValidationResult(
        valid=len(issues) == 0,
        issues=issues,
    )

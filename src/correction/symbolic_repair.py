# src/correction/symbolic_repair.py

# 2026-05-02 신규: Symbolic 검증 실패 내역을 기반으로 초기 Task Plan을 수정합니다.
import copy

from src.schemas.plan_schema import PlanStep, TaskPlan
from src.schemas.validation_schema import ValidationResult


def repair_symbolic_plan(plan: TaskPlan, validation_result: ValidationResult) -> TaskPlan:
    """
    ValidationResult에서 발견된 이슈들을 분석하여 TaskPlan에 누락된 step을 삽입합니다.
    
    현재 MVP는 'missing_precondition' (닫힌 컨테이너에서 PICK 시도)에 대해
    해당 PICK step 직전에 OPEN step을 삽입하는 규칙만 지원합니다.
    """
    if validation_result.valid or not validation_result.issues:
        return plan

    repaired_plan = copy.deepcopy(plan)
    repaired_plan.plan_id = f"{plan.plan_id}_repaired"
    
    for issue in validation_result.issues:
        if issue.failure_type == "missing_precondition" and issue.suggested_fix:
            # suggested_fix 예시: "OPEN drawer_1 before PICK cup_red_1"
            if issue.suggested_fix.startswith("OPEN"):
                parts = issue.suggested_fix.split(" ")
                if len(parts) >= 2:
                    container_id = parts[1]
                    _insert_open_step(repaired_plan, issue.failed_step_id, container_id)

    # step_id 순차적 재정렬
    for i, step in enumerate(repaired_plan.steps):
        step.step_id = i + 1

    return repaired_plan


def _insert_open_step(plan: TaskPlan, failed_step_id: int, container_id: str) -> None:
    """failed_step_id 직전에 OPEN step을 삽입합니다."""
    insert_index = 0
    for i, step in enumerate(plan.steps):
        if step.step_id == failed_step_id:
            insert_index = i
            break
            
    new_step = PlanStep(
        step_id=-1,  # 임시 ID, 나중에 재정렬됨
        action="OPEN",
        target=container_id,
        destination=None,
    )
    
    plan.steps.insert(insert_index, new_step)

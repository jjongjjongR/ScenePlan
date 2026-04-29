# src/planner/rule_task_planner.py


# 2026-04-29 신규: ParsedInstruction과 SemanticScene을 바탕으로 raw task plan을 생성합니다.
from src.schemas.instruction_schema import ParsedInstruction
from src.schemas.plan_schema import PlanStep, TaskPlan
from src.schemas.scene_schema import SemanticScene
from src.semantic_map.object_finder import find_object_by_attributes, find_place_by_type


def create_raw_plan(
    instruction: ParsedInstruction,
    scene: SemanticScene,
) -> TaskPlan:
    """
    파싱된 명령과 semantic scene을 바탕으로 raw task plan을 생성합니다.

    중요한 설계:
    - 이 함수는 일부러 완벽한 plan을 만들지 않습니다.
    - target이 drawer 안에 있어도 OPEN step을 넣지 않습니다.
    - OPEN step 삽입은 verifier와 self-corrector 단계에서 처리합니다.

    Args:
        instruction: rule_parser가 만든 ParsedInstruction
        scene: scene_loader가 만든 SemanticScene

    Returns:
        TaskPlan 객체

    Raises:
        ValueError: target object나 destination을 찾지 못한 경우
    """

    target_object_id = _find_target_object_id(instruction, scene)

    if instruction.intent == "retrieve_and_place":
        destination_place_id = _find_destination_place_id(instruction, scene)

        return TaskPlan(
            plan_id="raw_plan_001",
            instruction=instruction.raw_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="PICK",
                    target=target_object_id,
                ),
                PlanStep(
                    step_id=2,
                    action="PLACE",
                    target=target_object_id,
                    destination=destination_place_id,
                ),
            ],
        )

    if instruction.intent == "retrieve":
        return TaskPlan(
            plan_id="raw_plan_001",
            instruction=instruction.raw_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="PICK",
                    target=target_object_id,
                )
            ],
        )

    raise ValueError(f"Unsupported instruction intent: {instruction.intent}")


def _find_target_object_id(
    instruction: ParsedInstruction,
    scene: SemanticScene,
) -> str:
    """
    ParsedInstruction의 target_category와 target_color를 이용해 scene 안의 target object를 찾습니다.
    """

    target_object = find_object_by_attributes(
        scene=scene,
        category=instruction.target_category,
        color=instruction.target_color,
    )

    if target_object is None:
        raise ValueError(
            "Target object not found. "
            f"category={instruction.target_category}, color={instruction.target_color}"
        )

    return target_object.object_id


def _find_destination_place_id(
    instruction: ParsedInstruction,
    scene: SemanticScene,
) -> str:
    """
    ParsedInstruction의 destination_type을 이용해 scene 안의 destination place를 찾습니다.
    """

    destination_place = find_place_by_type(
        scene=scene,
        place_type=instruction.destination_type,
    )

    if destination_place is None:
        raise ValueError(
            "Destination place not found. "
            f"destination_type={instruction.destination_type}"
        )

    return destination_place.place_id
# src/skills/skill_path_generator.py

# 2026-05-02 신규: TaskPlan을 SkillPath Candidate로 변환합니다.
from src.schemas.plan_schema import PlanStep, TaskPlan
from src.schemas.scene_schema import Place, SceneObject, SemanticScene
from src.schemas.skill_path_schema import SkillPath, SkillPathStep, Waypoint
from src.semantic_map.object_finder import find_object_by_id, find_place_by_id


def create_skill_path(
    plan: TaskPlan,
    scene: SemanticScene,
    path_id: str = "raw_skill_path_001",
) -> SkillPath:
    """
    TaskPlan을 SkillPath Candidate로 변환합니다.

    Args:
        plan: raw task plan 또는 corrected task plan
        scene: 3D field가 포함된 SemanticScene
        path_id: 생성할 skill path id

    Returns:
        SkillPath 객체

    Raises:
        ValueError: 필요한 target, destination, pose 정보가 없는 경우
    """

    base_pose_id = _get_current_base_pose_id(scene)

    skill_steps = []

    for step in plan.steps:
        skill_step = _create_skill_path_step(
            step=step,
            scene=scene,
        )
        skill_steps.append(skill_step)

    return SkillPath(
        path_id=path_id,
        plan_id=plan.plan_id,
        base_pose_id=base_pose_id,
        skills=skill_steps,
    )


def _get_current_base_pose_id(scene: SemanticScene) -> str:
    """
    scene의 현재 base pose id를 가져옵니다.
    없으면 base_current로 처리합니다.
    """

    if scene.robot_state.current_base_pose_id:
        return scene.robot_state.current_base_pose_id

    return "base_current"


def _create_skill_path_step(
    step: PlanStep,
    scene: SemanticScene,
) -> SkillPathStep:
    """
    PlanStep 하나를 SkillPathStep 하나로 변환합니다.
    """

    if step.action == "OPEN":
        return _create_open_skill_path_step(step, scene)

    if step.action == "PICK":
        return _create_pick_skill_path_step(step, scene)

    if step.action == "PLACE":
        return _create_place_skill_path_step(step, scene)

    raise ValueError(f"Unsupported action for skill path generation: {step.action}")


def _create_open_skill_path_step(
    step: PlanStep,
    scene: SemanticScene,
) -> SkillPathStep:
    """
    OPEN step을 handle_pose 기반 SkillPathStep으로 변환합니다.
    """

    target_place = find_place_by_id(scene, step.target)

    if target_place is None:
        raise ValueError(f"OPEN target place not found: {step.target}")

    if target_place.handle_pose is None:
        raise ValueError(f"OPEN target has no handle_pose: {step.target}")

    waypoint = _create_waypoint(
        position=target_place.handle_pose.position,
        orientation=target_place.handle_pose.orientation,
        description=f"Handle pose for {step.target}",
    )

    return SkillPathStep(
        step_id=step.step_id,
        action=step.action,
        target=step.target,
        destination=step.destination,
        waypoints=[waypoint],
    )


def _create_pick_skill_path_step(
    step: PlanStep,
    scene: SemanticScene,
) -> SkillPathStep:
    """
    PICK step을 grasp_pose 기반 SkillPathStep으로 변환합니다.
    """

    target_object = find_object_by_id(scene, step.target)

    if target_object is None:
        raise ValueError(f"PICK target object not found: {step.target}")

    if target_object.grasp_pose is None:
        raise ValueError(f"PICK target has no grasp_pose: {step.target}")

    waypoint = _create_waypoint(
        position=target_object.grasp_pose.position,
        orientation=target_object.grasp_pose.orientation,
        description=f"Grasp pose for {step.target}",
    )

    return SkillPathStep(
        step_id=step.step_id,
        action=step.action,
        target=step.target,
        destination=step.destination,
        waypoints=[waypoint],
    )


def _create_place_skill_path_step(
    step: PlanStep,
    scene: SemanticScene,
) -> SkillPathStep:
    """
    PLACE step을 destination의 place_pose 기반 SkillPathStep으로 변환합니다.
    """

    if step.destination is None:
        raise ValueError(f"PLACE step requires destination: step_id={step.step_id}")

    destination_place = find_place_by_id(scene, step.destination)

    if destination_place is None:
        raise ValueError(f"PLACE destination not found: {step.destination}")

    waypoint = _create_place_waypoint(
        destination_place=destination_place,
    )

    return SkillPathStep(
        step_id=step.step_id,
        action=step.action,
        target=step.target,
        destination=step.destination,
        waypoints=[waypoint],
    )


def _create_place_waypoint(destination_place: Place) -> Waypoint:
    """
    PLACE에 사용할 waypoint를 생성합니다.

    우선순위:
    1. place_pose가 있으면 사용
    2. place_pose가 없고 pose가 있으면 pose 사용
    3. 둘 다 없으면 에러
    """

    if destination_place.place_pose is not None:
        return _create_waypoint(
            position=destination_place.place_pose.position,
            orientation=destination_place.place_pose.orientation,
            description=f"Place pose for {destination_place.place_id}",
        )

    if destination_place.pose is not None:
        return _create_waypoint(
            position=destination_place.pose.position,
            orientation=destination_place.pose.orientation,
            description=f"Fallback place pose for {destination_place.place_id}",
        )

    raise ValueError(f"PLACE destination has no place_pose or pose: {destination_place.place_id}")


def _create_waypoint(
    position: list,
    orientation: list,
    description: str,
) -> Waypoint:
    """
    공통 Waypoint 객체를 생성합니다.
    """

    return Waypoint(
        index=0,
        position=position,
        orientation=orientation,
        description=description,
    )
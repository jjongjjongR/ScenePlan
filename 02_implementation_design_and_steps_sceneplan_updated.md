# 2부. 구현 설계와 단계별 개발 계획

# 0. 구현 목표

이 문서는 `ScenePlan` 프로젝트를 실제 코드로 구현하기 위한 상세 설계서다.

1차 목표는 기존 symbolic demo를 유지하면서, 2차 목표로 closed-container retrieval에서 base pose와 arm reachability가 결합되어 실패하는 skill path를 검출하는 구조를 추가하는 것이다.

---

# 1. MVP 데모 목표

## 1.1 Symbolic MVP

```text
입력:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

scene:
drawer_1 = closed
cup_red_1 = inside drawer_1
table_1 = reachable

raw plan:
PICK cup_red_1
PLACE cup_red_1 table_1

검증:
PICK 불가능. drawer가 닫혀 있어 cup이 visible/reachable하지 않음.

수정 plan:
OPEN drawer_1
PICK cup_red_1
PLACE cup_red_1 table_1

실행:
success
```

## 1.2 Geometric MVP

```text
수정 plan:
OPEN drawer_1
PICK cup_red_1
PLACE cup_red_1 table_1

추가 검증:
현재 base_pose에서 drawer handle과 cup grasp pose에 arm reachability가 충분한가?
OPEN/PICK 접근 waypoint가 drawer edge 또는 obstacle과 충돌하지 않는가?
gripper clearance가 충분한가?

결과:
feasible / infeasible
failure_type
bad_skill 또는 bad_waypoint
suggested_repair
```

---

# 2. 레포 구조

이미 레포 이름을 `ScenePlan`으로 만들었다면 유지한다.

```text
ScenePlan/
├── README.md
├── docs/
│   ├── project_overview.md
│   ├── system_architecture.md
│   ├── semantic_scene_map.md
│   ├── skill_library.md
│   ├── skill_path_schema.md
│   ├── feasibility_verification.md
│   ├── failure_taxonomy.md
│   └── evaluation_protocol.md
├── data/
│   ├── scenes/
│   │   └── scene_001.json
│   ├── skills/
│   │   └── basic_skills.json
│   ├── instructions/
│   │   └── demo_instructions.json
│   ├── paths/
│   │   ├── raw_skill_path_001.json
│   │   └── corrected_skill_path_001.json
│   ├── plans/
│   │   ├── raw_plan_001.json
│   │   └── corrected_plan_001.json
│   ├── memory/
│   │   └── failure_memory.jsonl
│   └── results/
│       └── demo_result_001.json
├── src/
│   ├── schemas/
│   │   ├── scene_schema.py
│   │   ├── geometry_schema.py
│   │   ├── instruction_schema.py
│   │   ├── plan_schema.py
│   │   ├── skill_schema.py
│   │   ├── skill_path_schema.py
│   │   ├── validation_schema.py
│   │   ├── execution_schema.py
│   │   └── memory_schema.py
│   ├── semantic_map/
│   │   ├── scene_loader.py
│   │   ├── object_finder.py
│   │   ├── relation_finder.py
│   │   └── state_tracker.py
│   ├── instruction/
│   │   └── rule_parser.py
│   ├── planner/
│   │   ├── rule_task_planner.py
│   │   └── plan_formatter.py
│   ├── skills/
│   │   ├── skill_loader.py
│   │   ├── skill_matcher.py
│   │   └── skill_path_generator.py
│   ├── verifier/
│   │   ├── precondition_checker.py
│   │   ├── relation_checker.py
│   │   ├── skill_checker.py
│   │   └── plan_validator.py
│   ├── feasibility/
│   │   ├── reachability_checker.py
│   │   ├── collision_checker.py
│   │   ├── clearance_checker.py
│   │   ├── orientation_checker.py
│   │   └── skill_path_verifier.py
│   ├── correction/
│   │   ├── self_corrector.py
│   │   ├── correction_rules.py
│   │   ├── local_path_repair.py
│   │   └── base_pose_repair.py
│   ├── execution/
│   │   ├── symbolic_executor.py
│   │   └── state_updater.py
│   ├── memory/
│   │   ├── failure_memory.py
│   │   └── memory_writer.py
│   ├── eval/
│   │   ├── metrics.py
│   │   └── result_reporter.py
│   └── utils/
│       ├── geometry.py
│       ├── io.py
│       └── logger.py
├── scripts/
│   ├── run_demo.py
│   ├── validate_plan.py
│   ├── validate_skill_path.py
│   └── run_symbolic_execution.py
└── tests/
    ├── test_scene_loader.py
    ├── test_rule_parser.py
    ├── test_rule_task_planner.py
    ├── test_plan_validator.py
    ├── test_skill_matcher.py
    ├── test_skill_path_verifier.py
    ├── test_symbolic_executor.py
    └── test_self_corrector.py
```

---

# 3. 데이터 파일 설계

# 3.1 `data/scenes/scene_001.json`

MVP scene은 기존 symbolic 정보에 3D field를 추가한다.

```json
{
  "scene_id": "scene_001",
  "description": "A tabletop scene with a closed drawer and a red cup inside it.",
  "places": [
    {
      "place_id": "table_1",
      "type": "table",
      "name": "table",
      "state": "clear",
      "visible": true,
      "reachable": true,
      "pose": {
        "position": [0.70, 0.00, 0.70],
        "orientation": [0, 0, 0, 1]
      },
      "bbox_3d": [0.70, 0.00, 0.70, 0.80, 0.60, 0.05]
    },
    {
      "place_id": "drawer_1",
      "type": "drawer",
      "name": "drawer",
      "state": "closed",
      "visible": true,
      "reachable": true,
      "pose": {
        "position": [0.50, 0.20, 0.65],
        "orientation": [0, 0, 0, 1]
      },
      "bbox_3d": [0.50, 0.20, 0.65, 0.40, 0.30, 0.25],
      "handle_pose": {
        "position": [0.50, 0.05, 0.68],
        "orientation": [0, 0, 0, 1]
      }
    }
  ],
  "objects": [
    {
      "object_id": "cup_red_1",
      "category": "cup",
      "name": "red cup",
      "color": "red",
      "location": "inside:drawer_1",
      "visible": false,
      "reachable": false,
      "graspable": true,
      "known_from": "instruction_or_memory",
      "pose": {
        "position": [0.50, 0.22, 0.64],
        "orientation": [0, 0, 0, 1]
      },
      "bbox_3d": [0.50, 0.22, 0.64, 0.07, 0.07, 0.10],
      "grasp_pose": {
        "position": [0.50, 0.22, 0.72],
        "orientation": [0, 0, 0, 1]
      }
    }
  ],
  "relations": [
    {
      "subject": "cup_red_1",
      "relation": "inside",
      "object": "drawer_1"
    }
  ],
  "robot_state": {
    "holding": null,
    "gripper_state": "open",
    "current_location": "table_area",
    "base_pose": [0.10, -0.40, 0.00],
    "arm_reach_radius": 0.65,
    "min_clearance": 0.03
  },
  "base_pose_candidates": [
    {
      "base_pose_id": "base_bad_1",
      "pose": [0.10, -0.40, 0.00],
      "description": "Current base pose. Too far from drawer handle."
    },
    {
      "base_pose_id": "base_good_1",
      "pose": [0.45, -0.20, 1.57],
      "description": "Better pose for opening drawer and grasping cup."
    }
  ]
}
```

중요한 점:

```text
닫힌 drawer 안의 cup pose는 실제 camera observation이 아니라 instruction/prior memory/simulation metadata에서 온 정보로 가정한다.
실제 3D vision은 container pose, handle pose, obstacle geometry, base pose, reachability 계산에 주로 사용한다.
OPEN 이후에는 object pose를 perception update로 갱신하는 구조로 확장한다.
```

---

# 4. Python 스키마 설계

# 4.1 `src/schemas/geometry_schema.py`

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pose3D:
    position: List[float]
    orientation: List[float]


@dataclass
class Box3D:
    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float


@dataclass
class BasePoseCandidate:
    base_pose_id: str
    pose: List[float]
    description: Optional[str] = None
```

# 4.2 `src/schemas/skill_path_schema.py`

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Waypoint:
    index: int
    position: List[float]
    orientation: List[float]
    description: Optional[str] = None


@dataclass
class SkillPathStep:
    step_id: int
    action: str
    target: str
    waypoints: List[Waypoint]


@dataclass
class SkillPath:
    path_id: str
    plan_id: str
    base_pose_id: str
    skills: List[SkillPathStep]
```

# 4.3 `src/schemas/validation_schema.py` 보완

```python
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ValidationIssue:
    failure_type: str
    failed_step_id: int
    reason: str
    suggested_fix: Optional[str]


@dataclass
class FeasibilityIssue:
    failure_type: str
    failed_step_id: int
    waypoint_index: Optional[int]
    reason: str
    suggested_fix: Optional[str]


@dataclass
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue]


@dataclass
class FeasibilityResult:
    feasible: bool
    issues: List[FeasibilityIssue]
```

---

# 5. 모듈별 구현 설계

# 5.1 기존 symbolic modules

기존 모듈은 유지한다.

```text
scene_loader.py
object_finder.py
relation_finder.py
rule_parser.py
rule_task_planner.py
plan_validator.py
self_corrector.py
symbolic_executor.py
failure_memory.py
```

# 5.2 `skills/skill_path_generator.py`

역할:

```text
corrected task plan과 scene 정보를 바탕으로 simplified skill path candidate를 생성한다.
```

필수 함수:

```python
def create_skill_path(plan: TaskPlan, scene: SemanticScene) -> SkillPath:
    ...
```

MVP 규칙:

```text
1. scene.robot_state.base_pose를 기본 base pose로 사용한다.
2. OPEN drawer_1의 waypoint는 drawer_1.handle_pose.position을 사용한다.
3. PICK cup_red_1의 waypoint는 cup_red_1.grasp_pose.position을 사용한다.
4. 실제 motion planning은 하지 않는다.
```

# 5.3 `feasibility/reachability_checker.py`

역할:

```text
base_pose에서 target waypoint까지의 거리를 계산해 simplified reachability를 판단한다.
```

필수 함수:

```python
def is_reachable_from_base(
    base_pose: list[float],
    target_position: list[float],
    reach_radius: float
) -> bool:
    ...
```

MVP 규칙:

```text
base_pose의 x, y와 target_position의 x, y 거리만 계산한다.
거리 <= arm_reach_radius이면 reachable=true로 본다.
```

# 5.4 `feasibility/skill_path_verifier.py`

역할:

```text
SkillPath 전체가 현재 scene에서 실행 가능한지 검증한다.
```

필수 함수:

```python
def verify_skill_path(
    skill_path: SkillPath,
    scene: SemanticScene
) -> FeasibilityResult:
    ...
```

검증 항목:

```text
1. base_pose가 존재하는가
2. 각 waypoint가 base_pose 기준 reach_radius 안에 있는가
3. 각 waypoint가 container/obstacle bbox와 충돌하지 않는가
4. clearance 조건을 만족하는가
```

# 5.5 `correction/base_pose_repair.py`

역할:

```text
reachability failure가 발생했을 때 더 나은 base pose candidate를 선택한다.
```

필수 함수:

```python
def suggest_better_base_pose(
    scene: SemanticScene,
    failed_target_position: list[float]
) -> str | None:
    ...
```

MVP 규칙:

```text
base_pose_candidates 중 target_position에 가장 가까운 candidate를 선택한다.
candidate가 reach_radius 안에 들어오면 suggested_fix로 반환한다.
```

---

# 6. 단계별 개발 계획

# Phase 0. 기존 MVP 유지

목표:

```text
기존 symbolic demo가 깨지지 않게 유지한다.
```

완료 기준:

```text
python scripts/run_demo.py 실행 시 기존 OPEN 삽입 demo가 성공한다.
```

# Phase 1. 3D field 추가

목표:

```text
scene_001.json에 pose, bbox_3d, handle_pose, base_pose, arm_reach_radius를 추가한다.
```

완료 기준:

```text
기존 scene_loader가 새 필드를 읽을 수 있다.
추가 필드가 없어도 기존 symbolic pipeline은 동작한다.
```

# Phase 2. Skill Path Schema 추가

목표:

```text
TaskPlan 아래에 SkillPath를 표현할 수 있게 한다.
```

완료 기준:

```text
corrected_plan_001에서 raw_skill_path_001을 생성할 수 있다.
```

# Phase 3. Reachability Checker 구현

목표:

```text
현재 base_pose에서 drawer handle과 cup grasp pose가 reachable한지 검사한다.
```

완료 기준:

```text
base_bad_1은 infeasible로 판정된다.
base_good_1은 feasible로 판정된다.
```

# Phase 4. Collision / Clearance Checker 구현

목표:

```text
waypoint가 drawer/container bbox와 너무 가까운지 검사한다.
```

완료 기준:

```text
충돌 위험 waypoint에 대해 collision_risk issue가 생성된다.
```

# Phase 5. Base Pose Repair 구현

목표:

```text
reachability failure가 발생하면 더 나은 base pose candidate를 제안한다.
```

완료 기준:

```text
base_bad_1 사용 시 suggested_fix = base_good_1이 출력된다.
```

# Phase 6. 통합 데모

목표:

```text
symbolic validation + geometric feasibility verification이 한 번에 실행된다.
```

콘솔 출력에 포함될 것:

```text
[Instruction]
[Parsed Instruction]
[Raw Plan]
[Symbolic Validation Result]
[Corrected Plan]
[Raw Skill Path]
[Feasibility Result]
[Suggested Repair]
[Final Result]
```

---

# 7. 현재 한계

아래 한계는 보고서에 반드시 적는다.

```text
1. 현재 semantic/3D scene은 실제 perception에서 생성된 것이 아니라 수동 JSON이다.
2. 닫힌 container 내부 object pose는 실제 vision으로 관측한 것이 아니라 instruction/prior memory/simulation metadata로 가정한다.
3. 현재 reachability는 단순 거리 기반 proxy이며 실제 inverse kinematics가 아니다.
4. 현재 collision check는 bbox와 threshold 기반 proxy이며 실제 collision checker가 아니다.
5. 현재 local repair는 규칙 기반이며 trajectory optimization이 아니다.
6. 현재 executor는 실제 물리 시뮬레이션이 아니라 symbolic state update다.
7. Isaac Sim, ROS2, MoveIt, cuRobo 연동은 후속 단계다.
```

---

# 8. 최종 완료 기준

```text
1. 기존 symbolic demo가 성공한다.
2. scene_001.json에 3D field가 포함된다.
3. corrected plan에서 skill path candidate를 생성한다.
4. base_bad_1에서 reachability failure를 탐지한다.
5. base_good_1을 suggested repair로 제안한다.
6. failure_memory.jsonl에 symbolic/geometric failure가 저장된다.
7. tests가 최소 7개 이상 통과한다.
8. demo_report.md를 작성할 수 있을 정도의 결과가 남는다.
```

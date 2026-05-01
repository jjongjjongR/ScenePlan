# 2부. 구현 설계와 단계별 개발 계획 — MVP 기준

## 0. 구현 목표

이 문서는 ScenePlan MVP를 실제 코드로 마무리하기 위한 최소 구현 계획서다.

목표는 전체 로봇 시스템을 만드는 것이 아니라, 다음 흐름을 하나의 데모로 보여주는 것이다.

```text
Instruction
→ Scene JSON
→ Raw Task Plan
→ Skill Path Candidate
→ Symbolic + Reachability Check
→ Repair Suggestion
→ Demo Output
```

---

## 1. MVP 데모 목표

입력:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

기대 출력:

```text
[Raw Task Plan]
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

[Symbolic Issue]
PICK cannot be executed because cup_red_1 is inside closed drawer_1.
Suggested repair: OPEN drawer_1 before PICK cup_red_1.

[Skill Path Candidate]
base_pose = base_bad_1
PICK waypoint = cup_red_1.grasp_pose
PLACE waypoint = table_1.place_pose

[Reachability Result]
feasible = false
failure_type = arm_reachability_failure

[Suggested Repair]
Use base_good_1.
```

---

## 2. MVP 레포 구조

MVP에서 필요한 최소 구조는 다음과 같다.

```text
ScenePlan/
├── README.md
├── data/
│   ├── scenes/
│   │   └── scene_001.json
│   ├── skills/
│   │   └── basic_skills.json
│   ├── instructions/
│   │   └── demo_instructions.json
│   └── memory/
│       └── failure_memory.jsonl
├── src/
│   ├── schemas/
│   │   ├── scene_schema.py
│   │   ├── instruction_schema.py
│   │   ├── plan_schema.py
│   │   ├── skill_schema.py
│   │   ├── geometry_schema.py
│   │   ├── skill_path_schema.py
│   │   └── validation_schema.py
│   ├── semantic_map/
│   │   ├── scene_loader.py
│   │   ├── object_finder.py
│   │   └── relation_finder.py
│   ├── instruction/
│   │   └── rule_parser.py
│   ├── planner/
│   │   └── rule_task_planner.py
│   ├── skills/
│   │   └── skill_path_generator.py
│   ├── feasibility/
│   │   ├── reachability_checker.py
│   │   └── simple_feasibility_verifier.py
│   ├── correction/
│   │   └── base_pose_repair.py
│   └── utils/
│       └── io.py
├── scripts/
│   └── run_demo.py
└── tests/
    ├── test_rule_parser.py
    ├── test_rule_task_planner.py
    ├── test_skill_path_generator.py
    └── test_reachability_checker.py
```

---

## 3. 현재 완료된 구현

```text
완료:
- 프로젝트 기본 구조
- scene_001.json / basic_skills.json / demo_instructions.json
- scene / instruction / plan / skill / validation schema
- scene_loader.py
- object_finder.py
- relation_finder.py
- rule_parser.py
- rule_task_planner.py
```

---

## 4. 남은 MVP 구현 단계

| Phase | 단계 | 목표 | 완료 기준 |
|---|---|---|---|
| Phase 6 | 3D Scene Extension | scene_001.json에 pose, bbox, grasp_pose, base_pose 추가 | 기존 parser/planner 테스트가 깨지지 않음 |
| Phase 7 | Geometry / Skill Path Schema | waypoint와 skill path 구조 추가 | schema import 성공 |
| Phase 8 | Skill Path Generator | task plan을 waypoint 후보로 변환 | PICK/PLACE waypoint 생성 |
| Phase 9 | Simple Feasibility Verifier | symbolic issue와 reachability failure 탐지 | base_bad_1 infeasible 출력 |
| Phase 10 | Base Pose Repair | reachability failure 시 base_good_1 제안 | suggested_fix 출력 |
| Phase 11 | Integrated Demo | 전체 MVP 흐름 실행 | run_demo.py 출력 성공 |

---

## 5. 데이터 설계

### 5.1 `scene_001.json` 추가 필드

기존 symbolic field는 유지하고, 아래 3D field만 추가한다.

```text
place:
- pose
- bbox_3d
- handle_pose
- place_pose

object:
- known_from
- pose
- bbox_3d
- grasp_pose

robot_state:
- base_pose
- current_base_pose_id
- arm_reach_radius
- min_clearance

scene:
- base_pose_candidates
```

중요한 전제:

```text
cup_red_1은 닫힌 drawer 안에 있으므로 현재 camera observation으로 본 것이 아니다.
known_from = instruction_or_memory 로 표시한다.
```

---

## 6. 새로 추가할 schema

### 6.1 `src/schemas/geometry_schema.py`

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pose3D:
    position: List[float]
    orientation: List[float]


@dataclass
class BasePoseCandidate:
    base_pose_id: str
    pose: List[float]
    description: Optional[str] = None
```

### 6.2 `src/schemas/skill_path_schema.py`

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
    destination: Optional[str]
    waypoints: List[Waypoint]


@dataclass
class SkillPath:
    path_id: str
    plan_id: str
    base_pose_id: str
    skills: List[SkillPathStep]
```

---

## 7. 새로 구현할 모듈

### 7.1 `skills/skill_path_generator.py`

역할:

```text
TaskPlan의 각 step에 scene의 waypoint 후보를 연결한다.
```

MVP 규칙:

```text
PICK object → object.grasp_pose
PLACE object destination → destination.place_pose
OPEN drawer → drawer.handle_pose
```

### 7.2 `feasibility/reachability_checker.py`

역할:

```text
base_pose와 waypoint 사이의 2D 거리를 계산한다.
```

MVP 규칙:

```text
distance(base_xy, waypoint_xy) <= arm_reach_radius → reachable
otherwise → unreachable
```

### 7.3 `feasibility/simple_feasibility_verifier.py`

역할:

```text
MVP용 symbolic issue와 reachability issue를 한 번에 확인한다.
```

검증 항목:

```text
1. target이 closed drawer 안에 있는데 바로 PICK하려는가?
2. base_pose에서 waypoint까지 arm_reach_radius 안에 있는가?
```

### 7.4 `correction/base_pose_repair.py`

역할:

```text
reachability failure가 발생하면 base_pose_candidates 중 더 나은 후보를 제안한다.
```

MVP 규칙:

```text
base_good_1이 failed waypoint를 reach_radius 안에 포함하면 suggested_fix로 반환한다.
```

---

## 8. `scripts/run_demo.py` 출력 형식

```text
[Instruction]
...

[Parsed Instruction]
...

[Raw Task Plan]
...

[Symbolic Issue]
...

[Skill Path Candidate]
...

[Reachability Result]
...

[Suggested Repair]
...

[MVP Result]
ScenePlan generated a raw task plan, detected a symbolic/geometric feasibility issue, and suggested a local repair.
```

---

## 9. 테스트 기준

MVP에서 최소로 통과해야 하는 테스트:

```text
1. test_rule_parser.py
2. test_rule_task_planner.py
3. test_skill_path_generator.py
4. test_reachability_checker.py
```

선택 테스트:

```text
5. test_simple_feasibility_verifier.py
6. test_base_pose_repair.py
```

---

## 10. MVP 최종 완료 기준

```text
1. scene_001.json에 3D field가 포함된다.
2. 기존 raw task planner가 깨지지 않는다.
3. skill path candidate가 생성된다.
4. base_bad_1에서 reachability failure가 검출된다.
5. base_good_1이 suggested repair로 출력된다.
6. scripts/run_demo.py가 전체 흐름을 출력한다.
7. README가 MVP 기준으로 정리되어 있다.
```

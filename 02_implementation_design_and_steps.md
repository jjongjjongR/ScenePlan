# 2부. 구현 설계와 단계별 개발 계획

# 0. 구현 목표

이 문서는 `Semantic Map-Guided Task Planning and Verification for Language-Guided Robot Manipulation` 프로젝트를 실제 코드로 구현하기 위한 상세 설계서다.

1차 목표는 아래 데모를 끝까지 동작시키는 것이다.

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

---

# 1. 레포 구조

아래 구조로 시작한다.

```text
semantic_robot_planner/
├── README.md
├── docs/
│   ├── project_overview.md
│   ├── system_architecture.md
│   ├── semantic_scene_map.md
│   ├── skill_library.md
│   ├── failure_taxonomy.md
│   └── evaluation_protocol.md
├── data/
│   ├── scenes/
│   │   └── scene_001.json
│   ├── skills/
│   │   └── basic_skills.json
│   ├── instructions/
│   │   └── demo_instructions.json
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
│   │   ├── instruction_schema.py
│   │   ├── plan_schema.py
│   │   ├── skill_schema.py
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
│   ├── verifier/
│   │   ├── precondition_checker.py
│   │   ├── relation_checker.py
│   │   ├── skill_checker.py
│   │   └── plan_validator.py
│   ├── skills/
│   │   ├── skill_loader.py
│   │   └── skill_matcher.py
│   ├── execution/
│   │   ├── symbolic_executor.py
│   │   └── state_updater.py
│   ├── correction/
│   │   ├── self_corrector.py
│   │   └── correction_rules.py
│   ├── memory/
│   │   ├── failure_memory.py
│   │   └── memory_writer.py
│   ├── eval/
│   │   ├── metrics.py
│   │   └── result_reporter.py
│   └── utils/
│       ├── io.py
│       └── logger.py
├── scripts/
│   ├── run_demo.py
│   ├── validate_plan.py
│   └── run_symbolic_execution.py
└── tests/
    ├── test_scene_loader.py
    ├── test_rule_parser.py
    ├── test_rule_task_planner.py
    ├── test_plan_validator.py
    ├── test_skill_matcher.py
    ├── test_symbolic_executor.py
    └── test_self_corrector.py
```

---

# 2. 데이터 파일 설계

# 2.1 `data/scenes/scene_001.json`

MVP scene은 아래 하나로 시작한다.

```json
{
  "scene_id": "scene_001",
  "description": "A simple tabletop scene with a closed drawer and a red cup inside it.",
  "places": [
    {
      "place_id": "table_1",
      "type": "table",
      "name": "table",
      "state": "clear",
      "visible": true,
      "reachable": true
    },
    {
      "place_id": "drawer_1",
      "type": "drawer",
      "name": "drawer",
      "state": "closed",
      "visible": true,
      "reachable": true
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
      "graspable": true
    },
    {
      "object_id": "cup_blue_1",
      "category": "cup",
      "name": "blue cup",
      "color": "blue",
      "location": "on:table_1",
      "visible": true,
      "reachable": true,
      "graspable": true
    }
  ],
  "relations": [
    {
      "subject": "cup_red_1",
      "relation": "inside",
      "object": "drawer_1"
    },
    {
      "subject": "cup_blue_1",
      "relation": "on",
      "object": "table_1"
    },
    {
      "subject": "drawer_1",
      "relation": "near",
      "object": "table_1"
    }
  ],
  "robot_state": {
    "holding": null,
    "gripper_state": "open",
    "current_location": "table_area"
  }
}
```

---

# 2.2 `data/skills/basic_skills.json`

```json
{
  "skills": [
    {
      "skill_id": "open_drawer_skill",
      "action": "OPEN",
      "description": "Open a reachable closed drawer.",
      "target_type": "drawer",
      "required_conditions": [
        "target.type == drawer",
        "target.state == closed",
        "target.reachable == true"
      ],
      "effects": [
        "target.state = open",
        "objects_inside_target.visible = true",
        "objects_inside_target.reachable = true"
      ]
    },
    {
      "skill_id": "grasp_object_skill",
      "action": "PICK",
      "description": "Pick a visible, reachable, and graspable object.",
      "target_type": "object",
      "required_conditions": [
        "target.visible == true",
        "target.reachable == true",
        "target.graspable == true",
        "robot.holding == null"
      ],
      "effects": [
        "robot.holding = target.object_id",
        "target.location = held_by:robot"
      ]
    },
    {
      "skill_id": "place_object_skill",
      "action": "PLACE",
      "description": "Place the held object on a reachable destination.",
      "target_type": "object",
      "required_conditions": [
        "robot.holding == target.object_id",
        "destination.reachable == true"
      ],
      "effects": [
        "robot.holding = null",
        "target.location = on:destination.place_id"
      ]
    }
  ]
}
```

---

# 2.3 `data/instructions/demo_instructions.json`

```json
{
  "instructions": [
    {
      "instruction_id": "inst_001",
      "text": "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.",
      "expected_intent": "retrieve_and_place",
      "expected_target": "cup_red_1",
      "expected_destination": "table_1"
    }
  ]
}
```

---

# 3. Python 스키마 설계

처음에는 `dataclass`를 사용한다.  
나중에 안정화되면 Pydantic으로 교체해도 된다.

# 3.1 `src/schemas/scene_schema.py`

필요한 클래스:

```python
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Place:
    place_id: str
    type: str
    name: str
    state: Optional[str]
    visible: bool
    reachable: bool


@dataclass
class SceneObject:
    object_id: str
    category: str
    name: str
    color: Optional[str]
    location: str
    visible: bool
    reachable: bool
    graspable: bool


@dataclass
class Relation:
    subject: str
    relation: str
    object: str


@dataclass
class RobotState:
    holding: Optional[str]
    gripper_state: str
    current_location: str


@dataclass
class SemanticScene:
    scene_id: str
    description: str
    places: List[Place]
    objects: List[SceneObject]
    relations: List[Relation]
    robot_state: RobotState
```

---

# 3.2 `src/schemas/instruction_schema.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedInstruction:
    raw_text: str
    intent: str
    target_category: Optional[str]
    target_color: Optional[str]
    source_relation: Optional[str]
    source_place_type: Optional[str]
    destination_type: Optional[str]
```

예시 출력:

```json
{
  "raw_text": "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.",
  "intent": "retrieve_and_place",
  "target_category": "cup",
  "target_color": "red",
  "source_relation": "inside",
  "source_place_type": "drawer",
  "destination_type": "table"
}
```

---

# 3.3 `src/schemas/plan_schema.py`

```python
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PlanStep:
    step_id: int
    action: str
    target: str
    destination: Optional[str] = None


@dataclass
class TaskPlan:
    plan_id: str
    instruction: str
    steps: List[PlanStep]
```

---

# 3.4 `src/schemas/validation_schema.py`

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
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue]
```

---

# 3.5 `src/schemas/execution_schema.py`

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class StepExecutionResult:
    step_id: int
    action: str
    success: bool
    reason: Optional[str]


@dataclass
class ExecutionResult:
    success: bool
    step_results: List[StepExecutionResult]
    final_state: Dict[str, Any]
```

---

# 4. 모듈별 구현 설계

# 4.1 `semantic_map/scene_loader.py`

역할:

```text
scene_001.json을 읽어 SemanticScene 객체로 변환한다.
```

필수 함수:

```python
def load_scene(path: str) -> SemanticScene:
    ...
```

완료 기준:

```text
- JSON 파일을 읽는다.
- places, objects, relations, robot_state를 dataclass로 변환한다.
- scene_id가 비어 있으면 에러를 낸다.
- objects가 비어 있으면 에러를 낸다.
```

---

# 4.2 `semantic_map/object_finder.py`

역할:

```text
ParsedInstruction을 바탕으로 scene 안에서 target object를 찾는다.
```

필수 함수:

```python
def find_object_by_attributes(
    scene: SemanticScene,
    category: str | None,
    color: str | None
) -> SceneObject | None:
    ...
```

탐색 기준:

```text
1. category가 일치해야 한다.
2. color가 있으면 color도 일치해야 한다.
3. 후보가 여러 개면 visible=true인 것을 우선한다.
4. 그래도 여러 개면 첫 번째 후보를 반환한다.
5. 없으면 None을 반환한다.
```

---

# 4.3 `semantic_map/relation_finder.py`

역할:

```text
object와 place 사이 관계를 찾는다.
```

필수 함수:

```python
def find_relation(scene: SemanticScene, subject_id: str, relation: str) -> Relation | None:
    ...

def get_container_of_object(scene: SemanticScene, object_id: str) -> str | None:
    ...
```

예시:

```text
cup_red_1 is inside drawer_1
→ get_container_of_object(scene, "cup_red_1") == "drawer_1"
```

---

# 4.4 `instruction/rule_parser.py`

역할:

```text
한국어 instruction을 단순 규칙으로 파싱한다.
```

MVP 규칙:

```text
- "빨간" 포함 → target_color = red
- "파란" 포함 → target_color = blue
- "컵" 포함 → target_category = cup
- "그릇" 포함 → target_category = bowl
- "서랍 안" 포함 → source_relation = inside, source_place_type = drawer
- "테이블 위" 포함 → destination_type = table
- "올려" 또는 "놓아" 포함 → intent = retrieve_and_place
- "집어" 또는 "꺼내" 포함 → intent = retrieve
```

필수 함수:

```python
def parse_instruction(text: str) -> ParsedInstruction:
    ...
```

주의:

```text
처음부터 완벽한 자연어 처리를 하지 않는다.
명령 3~5개만 안정적으로 처리한다.
```

---

# 4.5 `planner/rule_task_planner.py`

역할:

```text
ParsedInstruction과 SemanticScene을 바탕으로 raw task plan을 만든다.
```

MVP에서는 일부러 틀린 raw plan을 생성한다.  
그래야 verifier와 corrector의 역할이 드러난다.

예시:

```text
instruction:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

raw plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

필수 함수:

```python
def create_raw_plan(
    instruction: ParsedInstruction,
    scene: SemanticScene
) -> TaskPlan:
    ...
```

생성 규칙:

```text
1. target object를 찾는다.
2. destination place를 찾는다.
3. intent가 retrieve_and_place이면 PICK → PLACE plan을 만든다.
4. source가 drawer inside여도 처음에는 OPEN을 넣지 않는다.
5. OPEN은 self_corrector가 삽입하게 한다.
```

이 설계가 중요한 이유:

```text
raw planner는 일부러 단순하게 둔다.
verifier와 self-corrector가 문제를 찾고 고치는지 보여주기 위함이다.
```

---

# 4.6 `verifier/plan_validator.py`

역할:

```text
TaskPlan이 현재 scene과 skill 조건에서 실행 가능한지 검증한다.
```

필수 함수:

```python
def validate_plan(
    plan: TaskPlan,
    scene: SemanticScene
) -> ValidationResult:
    ...
```

검증 로직:

```text
각 step을 순서대로 확인한다.

OPEN:
- target이 place에 존재해야 한다.
- target.type == drawer 여야 한다.
- target.state == closed 여야 한다.
- target.reachable == true 여야 한다.

PICK:
- target object가 존재해야 한다.
- target.visible == true 여야 한다.
- target.reachable == true 여야 한다.
- target.graspable == true 여야 한다.
- robot.holding == null 이어야 한다.
- target이 inside 관계에 있고 container가 closed면 실패 처리한다.

PLACE:
- target object가 존재해야 한다.
- destination이 존재해야 한다.
- robot.holding == target.object_id 이어야 한다.
- destination.reachable == true 여야 한다.
```

중요:

```text
validate_plan은 실제 state를 변경하지 않는다.
state 변경은 symbolic_executor가 담당한다.
```

---

# 4.7 `correction/self_corrector.py`

역할:

```text
ValidationResult의 failure_type을 보고 plan을 수정한다.
```

필수 함수:

```python
def correct_plan(
    plan: TaskPlan,
    scene: SemanticScene,
    validation_result: ValidationResult
) -> TaskPlan:
    ...
```

1차 correction rule:

```text
failure_type = missing_precondition
reason에 "inside"와 "closed"가 포함됨
→ PICK step 이전에 OPEN container step 삽입
```

예시:

```text
기존:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

수정:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

주의:

```text
수정 후 step_id를 1부터 다시 매긴다.
동일한 OPEN step이 이미 있으면 중복 삽입하지 않는다.
```

---

# 4.8 `execution/symbolic_executor.py`

역할:

```text
corrected plan을 실제로 실행하는 것처럼 scene state를 업데이트한다.
```

필수 함수:

```python
def execute_plan(
    plan: TaskPlan,
    scene: SemanticScene
) -> ExecutionResult:
    ...
```

실행 로직:

```text
OPEN drawer_1:
- drawer_1.state = open
- drawer_1 안에 있는 object들의 visible = true
- drawer_1 안에 있는 object들의 reachable = true

PICK cup_red_1:
- robot.holding = cup_red_1
- cup_red_1.location = held_by:robot

PLACE cup_red_1 table_1:
- robot.holding = null
- cup_red_1.location = on:table_1
- cup_red_1.visible = true
- cup_red_1.reachable = true
```

주의:

```text
executor는 실행 전 각 step 조건을 한 번 더 확인한다.
실패하면 그 지점에서 중단하고 ExecutionResult.success=false를 반환한다.
```

---

# 4.9 `memory/failure_memory.py`

역할:

```text
실패 사례를 JSONL로 저장한다.
```

필수 함수:

```python
def write_failure_memory(
    path: str,
    instruction_text: str,
    failure_type: str,
    bad_plan: TaskPlan,
    corrected_plan: TaskPlan,
    lesson: str
) -> None:
    ...
```

저장 예시:

```json
{
  "memory_id": "fail_001",
  "instruction_text": "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.",
  "failure_type": "missing_precondition",
  "bad_plan": ["PICK cup_red_1", "PLACE cup_red_1 table_1"],
  "corrected_plan": ["OPEN drawer_1", "PICK cup_red_1", "PLACE cup_red_1 table_1"],
  "lesson": "If target object is inside a closed drawer, open the drawer before picking."
}
```

---

# 4.10 `scripts/run_demo.py`

역할:

```text
MVP 전체 흐름을 한 번에 실행한다.
```

흐름:

```text
1. scene_001.json 로드
2. instruction 입력
3. rule_parser로 instruction 파싱
4. raw planner로 raw plan 생성
5. validator로 raw plan 검증
6. invalid이면 self_corrector로 plan 수정
7. corrected plan 다시 검증
8. symbolic_executor로 corrected plan 실행
9. failure_memory 저장
10. 결과 출력
```

콘솔 출력 예시:

```text
[Instruction]
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

[Parsed Instruction]
intent = retrieve_and_place
target = red cup
source = inside drawer
destination = table

[Raw Plan]
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

[Validation Result]
valid = false
failure_type = missing_precondition
reason = cup_red_1 is inside drawer_1, but drawer_1 is closed.

[Corrected Plan]
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1

[Execution Result]
success = true
final_state:
- drawer_1.state = open
- cup_red_1.location = on:table_1
- robot.holding = null
```

---

# 5. 단계별 개발 계획

# Phase 0. 프로젝트 초기화

## 목표

폴더 구조와 기본 문서를 만든다.

## 할 일

```text
1. semantic_robot_planner 폴더 생성
2. README.md 생성
3. docs 폴더 생성
4. data 폴더 생성
5. src 폴더 생성
6. scripts 폴더 생성
7. tests 폴더 생성
```

## 완료 기준

```text
tree 구조가 설계와 동일해야 한다.
README.md에 프로젝트 한 줄 정의가 있어야 한다.
```

---

# Phase 1. 데이터 파일 생성

## 목표

MVP에 필요한 scene, skill, instruction JSON을 만든다.

## 생성 파일

```text
data/scenes/scene_001.json
data/skills/basic_skills.json
data/instructions/demo_instructions.json
data/memory/failure_memory.jsonl
```

## 완료 기준

```text
scene_001.json에 table_1, drawer_1, cup_red_1, cup_blue_1이 있어야 한다.
cup_red_1은 inside:drawer_1이어야 한다.
drawer_1은 closed여야 한다.
cup_red_1은 visible=false, reachable=false여야 한다.
```

---

# Phase 2. Schema 구현

## 목표

프로젝트 전체에서 사용할 dataclass를 만든다.

## 구현 파일

```text
src/schemas/scene_schema.py
src/schemas/instruction_schema.py
src/schemas/plan_schema.py
src/schemas/validation_schema.py
src/schemas/execution_schema.py
src/schemas/memory_schema.py
```

## 완료 기준

```text
각 schema가 import 가능해야 한다.
dataclass 필드명이 JSON 키와 일관되어야 한다.
```

---

# Phase 3. Scene Loader 구현

## 목표

scene JSON을 Python 객체로 변환한다.

## 구현 파일

```text
src/semantic_map/scene_loader.py
src/semantic_map/object_finder.py
src/semantic_map/relation_finder.py
```

## 테스트

```text
tests/test_scene_loader.py
```

## 완료 기준

```text
load_scene("data/scenes/scene_001.json") 실행 시 SemanticScene이 반환되어야 한다.
cup_red_1을 object_id로 찾을 수 있어야 한다.
cup_red_1의 container가 drawer_1임을 찾을 수 있어야 한다.
```

---

# Phase 4. Instruction Parser 구현

## 목표

한국어 명령을 ParsedInstruction으로 변환한다.

## 구현 파일

```text
src/instruction/rule_parser.py
```

## 테스트

```text
tests/test_rule_parser.py
```

## 완료 기준

아래 입력을 파싱할 수 있어야 한다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

기대 결과:

```text
intent = retrieve_and_place
target_category = cup
target_color = red
source_relation = inside
source_place_type = drawer
destination_type = table
```

---

# Phase 5. Raw Task Planner 구현

## 목표

ParsedInstruction과 scene을 기반으로 raw plan을 생성한다.

## 구현 파일

```text
src/planner/rule_task_planner.py
```

## 테스트

```text
tests/test_rule_task_planner.py
```

## 완료 기준

입력:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

출력:

```text
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

중요:

```text
여기서 OPEN drawer_1을 넣으면 안 된다.
OPEN 삽입은 self_corrector가 담당한다.
```

---

# Phase 6. Plan Validator 구현

## 목표

raw plan의 문제를 탐지한다.

## 구현 파일

```text
src/verifier/plan_validator.py
src/verifier/precondition_checker.py
src/verifier/relation_checker.py
```

## 테스트

```text
tests/test_plan_validator.py
```

## 완료 기준

raw plan을 검증했을 때 아래 결과가 나와야 한다.

```text
valid = false
failure_type = missing_precondition
reason에 drawer_1 closed 또는 cup_red_1 inside drawer_1 정보가 포함되어야 한다.
suggested_fix에 OPEN drawer_1 삽입 제안이 있어야 한다.
```

---

# Phase 7. Self-Corrector 구현

## 목표

검증 실패 결과를 바탕으로 corrected plan을 만든다.

## 구현 파일

```text
src/correction/self_corrector.py
src/correction/correction_rules.py
```

## 테스트

```text
tests/test_self_corrector.py
```

## 완료 기준

입력 raw plan:

```text
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

출력 corrected plan:

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

---

# Phase 8. Skill Matcher 구현

## 목표

task action을 skill과 연결한다.

## 구현 파일

```text
src/skills/skill_loader.py
src/skills/skill_matcher.py
```

## 테스트

```text
tests/test_skill_matcher.py
```

## 완료 기준

```text
OPEN → open_drawer_skill
PICK → grasp_object_skill
PLACE → place_object_skill
```

매핑이 가능해야 한다.

---

# Phase 9. Symbolic Executor 구현

## 목표

corrected plan을 실행하고 scene state를 업데이트한다.

## 구현 파일

```text
src/execution/symbolic_executor.py
src/execution/state_updater.py
```

## 테스트

```text
tests/test_symbolic_executor.py
```

## 완료 기준

corrected plan 실행 후 최종 상태:

```text
drawer_1.state = open
cup_red_1.location = on:table_1
cup_red_1.visible = true
cup_red_1.reachable = true
robot.holding = null
```

---

# Phase 10. Run Demo 완성

## 목표

전체 파이프라인을 한 번에 실행한다.

## 구현 파일

```text
scripts/run_demo.py
```

## 완료 기준

아래 명령어로 데모가 실행되어야 한다.

```bash
python scripts/run_demo.py
```

출력에 반드시 포함되어야 하는 것:

```text
Instruction
Parsed Instruction
Raw Plan
Validation Result
Corrected Plan
Execution Result
```

---

# 6. Codex 작업 지시문

아래 내용을 Codex에게 그대로 전달한다.

```text
프로젝트명: semantic_robot_planner

목표:
사람의 한국어 언어 지시와 semantic scene map JSON을 입력받아 raw task plan을 생성하고, 각 step이 scene state와 skill precondition을 만족하는지 검증한 뒤, 실행 불가능한 plan은 self-correction으로 수정하고 symbolic execution 결과를 출력하는 MVP를 구현한다.

중요한 범위 제한:
- 실제 로봇 제어는 하지 않는다.
- ROS는 사용하지 않는다.
- Isaac Sim 제어는 하지 않는다.
- LLM API는 사용하지 않는다.
- 우선 JSON 기반 symbolic planning으로 구현한다.
- dataclass 기반으로 단순하고 읽기 쉬운 코드로 작성한다.

반드시 구현할 MVP 시나리오:
instruction = "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘."
scene:
- drawer_1은 closed
- cup_red_1은 inside drawer_1
- cup_red_1은 visible=false, reachable=false
- table_1은 reachable=true

raw plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

validator 결과:
- valid=false
- failure_type=missing_precondition
- reason: cup_red_1 is inside drawer_1 and drawer_1 is closed

self_corrector 결과:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1

executor 결과:
- success=true
- drawer_1.state=open
- cup_red_1.location=on:table_1
- robot.holding=null

구현 순서:
1. 폴더 구조 생성
2. data/scenes/scene_001.json 생성
3. data/skills/basic_skills.json 생성
4. schema dataclass 구현
5. scene_loader 구현
6. rule_parser 구현
7. rule_task_planner 구현
8. plan_validator 구현
9. self_corrector 구현
10. skill_matcher 구현
11. symbolic_executor 구현
12. scripts/run_demo.py 구현
13. tests 작성

출력 요구:
python scripts/run_demo.py 실행 시 아래 섹션이 콘솔에 출력되어야 한다.
- [Instruction]
- [Parsed Instruction]
- [Raw Plan]
- [Validation Result]
- [Corrected Plan]
- [Execution Result]

코드 스타일:
- 함수는 작게 나눈다.
- 변수명은 명확하게 작성한다.
- 예외 상황은 ValueError로 처리한다.
- JSON 입출력 함수는 utils/io.py에 분리한다.
- MVP가 먼저 돌아가게 하고, 과한 추상화는 피한다.
```

---

# 7. 테스트 케이스

# 7.1 정상 수정 케이스

입력:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

기대:

```text
raw plan은 실패해야 한다.
corrected plan은 성공해야 한다.
```

---

# 7.2 이미 보이는 물체 케이스

scene:

```text
cup_blue_1은 on table_1
visible=true
reachable=true
```

입력:

```text
파란 컵을 집어줘.
```

기대:

```text
raw plan:
1. PICK cup_blue_1

validation:
valid=true
```

---

# 7.3 목적지 없음 케이스

입력:

```text
빨간 컵을 싱크대 위에 올려줘.
```

scene:

```text
sink_1 없음
```

기대:

```text
failure_type = invalid_destination
```

---

# 7.4 잘못된 대상 케이스

입력:

```text
초록 컵을 집어줘.
```

scene:

```text
green cup 없음
```

기대:

```text
failure_type = wrong_target
또는 target_not_found
```

---

# 8. 평가 지표

MVP 이후에는 아래 지표를 기록한다.

# 8.1 Planning Success Rate

```text
성공한 task 수 / 전체 task 수
```

# 8.2 Verification Accuracy

```text
검증기가 실제 오류를 올바르게 탐지한 비율
```

# 8.3 Correction Success Rate

```text
수정된 plan이 symbolic execution에서 성공한 비율
```

# 8.4 Missing Step Recovery Rate

```text
누락된 step을 올바르게 삽입한 비율
```

# 8.5 Repeated Failure Reduction Rate

```text
failure memory 사용 후 반복 실패가 줄어든 비율
```

MVP에서는 수치보다 case study 중심으로 정리한다.

---

# 9. 결과 보고서 구조

MVP가 완성되면 `reports/demo_report.md`를 만든다.

구조:

```md
# Demo Report

## 1. 실험 목적

## 2. 입력 명령

## 3. Scene 상태

## 4. Raw Plan

## 5. 발견된 오류

## 6. Self-Correction 결과

## 7. Symbolic Execution 결과

## 8. 실패 유형 분석

## 9. 현재 한계

## 10. 다음 단계
```

---

# 10. 현재 한계

아래 한계는 보고서에 반드시 적는다.

```text
1. 현재 semantic map은 실제 perception에서 생성된 것이 아니라 수동 JSON이다.
2. 현재 instruction parser는 rule-based이므로 표현이 조금만 바뀌어도 실패할 수 있다.
3. 현재 executor는 실제 물리 시뮬레이션이 아니라 symbolic state update다.
4. grasp pose, collision, trajectory feasibility는 아직 다루지 않는다.
5. failure memory는 저장 중심이며 retrieval 기반 planning 개선은 후속 단계다.
```

---

# 11. 후속 확장 단계

MVP 이후 확장은 아래 순서로 한다.

# Step 1. instruction 다양화

```text
- 컵을 집어줘
- 컵을 테이블 위에 올려줘
- 서랍 안 물건을 꺼내줘
- 상자 안 물건을 꺼내줘
```

# Step 2. scene 다양화

```text
- drawer open scene
- drawer closed scene
- object on table scene
- object inside container scene
- object blocked by obstacle scene
```

# Step 3. LLM parser 추가

```text
rule_parser와 같은 출력 형식을 유지한다.
내부 구현만 LLM으로 바꾼다.
```

# Step 4. LLM planner 추가

```text
rule_task_planner와 같은 TaskPlan 형식을 유지한다.
내부 구현만 LLM planner로 바꾼다.
```

# Step 5. failure memory retrieval 추가

```text
새 instruction이 들어오면 유사 failure memory를 검색한다.
planner에 lesson을 제공한다.
```

# Step 6. Isaac Sim scene export 연결

```text
Isaac Sim에서 object metadata를 export한다.
export 결과를 scene JSON 형식으로 변환한다.
symbolic pipeline은 그대로 유지한다.
```

# Step 7. manipulation feasibility 추가

```text
graspable
reachable
blocked_by
container_state
distance
orientation
```

필드를 활용해 실행 가능성 검증을 강화한다.

---

# 12. 최종 완료 기준

프로젝트 1차 완료 기준은 아래다.

```text
1. README.md에 프로젝트 목적이 명확히 적혀 있다.
2. scene_001.json이 존재한다.
3. basic_skills.json이 존재한다.
4. python scripts/run_demo.py가 실행된다.
5. raw plan이 실패하는 이유가 출력된다.
6. corrected plan이 출력된다.
7. symbolic execution이 success=true를 반환한다.
8. failure_memory.jsonl에 실패 사례가 저장된다.
9. tests가 최소 5개 이상 통과한다.
10. demo_report.md를 작성할 수 있을 정도의 결과가 남는다.
```

---

# 13. 가장 중요한 원칙

이 프로젝트의 핵심은 거대한 로봇 시스템을 한 번에 만드는 것이 아니다.

핵심은 아래 한 흐름을 작게 증명하는 것이다.

```text
사람의 명령을
장면의 의미 구조와 연결하고,
작업 순서로 바꾸고,
그 작업 순서가 실제로 가능한지 검사하고,
틀리면 고친다.
```

이 흐름이 안정적으로 동작하면, 이후 LLM, VLA, Isaac Sim, ROS, real robot으로 확장할 수 있다.

# 1부. 프로젝트 정의와 기준점

# 0. 프로젝트 이름

## 영문 이름

`Semantic Map-Guided Task Planning and Verification for Language-Guided Robot Manipulation`

## 짧은 이름

`semantic_robot_planner`

## 한국어 이름

`언어 지시 기반 로봇 조작을 위한 Semantic Map 기반 작업 계획 및 실행 가능성 검증`

---

# 1. 프로젝트 한 줄 정의

이 프로젝트는 사람의 언어 지시와 semantic scene map을 입력받아 로봇이 수행해야 할 task plan을 생성하고, 각 step이 현재 장면 상태와 skill 조건을 만족하는지 검증한 뒤, 실행 불가능한 계획은 self-correction 또는 replanning으로 수정하는 JSON 기반 symbolic robot planning 시스템이다.

---

# 2. 프로젝트를 하는 이유

로봇이 사람의 말을 듣고 실제 환경에서 작업을 수행하려면 단순히 명령을 action sequence로 바꾸는 것만으로는 부족하다.

예를 들어 사람이 다음과 같이 말한다고 하자.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

겉으로 보기에는 단순한 명령이지만, 로봇 입장에서는 여러 단계의 판단이 필요하다.

```text
1. 빨간 컵이 무엇인지 찾아야 한다.
2. 빨간 컵이 어디에 있는지 알아야 한다.
3. 컵이 서랍 안에 있다면 서랍 상태를 확인해야 한다.
4. 서랍이 닫혀 있다면 먼저 열어야 한다.
5. 컵이 보이고 잡을 수 있는 상태가 되어야 한다.
6. 컵을 잡은 뒤 테이블 위에 놓아야 한다.
7. 중간에 실패하면 다시 계획해야 한다.
```

따라서 이 프로젝트의 핵심은 다음과 같다.

```text
언어 지시
→ 장면의 의미 구조 이해
→ 작업 계획 생성
→ 계획 검증
→ skill 조건 확인
→ 실행 가능성 판단
→ 실패 시 수정 / 재계획
```

이 프로젝트는 실제 로봇 제어 전체를 처음부터 구현하지 않는다.  
대신 **JSON 기반 symbolic scene**에서 시작해, 로봇 작업 계획의 구조를 작고 명확하게 검증한다.

---

# 3. 핵심 문제 정의

## 3.1 해결하려는 문제

LLM 또는 rule-based planner가 만든 task plan은 그럴듯해 보여도 실제 장면 상태와 맞지 않을 수 있다.

예시:

```text
명령:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

잘못된 plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

이 plan은 겉으로는 자연스럽지만 실제로는 틀렸다.

이유:

```text
- cup_red_1은 drawer_1 안에 있다.
- drawer_1은 closed 상태다.
- cup_red_1은 visible=false 이다.
- cup_red_1은 reachable=false 이다.
- 따라서 바로 PICK할 수 없다.
```

올바른 plan은 다음과 같아야 한다.

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

이 프로젝트는 이런 오류를 자동으로 찾고, 고친 plan을 생성하는 것을 목표로 한다.

---

# 4. 프로젝트 핵심 질문

이 프로젝트는 아래 질문에 답하기 위한 구조로 만든다.

## 4.1 메인 질문

```text
사람의 언어 지시와 semantic scene map이 주어졌을 때,
로봇이 실행 가능한 task plan을 생성하고,
잘못된 plan을 검증·수정할 수 있는가?
```

## 4.2 세부 질문

```text
1. 언어 지시에서 target object, source, destination, task intent를 추출할 수 있는가?
2. scene JSON에서 object, place, relation, state를 읽어 semantic map처럼 사용할 수 있는가?
3. task planner가 명령과 scene을 바탕으로 step sequence를 만들 수 있는가?
4. plan verifier가 precondition violation, wrong order, unreachable target을 탐지할 수 있는가?
5. skill matcher가 task action을 실행 가능한 robot skill과 연결할 수 있는가?
6. symbolic executor가 plan을 순서대로 실행하며 state 변화를 추적할 수 있는가?
7. self-corrector가 실패 원인을 바탕으로 필요한 step을 삽입하거나 plan을 수정할 수 있는가?
8. failure memory가 반복되는 실패 유형을 저장하고 다음 planning에 활용될 수 있는가?
```

---

# 5. 프로젝트에서 사용하는 핵심 개념

## 5.1 Human Instruction

사람이 자연어로 내리는 명령이다.

예시:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
파란 그릇을 집어줘.
상자 안에 있는 물건을 꺼내줘.
테이블 위 컵을 싱크대 옆에 놓아줘.
```

현재 MVP에서는 한국어 명령 3~5개만 지원한다.  
나중에 영어 명령과 LLM parser를 붙일 수 있다.

---

## 5.2 Semantic Scene Map

실제 SLAM이나 3D reconstruction을 의미하지 않는다.

이 프로젝트에서 semantic scene map은 JSON으로 표현된 장면의 의미 구조다.

포함 정보:

```text
- 장소: table, drawer, shelf, counter
- 물체: cup, bowl, book, bottle
- 상태: open, closed, visible, reachable, graspable
- 관계: inside, on, near, blocked_by
- 로봇 상태: holding, gripper_state, current_location
```

예시:

```json
{
  "scene_id": "scene_001",
  "places": [
    {
      "place_id": "table_1",
      "type": "table",
      "reachable": true
    },
    {
      "place_id": "drawer_1",
      "type": "drawer",
      "state": "closed",
      "reachable": true
    }
  ],
  "objects": [
    {
      "object_id": "cup_red_1",
      "category": "cup",
      "color": "red",
      "location": "inside:drawer_1",
      "visible": false,
      "reachable": false,
      "graspable": true
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
    "gripper_state": "open"
  }
}
```

---

## 5.3 Task Plan

로봇이 수행해야 하는 작업 순서다.

예시:

```json
{
  "plan_id": "plan_001",
  "steps": [
    {
      "step_id": 1,
      "action": "OPEN",
      "target": "drawer_1"
    },
    {
      "step_id": 2,
      "action": "PICK",
      "target": "cup_red_1"
    },
    {
      "step_id": 3,
      "action": "PLACE",
      "target": "cup_red_1",
      "destination": "table_1"
    }
  ]
}
```

현재 MVP에서 지원할 action은 아래 5개다.

```text
OPEN
PICK
PLACE
MOVE_TO
LOOK_AROUND
```

단, MVP 1차에서는 `OPEN`, `PICK`, `PLACE`만 구현한다.

---

## 5.4 Skill Library

task action을 실제 로봇 skill과 연결하는 사전이다.

예시:

```text
OPEN → open_drawer_skill
PICK → grasp_object_skill
PLACE → place_object_skill
```

각 skill은 실행 조건과 효과를 가진다.

예시:

```json
{
  "skill_id": "grasp_object_skill",
  "action": "PICK",
  "required_conditions": [
    "target.visible == true",
    "target.reachable == true",
    "target.graspable == true",
    "robot.holding == null"
  ],
  "effects": [
    "robot.holding = target.object_id"
  ]
}
```

이 프로젝트에서는 실제 gripper 제어를 하지 않는다.  
대신 skill이 실행 가능한 조건인지 symbolic하게 검사한다.

---

## 5.5 Plan Verification

생성된 task plan이 현재 scene에서 실행 가능한지 검사하는 단계다.

검사 항목:

```text
1. target object가 존재하는가?
2. destination이 존재하는가?
3. target object가 visible한가?
4. target object가 reachable한가?
5. target object가 graspable한가?
6. drawer/container가 닫혀 있는데 내부 물체를 바로 pick하려고 하지 않는가?
7. robot이 이미 물체를 들고 있는데 또 pick하려고 하지 않는가?
8. robot이 아무것도 들고 있지 않은데 place하려고 하지 않는가?
9. 이전 step의 effect가 다음 step의 precondition을 만족하는가?
```

---

## 5.6 Self-Correction

검증 실패가 발생했을 때 plan을 수정하는 단계다.

예시:

```text
실패:
PICK cup_red_1 불가능

원인:
cup_red_1은 drawer_1 안에 있고 drawer_1이 closed 상태임

수정:
PICK 이전에 OPEN drawer_1 삽입
```

수정 결과:

```text
기존 plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

수정 plan:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

---

## 5.7 Failure Memory

반복되는 실패 유형을 저장하는 memory다.

현재 MVP에서는 JSON 파일로 저장한다.

예시:

```json
{
  "memory_id": "fail_001",
  "instruction_pattern": "retrieve object inside closed drawer",
  "failure_type": "missing_precondition",
  "bad_plan": ["PICK cup_red_1"],
  "corrected_plan": ["OPEN drawer_1", "PICK cup_red_1"],
  "lesson": "If target object is inside a closed drawer, open the drawer before picking.",
  "success_after_use": 0
}
```

MVP에서는 저장만 하고, retrieval은 2차 단계에서 구현한다.

---

# 6. 포함 범위

이 프로젝트에 포함되는 것은 아래와 같다.

```text
1. JSON 기반 semantic scene map
2. 한국어 instruction 예시 3~5개
3. rule-based instruction parser
4. rule-based task planner
5. task plan schema
6. skill library
7. plan verifier
8. skill precondition checker
9. symbolic executor
10. self-correction
11. failure memory 저장
12. raw plan vs corrected plan 비교
13. 간단한 평가 지표
14. 데모 스크립트
```

---

# 7. 제외 범위

아래는 지금 하지 않는다.

```text
1. 실제 로봇 하드웨어 제어
2. 실제 gripper 제어
3. trajectory planning
4. motion planning 알고리즘 구현
5. 강화학습
6. imitation learning 학습
7. OpenVLA fine-tuning
8. 대규모 LLM agent 시스템
9. 실제 SLAM 기반 semantic map 생성
10. 대규모 dataset 구축
11. Isaac Sim 로봇 제어 자동화
12. ROS 연동
```

단, 나중에 확장할 수 있도록 구조는 열어둔다.

---

# 8. 시스템 전체 흐름

## 8.1 기본 흐름

```text
[1] Human Instruction
        ↓
[2] Instruction Parser
        ↓
[3] Semantic Scene Map Loader
        ↓
[4] Task Planner
        ↓
[5] Plan Verifier
        ↓
[6] Skill Matcher
        ↓
[7] Symbolic Executor
        ↓
[8] Failure Detector
        ↓
[9] Self-Corrector / Replanner
        ↓
[10] Failure Memory
        ↓
[11] Evaluation Result
```

---

## 8.2 MVP 데모 흐름

입력:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

scene 상태:

```text
drawer_1.state = closed
cup_red_1.location = inside:drawer_1
cup_red_1.visible = false
cup_red_1.reachable = false
table_1.reachable = true
robot.holding = null
```

raw plan:

```text
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

verification result:

```text
valid = false
failure_type = missing_precondition
reason = cup_red_1 is inside drawer_1, but drawer_1 is closed.
suggested_fix = Insert OPEN drawer_1 before PICK cup_red_1.
```

corrected plan:

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

execution result:

```text
success = true
final_robot_state.holding = null
cup_red_1.location = on:table_1
drawer_1.state = open
```

---

# 9. 실패 유형 정의

## 9.1 missing_precondition

필요한 조건이 만족되지 않았는데 action을 실행하려는 경우.

예시:

```text
drawer가 closed인데 내부 object를 PICK하려고 함.
```

---

## 9.2 wrong_order

step 순서가 잘못된 경우.

예시:

```text
PICK before OPEN
PLACE before PICK
```

---

## 9.3 wrong_target

instruction이 요구한 target과 다른 object를 선택한 경우.

예시:

```text
빨간 컵을 요청했는데 파란 컵을 선택함.
```

---

## 9.4 unreachable_object

object가 존재하지만 현재 상태에서 접근할 수 없는 경우.

예시:

```text
cup이 drawer 안에 있음.
drawer가 closed 상태임.
```

---

## 9.5 invisible_object

object가 존재하지만 visible하지 않은 경우.

예시:

```text
컵이 가려져 있거나 container 내부에 있음.
```

---

## 9.6 invalid_destination

목적지가 없거나 놓을 수 없는 장소인 경우.

예시:

```text
PLACE cup_red_1 sink_1
하지만 scene에 sink_1이 없음.
```

---

## 9.7 skill_not_available

action에 대응되는 skill이 없는 경우.

예시:

```text
POUR action이 plan에 있지만 skill library에 pour_skill이 없음.
```

---

## 9.8 execution_failed

symbolic executor가 step 실행 중 실패한 경우.

예시:

```text
PICK 조건은 맞는 것처럼 보였지만 robot.holding이 이미 다른 object였음.
```

---

# 10. MVP 기준

## 10.1 MVP 목표

MVP는 아래 하나의 데모가 성공하면 된다.

```text
scene_001.json을 읽는다.
instruction 하나를 입력한다.
raw plan을 만든다.
raw plan의 문제를 검증한다.
corrected plan을 만든다.
corrected plan을 symbolic execution한다.
최종 성공 결과를 출력한다.
```

---

## 10.2 MVP 입력

```text
instruction:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

---

## 10.3 MVP 출력

```json
{
  "instruction": "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.",
  "raw_plan": [
    "PICK cup_red_1",
    "PLACE cup_red_1 table_1"
  ],
  "validation": {
    "valid": false,
    "failure_type": "missing_precondition",
    "reason": "cup_red_1 is inside drawer_1 and drawer_1 is closed."
  },
  "corrected_plan": [
    "OPEN drawer_1",
    "PICK cup_red_1",
    "PLACE cup_red_1 table_1"
  ],
  "execution": {
    "success": true,
    "final_state": {
      "drawer_1.state": "open",
      "cup_red_1.location": "on:table_1",
      "robot.holding": null
    }
  }
}
```

---

# 11. 개발 원칙

## 11.1 작게 시작한다

처음부터 LLM, Isaac Sim, ROS, real robot을 붙이지 않는다.

우선 JSON 기반 symbolic planning으로 아래를 증명한다.

```text
언어 지시 → scene map → task plan → 검증 → 수정 → 실행 결과
```

---

## 11.2 모듈을 분리한다

각 기능은 독립 모듈로 만든다.

```text
instruction parser
semantic map loader
task planner
plan verifier
skill matcher
symbolic executor
self-corrector
failure memory
evaluator
```

나중에 rule-based parser를 LLM parser로 바꾸더라도 다른 모듈을 크게 수정하지 않도록 한다.

---

## 11.3 출력 형식을 고정한다

모든 중간 결과는 JSON 또는 dataclass/Pydantic model 형태로 고정한다.

예시:

```text
InstructionParseResult
SemanticSceneMap
TaskPlan
ValidationResult
ExecutionResult
CorrectionResult
MemoryRecord
```

---

## 11.4 실패 유형을 반드시 기록한다

단순히 `false`만 출력하면 안 된다.

반드시 아래를 같이 기록한다.

```text
- failure_type
- failed_step
- reason
- suggested_fix
```

---

## 11.5 데모가 먼저다

완벽한 시스템보다 먼저 하나의 데모가 끝까지 돌아가야 한다.

최초 목표는 아래 명령 하나다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

---

# 12. 최종 목표 이미지

이 프로젝트가 최종적으로 보여줘야 하는 것은 아래다.

```text
사람 명령:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

장면 이해:
cup_red_1 is inside drawer_1
drawer_1 is closed
table_1 is reachable

초기 plan:
PICK cup_red_1
PLACE cup_red_1 table_1

검증:
PICK 실패
이유: drawer가 닫혀 있어 cup이 visible/reachable하지 않음

수정:
OPEN drawer_1 삽입

최종 plan:
OPEN drawer_1
PICK cup_red_1
PLACE cup_red_1 table_1

실행:
success
```

이 한 흐름을 안정적으로 보여주는 것이 1차 목표다.

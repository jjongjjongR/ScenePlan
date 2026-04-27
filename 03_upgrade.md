# 3. Upgrade — 고도화 방향 정리

> 프로젝트명: `Semantic Map-Guided Task Planning and Verification for Language-Guided Robot Manipulation`  
> 목적: MVP 이후 고도화 방향을 정리한다.  
> 핵심 관점: **MVP는 JSON 기반 symbolic validation으로 작게 증명하고, 이후 Isaac Sim 기반 검증과 ROS2/실제 로봇 연동으로 확장한다.**

---

## 0. 이 문서의 역할

이 문서는 현재 MVP 이후 프로젝트를 어떻게 확장할지 정리한 고도화 문서다.

현재 MVP는 다음 흐름을 작게 검증한다.

```text
Human Instruction
→ Semantic Scene JSON
→ Raw Task Plan
→ Plan Verification
→ Self-Correction
→ Symbolic Execution
→ Result
```

하지만 최종 목표는 JSON 기반 symbolic validation에 머무는 것이 아니다.

장기적으로는 다음 흐름으로 확장한다.

```text
Human Instruction
→ Isaac Sim Scene / Object Metadata
→ Semantic Scene Map
→ Task Plan
→ Plan Verification
→ Skill Chaining
→ Isaac Sim Validation
→ Failure Memory
→ Replanning
→ ROS2 / Real Robot Extension
```

즉, 이 프로젝트는 처음부터 실제 로봇 제어를 만들기보다, **task planning과 plan verification 구조를 먼저 증명하고, 이후 simulated robotics validation으로 확장하는 방식**을 따른다.

---

## 1. 현재 MVP의 위치

## 1.1 MVP의 목표

현재 MVP의 목표는 매우 작고 명확하다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

이 명령에 대해 다음 흐름이 동작하면 된다.

```text
scene:
drawer_1 = closed
cup_red_1 = inside drawer_1
table_1 = reachable

raw plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

validation:
PICK 불가능. drawer가 닫혀 있어 cup_red_1이 visible/reachable하지 않음.

corrected plan:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1

execution:
success
```

## 1.2 MVP가 증명하는 것

MVP는 거대한 로봇 시스템을 증명하는 것이 아니다.

MVP가 증명하는 것은 아래 한 가지다.

> 사람의 언어 지시와 장면 상태가 주어졌을 때, 로봇 task plan이 현재 상태에서 실행 가능한지 검증하고, 틀린 plan을 수정할 수 있는가?

즉, MVP는 다음 문제를 작게 보여준다.

```text
언어 지시
→ 장면의 의미 구조
→ 작업 순서
→ 조건 검증
→ 오류 탐지
→ 계획 수정
```

이 구조가 안정적으로 동작하면, 이후 Isaac Sim, LLM planner, VLA, ROS2, real robot으로 확장할 수 있다.

---

## 2. 고도화 전체 로드맵

고도화는 한 번에 크게 가지 않는다.

아래 순서로 확장한다.

```text
MVP 1.0  JSON Symbolic Validation
MVP 1.5  Failure Memory 저장
MVP 2.0  Memory-Aware Replanning
MVP 2.5  Scene / Instruction Variation Evaluation
MVP 3.0  Isaac Sim Metadata Validation
MVP 3.5  Isaac Sim Execution Validation
MVP 4.0  ROS2 / Real Robot Extension
```

핵심 원칙은 다음과 같다.

```text
1. 먼저 symbolic 구조를 만든다.
2. 그 구조를 여러 scene과 instruction으로 검증한다.
3. 실패 사례를 memory로 저장하고 다시 사용한다.
4. Isaac Sim에서 object metadata를 추출해 같은 verifier에 연결한다.
5. 이후 high-level execution validation으로 확장한다.
6. ROS2는 실제 robot skill execution이 필요할 때 연결한다.
```

---

## 3. Level 1 — JSON Symbolic Validation

## 3.1 목표

JSON 기반 semantic scene에서 task plan의 논리적 실행 가능성을 검증한다.

```text
instruction
→ semantic scene JSON
→ raw task plan
→ precondition check
→ corrected plan
→ symbolic execution
```

## 3.2 검증할 오류 유형

MVP 1.0에서는 아래 오류를 우선 다룬다.

```text
1. missing_precondition
2. wrong_order
3. wrong_target
4. invalid_destination
5. unreachable_object
6. invisible_object
7. skill_not_available
```

## 3.3 예시

```text
상황:
drawer_1 = closed
cup_red_1 = inside drawer_1
cup_red_1.visible = false
cup_red_1.reachable = false

raw plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

검증 결과:
PICK 실패
이유: cup_red_1은 drawer_1 안에 있고 drawer_1이 closed 상태임

수정:
PICK 이전에 OPEN drawer_1 삽입
```

## 3.4 완료 기준

```text
- scene_001.json을 읽을 수 있다.
- instruction 하나를 parse할 수 있다.
- raw plan을 생성할 수 있다.
- raw plan의 오류를 탐지할 수 있다.
- corrected plan을 만들 수 있다.
- corrected plan이 symbolic execution에서 success=true가 된다.
```

---

## 4. Level 1.5 — Failure Memory 저장

## 4.1 목표

계획 실패 사례를 memory로 저장한다.

처음에는 retrieval까지 하지 않아도 된다.

MVP 1.5의 핵심은 다음이다.

```text
실패한 plan
→ 실패 유형 분석
→ corrected plan 생성
→ lesson 저장
```

## 4.2 Failure Memory 예시

```json
{
  "memory_id": "fail_001",
  "instruction_pattern": "retrieve object inside closed drawer",
  "failure_type": "missing_precondition",
  "bad_plan": ["PICK cup_red_1", "PLACE cup_red_1 table_1"],
  "corrected_plan": ["OPEN drawer_1", "PICK cup_red_1", "PLACE cup_red_1 table_1"],
  "lesson": "If target object is inside a closed drawer, open the drawer before picking.",
  "use_count": 0,
  "success_after_use": 0
}
```

## 4.3 완료 기준

```text
- failure_memory.jsonl에 실패 사례가 저장된다.
- failure_type, bad_plan, corrected_plan, lesson이 기록된다.
- demo_report.md에서 실패 원인과 수정 결과를 설명할 수 있다.
```

---

## 5. Level 2 — Memory-Aware Replanning

## 5.1 목표

저장된 failure memory를 다음 planning에 다시 활용한다.

이 단계부터 중앙대 AI & Robotics Lab 방향의 **active memory**와 더 직접적으로 연결된다.

## 5.2 구조

```text
New Instruction
→ Memory Retriever
→ Similar Failure Pattern
→ Planner Hint
→ Raw / Memory-Aware Plan
→ Verification
→ Correction
→ Memory Update
```

## 5.3 예시

이전 실패 memory:

```text
If target object is inside a closed drawer, open the drawer before picking.
```

새로운 instruction:

```text
서랍 안에 있는 파란 컵을 꺼내줘.
```

memory-aware planner는 처음부터 다음 plan을 만들 수 있다.

```text
1. OPEN drawer_1
2. PICK cup_blue_1
```

## 5.4 비교 실험

```text
Case A. Memory 없이 planning
Case B. Memory 사용 후 planning

비교 지표:
- repeated failure reduction rate
- raw plan success rate
- memory-aware plan success rate
- correction success rate
```

## 5.5 완료 기준

```text
- 유사 failure memory를 검색할 수 있다.
- 검색된 lesson을 planner에 전달할 수 있다.
- memory 사용 전/후 planning 결과를 비교할 수 있다.
- 반복 실패가 줄어드는 case study를 만들 수 있다.
```

---

## 6. Level 2.5 — Scene / Instruction Variation Evaluation

## 6.1 목표

단일 scene, 단일 instruction에서 벗어나 여러 상황으로 확장한다.

## 6.2 Scene Variation

```text
1. drawer closed scene
2. drawer open scene
3. object on table scene
4. object inside container scene
5. object blocked by obstacle scene
6. target object not visible scene
7. similar objects ambiguity scene
```

## 6.3 Instruction Variation

```text
1. 빨간 컵을 집어줘.
2. 서랍 안에 있는 빨간 컵을 꺼내줘.
3. 빨간 컵을 테이블 위에 올려줘.
4. 상자 안에 있는 물건을 꺼내줘.
5. 파란 컵 말고 빨간 컵을 집어줘.
6. 컵을 싱크대 옆에 놓아줘.
7. 보이지 않는 컵을 찾아서 꺼내줘.
```

## 6.4 평가 지표

```text
- task plan success rate
- verification accuracy
- correction success rate
- missing step recovery rate
- invalid destination detection rate
- wrong target detection rate
- repeated failure reduction rate
```

## 6.5 완료 기준

```text
- scene 3개 이상
- instruction 5개 이상
- failure type 3개 이상
- raw plan vs corrected plan 비교표 작성
- demo_report.md 또는 evaluation_report.md 작성
```

---

## 7. Level 3 — Isaac Sim Metadata Validation

## 7.1 목표

Isaac Sim 장면에서 object metadata를 추출하고, 이를 semantic scene JSON으로 변환해 기존 verifier에 연결한다.

이 단계에서도 아직 정교한 로봇 제어를 하지 않는다.

핵심은 다음이다.

```text
Isaac Sim Scene
→ Object Metadata Export
→ Semantic Scene JSON
→ Plan Verification
→ Self-Correction
```

## 7.2 Isaac Sim의 역할

Isaac Sim은 이 프로젝트에서 **controlled evaluation environment** 역할을 한다.

즉, 실제 로봇 하드웨어 없이도 table, drawer, object, obstacle이 있는 장면을 만들고, 그 상태를 기반으로 task plan이 말이 되는지 검증한다.

## 7.3 최소 Isaac Sim Scene

```text
- room 또는 tabletop scene 1개
- table_1
- drawer_1 또는 container_1
- cup_red_1
- cup_blue_1
- obstacle_1
- robot arm 또는 mobile-manipulation-like setup
```

## 7.4 추출할 Metadata

```json
{
  "scene_id": "isaac_scene_001",
  "objects": [
    {
      "object_id": "drawer_1",
      "category": "drawer",
      "state": "closed",
      "visible": true,
      "reachable": true,
      "position": [0.4, 0.2, 0.7]
    },
    {
      "object_id": "cup_red_1",
      "category": "cup",
      "color": "red",
      "location": "inside:drawer_1",
      "visible": false,
      "reachable": false,
      "position": [0.45, 0.2, 0.65]
    }
  ],
  "robot_state": {
    "holding": null,
    "gripper_state": "open",
    "current_location": "table_area"
  }
}
```

## 7.5 완료 기준

```text
- Isaac Sim에서 최소 scene screenshot을 확보한다.
- scene object list를 JSON으로 정리한다.
- 수동 또는 자동 metadata export 결과를 semantic scene JSON으로 변환한다.
- 기존 plan verifier가 Isaac Sim 기반 scene JSON에서도 동작한다.
```

---

## 8. Level 3.5 — Isaac Sim Execution Validation

## 8.1 목표

Corrected plan이 Isaac Sim 장면의 상태 변화와 일치하는지 검증한다.

처음부터 정교한 grasp trajectory나 low-level control을 구현하지 않는다.

초기에는 high-level state transition validation으로 충분하다.

## 8.2 검증 예시

Corrected plan:

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

Isaac Sim validation:

```text
- drawer_1.state가 closed에서 open으로 바뀌었는가
- cup_red_1이 drawer 밖으로 나왔는가
- cup_red_1이 table_1 위에 놓였는가
- robot.holding이 최종적으로 null인가
```

## 8.3 검증 방식

```text
1. symbolic executor가 예측한 final_state를 저장한다.
2. Isaac Sim scene의 실제 또는 proxy final_state를 저장한다.
3. 두 상태를 비교한다.
4. 일치하면 execution validation success로 본다.
```

## 8.4 완료 기준

```text
- corrected plan의 expected final_state를 생성할 수 있다.
- Isaac Sim scene의 observed final_state를 정리할 수 있다.
- expected final_state와 observed final_state를 비교할 수 있다.
- mismatch가 발생하면 failure_type으로 기록할 수 있다.
```

---

## 9. Level 4 — ROS2 / Real Robot Extension

## 9.1 현재 범위

ROS2는 현재 MVP 1차 범위에 포함하지 않는다.

이유는 다음과 같다.

```text
1. ROS2까지 넣으면 프로젝트 범위가 너무 커진다.
2. 현재 핵심은 low-level control이 아니라 task plan verification이다.
3. 신입 석사 지원 전 단계에서는 symbolic planning + Isaac Sim validation만으로도 충분한 연구 방향성을 보여줄 수 있다.
4. ROS2는 실제 skill execution 또는 real robot 연결이 필요해질 때 도입하는 것이 안전하다.
```

## 9.2 ROS2가 필요한 시점

ROS2는 다음 단계에서 필요하다.

```text
- task plan을 실제 robot skill server로 보내고 싶을 때
- Isaac Sim과 ROS2 bridge를 연결하고 싶을 때
- real robot arm 또는 mobile manipulator와 통신하고 싶을 때
- OPEN, PICK, PLACE를 ROS2 action interface로 실행하고 싶을 때
```

## 9.3 장기 구조

```text
Task Plan
→ Skill Matcher
→ ROS2 Action Interface
→ Robot Skill Server
→ Execution Result
→ Failure Detector
→ Replanner
```

## 9.4 컨택용 표현

```text
ROS2는 본 프로젝트의 1차 범위에는 포함하지 않는다. 현재는 JSON 기반 symbolic validation과 Isaac Sim metadata validation으로 task planning / verification 구조를 먼저 검증한다. 장기적으로는 task plan을 ROS2 action interface 또는 skill server와 연결하여 실제 로봇 실행으로 확장할 수 있다.
```

---

## 10. 연구실별 고도화 포지셔닝

## 10.1 중앙대 AI & Robotics Lab 기준

중앙대 AI & Robotics Lab 기준으로는 아래 키워드를 앞에 둔다.

```text
- robot task planning
- self-correction
- active memory
- continual adaptation
- LLM/VLA-style planner
- Isaac Sim validation
```

컨택용 설명:

```text
현재는 JSON 기반 symbolic scene에서 task plan verification과 self-correction 구조를 먼저 구현하고 있습니다. 이후에는 failure memory retrieval을 통해 같은 유형의 planning 오류를 줄이고, Isaac Sim 기반 scene validation으로 확장하여 self-corrective robot planning 구조를 검증하고자 합니다.
```

## 10.2 한양대 Robots with Humans Lab 기준

한양대 Robots with Humans Lab 기준으로는 아래 키워드를 앞에 둔다.

```text
- human-friendly robot intelligence
- semantic mapping
- task planning
- skill chaining
- grasping
- manipulation feasibility
- replanning
```

컨택용 설명:

```text
현재는 JSON 기반 semantic scene에서 사람의 언어 지시를 task plan으로 바꾸고, 각 step이 scene state와 skill condition을 만족하는지 검증하는 MVP를 구현하고 있습니다. 이후에는 Isaac Sim 기반 scene metadata validation과 manipulation feasibility check로 확장하여 language-guided robot planning 구조를 더 실제 로봇 작업에 가깝게 발전시키고자 합니다.
```

---

## 11. 고도화 후 평가 지표

## 11.1 Planning 지표

```text
- raw plan success rate
- corrected plan success rate
- memory-aware plan success rate
- task plan step accuracy
- correct step ordering rate
```

## 11.2 Verification 지표

```text
- precondition violation detection accuracy
- wrong order detection accuracy
- wrong target detection accuracy
- invalid destination detection accuracy
- unreachable object detection accuracy
```

## 11.3 Correction 지표

```text
- correction success rate
- missing step recovery rate
- unnecessary correction rate
- failed repair rate
```

## 11.4 Memory 지표

```text
- repeated failure reduction rate
- memory retrieval precision
- positive memory usefulness
- negative memory usefulness
```

## 11.5 Isaac Sim Validation 지표

```text
- metadata conversion success rate
- symbolic final_state vs Isaac Sim final_state match rate
- scene-state consistency score
- execution mismatch count
- manipulation feasibility mismatch count
```

---

## 12. 고도화 후 레포 구조 추가안

현재 MVP 구조 위에 아래 폴더와 파일을 추가한다.

```text
semantic_robot_planner/
├── docs/
│   ├── upgrade_plan.md
│   ├── isaac_sim_validation.md
│   ├── ros2_extension.md
│   ├── memory_aware_planning.md
│   └── lab_fit_comparison.md
├── data/
│   ├── isaac_scenes/
│   │   ├── isaac_scene_001.json
│   │   └── screenshots/
│   ├── scene_variations/
│   └── memory/
├── src/
│   ├── memory/
│   │   ├── memory_retriever.py
│   │   └── memory_aware_planner.py
│   ├── isaac/
│   │   ├── metadata_exporter.py
│   │   ├── scene_json_converter.py
│   │   └── state_comparator.py
│   ├── eval/
│   │   ├── scene_variation_eval.py
│   │   ├── memory_eval.py
│   │   └── isaac_validation_eval.py
│   └── ros2_extension/
│       ├── action_interface_plan.md
│       └── skill_server_design.md
└── reports/
    ├── demo_report.md
    ├── memory_eval_report.md
    └── isaac_validation_report.md
```

---

## 13. 고도화 우선순위

시간이 부족하면 아래 순서로 진행한다.

## 1순위 — 반드시

```text
1. MVP 완성
2. run_demo.py 실행 결과 확보
3. failure_memory 저장
4. demo_report.md 작성
5. README 정리
```

## 2순위 — 컨택 전에 가능하면

```text
1. scene 3개 이상으로 확장
2. failure type 3개 이상 검증
3. memory-aware planning 초안
4. raw vs corrected vs memory-aware 비교표
5. 중앙대 / 한양대 lab-fit 문서 작성
```

## 3순위 — 있으면 강해짐

```text
1. Isaac Sim scene screenshot
2. Isaac Sim object metadata JSON 예시
3. Isaac Sim metadata → semantic scene JSON 변환 예시
4. expected final_state vs observed final_state 비교 설계
```

## 4순위 — 장기 확장

```text
1. Isaac Sim execution validation
2. manipulation feasibility 확장
3. ROS2 action interface 설계
4. real robot skill server 연동
```

---

## 14. 최종 정리

이 프로젝트의 고도화 방향은 다음 한 문장으로 정리된다.

> JSON 기반 symbolic validation으로 language-guided task planning과 self-correction 구조를 먼저 증명하고, 이후 failure memory retrieval, Isaac Sim metadata validation, Isaac Sim execution validation, ROS2/real robot extension으로 단계적으로 확장한다.

중요한 것은 처음부터 모든 것을 구현하는 것이 아니다.

가장 중요한 순서는 다음이다.

```text
1. 작게 증명한다.
2. 실패 유형을 정의한다.
3. 실패를 고친다.
4. 실패를 기억한다.
5. 기억을 다음 planning에 사용한다.
6. Isaac Sim에서 같은 구조를 검증한다.
7. ROS2와 real robot은 마지막에 연결한다.
```

따라서 현재 프로젝트는 MVP만으로도 컨택용 출발점이 될 수 있다.

다만 중앙대 AI & Robotics Lab에는 **active memory / continual adaptation / Isaac Sim validation**을 고도화 방향으로 강조하고, 한양대 Robots with Humans Lab에는 **semantic mapping / task planning / skill chaining / manipulation feasibility / replanning**을 고도화 방향으로 강조하는 것이 가장 좋다.

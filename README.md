# ScenePlan

> 3D Scene-Aware Skill Path Feasibility Verification for Language-Guided Mobile Manipulation

## 프로젝트 정의

**ScenePlan**은 사람의 언어 지시와 semantic / 3D scene JSON을 바탕으로 로봇의 **Task Plan**과 **Skill Path Candidate**를 생성하고, 해당 경로가 현재 장면에서 실행 가능한지 검증하는 프로젝트입니다.

이 프로젝트의 핵심은 단순히 “어떤 행동을 해야 하는가”를 정하는 것이 아니라, 생성된 계획이 **symbolic precondition**과 **geometric feasibility**를 모두 만족하는지 확인하는 것입니다.

```text
Language Instruction
→ Semantic / 3D Scene
→ Task Plan
→ Skill Path Candidate
→ Feasibility Verification
→ Local Repair
→ Validation
```

---

## 프로젝트 개요

사람이 다음과 같이 명령했다고 가정합니다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

이 명령은 사람에게는 단순하지만, 로봇에게는 여러 단계의 판단이 필요합니다.

- 빨간 컵이 어떤 object인지 찾아야 합니다.
- 컵이 서랍 안에 있다는 semantic relation을 이해해야 합니다.
- 서랍이 닫혀 있다면 먼저 열어야 합니다.
- 현재 base pose에서 서랍 손잡이에 팔이 닿는지 확인해야 합니다.
- cup grasp pose가 arm reachability 안에 있는지 확인해야 합니다.
- 충돌 가능성이나 gripper clearance 문제를 확인해야 합니다.
- 실행 불가능한 경우 base pose나 waypoint를 수정해야 합니다.

ScenePlan은 이러한 과정을 JSON 기반 scene representation과 rule-based verification으로 작게 구현한 뒤, 이후 Isaac Sim과 learning-based feasibility prediction으로 확장하는 것을 목표로 합니다.

---

## 핵심 문제 정의

이 프로젝트가 다루는 핵심 문제는 다음입니다.

```text
Semantically Correct but Geometrically Infeasible Skill Path
```

한국어로는 다음과 같습니다.

```text
의미적으로는 맞지만 기하학적으로 실행 불가능한 Skill Path
```

예를 들어 아래 Task Plan은 의미적으로는 올바릅니다.

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

하지만 실제 mobile manipulation 환경에서는 여전히 실패할 수 있습니다.

- 현재 base pose에서 drawer handle에 팔이 닿지 않을 수 있습니다.
- cup grasp pose가 arm workspace 밖에 있을 수 있습니다.
- drawer를 여는 접근 경로가 container edge와 충돌할 수 있습니다.
- gripper clearance가 부족할 수 있습니다.
- base pose를 조금 조정하면 가능하지만, 현재 path에는 해당 수정이 없을 수 있습니다.

ScenePlan은 이러한 실패 가능성을 실행 전에 검증하고, 가능한 경우 local repair를 제안하는 구조를 목표로 합니다.

---

## 전체 시스템 파이프라인

```text
Human Instruction
→ Semantic / 3D Scene JSON
→ Task Plan
→ Skill Path Candidate
→ Symbolic + Geometric Feasibility Verification
→ Local Repair / Replanning
→ Symbolic / Simulated Validation
→ Failure Memory
→ Evaluation
```

| 단계 | 이름 | 설명 |
|---|---|---|
| 1 | Human Instruction | 사람이 자연어로 내리는 작업 명령 |
| 2 | Semantic / 3D Scene JSON | object, relation, state, pose, bbox, base pose 등을 포함한 장면 표현 |
| 3 | Task Plan | OPEN, PICK, PLACE 같은 high-level 작업 순서 |
| 4 | Skill Path Candidate | 각 skill을 수행하기 위한 base pose와 waypoint 후보 |
| 5 | Symbolic Feasibility Verification | object 존재 여부, container state, action precondition 검증 |
| 6 | Geometric Feasibility Verification | reachability, collision risk, clearance 검증 |
| 7 | Local Repair / Replanning | OPEN step 삽입, base pose 변경, waypoint 수정 |
| 8 | Symbolic / Simulated Validation | 수정된 plan/path의 최종 상태 변화 검증 |
| 9 | Failure Memory | 실패 유형, 원인, 수정 결과, lesson 저장 |
| 10 | Evaluation | raw / verified / repaired 결과 비교 |

---

## 개발 Phase 계획

| Phase | 단계 | 목표 | 주요 산출물 | 현재 상태 |
|---|---|---|---|---|
| Phase 0 | Project Setup | 프로젝트 기본 구조 생성 | README, data, src, tests, scripts 폴더 | 완료 |
| Phase 1 | Semantic Scene Data | 초기 scene / skill / instruction 데이터 작성 | `scene_001.json`, `basic_skills.json`, `demo_instructions.json` | 완료 |
| Phase 2 | Core Schema | Python dataclass 기반 핵심 자료구조 작성 | scene, instruction, plan, skill, validation, execution, memory schema | 완료 |
| Phase 3 | Scene Understanding | scene JSON 로드 및 object / relation 탐색 | scene_loader, object_finder, relation_finder | 완료 |
| Phase 4 | Instruction Parsing | 한국어 명령을 구조화된 ParsedInstruction으로 변환 | rule_parser | 완료 |
| Phase 5 | Raw Task Planning | ParsedInstruction과 scene을 바탕으로 raw task plan 생성 | rule_task_planner | 완료 |
| Phase 6 | 3D Scene Extension | scene JSON에 pose, bbox, base pose, handle pose 추가 | geometry field가 포함된 scene JSON | 예정 |
| Phase 7 | Geometry / Skill Path Schema | 3D pose와 skill path 자료구조 작성 | geometry_schema, skill_path_schema | 예정 |
| Phase 8 | Symbolic Feasibility Verification | symbolic precondition 위반 탐지 | plan_validator, precondition_checker | 예정 |
| Phase 9 | Symbolic Local Repair | missing precondition 기반 plan 수정 | self_corrector, correction_rules | 예정 |
| Phase 10 | Skill Path Generation | corrected task plan을 skill path candidate로 변환 | skill_path_generator | 예정 |
| Phase 11 | Geometric Feasibility Verification | reachability, collision, clearance 검증 | reachability_checker, collision_checker, clearance_checker | 예정 |
| Phase 12 | Geometric Local Repair | base pose 또는 waypoint 수정 제안 | base_pose_repair, local_path_repair | 예정 |
| Phase 13 | Integrated Demo | 전체 파이프라인 실행 | `scripts/run_demo.py` | 예정 |
| Phase 14 | Failure Memory | 실패 사례와 수정 결과 저장 | `failure_memory.jsonl`, memory_writer | 예정 |
| Phase 15 | Evaluation | scene / instruction / base pose variation 평가 | evaluation report, metrics | 예정 |
| Phase 16 | Isaac Sim Metadata Bridge | Isaac Sim metadata를 ScenePlan JSON으로 변환 | scene_json_converter | 장기 예정 |
| Phase 17 | Simulated Validation | Isaac Sim 기반 high-level validation | expected vs observed state 비교 | 장기 예정 |
| Phase 18 | Learning-based Feasibility Prediction | rule-based verifier를 학습 기반 predictor로 확장 | feasibility_model, dataset_builder | 장기 예정 |
| Phase 19 | ROS2 / Real Robot Extension | 실제 robot skill server와 연결 가능한 구조 설계 | ROS2 action interface design | 장기 예정 |

---

## 현재 구현 상태

현재 구현은 전체 파이프라인 중 **입력 처리와 Raw Task Planning 단계**까지 완료된 상태입니다.

완료된 기능:

- 프로젝트 기본 폴더 구조 생성
- symbolic scene / skill / instruction JSON 작성
- core dataclass schema 작성
- scene JSON 로더 구현
- object / relation finder 구현
- rule-based instruction parser 구현
- raw task planner 구현

현재 raw plan 예시:

```text
Instruction:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

Raw Task Plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

이 raw plan은 의도적으로 `OPEN drawer_1`을 포함하지 않습니다.  
이후 symbolic feasibility verifier와 local repair 단계에서 missing precondition을 탐지하고 수정하기 위한 기준 plan입니다.

---

## 프로젝트 한계 및 전제

현재 ScenePlan은 실제 로봇 시스템이 아니라, 연구 아이디어를 작게 검증하기 위한 JSON 기반 prototype입니다.

중요한 전제는 다음과 같습니다.

- 현재 semantic / 3D scene JSON은 실제 perception 결과가 아니라 수동으로 정의한 데이터입니다.
- 닫힌 서랍이나 상자 내부의 물체는 외부 카메라로 직접 볼 수 없습니다.
- hidden object 정보는 사용자 instruction, prior semantic map, memory, 또는 simulation metadata로 주어진다고 가정합니다.
- 3D vision의 역할은 hidden object를 투시하는 것이 아니라, container pose, handle pose, base pose, reachability, collision risk, clearance를 검증하는 것입니다.
- 현재 instruction parser는 rule-based이며, 자연어 이해 성능 자체를 목표로 하지 않습니다.
- 현재 reachability와 collision 검증은 실제 IK나 collision engine이 아닌 simplified geometry 기반으로 시작합니다.
- Isaac Sim, ROS2, MoveIt, cuRobo, real robot execution은 후속 확장 범위입니다.

---

## 실행 예시

현재까지 구현된 기능은 아래 명령으로 확인할 수 있습니다.

```bash
PYTHONPATH=. python tests/test_rule_parser.py
PYTHONPATH=. python tests/test_rule_task_planner.py
```

Raw Task Plan을 직접 출력하려면 다음을 실행합니다.

```bash
python - << 'PY'
from src.instruction.rule_parser import parse_instruction
from src.planner.rule_task_planner import create_raw_plan
from src.semantic_map.scene_loader import load_scene

scene = load_scene("data/scenes/scene_001.json")
instruction = parse_instruction("서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.")

raw_plan = create_raw_plan(
    instruction=instruction,
    scene=scene,
)

for step in raw_plan.steps:
    if step.destination is None:
        print(f"{step.step_id}. {step.action} {step.target}")
    else:
        print(f"{step.step_id}. {step.action} {step.target} {step.destination}")
PY
```

기대 출력:

```text
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

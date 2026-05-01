# Budget-aware Sim2Skill (formerly ScenePlan)

> 🚀 **Project Transition:** 이 프로젝트는 초기의 단순 JSON/규칙 기반 검증기(ScenePlan MVP)에서 발전하여, 제한된 로컬 GPU(RTX 3070 등) 환경을 타겟으로 한 **시뮬레이션 기반 로봇 모방학습(Robot Learning) 검증 파이프라인**으로 완전히 전환되었습니다.

## 1. 프로젝트 한 줄 정의

제한된 환경에서 시뮬레이터(`robosuite`, `MuJoCo`)를 띄워 작은 단위의 Pick & Place 태스크를 세팅하고, 전문가의 조작(Scripted Policy)을 시연 데이터(Demonstrations)로 수집한 뒤, 이를 Behavior Cloning(BC) 방식으로 지도학습하여 로봇의 성공률과 정책 평가 과정을 자동화하는 **Physical AI 실험 기반 프로젝트**입니다.

---

## 2. 핵심 목표 (Robot Learning for Manipulation)

과거 로드맵에서는 "의미적으로 맞으나 기하학적으로 불가능한 경로"를 규칙으로 필터링하는 데 그쳤습니다. 
새로운 고도화 버전에서는 **실제 물리엔진 상의 관측값(Observation)**과 **직접적인 로봇 조작 제어(Action)**를 통해 다음과 같은 전체 머신러닝 학습 사이클을 구현합니다.

```text
Simulation Environment (robosuite)
→ Scripted Policy (Expert)
→ Demonstration Collection (.hdf5)
→ Behavior Cloning (PyTorch MLP)
→ Policy Evaluation (Sim2Skill)
```

---

## 3. 핵심 기술 스택

- **시뮬레이터:** `robosuite` (with `MuJoCo` Engine), `Franka Emika Panda` 로봇 모델
- **인공지능/머신러닝:** `PyTorch`
- **데이터 처리:** `h5py`, `numpy`

---

## 4. 파이프라인 및 실행 가이드

모든 스크립트는 `scripts/` 폴더 내에 순차적으로 구성되어 있습니다. 프로젝트 루트 경로에서 아래 스크립트들을 차례로 실행하면 전체 로봇 학습 과정을 직접 경험할 수 있습니다.

### 4.1. 환경 테스트 (선택 사항)
로봇 시뮬레이션 창이 정상적으로 뜨는지, 초기 무작위 행동이 실행되는지 확인합니다.
```bash
python3 scripts/test_env.py
```

### 4.2. 데모 데이터 수집 (Data Collection)
`ScriptedPickPlacePolicy`가 시뮬레이션 환경 내에서 직접 로봇을 구동하여 대상 물체에 접근하고 집어 올리는 과정을 수행합니다. 이때의 State와 Action 값 500 스텝 분량이 `data/datasets/demo_dataset.hdf5`로 저장됩니다.
```bash
python3 scripts/collect_demonstrations.py
```

### 4.3. 행동 복제 학습 (Behavior Cloning)
수집된 `.hdf5` 파일을 PyTorch Dataset으로 로드하여, State를 보고 최적의 Action을 반환하도록 다층 퍼셉트론(MLP) 기반 모델을 학습합니다. 
```bash
python3 scripts/train_bc.py
```
> 학습이 완료되면 모델 가중치가 `data/models/bc_model.pt` 경로에 저장됩니다.

### 4.4. 학습된 모델 평가 (Policy Evaluation)
하드코딩 규칙을 완전히 제외하고, 오직 앞서 학습된 **인공신경망의 예측값**만으로 로봇을 제어하여 Pick & Place 환경에서의 성공률을 시각적으로 평가합니다.
```bash
python3 scripts/evaluate_policy.py
```

---

## 5. 향후 연구 방향성 (Future Works)

현재 파이프라인은 로봇 조작 학습의 가장 기초적인 "State-based Behavior Cloning"을 다루고 있습니다.
여기서 얻은 파이프라인을 바탕으로, 추후 다음과 같은 확장 실험을 진행할 예정입니다.

1. **Vision-based Policy (이미지 관측):** 1차원 숫자 배열(State) 대신 RGB-D 카메라 이미지를 입력으로 받는 Convolutional/ResNet 모델 기반 정책 학습
2. **Diffusion Policy / Reinforcement Learning:** 단순 모방을 넘어, 노이즈를 제거하는 디퓨전 방식이나 보상을 극대화하는 강화학습(PPO, SAC 등) 도입
3. **Isaac Sim / Isaac Lab 연동:** robosuite에서 충분한 검증 후, 보다 무겁지만 현실적인 NVIDIA Isaac 환경으로 확장 이식
4. **Failure Analysis:** 평가 스크립트 고도화를 통한 충돌(Collision), 목표 미달(Reachability Failure) 등 실패 유형 분류 및 로깅

---
---

# [참고] 이전 버전: ScenePlan MVP (Phase 11 완결)

> MVP: Language-guided task planning with simplified 3D skill-path feasibility checking
> 과거 작성되었던 JSON 파서 및 룰 기반 Reachability/Symbolic 수정 기능의 기록입니다.

## 프로젝트 정의

**ScenePlan**은 사람의 언어 지시와 semantic / 3D scene JSON을 바탕으로 로봇의 **Task Plan**과 **Skill Path Candidate**를 생성하고, 해당 경로가 현재 장면에서 실행 가능한지 간단히 검증하는 MVP 프로젝트입니다.

이 프로젝트의 핵심은 로봇이 “무엇을 해야 하는가”뿐 아니라, 그 행동이 현재 장면에서 **실행 가능한가**를 사전에 확인하는 것입니다.

```text
Language Instruction
→ Semantic / 3D Scene JSON
→ Raw Task Plan
→ Skill Path Candidate
→ Symbolic + Reachability Verification
→ Local Repair Suggestion
→ Demo Result
```

---

## 프로젝트 개요

사용자가 다음과 같이 명령했다고 가정합니다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

로봇은 이 명령을 단순히 `PICK → PLACE`로 바꾸는 것만으로는 충분하지 않습니다. 빨간 컵이 닫힌 서랍 안에 있다면 먼저 서랍을 열어야 하고, 모바일 매니퓰레이터라면 현재 base pose에서 서랍 손잡이나 컵 grasp pose에 팔이 닿는지도 확인해야 합니다.

ScenePlan MVP는 이 문제를 실제 로봇 제어가 아니라 **JSON 기반 장면 표현과 단순 거리 기반 reachability 검증**으로 작게 보여줍니다.

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

예를 들어 아래 Task Plan은 의미적으로는 맞습니다.

```text
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

하지만 실제 실행에서는 현재 base pose에서 drawer handle에 팔이 닿지 않거나, cup grasp pose가 arm reach radius 밖에 있을 수 있습니다. ScenePlan MVP는 이 중 **reachability failure**를 가장 작은 단위로 검출하고, `base_good_1` 같은 수정 후보를 제안하는 데 집중합니다.

---

## 전체 시스템 파이프라인

```text
Human Instruction
→ Semantic / 3D Scene JSON
→ Instruction Parser
→ Raw Task Planner
→ Skill Path Candidate Generator
→ Symbolic + Reachability Verifier
→ Local Repair Suggestion
→ Demo Result
```

| 단계 | 이름 | 설명 |
|---|---|---|
| 1 | Human Instruction | 사용자의 자연어 명령 |
| 2 | Semantic / 3D Scene JSON | object, relation, state, pose, grasp pose, base pose를 포함한 장면 데이터 |
| 3 | Instruction Parser | 명령에서 intent, target, source, destination 추출 |
| 4 | Raw Task Planner | `PICK → PLACE` 형태의 초기 작업 계획 생성 |
| 5 | Skill Path Candidate | 각 step에 waypoint 후보를 연결 |
| 6 | Symbolic Verification | 닫힌 container 내부 object를 바로 PICK하려는 문제 확인 |
| 7 | Reachability Verification | base pose에서 waypoint까지 거리 기반 실행 가능성 확인 |
| 8 | Local Repair Suggestion | `OPEN drawer_1`, `base_good_1` 같은 수정 후보 제안 |
| 9 | Demo Result | MVP 전체 결과를 콘솔에 출력 |

---

## 개발 Phase 계획

| Phase | 단계 | 목표 | 주요 산출물 | 현재 상태 |
|---|---|---|---|---|
| Phase 0 | Project Setup | 프로젝트 기본 구조 생성 | README, data, src, tests, scripts | 완료 |
| Phase 1 | Semantic Scene Data | 초기 scene / skill / instruction JSON 작성 | `scene_001.json`, `basic_skills.json`, `demo_instructions.json` | 완료 |
| Phase 2 | Core Schema | Python dataclass 기반 핵심 자료구조 작성 | scene, instruction, plan, skill, validation schema | 완료 |
| Phase 3 | Scene Understanding | scene JSON 로드 및 object / relation 탐색 | scene_loader, object_finder, relation_finder | 완료 |
| Phase 4 | Instruction Parsing | 한국어 명령을 ParsedInstruction으로 변환 | rule_parser | 완료 |
| Phase 5 | Raw Task Planning | ParsedInstruction과 scene으로 raw task plan 생성 | rule_task_planner | 완료 |
| Phase 6 | 3D Scene Extension | scene JSON에 pose, bbox, grasp pose, base pose 추가 | geometry field 포함 scene JSON | 완료 |
| Phase 7 | MVP Geometry / Skill Path Schema | waypoint와 skill path 표현 추가 | geometry_schema, skill_path_schema | 완료 |
| Phase 8 | Skill Path Candidate | raw/corrected task plan을 waypoint 후보로 변환 | skill_path_generator | 완료 |
| Phase 9 | MVP Feasibility Verification | symbolic issue와 reachability failure 검출 | simple verifier, reachability_checker | 완료 |
| Phase 10 | Local Repair Suggestion | OPEN step과 base pose 수정 후보 제안 | base_pose_repair, suggested_fix | 완료 |
| Phase 11 | Integrated Demo | 전체 MVP 흐름 실행 | `scripts/run_demo.py` | 완료 |

---

## 현재 구현 상태

현재 구현은 **Phase 11: Integrated Demo 단계**까지 완료되어 MVP가 최종 완성되었습니다.

완료된 기능:

- 프로젝트 기본 폴더 구조 생성
- symbolic scene / skill / instruction JSON 작성
- core dataclass schema 작성
- scene JSON loader 구현
- object / relation finder 구현
- rule-based instruction parser 구현
- raw task planner 구현
- 3D Scene 필드 확장 및 Geometry/Skill Path Schema 추가
- Task Plan을 Skill Path Candidate로 변환하는 generator 구현
- Symbolic (missing precondition) 및 Reachability 검증기 구현
- 검증 실패 시 OPEN step 삽입 및 base pose 대안을 탐색하는 Local Repair 로직 구현

현재 raw plan 예시:

```text
Instruction:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

Raw Task Plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

이 raw plan은 의도적으로 `OPEN drawer_1`을 포함하지 않습니다. 이후 MVP verifier에서 missing precondition을 확인하고, repair suggestion으로 `OPEN drawer_1`을 제안하기 위한 기준 plan입니다.

---

## MVP 완료 기준

ScenePlan은 아래 결과가 나오면 MVP 완료로 봅니다.

```text
[Instruction]
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

[Raw Task Plan]
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

[Symbolic Issue]
PICK cup_red_1 cannot be executed because cup_red_1 is inside closed drawer_1.
Suggested symbolic repair: OPEN drawer_1 before PICK cup_red_1.

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

## 프로젝트 한계 및 전제

ScenePlan은 실제 로봇 시스템이 아니라, 연구 아이디어를 작게 검증하기 위한 JSON 기반 MVP입니다.

중요한 전제는 다음과 같습니다.

- semantic / 3D scene JSON은 실제 perception 결과가 아니라 수동으로 정의한 데이터입니다.
- 닫힌 서랍 내부의 object는 외부 카메라로 직접 볼 수 없습니다.
- hidden object 정보는 사용자 instruction, prior semantic map, memory, 또는 simulation metadata로 주어진다고 가정합니다.
- 3D vision의 역할은 hidden object를 투시하는 것이 아니라, container pose, handle pose, base pose, reachability를 검증하는 것입니다.
- 현재 reachability 검증은 실제 inverse kinematics가 아니라 단순 거리 기반 proxy입니다.
- collision, clearance, full trajectory planning, Isaac Sim, ROS2, real robot execution은 이번 MVP 범위에 포함하지 않습니다.

---

## 향후 방향성

ScenePlan은 여기서 고도화를 계속하지 않더라도, 다음 의미를 가집니다.

- 언어 지시가 바로 로봇 실행으로 이어질 수 없다는 문제를 보여줍니다.
- task plan과 skill path를 분리해서 생각하는 구조를 보여줍니다.
- symbolic failure와 geometric failure를 구분하는 출발점을 제공합니다.
- 이후 Robot Learning / Simulation 기반 프로젝트에서 failure 분석, scene representation, skill execution 검증 아이디어로 이어질 수 있습니다.

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

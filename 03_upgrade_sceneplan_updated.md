# 3부. Upgrade — 고도화 방향 정리

> 프로젝트명: `ScenePlan`  
> 목적: MVP 이후 고도화 방향을 정리한다.  
> 핵심 관점: **MVP는 JSON 기반 symbolic + simplified geometry validation으로 작게 증명하고, 이후 Isaac Sim 기반 3D scene validation과 ROS2/실제 로봇 연동으로 확장한다.**

---

# 0. 이 문서의 역할

이 문서는 ScenePlan의 MVP 이후 확장 방향을 정리한 고도화 문서다.

현재 MVP는 다음 흐름을 작게 검증한다.

```text
Human Instruction
→ Semantic / 3D Scene JSON
→ Raw Task Plan
→ Symbolic Plan Verification
→ Self-Correction
→ Skill Path Candidate
→ Geometric Feasibility Verification
→ Suggested Repair
→ Result
```

장기적으로는 다음 흐름으로 확장한다.

```text
Human Instruction
→ Isaac Sim Scene / RGB-D / Object Metadata
→ Semantic + 3D Scene Map
→ Task Plan
→ Skill Chaining
→ Skill Path Generation
→ Feasibility Verification
→ Local Repair / Replanning
→ Isaac Sim Execution Validation
→ Failure Memory
→ ROS2 / Real Robot Extension
```

---

# 1. 현재 MVP의 위치

## 1.1 MVP의 목표

현재 MVP는 아래 문제를 작게 검증한다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

1차 symbolic validation:

```text
raw plan:
1. PICK cup_red_1
2. PLACE cup_red_1 table_1

검증:
PICK 불가능. drawer가 닫혀 있어 cup_red_1이 visible/reachable하지 않음.

corrected plan:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

2차 geometric feasibility validation:

```text
corrected plan은 의미적으로 맞지만,
현재 base_pose에서 drawer handle 또는 cup grasp pose에 arm reachability가 부족할 수 있다.

검증:
base_bad_1에서는 OPEN/PICK waypoint가 unreachable

수정 제안:
base_good_1으로 base pose 조정
또는 approach waypoint 수정
```

---

# 2. 이 프로젝트가 노리는 핵심 오류

이 프로젝트의 핵심 오류는 다음이다.

```text
Semantically Correct but Geometrically Infeasible Skill Path
```

한국어로는 다음과 같다.

```text
의미적으로는 올바르지만 기하학적으로 실행 불가능한 Skill Path
```

예시:

```text
OPEN drawer
PICK cup
PLACE cup on table
```

이 순서는 의미적으로 맞다. 그러나 mobile manipulation에서는 다음 이유로 실패할 수 있다.

```text
1. 현재 base pose에서 drawer handle이 arm workspace 밖에 있다.
2. drawer를 여는 접근 경로가 container edge와 충돌한다.
3. drawer를 연 뒤 cup grasp pose가 gripper clearance를 만족하지 못한다.
4. base를 조금 이동하면 가능한데 plan에는 base adjustment가 없다.
5. target은 의미적으로 맞지만 현재 시야와 arm reachability에서는 물리적으로 접근 불가능하다.
```

---

# 3. 닫힌 container 내부 object retrieval에서 3D vision의 역할

닫힌 container 내부 object는 외부 카메라로 직접 볼 수 없다.

따라서 이 프로젝트에서 hidden object 정보는 다음 방식으로 다룬다.

```text
1. 사용자 instruction
   - "서랍 안에 있는 빨간 컵"이라는 문장이 semantic relation을 제공한다.

2. prior semantic map / memory
   - 이전 관측 또는 기록에서 cup_red_1 inside drawer_1 정보를 갖고 있다.

3. simulation metadata
   - Isaac Sim 단계에서는 평가를 위해 object relation을 metadata로 제공할 수 있다.

4. post-open perception update
   - OPEN 이후에는 RGB-D / object detection으로 실제 object pose를 업데이트한다.
```

3D vision의 역할은 hidden object를 투시하는 것이 아니라 다음을 검증하는 것이다.

```text
- container pose
- handle pose
- obstacle geometry
- base pose candidate
- arm reachability
- collision risk
- gripper clearance
- OPEN 이후 object pose update
```

이 전제를 문서와 발표에서 반드시 명확히 해야 한다.

---

# 4. 고도화 전체 로드맵

```text
MVP 1.0  JSON Symbolic Validation
MVP 1.5  Failure Memory 저장
MVP 2.0  Skill Path Schema 추가
MVP 2.5  Simplified Geometric Feasibility Validation
MVP 3.0  Scene / Instruction / Base Pose Variation Evaluation
MVP 3.5  Isaac Sim Metadata Validation
MVP 4.0  Isaac Sim Execution Validation
MVP 4.5  Learning-based Feasibility Prediction
MVP 5.0  ROS2 / Real Robot Extension
```

핵심 원칙은 다음이다.

```text
1. 먼저 symbolic 구조를 만든다.
2. 그 위에 simplified geometry 검증을 추가한다.
3. failure case를 memory로 저장한다.
4. 여러 base pose와 scene variation으로 평가한다.
5. Isaac Sim metadata를 같은 구조에 연결한다.
6. 이후 learning-based feasibility prediction으로 확장한다.
7. ROS2는 실제 robot skill execution이 필요할 때 연결한다.
```

---

# 5. Level 1 — JSON Symbolic Validation

기존 MVP를 유지한다.

목표:

```text
instruction
→ semantic scene JSON
→ raw task plan
→ precondition check
→ corrected plan
→ symbolic execution
```

검증 오류:

```text
missing_precondition
wrong_order
wrong_target
invalid_destination
unreachable_object
invisible_object
skill_not_available
```

완료 기준:

```text
- scene_001.json을 읽을 수 있다.
- raw plan의 missing OPEN precondition을 탐지할 수 있다.
- OPEN drawer_1을 삽입한 corrected plan을 만들 수 있다.
- corrected plan이 symbolic execution에서 success=true가 된다.
```

---

# 6. Level 2 — Skill Path Schema 추가

목표:

```text
corrected task plan을 실행 가능한 skill path 후보로 표현한다.
```

추가 정보:

```text
base_pose
waypoints
target pose
handle pose
approach direction
tool orientation
```

완료 기준:

```text
- corrected plan에서 raw_skill_path_001을 생성할 수 있다.
- OPEN drawer_1의 waypoint가 drawer handle pose를 참조한다.
- PICK cup_red_1의 waypoint가 cup grasp pose를 참조한다.
```

---

# 7. Level 2.5 — Simplified Geometric Feasibility Validation

목표:

```text
base pose와 arm reachability가 결합되어 실패하는 skill path를 검출한다.
```

검증 항목:

```text
1. reachability
   - base pose에서 waypoint까지의 거리가 arm_reach_radius 안에 있는가?

2. collision risk
   - waypoint가 container edge 또는 obstacle bbox와 너무 가까운가?

3. clearance
   - gripper가 container opening에 들어갈 여유 공간이 있는가?

4. approach direction
   - drawer/box를 열기 위한 접근 방향이 적절한가?
```

완료 기준:

```text
- base_bad_1에서 reachability failure를 탐지한다.
- base_good_1을 suggested repair로 제안한다.
- collision/clearance issue를 최소 1개 이상 생성할 수 있다.
```

---

# 8. Level 3 — Scene / Instruction / Base Pose Variation Evaluation

목표:

```text
단일 scene, 단일 instruction에서 벗어나 여러 조건에서 verifier를 평가한다.
```

Scene variation:

```text
1. drawer closed + bad base pose
2. drawer closed + good base pose
3. drawer open + bad reachability
4. object on table + reachable
5. object inside box + clearance violation
6. target object not visible
7. similar objects ambiguity
```

Instruction variation:

```text
1. 서랍 안에 있는 빨간 컵을 꺼내줘.
2. 책장 안에 있는 물병을 꺼내줘.
3. 상자 안에 있는 물건을 집어줘.
4. 빨간 컵을 테이블 위에 올려줘.
5. 파란 컵 말고 빨간 컵을 집어줘.
```

평가 지표:

```text
- symbolic verification accuracy
- reachability failure detection accuracy
- collision risk detection accuracy
- base pose repair success rate
- local path repair success rate
- unnecessary repair rate
```

---

# 9. Level 3.5 — Isaac Sim Metadata Validation

목표:

```text
Isaac Sim 장면에서 object / container / robot metadata를 추출하고,
이를 semantic + 3D scene JSON으로 변환해 기존 verifier에 연결한다.
```

Isaac Sim의 역할:

```text
- controlled evaluation environment
- 3D scene metadata source
- base pose / container / obstacle 상태 검증 환경
```

추출할 metadata:

```text
container pose
handle pose
object pose
bbox_3d
obstacle geometry
robot base pose
target visibility
```

완료 기준:

```text
- Isaac Sim에서 drawer/container scene screenshot 확보
- scene object list를 JSON으로 정리
- Isaac Sim metadata를 ScenePlan JSON 형식으로 변환
- 기존 symbolic + geometric verifier가 동일하게 동작
```

---

# 10. Level 4 — Isaac Sim Execution Validation

목표:

```text
검증 및 수정된 skill path가 Isaac Sim proxy execution에서 예상 상태 변화와 일치하는지 확인한다.
```

초기에는 full robot trajectory가 아니라 high-level state transition validation으로 시작한다.

검증 예시:

```text
1. drawer_1.state가 closed에서 open으로 바뀌었는가?
2. cup_red_1이 drawer 밖으로 나왔는가?
3. corrected base pose에서 PICK이 reachable로 판정되는가?
4. expected final_state와 observed final_state가 일치하는가?
```

---

# 11. Level 4.5 — Learning-based Feasibility Prediction

중앙대 AI & Robotics Lab 방향으로 확장할 때 중요한 단계다.

목표:

```text
규칙 기반 feasibility checker에서 출발해,
scene/path/failure 데이터를 이용한 learning-based feasibility predictor로 확장한다.
```

입력:

```text
3D scene feature
base pose
target pose
waypoint sequence
container state
previous failure memory
```

출력:

```text
feasible / infeasible
failure type
failure probability
repair hint
```

가능한 모델:

```text
MLP baseline
Graph Neural Network
Transformer encoder for skill path
small multimodal model
```

평가:

```text
- failure type classification accuracy
- feasibility prediction accuracy
- repair suggestion success rate
- repeated failure reduction rate
```

---

# 12. Level 5 — ROS2 / Real Robot Extension

ROS2는 현재 MVP 범위가 아니다.

필요한 시점:

```text
- skill path를 실제 robot skill server로 보내고 싶을 때
- Isaac Sim과 ROS2 bridge를 연결하고 싶을 때
- real robot arm 또는 mobile manipulator와 통신하고 싶을 때
- OPEN, PICK, PLACE를 ROS2 action interface로 실행하고 싶을 때
```

장기 구조:

```text
Task Plan
→ Skill Matcher
→ Skill Path Verifier
→ ROS2 Action Interface
→ Robot Skill Server
→ Execution Result
→ Failure Detector
→ Replanner
```

---

# 13. 연구실별 고도화 포지셔닝

## 13.1 한양대 Robots with Humans Lab 기준

앞에 둘 키워드:

```text
human-friendly robot intelligence
semantic mapping
task and motion planning
skill chaining
grasping
manipulation feasibility
replanning
```

컨택용 설명:

```text
현재는 언어 지시와 semantic/3D scene JSON을 기반으로 task plan과 skill path를 생성하고, 각 step이 scene state와 manipulation feasibility를 만족하는지 검증하는 MVP를 구현하고 있습니다. 이후에는 Isaac Sim 기반 metadata validation과 mobile manipulation feasibility check로 확장하여, 서비스 로봇이 사람의 복잡한 요청을 수행하기 전에 실패 가능성이 높은 skill path를 사전에 수정하는 구조를 연구해보고자 합니다.
```

## 13.2 중앙대 AI & Robotics Lab 기준

앞에 둘 키워드:

```text
robot learning
self-corrective skill planning
failure-aware memory
continual adaptation
learning-based feasibility prediction
multi-modal scene/action representation
```

컨택용 설명:

```text
현재는 rule-based symbolic/geometric verifier로 시작하지만, 장기적으로는 failure memory와 scene/path 데이터를 이용해 learning-based feasibility prediction으로 확장하고자 합니다. 이를 통해 로봇이 반복되는 실패 유형을 기억하고, 유사한 skill path에서 사전에 실패 가능성을 예측하며, self-corrective planning 성능을 개선하는 방향을 고민하고 있습니다.
```

---

# 14. 고도화 후 평가 지표

## 14.1 Planning 지표

```text
raw plan success rate
corrected plan success rate
task plan step accuracy
correct step ordering rate
```

## 14.2 Feasibility 지표

```text
reachability failure detection accuracy
collision risk detection accuracy
clearance violation detection accuracy
base pose infeasibility detection accuracy
tool orientation error detection accuracy
```

## 14.3 Repair 지표

```text
base pose repair success rate
local waypoint repair success rate
unnecessary repair rate
failed repair rate
```

## 14.4 Memory / Learning 지표

```text
repeated failure reduction rate
memory retrieval precision
feasibility prediction accuracy
failure type classification accuracy
```

## 14.5 Isaac Sim Validation 지표

```text
metadata conversion success rate
symbolic final_state vs Isaac Sim final_state match rate
geometric feasibility match rate
execution mismatch count
```

---

# 15. 고도화 후 레포 구조 추가안

```text
ScenePlan/
├── docs/
│   ├── upgrade_plan.md
│   ├── isaac_sim_validation.md
│   ├── ros2_extension.md
│   ├── learning_feasibility_prediction.md
│   └── lab_fit_comparison.md
├── data/
│   ├── isaac_scenes/
│   ├── scene_variations/
│   ├── paths/
│   └── memory/
├── src/
│   ├── feasibility/
│   │   ├── reachability_checker.py
│   │   ├── collision_checker.py
│   │   ├── clearance_checker.py
│   │   └── skill_path_verifier.py
│   ├── correction/
│   │   ├── base_pose_repair.py
│   │   └── local_path_repair.py
│   ├── isaac/
│   │   ├── metadata_exporter.py
│   │   ├── scene_json_converter.py
│   │   └── state_comparator.py
│   ├── learning/
│   │   ├── dataset_builder.py
│   │   ├── feasibility_model.py
│   │   └── train_feasibility_predictor.py
│   └── ros2_extension/
│       ├── action_interface_plan.md
│       └── skill_server_design.md
└── reports/
    ├── demo_report.md
    ├── feasibility_eval_report.md
    └── isaac_validation_report.md
```

---

# 16. 고도화 우선순위

## 1순위 — 반드시

```text
1. 기존 symbolic MVP 완성
2. run_demo.py 실행 결과 확보
3. failure_memory 저장
4. demo_report.md 작성
5. README 정리
```

## 2순위 — 컨택 전에 가능하면

```text
1. scene_001.json에 3D field 추가
2. skill path schema 추가
3. base_bad_1 / base_good_1 비교
4. reachability failure detection 구현
5. raw plan/path vs corrected plan/path 비교표 작성
```

## 3순위 — 있으면 강해짐

```text
1. collision / clearance checker 초안
2. local path repair 초안
3. Isaac Sim scene screenshot
4. Isaac Sim object metadata JSON 예시
5. lab-fit 문서 작성
```

## 4순위 — 장기 확장

```text
1. Isaac Sim execution validation
2. learning-based feasibility prediction
3. ROS2 action interface 설계
4. real robot skill server 연동
```

---

# 17. 최종 정리

ScenePlan의 고도화 방향은 다음 한 문장으로 정리된다.

> JSON 기반 symbolic validation으로 language-guided task planning과 self-correction 구조를 먼저 증명하고, 이후 3D scene state를 이용한 base-arm reachability / collision / clearance 검증으로 확장하여, 의미적으로는 맞지만 기하학적으로 실행 불가능한 mobile manipulation skill path를 사전에 탐지하고 수정하는 구조를 만든다.

중요한 것은 처음부터 모든 것을 구현하는 것이 아니다.

가장 중요한 순서는 다음이다.

```text
1. 작게 증명한다.
2. symbolic failure를 정의한다.
3. symbolic failure를 고친다.
4. skill path를 추가한다.
5. geometric failure를 정의한다.
6. base-arm reachability를 먼저 검증한다.
7. 실패를 memory로 저장한다.
8. Isaac Sim에서 같은 구조를 검증한다.
9. learning-based predictor와 ROS2는 마지막에 연결한다.
```

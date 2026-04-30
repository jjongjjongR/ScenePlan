# 1부. 프로젝트 정의와 기준점

# 0. 프로젝트 이름

## 레포 이름

`ScenePlan`

## 영문 이름

`ScenePlan: 3D Scene-Aware Skill Path Feasibility Verification for Language-Guided Mobile Manipulation`

## 한국어 이름

`언어 지시 기반 모바일 매니퓰레이션을 위한 3D 장면 인식 Skill Path 실행 가능성 검증`

---

# 1. 프로젝트 한 줄 정의

ScenePlan은 사람의 언어 지시를 바탕으로 로봇이 수행해야 할 작업 계획과 Skill Path를 생성한 뒤, 3D 장면 상태·container 상태·base pose·arm reachability·충돌 가능성을 이용해 실행 가능성을 검증하고, 실패 가능성이 높은 경로는 국소 수정하거나 재계획하는 연구형 프로젝트다.

핵심은 “로봇이 무엇을 해야 하는지”만 맞추는 것이 아니라, 그 계획이 실제 장면에서 안전하게 실행 가능한지를 사전에 확인하는 것이다.

---

# 2. 프로젝트를 하는 이유

로봇이 사람의 말을 듣고 실제 환경에서 작업을 수행하려면 단순히 명령을 action sequence로 바꾸는 것만으로는 부족하다.

예를 들어 사람이 다음과 같이 말한다고 하자.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

겉으로 보기에는 단순한 명령이지만, 모바일 매니퓰레이터 입장에서는 여러 단계의 판단이 필요하다.

```text
1. 빨간 컵이 무엇인지 이해해야 한다.
2. 컵이 서랍 안에 있다는 semantic relation을 알아야 한다.
3. 서랍이 닫혀 있다면 먼저 열어야 한다.
4. 현재 base pose에서 서랍 손잡이에 접근 가능한지 확인해야 한다.
5. 서랍을 열 때 팔이 책장/서랍장 모서리와 충돌하지 않는지 확인해야 한다.
6. 서랍을 연 뒤 컵이 실제로 보이는지 다시 확인해야 한다.
7. 컵을 집을 때 arm reachability와 gripper clearance가 충분한지 확인해야 한다.
8. 실패 가능성이 높으면 base pose 조정, 접근 방향 변경, OPEN step 삽입, 재계획이 필요하다.
```

따라서 이 프로젝트의 핵심은 다음 흐름을 작게 증명하는 것이다.

```text
언어 지시
→ semantic / 3D scene state
→ task plan
→ skill path candidate
→ feasibility verification
→ local repair / replanning
→ symbolic or simulated validation
```

처음부터 실제 로봇 제어 전체를 구현하지 않는다. 먼저 JSON 기반 scene과 simplified geometry에서 핵심 구조를 검증하고, 이후 Isaac Sim metadata validation과 ROS2/real robot extension으로 확장한다.

---

# 3. 핵심 문제 정의

## 3.1 해결하려는 문제

LLM, VLA-style planner, 또는 rule-based planner가 만든 계획은 의미적으로는 맞아 보여도 실제 로봇이 수행하기에는 실패할 수 있다.

예시:

```text
명령:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

의미적으로 맞아 보이는 plan:
1. OPEN drawer_1
2. PICK cup_red_1
3. PLACE cup_red_1 table_1
```

이 plan은 task sequence 관점에서는 맞다. 하지만 실제 mobile manipulation에서는 여전히 실패할 수 있다.

가능한 실패 이유:

```text
- 현재 base_pose에서 drawer_1 손잡이에 팔이 닿지 않는다.
- drawer_1을 열기 위한 접근 방향이 잘못되어 팔이 책장/서랍장 모서리와 충돌한다.
- drawer_1을 열어도 cup_red_1이 gripper clearance 안에 들어오지 않는다.
- 컵이 의미적으로는 target이지만, 실제 3D 위치는 현재 arm workspace 밖에 있다.
- base를 조금 옮기면 가능하지만, 현재 plan에는 base adjustment가 없다.
```

따라서 본 프로젝트의 핵심 오류는 다음이다.

```text
Semantically Correct but Geometrically Infeasible Skill Path
```

한국어로는 다음과 같다.

```text
의미적으로는 맞지만 기하학적으로 실행 불가능한 Skill Path
```

---

# 4. 중요한 전제: 닫힌 container 내부 물체를 3D Vision으로 직접 볼 수는 없다

이 프로젝트에서 “닫힌 container 내부 object retrieval”을 다룬다고 해서, 3D vision이 닫힌 서랍 안의 물체를 직접 본다는 뜻은 아니다.

닫힌 서랍이나 책장 안 물체는 외부 카메라 또는 RGB-D 센서로 직접 관측할 수 없다.

따라서 이 프로젝트는 hidden object를 다음 중 하나의 정보로 다룬다.

```text
1. 사용자 명령 또는 prior semantic map
   - “서랍 안에 있는 빨간 컵”이라는 지시 자체가 cup_red_1 inside drawer_1 관계를 제공한다.

2. 기존 memory 또는 inventory
   - 이전 관측에서 cup_red_1이 drawer_1 안에 있었다는 기록이 있다.

3. simulation metadata
   - Isaac Sim 단계에서는 controlled evaluation을 위해 object relation을 metadata로 제공할 수 있다.

4. open 이후 perception update
   - OPEN drawer_1 이후에는 RGB-D / object detection으로 실제 컵의 pose와 visibility를 다시 업데이트한다.
```

즉, 3D vision의 1차 역할은 “닫힌 서랍 안 물체를 투시하는 것”이 아니다.

3D vision은 주로 아래를 검증한다.

```text
- container의 3D 위치와 크기
- drawer handle 또는 door 접근 위치
- base pose 후보
- arm reachability
- collision risk
- gripper clearance
- OPEN 이후 target object pose update
```

따라서 본 연구는 hidden object retrieval을 “prior semantic relation + 3D feasibility verification + post-open perception update” 문제로 본다.

---

# 5. 프로젝트 핵심 질문

## 5.1 메인 질문

```text
언어 지시와 semantic / 3D scene state가 주어졌을 때,
로봇이 생성한 skill path가 실제 mobile manipulation 환경에서 실행 가능한지
실행 전에 검증하고, 실패 가능성이 높은 구간을 수정할 수 있는가?
```

## 5.2 세부 질문

```text
1. 언어 지시에서 target object, container, destination, task intent를 추출할 수 있는가?
2. semantic scene map에서 object-container relation과 container state를 읽을 수 있는가?
3. task planner가 OPEN, PICK, PLACE 같은 skill sequence를 만들 수 있는가?
4. skill path candidate가 base pose, target pose, waypoint를 포함하도록 표현될 수 있는가?
5. verifier가 missing precondition, wrong order 같은 symbolic failure를 탐지할 수 있는가?
6. verifier가 reachability failure, collision risk, clearance violation 같은 geometric failure를 탐지할 수 있는가?
7. local repair가 base adjustment, waypoint shift, approach direction change를 제안할 수 있는가?
8. corrected plan/path가 symbolic execution 또는 Isaac Sim validation에서 더 높은 성공 가능성을 보이는가?
```

---

# 6. 프로젝트에서 사용하는 핵심 개념

## 6.1 Human Instruction

사람이 자연어로 내리는 명령이다.

예시:

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
책장 안에 있는 물병을 꺼내줘.
상자 안에 있는 물건을 집어줘.
테이블 위 컵을 싱크대 옆에 놓아줘.
```

현재 MVP에서는 한국어 명령 3~5개만 지원한다. 이후 LLM parser로 확장할 수 있다.

## 6.2 Semantic Scene Map

JSON으로 표현된 장면의 의미 구조다.

포함 정보:

```text
- 장소: table, drawer, shelf, cabinet, box
- 물체: cup, bottle, bowl, book
- 상태: open, closed, visible, reachable, graspable
- 관계: inside, on, near, blocked_by
- 로봇 상태: holding, gripper_state, current_location
```

## 6.3 3D Scene State

Semantic Scene Map에 기하 정보를 추가한 구조다.

포함 정보:

```text
- object pose
- container pose
- bbox_3d
- obstacle geometry
- base pose candidate
- target pose
- clearance
- approximate reachability score
```

MVP에서는 실제 RGB-D reconstruction이 아니라 수동 JSON 또는 Isaac Sim metadata로 시작한다.

## 6.4 Task Plan

로봇이 수행해야 하는 high-level 작업 순서다.

예시:

```text
OPEN drawer_1
PICK cup_red_1
PLACE cup_red_1 table_1
```

## 6.5 Skill Path

Task Plan의 각 skill을 실행하기 위한 base pose와 waypoint 후보를 포함한 구조다.

예시:

```json
{
  "skill_id": "pick_cup_red_1",
  "action": "PICK",
  "target": "cup_red_1",
  "base_pose": [0.55, -0.20, 1.57],
  "waypoints": [
    {
      "index": 0,
      "position": [0.40, 0.10, 0.70],
      "orientation": [0, 0, 0, 1],
      "tool_direction": [0, 0, -1]
    }
  ]
}
```

## 6.6 Feasibility Verification

생성된 task plan과 skill path가 현재 scene에서 실행 가능한지 검사하는 단계다.

검사 항목:

```text
1. symbolic precondition
   - container가 closed인데 내부 물체를 PICK하려고 하지 않는가?
   - robot이 아무것도 들고 있지 않은데 PLACE하려고 하지 않는가?

2. geometric feasibility
   - target이 현재 base pose에서 arm workspace 안에 있는가?
   - waypoint가 장애물 또는 container edge와 충돌하지 않는가?
   - gripper/tool이 들어갈 clearance가 충분한가?
   - tool orientation이 작업 조건과 맞는가?
```

## 6.7 Local Repair

검증 실패가 발생했을 때 plan 또는 path를 수정하는 단계다.

예시:

```text
symbolic repair:
PICK 이전에 OPEN drawer_1 삽입

geometric repair:
base pose를 왼쪽으로 20cm 조정
접근 방향을 drawer 정면 기준으로 재설정
collision risk waypoint를 surface normal 방향으로 이동
```

## 6.8 Failure Memory

반복되는 실패 유형을 저장하는 memory다.

MVP에서는 JSONL 파일로 저장한다.

예시:

```json
{
  "memory_id": "fail_001",
  "instruction_pattern": "retrieve object inside closed drawer",
  "failure_type": "base_arm_reachability_failure",
  "bad_path": ["base_pose=[0.2, 0.0, 0.0]", "PICK cup_red_1"],
  "corrected_path": ["base_pose=[0.55, -0.20, 1.57]", "OPEN drawer_1", "PICK cup_red_1"],
  "lesson": "For closed drawer retrieval, choose a base pose that allows both handle opening and target grasping."
}
```

---

# 7. 포함 범위

이 프로젝트에 포함되는 것은 아래와 같다.

```text
1. JSON 기반 semantic scene map
2. 3D scene state를 표현하기 위한 단순 geometry field
3. 한국어 instruction 예시 3~5개
4. rule-based instruction parser
5. rule-based task planner
6. task plan schema
7. skill library
8. skill path schema
9. symbolic precondition verifier
10. simple reachability checker
11. simple collision / clearance checker
12. local repair rule
13. symbolic executor
14. failure memory 저장
15. raw plan/path vs corrected plan/path 비교
16. 간단한 평가 지표
17. 데모 스크립트
```

---

# 8. 제외 범위

아래는 지금 하지 않는다.

```text
1. 실제 로봇 하드웨어 제어
2. 실제 gripper 제어
3. full trajectory planning 알고리즘 구현
4. MoveIt / cuRobo 직접 연동
5. 강화학습
6. imitation learning 학습
7. OpenVLA fine-tuning
8. 대규모 LLM agent 시스템
9. 실제 SLAM 기반 semantic map 생성
10. 대규모 dataset 구축
11. Isaac Sim 로봇 제어 자동화
12. ROS2 실시간 연동
```

단, 나중에 확장할 수 있도록 구조는 열어둔다.

---

# 9. 시스템 전체 흐름

```text
[1] Human Instruction
        ↓
[2] Instruction Parser
        ↓
[3] Semantic / 3D Scene Loader
        ↓
[4] Task Planner
        ↓
[5] Skill Matcher
        ↓
[6] Skill Path Candidate Generator
        ↓
[7] Feasibility Verifier
        ↓
[8] Local Repair / Self-Correction
        ↓
[9] Symbolic or Simulated Execution
        ↓
[10] Failure Memory
        ↓
[11] Evaluation Result
```

---

# 10. MVP 기준

## 10.1 MVP 1차 목표

MVP 1차는 기존 symbolic demo를 유지한다.

```text
scene_001.json을 읽는다.
instruction 하나를 입력한다.
raw plan을 만든다.
raw plan의 missing OPEN precondition을 검증한다.
corrected plan을 만든다.
corrected plan을 symbolic execution한다.
```

## 10.2 MVP 2차 목표

MVP 2차는 3D feasibility field를 추가한다.

```text
base_pose 후보를 읽는다.
target/container pose를 읽는다.
simple reachability score를 계산한다.
collision/clearance risk를 단순 threshold로 검증한다.
bad base pose 또는 bad waypoint를 탐지한다.
수정 후보를 제안한다.
```

---

# 11. 실패 유형 정의

## 11.1 symbolic failure

```text
missing_precondition
wrong_order
wrong_target
unreachable_object
invisible_object
invalid_destination
skill_not_available
```

## 11.2 geometric failure

```text
base_pose_infeasible
arm_reachability_failure
collision_risk
clearance_violation
tool_orientation_error
approach_direction_error
```

---

# 12. 최종 목표 이미지

```text
사람 명령:
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.

장면 이해:
cup_red_1 is inside drawer_1
drawer_1 is closed
drawer_1 pose = [0.50, 0.20, 0.70]
robot base_pose = [0.10, -0.40, 0.00]

초기 plan:
PICK cup_red_1
PLACE cup_red_1 table_1

symbolic 검증:
PICK 실패
이유: drawer가 닫혀 있어 cup이 visible/reachable하지 않음

수정 plan:
OPEN drawer_1
PICK cup_red_1
PLACE cup_red_1 table_1

geometric 검증:
현재 base pose에서는 drawer handle과 cup grasp pose에 reachability가 낮음
drawer edge와 approach waypoint 충돌 위험 있음

local repair:
base pose를 drawer 정면으로 조정
OPEN 접근 waypoint 수정
PICK 접근 방향 재계산

최종 결과:
symbolic condition과 simplified geometric feasibility를 모두 만족하는 skill path 출력
```

이 한 흐름을 안정적으로 보여주는 것이 1차 목표다.

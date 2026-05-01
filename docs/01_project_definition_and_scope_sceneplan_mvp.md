# 1부. 프로젝트 정의와 기준점 — MVP 기준

## 0. 프로젝트 이름

- 레포 이름: `ScenePlan`
- 영문 이름: `ScenePlan: MVP for 3D Scene-Aware Skill Path Feasibility Checking`
- 한국어 이름: `언어 지시 기반 로봇 작업 계획과 Skill Path 실행 가능성 검증 MVP`

---

## 1. 프로젝트 한 줄 정의

ScenePlan은 사람의 언어 지시와 semantic / 3D scene JSON을 바탕으로 로봇의 초기 Task Plan과 Skill Path Candidate를 만들고, 해당 경로가 현재 장면에서 실행 가능한지 **symbolic condition**과 **단순 reachability** 기준으로 확인하는 MVP 프로젝트다.

핵심은 완성형 로봇 시스템을 만드는 것이 아니라, 다음 문제를 작게 보여주는 것이다.

```text
의미적으로는 맞아 보이는 로봇 계획도
실제 base pose와 waypoint 조건에서는 실행 불가능할 수 있다.
```

---

## 2. 프로젝트를 하는 이유

사람이 다음과 같이 말한다고 하자.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

단순 planner는 다음 plan을 만들 수 있다.

```text
1. PICK cup_red_1
2. PLACE cup_red_1 table_1
```

하지만 이 plan은 현재 scene에서는 바로 실행할 수 없다.

```text
- cup_red_1은 drawer_1 안에 있다.
- drawer_1은 closed 상태다.
- cup_red_1은 visible=false, reachable=false다.
```

또한 `OPEN → PICK → PLACE` 순서로 고쳐도, mobile manipulator에서는 현재 base pose에서 drawer handle 또는 cup grasp pose까지 팔이 닿지 않을 수 있다.

ScenePlan MVP는 이 문제를 실제 로봇 제어가 아니라, JSON 기반 scene과 단순 geometry 계산으로 작게 검증한다.

---

## 3. 핵심 문제 정의

이 프로젝트가 다루는 핵심 문제는 다음이다.

```text
Semantically Correct but Geometrically Infeasible Skill Path
```

한국어로는 다음과 같다.

```text
의미적으로는 맞지만 기하학적으로 실행 불가능한 Skill Path
```

MVP에서는 이 중에서도 가장 단순한 형태만 다룬다.

```text
1. symbolic failure
   - closed drawer 안의 object를 바로 PICK하려는 문제

2. reachability failure
   - base pose에서 waypoint까지의 거리가 arm reach radius보다 먼 문제
```

---

## 4. MVP 핵심 질문

```text
언어 지시와 semantic / 3D scene JSON이 주어졌을 때,
초기 task plan과 skill path candidate를 만들고,
닫힌 container precondition 문제와 base-arm reachability 문제를
실행 전에 간단히 탐지할 수 있는가?
```

---

## 5. MVP 시스템 흐름

```text
Human Instruction
→ Semantic / 3D Scene JSON
→ Instruction Parser
→ Raw Task Planner
→ Skill Path Candidate
→ Symbolic + Reachability Verification
→ Local Repair Suggestion
→ Demo Result
```

---

## 6. 핵심 개념

### 6.1 Human Instruction

사용자가 자연어로 내리는 명령이다.

```text
서랍 안에 있는 빨간 컵을 테이블 위에 올려줘.
```

### 6.2 Semantic Scene JSON

물체, 장소, 관계, 상태를 표현한다.

```text
cup_red_1 is inside drawer_1
drawer_1 is closed
table_1 is reachable
```

### 6.3 3D Scene JSON

semantic scene에 pose, bbox, grasp pose, base pose 같은 단순 geometry field를 추가한 구조다.

```text
drawer_1.handle_pose
cup_red_1.grasp_pose
table_1.place_pose
robot.base_pose
robot.arm_reach_radius
```

### 6.4 Task Plan

로봇이 해야 할 high-level 작업 순서다.

```text
PICK cup_red_1
PLACE cup_red_1 table_1
```

### 6.5 Skill Path Candidate

Task Plan의 각 step에 waypoint 후보를 연결한 구조다.

```text
PICK cup_red_1 → cup_red_1.grasp_pose
PLACE cup_red_1 table_1 → table_1.place_pose
```

### 6.6 Local Repair Suggestion

MVP에서는 실제 trajectory optimization을 하지 않고, 수정 후보만 제안한다.

```text
symbolic repair: OPEN drawer_1 before PICK
geometric repair: use base_good_1
```

---

## 7. 포함 범위

```text
- JSON 기반 semantic scene
- 3D field가 포함된 scene JSON
- rule-based instruction parser
- rule-based raw task planner
- skill path schema
- simple reachability checker
- base pose repair suggestion
- MVP run_demo.py
```

---

## 8. 제외 범위

```text
- 실제 로봇 제어
- 실제 gripper 제어
- full trajectory planning
- inverse kinematics
- 실제 collision checker
- Isaac Sim 실행 자동화
- ROS2 연동
- learning-based feasibility prediction
- 대규모 VLA fine-tuning
```

---

## 9. MVP 완료 기준

ScenePlan MVP는 다음 결과가 나오면 완료로 본다.

```text
1. instruction을 ParsedInstruction으로 변환한다.
2. scene JSON에서 target object와 destination을 찾는다.
3. raw task plan을 생성한다.
4. closed drawer로 인한 symbolic issue를 출력한다.
5. skill path candidate를 생성한다.
6. base_bad_1에서 reachability failure를 탐지한다.
7. base_good_1을 suggested repair로 제안한다.
8. run_demo.py에서 전체 결과를 출력한다.
```

---

## 10. 중요한 전제와 한계

```text
- 닫힌 서랍 안의 object는 외부 카메라로 직접 관측할 수 없다.
- hidden object 정보는 instruction, prior map, memory, simulation metadata로 주어진다고 가정한다.
- 3D vision은 hidden object를 투시하는 것이 아니라 container pose, handle pose, base pose, reachability를 검증하는 역할이다.
- 현재 geometry 검증은 실제 IK가 아니라 단순 거리 기반 proxy다.
- 이 프로젝트는 연구 아이디어를 작게 보여주는 MVP이며, 완성형 로봇 시스템이 아니다.
```

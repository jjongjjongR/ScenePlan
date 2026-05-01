# 3부. MVP 한계와 향후 방향성

> 이 문서는 ScenePlan을 고도화하기 위한 실행 계획서가 아니라, MVP의 한계와 연구적 의의를 정리한 문서다.

---

## 0. 현재 위치

ScenePlan은 MVP 기준으로 다음 흐름을 작게 보여주는 프로젝트다.

```text
Human Instruction
→ Semantic / 3D Scene JSON
→ Raw Task Plan
→ Skill Path Candidate
→ Symbolic + Reachability Verification
→ Suggested Repair
→ Result
```

고도화 구현은 이번 프로젝트 범위에 포함하지 않는다.

---

## 1. MVP가 보여주는 것

ScenePlan MVP가 보여주는 핵심은 다음이다.

```text
언어 지시로 생성된 로봇 plan은 의미적으로 맞아 보여도,
현재 scene state와 base pose 조건에서는 실행 불가능할 수 있다.
```

MVP는 이 문제를 두 가지 failure로 단순화한다.

```text
1. symbolic failure
   - closed drawer 안 object를 바로 PICK하려는 문제

2. reachability failure
   - 현재 base pose에서 waypoint까지 팔이 닿지 않는 문제
```

---

## 2. MVP에서 의도적으로 하지 않는 것

```text
- 실제 perception pipeline
- 실제 inverse kinematics
- 실제 collision checker
- clearance 계산의 정교화
- trajectory optimization
- Isaac Sim 자동 실행
- ROS2 연동
- real robot execution
- learning-based feasibility prediction
```

이것들은 이번 프로젝트에서 구현하지 않는다.

---

## 3. 중요한 전제

닫힌 drawer 안의 object는 외부 카메라로 직접 볼 수 없다.

따라서 hidden object 정보는 다음 중 하나로 주어진다고 본다.

```text
1. 사용자 instruction
2. prior semantic map
3. memory / inventory
4. simulation metadata
5. OPEN 이후 perception update
```

즉, 3D vision의 역할은 hidden object를 투시하는 것이 아니다.

3D vision 또는 3D scene 정보의 역할은 다음에 가깝다.

```text
- container pose 확인
- handle pose 확인
- object pose update
- base pose 후보 확인
- arm reachability 계산
- collision / clearance 검증의 기반 제공
```

---

## 4. MVP의 한계

```text
1. scene JSON은 수동으로 정의한다.
2. hidden object pose는 실제 관측값이 아니라 instruction / memory / metadata 기반 가정이다.
3. reachability는 실제 IK가 아니라 2D 거리 기반 proxy다.
4. collision과 clearance는 MVP에서 구현하지 않거나, 후속 설명으로만 남긴다.
5. repair는 실제 motion re-planning이 아니라 suggested repair 수준이다.
6. run_demo.py는 연구 아이디어를 보여주는 prototype demo다.
```

---

## 5. 이 MVP의 의의

ScenePlan은 작은 MVP지만 다음 의미를 가진다.

```text
1. task plan과 skill path를 분리해서 생각하는 구조를 만든다.
2. symbolic failure와 geometric failure를 구분한다.
3. language-guided manipulation에서 실행 전 검증이 왜 필요한지 보여준다.
4. 이후 Robot Learning 프로젝트에서 failure type, scene representation, repair hint 설계로 이어질 수 있다.
```

특히 새 방향인 Robot Learning for Manipulation 관점에서는, ScenePlan의 결과를 다음처럼 재사용할 수 있다.

```text
- 실패 유형 정의
- scene state representation 설계
- skill-level task decomposition
- simulation experiment의 success / failure logging 기준
```

---

## 6. 향후 방향성: 구현하지 않지만 남겨둘 아이디어

ScenePlan 자체를 더 고도화하지는 않더라도, 아래 방향은 후속 연구/프로젝트 아이디어로 남긴다.

### 6.1 Isaac Sim Metadata Validation

```text
Isaac Sim 장면에서 object pose, handle pose, base pose, bbox 정보를 추출해
ScenePlan JSON 형식으로 변환할 수 있다.
```

### 6.2 Collision / Clearance Checker

```text
bbox 기반으로 waypoint와 container edge 사이의 거리를 계산해
collision risk 또는 clearance violation을 더 정교하게 다룰 수 있다.
```

### 6.3 Learning-based Feasibility Prediction

```text
rule-based checker로 만든 failure 데이터를 모아,
나중에는 scene/path feature를 입력으로 feasible / infeasible을 예측하는 모델을 학습할 수 있다.
```

### 6.4 Robot Learning 프로젝트와 연결

```text
ScenePlan의 verification 구조를 Robot Learning 실험의 failure analyzer로 활용할 수 있다.
예를 들어 policy rollout이 실패했을 때, 실패 원인을 reachability, collision, wrong order 등으로 기록하는 방식이다.
```

---

## 7. 최종 정리

ScenePlan은 최종 연구 프로젝트가 아니라, 다음 방향으로 넘어가기 위한 작은 연결 프로젝트다.

```text
Language-guided task planning
→ Skill path feasibility checking
→ Failure type definition
→ Robot Learning for Manipulation 실험 설계로 연결
```

따라서 ScenePlan은 MVP 수준에서 마무리하고, 이후 메인 프로젝트는 simulation 기반 Robot Learning 실험으로 전환한다.

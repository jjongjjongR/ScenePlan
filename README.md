# Markdown 문서 구성

이 폴더는 `Semantic Map-Guided Robot Task Planner` 프로젝트를 다른 채팅, Codex, 개발 환경에 그대로 넘겨도 이어서 진행할 수 있도록 만든 기준 문서다.

## 문서 구성

1. `01_project_definition_and_scope.md`
   - 프로젝트 목적
   - 문제 정의
   - 핵심 개념
   - 포함 범위 / 제외 범위
   - 전체 시스템 흐름
   - 데이터 기준
   - 실패 유형
   - MVP 기준

2. `02_implementation_design_and_steps.md`
   - 레포 구조
   - 모듈별 구현 설계
   - JSON 스키마
   - 핵심 알고리즘
   - 단계별 개발 순서
   - Codex 작업 지시문
   - 테스트 기준
   - 완료 기준
   
3. `03_upgrade.md`
   - Failure Memory / Memory-Aware Replanning
   - Scene / Instruction Variation Evaluation
   - Isaac Sim Metadata Validation
   - Isaac Sim Execution Validation
   - ROS2 / Real Robot 장기 확장 방향

## 프로젝트 한 줄 정의

사람의 언어 지시와 semantic scene map을 입력받아 로봇의 task plan을 생성하고, 각 step이 현재 장면 상태와 skill 조건을 만족하는지 검증한 뒤, 실행 불가능한 계획은 수정하거나 재계획하는 JSON 기반 symbolic robot planning 프로젝트다.

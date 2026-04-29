# test_rule_parser.py

# 2026-04-29 수정: 테스트 파일을 직접 실행해도 프로젝트 루트의 src 패키지를 찾을 수 있도록 경로를 추가합니다.
import sys
from pathlib import Path

# 2026-04-29 수정: tests 폴더의 부모 폴더, 즉 프로젝트 루트를 import 경로에 추가합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.instruction.rule_parser import parse_instruction


def test_parse_retrieve_and_place_instruction() -> None:
    instruction = "서랍 안에 있는 빨간 컵을 테이블 위에 올려줘."

    parsed = parse_instruction(instruction)

    assert parsed.raw_text == instruction
    assert parsed.intent == "retrieve_and_place"
    assert parsed.target_category == "cup"
    assert parsed.target_color == "red"
    assert parsed.source_relation == "inside"
    assert parsed.source_place_type == "drawer"
    assert parsed.destination_type == "table"


def test_parse_simple_pick_instruction() -> None:
    instruction = "파란 컵을 집어줘."

    parsed = parse_instruction(instruction)

    assert parsed.raw_text == instruction
    assert parsed.intent == "retrieve"
    assert parsed.target_category == "cup"
    assert parsed.target_color == "blue"
    assert parsed.source_relation is None
    assert parsed.source_place_type is None
    assert parsed.destination_type is None


if __name__ == "__main__":
    test_parse_retrieve_and_place_instruction()
    test_parse_simple_pick_instruction()
    print("rule_parser tests passed")
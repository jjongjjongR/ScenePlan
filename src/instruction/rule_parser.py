# src/instruction/rule_parser.py

# 2026-04-29 신규: 한국어 명령을 ParsedInstruction으로 바꾸는 rule-based parser입니다.
from typing import Optional

from src.schemas.instruction_schema import ParsedInstruction


def parse_instruction(text: str) -> ParsedInstruction:
    """
    한국어 자연어 명령을 ParsedInstruction으로 변환합니다.

    Args:
        text: 사람이 입력한 명령 문장

    Returns:
        ParsedInstruction 객체
    """

    normalized_text = _normalize_text(text)

    return ParsedInstruction(
        raw_text=text,
        intent=_parse_intent(normalized_text),
        target_category=_parse_target_category(normalized_text),
        target_color=_parse_target_color(normalized_text),
        source_relation=_parse_source_relation(normalized_text),
        source_place_type=_parse_source_place_type(normalized_text),
        destination_type=_parse_destination_type(normalized_text),
    )


def _normalize_text(text: str) -> str:
    """
    문장 비교를 쉽게 하기 위해 공백을 정리합니다.
    """

    return text.strip().replace(" ", "")


def _parse_intent(text: str) -> str:
    """
    명령의 의도를 파악합니다.
    """

    retrieve_and_place_keywords = ["올려줘", "올려", "놓아줘", "놓아", "놔줘", "놔"]
    retrieve_keywords = ["집어줘", "집어", "꺼내줘", "꺼내", "잡아줘", "잡아"]

    for keyword in retrieve_and_place_keywords:
        if keyword in text:
            return "retrieve_and_place"

    for keyword in retrieve_keywords:
        if keyword in text:
            return "retrieve"

    return "unknown"


def _parse_target_category(text: str) -> Optional[str]:
    """
    명령에서 대상 물체의 종류를 찾습니다.
    """

    if "컵" in text:
        return "cup"

    if "그릇" in text:
        return "bowl"

    if "책" in text:
        return "book"

    if "병" in text:
        return "bottle"

    return None


def _parse_target_color(text: str) -> Optional[str]:
    """
    명령에서 대상 물체의 색상을 찾습니다.
    """

    if "빨간" in text or "빨강" in text:
        return "red"

    if "파란" in text or "파랑" in text:
        return "blue"

    if "초록" in text or "초록색" in text:
        return "green"

    if "노란" in text or "노랑" in text:
        return "yellow"

    return None


def _parse_source_relation(text: str) -> Optional[str]:
    """
    대상 물체가 어디에서 출발하는지 관계를 찾습니다.
    """

    if "서랍안" in text or "상자안" in text or "안에있는" in text:
        return "inside"

    return None


def _parse_source_place_type(text: str) -> Optional[str]:
    """
    대상 물체가 들어 있는 장소나 구조물의 type을 찾습니다.
    """

    if "서랍" in text:
        return "drawer"

    if "상자" in text:
        return "box"

    return None


def _parse_destination_type(text: str) -> Optional[str]:
    """
    물체를 놓을 목적지 type을 찾습니다.
    """

    if "테이블위" in text or "테이블에" in text or "테이블" in text:
        return "table"

    if "싱크대위" in text or "싱크대에" in text or "싱크대" in text:
        return "sink"

    if "선반위" in text or "선반에" in text or "선반" in text:
        return "shelf"

    return None
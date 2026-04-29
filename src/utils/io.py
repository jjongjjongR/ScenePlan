# src/utils/io.py

# 2026-04-29 신규: 프로젝트 전체에서 사용할 JSON 입출력 유틸 함수입니다.
import json
from pathlib import Path
from typing import Any, Dict


def read_json(path: str) -> Dict[str, Any]:
    """
    JSON 파일을 읽어서 Python dict로 반환합니다.

    Args:
        path: 읽을 JSON 파일 경로

    Returns:
        JSON 내용을 담은 dict

    Raises:
        FileNotFoundError: 파일이 없을 때 발생
        ValueError: JSON 최상위 구조가 dict가 아닐 때 발생
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")

    return data


def write_json(path: str, data: Dict[str, Any]) -> None:
    """
    Python dict를 JSON 파일로 저장합니다.

    Args:
        path: 저장할 JSON 파일 경로
        data: 저장할 dict 데이터
    """

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    """
    하나의 dict record를 JSONL 파일에 한 줄로 추가합니다.

    JSONL은 JSON Lines 형식입니다.
    한 줄에 JSON 객체 하나씩 저장하는 방식입니다.

    Args:
        path: 저장할 JSONL 파일 경로
        record: 추가할 dict 데이터
    """

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("a", encoding="utf-8") as file:
        json_line = json.dumps(record, ensure_ascii=False)
        file.write(json_line + "\n")
#!/usr/bin/env python3
"""
이벤트 파일을 새로운 Cascade 구조로 변환하는 스크립트
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def add_cascade_structure(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    이벤트에 cascade 구조를 추가합니다.
    """
    # choices에 cascade_events 필드가 없으면 추가
    if "choices" in event:
        for choice in event["choices"]:
            if "cascade_events" not in choice:
                choice["cascade_events"] = []

    # 이벤트 레벨에 cascade_events 필드가 없으면 추가
    if "cascade_events" not in event:
        event["cascade_events"] = []

    # effects에 message 필드가 없으면 추가
    if "effects" in event:
        for effect in event["effects"]:
            if "message" not in effect:
                metric_name = effect["metric"].lower()
                value = float(effect["formula"].split("+")[-1].strip())
                effect["message"] = f"{metric_name}이(가) {'증가' if value >= 0 else '감소'}했습니다."

    return event


def process_event_file(file_path: Path) -> None:
    """
    단일 이벤트 파일을 처리합니다.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 이벤트 데이터가 직접 있는 경우
        if isinstance(data, dict) and "id" in data:
            data = add_cascade_structure(data)
        # 이벤트 컨테이너인 경우
        elif isinstance(data, dict) and "events" in data:
            data["events"] = [add_cascade_structure(event) for event in data["events"]]

        # 파일 백업
        backup_path = file_path.with_suffix(".json.bak")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 원본 파일 업데이트
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 변환 완료: {file_path}")

    except Exception as e:
        print(f"❌ 오류 발생 ({file_path}): {str(e)}")


def process_directory(directory: Path) -> None:
    """
    디렉토리 내의 모든 이벤트 파일을 처리합니다.
    """
    if not directory.exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {directory}")
        return

    for item in directory.glob("**/*.json"):
        if item.is_file() and not item.name.endswith(".bak"):
            process_event_file(item)


def main() -> None:
    """메인 함수"""
    base_dir = Path("data/events_bank")
    categories = ["daily_routine", "crisis_events", "opportunity"]

    for category in categories:
        category_dir = base_dir / category
        print(f"\n📁 {category} 디렉토리 처리 중...")
        process_directory(category_dir)


if __name__ == "__main__":
    main() 
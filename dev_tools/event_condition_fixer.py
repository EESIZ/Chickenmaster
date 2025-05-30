#!/usr/bin/env python3
"""
파일: dev_tools/event_condition_fixer.py
설명: 이벤트 조건 수정 도구
작성자: Manus
날짜: 2025-05-27
"""

import argparse
import json
from typing import Any, ClassVar


class EventConditionFixer:
    """이벤트 조건 수정 도구"""

    # 조건 매핑 정의
    CONDITION_MAPPING: ClassVar[dict[str, str]] = {
        "equal": "equal",
        "not_equal": "not_equal",
        "greater_than": "greater_than",
        "less_than": "less_than",
        "greater_than_or_equal": "greater_than_or_equal",
        "less_than_or_equal": "less_than_or_equal",
        "contains": "contains",
        "not_contains": "not_contains",
        # 이전 버전 호환성
        "=": "equal",
        "!=": "not_equal",
        ">": "greater_than",
        "<": "less_than",
        ">=": "greater_than_or_equal",
        "<=": "less_than_or_equal",
        "in": "contains",
        "not in": "not_contains",
    }

    def __init__(self, input_file: str, output_file: str):
        """
        초기화

        Args:
            input_file: 입력 이벤트 JSON 파일 경로
            output_file: 출력 이벤트 JSON 파일 경로
        """
        self.input_file = input_file
        self.output_file = output_file

    def load_events(self) -> dict[str, list[dict[str, Any]]]:
        """
        이벤트 JSON 파일 로드

        Returns:
            이벤트 데이터 딕셔너리
        """
        try:
            with open(self.input_file, encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict) or "events" not in data:
                    return {"events": []}
                return data
        except Exception as e:
            print(f"❌ 파일 로드 오류: {e!s}")
            return {"events": []}

    def fix_trigger_conditions(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        이벤트의 트리거 조건 수정

        Args:
            events: 이벤트 목록

        Returns:
            수정된 이벤트 목록
        """
        fixed_events = []

        for event in events:
            # 이벤트 복사본 생성
            fixed_event = event.copy()

            # 트리거 조건 수정
            if "trigger" in fixed_event:
                trigger = fixed_event["trigger"]
                if isinstance(trigger, dict) and "condition" in trigger:
                    old_condition = trigger["condition"]
                    if old_condition in self.CONDITION_MAPPING:
                        trigger["condition"] = self.CONDITION_MAPPING[old_condition]

            # 선택지의 연쇄 이벤트 트리거 조건 수정
            if "choices" in fixed_event:
                for choice in fixed_event["choices"]:
                    if "cascade_events" in choice:
                        for cascade in choice["cascade_events"]:
                            if "condition" in cascade:
                                old_condition = cascade["condition"]
                                if old_condition in self.CONDITION_MAPPING:
                                    cascade["condition"] = self.CONDITION_MAPPING[old_condition]

            fixed_events.append(fixed_event)

        return fixed_events

    def save_events(self, events: list[dict[str, Any]]) -> None:
        """
        수정된 이벤트를 JSON 파일로 저장

        Args:
            events: 저장할 이벤트 목록
        """
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump({"events": events}, f, ensure_ascii=False, indent=2)
            print(f"✅ 수정된 이벤트가 {self.output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 오류: {e!s}")

    def process(self) -> None:
        """이벤트 조건 수정 프로세스 실행"""
        # 이벤트 로드
        data = self.load_events()

        if "events" not in data or not data["events"]:
            print("❌ 이벤트 데이터가 없습니다.")
            return

        # 트리거 조건 수정
        fixed_events = self.fix_trigger_conditions(data["events"])

        # 수정된 이벤트 저장
        self.save_events(fixed_events)


def main() -> None:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="이벤트 조건 수정 도구")
    parser.add_argument("input", help="입력 이벤트 JSON 파일 경로")
    parser.add_argument("output", help="출력 이벤트 JSON 파일 경로")

    args = parser.parse_args()
    fixer = EventConditionFixer(args.input, args.output)
    fixer.process()


if __name__ == "__main__":
    main()

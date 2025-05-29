"""
파일: dev_tools/event_condition_fixer.py
설명: LLM 생성 이벤트의 트리거 조건을 자동으로 교정하는 도구
작성자: Manus
날짜: 2025-05-27
"""

import json
import argparse
import os
from typing import Dict, Any, List, Optional


class EventConditionFixer:
    """LLM 생성 이벤트의 트리거 조건을 자동으로 교정하는 클래스"""

    # 유효한 트리거 조건 매핑 - validator가 공식적으로 지원하는 세 가지 값만 허용
    CONDITION_MAPPING = {
        # 약어를 공식 지원 값으로 변환
        "gt": "greater_than",
        "gte": "greater_than",  # greater_than_or_equal은 지원되지 않으므로 greater_than으로 대체
        "lt": "less_than",
        "lte": "less_than",  # less_than_or_equal은 지원되지 않으므로 less_than으로 대체
        "eq": "equal",
        "neq": "equal",  # not_equal은 지원되지 않으므로 equal로 대체
        # 기호를 공식 지원 값으로 변환
        ">": "greater_than",
        ">=": "greater_than",  # greater_than_or_equal은 지원되지 않으므로 greater_than으로 대체
        "<": "less_than",
        "<=": "less_than",  # less_than_or_equal은 지원되지 않으므로 less_than으로 대체
        "==": "equal",
        "!=": "equal",  # not_equal은 지원되지 않으므로 equal로 대체
        # 풀네임을 공식 지원 값으로 변환
        "greater_than": "greater_than",
        "greater_than_or_equal": "greater_than",  # 지원되지 않으므로 greater_than으로 대체
        "less_than": "less_than",
        "less_than_or_equal": "less_than",  # 지원되지 않으므로 less_than으로 대체
        "equal": "equal",
        "not_equal": "equal",  # 지원되지 않으므로 equal로 대체
    }

    def __init__(self, input_file: str, output_file: Optional[str] = None):
        """
        초기화

        Args:
            input_file: 입력 이벤트 JSON 파일 경로
            output_file: 출력 이벤트 JSON 파일 경로 (기본값: 입력 파일명_fixed.json)
        """
        self.input_file = input_file

        if output_file is None:
            base, ext = os.path.splitext(input_file)
            self.output_file = f"{base}_fixed{ext}"
        else:
            self.output_file = output_file

    def load_events(self) -> Dict[str, Any]:
        """
        이벤트 JSON 파일 로드

        Returns:
            이벤트 데이터 딕셔너리
        """
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 파일 로드 오류: {str(e)}")
            return {"events": []}

    def save_events(self, data: Dict[str, Any]) -> None:
        """
        수정된 이벤트 JSON 파일 저장

        Args:
            data: 저장할 이벤트 데이터 딕셔너리
        """
        try:
            # 출력 디렉토리가 없으면 생성
            os.makedirs(
                os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True
            )

            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 수정된 이벤트가 {self.output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 오류: {str(e)}")
            # 예외 발생 시에도 빈 파일 생성 시도
            try:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump({"events": []}, f, ensure_ascii=False, indent=2)
                print(
                    f"⚠️ 오류 발생으로 빈 이벤트 파일이 생성되었습니다: {self.output_file}"
                )
            except Exception as inner_e:
                print(f"❌ 빈 파일 생성 시도 중 오류 발생: {str(inner_e)}")

    def fix_trigger_conditions(
        self, events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        이벤트의 트리거 조건 수정

        Args:
            events: 이벤트 리스트

        Returns:
            수정된 이벤트 리스트
        """
        fixed_events = []
        fixed_count = 0

        for event in events:
            # 트리거 필드가 있는 경우
            if "trigger" in event:
                if "condition" in event["trigger"]:
                    original_condition = event["trigger"]["condition"]

                    # 조건 매핑에 있는 경우 교체
                    if original_condition in self.CONDITION_MAPPING:
                        event["trigger"]["condition"] = self.CONDITION_MAPPING[
                            original_condition
                        ]
                        fixed_count += 1
                        print(
                            f"✅ 이벤트 {event['id']}의 트리거 조건 수정: {original_condition} → {event['trigger']['condition']}"
                        )

            fixed_events.append(event)

        print(f"✅ 총 {fixed_count}개 이벤트의 트리거 조건이 수정되었습니다.")
        return fixed_events

    def process(self) -> None:
        """
        이벤트 처리 메인 메서드
        """
        # 이벤트 로드
        data = self.load_events()

        if "events" not in data or not data["events"]:
            print("❌ 이벤트 데이터가 없습니다.")
            # 이벤트가 없어도 빈 파일 생성
            self.save_events({"events": []})
            return

        # 트리거 조건 수정
        fixed_events = self.fix_trigger_conditions(data["events"])

        # 수정된 이벤트 저장
        data["events"] = fixed_events
        self.save_events(data)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="LLM 생성 이벤트의 트리거 조건을 자동으로 교정하는 도구"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="입력 이벤트 JSON 파일 경로"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="출력 이벤트 JSON 파일 경로 (기본값: 입력 파일명_fixed.json)",
    )

    args = parser.parse_args()

    fixer = EventConditionFixer(args.input, args.output)
    fixer.process()


if __name__ == "__main__":
    main()

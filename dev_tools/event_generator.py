#!/usr/bin/env python3
"""
파일: dev_tools/event_generator.py
설명: 이벤트 생성기
작성자: Manus
날짜: 2025-05-27
"""

import json
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union

try:
    import anthropic  # type: ignore
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ anthropic 라이브러리를 찾을 수 없습니다. API 호출이 비활성화됩니다.")
    # mypy를 위한 더미 모듈 정의
    class anthropic:  # type: ignore
        class Anthropic:
            def __init__(self, api_key: str) -> None:
                pass

class EventGenerator:
    """이벤트 생성기"""

    def __init__(self, api_key: str):
        """
        초기화

        Args:
            api_key: Anthropic API 키
        """
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if ANTHROPIC_AVAILABLE else None

    def _call_claude_api(self, prompt: str) -> Dict[str, Any]:
        """
        Claude API 호출

        Args:
            prompt: 프롬프트 문자열

        Returns:
            API 응답 데이터
        """
        if not ANTHROPIC_AVAILABLE or not self.client:
            print("❌ anthropic 라이브러리가 설치되지 않았습니다.")
            return {}

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"messages": response.content[0].text}
        except Exception as e:
            print(f"❌ API 호출 오류: {str(e)}")
            return {}

    def create_prompt(self, category: str, tags: List[str], constraints: Dict[str, Any]) -> str:
        """
        이벤트 생성 프롬프트 생성

        Args:
            category: 이벤트 카테고리
            tags: 이벤트 태그 목록
            constraints: 제약 조건 딕셔너리

        Returns:
            생성된 프롬프트 문자열
        """
        prompt = f"""다음 조건에 맞는 치킨집 운영 게임의 이벤트를 생성해주세요:

카테고리: {category}
태그: {', '.join(tags)}

제약 조건:
- 이벤트는 JSON 형식으로 생성되어야 합니다.
- 이벤트는 다음 필드를 포함해야 합니다:
  - id: 고유 식별자 (문자열)
  - category: 이벤트 카테고리 (문자열)
  - type: 이벤트 타입 (THRESHOLD 또는 RANDOM)
  - name_ko: 한국어 이벤트 이름 (문자열)
  - name_en: 영어 이벤트 이름 (문자열)
  - text_ko: 한국어 이벤트 설명 (문자열)
  - text_en: 영어 이벤트 설명 (문자열)
  - conditions: 이벤트 발생 조건 목록 (배열)
  - effects: 이벤트 효과 목록 (배열)
  - choices: 선택지 목록 (배열)
  - tags: 이벤트 태그 목록 (배열)
  - probability: 이벤트 발생 확률 (0.0-1.0)
  - cooldown: 재발생 대기 시간 (턴 단위)
  - trigger: 트리거 조건 (객체)

추가 제약 조건:"""

        for key, value in constraints.items():
            prompt += f"\n- {key}: {value}"

        return prompt

    def generate_events(
        self,
        category: str,
        tags: List[str],
        count: int = 1,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        이벤트 생성

        Args:
            category: 이벤트 카테고리
            tags: 이벤트 태그 목록
            count: 생성할 이벤트 수
            constraints: 제약 조건 딕셔너리 (선택사항)

        Returns:
            생성된 이벤트 목록
        """
        if not ANTHROPIC_AVAILABLE:
            print("❌ anthropic 라이브러리가 설치되지 않았습니다.")
            return []

        events = []
        constraints = constraints or {}

        for _ in range(count):
            prompt = self.create_prompt(category, tags, constraints)
            response = self._call_claude_api(prompt)

            if not response or "messages" not in response:
                print("❌ API 응답이 유효하지 않습니다.")
                continue

            try:
                # JSON 문자열 추출
                json_str = re.search(r"\{[\s\S]*\}", response["messages"])
                if not json_str:
                    print("❌ JSON 데이터를 찾을 수 없습니다.")
                    continue

                event_data = json.loads(json_str.group())
                events.append(event_data)
                print(f"✅ 이벤트 생성 완료: {event_data.get('id', '알 수 없음')}")

            except Exception as e:
                print(f"❌ 이벤트 파싱 오류: {str(e)}")
                continue

        return events

    def save_events(self, events: List[Dict[str, Any]], output_file: str) -> None:
        """
        생성된 이벤트를 JSON 파일로 저장

        Args:
            events: 이벤트 목록
            output_file: 출력 파일 경로
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({"events": events}, f, ensure_ascii=False, indent=2)
            print(f"✅ 이벤트가 {output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 오류: {str(e)}")

def main() -> None:
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="이벤트 생성기")
    parser.add_argument("--api-key", required=True, help="Anthropic API 키")
    parser.add_argument("--category", required=True, help="이벤트 카테고리")
    parser.add_argument("--tags", nargs="+", default=[], help="이벤트 태그 목록")
    parser.add_argument("--count", type=int, default=1, help="생성할 이벤트 수")
    parser.add_argument("--output", required=True, help="출력 파일 경로")

    args = parser.parse_args()

    generator = EventGenerator(args.api_key)
    events = generator.generate_events(args.category, args.tags, args.count)
    generator.save_events(events, args.output)

if __name__ == "__main__":
    main()

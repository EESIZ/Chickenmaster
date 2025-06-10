#!/usr/bin/env python3
"""
파일: dev_tools/event_generator.py
목적: 이벤트 생성 도구
"""

import json
import re
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # type: ignore

from game_constants import PROBABILITY_HIGH_THRESHOLD


class EventGenerator:
    """이벤트 생성기"""

    def __init__(self, api_key: str):
        """
        초기화

        Args:
            api_key: Anthropic API 키
        """
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key) if Anthropic else None

    def _call_claude_api(self, prompt: str) -> dict[str, Any]:
        """
        Claude API 호출

        Args:
            prompt: 프롬프트 문자열

        Returns:
            API 응답 데이터
        """
        if not Anthropic or not self.client:
            print("[ERROR] anthropic 라이브러리가 설치되지 않았습니다.")
            return {}

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # 최신 모델로 변경
                max_tokens=4000,
                temperature=PROBABILITY_HIGH_THRESHOLD,
                messages=[{"role": "user", "content": prompt}],
            )
            return {"messages": response.content[0].text}
        except Exception as e:
            print(f"[ERROR] API 호출 오류: {e!s}")
            return {}

    def create_prompt(self, category: str, tags: list[str], constraints: dict[str, Any]) -> str:
        """
        이벤트 생성 프롬프트 생성

        Args:
            category: 이벤트 카테고리
            tags: 이벤트 태그 목록
            constraints: 제약 조건 딕셔너리

        Returns:
            생성된 프롬프트 문자열
        """
        import random

        random_suffix = random.randint(1000, 9999)

        prompt = f"""다음 조건에 맞는 치킨집 운영 게임의 이벤트를 생성해주세요:

카테고리: {category}
태그: {', '.join(tags)}

중요: 다음 JSON 형식을 정확히 따라주세요. 모든 필드는 필수입니다:

{{
  "id": "unique_event_id_{random_suffix}",
  "category": "{category}",
  "type": "THRESHOLD" 또는 "RANDOM",
  "name_ko": "한국어 이벤트 이름",
  "name_en": "English Event Name", 
  "text_ko": "한국어 이벤트 설명",
  "text_en": "English event description",
  "conditions": [],
  "effects": [
    {{
      "metric": "MONEY", 
      "formula": "100"
    }},
    {{
      "metric": "REPUTATION",
      "formula": "10"
    }}
  ],
  "choices": [
    {{
      "text_ko": "선택지 1",
      "text_en": "Choice 1",
      "effects": {{
        "money": 100,
        "reputation": -10
      }}
    }},
    {{
      "text_ko": "선택지 2", 
      "text_en": "Choice 2",
      "effects": {{
        "money": -50,
        "reputation": 20
      }}
    }}
  ],
  "tags": {tags},
  "probability": 0.5,
  "cooldown": 10,
  "trigger": {{
    "metric": "MONEY",
    "condition": "greater_than",
    "value": 1000
  }}
}}

필수 요구사항:
- id는 반드시 고유해야 하며, 다음 형식 중 하나를 사용: {category}_specific_name_{random_suffix}, event_{category}_{random.randint(10000, 99999)}, {category}_unique_situation_{random_suffix}
- 매번 다른 상황, 다른 이벤트를 생성해주세요 (배달 러시아워만 반복하지 마세요)
- effects 배열은 반드시 1개 이상의 요소를 포함해야 함
- 각 effect는 metric(MONEY, REPUTATION, CUSTOMER_SATISFACTION 등)과 formula(수식 문자열) 필드 필수
- trigger의 condition은 "greater_than", "less_than", "equal" 중 하나
- 선택지는 명확한 tradeoff를 가져야 함
- 한국 치킨집 문화를 반영해야 함
- 다양한 상황을 생성: 단골 손님, 신규 메뉴, 재료 부족, 리뷰, 경쟁업체, 날씨, 이벤트 등"""

        for key, value in constraints.items():
            prompt += f"\n- {key}: {value}"

        prompt += "\n\nJSON만 출력하고 다른 설명은 하지 마세요."

        return prompt

    def generate_events(
        self,
        category: str,
        tags: list[str] | None = None,
        count: int = 1,
        temperature: float = PROBABILITY_HIGH_THRESHOLD,
        max_tokens: int = 2048,
    ) -> list[dict[str, Any]]:
        """지정된 카테고리와 태그로 이벤트를 생성합니다."""
        events = []
        for _ in range(count):
            event = self._generate_single_event(category, tags or [])
            if event:
                events.append(event)
            else:
                print("[ERROR] API 응답이 유효하지 않습니다.")

        return events

    def _generate_single_event(self, category: str, tags: list[str]) -> dict[str, Any] | None:
        """단일 이벤트 생성"""
        prompt = self.create_prompt(category, tags, {})
        response = self._call_claude_api(prompt)

        if not response or "messages" not in response:
            return None

        # JSON 추출 후 events 배열에서 첫 번째 이벤트 반환
        extracted_data = self._extract_json_from_response(response["messages"])
        if extracted_data and "events" in extracted_data and extracted_data["events"]:
            return extracted_data["events"][0]  # 첫 번째 이벤트 반환

        return extracted_data  # events 키가 없으면 전체 데이터 반환

    def _extract_json_from_response(self, response_text: str) -> dict[str, Any] | None:
        """API 응답에서 JSON 추출"""
        # 디버깅을 위해 응답 일부 출력
        print(f"[DEBUG] API 응답 길이: {len(response_text)}")
        print(f"[DEBUG] API 응답 시작 부분: {response_text[:200]}...")

        # JSON 블록을 찾기 위한 여러 패턴 시도
        patterns = [
            r"```json\s*(.*?)\s*```",  # ```json ... ```
            r"```\s*(.*?)\s*```",  # ``` ... ```
            r"\{[\s\S]*\}",  # { ... }
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    # 패턴에 따라 다른 그룹 추출
                    json_str = match.group(1) if "```" in pattern else match.group(0)
                    event_data = json.loads(json_str)
                    print(f"[SUCCESS] 이벤트 생성 완료: {event_data.get('id', '알 수 없음')}")
                    return event_data
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 파싱 오류: {e!s}")
                    print(f"[DEBUG] JSON 문자열: {json_str[:200]}...")
                    continue

        print("[ERROR] JSON 데이터를 찾을 수 없습니다.")
        print(f"[DEBUG] 전체 응답: {response_text[:500]}...")
        return None

    def save_events(self, events: list[dict[str, Any]], output_file: str) -> None:
        """
        이벤트를 파일로 저장

        Args:
            events: 이벤트 목록
            output_file: 출력 파일 경로
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 이벤트가 {output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"[ERROR] 파일 저장 오류: {e!s}")


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

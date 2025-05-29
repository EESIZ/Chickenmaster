"""
파일: dev_tools/event_generator.py
목적: LLM 기반 이벤트 생성 도구
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import anthropic
import tomllib  # Python 3.11+

from dev_tools.config import Config


class EventGenerator:
    """이벤트 생성기 클래스"""

    def __init__(self) -> None:
        """초기화"""
        self.config = Config()
        self.client = None
        try:
            self.api_key = Config.get_api_key()
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            else:
                raise ValueError("API 키가 설정되지 않았습니다")
        except Exception as e:
            print(f"⚠️ Claude API 초기화 오류: {str(e)}")
            print("더미 데이터를 생성합니다.")

    def create_prompt(self, category: str, n: int = 10, variants: bool = False) -> str:
        """
        이벤트 생성 프롬프트 생성

        Args:
            category: 이벤트 카테고리 (daily_routine, crisis_events, opportunity, human_drama, chain_scenario)
            n: 생성할 이벤트 수
            variants: A/B 변형 생성 여부

        Returns:
            프롬프트 문자열
        """
        # 카테고리별 특화 프롬프트
        category_prompts = {
            "daily_routine": "한국 치킨집 일상에서 발생하는 소소한 이벤트를 생성해주세요. 배달, 단골 손님, 알바생 관련 상황 등이 포함되어야 합니다.",
            "crisis_events": "치킨집 경영에 위기를 가져올 수 있는 부정적 이벤트를 생성해주세요. 식자재 가격 상승, 경쟁업체 등장, 위생 문제 등이 포함되어야 합니다.",
            "opportunity": "치킨집에 기회가 될 수 있는 긍정적 이벤트를 생성해주세요. 지역 축제, 유명인 방문, 신메뉴 개발 기회 등이 포함되어야 합니다.",
            "human_drama": "치킨집 주변 인물들과의 드라마틱한 상황을 담은 이벤트를 생성해주세요. 손님과의 갈등, 직원 간 관계, 가족 문제 등이 포함되어야 합니다.",
            "chain_scenario": "여러 선택지가 연쇄적으로 이어지는 복합 시나리오를 생성해주세요. 초기 선택에 따라 다른 결과로 분기되는 구조여야 합니다.",
        }

        # 기본 프롬프트
        prompt = f"""
당신은 한국 치킨집 경영 시뮬레이션 게임 '치킨마스터'의 이벤트 생성 전문가입니다.
'{category}' 카테고리에 해당하는 게임 이벤트를 {n}개 생성해주세요.

{category_prompts.get(category, "다양한 상황의 이벤트를 생성해주세요.")}

각 이벤트는 다음 구조를 가진 JSON 형식으로 생성해야 합니다:
```json
{{
  "id": "고유 ID (예: daily_001)",
  "category": "{category}",
  "type": "이벤트 타입 (RANDOM, THRESHOLD, SCHEDULED, CASCADE 중 하나)",
  "name_ko": "한국어 이벤트 이름",
  "name_en": "영어 이벤트 이름",
  "text_ko": "한국어 이벤트 설명 (최소 100자)",
  "text_en": "영어 이벤트 설명 (최소 100자)",
  "probability": 0.1-1.0 사이 확률 (RANDOM 타입일 경우만),
  "cooldown": 0-30 사이 쿨다운 일수,
  "trigger": {{
    "metric": "트리거 지표 (money, reputation, stress 등)",
    "condition": "트리거 조건 (greater_than, less_than, equal 중 하나)",
    "value": 트리거 값
  }} (THRESHOLD, CASCADE 타입일 경우만),
  "schedule": 스케줄 일수 (SCHEDULED 타입일 경우만),
  "tags": ["관련 태그 (최소 3개)"],
  "effects": [
    {{
      "metric": "영향 지표 (money, reputation, stress 등)",
      "formula": "영향 수식 (예: +100, -50, *1.1, /2)"
    }}
  ],
  "choices": [
    {{
      "id": "선택지 ID (예: choice_1)",
      "text_ko": "한국어 선택지 텍스트",
      "text_en": "영어 선택지 텍스트",
      "effects": [
        {{
          "metric": "영향 지표",
          "formula": "영향 수식"
        }}
      ],
      "next_event": "다음 이벤트 ID (CASCADE 타입일 경우만)"
    }}
  ]
}}
```

중요 지침:
1. 응답은 반드시 유효한 JSON 형식이어야 합니다. 설명이나 추가 텍스트 없이 JSON 배열만 반환하세요.
2. 각 이벤트는 명확한 트레이드오프를 가져야 합니다 (한 지표를 올리면 다른 지표가 내려가는 등).
3. 한국 치킨집 문화를 반영한 현실적인 상황을 담아야 합니다.
4. 이벤트 타입별 필수 필드를 반드시 포함해야 합니다.
5. 트리거 조건은 반드시 'greater_than', 'less_than', 'equal' 중 하나여야 합니다.
6. 모든 텍스트 필드는 한국어와 영어 버전을 모두 포함해야 합니다.
"""

        # A/B 변형 지침 추가
        if variants:
            prompt += """
7. 각 이벤트에 대해 A/B 변형을 생성하세요. 변형은 "variant" 필드에 "a" 또는 "b"로 표시합니다.
   - A 변형: 원본 이벤트
   - B 변형: 동일한 상황이지만 다른 결과나 선택지를 제공하는 변형
"""

        return prompt

    def generate_events(
        self,
        category: str,
        n: int = 10,
        seed: Optional[int] = None,
        variants: bool = False,
        output_dir: str = ".",
    ) -> List[Dict[str, Any]]:
        """
        이벤트 생성

        Args:
            category: 이벤트 카테고리
            n: 생성할 이벤트 수
            seed: 랜덤 시드
            variants: A/B 변형 생성 여부
            output_dir: 출력 디렉토리

        Returns:
            생성된 이벤트 리스트
        """
        if seed is not None:
            random.seed(seed)

        # 프롬프트 생성
        prompt = self.create_prompt(category, n, variants)

        # Claude API 호출 또는 더미 데이터 생성
        events_list = []
        try:
            if self.client:
                api_response = self._call_claude_api(prompt)
                # 반환 구조 불일치 수정: 딕셔너리 응답에서 이벤트 리스트 추출
                if isinstance(api_response, dict) and "content" in api_response:
                    parsed_events = self._parse_json_response(
                        api_response["content"][0]["text"]
                    )
                    events_list = parsed_events if parsed_events else []
                else:
                    events_list = api_response if isinstance(api_response, list) else []
            else:
                events_list = self._generate_dummy_events(category, n, variants)
        except Exception as e:
            print(f"⚠️ 이벤트 생성 오류: {str(e)}")
            print("더미 데이터를 생성합니다.")
            events_list = self._generate_dummy_events(category, n, variants)

        # 결과 저장
        if events_list:
            self.save_events(events_list, output_dir)

        return events_list

    def _call_claude_api(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Claude API 호출

        Args:
            prompt: 프롬프트 문자열

        Returns:
            생성된 이벤트 리스트
        """
        try:
            # Claude API 호출
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.7,
                system="당신은 게임 이벤트 생성 전문가입니다. 응답은 반드시 유효한 JSON 형식이어야 합니다. 설명이나 추가 텍스트 없이 JSON 배열만 반환하세요.",
                messages=[{"role": "user", "content": prompt}],
            )

            # 응답 텍스트 추출
            response_text = response.content[0].text
            print(f"응답 길이: {len(response_text)}자")

            # JSON 파싱 (3단계 전략)
            events = self._parse_json_response(response_text)

            if not events:
                print("⚠️ 유효한 이벤트를 추출할 수 없습니다. 더미 데이터를 생성합니다.")
                return []

            return events

        except Exception as e:
            print(f"⚠️ Claude API 호출 오류: {str(e)}")
            raise

    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Claude 응답에서 JSON 추출

        Args:
            response_text: Claude 응답 텍스트

        Returns:
            추출된 이벤트 리스트
        """
        # 1. JSON 코드 블록 추출 시도
        json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        json_blocks = re.findall(json_block_pattern, response_text)

        for block in json_blocks:
            try:
                # 배열인 경우
                if block.strip().startswith("["):
                    data = json.loads(block)
                    if isinstance(data, list):
                        return data
                # 객체인 경우
                elif block.strip().startswith("{"):
                    data = json.loads(block)
                    if "events" in data and isinstance(data["events"], list):
                        return data["events"]
            except json.JSONDecodeError:
                continue

        # 2. 전체 텍스트에서 JSON 배열 추출 시도
        try:
            # 전체 텍스트가 JSON 배열인 경우
            if response_text.strip().startswith("[") and response_text.strip().endswith(
                "]"
            ):
                data = json.loads(response_text)
                if isinstance(data, list):
                    return data
            # 전체 텍스트가 JSON 객체인 경우
            elif response_text.strip().startswith(
                "{"
            ) and response_text.strip().endswith("}"):
                data = json.loads(response_text)
                if "events" in data and isinstance(data["events"], list):
                    return data["events"]
        except json.JSONDecodeError:
            pass

        # 3. 개별 JSON 객체 추출 시도
        json_object_pattern = r"(\{[\s\S]*?\})"
        json_objects = re.findall(json_object_pattern, response_text)

        events = []
        for obj in json_objects:
            try:
                data = json.loads(obj)
                if "id" in data and "category" in data:
                    events.append(data)
            except json.JSONDecodeError:
                continue

        if events:
            return events

        # 모든 시도 실패
        print(f"⚠️ JSON 파싱 실패. 응답: {response_text[:100]}...")
        return []

    def _generate_dummy_events(
        self, category: str, n: int, variants: bool
    ) -> List[Dict[str, Any]]:
        """
        더미 이벤트 생성

        Args:
            category: 이벤트 카테고리
            n: 생성할 이벤트 수
            variants: A/B 변형 생성 여부

        Returns:
            더미 이벤트 리스트
        """
        dummy_events = []
        event_types = ["RANDOM", "THRESHOLD", "SCHEDULED", "CASCADE"]
        metrics = [
            "money",
            "reputation",
            "stress",
            "customer_satisfaction",
            "employee_morale",
        ]
        conditions = ["greater_than", "less_than", "equal"]

        # 카테고리별 태그
        category_tags = {
            "daily_routine": ["일상", "배달", "단골", "알바생", "주방", "홀서빙"],
            "crisis_events": ["위기", "경쟁", "가격상승", "위생", "민원", "사고"],
            "opportunity": ["기회", "축제", "유명인", "신메뉴", "프로모션", "투자"],
            "human_drama": ["갈등", "관계", "가족", "직원", "손님", "감동"],
            "chain_scenario": ["선택", "분기", "시나리오", "결과", "연쇄", "전략"],
        }

        for i in range(n):
            event_type = random.choice(event_types)
            event_id = f"{category}_{i+1:03d}"

            # 기본 이벤트 구조
            event = {
                "id": event_id,
                "category": category,
                "type": event_type,
                "name_ko": f"테스트 이벤트 {i+1}",
                "name_en": f"Test Event {i+1}",
                "text_ko": f"이것은 {category} 카테고리의 테스트 이벤트입니다. 한국 치킨집 문화를 반영한 다양한 상황과 선택지를 제공합니다.",
                "text_en": f"This is a test event in the {category} category. It provides various situations and choices reflecting Korean chicken restaurant culture.",
                "cooldown": random.randint(0, 30),
                "tags": random.sample(
                    category_tags.get(category, ["테스트"]),
                    min(3, len(category_tags.get(category, ["테스트"]))),
                ),
                "effects": [
                    {
                        "metric": random.choice(metrics),
                        "formula": f"{'+' if random.random() > 0.5 else '-'}{random.randint(10, 500)}",
                    }
                ],
                "choices": [
                    {
                        "id": f"choice_{j+1}",
                        "text_ko": f"선택지 {j+1}",
                        "text_en": f"Choice {j+1}",
                        "effects": [
                            {
                                "metric": random.choice(metrics),
                                "formula": f"{'+' if random.random() > 0.5 else '-'}{random.randint(10, 500)}",
                            }
                        ],
                    }
                    for j in range(random.randint(2, 4))
                ],
            }

            # 이벤트 타입별 추가 필드
            if event_type == "RANDOM":
                event["probability"] = round(random.uniform(0.1, 1.0), 2)
            elif event_type in ["THRESHOLD", "CASCADE"]:
                event["trigger"] = {
                    "metric": random.choice(metrics),
                    "condition": random.choice(conditions),
                    "value": random.randint(0, 1000),
                }
                if event_type == "CASCADE":
                    for choice in event["choices"]:
                        choice["next_event"] = f"{category}_{random.randint(1, n):03d}"
            elif event_type == "SCHEDULED":
                event["schedule"] = random.randint(1, 30)

            # A/B 변형 추가
            if variants and i % 2 == 0:
                event["variant"] = "a"
            elif variants:
                event["variant"] = "b"

            dummy_events.append(event)

        return dummy_events

    def save_events(self, events: List[Dict[str, Any]], output_dir: str) -> str:
        """
        이벤트 저장

        Args:
            events: 이벤트 리스트
            output_dir: 출력 디렉토리

        Returns:
            저장된 파일 경로
        """
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

        # 파일 경로 생성
        file_path = os.path.join(output_dir, f"raw_events_{timestamp}.json")

        # 이벤트 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"events": events}, f, ensure_ascii=False, indent=2)

        print(f"✅ 이벤트 {len(events)}개가 {file_path}에 저장되었습니다.")

        return file_path


def main() -> int:
    parser = argparse.ArgumentParser(description="치킨집 경영 게임 이벤트 생성기")
    parser.add_argument(
        "--category",
        type=str,
        choices=[
            "daily_routine",
            "crisis_events",
            "opportunity",
            "human_drama",
            "chain_scenario",
        ],
        default="daily_routine",
        help="이벤트 카테고리",
    )
    parser.add_argument("--n", type=int, default=10, help="생성할 이벤트 수")
    parser.add_argument("--seed", type=int, help="랜덤 시드")
    parser.add_argument("--variants", action="store_true", help="A/B 변형 생성 여부")
    parser.add_argument("--output", type=str, default=".", help="출력 디렉토리")

    args = parser.parse_args()

    generator = EventGenerator()
    generator.generate_events(
        category=args.category,
        n=args.n,
        seed=args.seed,
        variants=args.variants,
        output_dir=args.output,
    )

    return 0


if __name__ == "__main__":
    main()

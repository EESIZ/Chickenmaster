#!/usr/bin/env python3
"""
파일: scripts/mass_event_generation.py
목적: 대량의 이벤트 데이터 생성 도구
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# 프로젝트 루트 디렉토리 찾기
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent

# 프로젝트 모듈 import를 위한 경로 설정
sys.path.insert(0, str(project_root))

from dev_tools.event_validator import EventValidator
from dev_tools.openai_client import OpenAIClient

# 생성 설정
GENERATION_CONFIG = {
    "MODEL": "gpt-4-turbo",
    "TEMPERATURE": 0.8,
    "MAX_TOKENS": 2000,
    "COST_PER_EVENT": 0.05,  # 예상 비용 (USD)
    "COST_WARNING_THRESHOLD": 5.0,  # 비용 경고 임계값 (USD)
    "BATCH_SIZE": 5,  # 한 번에 생성할 이벤트 수
    "RETRY_ATTEMPTS": 3,  # 실패 시 재시도 횟수
    "DELAY_BETWEEN_BATCHES": 2,  # 배치 간 지연 시간 (초)
}

# 이벤트 카테고리 및 설명
EVENT_CATEGORIES = {
    "customer": {
        "description": "고객 관련 이벤트 (주문, 불만, 리뷰 등)",
        "examples": ["단골 손님의 특별 요청", "악성 리뷰 대응", "대량 주문 요청"],
        "weight": 3,  # 가중치 (높을수록 더 많이 생성)
    },
    "employee": {
        "description": "직원 관련 이벤트 (채용, 교육, 갈등 등)",
        "examples": ["알바생 지각", "주방장 퇴사 위기", "직원 간 갈등"],
        "weight": 2,
    },
    "business": {
        "description": "사업 관련 이벤트 (재정, 마케팅, 경쟁 등)",
        "examples": ["경쟁 업체 오픈", "프랜차이즈 제안", "세무조사"],
        "weight": 2,
    },
    "supply": {
        "description": "공급망 관련 이벤트 (재료, 장비, 배달 등)",
        "examples": ["닭 가격 폭등", "냉장고 고장", "식자재 유통기한 문제"],
        "weight": 2,
    },
    "random": {
        "description": "예측 불가능한 이벤트 (날씨, 사고, 행운 등)",
        "examples": ["갑작스러운 폭우", "유명인 방문", "건물 누수"],
        "weight": 1,
    },
}

# 프롬프트 템플릿
SYSTEM_PROMPT = """당신은 치킨집 경영 시뮬레이션 게임 '치킨마스터'의 이벤트 생성 AI입니다.
한국 치킨집 문화와 경영 현실을 반영한 게임 이벤트를 생성해주세요.

게임의 핵심 철학:
1. 정답 없음(noRightAnswer): 모든 선택은 득과 실을 동시에 가져옵니다.
2. 트레이드오프(tradeoff): 한 지표를 올리면 다른 지표는 내려갑니다.
3. 불확실성(uncertainty): 세상은 예측 불가능하며, 완벽한 대비는 불가능합니다.

게임의 주요 지표:
- MONEY: 현금 (사업 운영 자금)
- REPUTATION: 평판 (가게의 사회적 평가)
- HAPPINESS: 행복 (사장의 정신적 만족도)
- PAIN: 고통 (사장의 정신적 스트레스)
- EMPLOYEE_SATISFACTION: 직원 만족도
- CUSTOMER_SATISFACTION: 고객 만족도
- INGREDIENT_QUALITY: 재료 품질
- EQUIPMENT_CONDITION: 장비 상태
- STORE_CLEANLINESS: 매장 청결도
- MENU_DIVERSITY: 메뉴 다양성

이벤트 타입:
- RANDOM: 무작위로 발생하는 이벤트 (probability 필요)
- THRESHOLD: 특정 조건 충족 시 발생하는 이벤트 (trigger 필요)
- SCHEDULED: 특정 게임 일차에 발생하는 이벤트 (schedule 필요)
- CASCADE: 다른 이벤트의 결과로 발생하는 이벤트 (trigger 필요)

출력 형식은 JSON 배열로, 각 이벤트는 다음 구조를 따라야 합니다:
```
{
  "id": "unique_event_id",
  "type": "RANDOM|THRESHOLD|SCHEDULED|CASCADE",
  "category": "customer|employee|business|supply|random",
  "name_ko": "이벤트 제목 (한국어)",
  "name_en": "Event Title (English)",
  "text_ko": "이벤트 설명 텍스트 (한국어)",
  "text_en": "Event description text (English)",
  "effects": [
    {
      "metric": "METRIC_NAME",
      "formula": "value * 0.1"  // 수식 또는 고정값
    }
  ],
  "choices": [
    {
      "text_ko": "선택지 1 (한국어)",
      "text_en": "Choice 1 (English)",
      "effects": {
        "MONEY": 100,
        "REPUTATION": -20
        // 트레이드오프 필수 (긍정+부정 효과 혼합)
      }
    },
    {
      "text_ko": "선택지 2 (한국어)",
      "text_en": "Choice 2 (English)",
      "effects": {
        "MONEY": -50,
        "REPUTATION": 30
      }
    }
  ],
  "tags": ["태그1", "태그2"],
  
  // 이벤트 타입별 추가 필드
  "probability": 0.3,  // RANDOM 타입일 경우
  "schedule": 5,       // SCHEDULED 타입일 경우
  "trigger": {         // THRESHOLD 또는 CASCADE 타입일 경우
    "metric": "METRIC_NAME",
    "condition": "less_than|greater_than|equal",
    "value": 50
  },
  "cooldown": 10       // 선택사항: 이벤트 재발생 전 대기 일수
}
```

중요 지침:
1. 한국 치킨집 문화와 현실을 반영한 이벤트를 생성하세요.
2. 모든 선택지는 트레이드오프를 가져야 합니다 (긍정적 효과와 부정적 효과 모두 포함).
3. 이벤트 ID는 고유하고 의미있는 영문 문자열이어야 합니다.
4. 이벤트 설명과 선택지는 한국어와 영어 모두 제공해야 합니다.
5. 각 이벤트는 최소 2개 이상의 선택지를 가져야 합니다.
6. 현실적이고 흥미로운 시나리오를 만들되, 너무 극단적이거나 비현실적인 상황은 피하세요.
7. 게임의 핵심 철학(정답 없음, 트레이드오프, 불확실성)을 반영하세요.
"""

USER_PROMPT_TEMPLATE = """다음 카테고리의 이벤트 {count}개를 생성해주세요: {category}

카테고리 설명: {description}
예시: {examples}

이벤트 타입은 다양하게 섞어서 생성해주세요.
각 이벤트는 고유한 ID를 가져야 하며, 한국 치킨집 문화를 잘 반영해야 합니다.
모든 선택지는 트레이드오프(긍정+부정 효과 혼합)를 가져야 합니다.
"""


class EventGenerator:
    """이벤트 생성기"""

    def __init__(self, api_key: str, output_dir: Path):
        """초기화"""
        self.client = OpenAIClient(api_key)
        self.validator = EventValidator()
        self.output_dir = output_dir
        self.generated_count = 0
        self.valid_count = 0
        self.invalid_count = 0
        self.total_cost = 0.0

    def generate_events(self, category: str, count: int) -> list[dict[str, Any]]:
        """특정 카테고리의 이벤트 생성"""
        category_info = EVENT_CATEGORIES.get(category, {})
        if not category_info:
            print(f"오류: 알 수 없는 카테고리 '{category}'")
            return []

        description = category_info.get("description", "")
        examples = category_info.get("examples", [])
        examples_str = ", ".join(examples)

        USER_PROMPT_TEMPLATE.format(
            count=count, category=category, description=description, examples=examples_str
        )

        print(f"\n[생성 시작] 카테고리: {category}, 수량: {count}개")

        all_events = []
        remaining = count
        batch_size = min(GENERATION_CONFIG["BATCH_SIZE"], remaining)

        while remaining > 0:
            batch_size = min(GENERATION_CONFIG["BATCH_SIZE"], remaining)
            batch_prompt = USER_PROMPT_TEMPLATE.format(
                count=batch_size, category=category, description=description, examples=examples_str
            )

            print(f"  배치 생성 중... ({batch_size}개)")

            for attempt in range(GENERATION_CONFIG["RETRY_ATTEMPTS"]):
                try:
                    response = self.client.chat_completion(
                        model=GENERATION_CONFIG["MODEL"],
                        system_prompt=SYSTEM_PROMPT,
                        user_prompt=batch_prompt,
                        temperature=GENERATION_CONFIG["TEMPERATURE"],
                        max_tokens=GENERATION_CONFIG["MAX_TOKENS"],
                    )

                    # 비용 추적
                    self.total_cost += response.get("cost", 0)

                    # JSON 파싱
                    content = response.get("content", "")
                    events = self._extract_json(content)

                    if events:
                        # 유효성 검사
                        valid_events = []
                        for event in events:
                            if self.validator.validate_event(event):
                                valid_events.append(event)
                                self.valid_count += 1
                            else:
                                self.invalid_count += 1
                                print(f"    ❌ 유효하지 않은 이벤트: {event.get('id', 'unknown')}")
                                for error in self.validator.errors:
                                    print(f"       - {error}")

                        all_events.extend(valid_events)
                        self.generated_count += len(valid_events)

                        print(f"    ✅ 배치 완료: {len(valid_events)}/{batch_size}개 유효")
                        break
                    else:
                        print(
                            f"    ⚠️ JSON 파싱 실패 (시도 {attempt+1}/{GENERATION_CONFIG['RETRY_ATTEMPTS']})"
                        )

                except Exception as e:
                    print(
                        f"    ⚠️ 오류 발생: {e} (시도 {attempt+1}/{GENERATION_CONFIG['RETRY_ATTEMPTS']})"
                    )

                # 마지막 시도가 아니면 잠시 대기
                if attempt < GENERATION_CONFIG["RETRY_ATTEMPTS"] - 1:
                    time.sleep(2)

            remaining -= batch_size

            # 배치 간 지연
            if remaining > 0:
                time.sleep(GENERATION_CONFIG["DELAY_BETWEEN_BATCHES"])

        return all_events

    def generate_events_by_plan(
        self, plan: dict[str, dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """계획에 따라 여러 카테고리의 이벤트 생성"""
        all_events_by_category: dict[str, list[dict[str, Any]]] = {}

        for category, info in plan.items():
            count = info.get("count", 0)
            if count <= 0:
                continue

            events = self.generate_events(category, count)
            all_events_by_category[category] = events

            # 진행 상황 출력
            print(
                f"\n[진행 상황] 총 {self.generated_count}개 생성 완료 (유효: {self.valid_count}, 무효: {self.invalid_count})"
            )
            print(f"[비용] 현재까지: ${self.total_cost:.2f}")

        return all_events_by_category

    def save_events(
        self, events_by_category: dict[str, list[dict[str, Any]]]
    ) -> tuple[int, list[Path]]:
        """생성된 이벤트를 파일로 저장"""
        os.makedirs(self.output_dir, exist_ok=True)

        total_saved = 0
        saved_files = []

        # 카테고리별로 저장
        for category, events in events_by_category.items():
            if not events:
                continue

            # 파일명 생성 (타임스탬프 포함)
            timestamp = int(time.time())
            file_path = self.output_dir / f"events_{category}_{timestamp}.json"

            # JSON 형식으로 저장
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"events": events}, f, ensure_ascii=False, indent=2)

            total_saved += len(events)
            saved_files.append(file_path)
            print(f"✅ 저장 완료: {file_path} ({len(events)}개)")

        return total_saved, saved_files

    def _extract_json(self, content: str) -> list[dict[str, Any]]:
        """텍스트에서 JSON 추출"""
        try:
            # 코드 블록 내 JSON 추출 시도
            if "```json" in content and "```" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
                data = json.loads(json_str)
                return data if isinstance(data, list) else []

            # 전체 텍스트를 JSON으로 파싱 시도
            data = json.loads(content)
            return data if isinstance(data, list) else []

        except json.JSONDecodeError:
            return []

    def _check_cost_warning(self, estimated_cost: float) -> bool:
        """비용 경고 확인"""
        if estimated_cost > GENERATION_CONFIG["COST_WARNING_THRESHOLD"]:
            print(
                f"\n⚠️ 경고: 예상 비용(${estimated_cost:.2f})이 임계값(${GENERATION_CONFIG['COST_WARNING_THRESHOLD']:.2f})을 초과합니다."
            )
            confirm = input("계속 진행하시겠습니까? (y/n): ").lower()
            return confirm == "y"
        return True

    def create_generation_plan(
        self, total_count: int, category_weights: dict[str, float] | None = None
    ) -> dict[str, dict[str, Any]]:
        """카테고리별 생성 계획 수립"""
        if category_weights is None:
            # 기본 가중치 사용
            category_weights = {
                category: info.get("weight", 1) for category, info in EVENT_CATEGORIES.items()
            }

        # 가중치 합계 계산
        total_weight = sum(category_weights.values())

        # 카테고리별 이벤트 수 계산
        plan = {}
        remaining = total_count

        for category, weight in category_weights.items():
            if category not in EVENT_CATEGORIES:
                continue

            # 가중치에 비례하여 이벤트 수 할당
            count = int(total_count * (weight / total_weight))
            plan[category] = {
                "count": count,
                "description": EVENT_CATEGORIES[category].get("description", ""),
            }
            remaining -= count

        # 남은 이벤트 분배 (반올림 오차 처리)
        if remaining > 0:
            # 가중치가 가장 높은 카테고리에 할당
            max_category = max(category_weights.items(), key=lambda x: x[1])[0]
            plan[max_category]["count"] += remaining

        return plan

    def print_plan_summary(self, plan: dict[str, dict[str, Any]]) -> None:
        """생성 계획 요약 출력"""
        total_categories = len(plan)
        total_target = sum(info["count"] for info in plan.values())

        print(f"총 {total_categories}개 카테고리에서 {total_target}개 이벤트 생성 예정")

        for category, info in plan.items():
            print(f"  - {category}: {info['count']}개")
        print(f"  [TOTAL] 총 목표: {total_target}개")

        # 예상 비용 계산
        estimated_cost = total_target * GENERATION_CONFIG["COST_PER_EVENT"]
        print(f"\n[COST] 예상 비용: ~${estimated_cost:.2f} (이벤트당 약 $0.05)")
        if not self._check_cost_warning(estimated_cost):
            print("생성 취소됨")
            sys.exit(0)


def main() -> int:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="대량 이벤트 생성 도구")
    parser.add_argument("--count", type=int, default=10, help="생성할 이벤트 수 (기본값: 10)")
    parser.add_argument("--category", help="특정 카테고리만 생성 (기본값: 모든 카테고리)")
    parser.add_argument("--output", help="출력 디렉토리 (기본값: data/generated_events)")
    parser.add_argument("--api-key", help="OpenAI API 키")
    args = parser.parse_args()

    # API 키 확인
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "오류: OpenAI API 키가 필요합니다. --api-key 옵션이나 OPENAI_API_KEY 환경 변수를 설정하세요."
        )
        return 1

    # 출력 디렉토리 설정
    output_dir = Path(args.output) if args.output else project_root / "data" / "generated_events"

    # 이벤트 생성기 초기화
    generator = EventGenerator(api_key, output_dir)

    # 생성 계획 수립
    if args.category:
        if args.category not in EVENT_CATEGORIES:
            print(f"오류: 알 수 없는 카테고리 '{args.category}'")
            print(f"사용 가능한 카테고리: {', '.join(EVENT_CATEGORIES.keys())}")
            return 1

        # 단일 카테고리 생성
        plan = {
            args.category: {
                "count": args.count,
                "description": EVENT_CATEGORIES[args.category].get("description", ""),
            }
        }
    else:
        # 모든 카테고리 가중치 기반 생성
        plan = generator.create_generation_plan(args.count)

    # 계획 요약 출력
    generator.print_plan_summary(plan)

    # 이벤트 생성
    print("\n[생성 시작]")
    events_by_category = generator.generate_events_by_plan(plan)

    # 결과 저장
    total_saved, saved_files = generator.save_events(events_by_category)

    # 결과 요약
    print("\n[생성 완료]")
    print(
        f"총 생성: {generator.generated_count}개 (유효: {generator.valid_count}, 무효: {generator.invalid_count})"
    )
    print(f"저장된 파일: {len(saved_files)}개")
    print(f"총 비용: ${generator.total_cost:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
파일: dev_tools/event_validator.py
목적: 이벤트 데이터 검증 및 품질 평가 도구
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import tomllib  # Python 3.11+
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set


class EventType(Enum):
    """이벤트 타입 열거형"""

    RANDOM = "RANDOM"
    THRESHOLD = "THRESHOLD"
    SCHEDULED = "SCHEDULED"
    CASCADE = "CASCADE"


class TriggerCondition(Enum):
    """트리거 조건 열거형"""

    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    EQUAL = "equal"


class ValidationError(Exception):
    """이벤트 검증 오류"""

    pass


class EventValidator:
    def __init__(self) -> None:
        """초기화"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.event_ids: Set[str] = set()

    def validate_file(self, file_path: Path) -> bool:
        """
        단일 파일 검증

        Args:
            file_path: 검증할 TOML/JSON 파일 경로

        Returns:
            검증 성공 여부
        """
        self.errors = []
        self.warnings = []

        try:
            # 파일 확장자에 따라 로더 선택
            if file_path.suffix.lower() == ".toml":
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
            elif file_path.suffix.lower() == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                self.errors.append(f"지원하지 않는 파일 형식: {file_path.suffix}")
                return False

            # 이벤트 데이터 추출
            events = data.get("events", [])
            if not events:
                self.warnings.append(f"이벤트가 없습니다: {file_path}")
                return True

            # 각 이벤트 검증
            for event in events:
                self._validate_event(event)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"파일 처리 오류: {str(e)}")
            return False

    def validate_directory(self, directory_path: Path) -> bool:
        """
        디렉토리 내 모든 TOML/JSON 파일 검증

        Args:
            directory_path: 검증할 디렉토리 경로

        Returns:
            검증 성공 여부
        """
        all_valid = True
        self.event_ids = set()  # ID 유일성 검사를 위해 초기화

        # TOML 파일 먼저 처리
        for file_path in directory_path.glob("**/*.toml"):
            if not self.validate_file(file_path):
                all_valid = False

        # JSON 파일 처리
        for file_path in directory_path.glob("**/*.json"):
            if not self.validate_file(file_path):
                all_valid = False

        return all_valid

    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """
        단일 이벤트 검증

        Args:
            event: 이벤트 데이터 딕셔너리

        Returns:
            검증 성공 여부
        """
        # 필수 필드 검증
        required_fields = ["id", "type"]
        for field in required_fields:
            if field not in event:
                self.errors.append(f"필수 필드 누락: {field}")
                return False

        # ID 유일성 검증
        event_id = event["id"]
        if event_id in self.event_ids:
            self.errors.append(f"중복된 이벤트 ID: {event_id}")
            return False
        self.event_ids.add(event_id)

        # 이벤트 타입 검증
        try:
            event_type = EventType(event["type"])
        except ValueError:
            self.errors.append(f"유효하지 않은 이벤트 타입: {event['type']}")
            return False

        # 타입별 필수 필드 검증
        if event_type == EventType.RANDOM:
            if "probability" not in event:
                self.errors.append(f"RANDOM 이벤트에 probability 필드 누락: {event_id}")
                return False
            if not (0.0 <= event["probability"] <= 1.0):
                self.errors.append(f"확률 범위 오류 (0.0-1.0): {event['probability']}")
                return False

        elif event_type in [EventType.THRESHOLD, EventType.CASCADE]:
            if "trigger" not in event:
                self.errors.append(
                    f"{event_type.value} 이벤트에 trigger 필드 누락: {event_id}"
                )
                return False
            if not self._validate_trigger(event["trigger"]):
                return False

        elif event_type == EventType.SCHEDULED:
            if "schedule" not in event:
                self.errors.append(f"SCHEDULED 이벤트에 schedule 필드 누락: {event_id}")
                return False
            if not isinstance(event["schedule"], int) or event["schedule"] <= 0:
                self.errors.append(f"schedule은 양의 정수여야 함: {event['schedule']}")
                return False

        # 쿨다운 검증
        if "cooldown" in event and (
            not isinstance(event["cooldown"], int) or event["cooldown"] < 0
        ):
            self.errors.append(f"cooldown은 0 이상의 정수여야 함: {event['cooldown']}")
            return False

        # 효과 검증
        if "effects" not in event or not event["effects"]:
            self.errors.append(f"effects 필드 누락 또는 비어 있음: {event_id}")
            return False

        for effect in event["effects"]:
            if not self._validate_effect(effect):
                return False

        return True

    def _validate_trigger(self, trigger: Dict[str, Any]) -> bool:
        """
        트리거 검증

        Args:
            trigger: 트리거 데이터 딕셔너리

        Returns:
            검증 성공 여부
        """
        required_fields = ["metric", "condition", "value"]
        for field in required_fields:
            if field not in trigger:
                self.errors.append(f"트리거 필수 필드 누락: {field}")
                return False

        # 조건 검증
        try:
            TriggerCondition(trigger["condition"])
        except ValueError:
            self.errors.append(f"유효하지 않은 트리거 조건: {trigger['condition']}")
            return False

        return True

    def _validate_effect(self, effect: Dict[str, Any]) -> bool:
        """
        효과 검증

        Args:
            effect: 효과 데이터 딕셔너리

        Returns:
            검증 성공 여부
        """
        required_fields = ["metric", "formula"]
        for field in required_fields:
            if field not in effect:
                self.errors.append(f"효과 필수 필드 누락: {field}")
                return False

        # 포뮬러 검증
        if not self._validate_formula(effect["formula"]):
            return False

        return True

    def _validate_formula(self, formula: str) -> bool:
        """
        포뮬러 문자열 검증

        Args:
            formula: 검증할 포뮬러 문자열

        Returns:
            검증 성공 여부
        """
        # 퍼센트 표기법 처리
        if formula.endswith("%"):
            formula = formula[:-1] + " * 0.01 * value"

        # 간단한 숫자 리터럴 처리
        try:
            float(formula)
            return True
        except ValueError:
            pass

        # 안전한 수식 평가 시도
        try:
            # 실제 구현에서는 ast.parse와 노드 화이트리스트 검사 필요
            ast.parse(formula, mode="eval")
            return True
        except SyntaxError:
            self.errors.append(f"포뮬러 구문 오류: {formula}")
            return False

    def calculate_quality_metrics(
        self, events: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        이벤트 품질 메트릭 계산

        Args:
            events: 이벤트 데이터 리스트

        Returns:
            품질 메트릭 딕셔너리
        """
        metrics = {
            "diversity_score": self._calculate_diversity_score(events),
            "tradeoff_clarity": self._calculate_tradeoff_clarity(events),
            "cultural_authenticity": self._calculate_cultural_authenticity(events),
            "replayability": self._calculate_replayability(events),
        }

        return metrics

    def _calculate_diversity_score(self, events: List[Dict[str, Any]]) -> float:
        """
        카테고리 분포의 균등성 (Shannon Entropy 기반)

        Returns:
            0.0 ~ 1.0 (목표: >= 0.8)
        """
        # 카테고리별 이벤트 수 계산
        categories: Dict[str, int] = {}
        for event in events:
            category = event.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        if not categories:
            return 0.0

        # Shannon Entropy 계산
        total = sum(categories.values())
        entropy = 0.0
        for count in categories.values():
            p = count / total
            entropy -= p * math.log(p)

        # 정규화 (0-1 범위)
        max_entropy = math.log(len(categories))
        if max_entropy == 0:
            return 0.0

        return entropy / max_entropy

    def _calculate_tradeoff_clarity(self, events: List[Dict[str, Any]]) -> float:
        """
        각 선택지가 명확한 득실을 가지는지

        Returns:
            0.0 ~ 1.0 (목표: >= 0.9)
        """
        if not events:
            return 0.0

        events_with_tradeoffs = 0

        for event in events:
            choices = event.get("choices", [])
            if self._has_clear_tradeoffs(choices):
                events_with_tradeoffs += 1

        return events_with_tradeoffs / len(events)

    def _has_clear_tradeoffs(self, choices: List[Dict[str, Any]]) -> bool:
        """
        선택지들이 명확한 트레이드오프를 가지는지 확인

        Args:
            choices: 선택지 리스트

        Returns:
            트레이드오프 존재 여부
        """
        if len(choices) < 2:
            return False

        # 각 선택지가 최소 하나의 긍정적 효과와 하나의 부정적 효과를 가지는지 확인
        for choice in choices:
            effects = choice.get("effects", {})
            has_positive = False
            has_negative = False

            for metric, value in effects.items():
                if value > 0:
                    has_positive = True
                elif value < 0:
                    has_negative = True

            if not (has_positive and has_negative):
                return False

        return True

    def _calculate_cultural_authenticity(self, events: List[Dict[str, Any]]) -> float:
        """
        한국 치킨집 문화 반영도

        Returns:
            0.0 ~ 1.0 (목표: >= 0.7)
        """
        if not events:
            return 0.0

        # 한국 치킨집 관련 키워드
        keywords = [
            "배달",
            "프랜차이즈",
            "단골",
            "동네",
            "치킨",
            "맥주",
            "소주",
            "양념",
            "후라이드",
            "반반",
            "사장님",
            "알바",
            "주문",
            "포장",
            "매장",
            "손님",
            "서비스",
            "할인",
            "이벤트",
            "마케팅",
        ]

        authentic_events = 0

        for event in events:
            text_ko = event.get("text_ko", "")
            name_ko = event.get("name_ko", "")

            # 키워드 매칭
            matched_keywords = 0
            for keyword in keywords:
                if keyword in text_ko or keyword in name_ko:
                    matched_keywords += 1

            # 최소 2개 이상의 키워드가 매칭되면 진정성 있는 이벤트로 간주
            if matched_keywords >= 2:
                authentic_events += 1

        return authentic_events / len(events)

    def _calculate_replayability(self, events: List[Dict[str, Any]]) -> float:
        """
        재플레이 가치 (조건 다양성, 확률 분포 기반)

        Returns:
            0.0 ~ 1.0 (목표: >= 0.8)
        """
        if not events:
            return 0.0

        # 조건 다양성 및 확률 분포 평가
        condition_variety = 0
        probability_spread = 0

        # 조건 유형 카운트
        condition_types = set()
        probabilities = []

        for event in events:
            # 트리거 조건 다양성
            if "trigger" in event:
                condition = event["trigger"].get("condition")
                if condition:
                    condition_types.add(condition)

            # 확률 분포
            if "probability" in event:
                probabilities.append(event["probability"])

        # 조건 다양성 점수 (최대 3가지 조건)
        condition_variety = min(1.0, len(condition_types) / 3)

        # 확률 분포 점수 (표준편차 기반)
        if probabilities:
            mean = sum(probabilities) / len(probabilities)
            variance = sum((p - mean) ** 2 for p in probabilities) / len(probabilities)
            std_dev = math.sqrt(variance)

            # 적절한 표준편차 (0.1-0.3 범위가 이상적)
            if 0.1 <= std_dev <= 0.3:
                probability_spread = 1.0
            elif std_dev < 0.1:
                probability_spread = std_dev / 0.1
            else:  # std_dev > 0.3
                probability_spread = 0.3 / std_dev

        # 종합 점수 (조건 다양성 50%, 확률 분포 50%)
        return (condition_variety * 0.5) + (probability_spread * 0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description="치킨집 경영 게임 이벤트 검증기")
    parser.add_argument(
        "--file", type=str, help="검증할 단일 이벤트 파일 경로 (TOML 또는 JSON)"
    )
    parser.add_argument("--dir", type=str, help="검증할 이벤트 디렉토리 경로")
    parser.add_argument(
        "--metrics", action="store_true", help="품질 메트릭 계산 및 출력"
    )

    args = parser.parse_args()

    if not args.file and not args.dir:
        print("❌ 파일 또는 디렉토리 경로를 지정해야 합니다.")
        return 1

    validator = EventValidator()
    success = False

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
            return 1

        print(f"🔍 파일 검증 중: {file_path}")
        success = validator.validate_file(file_path)

    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ 디렉토리를 찾을 수 없습니다: {args.dir}")
            return 1

        print(f"🔍 디렉토리 검증 중: {dir_path}")
        success = validator.validate_directory(dir_path)

    # 결과 출력
    if success:
        print("✅ 검증 성공!")
        if validator.warnings:
            print("\n⚠️ 경고:")
            for warning in validator.warnings:
                print(f"  - {warning}")
    else:
        print("❌ 검증 실패!")
        print("\n오류:")
        for error in validator.errors:
            print(f"  - {error}")

    # 품질 메트릭 계산 (요청 시)
    if args.metrics and success:
        # 이벤트 데이터 로드
        events = []
        if args.file:
            file_path = Path(args.file)
            if file_path.suffix.lower() == ".toml":
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    events = data.get("events", [])
            elif file_path.suffix.lower() == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    events = data.get("events", [])

        elif args.dir:
            # 디렉토리 내 모든 파일에서 이벤트 수집
            dir_path = Path(args.dir)
            for file_path in dir_path.glob("**/*.toml"):
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    events.extend(data.get("events", []))

            for file_path in dir_path.glob("**/*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    events.extend(data.get("events", []))

        # 메트릭 계산 및 출력
        metrics = validator.calculate_quality_metrics(events)
        print("\n📊 품질 메트릭:")
        for name, value in metrics.items():
            status = "✅" if value >= 0.7 else "⚠️"
            print(f"  {status} {name}: {value:.2f}")

    return 0 if success else 1


if __name__ == "__main__":
    main()

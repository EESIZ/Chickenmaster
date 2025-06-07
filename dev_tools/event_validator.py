#!/usr/bin/env python3
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
from pathlib import Path
from typing import Any, ClassVar

from game_constants import MAGIC_NUMBER_ZERO, MAGIC_NUMBER_ONE, MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIFTY, MAGIC_NUMBER_ONE_HUNDRED, PROBABILITY_LOW_THRESHOLD, PROBABILITY_HIGH_THRESHOLD


class EventValidator:
    """이벤트 데이터 검증 도구"""

    # 검증 규칙 정의
    VALIDATION_RULES: ClassVar[dict[str, dict[str, Any]]] = {
        "required_fields": {
            "id": str,
            "name": str,
            "description": str,
            "category": str,
            "type": str,
        },
        "optional_fields": {
            "name_ko": str,
            "description_ko": str,
            "triggers": list,
            "effects": list,
            "choices": list,
            "tags": list,
            "weight": (int, float),
            "cooldown": int,
            "prerequisites": list,
        },
        "category_values": ["daily_routine", "crisis", "opportunity", "random"],
        "type_values": ["triggered", "random", "choice"],
    }

    def __init__(self, input_file: str, output_file: str | None = None):
        """
        초기화

        Args:
            input_file: 검증할 이벤트 파일 경로
            output_file: 검증 결과 출력 파일 경로 (선택사항)
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else None
        self.validation_results: dict[str, Any] = {}

    def load_events(self) -> dict[str, Any]:
        """
        이벤트 파일 로드

        Returns:
            이벤트 데이터 딕셔너리

        Raises:
            FileNotFoundError: 파일을 찾을 수 없는 경우
            ValueError: 파일 형식이 올바르지 않은 경우
        """
        if not self.input_file.exists():
            msg = f"파일을 찾을 수 없습니다: {self.input_file}"
            raise FileNotFoundError(msg)

        try:
            if self.input_file.suffix.lower() == ".json":
                with self.input_file.open(encoding="utf-8") as f:
                    return json.load(f)
            elif self.input_file.suffix.lower() == ".toml":
                with self.input_file.open("rb") as f:
                    return tomllib.load(f)
            else:
                msg = f"지원하지 않는 파일 형식: {self.input_file.suffix}"
                raise ValueError(msg)
        except Exception as e:
            msg = f"파일 로드 오류: {e!s}"
            raise ValueError(msg) from e

    def validate_event_structure(self, event: dict[str, Any]) -> list[str]:
        """
        이벤트 구조 검증

        Args:
            event: 검증할 이벤트 데이터

        Returns:
            검증 오류 목록
        """
        errors = []

        # 필수 필드 검증
        for field, expected_type in self.VALIDATION_RULES["required_fields"].items():
            if field not in event:
                errors.append(f"필수 필드 누락: {field}")
            elif not isinstance(event[field], expected_type):
                errors.append(f"필드 타입 오류: {field} (기대: {expected_type.__name__})")

        # 선택 필드 타입 검증
        for field, expected_type in self.VALIDATION_RULES["optional_fields"].items():
            if field in event and not isinstance(event[field], expected_type):
                errors.append(f"필드 타입 오류: {field} (기대: {expected_type})")

        # 카테고리 값 검증
        if "category" in event and event["category"] not in self.VALIDATION_RULES["category_values"]:
            errors.append(f"잘못된 카테고리: {event['category']}")

        # 타입 값 검증
        if "type" in event and event["type"] not in self.VALIDATION_RULES["type_values"]:
            errors.append(f"잘못된 타입: {event['type']}")

        return errors

    def validate_triggers(self, triggers: list[dict[str, Any]]) -> list[str]:
        """
        트리거 검증

        Args:
            triggers: 트리거 목록

        Returns:
            검증 오류 목록
        """
        errors = []

        for i, trigger in enumerate(triggers):
            if not isinstance(trigger, dict):
                errors.append(f"트리거 {i}: 딕셔너리가 아님")
                continue

            # 필수 필드 검증
            required_fields = ["metric", "condition", "value"]
            for field in required_fields:
                if field not in trigger:
                    errors.append(f"트리거 {i}: 필수 필드 누락 - {field}")

            # 조건 값 검증
            if "condition" in trigger:
                valid_conditions = ["equal", "not_equal", "greater_than", "less_than", "greater_than_or_equal", "less_than_or_equal"]
                if trigger["condition"] not in valid_conditions:
                    errors.append(f"트리거 {i}: 잘못된 조건 - {trigger['condition']}")

            # 값 타입 검증
            if "value" in trigger and not isinstance(trigger["value"], (int, float)):
                errors.append(f"트리거 {i}: 값이 숫자가 아님")

        return errors

    def validate_effects(self, effects: list[dict[str, Any]]) -> list[str]:
        """
        효과 검증

        Args:
            effects: 효과 목록

        Returns:
            검증 오류 목록
        """
        errors = []

        for i, effect in enumerate(effects):
            if not isinstance(effect, dict):
                errors.append(f"효과 {i}: 딕셔너리가 아님")
                continue

            # 필수 필드 검증
            required_fields = ["metric", "value"]
            for field in required_fields:
                if field not in effect:
                    errors.append(f"효과 {i}: 필수 필드 누락 - {field}")

            # 값 타입 검증
            if "value" in effect and not isinstance(effect["value"], (int, float)):
                errors.append(f"효과 {i}: 값이 숫자가 아님")

            # 값 범위 검증 (합리적인 범위)
            if "value" in effect:
                value = effect["value"]
                if abs(value) > 1000:  # 너무 큰 값
                    errors.append(f"효과 {i}: 값이 너무 큼 - {value}")

        return errors

    def validate_choices(self, choices: list[dict[str, Any]]) -> list[str]:
        """
        선택지 검증

        Args:
            choices: 선택지 목록

        Returns:
            검증 오류 목록
        """
        errors = []

        for i, choice in enumerate(choices):
            if not isinstance(choice, dict):
                errors.append(f"선택지 {i}: 딕셔너리가 아님")
                continue

            # 필수 필드 검증
            required_fields = ["id", "text", "effects"]
            for field in required_fields:
                if field not in choice:
                    errors.append(f"선택지 {i}: 필수 필드 누락 - {field}")

            # 효과 검증
            if "effects" in choice:
                choice_errors = self.validate_effects(choice["effects"])
                errors.extend([f"선택지 {i} - {error}" for error in choice_errors])

        return errors

    def validate_balance(self, event: dict[str, Any]) -> list[str]:
        """
        게임 밸런스 검증

        Args:
            event: 검증할 이벤트

        Returns:
            밸런스 관련 경고 목록
        """
        warnings = []

        # 효과 밸런스 검증
        if "effects" in event:
            total_positive = sum(
                effect["value"] for effect in event["effects"]
                if effect.get("value", 0) > MAGIC_NUMBER_ZERO
            )
            total_negative = sum(
                abs(effect["value"]) for effect in event["effects"]
                if effect.get("value", 0) < MAGIC_NUMBER_ZERO
            )

            # 너무 긍정적이거나 부정적인 이벤트 경고
            if total_positive > total_negative * 2:
                warnings.append("이벤트가 너무 긍정적임 (트레이드오프 부족)")
            elif total_negative > total_positive * 2:
                warnings.append("이벤트가 너무 부정적임 (밸런스 문제)")

        # 선택지 밸런스 검증
        if "choices" in event and len(event["choices"]) > 1:
            choice_values = []
            for choice in event["choices"]:
                if "effects" in choice:
                    total_value = sum(effect.get("value", 0) for effect in choice["effects"])
                    choice_values.append(total_value)

            if choice_values:
                max_value = max(choice_values)
                min_value = min(choice_values)
                if max_value - min_value > MAGIC_NUMBER_FIFTY:  # 차이가 너무 큰 경우
                    warnings.append("선택지 간 밸런스 차이가 큼")

        return warnings

    def validate_uncertainty_elements(self, event: dict[str, Any]) -> list[str]:
        """
        불확실성 요소 검증

        Args:
            event: 검증할 이벤트

        Returns:
            불확실성 관련 평가 목록
        """
        assessments = []

        # 랜덤 요소 확인
        if event.get("type") == "random":
            assessments.append("✓ 랜덤 이벤트 - 불확실성 요소 포함")

        # 확률적 효과 확인
        if "effects" in event:
            for effect in event["effects"]:
                if "probability" in effect:
                    prob = effect["probability"]
                    if PROBABILITY_LOW_THRESHOLD <= prob <= PROBABILITY_HIGH_THRESHOLD:
                        assessments.append("✓ 확률적 효과 - 적절한 불확실성")
                    else:
                        assessments.append("⚠ 확률적 효과 - 불확실성 부족")

        # 복잡한 선택지 확인
        if "choices" in event and len(event["choices"]) >= 3:
            assessments.append("✓ 다중 선택지 - 결과 예측 어려움")

        return assessments

    def validate_no_right_answer_principle(self, event: dict[str, Any]) -> list[str]:
        """
        정답 없음 원칙 검증

        Args:
            event: 검증할 이벤트

        Returns:
            정답 없음 원칙 관련 평가 목록
        """
        assessments = []

        # 선택지가 있는 경우
        if "choices" in event and len(event["choices"]) > 1:
            has_clear_winner = False
            choice_scores = []

            for choice in event["choices"]:
                if "effects" in choice:
                    # 각 선택지의 총 점수 계산 (단순화)
                    total_score = sum(effect.get("value", 0) for effect in choice["effects"])
                    choice_scores.append(total_score)

            if choice_scores:
                max_score = max(choice_scores)
                min_score = min(choice_scores)

                # 명확한 승자가 있는지 확인
                if max_score > min_score + MAGIC_NUMBER_TWENTY:
                    has_clear_winner = True

            if has_clear_winner:
                assessments.append("⚠ 명확한 최선의 선택지 존재 - 정답 없음 원칙 위배")
            else:
                assessments.append("✓ 선택지 간 트레이드오프 존재 - 정답 없음 원칙 준수")

        # 단순 효과만 있는 경우
        elif "effects" in event:
            positive_effects = [e for e in event["effects"] if e.get("value", 0) > MAGIC_NUMBER_ZERO]
            negative_effects = [e for e in event["effects"] if e.get("value", 0) < MAGIC_NUMBER_ZERO]

            if positive_effects and negative_effects:
                assessments.append("✓ 긍정적/부정적 효과 혼재 - 트레이드오프 존재")
            elif positive_effects and not negative_effects:
                assessments.append("⚠ 긍정적 효과만 존재 - 트레이드오프 부족")
            elif negative_effects and not positive_effects:
                assessments.append("⚠ 부정적 효과만 존재 - 밸런스 문제")

        return assessments

    def validate_events(self) -> dict[str, Any]:
        """
        전체 이벤트 검증 실행

        Returns:
            검증 결과 딕셔너리
        """
        try:
            data = self.load_events()
        except (FileNotFoundError, ValueError) as e:
            return {"error": str(e), "events": []}

        events = data.get("events", [])
        if not events:
            return {"error": "이벤트 데이터가 없습니다", "events": []}

        results = {
            "total_events": len(events),
            "valid_events": 0,
            "events": [],
            "summary": {
                "structure_errors": 0,
                "balance_warnings": 0,
                "uncertainty_assessments": 0,
                "no_right_answer_assessments": 0,
            },
        }

        for i, event in enumerate(events):
            event_result = {
                "index": i,
                "id": event.get("id", f"event_{i}"),
                "structure_errors": [],
                "balance_warnings": [],
                "uncertainty_assessments": [],
                "no_right_answer_assessments": [],
            }

            # 구조 검증
            structure_errors = self.validate_event_structure(event)
            event_result["structure_errors"] = structure_errors

            # 트리거 검증
            if "triggers" in event:
                trigger_errors = self.validate_triggers(event["triggers"])
                event_result["structure_errors"].extend(trigger_errors)

            # 효과 검증
            if "effects" in event:
                effect_errors = self.validate_effects(event["effects"])
                event_result["structure_errors"].extend(effect_errors)

            # 선택지 검증
            if "choices" in event:
                choice_errors = self.validate_choices(event["choices"])
                event_result["structure_errors"].extend(choice_errors)

            # 밸런스 검증
            balance_warnings = self.validate_balance(event)
            event_result["balance_warnings"] = balance_warnings

            # 불확실성 검증
            uncertainty_assessments = self.validate_uncertainty_elements(event)
            event_result["uncertainty_assessments"] = uncertainty_assessments

            # 정답 없음 원칙 검증
            no_right_answer_assessments = self.validate_no_right_answer_principle(event)
            event_result["no_right_answer_assessments"] = no_right_answer_assessments

            # 통계 업데이트
            if not event_result["structure_errors"]:
                results["valid_events"] += 1

            results["summary"]["structure_errors"] += len(event_result["structure_errors"])
            results["summary"]["balance_warnings"] += len(event_result["balance_warnings"])
            results["summary"]["uncertainty_assessments"] += len(event_result["uncertainty_assessments"])
            results["summary"]["no_right_answer_assessments"] += len(event_result["no_right_answer_assessments"])

            results["events"].append(event_result)

        self.validation_results = results
        return results

    def save_results(self, results: dict[str, Any]) -> None:
        """
        검증 결과 저장

        Args:
            results: 검증 결과
        """
        if not self.output_file:
            return

        try:
            with self.output_file.open("w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 검증 결과가 {self.output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 결과 저장 오류: {e!s}")

    def print_summary(self, results: dict[str, Any]) -> None:
        """
        검증 결과 요약 출력

        Args:
            results: 검증 결과
        """
        if "error" in results:
            print(f"❌ 검증 오류: {results['error']}")
            return

        print(f"\n📊 이벤트 검증 결과 요약")
        print(f"총 이벤트 수: {results['total_events']}")
        print(f"유효한 이벤트 수: {results['valid_events']}")
        print(f"성공률: {results['valid_events'] / results['total_events'] * 100:.1f}%")

        summary = results["summary"]
        print(f"\n📈 검증 통계:")
        print(f"  구조 오류: {summary['structure_errors']}개")
        print(f"  밸런스 경고: {summary['balance_warnings']}개")
        print(f"  불확실성 평가: {summary['uncertainty_assessments']}개")
        print(f"  정답 없음 평가: {summary['no_right_answer_assessments']}개")

        # 주요 문제 이벤트 출력
        problem_events = [
            event for event in results["events"]
            if event["structure_errors"] or len(event["balance_warnings"]) > 2
        ]

        if problem_events:
            print(f"\n⚠️ 주요 문제 이벤트 ({len(problem_events)}개):")
            for event in problem_events[:5]:  # 최대 5개만 출력
                print(f"  - {event['id']}: {len(event['structure_errors'])}개 오류")

    def process(self) -> None:
        """검증 프로세스 실행"""
        print(f"🔍 이벤트 검증 시작: {self.input_file}")

        results = self.validate_events()
        self.print_summary(results)

        if self.output_file:
            self.save_results(results)

    def calculate_quality_metrics(self, events: list[dict[str, Any]]) -> dict[str, float]:
        """
        이벤트 품질 메트릭 계산

        Args:
            events: 이벤트 목록

        Returns:
            품질 메트릭 딕셔너리
        """
        if not events:
            return {
                "diversity_score": 0.0,
                "tradeoff_clarity": 0.0,
                "cultural_authenticity": 0.0,
                "replayability": 0.0,
            }

        # 다양성 점수 계산
        categories = set()
        types = set()
        for event in events:
            if "category" in event:
                categories.add(event["category"])
            if "type" in event:
                types.add(event["type"])

        diversity_score = min(1.0, (len(categories) + len(types)) / 10.0)

        # 트레이드오프 명확성 계산
        tradeoff_events = 0
        for event in events:
            if "effects" in event and len(event["effects"]) > 1:
                tradeoff_events += 1

        tradeoff_clarity = min(1.0, tradeoff_events / len(events))

        # 문화적 진정성 (한국어 텍스트 비율)
        korean_events = 0
        for event in events:
            if "name_ko" in event or "text_ko" in event:
                korean_events += 1

        cultural_authenticity = korean_events / len(events)

        # 재플레이성 (확률 기반 이벤트 비율)
        random_events = 0
        for event in events:
            if event.get("type") == "RANDOM" or event.get("probability", 0) < 1.0:
                random_events += 1

        replayability = random_events / len(events)

        return {
            "diversity_score": diversity_score,
            "tradeoff_clarity": tradeoff_clarity,
            "cultural_authenticity": cultural_authenticity,
            "replayability": replayability,
        }


def main() -> None:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="이벤트 데이터 검증 도구")
    parser.add_argument("input", help="검증할 이벤트 파일 경로")
    parser.add_argument("--output", help="검증 결과 출력 파일 경로")

    args = parser.parse_args()

    validator = EventValidator(args.input, args.output)
    validator.process()


if __name__ == "__main__":
    main()


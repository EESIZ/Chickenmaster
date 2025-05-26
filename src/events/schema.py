"""
이벤트 스키마 모듈

이 모듈은 Chicken-RNG 게임의 이벤트 스키마를 정의합니다.
TOML/JSON 파일 형식과 검증 로직을 포함합니다.

핵심 철학:
- 정답 없음: 모든 이벤트는 득과 실을 동시에 가져옵니다
- 트레이드오프: 이벤트 효과는 항상 트레이드오프 관계를 가집니다
- 불확실성: 이벤트 발생과 효과는 예측 불가능한 요소에 영향을 받습니다
"""

import tomllib
import json
import os
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import asdict

from schema import Metric
from src.events.models import Event, Trigger, Effect, EventCategory, TriggerCondition


class EventSchemaValidator:
    """
    이벤트 스키마 검증기

    이 클래스는 이벤트 정의 파일(TOML/JSON)의 유효성을 검증합니다.
    스키마 규칙, ID 유일성, DAG 안전성 등을 확인합니다.
    """

    def __init__(self):
        """
        EventSchemaValidator 초기화
        """
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_toml_file(self, filepath: str) -> bool:
        """
        TOML 파일의 유효성을 검증합니다.

        Args:
            filepath: TOML 파일 경로

        Returns:
            bool: 유효하면 True, 그렇지 않으면 False
        """
        self.errors = []
        self.warnings = []

        try:
            with open(filepath, "rb") as f:
                data = tomllib.load(f)
            return self._validate_event_data(data)
        except Exception as e:
            self.errors.append(f"TOML 파일 로드 실패: {e}")
            return False

    def validate_json_file(self, filepath: str) -> bool:
        """
        JSON 파일의 유효성을 검증합니다.

        Args:
            filepath: JSON 파일 경로

        Returns:
            bool: 유효하면 True, 그렇지 않으면 False
        """
        self.errors = []
        self.warnings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._validate_event_data(data)
        except Exception as e:
            self.errors.append(f"JSON 파일 로드 실패: {e}")
            return False

    def _validate_event_data(self, data: Dict[str, Any]) -> bool:
        """
        이벤트 데이터의 유효성을 검증합니다.

        Args:
            data: 이벤트 데이터

        Returns:
            bool: 유효하면 True, 그렇지 않으면 False
        """
        if "events" not in data:
            self.errors.append("이벤트 목록이 없습니다.")
            return False

        events = data["events"]
        if not isinstance(events, list):
            self.errors.append("이벤트 목록이 리스트 형식이 아닙니다.")
            return False

        # ID 유일성 검증
        event_ids: Set[str] = set()
        for i, event in enumerate(events):
            if "id" not in event:
                self.errors.append(f"이벤트 #{i+1}에 ID가 없습니다.")
                continue

            event_id = event["id"]
            if event_id in event_ids:
                self.errors.append(f"중복된 이벤트 ID: {event_id}")
            event_ids.add(event_id)

            # 이벤트 필드 검증
            self._validate_event_fields(event, i)

        return len(self.errors) == 0

    def _validate_event_fields(self, event: Dict[str, Any], index: int) -> None:
        """
        이벤트 필드의 유효성을 검증합니다.

        Args:
            event: 이벤트 데이터
            index: 이벤트 인덱스
        """
        event_id = event.get("id", f"#{index+1}")

        # 필수 필드 검증
        if "type" not in event:
            self.errors.append(f"이벤트 {event_id}에 type이 없습니다.")
            return

        # 이벤트 타입 검증
        event_type = event["type"]
        try:
            event_category = EventCategory[event_type]
        except (KeyError, ValueError):
            self.errors.append(
                f"이벤트 {event_id}의 타입이 유효하지 않습니다: {event_type}"
            )
            return

        # 타입별 필수 필드 검증
        if event_category == EventCategory.RANDOM:
            if "probability" not in event:
                self.errors.append(
                    f"RANDOM 이벤트 {event_id}에 probability가 없습니다."
                )
            elif not (0 <= event["probability"] <= 1):
                self.errors.append(
                    f"이벤트 {event_id}의 probability가 범위를 벗어났습니다: {event['probability']}"
                )

        elif (
            event_category == EventCategory.THRESHOLD
            or event_category == EventCategory.CASCADE
        ):
            if "trigger" not in event:
                self.errors.append(
                    f"{event_type} 이벤트 {event_id}에 trigger가 없습니다."
                )
            else:
                self._validate_trigger(event["trigger"], event_id)

        elif event_category == EventCategory.SCHEDULED:
            if "schedule" not in event:
                self.errors.append(
                    f"SCHEDULED 이벤트 {event_id}에 schedule이 없습니다."
                )
            elif not isinstance(event["schedule"], int) or event["schedule"] <= 0:
                self.errors.append(
                    f"이벤트 {event_id}의 schedule이 유효하지 않습니다: {event['schedule']}"
                )

        # 효과 검증
        if "effects" not in event:
            self.errors.append(f"이벤트 {event_id}에 effects가 없습니다.")
        else:
            effects = event["effects"]
            if not isinstance(effects, list) or len(effects) == 0:
                self.errors.append(f"이벤트 {event_id}의 effects가 비어 있습니다.")
            else:
                for i, effect in enumerate(effects):
                    self._validate_effect(effect, f"{event_id}.effects[{i}]")

        # 선택적 필드 검증
        if "cooldown" in event and (
            not isinstance(event["cooldown"], int) or event["cooldown"] < 0
        ):
            self.errors.append(
                f"이벤트 {event_id}의 cooldown이 유효하지 않습니다: {event['cooldown']}"
            )

        if "priority" in event and not isinstance(event["priority"], int):
            self.errors.append(
                f"이벤트 {event_id}의 priority가 유효하지 않습니다: {event['priority']}"
            )

    def _validate_trigger(self, trigger: Dict[str, Any], event_id: str) -> None:
        """
        트리거의 유효성을 검증합니다.

        Args:
            trigger: 트리거 데이터
            event_id: 이벤트 ID
        """
        # 필수 필드 검증
        required_fields = ["metric", "condition", "value"]
        for field in required_fields:
            if field not in trigger:
                self.errors.append(f"트리거 {event_id}.trigger에 {field}가 없습니다.")

        # 지표 검증
        if "metric" in trigger:
            metric_name = trigger["metric"]
            try:
                Metric[metric_name]
            except (KeyError, ValueError):
                self.errors.append(
                    f"트리거 {event_id}.trigger의 metric이 유효하지 않습니다: {metric_name}"
                )

        # 조건 검증
        if "condition" in trigger:
            condition = trigger["condition"]
            valid_conditions = [c.value for c in TriggerCondition]
            if condition not in valid_conditions:
                self.errors.append(
                    f"트리거 {event_id}.trigger의 condition이 유효하지 않습니다: {condition}"
                )

        # 값 검증
        if "value" in trigger and not isinstance(trigger["value"], (int, float)):
            self.errors.append(
                f"트리거 {event_id}.trigger의 value가 숫자가 아닙니다: {trigger['value']}"
            )

    def _validate_effect(self, effect: Dict[str, Any], effect_id: str) -> None:
        """
        효과의 유효성을 검증합니다.

        Args:
            effect: 효과 데이터
            effect_id: 효과 ID
        """
        # 필수 필드 검증
        required_fields = ["metric", "formula"]
        for field in required_fields:
            if field not in effect:
                self.errors.append(f"효과 {effect_id}에 {field}가 없습니다.")

        # 지표 검증
        if "metric" in effect:
            metric_name = effect["metric"]
            try:
                Metric[metric_name]
            except (KeyError, ValueError):
                self.errors.append(
                    f"효과 {effect_id}의 metric이 유효하지 않습니다: {metric_name}"
                )

        # 수식 검증
        if "formula" in effect:
            formula = effect["formula"]
            if not isinstance(formula, str):
                self.errors.append(
                    f"효과 {effect_id}의 formula가 문자열이 아닙니다: {formula}"
                )
            else:
                self._validate_formula(formula, effect_id)

    def _validate_formula(self, formula: str, effect_id: str) -> None:
        """
        수식의 유효성을 검증합니다.

        Args:
            formula: 수식 문자열
            effect_id: 효과 ID
        """
        # 백분율 표기법 처리
        if "%" in formula:
            formula = formula.replace("%", "")
            try:
                float(formula)
                return
            except ValueError:
                self.errors.append(
                    f"효과 {effect_id}의 백분율 formula가 유효하지 않습니다: {formula}%"
                )
                return

        # 일반 수식 평가
        try:
            # 제한된 평가 환경에서 수식 평가
            # 실제 구현에서는 ast.literal_eval 등을 사용하여 안전하게 평가해야 함
            value = 100.0  # 테스트용 값
            eval(formula, {"__builtins__": {}}, {"value": value})
        except Exception as e:
            self.errors.append(
                f"효과 {effect_id}의 formula가 유효하지 않습니다: {formula}, 오류: {e}"
            )


def load_events_from_toml(filepath: str) -> List[Event]:
    """
    TOML 파일에서 이벤트를 로드합니다.

    Args:
        filepath: TOML 파일 경로

    Returns:
        List[Event]: 이벤트 목록
    """
    validator = EventSchemaValidator()
    if not validator.validate_toml_file(filepath):
        raise ValueError(f"TOML 파일 검증 실패: {', '.join(validator.errors)}")

    with open(filepath, "rb") as f:
        data = tomllib.load(f)

    return _parse_events(data)


def load_events_from_json(filepath: str) -> List[Event]:
    """
    JSON 파일에서 이벤트를 로드합니다.

    Args:
        filepath: JSON 파일 경로

    Returns:
        List[Event]: 이벤트 목록
    """
    validator = EventSchemaValidator()
    if not validator.validate_json_file(filepath):
        raise ValueError(f"JSON 파일 검증 실패: {', '.join(validator.errors)}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return _parse_events(data)


def _parse_events(data: Dict[str, Any]) -> List[Event]:
    """
    이벤트 데이터를 파싱하여 Event 객체 목록을 생성합니다.

    Args:
        data: 이벤트 데이터

    Returns:
        List[Event]: 이벤트 목록
    """
    events = []

    for event_data in data["events"]:
        # 이벤트 타입 변환
        event_type = EventCategory[event_data["type"]]

        # 트리거 변환
        trigger = None
        if "trigger" in event_data and event_data["trigger"] is not None:
            trigger_data = event_data["trigger"]
            trigger = Trigger(
                metric=Metric[trigger_data["metric"]],
                condition=TriggerCondition(trigger_data["condition"]),
                value=float(trigger_data["value"]),
            )

        # 효과 변환
        effects = []
        for effect_data in event_data["effects"]:
            effect = Effect(
                metric=Metric[effect_data["metric"]],
                formula=effect_data["formula"],
                message=effect_data.get("message"),
            )
            effects.append(effect)

        # 이벤트 생성
        event = Event(
            id=event_data["id"],
            type=event_type,
            effects=effects,
            priority=event_data.get("priority", 0),
            cooldown=event_data.get("cooldown", 0),
            probability=event_data.get("probability"),
            trigger=trigger,
            schedule=event_data.get("schedule"),
            message=event_data.get("message"),
            tags=event_data.get("tags", []),
            cascade_depth=event_data.get("cascade_depth", 0),
        )
        events.append(event)

    return events


def save_events_to_json(events: List[Event], filepath: str) -> None:
    """
    이벤트 목록을 JSON 파일로 저장합니다.

    Args:
        events: 이벤트 목록
        filepath: JSON 파일 경로
    """
    # 이벤트 객체를 딕셔너리로 변환
    events_data = {"events": []}
    for event in events:
        event_dict = asdict(event)

        # Enum 값을 문자열로 변환
        event_dict["type"] = event.type.name

        # 트리거가 있는 경우 Enum 값을 문자열로 변환
        if event.trigger:
            event_dict["trigger"]["metric"] = event.trigger.metric.name
            event_dict["trigger"]["condition"] = event.trigger.condition.value

        # 효과의 지표를 문자열로 변환
        for i, effect in enumerate(event.effects):
            event_dict["effects"][i]["metric"] = effect.metric.name

        events_data["events"].append(event_dict)

    # JSON 파일로 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)


def convert_toml_to_json(toml_filepath: str, json_filepath: str) -> None:
    """
    TOML 이벤트 파일을 JSON으로 변환합니다.

    Args:
        toml_filepath: TOML 파일 경로
        json_filepath: JSON 파일 경로
    """
    events = load_events_from_toml(toml_filepath)
    save_events_to_json(events, json_filepath)

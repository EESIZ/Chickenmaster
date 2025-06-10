"""
이벤트 시스템
게임 내 이벤트를 관리하고 처리하는 시스템입니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple

from .game_state import GameState
from ..game_constants import (
    Metric,
    MAX_EVENTS_PER_DAY,
    EVENT_COOLDOWN_DAYS,
    MAX_CASCADE_DEPTH,
    PROBABILITY_HIGH_THRESHOLD,
    PROBABILITY_MEDIUM_THRESHOLD,
    PROBABILITY_LOW_THRESHOLD,
)


class EventType(Enum):
    """이벤트 타입"""
    RANDOM = auto()  # 무작위 발생
    THRESHOLD = auto()  # 특정 조건 달성 시 발생
    SCHEDULED = auto()  # 예정된 시점에 발생
    CASCADE = auto()  # 다른 이벤트의 결과로 발생


class EventSeverity(Enum):
    """이벤트 심각도"""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass(frozen=True)
class EventEffect:
    """이벤트 효과"""
    metric: Metric
    value: float
    is_percentage: bool = False


@dataclass(frozen=True)
class EventTrigger:
    """이벤트 발생 조건"""
    metric: Metric
    threshold: float
    is_greater_than: bool = True


@dataclass(frozen=True)
class Event:
    """이벤트"""
    id: str
    name_ko: str
    name_en: str
    description_ko: str
    description_en: str
    type: EventType
    severity: EventSeverity
    probability: float
    cooldown: int = EVENT_COOLDOWN_DAYS
    triggers: Tuple[EventTrigger, ...] = field(default_factory=tuple)
    effects: Tuple[EventEffect, ...] = field(default_factory=tuple)
    cascade_events: Tuple[str, ...] = field(default_factory=tuple)  # 연쇄 이벤트 ID 목록


class EventSystem:
    """이벤트 시스템"""

    def __init__(self, game_state: GameState):
        """
        Args:
            game_state: 현재 게임 상태
        """
        self.game_state = game_state
        self.events: Dict[str, Event] = {}
        self.event_history: List[Tuple[str, datetime]] = []  # (이벤트 ID, 발생 시간)
        self.cascade_depth = 0

    def register_event(self, event: Event) -> None:
        """이벤트 등록

        Args:
            event: 등록할 이벤트
        """
        self.events[event.id] = event

    def get_applicable_events(self) -> List[Event]:
        """현재 상태에서 발생 가능한 이벤트 목록을 반환합니다.

        Returns:
            List[Event]: 발생 가능한 이벤트 목록
        """
        applicable_events = []
        for event in self.events.values():
            if self._is_event_applicable(event):
                applicable_events.append(event)
        return applicable_events

    def _is_event_applicable(self, event: Event) -> bool:
        """이벤트가 현재 상태에서 발생 가능한지 확인합니다.

        Args:
            event: 확인할 이벤트

        Returns:
            bool: 발생 가능 여부
        """
        # 쿨다운 확인
        if self._is_in_cooldown(event):
            return False

        # 트리거 조건 확인
        for trigger in event.triggers:
            current_value = self._get_metric_value(trigger.metric)
            if trigger.is_greater_than:
                if current_value <= trigger.threshold:
                    return False
            else:
                if current_value >= trigger.threshold:
                    return False

        return True

    def _is_in_cooldown(self, event: Event) -> bool:
        """이벤트가 쿨다운 상태인지 확인합니다.

        Args:
            event: 확인할 이벤트

        Returns:
            bool: 쿨다운 상태 여부
        """
        for event_id, timestamp in reversed(self.event_history):
            if event_id == event.id:
                days_passed = (datetime.now() - timestamp).days
                return days_passed < event.cooldown
        return False

    def _get_metric_value(self, metric: Metric) -> float:
        """메트릭의 현재 값을 반환합니다.

        Args:
            metric: 확인할 메트릭

        Returns:
            float: 메트릭 값
        """
        return self.game_state.metrics[metric]

    def process_turn(self) -> List[Event]:
        """현재 턴의 이벤트를 처리합니다.

        Returns:
            List[Event]: 발생한 이벤트 목록
        """
        triggered_events = []
        self.cascade_depth = 0

        # 기본 이벤트 처리
        applicable_events = self.get_applicable_events()
        for _ in range(MAX_EVENTS_PER_DAY):
            if not applicable_events:
                break

            event = self._select_event(applicable_events)
            if event:
                triggered_events.append(event)
                self._apply_event(event)
                applicable_events.remove(event)

        # 연쇄 이벤트 처리
        for event in triggered_events:
            self._process_cascade_events(event)

        return triggered_events

    def _select_event(self, events: List[Event]) -> Optional[Event]:
        """이벤트 목록에서 하나를 선택합니다.

        Args:
            events: 선택할 이벤트 목록

        Returns:
            Optional[Event]: 선택된 이벤트
        """
        # TODO: 확률 기반 이벤트 선택 로직 구현
        return events[0] if events else None

    def _apply_event(self, event: Event) -> None:
        """이벤트 효과를 적용합니다.

        Args:
            event: 적용할 이벤트
        """
        # TODO: 이벤트 효과 적용 로직 구현
        self.event_history.append((event.id, datetime.now()))

    def _process_cascade_events(self, event: Event) -> None:
        """연쇄 이벤트를 처리합니다.

        Args:
            event: 연쇄 이벤트를 발생시킨 이벤트
        """
        if self.cascade_depth >= MAX_CASCADE_DEPTH:
            return

        self.cascade_depth += 1
        for cascade_event_id in event.cascade_events:
            if cascade_event_id in self.events:
                cascade_event = self.events[cascade_event_id]
                if self._is_event_applicable(cascade_event):
                    self._apply_event(cascade_event)
                    self._process_cascade_events(cascade_event) 
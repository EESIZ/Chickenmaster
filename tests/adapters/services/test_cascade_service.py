"""
Cascade 서비스 어댑터 테스트.

이 모듈은 연쇄 이벤트 서비스 구현체를 테스트합니다.
"""

import unittest
from datetime import timedelta
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass, field

from src.adapters.services.cascade_service import CascadeServiceImpl
from src.core.domain.cascade import CascadeType, TriggerCondition
from src.core.domain.events import Event
from src.core.domain.game_state import GameState
from src.core.ports.event_port import IEventService


@dataclass(frozen=True)
class MockEvent(Event):
    """테스트용 이벤트 목 객체"""

    id: str
    type: str = "test_event"
    name_ko: str = "테스트 이벤트"
    name_en: str = "Test Event"
    text_ko: str = "테스트 이벤트 설명"
    text_en: str = "Test event description"
    effects: dict = field(default_factory=lambda: {"reputation": -0.1, "cash": -100})
    conditions: tuple = field(default_factory=tuple)
    probability: float = 0.5
    cooldown: int = 0
    category: str = "test"
    severity: float = 0.5
    tags: tuple = field(default_factory=tuple)

    @property
    def metrics_impact(self):
        """지표 영향도 계산 (effects를 기반으로)"""
        return self.effects


@dataclass(frozen=True)
class MockGameState(GameState):
    """테스트용 게임 상태 목 객체"""

    money: int = 1000
    reputation: int = 70
    happiness: int = 80
    pain: int = 20
    day: int = 1
    events_history: tuple = field(default_factory=tuple)
    metrics: dict = field(
        default_factory=lambda: {"reputation": 0.7, "cash": 1000, "customer_satisfaction": 0.8}
    )


class TestCascadeServiceImpl(unittest.TestCase):
    """CascadeServiceImpl 클래스 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.event_service = Mock(spec=IEventService)
        self.cascade_service = CascadeServiceImpl(self.event_service)

        # 이벤트 서비스 목 설정
        self.event1 = MockEvent(id="event1")
        self.event2 = MockEvent(id="event2")
        self.event3 = MockEvent(id="event3")

        self.event_service.get_event_by_id = MagicMock(
            side_effect=lambda id: {
                "event1": self.event1,
                "event2": self.event2,
                "event3": self.event3,
            }.get(id)
        )

        self.event_service.apply_event = MagicMock(side_effect=lambda event, game_state: game_state)

        # 게임 상태
        self.game_state = MockGameState()

    def test_register_cascade_relation(self):
        """연쇄 관계 등록 테스트"""
        # 기본 관계 등록
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1", target_event_id="event2", cascade_type=CascadeType.IMMEDIATE
        )

        # 지연 관계 등록
        delay = timedelta(hours=1)
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1",
            target_event_id="event3",
            cascade_type=CascadeType.DELAYED,
            delay=delay,
        )

        # 조건부 관계 등록 - tuple로 변경
        conditions = (TriggerCondition("reputation", 0.5, ">"),)
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event2",
            target_event_id="event3",
            cascade_type=CascadeType.CONDITIONAL,
            conditions=conditions,
        )

        # 확률적 관계 등록
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event3",
            target_event_id="event1",
            cascade_type=CascadeType.PROBABILISTIC,
            probability=0.5,
        )

        # 등록 확인
        self.assertIn("event1", self.cascade_service._cascade_chains)
        self.assertIn("event2", self.cascade_service._cascade_chains)
        self.assertIn("event3", self.cascade_service._cascade_chains)

    def test_get_cascade_events_immediate(self):
        """즉시 발생 연쇄 이벤트 테스트"""
        # 관계 등록
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1", target_event_id="event2", cascade_type=CascadeType.IMMEDIATE
        )

        # 연쇄 이벤트 조회
        events = self.cascade_service.get_cascade_events(self.event1, self.game_state)

        # 검증
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, "event2")

    def test_get_cascade_events_delayed(self):
        """지연 발생 연쇄 이벤트 테스트"""
        # 관계 등록
        delay = timedelta(hours=1)
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1",
            target_event_id="event2",
            cascade_type=CascadeType.DELAYED,
            delay=delay,
        )

        # 연쇄 이벤트 조회
        events = self.cascade_service.get_cascade_events(self.event1, self.game_state)

        # 검증 - 지연 이벤트는 즉시 반환되지 않음
        self.assertEqual(len(events), 0)

        # 지연 이벤트 등록 확인
        self.assertEqual(len(self.cascade_service._pending_events), 1)
        self.assertEqual(self.cascade_service._pending_events[0].event.id, "event2")

    def test_get_cascade_events_conditional(self):
        """조건부 발생 연쇄 이벤트 테스트"""
        # 만족하는 조건 관계 등록 - tuple로 변경
        conditions1 = (TriggerCondition("reputation", 0.5, ">"),)
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1",
            target_event_id="event2",
            cascade_type=CascadeType.CONDITIONAL,
            conditions=conditions1,
        )

        # 만족하지 않는 조건 관계 등록 - tuple로 변경
        conditions2 = (TriggerCondition("reputation", 0.8, ">"),)
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1",
            target_event_id="event3",
            cascade_type=CascadeType.CONDITIONAL,
            conditions=conditions2,
        )

        # 연쇄 이벤트 조회
        events = self.cascade_service.get_cascade_events(self.event1, self.game_state)

        # 검증 - 조건 만족하는 이벤트만 반환
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, "event2")

    def test_calculate_cascade_depth(self):
        """연쇄 깊이 계산 테스트"""
        # 관계 등록
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1", target_event_id="event2", cascade_type=CascadeType.IMMEDIATE
        )

        self.cascade_service.register_cascade_relation(
            trigger_event_id="event2", target_event_id="event3", cascade_type=CascadeType.IMMEDIATE
        )

        # 깊이 계산
        depth = self.cascade_service.calculate_cascade_depth(self.event1, self.game_state)

        # 검증
        self.assertEqual(depth, 2)  # event1 -> event2 -> event3

    def test_validate_cascade_limits(self):
        """연쇄 깊이 제한 검증 테스트"""
        # 기본 최대 깊이는 5
        self.assertTrue(self.cascade_service.validate_cascade_limits(5))
        self.assertTrue(self.cascade_service.validate_cascade_limits(4))
        self.assertFalse(self.cascade_service.validate_cascade_limits(6))

    def test_process_cascade_chain(self):
        """전체 연쇄 체인 처리 테스트"""
        # 관계 등록
        self.cascade_service.register_cascade_relation(
            trigger_event_id="event1", target_event_id="event2", cascade_type=CascadeType.IMMEDIATE
        )

        self.cascade_service.register_cascade_relation(
            trigger_event_id="event2", target_event_id="event3", cascade_type=CascadeType.IMMEDIATE
        )

        # 연쇄 체인 처리
        events, final_state = self.cascade_service.process_cascade_chain(
            self.event1, self.game_state, max_depth=3
        )

        # 검증
        self.assertEqual(len(events), 3)  # event1, event2, event3
        self.assertEqual(events[0].id, "event1")
        self.assertEqual(events[1].id, "event2")
        self.assertEqual(events[2].id, "event3")

        # 이벤트 적용 호출 확인
        self.assertEqual(self.event_service.apply_event.call_count, 2)  # event2, event3

    def test_check_cascade_cycle(self):
        """연쇄 효과 사이클 검사 테스트"""
        # 사이클 없는 체인
        events1 = [MockEvent(id="event1"), MockEvent(id="event2"), MockEvent(id="event3")]
        self.assertFalse(self.cascade_service.check_cascade_cycle(events1))

        # 사이클 있는 체인
        events2 = [
            MockEvent(id="event1"),
            MockEvent(id="event2"),
            MockEvent(id="event1"),  # 사이클 형성
        ]
        self.assertTrue(self.cascade_service.check_cascade_cycle(events2))


if __name__ == "__main__":
    unittest.main()

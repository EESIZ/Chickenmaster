from game_constants import PROBABILITY_HIGH_THRESHOLD, PROBABILITY_HIGH_THRESHOLD5

"""
Cascade 도메인 모델 테스트.

이 모듈은 연쇄 이벤트 처리를 위한 도메인 객체들을 테스트합니다.
"""

import unittest
from datetime import datetime, timedelta
from freezegun import freeze_time
from dataclasses import dataclass, field
from typing import Dict, Any

from src.core.domain.cascade import (
    CascadeType,
    TriggerCondition,
    PendingEvent,
    CascadeNode,
    CascadeChain,
    CascadeResult,
)
from src.core.domain.events import Event
from src.core.domain.game_state import GameState
from src.core.domain.metrics import MetricEnum
from src.cascade.domain.models import (
    CascadeEffect,
    CascadeStrategy,
)


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


@dataclass(frozen=True)
class MockGameState(GameState):
    """테스트용 게임 상태 목 객체"""

    current_day: int = 1
    money: float = 1000
    reputation: float = 70
    happiness: float = 80
    suffering: float = 20
    inventory: float = 50
    staff_fatigue: float = 30
    facility: float = 80
    demand: float = 50
    events_history: tuple = field(default_factory=tuple)
    metrics: dict = field(
        default_factory=lambda: {
            MetricEnum.REPUTATION: PROBABILITY_HIGH_THRESHOLD,
            MetricEnum.MONEY: 1000,
            MetricEnum.HAPPINESS: 0.8,
        }
    )


class TestCascadeType(unittest.TestCase):
    """CascadeType 열거형 테스트"""

    def test_cascade_types(self):
        """연쇄 이벤트 유형 테스트"""
        self.assertIsNotNone(CascadeType.IMMEDIATE)
        self.assertIsNotNone(CascadeType.DELAYED)
        self.assertIsNotNone(CascadeType.CONDITIONAL)
        self.assertIsNotNone(CascadeType.PROBABILISTIC)

        # 유형 간 비교
        self.assertNotEqual(CascadeType.IMMEDIATE, CascadeType.DELAYED)
        self.assertNotEqual(CascadeType.CONDITIONAL, CascadeType.PROBABILISTIC)


class TestTriggerCondition(unittest.TestCase):
    """TriggerCondition 클래스 테스트"""

    def test_condition_creation(self):
        """조건 생성 테스트"""
        condition = TriggerCondition(metric_name="reputation", threshold=0.5, comparison=">")

        self.assertEqual(condition.metric_name, "reputation")
        self.assertEqual(condition.threshold, 0.5)
        self.assertEqual(condition.comparison, ">")

    def test_condition_satisfaction(self):
        """조건 만족 여부 테스트"""
        game_state = MockGameState()

        # 만족하는 조건
        condition1 = TriggerCondition("reputation", 0.5, ">")
        self.assertTrue(condition1.is_satisfied(game_state))

        # 만족하지 않는 조건
        condition2 = TriggerCondition("reputation", 0.8, ">")
        self.assertFalse(condition2.is_satisfied(game_state))

        # 다양한 비교 연산자
        self.assertTrue(TriggerCondition("cash", 500, ">").is_satisfied(game_state))
        self.assertTrue(TriggerCondition("cash", 1000, "==").is_satisfied(game_state))
        self.assertTrue(TriggerCondition("cash", 1001, "<").is_satisfied(game_state))
        self.assertTrue(TriggerCondition("cash", 1000, ">=").is_satisfied(game_state))
        self.assertTrue(TriggerCondition("cash", 1000, "<=").is_satisfied(game_state))
        self.assertTrue(TriggerCondition("cash", 900, "!=").is_satisfied(game_state))

        # 존재하지 않는 지표
        condition3 = TriggerCondition("nonexistent", 0.5, ">")
        self.assertFalse(condition3.is_satisfied(game_state))

        # 알 수 없는 비교 연산자
        condition4 = TriggerCondition("reputation", 0.5, "??")
        self.assertFalse(condition4.is_satisfied(game_state))


class TestPendingEvent(unittest.TestCase):
    """PendingEvent 클래스 테스트"""

    def test_pending_event_creation(self):
        """지연 이벤트 생성 테스트"""
        event = MockEvent(id="test_event")
        trigger_time = datetime.now() + timedelta(hours=1)
        conditions = (TriggerCondition("reputation", 0.5, ">"),)

        pending = PendingEvent(
            event=event, trigger_time=trigger_time, conditions=conditions, probability=0.8
        )

        self.assertEqual(pending.event, event)
        self.assertEqual(pending.trigger_time, trigger_time)
        self.assertEqual(pending.conditions, conditions)
        self.assertEqual(pending.probability, 0.8)

    @freeze_time("2025-01-01 12:00:00")
    def test_is_ready(self):
        """이벤트 발생 준비 여부 테스트"""
        event = MockEvent(id="test_event")
        game_state = MockGameState()

        # 시간 조건 만족, 다른 조건 없음
        past_time = datetime(2025, 1, 1, 11, 0)
        pending1 = PendingEvent(event=event, trigger_time=past_time)
        self.assertTrue(pending1.is_ready(datetime.now(), game_state))

        # 시간 조건 불만족
        future_time = datetime(2025, 1, 1, 13, 0)
        pending2 = PendingEvent(event=event, trigger_time=future_time)
        self.assertFalse(pending2.is_ready(datetime.now(), game_state))

        # 시간 조건 만족, 다른 조건 만족
        conditions = (TriggerCondition("reputation", 0.5, ">"),)
        pending3 = PendingEvent(event=event, trigger_time=past_time, conditions=conditions)
        self.assertTrue(pending3.is_ready(datetime.now(), game_state))

        # 시간 조건 만족, 다른 조건 불만족
        conditions = (TriggerCondition("reputation", 0.8, ">"),)
        pending4 = PendingEvent(event=event, trigger_time=past_time, conditions=conditions)
        self.assertFalse(pending4.is_ready(datetime.now(), game_state))


class TestCascadeNode(unittest.TestCase):
    """CascadeNode 클래스 테스트"""

    def test_node_creation(self):
        """노드 생성 테스트"""
        node = CascadeNode(event_id="test_event", cascade_type=CascadeType.IMMEDIATE)

        self.assertEqual(node.event_id, "test_event")
        self.assertEqual(node.cascade_type, CascadeType.IMMEDIATE)
        self.assertIsNone(node.delay)
        self.assertEqual(node.conditions, ())
        self.assertEqual(node.probability, 1.0)
        self.assertEqual(node.impact_factor, 1.0)

    def test_calculate_impact(self):
        """영향도 계산 테스트"""
        # 기본 영향도 계수
        node1 = CascadeNode(event_id="test_event", cascade_type=CascadeType.IMMEDIATE)
        self.assertEqual(node1.calculate_impact(0.5), 0.5)

        # 사용자 지정 영향도 계수
        node2 = CascadeNode(
            event_id="test_event", cascade_type=CascadeType.IMMEDIATE, impact_factor=1.5
        )
        self.assertEqual(node2.calculate_impact(0.5), PROBABILITY_HIGH_THRESHOLD5)


class TestCascadeChain(unittest.TestCase):
    """CascadeChain 클래스 테스트"""

    def test_chain_creation(self):
        """체인 생성 테스트"""
        node1 = CascadeNode("event2", CascadeType.IMMEDIATE)
        node2 = CascadeNode("event3", CascadeType.DELAYED)

        nodes = {"event1": frozenset([node1, node2])}

        chain = CascadeChain(trigger_event_id="event1", nodes=nodes, max_depth=3)

        self.assertEqual(chain.trigger_event_id, "event1")
        self.assertEqual(chain.nodes, nodes)
        self.assertEqual(chain.max_depth, 3)

    def test_get_next_nodes(self):
        """다음 노드 조회 테스트"""
        node1 = CascadeNode("event2", CascadeType.IMMEDIATE)
        node2 = CascadeNode("event3", CascadeType.DELAYED)

        nodes = {"event1": frozenset([node1, node2])}

        chain = CascadeChain(trigger_event_id="event1", nodes=nodes)

        # 존재하는 이벤트
        next_nodes = chain.get_next_nodes("event1")
        self.assertEqual(len(next_nodes), 2)
        self.assertIn(node1, next_nodes)
        self.assertIn(node2, next_nodes)

        # 존재하지 않는 이벤트
        next_nodes = chain.get_next_nodes("nonexistent")
        self.assertEqual(len(next_nodes), 0)

    def test_has_cycle(self):
        """사이클 존재 여부 테스트"""
        # 사이클 없는 체인
        node1 = CascadeNode("event2", CascadeType.IMMEDIATE)
        node2 = CascadeNode("event3", CascadeType.DELAYED)
        node3 = CascadeNode("event4", CascadeType.IMMEDIATE)

        nodes1 = {"event1": frozenset([node1, node2]), "event2": frozenset([node3])}

        chain1 = CascadeChain(trigger_event_id="event1", nodes=nodes1)

        self.assertFalse(chain1.has_cycle())

        # 사이클 있는 체인
        node4 = CascadeNode("event2", CascadeType.IMMEDIATE)
        node5 = CascadeNode("event3", CascadeType.IMMEDIATE)
        node6 = CascadeNode("event1", CascadeType.IMMEDIATE)

        nodes2 = {
            "event1": frozenset([node4]),
            "event2": frozenset([node5]),
            "event3": frozenset([node6]),  # 사이클 형성
        }

        chain2 = CascadeChain(trigger_event_id="event1", nodes=nodes2)

        self.assertTrue(chain2.has_cycle())


class TestCascadeResult(unittest.TestCase):
    """CascadeResult 클래스 테스트"""

    def test_result_creation(self):
        """결과 생성 테스트"""
        events = (MockEvent(id="event1"), MockEvent(id="event2"))
        pending_events = (
            PendingEvent(
                event=MockEvent(id="event3"), trigger_time=datetime.now() + timedelta(hours=1)
            ),
        )
        metrics_impact = {"reputation": -0.2, "cash": -200}

        result = CascadeResult(
            events=events,
            pending_events=pending_events,
            metrics_impact=metrics_impact,
            max_depth_reached=2,
            cycle_detected=False,
        )

        self.assertEqual(result.events, events)
        self.assertEqual(result.pending_events, pending_events)
        self.assertEqual(result.metrics_impact, metrics_impact)
        self.assertEqual(result.max_depth_reached, 2)
        self.assertFalse(result.cycle_detected)

    def test_get_total_impact(self):
        """총 영향도 계산 테스트"""
        metrics_impact = {"reputation": -0.2, "cash": -200, "customer_satisfaction": 0.1}

        result = CascadeResult(
            events=(), pending_events=(), metrics_impact=metrics_impact, max_depth_reached=0
        )

        # 절대값의 합계
        self.assertEqual(result.get_total_impact(), 0.2 + 200 + 0.1)

    def test_get_most_affected_metric(self):
        """가장 큰 영향을 받은 지표 테스트"""
        # 양수 영향
        metrics_impact1 = {"reputation": 0.2, "cash": 100, "customer_satisfaction": 0.1}
        result1 = CascadeResult(
            events=(), pending_events=(), metrics_impact=metrics_impact1, max_depth_reached=0
        )
        self.assertEqual(result1.get_most_affected_metric(), "cash")

        # 음수 영향 (절대값 기준)
        metrics_impact2 = {"reputation": -0.2, "cash": -300, "customer_satisfaction": 0.1}
        result2 = CascadeResult(
            events=(), pending_events=(), metrics_impact=metrics_impact2, max_depth_reached=0
        )
        self.assertEqual(result2.get_most_affected_metric(), "cash")

        # 빈 지표
        metrics_impact3 = {}
        result3 = CascadeResult(
            events=(), pending_events=(), metrics_impact=metrics_impact3, max_depth_reached=0
        )
        self.assertEqual(result3.get_most_affected_metric(), "")


if __name__ == "__main__":
    unittest.main()

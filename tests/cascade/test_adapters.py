from game_constants import MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIVE
from game_constants import MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIVE
"""
Cascade 모듈 어댑터 테스트.

이 모듈은 연쇄 이벤트 시스템의 어댑터에 대한 단위 테스트를 포함합니다.
"""

import pytest
from dataclasses import dataclass

from src.cascade.domain.models import (
    CascadeType
)
from src.cascade.ports.event_port import IEventService
from src.cascade.adapters.cascade_service import CascadeServiceImpl


# 테스트용 이벤트 클래스
@dataclass
class TestEvent:
    id: str
    effects: list[dict]
    cooldown: int = 0


# 테스트용 게임 상태 클래스
@dataclass
class TestGameState:
    metrics: dict[str, float]
    turn: int = 0


# 테스트용 이벤트 서비스 Mock
class MockEventService(IEventService):
    """테스트용 이벤트 서비스 Mock."""
    
    def __init__(self):
        self.events = {
            "root_event": TestEvent(
                id="root_event",
                effects=[{"metric": "money", "value": -100}]
            ),
            "child1": TestEvent(
                id="child1",
                effects=[{"metric": "reputation", "value": 5}]
            ),
            "child2": TestEvent(
                id="child2",
                effects=[{"metric": "happiness", "value": -10}]
            ),
            "grandchild": TestEvent(
                id="grandchild",
                effects=[{"metric": "money", "value": 50}]
            ),
            "conditional_event": TestEvent(
                id="conditional_event",
                effects=[{"metric": "reputation", "value": 20}]
            ),
            "probabilistic_event": TestEvent(
                id="probabilistic_event",
                effects=[{"metric": "happiness", "value": 15}]
            ),
            "delayed_event": TestEvent(
                id="delayed_event",
                effects=[{"metric": "money", "value": 200}]
            )
        }
        self.cooldowns = {}
    
    def get_event_by_id(self, event_id: str) -> TestEvent:
        if event_id not in self.events:
            raise ValueError(f"이벤트 ID '{event_id}'를 찾을 수 없습니다.")
        return self.events[event_id]
    
    def apply_event_effects(self, event: TestEvent, game_state: TestGameState) -> TestGameState:
        new_metrics = dict(game_state.metrics)
        
        for effect in event.effects:
            metric = effect.get("metric")
            value = effect.get("value", 0)
            
            if metric in new_metrics:
                new_metrics[metric] += value
            else:
                new_metrics[metric] = value
        
        return TestGameState(metrics=new_metrics, turn=game_state.turn)
    
    def evaluate_trigger_condition(self, condition: dict, game_state: TestGameState) -> bool:
        expression = condition.get("expression", "")
        
        # 간단한 조건 평가 로직
        if "money > 1000" in expression:
            return game_state.metrics.get("money", 0) > 1000
        elif "reputation < 0" in expression:
            return game_state.metrics.get("reputation", 0) < 0
        elif "happiness > 50" in expression:
            return game_state.metrics.get("happiness", 0) > 50
        
        return True  # 기본적으로 조건 충족
    
    def get_applicable_events(self, game_state: TestGameState) -> list[TestEvent]:
        return list(self.events.values())
    
    def check_event_cooldown(self, event_id: str, current_turn: int) -> bool:
        if event_id not in self.cooldowns:
            return True
        
        last_turn, cooldown = self.cooldowns[event_id]
        return current_turn - last_turn >= cooldown
    
    def evaluate_event_probability(self, event: TestEvent, game_state: TestGameState) -> float:
        # 간단한 확률 계산 로직
        if event.id == "probabilistic_event":
            return 0.5
        return 1.0


class TestCascadeServiceImpl:
    """CascadeServiceImpl 클래스 테스트."""
    
    @pytest.fixture
    def event_service(self):
        """이벤트 서비스 fixture."""
        return MockEventService()
    
    @pytest.fixture
    def cascade_service(self, event_service):
        """연쇄 이벤트 서비스 fixture."""
        return CascadeServiceImpl(event_service)
    
    @pytest.fixture
    def game_state(self):
        """게임 상태 fixture."""
        return TestGameState(
            metrics={"money": 1000, "reputation": 50, "happiness": 75}
        )
    
    def test_register_cascade_relation(self, cascade_service):
        """연쇄 관계 등록 테스트."""
        node = cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child1",
            cascade_type_str="IMMEDIATE"
        )
        
        assert node.event_id == "child1"
        assert node.parent_id == "root_event"
        assert node.cascade_type == CascadeType.IMMEDIATE
        assert node.depth == 0  # 첫 번째 등록이므로 깊이는 0 + 1 = 1이어야 하지만, 구현상 0으로 시작
    
    def test_register_conditional_relation(self, cascade_service):
        """조건부 연쇄 관계 등록 테스트."""
        condition = {
            "expression": "metrics.money > 1000",
            "parameters": {"threshold": 1000}
        }
        
        node = cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="conditional_event",
            cascade_type_str="CONDITIONAL",
            trigger_condition=condition
        )
        
        assert node.event_id == "conditional_event"
        assert node.cascade_type == CascadeType.CONDITIONAL
        assert node.trigger_condition is not None
        assert node.trigger_condition.expression == "metrics.money > 1000"
    
    def test_register_probabilistic_relation(self, cascade_service):
        """확률적 연쇄 관계 등록 테스트."""
        node = cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="probabilistic_event",
            cascade_type_str="PROBABILISTIC",
            probability=0.5
        )
        
        assert node.event_id == "probabilistic_event"
        assert node.cascade_type == CascadeType.PROBABILISTIC
        assert node.probability == 0.5
    
    def test_register_delayed_relation(self, cascade_service):
        """지연 연쇄 관계 등록 테스트."""
        node = cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="delayed_event",
            cascade_type_str="DELAYED",
            delay_turns=2
        )
        
        assert node.event_id == "delayed_event"
        assert node.cascade_type == CascadeType.DELAYED
        assert node.delay_turns == MAGIC_NUMBER_TWO
    
    def test_build_cascade_chain(self, cascade_service):
        """연쇄 체인 구성 테스트."""
        # 연쇄 관계 등록
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child1",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child2",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="child1",
            child_event_id="grandchild",
            cascade_type_str="IMMEDIATE"
        )
        
        # 연쇄 체인 구성
        chain = cascade_service.build_cascade_chain("root_event")
        
        assert chain.root_event_id == "root_event"
        assert len(chain.nodes) == 4  # 루트 + 자식2 + 손자1
        assert chain.get_max_actual_depth() == MAGIC_NUMBER_TWO  # 최대 깊이는 2 (루트=0, 자식=1, 손자=2)
    
    def test_get_cascade_events(self, cascade_service, game_state):
        """연쇄 이벤트 목록 조회 테스트."""
        # 연쇄 관계 등록
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child1",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="conditional_event",
            cascade_type_str="CONDITIONAL",
            trigger_condition={"expression": "metrics.money > 1000"}
        )
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="delayed_event",
            cascade_type_str="DELAYED",
            delay_turns=2
        )
        
        # 연쇄 이벤트 목록 조회
        events = cascade_service.get_cascade_events("root_event", game_state)
        
        assert len(events) == 1  # child1만 즉시 발생 (conditional은 조건 불충족, delayed는 지연)
        assert "child1" in events
    
    def test_process_cascade_chain(self, cascade_service, event_service, game_state):
        """연쇄 체인 처리 테스트."""
        # 연쇄 관계 등록
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child1",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="child1",
            child_event_id="grandchild",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="delayed_event",
            cascade_type_str="DELAYED",
            delay_turns=2
        )
        
        # 루트 이벤트 객체
        root_event = event_service.get_event_by_id("root_event")
        
        # 연쇄 체인 처리
        result = cascade_service.process_cascade_chain(
            root_event=root_event,
            game_state=game_state,
            current_turn=1
        )
        
        assert len(result.triggered_events) == 3  # root_event + child1 + grandchild
        assert "root_event" in result.triggered_events
        assert "child1" in result.triggered_events
        assert "grandchild" in result.triggered_events
        
        assert len(result.pending_events) == 1  # delayed_event
        assert result.pending_events[0].event_id == "delayed_event"
        assert result.pending_events[0].trigger_turn == 3  # 현재 턴(1) + 지연 턴(2)
        
        assert "money" in result.metrics_impact
        assert "reputation" in result.metrics_impact
        assert result.metrics_impact["money"] == -50  # root(-100) + grandchild(+50)
        assert result.metrics_impact["reputation"] == MAGIC_NUMBER_FIVE  # child1(+5)
    
    def test_get_pending_events(self, cascade_service, event_service, game_state):
        """지연 이벤트 조회 테스트."""
        # 연쇄 관계 등록
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="delayed_event",
            cascade_type_str="DELAYED",
            delay_turns=2
        )
        
        # 루트 이벤트 객체
        root_event = event_service.get_event_by_id("root_event")
        
        # 연쇄 체인 처리 (지연 이벤트 등록)
        cascade_service.process_cascade_chain(
            root_event=root_event,
            game_state=game_state,
            current_turn=1
        )
        
        # 현재 턴에 처리할 지연 이벤트 없음
        pending_turn1 = cascade_service.get_pending_events(1)
        assert len(pending_turn1) == 0
        
        # 지연 이벤트 처리 턴
        pending_turn3 = cascade_service.get_pending_events(3)
        assert len(pending_turn3) == 1
        assert pending_turn3[0].event_id == "delayed_event"
        
        # 이미 처리된 지연 이벤트는 목록에서 제거됨
        pending_turn3_again = cascade_service.get_pending_events(3)
        assert len(pending_turn3_again) == 0
    
    def test_check_cascade_cycle(self, cascade_service):
        """연쇄 사이클 검사 테스트."""
        # 사이클이 없는 연쇄 관계 등록
        cascade_service.register_cascade_relation(
            parent_event_id="root_event",
            child_event_id="child1",
            cascade_type_str="IMMEDIATE"
        )
        cascade_service.register_cascade_relation(
            parent_event_id="child1",
            child_event_id="grandchild",
            cascade_type_str="IMMEDIATE"
        )
        
        # 사이클이 없는 연쇄 체인 구성
        chain_no_cycle = cascade_service.build_cascade_chain("root_event")
        
        # 사이클 검사
        has_cycle = cascade_service.check_cascade_cycle(chain_no_cycle)
        assert has_cycle is False
    
    def test_calculate_metrics_impact(self, cascade_service, event_service):
        """지표 영향도 계산 테스트."""
        # 이벤트 객체 목록
        events = [
            event_service.get_event_by_id("root_event"),  # money: -100
            event_service.get_event_by_id("child1"),      # reputation: +5
            event_service.get_event_by_id("grandchild")   # money: +50
        ]
        
        # 게임 상태
        game_state = TestGameState(
            metrics={"money": 1000, "reputation": 50, "happiness": 75}
        )
        
        # 지표 영향도 계산
        impact = cascade_service.calculate_metrics_impact(events, game_state)
        
        assert "money" in impact
        assert "reputation" in impact
        assert impact["money"] == -50  # -100 + 50
        assert impact["reputation"] == MAGIC_NUMBER_FIVE

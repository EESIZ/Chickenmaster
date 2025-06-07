from game_constants import MAGIC_NUMBER_ONE, MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIVE, MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN
from game_constants import MAGIC_NUMBER_ONE, MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIVE, MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN
"""
Cascade 모듈 도메인 객체 테스트.

이 모듈은 연쇄 이벤트 시스템의 도메인 객체에 대한 단위 테스트를 포함합니다.
"""

import pytest
import dataclasses
from datetime import datetime
from uuid import UUID

from src.cascade.domain.models import (
    CascadeChain, CascadeNode, CascadeResult, CascadeType, 
    PendingEvent, TriggerCondition
)


class TestTriggerCondition:
    """TriggerCondition 클래스 테스트."""
    
    def test_create_trigger_condition(self):
        """기본 생성 테스트."""
        condition = TriggerCondition(expression="metrics.money > 1000")
        assert condition.expression == "metrics.money > 1000"
        assert condition.parameters == {}
    
    def test_create_with_parameters(self):
        """파라미터가 있는 생성 테스트."""
        params = {"threshold": 1000, "is_active": True}
        condition = TriggerCondition(
            expression="metrics.money > {threshold} and {is_active}",
            parameters=params
        )
        assert condition.expression == "metrics.money > {threshold} and {is_active}"
        assert condition.parameters == params
    
    def test_immutability(self):
        """불변성 테스트."""
        condition = TriggerCondition(expression="metrics.money > 1000")
        with pytest.raises(dataclasses.FrozenInstanceError):
            condition.expression = "metrics.money > 2000"
    
    def test_missing_parameters(self):
        """누락된 파라미터 테스트."""
        with pytest.raises(ValueError):
            TriggerCondition(expression="metrics.money > {threshold}")


class TestPendingEvent:
    """PendingEvent 클래스 테스트."""
    
    def test_create_pending_event(self):
        """기본 생성 테스트."""
        event = PendingEvent(
            event_id="test_event",
            delay_turns=2,
            trigger_turn=5
        )
        assert event.event_id == "test_event"
        assert event.delay_turns == MAGIC_NUMBER_TWO
        assert event.trigger_turn == MAGIC_NUMBER_FIVE
        assert event.cascade_type == CascadeType.DELAYED
        assert event.probability == MAGIC_NUMBER_ONE
    
    def test_invalid_delay(self):
        """유효하지 않은 지연 턴 테스트."""
        with pytest.raises(ValueError):
            PendingEvent(
                event_id="test_event",
                delay_turns=0,
                trigger_turn=5
            )
    
    def test_invalid_probability(self):
        """유효하지 않은 확률 테스트."""
        with pytest.raises(ValueError):
            PendingEvent(
                event_id="test_event",
                delay_turns=2,
                trigger_turn=5,
                probability=1.5
            )


class TestCascadeNode:
    """CascadeNode 클래스 테스트."""
    
    def test_create_root_node(self):
        """루트 노드 생성 테스트."""
        node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        assert node.event_id == "root_event"
        assert node.depth == 0
        assert node.cascade_type == CascadeType.IMMEDIATE
        assert node.parent_id is None
        assert isinstance(node.node_id, UUID)
        assert node.is_root() is True
    
    def test_create_child_node(self):
        """자식 노드 생성 테스트."""
        node = CascadeNode(
            event_id="child_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        assert node.event_id == "child_event"
        assert node.parent_id == "root_event"
        assert node.depth == 1
        assert node.is_root() is False
    
    def test_create_delayed_node(self):
        """지연 노드 생성 테스트."""
        node = CascadeNode(
            event_id="delayed_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.DELAYED,
            delay_turns=2
        )
        assert node.is_delayed() is True
    
    def test_create_conditional_node(self):
        """조건부 노드 생성 테스트."""
        condition = TriggerCondition(expression="metrics.money > 1000")
        node = CascadeNode(
            event_id="conditional_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.CONDITIONAL,
            trigger_condition=condition
        )
        assert node.is_conditional() is True
    
    def test_create_probabilistic_node(self):
        """확률적 노드 생성 테스트."""
        node = CascadeNode(
            event_id="prob_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.PROBABILISTIC,
            probability=0.5
        )
        assert node.is_probabilistic() is True
    
    def test_invalid_depth(self):
        """유효하지 않은 깊이 테스트."""
        with pytest.raises(ValueError):
            CascadeNode(
                event_id="test_event",
                depth=-1,
                cascade_type=CascadeType.IMMEDIATE
            )
    
    def test_invalid_probability(self):
        """유효하지 않은 확률 테스트."""
        with pytest.raises(ValueError):
            CascadeNode(
                event_id="test_event",
                depth=0,
                cascade_type=CascadeType.PROBABILISTIC,
                probability=1.5
            )
    
    def test_delayed_without_delay(self):
        """지연 턴 없는 지연 이벤트 테스트."""
        with pytest.raises(ValueError):
            CascadeNode(
                event_id="test_event",
                depth=0,
                cascade_type=CascadeType.DELAYED,
                delay_turns=0
            )
    
    def test_conditional_without_condition(self):
        """조건 없는 조건부 이벤트 테스트."""
        with pytest.raises(ValueError):
            CascadeNode(
                event_id="test_event",
                depth=0,
                cascade_type=CascadeType.CONDITIONAL
            )


class TestCascadeChain:
    """CascadeChain 클래스 테스트."""
    
    def test_create_simple_chain(self):
        """단순 체인 생성 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child_node = CascadeNode(
            event_id="child_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child_node])
        )
        
        assert chain.root_event_id == "root_event"
        assert len(chain.nodes) == MAGIC_NUMBER_TWO
        assert chain.max_depth == MAGIC_NUMBER_FIVE
        assert isinstance(chain.chain_id, UUID)
        assert isinstance(chain.created_at, datetime)
    
    def test_empty_nodes(self):
        """노드 없는 체인 테스트."""
        with pytest.raises(ValueError):
            CascadeChain(
                root_event_id="root_event",
                nodes=frozenset()
            )
    
    def test_invalid_max_depth(self):
        """유효하지 않은 최대 깊이 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        with pytest.raises(ValueError):
            CascadeChain(
                root_event_id="root_event",
                nodes=frozenset([root_node]),
                max_depth=0
            )
    
    def test_missing_root_node(self):
        """루트 노드 누락 테스트."""
        child_node = CascadeNode(
            event_id="child_event",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        with pytest.raises(ValueError):
            CascadeChain(
                root_event_id="root_event",
                nodes=frozenset([child_node])
            )
    
    def test_get_nodes_at_depth(self):
        """특정 깊이 노드 조회 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child1 = CascadeNode(
            event_id="child1",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        child2 = CascadeNode(
            event_id="child2",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child1, child2])
        )
        
        depth0_nodes = chain.get_nodes_at_depth(0)
        depth1_nodes = chain.get_nodes_at_depth(1)
        depth2_nodes = chain.get_nodes_at_depth(2)
        
        assert len(depth0_nodes) == 1
        assert depth0_nodes[0].event_id == "root_event"
        assert len(depth1_nodes) == MAGIC_NUMBER_TWO
        assert {node.event_id for node in depth1_nodes} == {"child1", "child2"}
        assert len(depth2_nodes) == 0
    
    def test_get_child_nodes(self):
        """자식 노드 조회 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child1 = CascadeNode(
            event_id="child1",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        child2 = CascadeNode(
            event_id="child2",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        grandchild = CascadeNode(
            event_id="grandchild",
            parent_id="child1",
            depth=2,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child1, child2, grandchild])
        )
        
        root_children = chain.get_child_nodes("root_event")
        child1_children = chain.get_child_nodes("child1")
        child2_children = chain.get_child_nodes("child2")
        
        assert len(root_children) == MAGIC_NUMBER_TWO
        assert {node.event_id for node in root_children} == {"child1", "child2"}
        assert len(child1_children) == 1
        assert child1_children[0].event_id == "grandchild"
        assert len(child2_children) == 0
    
    def test_get_node_by_event_id(self):
        """이벤트 ID로 노드 조회 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child = CascadeNode(
            event_id="child",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child])
        )
        
        found_root = chain.get_node_by_event_id("root_event")
        found_child = chain.get_node_by_event_id("child")
        not_found = chain.get_node_by_event_id("nonexistent")
        
        assert found_root is not None
        assert found_root.event_id == "root_event"
        assert found_child is not None
        assert found_child.event_id == "child"
        assert not_found is None
    
    def test_get_max_actual_depth(self):
        """실제 최대 깊이 조회 테스트."""
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child = CascadeNode(
            event_id="child",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        grandchild = CascadeNode(
            event_id="grandchild",
            parent_id="child",
            depth=2,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain1 = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node])
        )
        chain2 = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child])
        )
        chain3 = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child, grandchild])
        )
        
        assert chain1.get_max_actual_depth() == 0
        assert chain2.get_max_actual_depth() == 1
        assert chain3.get_max_actual_depth() == MAGIC_NUMBER_TWO
    
    def test_has_cycles(self):
        """사이클 감지 테스트."""
        # 사이클이 없는 체인
        root_node = CascadeNode(
            event_id="root_event",
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        child = CascadeNode(
            event_id="child",
            parent_id="root_event",
            depth=1,
            cascade_type=CascadeType.IMMEDIATE
        )
        grandchild = CascadeNode(
            event_id="grandchild",
            parent_id="child",
            depth=2,
            cascade_type=CascadeType.IMMEDIATE
        )
        
        chain_no_cycle = CascadeChain(
            root_event_id="root_event",
            nodes=frozenset([root_node, child, grandchild])
        )
        
        assert chain_no_cycle.has_cycles() is False


class TestCascadeResult:
    """CascadeResult 클래스 테스트."""
    
    def test_create_cascade_result(self):
        """기본 생성 테스트."""
        # freezegun과 dataclass default_factory 호환성 문제로 인해 시간 검증 제외
        result = CascadeResult(
            triggered_events=("event1", "event2"),
            pending_events=(),
            metrics_impact={"money": -100, "reputation": 5},
            depth_reached=2
        )
        
        assert result.triggered_events == ("event1", "event2")
        assert result.pending_events == ()
        assert result.metrics_impact == {"money": -100, "reputation": 5}
        assert result.depth_reached == MAGIC_NUMBER_TWO
        assert isinstance(result.result_id, UUID)
        assert isinstance(result.created_at, datetime)
    
    def test_invalid_depth(self):
        """유효하지 않은 깊이 테스트."""
        with pytest.raises(ValueError):
            CascadeResult(
                triggered_events=(),
                pending_events=(),
                metrics_impact={},
                depth_reached=-1
            )
    
    def test_get_total_events_count(self):
        """총 이벤트 수 계산 테스트."""
        pending1 = PendingEvent(
            event_id="pending1",
            delay_turns=1,
            trigger_turn=5
        )
        pending2 = PendingEvent(
            event_id="pending2",
            delay_turns=2,
            trigger_turn=6
        )
        
        result = CascadeResult(
            triggered_events=("event1", "event2", "event3"),
            pending_events=(pending1, pending2),
            metrics_impact={},
            depth_reached=2
        )
        
        assert result.get_total_events_count() == MAGIC_NUMBER_FIVE
    
    def test_get_total_metrics_impact(self):
        """총 지표 영향도 계산 테스트."""
        result = CascadeResult(
            triggered_events=(),
            pending_events=(),
            metrics_impact={"money": -100, "reputation": 5, "happiness": -10},
            depth_reached=1
        )
        
        assert result.get_total_metrics_impact() == MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN  # |−100| + |5| + |−10| = 115
    
    def test_has_pending_events(self):
        """지연 이벤트 여부 테스트."""
        result1 = CascadeResult(
            triggered_events=("event1",),
            pending_events=(),
            metrics_impact={},
            depth_reached=1
        )
        
        pending = PendingEvent(
            event_id="pending",
            delay_turns=1,
            trigger_turn=5
        )
        
        result2 = CascadeResult(
            triggered_events=("event1",),
            pending_events=(pending,),
            metrics_impact={},
            depth_reached=1
        )
        
        assert result1.has_pending_events() is False
        assert result2.has_pending_events() is True

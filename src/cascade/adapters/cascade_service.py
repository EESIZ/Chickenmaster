"""
연쇄 이벤트 서비스 구현체.

이 모듈은 ICascadeService 인터페이스를 구현하여 연쇄 이벤트 처리 로직을 제공합니다.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, cast
from uuid import UUID

from src.cascade.domain.models import (
    CascadeChain, CascadeNode, CascadeResult, CascadeType, 
    PendingEvent, TriggerCondition
)
from src.cascade.ports.cascade_port import ICascadeService
from src.cascade.ports.event_port import IEventService


class CascadeServiceImpl(ICascadeService):
    """
    ICascadeService 인터페이스 구현체.
    
    연쇄 이벤트 처리 로직을 구현합니다.
    """
    
    def __init__(self, event_service: IEventService):
        """
        CascadeServiceImpl 생성자.
        
        Args:
            event_service: 이벤트 서비스 인스턴스
        """
        self._event_service = event_service
        self._cascade_relations: Dict[str, List[CascadeNode]] = {}  # 부모 이벤트 ID -> 자식 노드 목록
        self._pending_events: List[PendingEvent] = []  # 지연 이벤트 목록
    
    def get_cascade_events(self, event_id: str, game_state: Any) -> List[str]:
        """
        트리거 이벤트로 인한 연쇄 이벤트 목록을 반환합니다.
        
        Args:
            event_id: 트리거 이벤트 ID
            game_state: 현재 게임 상태
            
        Returns:
            연쇄적으로 발생할 이벤트 ID 목록
            
        Raises:
            ValueError: 유효하지 않은 이벤트 ID인 경우
        """
        if event_id not in self._cascade_relations:
            return []
        
        result: List[str] = []
        
        for node in self._cascade_relations[event_id]:
            # 조건부 이벤트인 경우 조건 평가
            if node.is_conditional() and node.trigger_condition:
                condition_dict = {
                    'expression': node.trigger_condition.expression,
                    'parameters': dict(node.trigger_condition.parameters)
                }
                if not self._event_service.evaluate_trigger_condition(condition_dict, game_state):
                    continue
            
            # 확률적 이벤트인 경우 확률 계산
            if node.is_probabilistic():
                if random.random() > node.probability:
                    continue
            
            # 지연 이벤트인 경우 지연 이벤트 목록에 추가
            if node.is_delayed():
                continue
            
            result.append(node.event_id)
        
        return result
    
    def calculate_cascade_depth(self, event_chain: CascadeChain) -> int:
        """
        연쇄 효과 깊이를 계산합니다.
        
        Args:
            event_chain: 연쇄 이벤트 체인
            
        Returns:
            연쇄 효과의 최대 깊이
        """
        return event_chain.get_max_actual_depth()
    
    def validate_cascade_limits(self, event_chain: CascadeChain) -> bool:
        """
        연쇄 깊이 제한을 검증합니다.
        
        Args:
            event_chain: 연쇄 이벤트 체인
            
        Returns:
            제한 내에 있으면 True, 아니면 False
            
        Raises:
            ValueError: 연쇄 체인에 사이클이 있는 경우
        """
        # 사이클 검사
        if event_chain.has_cycles():
            raise ValueError("연쇄 체인에 사이클이 있습니다.")
        
        # 깊이 제한 검사
        return self.calculate_cascade_depth(event_chain) <= event_chain.max_depth
    
    def process_cascade_chain(
        self, 
        root_event: Any, 
        game_state: Any,
        current_turn: int = 0,
        max_depth: int = 5
    ) -> CascadeResult:
        """
        전체 연쇄 체인을 처리합니다.
        
        Args:
            root_event: 최초 트리거 이벤트
            game_state: 현재 게임 상태
            current_turn: 현재 게임 턴 (기본값: 0)
            max_depth: 최대 연쇄 깊이 (기본값: 5)
            
        Returns:
            연쇄 이벤트 처리 결과
            
        Raises:
            ValueError: 연쇄 체인에 사이클이 있거나 최대 깊이를 초과하는 경우
        """
        # 루트 이벤트 ID 추출
        root_event_id = getattr(root_event, 'id', str(root_event))
        
        # 연쇄 체인 구성
        cascade_chain = self.build_cascade_chain(root_event_id, max_depth)
        
        # 연쇄 체인 검증
        if not self.validate_cascade_limits(cascade_chain):
            raise ValueError(f"연쇄 체인이 최대 깊이({max_depth})를 초과합니다.")
        
        # 처리 결과 초기화
        triggered_events: List[str] = []
        pending_events: List[PendingEvent] = []
        triggered_event_objects: List[Any] = []
        
        # 루트 이벤트 처리
        triggered_events.append(root_event_id)
        triggered_event_objects.append(root_event)
        
        # 현재 게임 상태 복사
        current_state = game_state
        
        # 루트 이벤트 효과 적용
        current_state = self._event_service.apply_event_effects(root_event, current_state)
        
        # 연쇄 이벤트 처리 (BFS)
        queue = [root_event_id]
        processed = {root_event_id}
        
        while queue:
            current_id = queue.pop(0)
            
            # 현재 이벤트의 자식 이벤트 처리
            if current_id in self._cascade_relations:
                for node in self._cascade_relations[current_id]:
                    # 이미 처리된 노드 스킵
                    if node.event_id in processed:
                        continue
                    
                    # 조건부 이벤트인 경우 조건 평가
                    if node.is_conditional() and node.trigger_condition:
                        condition_dict = {
                            'expression': node.trigger_condition.expression,
                            'parameters': dict(node.trigger_condition.parameters)
                        }
                        if not self._event_service.evaluate_trigger_condition(condition_dict, current_state):
                            continue
                    
                    # 확률적 이벤트인 경우 확률 계산
                    if node.is_probabilistic():
                        if random.random() > node.probability:
                            continue
                    
                    # 지연 이벤트인 경우 지연 이벤트 목록에 추가
                    if node.is_delayed():
                        delay_event = PendingEvent(
                            event_id=node.event_id,
                            delay_turns=node.delay_turns,
                            trigger_turn=current_turn + node.delay_turns,
                            cascade_type=CascadeType.DELAYED,
                            probability=node.probability
                        )
                        pending_events.append(delay_event)
                        self._pending_events.append(delay_event)
                        processed.add(node.event_id)  # 지연 이벤트도 처리된 것으로 표시
                        continue
                    
                    # 이벤트 효과 적용
                    event = self._event_service.get_event_by_id(node.event_id)
                    current_state = self._event_service.apply_event_effects(event, current_state)
                    triggered_events.append(node.event_id)
                    triggered_event_objects.append(event)
                    processed.add(node.event_id)
                    queue.append(node.event_id)  # 다음 레벨 처리를 위해 큐에 추가
        
        # 지표 영향도 계산
        metrics_impact = self.calculate_metrics_impact(triggered_event_objects, game_state)
        
        # 결과 반환
        return CascadeResult(
            triggered_events=tuple(triggered_events),
            pending_events=tuple(pending_events),
            metrics_impact=metrics_impact,
            depth_reached=cascade_chain.get_max_actual_depth()
        )
    
    def check_cascade_cycle(self, event_chain: CascadeChain) -> bool:
        """
        연쇄 효과 사이클을 검사합니다.
        
        Args:
            event_chain: 연쇄 이벤트 체인
            
        Returns:
            사이클이 있으면 True, 없으면 False
        """
        return event_chain.has_cycles()
    
    def get_pending_events(self, current_turn: int) -> List[PendingEvent]:
        """
        현재 턴에 처리해야 할 지연 이벤트 목록을 반환합니다.
        
        Args:
            current_turn: 현재 게임 턴
            
        Returns:
            처리해야 할 지연 이벤트 목록
        """
        result = [
            event for event in self._pending_events 
            if event.trigger_turn == current_turn
        ]
        
        # 처리된 이벤트는 목록에서 제거
        self._pending_events = [
            event for event in self._pending_events 
            if event.trigger_turn != current_turn
        ]
        
        return result
    
    def register_cascade_relation(
        self, 
        parent_event_id: str, 
        child_event_id: str,
        cascade_type_str: str,
        trigger_condition: Optional[Dict[str, Any]] = None,
        probability: float = 1.0,
        delay_turns: int = 0
    ) -> CascadeNode:
        """
        두 이벤트 간의 연쇄 관계를 등록합니다.
        
        Args:
            parent_event_id: 부모 이벤트 ID
            child_event_id: 자식 이벤트 ID
            cascade_type_str: 연쇄 유형 ("IMMEDIATE", "DELAYED", "CONDITIONAL", "PROBABILISTIC")
            trigger_condition: 트리거 조건 (조건부 이벤트인 경우)
            probability: 발생 확률 (0.0~1.0, 기본값: 1.0)
            delay_turns: 지연 턴 수 (지연 이벤트인 경우, 기본값: 0)
            
        Returns:
            생성된 연쇄 노드
            
        Raises:
            ValueError: 유효하지 않은 이벤트 ID 또는 파라미터인 경우
        """
        # 이벤트 ID 검증
        try:
            self._event_service.get_event_by_id(parent_event_id)
            self._event_service.get_event_by_id(child_event_id)
        except ValueError as e:
            raise ValueError(f"유효하지 않은 이벤트 ID: {str(e)}")
        
        # 연쇄 유형 변환
        try:
            cascade_type = CascadeType[cascade_type_str]
        except KeyError:
            raise ValueError(f"유효하지 않은 연쇄 유형: {cascade_type_str}")
        
        # 트리거 조건 변환
        trigger_condition_obj = None
        if trigger_condition:
            expression = trigger_condition.get('expression', '')
            parameters = trigger_condition.get('parameters', {})
            trigger_condition_obj = TriggerCondition(expression=expression, parameters=parameters)
        
        # 깊이 계산 (부모의 깊이 + 1)
        depth = 0
        if parent_event_id in self._cascade_relations:
            # 부모가 이미 자식 노드인 경우, 부모의 깊이 + 1
            for nodes in self._cascade_relations.values():
                for node in nodes:
                    if node.event_id == parent_event_id:
                        depth = node.depth + 1
                        break
        
        # 연쇄 노드 생성
        node = CascadeNode(
            event_id=child_event_id,
            parent_id=parent_event_id,
            depth=depth,
            cascade_type=cascade_type,
            trigger_condition=trigger_condition_obj,
            probability=probability,
            delay_turns=delay_turns
        )
        
        # 연쇄 관계 등록
        if parent_event_id not in self._cascade_relations:
            self._cascade_relations[parent_event_id] = []
        
        self._cascade_relations[parent_event_id].append(node)
        
        return node
    
    def build_cascade_chain(self, root_event_id: str, max_depth: int = 5) -> CascadeChain:
        """
        루트 이벤트로부터 연쇄 체인을 구성합니다.
        
        Args:
            root_event_id: 루트 이벤트 ID
            max_depth: 최대 연쇄 깊이 (기본값: 5)
            
        Returns:
            구성된 연쇄 체인
            
        Raises:
            ValueError: 유효하지 않은 이벤트 ID이거나 연쇄 체인에 사이클이 있는 경우
        """
        # 이벤트 ID 검증
        try:
            self._event_service.get_event_by_id(root_event_id)
        except ValueError as e:
            raise ValueError(f"유효하지 않은 루트 이벤트 ID: {str(e)}")
        
        # 노드 집합 초기화
        nodes: Set[CascadeNode] = set()
        
        # 루트 노드 추가
        root_node = CascadeNode(
            event_id=root_event_id,
            depth=0,
            cascade_type=CascadeType.IMMEDIATE
        )
        nodes.add(root_node)
        
        # 노드 깊이 맵 (이벤트 ID -> 깊이)
        depth_map = {root_event_id: 0}
        
        # BFS로 연쇄 체인 구성
        queue = [root_event_id]
        visited = {root_event_id}
        
        while queue and len(nodes) < 100:  # 안전장치: 최대 100개 노드
            current_id = queue.pop(0)
            current_depth = depth_map[current_id]
            
            if current_id in self._cascade_relations:
                for child_node in self._cascade_relations[current_id]:
                    # 깊이 재설정 (부모 깊이 + 1)
                    updated_child_node = CascadeNode(
                        event_id=child_node.event_id,
                        parent_id=child_node.parent_id,
                        depth=current_depth + 1,  # 부모 깊이 + 1
                        cascade_type=child_node.cascade_type,
                        trigger_condition=child_node.trigger_condition,
                        probability=child_node.probability,
                        delay_turns=child_node.delay_turns,
                        node_id=child_node.node_id
                    )
                    
                    nodes.add(updated_child_node)
                    
                    if child_node.event_id not in visited:
                        visited.add(child_node.event_id)
                        queue.append(child_node.event_id)
                        depth_map[child_node.event_id] = current_depth + 1
        
        # 연쇄 체인 생성
        chain = CascadeChain(
            root_event_id=root_event_id,
            nodes=frozenset(nodes),
            max_depth=max_depth
        )
        
        # 사이클 검사
        if chain.has_cycles():
            raise ValueError("연쇄 체인에 사이클이 있습니다.")
        
        return chain
    
    def calculate_metrics_impact(
        self, 
        triggered_events: List[Any], 
        game_state: Any
    ) -> Dict[str, float]:
        """
        트리거된 이벤트들의 지표 영향도를 계산합니다.
        
        Args:
            triggered_events: 트리거된 이벤트 목록
            game_state: 현재 게임 상태
            
        Returns:
            지표별 영향도 (지표명: 영향값)
        """
        # 지표 영향도 초기화
        metrics_impact: Dict[str, float] = {}
        
        # 각 이벤트의 효과를 누적
        for event in triggered_events:
            # 이벤트 효과 추출 (테스트 코드의 MockEventService와 일치하도록 수정)
            effects = getattr(event, 'effects', [])
            
            for effect in effects:
                # 테스트 코드의 MockEventService에서는 effect가 딕셔너리 형태
                if isinstance(effect, dict):
                    metric = effect.get('metric')
                    value = effect.get('value', 0.0)
                else:
                    metric = getattr(effect, 'metric', None)
                    value = getattr(effect, 'value', 0.0)
                
                if metric:
                    if metric in metrics_impact:
                        metrics_impact[metric] += float(value)
                    else:
                        metrics_impact[metric] = float(value)
        
        return metrics_impact

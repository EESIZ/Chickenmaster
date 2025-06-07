"""
연쇄 이벤트 서비스 구현체.

이 모듈은 ICascadeService 인터페이스를 구현하여 연쇄 이벤트 처리 기능을 제공합니다.
"""

from datetime import datetime, timedelta
import random

from ...core.ports.cascade_port import ICascadeService
from ...core.ports.event_port import IEventService
from ...core.domain.events import Event
from ...core.domain.game_state import GameState
from ...core.domain.cascade import (
    CascadeChain,
    CascadeNode,
    CascadeType,
    PendingEvent,
    CascadeResult,
    TriggerCondition,
)


class CascadeServiceImpl(ICascadeService):
    """연쇄 이벤트 서비스 구현체"""

    def __init__(self, event_service: IEventService):
        """초기화

        Args:
            event_service: 이벤트 서비스 인스턴스
        """
        self._event_service = event_service
        self._cascade_chains: dict[str, CascadeChain] = {}
        self._pending_events: list[PendingEvent] = []
        self._max_cascade_depth = 5  # 기본 최대 연쇄 깊이

    def register_cascade_relation(
        self,
        trigger_event_id: str,
        target_event_id: str,
        cascade_type: CascadeType,
        delay: timedelta | None = None,
        conditions: list[TriggerCondition] | None = None,
        probability: float = 1.0,
        impact_factor: float = 1.0,
    ) -> None:
        """연쇄 관계 등록

        Args:
            trigger_event_id: 트리거 이벤트 ID
            target_event_id: 대상 이벤트 ID
            cascade_type: 연쇄 유형
            delay: 지연 시간 (CascadeType.DELAYED인 경우)
            conditions: 조건 목록 (CascadeType.CONDITIONAL인 경우)
            probability: 발생 확률 (CascadeType.PROBABILISTIC인 경우)
            impact_factor: 영향도 계수
        """
        # list → tuple로 변환하여 hashable 보장
        conditions_tuple = tuple(conditions) if conditions else tuple()

        # 새 노드 생성
        node = CascadeNode(
            event_id=target_event_id,
            cascade_type=cascade_type,
            delay=delay,
            conditions=conditions_tuple,  # tuple 사용
            probability=probability,
            impact_factor=impact_factor,
        )

        # 체인에 노드 추가
        if trigger_event_id not in self._cascade_chains:
            # 초기 노드 맵 생성
            nodes_dict: dict[str, frozenset[CascadeNode]] = {}
            
            self._cascade_chains[trigger_event_id] = CascadeChain(
                trigger_event_id=trigger_event_id, 
                nodes=nodes_dict, 
                max_depth=self._max_cascade_depth
            )

        chain = self._cascade_chains[trigger_event_id]
        
        # 노드 집합 업데이트
        if trigger_event_id not in chain.nodes:
            # 새 frozenset 생성
            nodes_set: frozenset[CascadeNode] = frozenset([node])
            chain.nodes[trigger_event_id] = nodes_set
        else:
            # 기존 frozenset에 노드 추가
            existing_nodes = set(chain.nodes[trigger_event_id])
            existing_nodes.add(node)
            chain.nodes[trigger_event_id] = frozenset(existing_nodes)

    def get_cascade_events(self, trigger_event: Event, game_state: GameState) -> list[Event]:
        """트리거 이벤트로 인한 연쇄 이벤트 목록

        Args:
            trigger_event: 트리거 이벤트
            game_state: 현재 게임 상태

        Returns:
            연쇄 발생 이벤트 목록
        """
        result_events: list[Event] = []

        # 해당 이벤트에 대한 연쇄 체인이 없으면 빈 목록 반환
        if trigger_event.id not in self._cascade_chains:
            return result_events

        chain = self._cascade_chains[trigger_event.id]
        next_nodes = chain.get_next_nodes(trigger_event.id)

        current_time = datetime.now()

        for node in next_nodes:
            # 이벤트 조회
            event = self._event_service.get_event_by_id(node.event_id)
            if not event:
                continue

            # 연쇄 유형에 따른 처리
            if node.cascade_type == CascadeType.IMMEDIATE:
                # 즉시 발생 이벤트
                result_events.append(event)

            elif node.cascade_type == CascadeType.DELAYED:
                # 지연 발생 이벤트
                if node.delay:
                    trigger_time = current_time + node.delay
                    pending = PendingEvent(
                        event=event,
                        trigger_time=trigger_time,
                        conditions=node.conditions,  # 이미 tuple
                        probability=node.probability,
                    )
                    self._pending_events.append(pending)

            elif node.cascade_type == CascadeType.CONDITIONAL:
                # 조건부 발생 이벤트
                all_conditions_met = True
                for condition in node.conditions:
                    if not condition.is_satisfied(game_state):
                        all_conditions_met = False
                        break

                if all_conditions_met:
                    result_events.append(event)

            elif node.cascade_type == CascadeType.PROBABILISTIC:
                # 확률적 발생 이벤트
                if random.random() <= node.probability:
                    result_events.append(event)

        return result_events

    def calculate_cascade_depth(self, initial_event: Event, game_state: GameState) -> int:
        """연쇄 효과 깊이 계산

        Args:
            initial_event: 초기 이벤트
            game_state: 현재 게임 상태

        Returns:
            최대 연쇄 깊이
        """
        if initial_event.id not in self._cascade_chains:
            return 0

        visited: set[str] = set()

        def dfs(event_id: str, depth: int) -> int:
            if event_id in visited:
                return depth

            visited.add(event_id)

            if event_id not in self._cascade_chains:
                return depth

            chain = self._cascade_chains[event_id]
            next_nodes = chain.get_next_nodes(event_id)

            max_child_depth = depth
            for node in next_nodes:
                child_depth = dfs(node.event_id, depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            return max_child_depth

        return dfs(initial_event.id, 0)

    def validate_cascade_limits(self, depth: int) -> bool:
        """연쇄 깊이 제한 검증

        Args:
            depth: 연쇄 깊이

        Returns:
            제한 내 여부 (True: 허용, False: 제한 초과)
        """
        return depth <= self._max_cascade_depth

    def process_cascade_chain(
        self, trigger_event: Event, game_state: GameState, max_depth: int = 5
    ) -> tuple[list[Event], GameState]:
        """전체 연쇄 체인 처리

        Args:
            trigger_event: 트리거 이벤트
            game_state: 현재 게임 상태
            max_depth: 최대 연쇄 깊이

        Returns:
            (발생한 모든 이벤트 목록, 최종 게임 상태) 튜플
        """
        self._max_cascade_depth = max_depth
        processed_events: list[Event] = [trigger_event]
        pending_events: list[PendingEvent] = []
        metrics_impact: dict[str, float] = {}
        current_depth = 0
        cycle_detected = False

        # BFS로 연쇄 관계 탐색
        queue: list[tuple[Event, int]] = [(trigger_event, 0)]  # (이벤트, 깊이)
        visited: set[str] = {trigger_event.id}

        while queue and current_depth <= max_depth:
            current_event, depth = queue.pop(0)
            current_depth = max(current_depth, depth)

            # 연쇄 이벤트 가져오기
            cascade_events = self.get_cascade_events(current_event, game_state)

            for event in cascade_events:
                # 사이클 검사
                if event.id in visited:
                    cycle_detected = True
                    continue

                # 이벤트 처리
                processed_events.append(event)
                visited.add(event.id)

                # 게임 상태 업데이트
                game_state = self._event_service.apply_event(event, game_state)

                # 지표 영향 기록
                if hasattr(event, 'metrics_impact'):
                    for metric, value in event.metrics_impact.items():
                        if metric in metrics_impact:
                            metrics_impact[metric] += value
                        else:
                            metrics_impact[metric] = value

                # 다음 깊이 탐색 예약
                if depth + 1 <= max_depth:
                    queue.append((event, depth + 1))

        # 지연 이벤트 처리
        for pending in self._pending_events:
            if pending.event.id not in visited:
                pending_events.append(pending)

        # 결과 생성 - 튜플로 변환하여 불변성 보장
        CascadeResult(
            events=tuple(processed_events),  # List → Tuple
            pending_events=tuple(pending_events),  # List → Tuple
            metrics_impact=metrics_impact,
            max_depth_reached=current_depth,
            cycle_detected=cycle_detected,
        )

        return processed_events, game_state

    def check_cascade_cycle(self, event_chain: list[Event]) -> bool:
        """연쇄 효과 사이클 검사

        Args:
            event_chain: 이벤트 체인

        Returns:
            사이클 존재 여부 (True: 사이클 있음, False: 사이클 없음)
        """
        event_ids = [event.id for event in event_chain]
        return len(event_ids) != len(set(event_ids))

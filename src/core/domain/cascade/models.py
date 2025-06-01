"""
Cascade 모듈의 도메인 모델.

이 모듈은 연쇄 이벤트 처리를 위한 도메인 객체들을 정의합니다.
모든 객체는 불변(immutable)으로 설계되어 있습니다.

@freeze v0.1.0
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta

from ..events import Event
from ..game_state import GameState


class CascadeType(Enum):
    """연쇄 이벤트 유형"""

    IMMEDIATE = auto()  # 즉시 발생
    DELAYED = auto()  # 지연 발생
    CONDITIONAL = auto()  # 조건부 발생
    PROBABILISTIC = auto()  # 확률적 발생


@dataclass(frozen=True)
class TriggerCondition:
    """이벤트 트리거 조건"""

    metric_name: str
    threshold: float
    comparison: str  # '>', '<', '>=', '<=', '==', '!='

    def is_satisfied(self, game_state: GameState) -> bool:
        """조건 만족 여부 확인

        Args:
            game_state: 현재 게임 상태

        Returns:
            조건 만족 여부
        """
        if not hasattr(game_state, "metrics") or self.metric_name not in game_state.metrics:
            return False

        current_value = game_state.metrics[self.metric_name]

        if self.comparison == ">":
            return current_value > self.threshold
        elif self.comparison == "<":
            return current_value < self.threshold
        elif self.comparison == ">=":
            return current_value >= self.threshold
        elif self.comparison == "<=":
            return current_value <= self.threshold
        elif self.comparison == "==":
            return current_value == self.threshold
        elif self.comparison == "!=":
            return current_value != self.threshold
        else:
            return False  # 알 수 없는 비교 연산자


@dataclass(frozen=True)
class PendingEvent:
    """지연 처리될 이벤트 정보"""

    event: Event
    trigger_time: datetime
    conditions: tuple[TriggerCondition, ...] = field(
        default_factory=tuple
    )  # List → Tuple로 변경 (hashable)
    probability: float = 1.0  # 발생 확률 (0.0 ~ 1.0)

    def is_ready(self, current_time: datetime, game_state: GameState) -> bool:
        """이벤트 발생 준비 여부

        Args:
            current_time: 현재 시간
            game_state: 현재 게임 상태

        Returns:
            발생 준비 여부
        """
        # 시간 조건 확인
        if current_time < self.trigger_time:
            return False

        # 모든 조건 확인
        for condition in self.conditions:
            if not condition.is_satisfied(game_state):
                return False

        return True


@dataclass(frozen=True)
class CascadeNode:
    """연쇄 체인 내 노드"""

    event_id: str
    cascade_type: CascadeType
    delay: timedelta | None = None
    conditions: tuple[TriggerCondition, ...] = field(
        default_factory=tuple
    )  # List → Tuple로 변경 (hashable)
    probability: float = 1.0
    impact_factor: float = 1.0  # 영향도 계수

    def calculate_impact(self, base_severity: float) -> float:
        """영향도 계산

        Args:
            base_severity: 기본 심각도

        Returns:
            조정된 영향도
        """
        return base_severity * self.impact_factor


@dataclass(frozen=True)
class CascadeChain:
    """연쇄 이벤트 체인"""

    trigger_event_id: str
    nodes: dict[str, frozenset[CascadeNode]]  # Set → FrozenSet으로 변경 (hashable)
    max_depth: int = 5

    def get_next_nodes(self, event_id: str) -> frozenset[CascadeNode]:
        """다음 연쇄 노드 목록

        Args:
            event_id: 현재 이벤트 ID

        Returns:
            다음 연쇄 노드 집합
        """
        return self.nodes.get(event_id, frozenset())  # set() → frozenset()으로 변경

    def has_cycle(self) -> bool:
        """사이클 존재 여부 확인

        Returns:
            사이클 존재 여부
        """
        visited = set()
        path = set()

        def dfs(node_id: str) -> bool:
            if node_id in path:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            path.add(node_id)

            for next_node in self.get_next_nodes(node_id):
                if dfs(next_node.event_id):
                    return True

            path.remove(node_id)
            return False

        return dfs(self.trigger_event_id)


@dataclass(frozen=True)
class CascadeResult:
    """연쇄 이벤트 처리 결과"""

    events: tuple[Event, ...]  # List → Tuple로 변경 (hashable)
    pending_events: tuple[PendingEvent, ...]  # List → Tuple로 변경 (hashable)
    metrics_impact: dict[str, float]
    max_depth_reached: int
    cycle_detected: bool = False

    def get_total_impact(self) -> float:
        """총 영향도 계산

        Returns:
            모든 지표 영향의 합계
        """
        return sum(abs(impact) for impact in self.metrics_impact.values())

    def get_most_affected_metric(self) -> str:
        """가장 큰 영향을 받은 지표

        Returns:
            가장 큰 영향을 받은 지표 이름
        """
        if not self.metrics_impact:
            return ""

        return max(self.metrics_impact.items(), key=lambda x: abs(x[1]))[0]

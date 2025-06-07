"""
Cascade 모듈의 도메인 모델.

이 모듈은 연쇄 이벤트 시스템의 핵심 비즈니스 엔티티를 정의합니다.
모든 도메인 객체는 불변(immutable)이며 외부 의존성이 없습니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from collections.abc import Mapping
from uuid import UUID, uuid4


class CascadeType(Enum):
    """연쇄 이벤트 유형."""
    
    IMMEDIATE = auto()  # 즉시 발생하는 연쇄 이벤트
    DELAYED = auto()    # 지연 후 발생하는 연쇄 이벤트
    CONDITIONAL = auto() # 조건부 발생하는 연쇄 이벤트
    PROBABILISTIC = auto() # 확률적으로 발생하는 연쇄 이벤트


@dataclass(frozen=True)
class TriggerCondition:
    """
    이벤트 트리거 조건.
    
    조건식과 필요한 파라미터를 포함합니다.
    """
    
    expression: str  # 조건식 (예: "metrics.money > threshold")
    parameters: Mapping[str, int | float | str | bool] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """불변 매핑으로 파라미터 변환."""
        # frozen=True로 인해 직접 할당이 불가능하므로 object.__setattr__ 사용
        if not isinstance(self.parameters, Mapping):
            object.__setattr__(self, 'parameters', dict(self.parameters))
        
        # 파라미터가 비어있지만 expression에 파라미터가 필요한 경우 검증
        if not self.parameters and '{' in self.expression:
            raise ValueError(f"조건식 '{self.expression}'에 파라미터가 필요하지만 제공되지 않았습니다.")


@dataclass(frozen=True)
class PendingEvent:
    """
    지연 처리될 이벤트 정보.
    
    특정 턴 이후에 발생할 이벤트의 정보를 담습니다.
    """
    
    event_id: str
    delay_turns: int  # 지연 턴 수
    trigger_turn: int  # 실제 트리거될 턴
    cascade_type: CascadeType = CascadeType.DELAYED
    probability: float = 1.0  # 발생 확률 (0.0~1.0)
    
    def __post_init__(self) -> None:
        """값 검증."""
        if self.delay_turns < 1:
            raise ValueError("지연 턴 수는 1 이상이어야 합니다.")
        
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("확률은 0.0에서 1.0 사이여야 합니다.")


@dataclass(frozen=True)
class CascadeNode:
    """
    연쇄 체인 내의 개별 노드.
    
    연쇄 체인 내에서 하나의 이벤트 노드를 표현합니다.
    """
    
    event_id: str
    depth: int  # 연쇄 깊이 (루트는 0)
    cascade_type: CascadeType
    parent_id: str | None = None  # 부모 이벤트 ID (없으면 None)
    node_id: UUID = field(default_factory=uuid4)  # 노드 고유 ID
    trigger_condition: TriggerCondition | None = None  # 트리거 조건
    probability: float = 1.0  # 발생 확률 (0.0~1.0)
    delay_turns: int = 0  # 지연 턴 수
    
    def __post_init__(self) -> None:
        """값 검증."""
        if self.depth < 0:
            raise ValueError("연쇄 깊이는 0 이상이어야 합니다.")
        
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("확률은 0.0에서 1.0 사이여야 합니다.")
        
        if self.delay_turns < 0:
            raise ValueError("지연 턴 수는 0 이상이어야 합니다.")
        
        # 지연 이벤트인데 지연 턴이 0인 경우
        if self.cascade_type == CascadeType.DELAYED and self.delay_turns == 0:
            raise ValueError("지연 이벤트의 지연 턴 수는 1 이상이어야 합니다.")
        
        # 조건부 이벤트인데 조건이 없는 경우
        if self.cascade_type == CascadeType.CONDITIONAL and self.trigger_condition is None:
            raise ValueError("조건부 이벤트는 트리거 조건이 필요합니다.")
    
    def is_root(self) -> bool:
        """루트 노드인지 확인."""
        return self.parent_id is None and self.depth == 0
    
    def is_delayed(self) -> bool:
        """지연 이벤트인지 확인."""
        return self.cascade_type == CascadeType.DELAYED and self.delay_turns > 0
    
    def is_conditional(self) -> bool:
        """조건부 이벤트인지 확인."""
        return self.cascade_type == CascadeType.CONDITIONAL and self.trigger_condition is not None
    
    def is_probabilistic(self) -> bool:
        """확률적 이벤트인지 확인."""
        return self.cascade_type == CascadeType.PROBABILISTIC and self.probability < 1.0


@dataclass(frozen=True)
class CascadeChain:
    """
    연쇄 이벤트 체인.
    
    연쇄적으로 발생하는 이벤트들의 전체 체인을 표현합니다.
    """
    
    root_event_id: str  # 최초 트리거 이벤트 ID
    nodes: frozenset[CascadeNode]  # 연쇄 노드들의 집합
    max_depth: int = 5  # 최대 연쇄 깊이
    chain_id: UUID = field(default_factory=uuid4)  # 체인 고유 ID
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """값 검증 및 초기화."""
        if not self.nodes:
            raise ValueError("연쇄 체인에는 최소 하나의 노드가 필요합니다.")
        
        if self.max_depth < 1:
            raise ValueError("최대 연쇄 깊이는 1 이상이어야 합니다.")
        
        # 루트 이벤트 ID가 노드 중에 있는지 확인
        root_exists = any(node.event_id == self.root_event_id and node.is_root() for node in self.nodes)
        if not root_exists:
            raise ValueError(f"루트 이벤트 ID '{self.root_event_id}'에 해당하는 루트 노드가 없습니다.")
    
    def get_nodes_at_depth(self, depth: int) -> tuple[CascadeNode, ...]:
        """특정 깊이의 노드들을 반환."""
        return tuple(node for node in self.nodes if node.depth == depth)
    
    def get_child_nodes(self, parent_id: str) -> tuple[CascadeNode, ...]:
        """특정 부모 노드의 자식 노드들을 반환."""
        return tuple(node for node in self.nodes if node.parent_id == parent_id)
    
    def get_node_by_event_id(self, event_id: str) -> CascadeNode | None:
        """이벤트 ID로 노드를 찾아 반환."""
        for node in self.nodes:
            if node.event_id == event_id:
                return node
        return None
    
    def get_max_actual_depth(self) -> int:
        """실제 최대 깊이를 반환."""
        if not self.nodes:
            return 0
        return max(node.depth for node in self.nodes)
    
    def has_cycles(self) -> bool:
        """사이클이 있는지 확인."""
        # 각 노드의 부모 체인을 추적하여 사이클 검사
        for node in self.nodes:
            if self._check_cycle_from_node(node):
                return True
        return False
    
    def _check_cycle_from_node(self, start_node: CascadeNode) -> bool:
        """특정 노드에서 시작하여 사이클이 있는지 확인."""
        visited_event_ids = set()
        current_id = start_node.event_id
        
        while current_id:
            if current_id in visited_event_ids:
                return True  # 사이클 발견
            
            visited_event_ids.add(current_id)
            
            # 부모 노드 찾기
            parent_id = None
            for node in self.nodes:
                if node.event_id == current_id:
                    parent_id = node.parent_id
                    break
            
            current_id = parent_id
        
        return False


@dataclass(frozen=True)
class CascadeResult:
    """
    연쇄 이벤트 처리 결과.
    
    연쇄 이벤트 체인 처리 결과를 표현합니다.
    """
    
    triggered_events: tuple[str, ...]  # 트리거된 이벤트 ID 목록
    pending_events: tuple[PendingEvent, ...]  # 지연된 이벤트 정보
    metrics_impact: dict[str, float]  # 지표 영향도
    depth_reached: int  # 도달한 최대 깊이
    result_id: UUID = field(default_factory=uuid4)  # 결과 고유 ID
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """값 검증 및 불변 컬렉션으로 변환."""
        if self.depth_reached < 0:
            raise ValueError("도달한 최대 깊이는 0 이상이어야 합니다.")
        
        # metrics_impact를 불변으로 만들기 위한 처리
        # frozen=True로 인해 직접 할당이 불가능하므로 object.__setattr__ 사용
        object.__setattr__(self, 'metrics_impact', dict(self.metrics_impact))
    
    def get_total_events_count(self) -> int:
        """총 이벤트 수 (트리거 + 지연) 반환."""
        return len(self.triggered_events) + len(self.pending_events)
    
    def get_total_metrics_impact(self) -> float:
        """총 지표 영향도 합계 반환."""
        return sum(abs(impact) for impact in self.metrics_impact.values())
    
    def has_pending_events(self) -> bool:
        """지연 이벤트가 있는지 확인."""
        return len(self.pending_events) > 0

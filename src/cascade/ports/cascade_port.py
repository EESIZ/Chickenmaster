"""
연쇄 이벤트 서비스 인터페이스.

이 모듈은 연쇄 이벤트 처리 관련 비즈니스 로직 경계를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from src.cascade.domain.models import CascadeChain, CascadeNode, CascadeResult, PendingEvent

# @freeze v0.1.0
# 타입 변수 정의
GameState = TypeVar('GameState')
Event = TypeVar('Event')


class ICascadeService(ABC):
    """
    연쇄 이벤트 처리 관련 비즈니스 로직 경계를 정의하는 인터페이스.
    
    이 인터페이스는 이벤트 간 연쇄 관계 및 의존성 설정, 연쇄 깊이 제한 및 사이클 검사,
    스토리라인 및 플레이 흐름 구성 등의 기능을 제공합니다.
    """
    
    @abstractmethod
    def get_cascade_events(self, event_id: str, game_state: GameState) -> list[str]:
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
        pass
    
    @abstractmethod
    def calculate_cascade_depth(self, event_chain: CascadeChain) -> int:
        """
        연쇄 효과 깊이를 계산합니다.
        
        Args:
            event_chain: 연쇄 이벤트 체인
            
        Returns:
            연쇄 효과의 최대 깊이
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def process_cascade_chain(
        self, 
        root_event: Event, 
        game_state: GameState,
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
        pass
    
    @abstractmethod
    def check_cascade_cycle(self, event_chain: CascadeChain) -> bool:
        """
        연쇄 효과 사이클을 검사합니다.
        
        Args:
            event_chain: 연쇄 이벤트 체인
            
        Returns:
            사이클이 있으면 True, 없으면 False
        """
        pass
    
    @abstractmethod
    def get_pending_events(self, current_turn: int) -> list[PendingEvent]:
        """
        현재 턴에 처리해야 할 지연 이벤트 목록을 반환합니다.
        
        Args:
            current_turn: 현재 게임 턴
            
        Returns:
            처리해야 할 지연 이벤트 목록
        """
        pass
    
    @abstractmethod
    def register_cascade_relation(
        self, 
        parent_event_id: str, 
        child_event_id: str,
        cascade_type: str,
        trigger_condition: dict | None = None,
        probability: float = 1.0,
        delay_turns: int = 0
    ) -> CascadeNode:
        """
        두 이벤트 간의 연쇄 관계를 등록합니다.
        
        Args:
            parent_event_id: 부모 이벤트 ID
            child_event_id: 자식 이벤트 ID
            cascade_type: 연쇄 유형 ("IMMEDIATE", "DELAYED", "CONDITIONAL", "PROBABILISTIC")
            trigger_condition: 트리거 조건 (조건부 이벤트인 경우)
            probability: 발생 확률 (0.0~1.0, 기본값: 1.0)
            delay_turns: 지연 턴 수 (지연 이벤트인 경우, 기본값: 0)
            
        Returns:
            생성된 연쇄 노드
            
        Raises:
            ValueError: 유효하지 않은 이벤트 ID 또는 파라미터인 경우
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def calculate_metrics_impact(
        self, 
        triggered_events: list[Event], 
        game_state: GameState
    ) -> dict[str, float]:
        """
        트리거된 이벤트들의 지표 영향도를 계산합니다.
        
        Args:
            triggered_events: 트리거된 이벤트 목록
            game_state: 현재 게임 상태
            
        Returns:
            지표별 영향도 (지표명: 영향값)
        """
        pass

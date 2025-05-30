"""
연쇄 효과 포트 인터페이스
이벤트 연쇄 효과 처리 관련 비즈니스 로직 경계를 정의합니다.

@freeze v0.1.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from ..domain.events import Event
from ..domain.game_state import GameState


class ICascadeService(ABC):
    """연쇄 효과 처리 포트 인터페이스"""
    
    @abstractmethod
    def get_cascade_events(
        self, 
        trigger_event: Event, 
        game_state: GameState
    ) -> List[Event]:
        """트리거 이벤트로 인한 연쇄 이벤트 목록
        
        Args:
            trigger_event: 트리거 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            연쇄 발생 이벤트 목록
        """
        pass
    
    @abstractmethod
    def calculate_cascade_depth(
        self, 
        initial_event: Event, 
        game_state: GameState
    ) -> int:
        """연쇄 효과 깊이 계산
        
        Args:
            initial_event: 초기 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            최대 연쇄 깊이
        """
        pass
    
    @abstractmethod
    def validate_cascade_limits(self, depth: int) -> bool:
        """연쇄 깊이 제한 검증
        
        Args:
            depth: 연쇄 깊이
            
        Returns:
            제한 내 여부 (True: 허용, False: 제한 초과)
        """
        pass
    
    @abstractmethod
    def process_cascade_chain(
        self, 
        trigger_event: Event, 
        game_state: GameState,
        max_depth: int = 5
    ) -> Tuple[List[Event], GameState]:
        """전체 연쇄 체인 처리
        
        Args:
            trigger_event: 트리거 이벤트
            game_state: 현재 게임 상태
            max_depth: 최대 연쇄 깊이
            
        Returns:
            (발생한 모든 이벤트 목록, 최종 게임 상태) 튜플
        """
        pass
    
    @abstractmethod
    def check_cascade_cycle(
        self,
        event_chain: List[Event]
    ) -> bool:
        """연쇄 효과 사이클 검사
        
        Args:
            event_chain: 이벤트 체인
            
        Returns:
            사이클 존재 여부 (True: 사이클 있음, False: 사이클 없음)
        """
        pass

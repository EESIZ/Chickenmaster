"""
이벤트 포트 인터페이스
이벤트 처리 관련 비즈니스 로직 경계를 정의합니다.

@freeze v0.1.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple

from ..domain.events import Event
from ..domain.game_state import GameState


class IEventService(ABC):
    """이벤트 처리 포트 인터페이스"""
    
    @abstractmethod
    def get_applicable_events(
        self, 
        game_state: GameState,
        category: Optional[str] = None
    ) -> List[Event]:
        """현재 상태에서 발생 가능한 이벤트 목록 반환
        
        Args:
            game_state: 현재 게임 상태
            category: 필터링할 이벤트 카테고리 (선택적)
            
        Returns:
            발생 가능한 이벤트 목록
        """
        pass
    
    @abstractmethod
    def apply_event_effects(
        self, 
        event: Event, 
        game_state: GameState
    ) -> GameState:
        """이벤트 효과를 적용한 새 게임 상태 반환
        
        Args:
            event: 적용할 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            효과가 적용된 새 게임 상태
        """
        pass
    
    @abstractmethod
    def validate_event_conditions(
        self, 
        event: Event, 
        game_state: GameState
    ) -> bool:
        """이벤트 발생 조건 검증
        
        Args:
            event: 검증할 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            조건 충족 여부
        """
        pass
    
    @abstractmethod
    def evaluate_event_probability(
        self,
        event: Event,
        game_state: GameState
    ) -> float:
        """이벤트 발생 확률 계산
        
        Args:
            event: 확률을 계산할 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            0.0~1.0 사이의 발생 확률
        """
        pass
    
    @abstractmethod
    def check_event_cooldown(
        self,
        event: Event,
        game_state: GameState
    ) -> bool:
        """이벤트 쿨다운 상태 확인
        
        Args:
            event: 쿨다운을 확인할 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            이벤트 발생 가능 여부 (True: 쿨다운 종료, False: 쿨다운 중)
        """
        pass

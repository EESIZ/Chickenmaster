"""
이벤트 서비스 인터페이스.

이 모듈은 이벤트 처리 관련 비즈니스 로직 경계를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

# 타입 변수 정의
GameState = TypeVar('GameState')
Event = TypeVar('Event')

# @freeze v0.1.0
class IEventService(ABC):
    """
    이벤트 처리 관련 비즈니스 로직 경계를 정의하는 인터페이스.
    
    이 인터페이스는 이벤트 조회, 효과 적용, 조건 검증 등의 기능을 제공합니다.
    """
    
    @abstractmethod
    def get_event_by_id(self, event_id: str) -> Event:
        """
        ID로 이벤트를 조회합니다.
        
        Args:
            event_id: 이벤트 ID
            
        Returns:
            조회된 이벤트
            
        Raises:
            ValueError: 유효하지 않은 이벤트 ID인 경우
        """
        pass
    
    @abstractmethod
    def apply_event_effects(self, event: Event, game_state: GameState) -> GameState:
        """
        이벤트 효과를 적용한 새 게임 상태를 반환합니다.
        
        Args:
            event: 적용할 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            이벤트 효과가 적용된 새 게임 상태
        """
        pass
    
    @abstractmethod
    def evaluate_trigger_condition(self, condition: dict[str, Any], game_state: GameState) -> bool:
        """
        트리거 조건을 평가합니다.
        
        Args:
            condition: 트리거 조건
            game_state: 현재 게임 상태
            
        Returns:
            조건이 충족되면 True, 아니면 False
        """
        pass
    
    @abstractmethod
    def get_applicable_events(self, game_state: GameState) -> list[Event]:
        """
        현재 상태에서 발생 가능한 이벤트 목록을 반환합니다.
        
        Args:
            game_state: 현재 게임 상태
            
        Returns:
            발생 가능한 이벤트 목록
        """
        pass
    
    @abstractmethod
    def check_event_cooldown(self, event_id: str, current_turn: int) -> bool:
        """
        이벤트 쿨다운 상태를 확인합니다.
        
        Args:
            event_id: 이벤트 ID
            current_turn: 현재 게임 턴
            
        Returns:
            쿨다운이 끝났으면 True, 아직 쿨다운 중이면 False
        """
        pass
    
    @abstractmethod
    def evaluate_event_probability(self, event: Event, game_state: GameState) -> float:
        """
        이벤트 발생 확률을 계산합니다.
        
        Args:
            event: 이벤트
            game_state: 현재 게임 상태
            
        Returns:
            이벤트 발생 확률 (0.0~1.0)
        """
        pass

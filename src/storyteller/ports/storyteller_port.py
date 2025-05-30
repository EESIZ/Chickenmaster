"""
스토리텔러 서비스 인터페이스.

이 모듈은 스토리텔러 처리 관련 비즈니스 로직 경계를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.storyteller.domain.models import NarrativeResponse, StoryContext, StoryPattern

# @freeze v0.1.0
class IStorytellerService(ABC):
    """
    스토리텔러 서비스 인터페이스.
    
    이 인터페이스는 게임 상태에 따른 내러티브 생성, 이벤트 제안,
    지표 분석 등의 기능을 제공합니다.
    """
    
    @abstractmethod
    def generate_narrative(self, context: StoryContext) -> NarrativeResponse:
        """
        현재 게임 상태에 맞는 내러티브를 생성합니다.
        
        Args:
            context: 현재 게임 상태 컨텍스트
            
        Returns:
            생성된 내러티브 응답
            
        Raises:
            ValueError: 유효하지 않은 컨텍스트인 경우
        """
        pass
    
    @abstractmethod
    def suggest_event(self, context: StoryContext) -> Optional[str]:
        """
        현재 상황에 적절한 이벤트를 제안합니다.
        
        Args:
            context: 현재 게임 상태 컨텍스트
            
        Returns:
            제안된 이벤트 ID (없으면 None)
            
        Raises:
            ValueError: 유효하지 않은 컨텍스트인 경우
        """
        pass
    
    @abstractmethod
    def analyze_metrics_trend(self, context: StoryContext) -> Dict[str, float]:
        """
        지표 변화 추세를 분석합니다.
        
        Args:
            context: 현재 게임 상태 컨텍스트
            
        Returns:
            지표별 변화 추세 (지표명: 변화율)
            
        Raises:
            ValueError: 유효하지 않은 컨텍스트인 경우
        """
        pass
    
    @abstractmethod
    def get_story_patterns(self, context: StoryContext) -> List[StoryPattern]:
        """
        현재 상황에 적용 가능한 스토리 패턴을 반환합니다.
        
        Args:
            context: 현재 게임 상태 컨텍스트
            
        Returns:
            적용 가능한 스토리 패턴 목록
            
        Raises:
            ValueError: 유효하지 않은 컨텍스트인 경우
        """
        pass 
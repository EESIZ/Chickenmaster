"""
이벤트 저장소 포트 인터페이스
이벤트 데이터 관리 관련 비즈니스 로직 경계를 정의합니다.

@freeze v0.1.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

from ..domain.events import Event


class IEventBank(ABC):
    """이벤트 저장소 포트 인터페이스"""
    
    @abstractmethod
    def load_events_by_category(self, category: str) -> List[Event]:
        """카테고리별 이벤트 로딩
        
        Args:
            category: 이벤트 카테고리
            
        Returns:
            해당 카테고리의 이벤트 목록
        """
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """ID로 특정 이벤트 조회
        
        Args:
            event_id: 이벤트 ID
            
        Returns:
            이벤트 객체 또는 None (없을 경우)
        """
        pass
    
    @abstractmethod
    def filter_events_by_conditions(
        self, 
        conditions: Dict[str, Any]
    ) -> List[Event]:
        """조건에 맞는 이벤트 필터링
        
        Args:
            conditions: 필터링 조건 (키: 속성명, 값: 조건값)
            
        Returns:
            조건에 맞는 이벤트 목록
        """
        pass
    
    @abstractmethod
    def get_available_categories(self) -> List[str]:
        """사용 가능한 이벤트 카테고리 목록
        
        Returns:
            카테고리 목록
        """
        pass
    
    @abstractmethod
    def validate_event_data(self) -> Dict[str, List[str]]:
        """이벤트 데이터 무결성 검증
        
        Returns:
            오류 목록 (키: 이벤트 ID, 값: 오류 메시지 목록)
        """
        pass
    
    @abstractmethod
    def reload_events(self) -> int:
        """이벤트 데이터 다시 로드
        
        Returns:
            로드된 이벤트 수
        """
        pass

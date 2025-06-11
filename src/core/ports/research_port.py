"""
연구개발(R&D) 포트 인터페이스
연구개발 관련 비즈니스 로직 경계를 정의합니다.

@freeze v0.1.0
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple

from ..domain.research import (
    ResearchProject, 
    ResearchResult, 
    ResearchType, 
    ResearchConfiguration
)
from ..domain.game_state import GameState
from ..domain.metrics import MetricsSnapshot


class IResearchService(ABC):
    """연구개발 서비스 포트 인터페이스"""
    
    @abstractmethod
    def get_available_projects(
        self, 
        current_money: int,
        research_type: Optional[ResearchType] = None
    ) -> List[ResearchProject]:
        """현재 자금으로 시작 가능한 연구 프로젝트 목록
        
        Args:
            current_money: 현재 보유 자금
            research_type: 필터링할 연구 유형 (None이면 전체)
            
        Returns:
            시작 가능한 연구 프로젝트 리스트
        """
        pass
    
    @abstractmethod
    def execute_research(
        self,
        project: ResearchProject,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> ResearchResult:
        """연구 프로젝트 실행
        
        Args:
            project: 실행할 연구 프로젝트
            game_state: 현재 게임 상태
            metrics_snapshot: 현재 지표 스냅샷
            
        Returns:
            연구 결과
        """
        pass
    
    @abstractmethod
    def calculate_success_probability(
        self,
        project: ResearchProject,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """실제 성공 확률 계산 (게임 상태 고려)
        
        Args:
            project: 연구 프로젝트
            game_state: 현재 게임 상태
            metrics_snapshot: 현재 지표 스냅샷
            
        Returns:
            조정된 성공 확률 (0.0 ~ 1.0)
        """
        pass
    
    @abstractmethod
    def simulate_research_outcome(
        self,
        project: ResearchProject,
        success_probability: float
    ) -> Tuple[bool, str]:
        """연구 결과 시뮬레이션
        
        Args:
            project: 연구 프로젝트
            success_probability: 성공 확률
            
        Returns:
            (성공 여부, 결과 메시지) 튜플
        """
        pass
    
    @abstractmethod
    def get_research_recommendations(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot,
        max_recommendations: int = 3
    ) -> List[ResearchProject]:
        """현재 상황에 맞는 연구 추천
        
        Args:
            game_state: 현재 게임 상태
            metrics_snapshot: 현재 지표 스냅샷
            max_recommendations: 최대 추천 개수
            
        Returns:
            추천 연구 프로젝트 리스트
        """
        pass
    
    @abstractmethod
    def calculate_risk_assessment(
        self,
        project: ResearchProject,
        game_state: GameState
    ) -> Dict[str, float]:
        """연구 리스크 평가
        
        Args:
            project: 연구 프로젝트
            game_state: 현재 게임 상태
            
        Returns:
            리스크 평가 결과 (키: 리스크 유형, 값: 위험도 0.0~1.0)
        """
        pass


class IResearchRepository(ABC):
    """연구개발 저장소 포트 인터페이스"""
    
    @abstractmethod
    def get_project_by_id(self, project_id: str) -> Optional[ResearchProject]:
        """ID로 연구 프로젝트 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            연구 프로젝트 (없으면 None)
        """
        pass
    
    @abstractmethod
    def get_all_projects(self) -> List[ResearchProject]:
        """모든 연구 프로젝트 조회
        
        Returns:
            전체 연구 프로젝트 리스트
        """
        pass
    
    @abstractmethod
    def get_projects_by_type(self, research_type: ResearchType) -> List[ResearchProject]:
        """연구 유형별 프로젝트 조회
        
        Args:
            research_type: 연구 유형
            
        Returns:
            해당 유형 연구 프로젝트 리스트
        """
        pass
    
    @abstractmethod
    def save_research_result(self, result: ResearchResult) -> bool:
        """연구 결과 저장
        
        Args:
            result: 저장할 연구 결과
            
        Returns:
            저장 성공 여부
        """
        pass
    
    @abstractmethod
    def get_research_history(
        self, 
        limit: int = 10
    ) -> List[ResearchResult]:
        """연구 이력 조회
        
        Args:
            limit: 조회할 최대 개수
            
        Returns:
            연구 결과 이력 리스트
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> ResearchConfiguration:
        """연구개발 설정 조회
        
        Returns:
            현재 연구개발 설정
        """
        pass
    
    @abstractmethod
    def update_configuration(self, config: ResearchConfiguration) -> bool:
        """연구개발 설정 업데이트
        
        Args:
            config: 새로운 설정
            
        Returns:
            업데이트 성공 여부
        """
        pass


class IResearchEventPublisher(ABC):
    """연구개발 이벤트 발행 포트 인터페이스"""
    
    @abstractmethod
    def publish_research_started(
        self,
        project: ResearchProject,
        game_state: GameState
    ) -> None:
        """연구 시작 이벤트 발행
        
        Args:
            project: 시작된 연구 프로젝트
            game_state: 현재 게임 상태
        """
        pass
    
    @abstractmethod
    def publish_research_completed(
        self,
        result: ResearchResult,
        game_state: GameState
    ) -> None:
        """연구 완료 이벤트 발행
        
        Args:
            result: 연구 결과
            game_state: 업데이트된 게임 상태
        """
        pass
    
    @abstractmethod
    def publish_breakthrough_achieved(
        self,
        result: ResearchResult,
        breakthrough_type: str
    ) -> None:
        """혁신 달성 이벤트 발행
        
        Args:
            result: 연구 결과
            breakthrough_type: 혁신 유형
        """
        pass 
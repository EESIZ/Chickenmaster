"""
지표 포트 인터페이스
지표 관리 관련 비즈니스 로직 경계를 정의합니다.

@freeze v0.1.0
"""

from abc import ABC, abstractmethod

from ..domain.game_state import GameState
from ..domain.metrics import Metric, MetricsSnapshot


class IMetricService(ABC):
    """지표 관리 포트 인터페이스"""
    
    @abstractmethod
    def calculate_happiness_pain_balance(
        self, 
        current_happiness: int, 
        current_pain: int,
        effects: dict[str, int]
    ) -> tuple[int, int]:
        """행복-고통 시소 계산 (합계 = 100 유지)
        
        Args:
            current_happiness: 현재 행복 수치
            current_pain: 현재 고통 수치
            effects: 적용할 효과
            
        Returns:
            (새 행복 수치, 새 고통 수치) 튜플
        """
        pass
    
    @abstractmethod
    def check_bankruptcy_risk(self, game_state: GameState) -> float:
        """파산 위험도 계산 (0.0 ~ 1.0)
        
        Args:
            game_state: 현재 게임 상태
            
        Returns:
            파산 위험도 (0.0: 안전, 1.0: 파산 임박)
        """
        pass
    
    @abstractmethod
    def calculate_game_over_conditions(
        self, 
        game_state: GameState
    ) -> dict[str, bool]:
        """게임 종료 조건들 검증
        
        Args:
            game_state: 현재 게임 상태
            
        Returns:
            조건별 게임 종료 여부 (키: 조건명, 값: 종료 여부)
        """
        pass
    
    @abstractmethod
    def get_metric_bounds(self) -> dict[str, tuple[int, int]]:
        """각 지표의 최소/최대값 반환
        
        Returns:
            지표별 (최소값, 최대값) 튜플 딕셔너리
        """
        pass
    
    @abstractmethod
    def apply_tradeoff_effects(
        self,
        primary_effect: dict[str, int],
        metrics_snapshot: MetricsSnapshot
    ) -> dict[str, int]:
        """트레이드오프 효과 적용
        
        Args:
            primary_effect: 원래 효과
            metrics_snapshot: 현재 지표 스냅샷
            
        Returns:
            트레이드오프가 적용된 최종 효과
        """
        pass
    
    @abstractmethod
    def get_critical_metrics(
        self,
        game_state: GameState
    ) -> dict[str, Metric]:
        """위험 수준의 지표 목록 반환
        
        Args:
            game_state: 현재 게임 상태
            
        Returns:
            위험 수준 지표 딕셔너리 (키: 지표명, 값: 지표 객체)
        """
        pass

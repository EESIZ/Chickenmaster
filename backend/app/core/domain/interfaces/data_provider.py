"""
게임 데이터 제공자 인터페이스

이 모듈은 게임 초기값과 설정을 제공하는 인터페이스를 정의합니다.
헥사고널 아키텍처의 포트(Port) 역할을 합니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Protocol


@dataclass(frozen=True)
class GameMetric:
    """게임 메트릭 데이터"""
    base_value: float
    min_value: float
    max_value: float | str  # 'inf'도 허용
    description: str


@dataclass(frozen=True)
class TradeoffRelationship:
    """트레이드오프 관계 데이터"""
    target_metric: str
    impact_factor: float
    description: str


class GameDataProvider(Protocol):
    """
    게임 데이터 제공자 프로토콜
    
    이 프로토콜을 구현하는 클래스는 게임의 초기값과 설정 데이터를 제공해야 합니다.
    데이터 소스는 엑셀, JSON, YAML 등 다양할 수 있습니다.
    """
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        """게임 핵심 지표 데이터를 반환합니다."""
        ...
    
    def get_game_constants(self) -> Dict[str, Any]:
        """게임 상수 데이터를 반환합니다."""
        ...
    
    def get_tradeoff_relationships(self) -> Dict[str, Dict[str, TradeoffRelationship]]:
        """지표 간 트레이드오프 관계 데이터를 반환합니다."""
        ...
    
    def get_uncertainty_weights(self) -> Dict[str, float]:
        """불확실성 가중치 데이터를 반환합니다."""
        ...
    
    def get_probability_thresholds(self) -> Dict[str, float]:
        """확률 임계값 데이터를 반환합니다."""
        ...
    
    def get_warning_thresholds(self) -> Dict[str, Dict[str, float]]:
        """경고 임계값 데이터를 반환합니다."""
        ... 
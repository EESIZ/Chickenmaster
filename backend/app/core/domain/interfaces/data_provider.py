"""
게임 데이터 제공자 인터페이스

이 모듈은 게임 초기값과 설정을 제공하는 인터페이스를 정의합니다.
헥사고널 아키텍처의 포트(Port) 역할을 합니다.

중요: 모든 데이터 제공자는 읽기 전용(Read-Only)이어야 합니다.
데이터 소스(엑셀, JSON 등)는 외부에서만 수정되어야 하며,
코드에서는 절대 데이터를 변경해서는 안 됩니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Protocol


@dataclass(frozen=True)
class GameMetric:
    """
    게임 메트릭 데이터 - 불변 객체
    
    엑셀 파일에서 읽어온 메트릭 정보를 담는 불변 데이터 클래스입니다.
    """
    base_value: float
    min_value: float
    max_value: float | str  # 'inf'도 허용
    description: str


@dataclass(frozen=True)
class TradeoffRelationship:
    """
    트레이드오프 관계 데이터 - 불변 객체
    
    지표 간의 트레이드오프 관계를 나타내는 불변 데이터 클래스입니다.
    """
    target_metric: str
    impact_factor: float
    description: str


class GameDataProvider(Protocol):
    """
    게임 데이터 제공자 프로토콜 (읽기 전용)
    
    이 프로토콜을 구현하는 클래스는 게임의 초기값과 설정 데이터를 제공해야 합니다.
    데이터 소스는 엑셀, JSON, YAML 등 다양할 수 있습니다.
    
    ⚠️ 중요한 아키텍처 원칙:
    1. 모든 메서드는 읽기 전용이어야 합니다.
    2. 데이터 소스를 수정하는 메서드는 절대 포함하지 않습니다.
    3. 반환되는 데이터는 불변 객체이거나 복사본이어야 합니다.
    4. 데이터 흐름: 외부 데이터 소스 → 읽기 → 게임 로직
    
    데이터 수정이 필요한 경우:
    - 엑셀 파일: 직접 엑셀에서 수정
    - JSON 파일: 텍스트 에디터에서 수정
    - 코드에서는 절대 데이터 소스를 변경하지 않음
    """
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        """
        게임 핵심 지표 데이터를 반환합니다.
        
        Returns:
            Dict[str, GameMetric]: 메트릭 이름을 키로 하는 불변 메트릭 객체들
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...
    
    def get_game_constants(self) -> Dict[str, Any]:
        """
        게임 상수 데이터를 반환합니다.
        
        Returns:
            Dict[str, Any]: 상수 이름을 키로 하는 상수 값들
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...
    
    def get_tradeoff_relationships(self) -> Dict[str, Dict[str, TradeoffRelationship]]:
        """
        지표 간 트레이드오프 관계 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, TradeoffRelationship]]: 소스 메트릭별 트레이드오프 관계들
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...
    
    def get_uncertainty_weights(self) -> Dict[str, float]:
        """
        불확실성 가중치 데이터를 반환합니다.
        
        Returns:
            Dict[str, float]: 메트릭별 불확실성 가중치
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...
    
    def get_probability_thresholds(self) -> Dict[str, float]:
        """
        확률 임계값 데이터를 반환합니다.
        
        Returns:
            Dict[str, float]: 확률 임계값들
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...
    
    def get_warning_thresholds(self) -> Dict[str, Dict[str, float]]:
        """
        경고 임계값 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, float]]: 메트릭별 경고 임계값들
            
        Note:
            반환되는 데이터는 읽기 전용입니다. 수정하지 마세요.
        """
        ...


class ReadOnlyDataProvider(ABC):
    """
    읽기 전용 데이터 제공자 추상 클래스
    
    GameDataProvider 프로토콜을 구현하는 클래스들의 기본 클래스입니다.
    데이터 무결성을 보장하기 위한 추가적인 보호 기능을 제공합니다.
    """
    
    def __init__(self, data_source_path: str):
        """
        Args:
            data_source_path: 데이터 소스 파일 경로 (읽기 전용)
        """
        self._data_source_path = data_source_path
        self._validate_data_source()
    
    @abstractmethod
    def _validate_data_source(self) -> None:
        """
        데이터 소스의 유효성을 검증합니다.
        
        Raises:
            FileNotFoundError: 데이터 소스 파일이 존재하지 않을 때
            ValueError: 데이터 소스 형식이 올바르지 않을 때
        """
        pass
    
    def get_data_source_path(self) -> str:
        """
        데이터 소스 파일 경로를 반환합니다.
        
        Returns:
            str: 읽기 전용 데이터 소스 파일 경로
        """
        return self._data_source_path
    
    def _ensure_immutable_copy(self, data: Any) -> Any:
        """
        데이터의 불변 복사본을 생성합니다.
        
        Args:
            data: 복사할 데이터
            
        Returns:
            Any: 불변 복사본
            
        Note:
            이 메서드는 데이터 무결성을 보장하기 위해 사용됩니다.
        """
        import copy
        return copy.deepcopy(data) 
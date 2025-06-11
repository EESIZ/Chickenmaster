"""
연쇄 효과 전략 팩토리

전략 패턴의 의존성 주입을 담당하며, 
cascade 타입에 따라 적절한 전략을 제공합니다.
"""

from typing import Dict, Type
from src.cascade.domain.models import CascadeType
from src.cascade.domain.strategies.cascade_strategy import (
    ICascadeStrategy,
    DefaultCascadeStrategy,
    EconomicCascadeStrategy,
    SocialCascadeStrategy,
    CulturalCascadeStrategy,
    TechnologicalCascadeStrategy,
    EnvironmentalCascadeStrategy,
)
from src.cascade.domain.strategies.economic_cascade_strategy import EconomicCascadeStrategy as ExtendedEconomicStrategy
from src.cascade.domain.strategies.social_cascade_strategy import SocialCascadeStrategy as ExtendedSocialStrategy
from src.cascade.domain.strategies.cultural_cascade_strategy import CulturalCascadeStrategy as ExtendedCulturalStrategy
from src.cascade.domain.strategies.technological_cascade_strategy import TechnologicalCascadeStrategy as ExtendedTechnologicalStrategy
from src.cascade.domain.strategies.environmental_cascade_strategy import EnvironmentalCascadeStrategy as ExtendedEnvironmentalStrategy


class CascadeStrategyFactory:
    """연쇄 효과 전략 팩토리
    
    헥사고널 아키텍처의 의존성 역전 원칙에 따라
    cascade 타입별로 적절한 전략 구현체를 제공합니다.
    """
    
    def __init__(self):
        """팩토리 초기화 - 전략 타입 매핑"""
        self._strategies: Dict[str, ICascadeStrategy] = {
            # 기본 전략
            "DEFAULT": DefaultCascadeStrategy(),
            "IMMEDIATE": DefaultCascadeStrategy(),
            
            # 확장된 전략들 (각 도메인별 구현체 사용)
            "ECONOMIC": ExtendedEconomicStrategy(),
            "SOCIAL": ExtendedSocialStrategy(),
            "CULTURAL": ExtendedCulturalStrategy(),
            "TECHNOLOGICAL": ExtendedTechnologicalStrategy(),
            "ENVIRONMENTAL": ExtendedEnvironmentalStrategy(),
            
            # cascade_strategy.py의 기본 구현들도 지원
            "DELAYED": DefaultCascadeStrategy(),
            "CONDITIONAL": DefaultCascadeStrategy(),
            "PROBABILISTIC": DefaultCascadeStrategy(),
        }
        
        # 타입별 전략 매핑 (CascadeType enum 지원)
        self._type_mappings: Dict[CascadeType, str] = {
            CascadeType.IMMEDIATE: "DEFAULT",
            CascadeType.DELAYED: "DEFAULT", 
            CascadeType.CONDITIONAL: "DEFAULT",
            CascadeType.PROBABILISTIC: "DEFAULT",
        }
        
    def get_strategy(self, cascade_type: CascadeType | str | None = None) -> ICascadeStrategy:
        """cascade 타입에 맞는 전략 반환
        
        Args:
            cascade_type: 연쇄 효과 타입 (CascadeType enum 또는 문자열)
            
        Returns:
            해당 타입에 맞는 전략 구현체
        """
        if cascade_type is None:
            return self._strategies["DEFAULT"]
            
        # CascadeType enum인 경우 문자열로 변환
        if isinstance(cascade_type, CascadeType):
            strategy_key = self._type_mappings.get(cascade_type, "DEFAULT")
            return self._strategies[strategy_key]
            
        # 문자열인 경우 직접 매핑
        if isinstance(cascade_type, str):
            strategy_key = cascade_type.upper()
            return self._strategies.get(strategy_key, self._strategies["DEFAULT"])
            
        # 알 수 없는 타입인 경우 기본 전략
        return self._strategies["DEFAULT"]
        
    def get_strategy_by_event_category(self, event_category: str) -> ICascadeStrategy:
        """이벤트 카테고리에 따른 전략 선택
        
        이벤트의 성격에 따라 적절한 도메인 전략을 선택합니다.
        
        Args:
            event_category: 이벤트 카테고리 (예: "economy", "social", "cultural")
            
        Returns:
            해당 카테고리에 맞는 전략
        """
        category_mappings = {
            "economy": "ECONOMIC",
            "economic": "ECONOMIC", 
            "finance": "ECONOMIC",
            "money": "ECONOMIC",
            
            "social": "SOCIAL",
            "society": "SOCIAL",
            "community": "SOCIAL",
            "people": "SOCIAL",
            
            "culture": "CULTURAL",
            "cultural": "CULTURAL",
            "tradition": "CULTURAL",
            
            "tech": "TECHNOLOGICAL",
            "technology": "TECHNOLOGICAL",
            "technological": "TECHNOLOGICAL",
            "innovation": "TECHNOLOGICAL",
            
            "environment": "ENVIRONMENTAL",
            "environmental": "ENVIRONMENTAL",
            "eco": "ENVIRONMENTAL",
            "nature": "ENVIRONMENTAL",
        }
        
        strategy_key = category_mappings.get(event_category.lower(), "DEFAULT")
        return self._strategies[strategy_key]
        
    def register_strategy(self, key: str, strategy: ICascadeStrategy) -> None:
        """새로운 전략 등록 (확장성)
        
        Args:
            key: 전략 식별 키
            strategy: 전략 구현체
        """
        self._strategies[key.upper()] = strategy
        
    def list_available_strategies(self) -> list[str]:
        """사용 가능한 전략 목록 반환"""
        return list(self._strategies.keys())


# 싱글톤 팩토리 인스턴스 (의존성 주입 지원)
_cascade_strategy_factory = CascadeStrategyFactory()


def get_cascade_strategy_factory() -> CascadeStrategyFactory:
    """전역 cascade 전략 팩토리 인스턴스 반환
    
    의존성 주입이나 서비스 컨테이너에서 사용할 수 있습니다.
    """
    return _cascade_strategy_factory 
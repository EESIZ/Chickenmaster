"""
스토리텔러 전략 팩토리

스토리텔러 서비스의 전략 패턴 의존성 주입을 담당합니다.
상태 평가, 추세 분석, 패턴 선택 전략을 제공합니다.
"""

from typing import Dict, Protocol
from src.storyteller.domain.strategies import (
    IStateEvaluator,
    ITrendAnalyzer, 
    IPatternSelector,
    DefaultStateEvaluator,
    LinearTrendAnalyzer,
    WeightedPatternSelector,
)


class StorytellerStrategyFactory:
    """스토리텔러 전략 팩토리
    
    헥사고널 아키텍처의 의존성 역전 원칙에 따라
    스토리텔러의 다양한 전략 구현체를 제공합니다.
    """
    
    def __init__(self):
        """팩토리 초기화 - 기본 전략들 등록"""
        
        # 상태 평가 전략들
        self._state_evaluators: Dict[str, IStateEvaluator] = {
            "default": DefaultStateEvaluator(),
            "basic": DefaultStateEvaluator(),
            "standard": DefaultStateEvaluator(),
        }
        
        # 추세 분석 전략들
        self._trend_analyzers: Dict[str, ITrendAnalyzer] = {
            "linear": LinearTrendAnalyzer(),
            "default": LinearTrendAnalyzer(),
            "basic": LinearTrendAnalyzer(),
        }
        
        # 패턴 선택 전략들
        self._pattern_selectors: Dict[str, IPatternSelector] = {
            "weighted": WeightedPatternSelector(),
            "default": WeightedPatternSelector(),
            "smart": WeightedPatternSelector(),
        }
        
    def get_state_evaluator(self, strategy_name: str = "default") -> IStateEvaluator:
        """상태 평가 전략 반환
        
        Args:
            strategy_name: 전략 이름 (default, basic, standard)
            
        Returns:
            상태 평가 전략 구현체
        """
        return self._state_evaluators.get(
            strategy_name.lower(), 
            self._state_evaluators["default"]
        )
        
    def get_trend_analyzer(self, strategy_name: str = "linear") -> ITrendAnalyzer:
        """추세 분석 전략 반환
        
        Args:
            strategy_name: 전략 이름 (linear, default, basic)
            
        Returns:
            추세 분석 전략 구현체
        """
        return self._trend_analyzers.get(
            strategy_name.lower(),
            self._trend_analyzers["default"]
        )
        
    def get_pattern_selector(self, strategy_name: str = "weighted") -> IPatternSelector:
        """패턴 선택 전략 반환
        
        Args:
            strategy_name: 전략 이름 (weighted, default, smart)
            
        Returns:
            패턴 선택 전략 구현체
        """
        return self._pattern_selectors.get(
            strategy_name.lower(),
            self._pattern_selectors["default"]
        )
        
    def register_state_evaluator(self, name: str, evaluator: IStateEvaluator) -> None:
        """새로운 상태 평가 전략 등록 (확장성)"""
        self._state_evaluators[name.lower()] = evaluator
        
    def register_trend_analyzer(self, name: str, analyzer: ITrendAnalyzer) -> None:
        """새로운 추세 분석 전략 등록 (확장성)"""
        self._trend_analyzers[name.lower()] = analyzer
        
    def register_pattern_selector(self, name: str, selector: IPatternSelector) -> None:
        """새로운 패턴 선택 전략 등록 (확장성)"""
        self._pattern_selectors[name.lower()] = selector
        
    def list_available_strategies(self) -> Dict[str, list[str]]:
        """사용 가능한 모든 전략 목록 반환"""
        return {
            "state_evaluators": list(self._state_evaluators.keys()),
            "trend_analyzers": list(self._trend_analyzers.keys()),
            "pattern_selectors": list(self._pattern_selectors.keys()),
        }


# 싱글톤 팩토리 인스턴스 (의존성 주입 지원)
_storyteller_strategy_factory = StorytellerStrategyFactory()


def get_storyteller_strategy_factory() -> StorytellerStrategyFactory:
    """전역 storyteller 전략 팩토리 인스턴스 반환
    
    의존성 주입이나 서비스 컨테이너에서 사용할 수 있습니다.
    """
    return _storyteller_strategy_factory


class StorytellerStrategyBundle:
    """스토리텔러 전략 번들
    
    관련된 전략들을 하나의 번들로 관리하여
    일관성 있는 스토리텔링 경험을 제공합니다.
    """
    
    def __init__(
        self, 
        state_evaluator: IStateEvaluator,
        trend_analyzer: ITrendAnalyzer,
        pattern_selector: IPatternSelector,
        bundle_name: str = "custom"
    ):
        self.state_evaluator = state_evaluator
        self.trend_analyzer = trend_analyzer
        self.pattern_selector = pattern_selector
        self.bundle_name = bundle_name
        
    @classmethod
    def create_default_bundle(cls) -> "StorytellerStrategyBundle":
        """기본 전략 번들 생성"""
        factory = get_storyteller_strategy_factory()
        return cls(
            state_evaluator=factory.get_state_evaluator("default"),
            trend_analyzer=factory.get_trend_analyzer("linear"),
            pattern_selector=factory.get_pattern_selector("weighted"),
            bundle_name="default"
        )
        
    @classmethod  
    def create_advanced_bundle(cls) -> "StorytellerStrategyBundle":
        """고급 전략 번들 생성 (향후 확장용)"""
        factory = get_storyteller_strategy_factory()
        return cls(
            state_evaluator=factory.get_state_evaluator("default"),
            trend_analyzer=factory.get_trend_analyzer("linear"),
            pattern_selector=factory.get_pattern_selector("smart"),
            bundle_name="advanced"
        ) 
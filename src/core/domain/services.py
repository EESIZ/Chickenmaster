"""
코어 도메인 서비스
게임 상태와 지표를 관리하는 서비스 클래스들을 제공합니다.
"""
from typing import Dict, List, Optional
from datetime import datetime

from .models import GameState, GameMetrics, MetricValue, EventEffect

class GameStateService:
    """게임 상태 관리 서비스"""

    @staticmethod
    def apply_effects(state: GameState, effects: Dict[str, float]) -> GameState:
        """효과를 게임 상태에 적용"""
        return state.apply_effects(effects)

    @staticmethod
    def validate_state(state: GameState) -> bool:
        """게임 상태가 유효한지 검증"""
        if state.money < 0:
            return False
        if not (0 <= state.reputation <= 100):
            return False
        if not (0 <= state.happiness <= 100):
            return False
        if not (0 <= state.pain <= 100):
            return False
        if state.day < 1:
            return False
        return True

    @staticmethod
    def calculate_metrics(state: GameState) -> Dict[str, float]:
        """게임 상태로부터 파생 지표 계산"""
        return {
            'business_health': (state.money / 10000000) * 0.4 + (state.reputation / 100) * 0.6,
            'employee_satisfaction': (state.happiness / 100) * 0.7 - (state.pain / 100) * 0.3,
            'survival_chance': 1.0 - (state.pain / 100) * 0.5 - (max(0, -state.money) / 1000000) * 0.5
        }

class MetricsService:
    """게임 지표 관리 서비스"""

    @staticmethod
    def update_metrics(metrics: GameMetrics, effects: Dict[str, float]) -> GameMetrics:
        """효과를 게임 지표에 적용"""
        return metrics.apply_effects(effects)

    @staticmethod
    def validate_metrics(metrics: GameMetrics) -> bool:
        """게임 지표가 유효한지 검증"""
        if not (0 <= metrics.inventory <= 999):
            return False
        if not (0 <= metrics.staff_fatigue <= 100):
            return False
        if not (0 <= metrics.facility <= 100):
            return False
        if not (0 <= metrics.demand <= 100):
            return False
        return True

    @staticmethod
    def calculate_derived_metrics(metrics: GameMetrics) -> Dict[str, float]:
        """게임 지표로부터 파생 지표 계산"""
        return {
            'operational_efficiency': (100 - metrics.staff_fatigue) * 0.4 + metrics.facility * 0.6,
            'market_potential': metrics.demand * 0.8 + (min(metrics.inventory, 100) / 100) * 0.2,
            'risk_factor': (metrics.staff_fatigue / 100) * 0.3 + (max(0, metrics.inventory - 500) / 500) * 0.7
        }

class EffectService:
    """이벤트 효과 관리 서비스"""

    @staticmethod
    def apply_effect(effect: EventEffect, state: GameState) -> Optional[Dict[str, float]]:
        """이벤트 효과를 평가하고 적용 가능한 효과 반환"""
        if not effect.is_applicable(state):
            return None

        if effect.effect_type == 'IMMEDIATE':
            return {effect.metric: effect.value}

        elif effect.effect_type == 'DELAYED':
            if effect.delay_days and effect.delay_days <= 0:
                return {effect.metric: effect.value}
            return None

        elif effect.effect_type == 'CONDITIONAL':
            if effect.condition and EffectService._evaluate_condition(effect.condition, state):
                return {effect.metric: effect.value}
            return None

        return None

    @staticmethod
    def _evaluate_condition(condition: Dict[str, any], state: GameState) -> bool:
        """조건을 평가"""
        metric = condition.get('metric')
        operator = condition.get('operator')
        value = condition.get('value')

        if not all([metric, operator, value]):
            return False

        current_value = getattr(state, metric, None)
        if current_value is None:
            return False

        if operator == 'eq':
            return current_value == value
        elif operator == 'gt':
            return current_value > value
        elif operator == 'lt':
            return current_value < value
        elif operator == 'gte':
            return current_value >= value
        elif operator == 'lte':
            return current_value <= value
        
        return False 
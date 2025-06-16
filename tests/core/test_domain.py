"""
코어 도메인 테스트
게임의 핵심 도메인 객체와 서비스를 테스트합니다.
"""
import pytest
from datetime import datetime
from src.core.domain.game_state import GameState
from src.core.domain.game_settings import GameSettings
from src.core.domain.metrics import MetricEnum
from src.core.domain.models import GameMetrics, MetricValue, EventEffect
from src.core.domain.services import GameStateService, MetricsService, EffectService
from src.core.domain.exceptions import (
    InvalidStateException,
    InvalidMetricException,
    InvalidEffectException,
    GameOverException
)

class TestGameState:
    """GameState 클래스 테스트"""

    def test_create_game_state(self):
        """GameState 생성 테스트"""
        state = GameState(
            current_day=1,
            money=1000000,
            reputation=50,
            happiness=70,
            suffering=30,
            inventory=50,
            staff_fatigue=30,
            facility=80,
            demand=50
        )
        assert state.money == 1000000
        assert state.reputation == 50
        assert state.happiness == 70
        assert state.suffering == 30
        assert state.current_day == 1
        assert isinstance(state.events_history, tuple)
        assert len(state.events_history) == 0

    def test_apply_effects(self):
        """효과 적용 테스트"""
        state = GameState(
            current_day=1,
            money=1000000,
            reputation=50,
            happiness=70,
            suffering=30,
            inventory=50,
            staff_fatigue=30,
            facility=80,
            demand=50
        )
        effects = {
            MetricEnum.MONEY: 500000,
            MetricEnum.REPUTATION: 10,
            MetricEnum.HAPPINESS: -20,
            MetricEnum.SUFFERING: 15
        }
        new_state = state.apply_effects(effects)
        
        assert new_state.money == 1500000
        assert new_state.reputation == 60
        assert new_state.happiness == 50
        assert new_state.suffering == 45
        assert new_state.current_day == state.current_day
        assert new_state.events_history == state.events_history

    def test_add_event(self):
        """이벤트 추가 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        new_state = state.add_event("EVENT_001")
        
        assert len(new_state.events_history) == 1
        assert new_state.events_history[0] == "EVENT_001"
        assert new_state.money == state.money
        assert new_state.reputation == state.reputation
        assert new_state.happiness == state.happiness
        assert new_state.pain == state.pain
        assert new_state.day == state.day

    def test_next_day(self):
        """다음 날 진행 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        new_state = state.next_day()
        
        assert new_state.day == 2
        assert new_state.money == state.money
        assert new_state.reputation == state.reputation
        assert new_state.happiness == state.happiness
        assert new_state.pain == state.pain
        assert new_state.events_history == state.events_history

class TestGameSettings:
    """GameSettings 클래스 테스트"""

    def test_create_initial_state(self):
        """초기 상태 생성 테스트"""
        settings = GameSettings(
            starting_money=5000000,
            starting_reputation=40,
            starting_happiness=80,
            starting_pain=20,
            max_cascade_depth=3,
            bankruptcy_threshold=-1000000
        )
        initial_state = settings.create_initial_state()
        
        assert initial_state.money == settings.starting_money
        assert initial_state.reputation == settings.starting_reputation
        assert initial_state.happiness == settings.starting_happiness
        assert initial_state.pain == settings.starting_pain
        assert initial_state.day == 1
        assert len(initial_state.events_history) == 0

class TestGameMetrics:
    """GameMetrics 클래스 테스트"""

    def test_create_game_metrics(self):
        """GameMetrics 생성 테스트"""
        metrics = GameMetrics(
            inventory=100,
            staff_fatigue=30,
            facility=80,
            demand=60
        )
        assert metrics.inventory == 100
        assert metrics.staff_fatigue == 30
        assert metrics.facility == 80
        assert metrics.demand == 60
        assert isinstance(metrics.last_updated, datetime)

    def test_apply_effects(self):
        """효과 적용 테스트"""
        metrics = GameMetrics(inventory=100, staff_fatigue=30, facility=80, demand=60)
        effects = {
            'inventory': 50,
            'staff_fatigue': 20,
            'facility': -10,
            'demand': 15
        }
        new_metrics = metrics.apply_effects(effects)
        
        assert new_metrics.inventory == 150
        assert new_metrics.staff_fatigue == 50
        assert new_metrics.facility == 70
        assert new_metrics.demand == 75

class TestGameStateService:
    """GameStateService 클래스 테스트"""

    def test_validate_state_valid(self):
        """유효한 상태 검증 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        assert GameStateService.validate_state(state) is True

    def test_validate_state_invalid(self):
        """잘못된 상태 검증 테스트"""
        invalid_states = [
            GameState(money=-1, reputation=50, happiness=70, pain=30, day=1),
            GameState(money=1000000, reputation=101, happiness=70, pain=30, day=1),
            GameState(money=1000000, reputation=50, happiness=101, pain=30, day=1),
            GameState(money=1000000, reputation=50, happiness=70, pain=101, day=1),
            GameState(money=1000000, reputation=50, happiness=70, pain=30, day=0)
        ]
        for state in invalid_states:
            assert GameStateService.validate_state(state) is False

    def test_calculate_metrics(self):
        """파생 지표 계산 테스트"""
        state = GameState(money=5000000, reputation=80, happiness=90, pain=20, day=1)
        metrics = GameStateService.calculate_metrics(state)
        
        assert 'business_health' in metrics
        assert 'employee_satisfaction' in metrics
        assert 'survival_chance' in metrics
        assert 0 <= metrics['business_health'] <= 1
        assert 0 <= metrics['employee_satisfaction'] <= 1
        assert 0 <= metrics['survival_chance'] <= 1

class TestMetricsService:
    """MetricsService 클래스 테스트"""

    def test_validate_metrics_valid(self):
        """유효한 지표 검증 테스트"""
        metrics = GameMetrics(inventory=100, staff_fatigue=30, facility=80, demand=60)
        assert MetricsService.validate_metrics(metrics) is True

    def test_validate_metrics_invalid(self):
        """잘못된 지표 검증 테스트"""
        invalid_metrics = [
            GameMetrics(inventory=1000, staff_fatigue=30, facility=80, demand=60),
            GameMetrics(inventory=100, staff_fatigue=101, facility=80, demand=60),
            GameMetrics(inventory=100, staff_fatigue=30, facility=101, demand=60),
            GameMetrics(inventory=100, staff_fatigue=30, facility=80, demand=101)
        ]
        for metrics in invalid_metrics:
            assert MetricsService.validate_metrics(metrics) is False

    def test_calculate_derived_metrics(self):
        """파생 지표 계산 테스트"""
        metrics = GameMetrics(inventory=100, staff_fatigue=30, facility=80, demand=60)
        derived = MetricsService.calculate_derived_metrics(metrics)
        
        assert 'operational_efficiency' in derived
        assert 'market_potential' in derived
        assert 'risk_factor' in derived
        assert 0 <= derived['operational_efficiency'] <= 100
        assert 0 <= derived['market_potential'] <= 100
        assert 0 <= derived['risk_factor'] <= 1

class TestEffectService:
    """EffectService 클래스 테스트"""

    def test_apply_immediate_effect(self):
        """즉시 효과 적용 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        effect = EventEffect(metric='money', value=500000, effect_type='IMMEDIATE')
        result = EffectService.apply_effect(effect, state)
        
        assert result is not None
        assert result['money'] == 500000

    def test_apply_delayed_effect(self):
        """지연 효과 적용 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        effect = EventEffect(
            metric='money',
            value=500000,
            effect_type='DELAYED',
            delay_days=2
        )
        result = EffectService.apply_effect(effect, state)
        assert result is None

        effect = EventEffect(
            metric='money',
            value=500000,
            effect_type='DELAYED',
            delay_days=0
        )
        result = EffectService.apply_effect(effect, state)
        assert result is not None
        assert result['money'] == 500000

    def test_apply_conditional_effect(self):
        """조건부 효과 적용 테스트"""
        state = GameState(money=1000000, reputation=50, happiness=70, pain=30, day=1)
        effect = EventEffect(
            metric='money',
            value=500000,
            effect_type='CONDITIONAL',
            condition={'metric': 'reputation', 'operator': 'gte', 'value': 50}
        )
        result = EffectService.apply_effect(effect, state)
        assert result is not None
        assert result['money'] == 500000

        effect = EventEffect(
            metric='money',
            value=500000,
            effect_type='CONDITIONAL',
            condition={'metric': 'reputation', 'operator': 'gt', 'value': 50}
        )
        result = EffectService.apply_effect(effect, state)
        assert result is None 
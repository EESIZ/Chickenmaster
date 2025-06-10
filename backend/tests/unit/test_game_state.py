import dataclasses
import pytest
from datetime import datetime

from app.core.domain.game_state import GameState
from app.core.game_constants import Metric


@pytest.fixture
def initial_game_state():
    return GameState(
        money=10000.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=50.0,
        demand=50.0,
        current_day=1,
    )


def test_game_state_creation(initial_game_state):
    """GameState 생성 테스트"""
    assert initial_game_state.money == 10000.0
    assert initial_game_state.reputation == 50.0
    assert initial_game_state.happiness == 50.0
    assert initial_game_state.suffering == 50.0
    assert initial_game_state.inventory == 50.0
    assert initial_game_state.staff_fatigue == 50.0
    assert initial_game_state.facility == 50.0
    assert initial_game_state.demand == 50.0
    assert initial_game_state.current_day == 1
    assert initial_game_state.events_history == ()
    assert isinstance(initial_game_state.last_updated, datetime)


def test_metrics_property(initial_game_state):
    """metrics 프로퍼티 테스트"""
    metrics = initial_game_state.metrics
    assert metrics[Metric.MONEY] == 10000.0
    assert metrics[Metric.REPUTATION] == 50.0
    assert metrics[Metric.HAPPINESS] == 50.0
    assert metrics[Metric.SUFFERING] == 50.0
    assert metrics[Metric.INVENTORY] == 50.0
    assert metrics[Metric.STAFF_FATIGUE] == 50.0
    assert metrics[Metric.FACILITY] == 50.0
    assert metrics[Metric.DEMAND] == 50.0


def test_game_progression(initial_game_state):
    """게임 진행률 테스트"""
    assert initial_game_state.game_progression == 1 / 730  # 1일차 / 총 730일


def test_game_stages(initial_game_state):
    """게임 단계 테스트"""
    # 초기 단계
    assert initial_game_state.is_early_game
    assert not initial_game_state.is_mid_game
    assert not initial_game_state.is_late_game

    # 중반 단계
    mid_game_state = GameState(
        money=10000.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=50.0,
        demand=50.0,
        current_day=300,
    )
    assert not mid_game_state.is_early_game
    assert mid_game_state.is_mid_game
    assert not mid_game_state.is_late_game

    # 후반 단계
    late_game_state = GameState(
        money=10000.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=50.0,
        demand=50.0,
        current_day=600,
    )
    assert not late_game_state.is_early_game
    assert not late_game_state.is_mid_game
    assert late_game_state.is_late_game


def test_apply_effects(initial_game_state):
    """효과 적용 테스트"""
    effects = {
        Metric.MONEY: 1000.0,
        Metric.REPUTATION: -10.0,
        Metric.HAPPINESS: 5.0,
    }

    new_state = initial_game_state.apply_effects(effects)

    assert new_state.money == 11000.0
    assert new_state.reputation == 40.0
    assert new_state.happiness == 55.0
    assert new_state.suffering == 50.0  # 변경되지 않은 메트릭
    assert new_state.inventory == 50.0  # 변경되지 않은 메트릭
    assert new_state.staff_fatigue == 50.0  # 변경되지 않은 메트릭
    assert new_state.facility == 50.0  # 변경되지 않은 메트릭
    assert new_state.demand == 50.0  # 변경되지 않은 메트릭


def test_add_event_to_history(initial_game_state):
    """이벤트 히스토리 추가 테스트"""
    new_state = initial_game_state.add_event_to_history("test_event")

    assert new_state.events_history == ("test_event",)
    assert new_state.money == initial_game_state.money  # 다른 속성은 변경되지 않음


def test_get_metric_value(initial_game_state):
    """메트릭 값 조회 테스트"""
    assert initial_game_state.get_metric_value(Metric.MONEY) == 10000.0
    assert initial_game_state.get_metric_value(Metric.REPUTATION) == 50.0


def test_is_metric_in_warning_zone(initial_game_state):
    """메트릭 경고 구간 테스트"""
    # 돈이 1000 미만인 경우
    low_money_state = GameState(
        money=500.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=50.0,
        demand=50.0,
        current_day=1,
    )
    assert low_money_state.is_metric_in_warning_zone(Metric.MONEY)

    # 평판이 20 미만인 경우
    low_reputation_state = GameState(
        money=10000.0,
        reputation=10.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=50.0,
        demand=50.0,
        current_day=1,
    )
    assert low_reputation_state.is_metric_in_warning_zone(Metric.REPUTATION)

    # 직원 피로도가 80 초과인 경우
    high_fatigue_state = GameState(
        money=10000.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=90.0,
        facility=50.0,
        demand=50.0,
        current_day=1,
    )
    assert high_fatigue_state.is_metric_in_warning_zone(Metric.STAFF_FATIGUE)

    # 시설 상태가 30 미만인 경우
    low_facility_state = GameState(
        money=10000.0,
        reputation=50.0,
        happiness=50.0,
        suffering=50.0,
        inventory=50.0,
        staff_fatigue=50.0,
        facility=20.0,
        demand=50.0,
        current_day=1,
    )
    assert low_facility_state.is_metric_in_warning_zone(Metric.FACILITY)


def test_immutability(initial_game_state):
    """불변성 테스트"""
    with pytest.raises(dataclasses.FrozenInstanceError):
        initial_game_state.money = 20000.0

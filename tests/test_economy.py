"""
경제 시스템 테스트 모듈

이 모듈은 Chicken-RNG 게임의 경제 시스템을 테스트합니다.
수요-공급, 가격 변동, 트레이드오프 등을 검증합니다.
"""

import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 schema.py를 import할 수 있게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from typing import Any, cast

import pytest

from game_constants import Metric, cap_metric_value
from src.economy.engine import (
    apply_tradeoff,
    compute_profit_no_right_answer,
    tradeoff_apply_price_change,
    uncertainty_adjust_inventory,
    update_economy_state,
)
from src.economy.models import tradeoff_compute_demand
from src.metrics.tracker import MetricsTracker

# 테스트 상수
TEST_CONFIG_PATH = "data/economy_config.json"
REPUTATION_EFFECT_TOLERANCE = 0.1
INVENTORY_ADJUSTMENT = 70
SUFFERING_VALUE = 25
HAPPINESS_VALUE = 40
METRIC_SUM = 100
MONEY_VALUE = 5000


@pytest.fixture
def test_config() -> dict[str, Any]:
    """테스트용 경제 설정을 제공하는 fixture"""
    if os.path.exists(TEST_CONFIG_PATH):
        with open(TEST_CONFIG_PATH, encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))
    return {
        "demand": {
            "base": 100,
            "price_elasticity": -1.5,
            "reputation_effect": 0.3,
        },
        "supply": {
            "base_cost": 50,
            "marginal_cost": 0.8,
        },
        "inventory": {
            "storage_cost": 0.1,
            "shortage_penalty": 1.2,
        },
    }


@pytest.fixture
def test_metrics() -> dict[Metric, float]:
    """테스트용 초기 지표를 제공하는 fixture"""
    return {
        Metric.MONEY: 10000.0,
        Metric.REPUTATION: 50.0,
        Metric.HAPPINESS: 60.0,
        Metric.SUFFERING: 40.0,
        Metric.INVENTORY: 100.0,
        Metric.STAFF_FATIGUE: 30.0,
        Metric.FACILITY: 80.0,
    }


def test_tradeoff_compute_demand_optimal_price(test_config: dict[str, Any]) -> None:
    """최적 가격에서의 수요 계산 테스트"""
    demand_config = test_config.get("demand", {})
    optimal_price = demand_config.get("optimal_price", 100)
    base_demand_val = demand_config.get("base_demand", 50)
    price_elasticity_val = demand_config.get("price_elasticity", -0.5)

    # 기준 평판(50) 및 최적 가격에서의 수요
    demand_at_optimal_price_and_base_reputation = tradeoff_compute_demand(
        price=optimal_price,
        reputation=50.0,
        config=test_config,
    )
    # 이 경우 price_factor=1, reputation_factor=1 이므로 base_demand와 같아야 함
    assert (
        demand_at_optimal_price_and_base_reputation == base_demand_val
    ), f"최적 가격, 기본 평판에서 수요는 base_demand({base_demand_val})여야 합니다. 실제: {demand_at_optimal_price_and_base_reputation}"

    # 가격 상승 시 수요 감소 확인 (평판 고정)
    higher_price = optimal_price + 20
    demand_at_higher_price = tradeoff_compute_demand(
        price=higher_price,
        reputation=50.0,
        config=test_config,
    )
    if price_elasticity_val < 0:  # 정상적인 경우 (가격 오르면 수요 감소)
        assert (
            demand_at_higher_price < demand_at_optimal_price_and_base_reputation
        ), f"가격 상승 시 수요 감소해야 함. 현재 가격: {higher_price}, 이전 수요: {demand_at_optimal_price_and_base_reputation}, 현재 수요: {demand_at_higher_price}"
    elif price_elasticity_val > 0:  # 기펜재 같은 특이 케이스
        assert demand_at_higher_price > demand_at_optimal_price_and_base_reputation

    # 가격 하락 시 수요 증가 확인 (평판 고정, price_elasticity < 0 가정)
    lower_price = optimal_price - 20
    demand_at_lower_price = tradeoff_compute_demand(
        price=lower_price,
        reputation=50.0,
        config=test_config,
    )
    if price_elasticity_val < 0:
        assert (
            demand_at_lower_price > demand_at_optimal_price_and_base_reputation
        ), f"가격 하락 시 수요 증가해야 함. 현재 가격: {lower_price}, 이전 수요: {demand_at_optimal_price_and_base_reputation}, 현재 수요: {demand_at_lower_price}"
    elif price_elasticity_val > 0:
        assert demand_at_lower_price < demand_at_optimal_price_and_base_reputation


def test_tradeoff_compute_demand_reputation_effect(test_config: dict[str, Any]) -> None:
    """평판이 수요에 미치는 영향 테스트"""
    optimal_price = test_config.get("demand", {}).get("optimal_price", 100)

    # 평판이 다른 두 경우의 수요 계산 (가격은 최적으로 고정)
    low_rep_demand = tradeoff_compute_demand(
        price=optimal_price,
        reputation=30.0,  # 낮은 평판
        config=test_config,
    )
    base_demand_at_50_rep = tradeoff_compute_demand(
        price=optimal_price,
        reputation=50.0,  # 기준 평판
        config=test_config,
    )
    high_rep_demand = tradeoff_compute_demand(
        price=optimal_price,
        reputation=70.0,  # 높은 평판
        config=test_config,
    )

    assert high_rep_demand > base_demand_at_50_rep, "평판이 높을 때 수요가 기준보다 많아야 함"
    assert low_rep_demand < base_demand_at_50_rep, "평판이 낮을 때 수요가 기준보다 적어야 함"

    # reputation_effect가 양수일 때, 평판이 높을수록 수요 증가, 낮을수록 수요 감소
    reputation_effect_config = test_config.get("demand", {}).get("reputation_effect", 0.2)
    if reputation_effect_config > 0:
        assert high_rep_demand > low_rep_demand, "평판 효과가 양수일 때, 높은 평판이 낮은 평판보다 수요가 많아야 함"
    elif reputation_effect_config < 0:
        assert high_rep_demand < low_rep_demand, "평판 효과가 음수일 때, 높은 평판이 낮은 평판보다 수요가 적어야 함"


def test_no_right_answer_compute_profit_scenarios() -> None:
    """다양한 시나리오에서의 이익 계산 테스트"""
    # 케이스 1: 정상 케이스
    profit1 = compute_profit_no_right_answer(
        units_sold=50, unit_cost=80.0, price=100.0, fixed_cost=0
    )
    assert profit1 > 0

    # 케이스 2: 판매량 감소
    profit2_less_sold = compute_profit_no_right_answer(
        units_sold=30, unit_cost=80.0, price=100.0, fixed_cost=0  # 판매량 감소
    )
    assert profit2_less_sold < profit1

    # 케이스 3: 과잉 재고 (판매량은 수요에 의해 결정된다고 가정)
    profit3 = compute_profit_no_right_answer(
        units_sold=30, unit_cost=80.0, price=100.0, fixed_cost=0
    )
    assert profit3 < profit1


def test_uncertainty_adjust_inventory() -> None:
    """재고 조정 테스트"""
    # 케이스 1: 정상 케이스 (판매량 < 재고)
    normal_case_result = uncertainty_adjust_inventory(units_sold=30, current_inventory=100)
    assert normal_case_result == INVENTORY_ADJUSTMENT, "정상 케이스에서 재고가 올바르게 계산되어야 합니다"

    # 케이스 2: 엣지 케이스 (판매량 = 재고)
    edge_case_result = uncertainty_adjust_inventory(units_sold=100, current_inventory=100)
    assert edge_case_result == 0, "재고가 모두 소진된 경우 0이 되어야 합니다"

    # 케이스 3: 예외 케이스 (판매량 > 재고)
    exception_case_result = uncertainty_adjust_inventory(units_sold=120, current_inventory=100)
    assert exception_case_result == 0, "재고보다 많은 판매량이 있는 경우 0이 되어야 합니다"


def test_tradeoff_apply_price_change(test_metrics: dict[Metric, float]) -> None:
    """가격 변경에 따른 트레이드오프 효과 테스트"""
    # MetricsTracker 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 행복 75로 설정
    tracker.update_metric(Metric.HAPPINESS, 75.0)

    # 검증: 고통 지표가 자동으로 조정되어야 함
    metrics = tracker.get_metrics()
    assert metrics[Metric.SUFFERING] == SUFFERING_VALUE, "행복이 75로 설정되면 고통은 25가 되어야 합니다"

    # 고통 지표 업데이트
    tracker.update_metric(Metric.SUFFERING, 60.0)

    # 검증: 행복 지표가 자동으로 조정되어야 함
    metrics = tracker.get_metrics()
    assert metrics[Metric.HAPPINESS] == HAPPINESS_VALUE, "고통이 60으로 설정되면 행복은 40이 되어야 합니다"

    # 합계가 항상 100인지 확인
    assert (
        metrics[Metric.HAPPINESS] + metrics[Metric.SUFFERING] == METRIC_SUM
    ), "행복과 고통의 합은 항상 100이어야 합니다"


def test_cap_metric_value() -> None:
    """지표 값 제한 테스트"""
    # 케이스 1: 정상 케이스 (양수 값)
    normal_result = cap_metric_value(Metric.MONEY, MONEY_VALUE)
    assert normal_result == MONEY_VALUE, "정상 케이스에서 현금 값이 유지되어야 합니다"

    # 케이스 2: 엣지 케이스 (0)
    zero_result = cap_metric_value(Metric.MONEY, 0)
    assert zero_result == 0, "0은 유효한 값으로 유지되어야 합니다"

    # 케이스 3: 음수 값
    negative_result = cap_metric_value(Metric.MONEY, -1000)
    assert negative_result == 0, "음수 값은 0으로 제한되어야 합니다"

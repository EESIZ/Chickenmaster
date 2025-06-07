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
    compute_profit_no_right_answer,
    uncertainty_adjust_inventory,
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
            "cost_fluctuation": 0.2,
        },
        "tradeoffs": {
            "price_to_reputation": 0.3,
            "price_to_fatigue": 0.2,
        },
        "uncertainty": {
            "daily_random_factor": 0.1,
            "event_trigger_threshold": 0.7,
            "max_event_severity": 3,
        },
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
    higher_price = optimal_price + 200  # 더 큰 가격 차이로 변경
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
    lower_price = optimal_price - 200  # 더 큰 가격 차이로 변경
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


def test_uncertainty_adjust_inventory() -> None:
    """재고 조정 테스트"""
    # 판매량이 재고보다 적은 경우
    units_sold = 30
    current_inventory = 100
    new_inventory = uncertainty_adjust_inventory(units_sold, current_inventory)
    assert new_inventory == current_inventory - units_sold

    # 판매량이 재고보다 많은 경우 (재고 부족)
    units_sold = 120
    current_inventory = 100
    new_inventory = uncertainty_adjust_inventory(units_sold, current_inventory)
    assert new_inventory == 0  # 재고는 음수가 될 수 없음


def test_compute_profit_no_right_answer() -> None:
    """이익 계산 테스트"""
    units_sold = 100
    unit_cost = 50
    price = 100
    fixed_cost = 1000

    # 이익 = 수익 - 비용 = (판매량 * 가격) - (판매량 * 단위비용 + 고정비용)
    expected_profit = (units_sold * price) - (units_sold * unit_cost + fixed_cost)
    actual_profit = compute_profit_no_right_answer(
        units_sold, unit_cost, price, fixed_cost
    )

    assert actual_profit == expected_profit


def test_cap_metric_value() -> None:
    """지표 값 보정 테스트"""
    # 최소값 보정
    assert cap_metric_value(Metric.MONEY, -100) == 0
    assert cap_metric_value(Metric.REPUTATION, -10) == 0

    # 최대값 보정
    assert cap_metric_value(Metric.REPUTATION, 120) == 100
    assert cap_metric_value(Metric.HAPPINESS, 150) == 100

    # 범위 내 값은 그대로 유지
    assert cap_metric_value(Metric.MONEY, 5000) == 5000
    assert cap_metric_value(Metric.REPUTATION, 75) == 75


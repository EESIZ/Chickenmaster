"""
경제 시스템 테스트 모듈

이 모듈은 Chicken-RNG 게임의 경제 시스템을 테스트합니다.
수요-공급, 가격 변동, 트레이드오프 등을 검증합니다.
"""

import json
import os
import sys
from typing import Any, cast

import pytest

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 schema.py를 import할 수 있게 함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schema import Metric, cap_metric_value
from src.economy.engine import (
    no_right_answer_compute_profit,
    tradeoff_apply_price_change,
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
    # 기본 설정으로 수요 계산
    demand = tradeoff_compute_demand(
        price=100.0,
        reputation=50.0,
        config=test_config,
    )

    # 수요가 양수여야 함
    assert demand > 0

    # 가격 탄력성 검증
    high_price_demand = tradeoff_compute_demand(
        price=120.0,
        reputation=50.0,
        config=test_config,
    )
    assert high_price_demand < demand

def test_tradeoff_compute_demand_reputation_effect(test_config: dict[str, Any]) -> None:
    """평판이 수요에 미치는 영향 테스트"""
    # 평판이 다른 두 경우의 수요 계산
    low_rep_demand = tradeoff_compute_demand(
        price=100.0,
        reputation=30.0,
        config=test_config,
    )
    high_rep_demand = tradeoff_compute_demand(
        price=100.0,
        reputation=60.0,
        config=test_config,
    )

    # 평판이 높을 때 수요가 더 많아야 함
    assert high_rep_demand > low_rep_demand

    # 평판 효과의 크기가 설정값에 비례하는지 확인
    expected_ratio = 1 + test_config["demand"]["reputation_effect"] * (60.0 - 30.0) / 100.0
    actual_ratio = high_rep_demand / low_rep_demand if low_rep_demand > 0 else float("inf")

    assert abs(actual_ratio - expected_ratio) < REPUTATION_EFFECT_TOLERANCE, "평판 효과가 설정값에 비례해야 합니다"

def test_no_right_answer_compute_profit_scenarios() -> None:
    """다양한 시나리오에서의 이익 계산 테스트"""
    # 케이스 1: 정상 케이스
    profit1 = no_right_answer_compute_profit(
        price=100.0,
        cost=80.0,
        demand=50,
        inventory=60,
    )
    assert profit1 > 0

    # 케이스 2: 재고 부족
    profit2 = no_right_answer_compute_profit(
        price=100.0,
        cost=80.0,
        demand=70,
        inventory=50,
    )
    assert profit2 < profit1  # 재고 부족 패널티로 인해 이익이 감소해야 함

    # 케이스 3: 과잉 재고
    profit3 = no_right_answer_compute_profit(
        price=100.0,
        cost=80.0,
        demand=30,
        inventory=100,
    )
    assert profit3 < profit1  # 보관 비용으로 인해 이익이 감소해야 함

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

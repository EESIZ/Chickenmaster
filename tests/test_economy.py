"""
경제 엔진 테스트 모듈

이 모듈은 Chicken-RNG 게임의 경제 엔진 시스템에 대한 테스트를 포함합니다.
수요 계산, 이익 계산, 트레이드오프 적용, 음수 방지 등의 기능을 검증합니다.

핵심 철학:
- 정답 없음: 모든 경제적 결정은 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 경제 상황은 예측 불가능하게 변화할 수 있습니다
"""

import os
import sys
import json
import pytest
from typing import Dict, Any, cast

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 schema.py를 import할 수 있게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# schema.py에서 필요한 상수와 Enum 가져오기
from schema import Metric, cap_metric_value

# 테스트할 모듈 가져오기
from src.economy.models import (
    tradeoff_compute_demand,
)  # load_economy_config는 향후 사용 예정
from src.economy.engine import (
    noRightAnswer_compute_profit,
    uncertainty_adjust_inventory,
    tradeoff_apply_price_change,
    # apply_tradeoff는 향후 확장을 위해 준비됨
)
from src.metrics.tracker import MetricsTracker


# 테스트 설정 파일 경로
TEST_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../data/economy_config.json")


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """테스트용 경제 설정을 제공하는 fixture"""
    if os.path.exists(TEST_CONFIG_PATH):
        with open(TEST_CONFIG_PATH, "r", encoding="utf-8") as f:
            return cast(Dict[str, Any], json.load(f))
    return {
        "demand": {
            "base_demand": 50,
            "price_sensitivity": 0.5,
            "reputation_factor": 0.8,
            "min_price": 5000,
            "max_price": 20000,
            "optimal_price": 10000,
            "uncertainty_factor": 0.2,
        },
        "profit": {
            "base_unit_cost": 3000,
            "fixed_cost_daily": 15000,
            "cost_fluctuation_range": 0.2,
        },
        "tradeoffs": {
            "price_to_reputation_factor": 0.3,
            "price_to_fatigue_factor": 0.2,
        },
    }


@pytest.fixture
def test_metrics() -> Dict[Metric, float]:
    """테스트용 초기 지표를 제공하는 fixture"""
    return {
        Metric.MONEY: 10000,
        Metric.REPUTATION: 50,
        Metric.HAPPINESS: 50,
        Metric.SUFFERING: 50,
        Metric.INVENTORY: 100,
        Metric.STAFF_FATIGUE: 30,
        Metric.FACILITY: 80,
    }


def test_tradeoff_compute_demand_optimal_price(test_config: Dict[str, Any]) -> None:
    """
    최적 가격에서의 수요 계산 테스트

    최적 가격에서는 가격 효과가 최대가 되어 수요가 가장 높아야 합니다.
    """
    # 설정
    config = test_config["demand"]
    optimal_price = config["optimal_price"]
    reputation = 50  # 중간 평판

    # 실행
    demand = tradeoff_compute_demand(optimal_price, reputation, config)

    # 검증
    expected_base_demand = config["base_demand"]
    expected_reputation_effect = 1.0 + (reputation / 100.0 * config["reputation_factor"])
    expected_demand = round(expected_base_demand * 1.0 * expected_reputation_effect)

    assert demand == expected_demand, f"최적 가격({optimal_price})에서 수요가 예상값과 다릅니다"

    # 추가 검증: 최적 가격보다 높거나 낮은 가격에서는 수요가 감소해야 함
    higher_price_demand = tradeoff_compute_demand(optimal_price + 2000, reputation, config)
    lower_price_demand = tradeoff_compute_demand(optimal_price - 2000, reputation, config)

    assert demand > higher_price_demand, "최적 가격보다 높은 가격에서 수요가 감소해야 합니다"
    assert demand > lower_price_demand, "최적 가격보다 낮은 가격에서 수요가 감소해야 합니다"


def test_tradeoff_compute_demand_reputation_effect(test_config: Dict[str, Any]) -> None:
    """
    평판이 수요에 미치는 영향 테스트

    평판이 높을수록 수요가 증가해야 합니다.
    """
    # 설정
    config = test_config["demand"]
    price = config["optimal_price"]  # 최적 가격 사용
    low_reputation = 20
    high_reputation = 80

    # 실행
    low_rep_demand = tradeoff_compute_demand(price, low_reputation, config)
    high_rep_demand = tradeoff_compute_demand(price, high_reputation, config)

    # 검증
    assert high_rep_demand > low_rep_demand, "평판이 높을수록 수요가 증가해야 합니다"

    # 추가 검증: 평판 효과의 크기가 설정값에 비례해야 함
    reputation_factor = config["reputation_factor"]
    expected_ratio = (1.0 + (high_reputation / 100.0 * reputation_factor)) / (
        1.0 + (low_reputation / 100.0 * reputation_factor)
    )
    actual_ratio = high_rep_demand / low_rep_demand if low_rep_demand > 0 else float("inf")

    assert abs(actual_ratio - expected_ratio) < 0.1, "평판 효과가 설정값에 비례해야 합니다"


def test_noRightAnswer_compute_profit_scenarios() -> None:
    """
    다양한 시나리오에서의 이익 계산 테스트

    이 테스트는 '정답 없음' 원칙을 검증합니다:
    - 가격이 높으면 단위당 이익은 높지만 판매량이 적을 수 있음
    - 가격이 낮으면 판매량은 많지만 단위당 이익이 낮을 수 있음
    """
    # 시나리오 1: 높은 가격, 적은 판매량
    high_price_scenario = {
        "units_sold": 30,
        "unit_cost": 3000,
        "price": 15000,
        "fixed_cost": 15000,
    }

    # 시나리오 2: 낮은 가격, 많은 판매량
    low_price_scenario = {
        "units_sold": 70,
        "unit_cost": 3000,
        "price": 8000,
        "fixed_cost": 15000,
    }

    # 실행
    high_price_profit = noRightAnswer_compute_profit(**high_price_scenario)
    low_price_profit = noRightAnswer_compute_profit(**low_price_scenario)

    # 검증: 두 시나리오 모두 이익이 발생해야 함
    assert high_price_profit > 0, "높은 가격 시나리오에서 이익이 발생해야 합니다"
    assert low_price_profit > 0, "낮은 가격 시나리오에서 이익이 발생해야 합니다"

    # 추가 검증: 어느 시나리오가 더 이익이 높은지는 상황에 따라 다름 (정답 없음)
    print(f"높은 가격 시나리오 이익: {high_price_profit}")
    print(f"낮은 가격 시나리오 이익: {low_price_profit}")


def test_uncertainty_adjust_inventory_edge_cases() -> None:
    """
    재고 조정 엣지 케이스 테스트

    불확실성 ≠ 불합리한 음수: 재고가 음수가 되지 않도록 보정되어야 합니다.
    """
    # 케이스 1: 정상 케이스 (판매량 < 재고)
    normal_case_result = uncertainty_adjust_inventory(units_sold=30, current_inventory=100)
    assert normal_case_result == 70, "정상 케이스에서 재고가 올바르게 계산되어야 합니다"

    # 케이스 2: 엣지 케이스 (판매량 = 재고)
    edge_case_result = uncertainty_adjust_inventory(units_sold=100, current_inventory=100)
    assert edge_case_result == 0, "재고를 모두 판매한 경우 재고는 0이 되어야 합니다"

    # 케이스 3: 엣지 케이스 (판매량 > 재고) - 음수 방지 검증
    overflow_case_result = uncertainty_adjust_inventory(units_sold=150, current_inventory=100)
    assert (
        overflow_case_result == 0
    ), "판매량이 재고보다 많은 경우에도 재고는 음수가 되지 않아야 합니다"


def test_tradeoff_apply_price_change(test_metrics: Dict[Metric, float]) -> None:
    """
    가격 변경에 따른 트레이드오프 효과 테스트

    가격을 내리면:
    - 평판(손님 수)이 증가하지만
    - 직원 피로도가 증가해야 합니다

    가격을 올리면:
    - 평판(손님 수)이 감소하지만
    - 직원 피로도가 감소해야 합니다
    """
    # 케이스 1: 가격 인하
    price_decrease = -2000
    result_decrease = tradeoff_apply_price_change(price_decrease, test_metrics)

    # 검증: 가격 인하 시 평판 증가, 직원 피로도 증가
    assert (
        result_decrease[Metric.REPUTATION] > test_metrics[Metric.REPUTATION]
    ), "가격 인하 시 평판이 증가해야 합니다"
    assert (
        result_decrease[Metric.STAFF_FATIGUE] > test_metrics[Metric.STAFF_FATIGUE]
    ), "가격 인하 시 직원 피로도가 증가해야 합니다"

    # 케이스 2: 가격 인상
    price_increase = 2000
    result_increase = tradeoff_apply_price_change(price_increase, test_metrics)

    # 검증: 가격 인상 시 평판 감소, 직원 피로도 감소
    assert (
        result_increase[Metric.REPUTATION] < test_metrics[Metric.REPUTATION]
    ), "가격 인상 시 평판이 감소해야 합니다"
    assert (
        result_increase[Metric.STAFF_FATIGUE] < test_metrics[Metric.STAFF_FATIGUE]
    ), "가격 인상 시 직원 피로도가 감소해야 합니다"


def test_metrics_tracker_happiness_suffering_balance() -> None:
    """
    행복-고통 시소 관계 테스트

    행복과 고통은 합이 항상 100으로 유지되는 트레이드오프 관계입니다.
    """
    # 초기 지표로 MetricsTracker 초기화
    tracker = MetricsTracker()

    # 행복 지표 업데이트
    tracker.update_metric(Metric.HAPPINESS, 75)

    # 검증: 고통 지표가 자동으로 조정되어야 함
    metrics = tracker.get_metrics()
    assert metrics[Metric.SUFFERING] == 25, "행복이 75로 설정되면 고통은 25가 되어야 합니다"

    # 고통 지표 업데이트
    tracker.update_metric(Metric.SUFFERING, 60)

    # 검증: 행복 지표가 자동으로 조정되어야 함
    metrics = tracker.get_metrics()
    assert metrics[Metric.HAPPINESS] == 40, "고통이 60으로 설정되면 행복은 40이 되어야 합니다"

    # 합계가 항상 100인지 확인
    assert (
        metrics[Metric.HAPPINESS] + metrics[Metric.SUFFERING] == 100
    ), "행복과 고통의 합은 항상 100이어야 합니다"


def test_cap_metric_value_money_edge_case() -> None:
    """
    현금 지표 음수 방지 엣지 케이스 테스트

    불확실성 ≠ 불합리한 음수: 현금이 음수가 되지 않도록 보정되어야 합니다.
    """
    # 케이스 1: 정상 케이스 (양수 값)
    normal_result = cap_metric_value(Metric.MONEY, 5000)
    assert normal_result == 5000, "정상 케이스에서 현금 값이 유지되어야 합니다"

    # 케이스 2: 엣지 케이스 (0)
    zero_result = cap_metric_value(Metric.MONEY, 0)
    assert zero_result == 0, "현금이 0인 경우 그대로 유지되어야 합니다"

    # 케이스 3: 엣지 케이스 (음수) - 음수 방지 검증
    negative_result = cap_metric_value(Metric.MONEY, -5000)
    assert negative_result == 0, "현금이 음수인 경우 0으로 보정되어야 합니다"

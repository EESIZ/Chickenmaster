"""
경제 시스템 모델

게임의 경제 시스템을 구성하는 핵심 모델들을 정의합니다.
"""

# import math  # 향후 수학 함수 사용을 위해 준비 (현재 미사용)

import json
import os
from typing import Any, cast

from game_constants import (
    METRIC_RANGES,
    TRADEOFF_RELATIONSHIPS,
    UNCERTAINTY_WEIGHTS,
    ActionType,
    Metric,
    cap_metric_value,
)


def load_economy_config() -> dict[str, Any]:
    """
    경제 설정 파일을 로드합니다.

    Returns:
        Dict[str, Any]: 경제 설정 파라미터
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "economy_config.json",
    )

    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))
    # 기본 설정 (파일이 없을 경우)

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
            "lost_cust_rep_factor": 0.1,
        },
    }


def tradeoff_compute_demand(price: int, reputation: float, config: dict[str, Any]) -> int:
    """
    가격과 평판을 기반으로 수요를 계산합니다.

    트레이드오프: 가격이 낮을수록 수요는 증가하지만 이익률은 감소합니다.

    Args:
        price: 현재 가격
        reputation: 현재 평판 (0-100)
        config: 경제 설정 파라미터

    Returns:
        int: 계산된 수요량
    """
    base_demand = config["base_demand"]
    price_sensitivity = config["price_sensitivity"]
    min_price = config["min_price"]
    max_price = config["max_price"]
    optimal_price = config["optimal_price"]
    _uncertainty_factor = config["uncertainty_factor"]  # 향후 확장을 위해 유지

    # 평판 정규화 (0-100 범위를 0-1로 변환)

    normalized_reputation = reputation / 100.0

    # 가격 효과 계산 (최적 가격에서 멀어질수록 감소)

    price_effect = 1.0 - (price_sensitivity * abs(price - optimal_price) / (max_price - min_price))

    # 평판 효과 계산 (평판이 높을수록 증가)

    reputation_factor = config["reputation_factor"]
    reputation_effect = 1.0 + (normalized_reputation * reputation_factor)

    # 최종 수요 계산

    demand = round(base_demand * price_effect * reputation_effect)

    # 음수 수요 방지

    return int(max(0, demand))

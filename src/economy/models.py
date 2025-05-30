"""
경제 시스템 모델

게임의 경제 시스템을 구성하는 핵심 모델들을 정의합니다.
"""

# import math  # 향후 수학 함수 사용을 위해 준비 (현재 미사용)

import json
import os
from typing import Any, cast


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
    demand_config = config.get("demand", {})
    base_demand = demand_config.get("base_demand", 50)
    price_elasticity = demand_config.get("price_elasticity", -0.5)
    reputation_effect = demand_config.get("reputation_effect", 0.2)
    optimal_price = demand_config.get("optimal_price", 100)

    price_factor = 1.0
    if optimal_price > 0 and price != optimal_price:
        price_factor = 1 + price_elasticity * (price - optimal_price) / optimal_price
    elif price == optimal_price:
        price_factor = 1.0
    else:
        price_factor = 1.0

    reputation_factor = 1.0
    if reputation != 50:
        reputation_factor = 1 + reputation_effect * (reputation - 50) / 50

    calculated_demand = int(max(0, base_demand * price_factor * reputation_factor))
    return calculated_demand

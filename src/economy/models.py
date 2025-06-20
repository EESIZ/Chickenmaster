#!/usr/bin/env python3
"""
경제 모델

게임의 경제 시뮬레이션을 위한 모델과 함수들을 정의합니다.
각 함수는 완전히 독립적이며, 단위 테스트가 가능합니다.
"""

# import math  # 향후 수학 함수 사용을 위해 준비 (현재 미사용)

import json
import os
from typing import Any, cast

from game_constants import PROBABILITY_LOW_THRESHOLD, REPUTATION_BASELINE


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
            "price_to_reputation_factor": PROBABILITY_LOW_THRESHOLD,
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
    optimal_price = demand_config.get("optimal_price", 10000)

    # 가격 탄력성 적용 (가격이 높을수록 수요 감소, 낮을수록 수요 증가)
    price_factor = 1.0
    if optimal_price > 0 and price != optimal_price:
        # 가격 변화에 따른 수요 변화 계산
        price_factor = 1 + price_elasticity * (price - optimal_price) / optimal_price

    # 평판 효과 적용 (평판이 높을수록 수요 증가)
    reputation_factor = 1.0
    if reputation != REPUTATION_BASELINE:
        reputation_factor = (
            1 + reputation_effect * (reputation - REPUTATION_BASELINE) / REPUTATION_BASELINE
        )

    # 최종 수요 계산 (음수 방지, 소수점 반올림)
    calculated_demand = max(0, base_demand * price_factor * reputation_factor)
    return round(calculated_demand)

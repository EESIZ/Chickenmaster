"""
경제 모델 모듈

이 모듈은 Chicken-RNG 게임의 경제 모델 함수들을 제공합니다.
수요 계산, 가격 효과, 평판 효과 등의 핵심 경제 함수를 포함합니다.

핵심 철학:
- 정답 없음: 모든 경제적 결정은 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 경제 상황은 예측 불가능하게 변화할 수 있습니다
"""

# import math  # 향후 수학 함수 사용을 위해 준비 (현재 미사용)
import json
import os
from typing import Dict, Any

# schema.py에서 필요한 상수와 Enum 가져오기
from schema import Metric, METRIC_RANGES, cap_metric_value  # noqa: F401 - 향후 확장을 위해 유지


def load_economy_config() -> Dict[str, Any]:
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
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

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


def tradeoff_compute_demand(price: int, reputation: float, config: Dict[str, Any]) -> int:
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
    price_effect = 1.0 - (
        price_sensitivity * abs(price - optimal_price) / (max_price - min_price)
    )

    # 평판 효과 계산 (평판이 높을수록 증가)
    reputation_factor = config["reputation_factor"]
    reputation_effect = 1.0 + (normalized_reputation * reputation_factor)

    # 최종 수요 계산
    demand = round(base_demand * price_effect * reputation_effect)

    # 음수 수요 방지
    return max(0, demand)

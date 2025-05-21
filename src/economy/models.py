"""
경제 모델 모듈

이 모듈은 Chicken-RNG 게임의 경제 시스템에 필요한 핵심 모델과 계산 함수를 제공합니다.
수요, 이익, 비용 등의 경제적 요소를 계산하는 함수들이 포함되어 있습니다.

핵심 철학:
- 정답 없음: 모든 경제적 결정은 득과 실을 동시에 가져옵니다
- 트레이드오프: 가격을 낮추면 수요는 증가하지만 이익률은 감소합니다
- 불확실성: 시장 상황은 예측 불가능하게 변화할 수 있습니다
"""

import math
import json
import os
from typing import Dict, Any, Optional

# schema.py에서 필요한 상수와 Enum 가져오기
from schema import Metric, METRIC_RANGES, cap_metric_value


def load_economy_config() -> Dict[str, Any]:
    """
    경제 시스템 설정 파일을 로드합니다.
    
    설정 파일이 없는 경우 기본값을 반환합니다.
    
    Returns:
        Dict[str, Any]: 경제 시스템 설정값
    """
    config_path = os.path.join(os.path.dirname(__file__), '../../data/economy_config.json')
    
    # 설정 파일 기본값
    default_config = {
        "demand": {
            "base_demand": 50,  # 기본 수요량
            "price_sensitivity": 0.5,  # 가격 민감도 (높을수록 가격 변화에 민감)
            "reputation_factor": 0.8,  # 평판 영향력 (높을수록 평판이 수요에 큰 영향)
            "min_price": 5000,  # 최소 가격
            "max_price": 20000,  # 최대 가격
            "optimal_price": 10000,  # 최적 가격 (이 가격에서 수요가 가장 높음)
            "uncertainty_factor": 0.2  # 불확실성 요소 (수요 변동성)
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    except Exception:
        return default_config


def tradeoff_compute_demand(price: float, reputation: float, config: Optional[Dict[str, Any]] = None) -> int:
    """
    가격과 평판을 기반으로 수요를 계산합니다.
    
    이 함수는 트레이드오프 원칙을 반영합니다:
    - 가격이 낮을수록 수요는 증가하지만 이익률은 감소합니다
    - 평판이 높을수록 수요는 증가하지만 유지하기 어렵습니다
    
    Args:
        price: 현재 설정된 가격
        reputation: 현재 평판 (0-100)
        config: 경제 설정 파라미터 (기본값: None, 이 경우 설정 파일에서 로드)
        
    Returns:
        int: 계산된 수요량 (판매 가능한 단위)
    """
    # 설정 로드
    if config is None:
        config = load_economy_config()["demand"]
    
    # 설정값 추출
    base_demand = config["base_demand"]
    price_sensitivity = config["price_sensitivity"]
    reputation_factor = config["reputation_factor"]
    min_price = config["min_price"]
    max_price = config["max_price"]
    optimal_price = config["optimal_price"]
    uncertainty_factor = config["uncertainty_factor"]
    
    # 평판 정규화 (0-100 범위를 0-1로 변환)
    normalized_reputation = reputation / 100.0
    
    # 가격 효과 계산 (최적 가격에서 멀어질수록 수요 감소)
    price_effect = 1.0 - (price_sensitivity * abs(price - optimal_price) / (max_price - min_price))
    price_effect = max(0.1, min(1.0, price_effect))  # 0.1-1.0 범위로 제한
    
    # 평판 효과 계산 (평판이 높을수록 수요 증가)
    reputation_effect = 1.0 + (normalized_reputation * reputation_factor)
    
    # 불확실성 요소 (약간의 무작위성 추가)
    # 실제 구현에서는 이 부분이 더 복잡한 확률 분포를 따를 수 있음
    uncertainty_multiplier = 1.0
    
    # 최종 수요 계산
    demand = base_demand * price_effect * reputation_effect * uncertainty_multiplier
    
    # 정수로 반올림
    return max(0, round(demand))


def uncertainty_adjust_demand(base_demand: int, day: int, season_factor: float = 1.0) -> int:
    """
    기본 수요에 불확실성 요소를 적용합니다.
    
    현실 세계의 불확실성을 반영하여 수요에 변동성을 추가합니다.
    
    Args:
        base_demand: 기본 계산된 수요
        day: 현재 게임 일수
        season_factor: 계절적 요인 (기본값: 1.0)
        
    Returns:
        int: 불확실성이 적용된 수요
    """
    # 이 함수는 향후 구현 예정
    # 현재는 기본 수요를 그대로 반환
    return base_demand

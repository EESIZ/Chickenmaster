"""
지표 모듈

이 모듈은 게임의 핵심 지표를 정의하고 관리하는 클래스들을 포함합니다.
"""

from enum import Enum
from typing import Final

from app.core.game_constants import (
    DEFAULT_STARTING_MONEY,
    DEFAULT_STARTING_REPUTATION,
    DEFAULT_STARTING_HAPPINESS,
    DEFAULT_STARTING_SUFFERING,
    DEFAULT_STARTING_INVENTORY,
    DEFAULT_STARTING_STAFF_FATIGUE,
    DEFAULT_STARTING_FACILITY,
    DEFAULT_STARTING_DEMAND,
)

class MetricEnum(Enum):
    """
    게임의 핵심 지표를 정의하는 열거형
    
    각 지표는 게임 내에서 특정한 의미를 가집니다.
    """
    MONEY = "money"           # 자금
    REPUTATION = "reputation" # 평판
    HAPPINESS = "happiness"   # 행복도
    SUFFERING = "suffering"   # 고통도
    INVENTORY = "inventory"   # 재고
    STAFF_FATIGUE = "staff_fatigue"  # 직원 피로도
    FACILITY = "facility"     # 시설 상태
    DEMAND = "demand"         # 수요

# 지표별 기본값 정의
METRIC_DEFAULTS: dict[MetricEnum, float] = {
    MetricEnum.MONEY: DEFAULT_STARTING_MONEY,
    MetricEnum.REPUTATION: DEFAULT_STARTING_REPUTATION,
    MetricEnum.HAPPINESS: DEFAULT_STARTING_HAPPINESS,
    MetricEnum.SUFFERING: DEFAULT_STARTING_SUFFERING,
    MetricEnum.INVENTORY: DEFAULT_STARTING_INVENTORY,
    MetricEnum.STAFF_FATIGUE: DEFAULT_STARTING_STAFF_FATIGUE,
    MetricEnum.FACILITY: DEFAULT_STARTING_FACILITY,
    MetricEnum.DEMAND: DEFAULT_STARTING_DEMAND,
}

def validate_metric_value(metric: MetricEnum, value: float) -> float:
    """
    지표 값이 유효한 범위 내에 있는지 확인하고, 필요한 경우 조정합니다.
    
    Args:
        metric: 검증할 지표
        value: 검증할 값
        
    Returns:
        float: 유효한 범위 내로 조정된 값
        
    Note:
        - 모든 지표는 0.0 이상이어야 합니다.
        - MONEY는 최대 1,000,000.0까지 가능합니다.
        - INVENTORY는 최대 1,000.0까지 가능합니다.
        - 나머지 지표는 최대 100.0까지 가능합니다.
    """
    if metric not in METRIC_DEFAULTS:
        return value
    
    default_value = METRIC_DEFAULTS[metric]
    min_value = 0.0
    max_value = 100.0
    
    if metric == MetricEnum.MONEY:
        max_value = 1000000.0
    elif metric == MetricEnum.INVENTORY:
        max_value = 1000.0
    
    return max(min_value, min(value, max_value)) 
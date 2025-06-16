"""
게임 지표 관련 모듈

이 모듈은 게임의 각종 지표를 정의하고 관리하는 기능을 제공합니다.
"""

from enum import Enum, auto
from typing import Dict, Any

class MetricEnum(Enum):
    """게임 지표 종류"""
    MONEY = "money"
    REPUTATION = "reputation"
    HAPPINESS = "happiness"
    SUFFERING = "suffering"
    INVENTORY = "inventory"
    STAFF_FATIGUE = "staff_fatigue"
    FACILITY = "facility"
    DEMAND = "demand"

def validate_metric_value(metric: MetricEnum, value: float) -> float:
    """
    지표 값이 유효한 범위 내에 있는지 검증하고 보정합니다.

    Args:
        metric: 지표 종류
        value: 검증할 값

    Returns:
        float: 보정된 값
    """
    if metric == MetricEnum.MONEY:
        return max(0, value)  # 돈은 음수가 될 수 없음
    elif metric in [MetricEnum.REPUTATION, MetricEnum.HAPPINESS, MetricEnum.SUFFERING,
                   MetricEnum.STAFF_FATIGUE, MetricEnum.FACILITY]:
        return max(0, min(100, value))  # 0-100 사이의 값
    elif metric in [MetricEnum.INVENTORY, MetricEnum.DEMAND]:
        return max(0, min(999, value))  # 0-999 사이의 값
    else:
        raise ValueError(f"Unknown metric: {metric}")

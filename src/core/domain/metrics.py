"""
게임 지표 관련 모듈

이 모듈은 게임의 각종 지표를 정의하고 관리하는 기능을 제공합니다.
"""

from enum import Enum, auto
from typing import Dict, Any
from ..ports.data_provider import DataProvider, DataCategory, DataRequest

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

class MetricsValidator:
    """지표 값 검증기"""
    
    def __init__(self, provider: DataProvider):
        self.provider = provider
        
    def validate_metric_value(self, metric: MetricEnum, value: float) -> float:
        """
        지표 값이 유효한 범위 내에 있는지 검증하고 보정합니다.

        Args:
            metric: 지표 종류
            value: 검증할 값

        Returns:
            float: 보정된 값
        """
        limits = self.provider.get_dict(DataCategory.METRICS, f"{metric.value}_limits")
        
        if metric == MetricEnum.MONEY:
            return max(limits.get("min", 0), value)
        elif metric in [MetricEnum.REPUTATION, MetricEnum.HAPPINESS, MetricEnum.SUFFERING,
                     MetricEnum.STAFF_FATIGUE, MetricEnum.FACILITY]:
            return max(limits.get("min", 0), min(limits.get("max", 100), value))
        elif metric in [MetricEnum.INVENTORY, MetricEnum.DEMAND]:
            return max(limits.get("min", 0), min(limits.get("max", 999), value))
        else:
            raise ValueError(f"Unknown metric: {metric}")

"""
지표 수정자 모듈

지표 변화에 대한 다양한 수정자를 제공합니다.
"""

import random

from game_constants import Metric

from abc import ABC, abstractmethod
from typing import Any


class MetricModifier(ABC):
    """지표 수정자 인터페이스"""

    @abstractmethod
    def apply(
        self, metrics: dict[Metric, float], updates: dict[Metric, float]
    ) -> dict[Metric, float]:
        """지표 업데이트를 적용하고 수정된 지표를 반환합니다."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """수정자 이름을 반환합니다."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """수정자 설명을 반환합니다."""
        pass

class SimpleSeesawModifier(MetricModifier):
    """행복-고통 시소 관계를 유지하는 단순 수정자"""

    def apply(
        self, metrics: dict[Metric, float], updates: dict[Metric, float]
    ) -> dict[Metric, float]:
        """지표 업데이트를 적용하고 행복-고통 시소 불변식을 유지합니다."""
        # 지표 복사
        new_metrics = metrics.copy()

        # 업데이트 적용
        for metric, value in updates.items():
            new_metrics[metric] = value

        # 행복-고통 시소 불변식 유지
        if Metric.HAPPINESS in updates:
            new_metrics[Metric.SUFFERING] = 100.0 - new_metrics[Metric.HAPPINESS]
        elif Metric.SUFFERING in updates:
            new_metrics[Metric.HAPPINESS] = 100.0 - new_metrics[Metric.SUFFERING]

        return new_metrics

    def get_name(self) -> str:
        """수정자 이름을 반환합니다."""
        return "SimpleSeesawModifier"

    def get_description(self) -> str:
        """수정자 설명을 반환합니다."""
        return "행복과 고통의 합이 100이 되도록 유지하는 단순 수정자"

class AdaptiveModifier(MetricModifier):
    """플레이어 성향과 게임 상태에 따라 적응하는 수정자"""

    def __init__(self, player_profile: dict[str, Any] | None = None):
        """AdaptiveModifier 초기화"""
        self.player_profile = player_profile or {}

    def apply(
        self, metrics: dict[Metric, float], updates: dict[Metric, float]
    ) -> dict[Metric, float]:
        """지표 업데이트를 적용하고 적응형 수정을 수행합니다."""
        # 현재는 SimpleSeesawModifier와 동일하게 동작
        # M-6에서 적응형 로직 구현 예정
        new_metrics = metrics.copy()

        # 업데이트 적용
        for metric, value in updates.items():
            new_metrics[metric] = value

        # 행복-고통 시소 불변식 유지
        if Metric.HAPPINESS in updates:
            new_metrics[Metric.SUFFERING] = 100.0 - new_metrics[Metric.HAPPINESS]
        elif Metric.SUFFERING in updates:
            new_metrics[Metric.HAPPINESS] = 100.0 - new_metrics[Metric.SUFFERING]

        return new_metrics

    def get_name(self) -> str:
        """수정자 이름을 반환합니다."""
        return "AdaptiveModifier"

    def get_description(self) -> str:
        """수정자 설명을 반환합니다."""
        return (
            "게임 진행 상황과 플레이어 성향에 따라 지표 간 관계를 동적으로 조정하는 "
            "적응형 수정자 (M-6에서 구현 예정)"
        )

def uncertainty_apply_random_fluctuation(
    metrics: dict[Metric, float], intensity: float = 0.1, seed: int | None = None
) -> dict[Metric, float]:
    """불확실성 요소를 반영하여 지표에 무작위 변동을 적용합니다."""
    # 시드 설정
    if seed is not None:
        random.seed(seed)

    # 지표 복사
    new_metrics = metrics.copy()

    # 각 지표에 무작위 변동 적용
    for metric in metrics:
        if metric not in {Metric.HAPPINESS, Metric.SUFFERING}:  # 행복-고통은 시소 관계로 처리
            current_value = new_metrics[metric]
            fluctuation = random.uniform(-intensity, intensity) * current_value
            new_metrics[metric] = current_value + fluctuation

    # 행복-고통 시소 불변식 유지
    if random.random() < 0.5:  # 50% 확률로 행복 또는 고통 중 하나를 변경
        happiness = new_metrics[Metric.HAPPINESS]
        fluctuation = random.uniform(-intensity, intensity) * happiness
        new_metrics[Metric.HAPPINESS] = happiness + fluctuation
        new_metrics[Metric.SUFFERING] = 100.0 - new_metrics[Metric.HAPPINESS]
    else:
        suffering = new_metrics[Metric.SUFFERING]
        fluctuation = random.uniform(-intensity, intensity) * suffering
        new_metrics[Metric.SUFFERING] = suffering + fluctuation
        new_metrics[Metric.HAPPINESS] = 100.0 - new_metrics[Metric.SUFFERING]

    return new_metrics

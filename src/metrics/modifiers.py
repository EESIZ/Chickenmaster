"""
지표 수정자(Modifier) 모듈

이 모듈은 Chicken-RNG 게임의 지표 수정 메커니즘을 정의합니다.
다양한 지표 수정자(Modifier)를 통해 지표 간 관계와 변화 규칙을 구현합니다.

핵심 철학:
- 정답 없음: 모든 지표 변화는 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 지표 변화는 예측 불가능한 요소에 영향을 받습니다

미래 확장 (M-6):
- from abc import ABC, abstractmethod: AdaptiveModifier 구현 시 사용 예정
- baseline, sensitivity 로직 추가 예정
"""

from typing import Dict, Any, Optional, Protocol, runtime_checkable
import random
import logging

from schema import Metric, cap_metric_value

# 로거 설정
logger = logging.getLogger(__name__)


@runtime_checkable
class MetricModifier(Protocol):
    """
    지표 수정자 인터페이스

    이 프로토콜은 지표 수정 메커니즘의 표준 인터페이스를 정의합니다.
    모든 지표 수정자는 이 프로토콜을 구현해야 합니다.
    """

    def apply(
        self, metrics: Dict[Metric, float], updates: Dict[Metric, float]
    ) -> Dict[Metric, float]:
        """
        지표 업데이트를 적용하고 수정된 지표를 반환합니다.

        Args:
            metrics: 현재 지표 상태
            updates: 적용할 지표 변경사항

        Returns:
            Dict[Metric, float]: 수정된 지표 상태
        """
        ...

    def get_name(self) -> str:
        """
        수정자의 이름을 반환합니다.

        Returns:
            str: 수정자 이름
        """
        ...

    def get_description(self) -> str:
        """
        수정자의 설명을 반환합니다.

        Returns:
            str: 수정자 설명
        """
        ...


class SimpleSeesawModifier:
    """
    행복-고통 시소 불변식을 유지하는 기본 수정자

    이 수정자는 행복과 고통의 합이 항상 100이 되도록 보장합니다.
    한쪽이 증가하면 다른 쪽은 자동으로 감소합니다.
    """

    def apply(
        self, metrics: Dict[Metric, float], updates: Dict[Metric, float]
    ) -> Dict[Metric, float]:
        """
        지표 업데이트를 적용하고 행복-고통 시소 불변식을 유지합니다.

        Args:
            metrics: 현재 지표 상태
            updates: 적용할 지표 변경사항

        Returns:
            Dict[Metric, float]: 수정된 지표 상태
        """
        # 현재 지표의 복사본 생성
        result = metrics.copy()

        # 미정의 지표 경고
        for metric in updates:
            if metric not in Metric:
                logger.warning(f"Unknown metric update attempted: {metric}")

        # 업데이트 적용
        for metric, value in updates.items():
            result[metric] = cap_metric_value(metric, value)

        # 행복-고통 시소 불변식 적용
        if Metric.HAPPINESS in updates:
            result[Metric.SUFFERING] = 100 - result[Metric.HAPPINESS]
        elif Metric.SUFFERING in updates:
            result[Metric.HAPPINESS] = 100 - result[Metric.SUFFERING]

        return result

    def get_name(self) -> str:
        """
        수정자의 이름을 반환합니다.

        Returns:
            str: 수정자 이름
        """
        return "SimpleSeesawModifier"

    def get_description(self) -> str:
        """
        수정자의 설명을 반환합니다.

        Returns:
            str: 수정자 설명
        """
        return "행복과 고통의 합이 항상 100이 되도록 유지하는 기본 수정자"


class AdaptiveModifier:
    """
    적응형 지표 수정자 (M-6에서 구현 예정)

    이 수정자는 게임 진행 상황과 플레이어 성향에 따라
    지표 간 관계를 동적으로 조정합니다.

    TODO: M-6에서 실제 구현 예정
    현재는 SimpleSeesawModifier와 동일하게 동작하는 스켈레톤만 제공
    """

    def __init__(self, player_profile: Optional[Dict[str, Any]] = None):
        """
        AdaptiveModifier 초기화

        Args:
            player_profile: 플레이어 성향 프로필 (기본값: None)
        """
        # TODO: M-6에서 플레이어 성향 분석 및 적응형 로직 구현
        self.player_profile = player_profile or {}

    def apply(
        self, metrics: Dict[Metric, float], updates: Dict[Metric, float]
    ) -> Dict[Metric, float]:
        """
        지표 업데이트를 적용하고 적응형 수정을 수행합니다.

        Args:
            metrics: 현재 지표 상태
            updates: 적용할 지표 변경사항

        Returns:
            Dict[Metric, float]: 수정된 지표 상태
        """
        # TODO: M-6에서 적응형 로직 구현
        # 현재는 SimpleSeesawModifier와 동일하게 동작

        # 현재 지표의 복사본 생성
        result = metrics.copy()

        # 미정의 지표 경고
        for metric in updates:
            if metric not in Metric:
                logger.warning(f"Unknown metric update attempted: {metric}")

        # 업데이트 적용
        for metric, value in updates.items():
            result[metric] = cap_metric_value(metric, value)

        # 행복-고통 시소 불변식 적용
        if Metric.HAPPINESS in updates:
            result[Metric.SUFFERING] = 100 - result[Metric.HAPPINESS]
        elif Metric.SUFFERING in updates:
            result[Metric.HAPPINESS] = 100 - result[Metric.SUFFERING]

        return result

    def get_name(self) -> str:
        """
        수정자의 이름을 반환합니다.

        Returns:
            str: 수정자 이름
        """
        return "AdaptiveModifier"

    def get_description(self) -> str:
        """
        수정자의 설명을 반환합니다.

        Returns:
            str: 수정자 설명
        """
        return "게임 진행 상황과 플레이어 성향에 따라 지표 간 관계를 동적으로 조정하는 적응형 수정자 (M-6에서 구현 예정)"


def uncertainty_apply_random_fluctuation(
    metrics: Dict[Metric, float], intensity: float = 0.1, seed: Optional[int] = None
) -> Dict[Metric, float]:
    """
    불확실성 요소를 반영하여 지표에 무작위 변동을 적용합니다.

    Args:
        metrics: 현재 지표 상태
        intensity: 변동 강도 (기본값: 0.1, 즉 ±10%)
        seed: 난수 생성 시드 (기본값: None)

    Returns:
        Dict[Metric, float]: 변동이 적용된 지표 상태
    """
    # 시드가 제공된 경우 설정
    if seed is not None:
        random.seed(seed)

    # 결과 지표 초기화
    result = metrics.copy()

    # 행복과 고통은 시소 관계를 유지해야 하므로 별도 처리
    happiness_suffering_pair = {Metric.HAPPINESS, Metric.SUFFERING}

    # 행복-고통 외 다른 지표에 무작위 변동 적용
    for metric, value in metrics.items():
        if metric not in happiness_suffering_pair:
            # ±intensity 범위 내에서 무작위 변동 적용
            fluctuation = 1.0 + (random.random() * 2 - 1) * intensity
            result[metric] = cap_metric_value(metric, value * fluctuation)

    # 행복-고통 시소 관계 유지하면서 변동 적용
    if Metric.HAPPINESS in metrics:
        happiness = metrics[Metric.HAPPINESS]
        # 행복에만 변동 적용하고 고통은 시소 관계로 조정
        fluctuation = 1.0 + (random.random() * 2 - 1) * intensity
        new_happiness = cap_metric_value(Metric.HAPPINESS, happiness * fluctuation)
        result[Metric.HAPPINESS] = new_happiness
        result[Metric.SUFFERING] = 100 - new_happiness

    return result

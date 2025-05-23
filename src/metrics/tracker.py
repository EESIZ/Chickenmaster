"""
지표 추적 모듈

이 모듈은 Chicken-RNG 게임의 지표(metrics)를 추적하고 관리합니다.
돈, 평판, 행복/고통, 재고, 직원 피로도 등의 지표를 업데이트하고 균형을 유지합니다.

핵심 철학:
- 정답 없음: 모든 지표 변화는 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 지표 변화는 예측 불가능한 요소에 영향을 받습니다
"""

from typing import Dict, Any, Optional

# schema.py에서 필요한 상수와 Enum 가져오기
from schema import (
    Metric,
    METRIC_RANGES,
    cap_metric_value,
    are_happiness_suffering_balanced,
)


class MetricsTracker:
    """
    게임 지표를 추적하고 관리하는 클래스

    이 클래스는 게임의 모든 지표를 중앙에서 관리하고,
    지표 간 트레이드오프 관계를 유지합니다.
    """

    def __init__(self, initial_metrics: Optional[Dict[Metric, float]] = None):
        """
        MetricsTracker 초기화

        Args:
            initial_metrics: 초기 지표 값 (기본값: None, 이 경우 schema.py의 기본값 사용)
        """
        self.metrics = {}

        # 초기 지표 설정
        for metric, (min_val, max_val, default_val) in METRIC_RANGES.items():
            if initial_metrics and metric in initial_metrics:
                self.metrics[metric] = cap_metric_value(metric, initial_metrics[metric])
            else:
                self.metrics[metric] = default_val

    def get_metrics(self) -> Dict[Metric, float]:
        """
        현재 지표 상태를 반환합니다.

        Returns:
            Dict[Metric, float]: 현재 지표 상태
        """
        return self.metrics.copy()

    def update_metric(self, metric: Metric, value: float) -> None:
        """
        단일 지표를 업데이트합니다.

        불확실성 ≠ 불합리한 음수: 불확실성은 게임의 핵심이지만,
        물리적으로 불가능한 음수 재고나 음수 자금은 허용하지 않습니다.

        Args:
            metric: 업데이트할 지표
            value: 새 지표 값
        """
        # 지표 값이 허용 범위 내에 있도록 보정
        self.metrics[metric] = cap_metric_value(metric, value)

        # 행복-고통 시소 관계 유지
        if metric == Metric.HAPPINESS:
            self.metrics[Metric.SUFFERING] = 100 - value
        elif metric == Metric.SUFFERING:
            self.metrics[Metric.HAPPINESS] = 100 - value

    def tradeoff_update_metrics(self, updates: Dict[Metric, float]) -> None:
        """
        여러 지표를 동시에 업데이트하고 트레이드오프 관계를 적용합니다.

        Args:
            updates: 업데이트할 지표와 값의 딕셔너리
        """
        # 먼저 모든 지표 업데이트
        for metric, value in updates.items():
            self.update_metric(metric, value)

        # 행복-고통 시소 관계 확인
        happiness = self.metrics.get(Metric.HAPPINESS, 50)
        suffering = self.metrics.get(Metric.SUFFERING, 50)

        if not are_happiness_suffering_balanced(happiness, suffering):
            # 행복과 고통의 합이 100이 아니면 조정
            self.metrics[Metric.SUFFERING] = 100 - happiness

    def uncertainty_apply_random_fluctuation(
        self, day: int, intensity: float = 0.1
    ) -> None:
        """
        불확실성 요소를 반영하여 지표에 무작위 변동을 적용합니다.

        Args:
            day: 현재 게임 일수
            intensity: 변동 강도 (기본값: 0.1)
        """
        # 이 함수는 향후 구현 예정
        # 현재는 아무 작업도 수행하지 않음
        pass

    def noRightAnswer_simulate_decision(
        self, decision: Dict[str, Any]
    ) -> Dict[Metric, float]:
        """
        플레이어 결정의 결과를 시뮬레이션하여 예상 지표 변화를 반환합니다.

        이 함수는 '정답 없음' 원칙을 반영하여, 모든 결정에 장단점이 있음을 보여줍니다.

        Args:
            decision: 플레이어의 결정 (행동 유형과 파라미터)

        Returns:
            Dict[Metric, float]: 예상되는 지표 변화
        """
        # 이 함수는 향후 구현 예정
        # 현재는 빈 딕셔너리 반환
        return {}

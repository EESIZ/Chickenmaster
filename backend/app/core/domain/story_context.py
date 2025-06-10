"""
스토리 컨텍스트 모듈

이 모듈은 게임의 현재 상태와 컨텍스트를 관리하는 클래스들을 정의합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.core.domain.metrics import MetricEnum
from app.core.game_constants import (
    EARLY_GAME_THRESHOLD,
    MID_GAME_THRESHOLD,
    MINIMUM_TREND_POINTS,
    TOTAL_GAME_DAYS,
)


@dataclass(frozen=True)
class MetricSnapshot:
    """
    지표 스냅샷을 나타내는 불변 데이터 클래스

    특정 시점의 지표 값을 기록합니다.
    """

    value: float
    timestamp: datetime


@dataclass(frozen=True)
class GameEvent:
    """
    게임 이벤트를 나타내는 불변 데이터 클래스

    게임 내에서 발생하는 이벤트를 기록합니다.
    """

    event_id: str
    description: str
    timestamp: datetime
    severity: float
    affected_metrics: list[MetricEnum]


@dataclass(frozen=True)
class StoryContext:
    """
    게임의 현재 상태와 컨텍스트를 나타내는 불변 데이터 클래스

    게임의 현재 상태, 지표 히스토리, 이벤트, 스토리 패턴 등을 관리합니다.
    모든 속성은 불변이며, 상태 변경은 새로운 인스턴스를 생성하여 이루어집니다.
    """

    current_day: int
    total_days: int = TOTAL_GAME_DAYS
    current_metrics: dict[MetricEnum, float] = field(default_factory=dict)
    metrics_history: dict[MetricEnum, list[MetricSnapshot]] = field(default_factory=dict)
    recent_events: list[GameEvent] = field(default_factory=list)
    story_patterns: list[str] = field(default_factory=list)

    @property
    def game_progress(self) -> float:
        """
        게임 진행률을 계산합니다.

        Returns:
            float: 0.0 ~ 1.0 사이의 게임 진행률
        """
        return self.current_day / self.total_days

    @property
    def game_stage(self) -> str:
        """
        현재 게임 단계를 반환합니다.

        Returns:
            str: "early", "mid", "late" 중 하나
        """
        if self.current_day <= EARLY_GAME_THRESHOLD:
            return "early"
        elif self.current_day <= MID_GAME_THRESHOLD:
            return "mid"
        else:
            return "late"

    def get_metric_trend(self, metric: MetricEnum, days: int = 7) -> list[float]:
        """
        특정 지표의 최근 추세를 반환합니다.

        Args:
            metric: 추세를 확인할 지표
            days: 확인할 기간 (일)

        Returns:
            list[float]: 최근 지표 값들의 리스트
        """
        if metric not in self.metrics_history:
            return []

        history = self.metrics_history[metric]
        recent_snapshots = [s for s in history if s.timestamp >= datetime.now()]
        return [s.value for s in recent_snapshots[-days:]]

    def get_metric_history(self, metric: MetricEnum) -> list[MetricSnapshot]:
        """
        특정 지표의 전체 히스토리를 반환합니다.

        Args:
            metric: 히스토리를 확인할 지표

        Returns:
            list[MetricSnapshot]: 지표의 전체 히스토리
        """
        return self.metrics_history.get(metric, [])

    def get_recent_events(self, count: int = 5) -> list[GameEvent]:
        """
        최근 이벤트들을 반환합니다.

        Args:
            count: 반환할 이벤트 수

        Returns:
            list[GameEvent]: 최근 이벤트들의 리스트
        """
        return sorted(self.recent_events, key=lambda e: e.timestamp, reverse=True)[:count]

    def get_active_story_patterns(self) -> list[str]:
        """
        현재 활성화된 스토리 패턴들을 반환합니다.

        Returns:
            list[str]: 활성화된 스토리 패턴 ID들의 리스트
        """
        return self.story_patterns

    def get_metric_value(self, metric: MetricEnum) -> float:
        """
        특정 지표의 현재 값을 반환합니다.

        Args:
            metric: 값을 확인할 지표

        Returns:
            float: 지표의 현재 값
        """
        return self.current_metrics.get(metric, 0.0)

    def get_metric_change(self, metric: MetricEnum, days: int = 7) -> float:
        """
        특정 지표의 변화량을 계산합니다.

        Args:
            metric: 변화량을 계산할 지표
            days: 계산할 기간 (일)

        Returns:
            float: 지표의 변화량
        """
        trend = self.get_metric_trend(metric, days)
        if len(trend) < MINIMUM_TREND_POINTS:
            return 0.0
        return trend[-1] - trend[0]

    def get_metric_volatility(self, metric: MetricEnum, days: int = 7) -> float:
        """
        특정 지표의 변동성을 계산합니다.

        Args:
            metric: 변동성을 계산할 지표
            days: 계산할 기간 (일)

        Returns:
            float: 지표의 변동성 (평균 절대 변화량)
        """
        trend = self.get_metric_trend(metric, days)
        if len(trend) < MINIMUM_TREND_POINTS:
            return 0.0

        changes = [abs(trend[i] - trend[i - 1]) for i in range(1, len(trend))]
        return sum(changes) / len(changes) if changes else 0.0

    def get_metric_correlation(
        self, metric1: MetricEnum, metric2: MetricEnum, days: int = 7
    ) -> float:
        """
        두 지표 간의 상관관계를 계산합니다.

        Args:
            metric1: 첫 번째 지표
            metric2: 두 번째 지표
            days: 계산할 기간 (일)

        Returns:
            float: -1.0 ~ 1.0 사이의 상관계수
        """
        trend1 = self.get_metric_trend(metric1, days)
        trend2 = self.get_metric_trend(metric2, days)

        if len(trend1) != len(trend2) or len(trend1) < MINIMUM_TREND_POINTS:
            return 0.0

        # 평균 계산
        mean1 = sum(trend1) / len(trend1)
        mean2 = sum(trend2) / len(trend2)

        # 공분산 계산
        covariance = sum(
            (x - mean1) * (y - mean2) for x, y in zip(trend1, trend2, strict=False)
        ) / len(trend1)

        # 표준편차 계산
        std1 = (sum((x - mean1) ** 2 for x in trend1) / len(trend1)) ** 0.5
        std2 = (sum((y - mean2) ** 2 for y in trend2) / len(trend2)) ** 0.5

        if std1 == 0 or std2 == 0:
            return 0.0

        return covariance / (std1 * std2)

    def get_game_state_summary(self) -> dict:
        """
        게임 상태 요약을 반환합니다.

        Returns:
            dict: 게임 상태 요약 정보를 담은 딕셔너리
        """
        return {
            "current_day": self.current_day,
            "total_days": self.total_days,
            "game_progress": self.game_progress,
            "game_stage": self.game_stage,
            "metrics": self.current_metrics,
            "recent_events": [e.event_id for e in self.get_recent_events()],
            "active_patterns": self.get_active_story_patterns(),
        }

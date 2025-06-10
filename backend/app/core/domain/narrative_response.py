"""
내러티브 응답 모듈

이 모듈은 게임의 내러티브 응답을 정의하고 관리하는 클래스들을 포함합니다.
"""

from dataclasses import dataclass, field

from app.core.domain.metrics import MetricEnum
from app.core.game_constants import (
    PROBABILITY_HIGH_THRESHOLD,
    PROBABILITY_MEDIUM_THRESHOLD,
)


@dataclass(frozen=True)
class MetricChange:
    """
    지표 변화를 나타내는 불변 데이터 클래스

    게임 내에서 발생하는 지표의 변화를 기록합니다.
    """

    metric: MetricEnum
    value: float
    is_multiplier: bool = False


@dataclass(frozen=True)
class SuggestedEvent:
    """
    제안된 이벤트를 나타내는 불변 데이터 클래스

    게임 내에서 발생할 수 있는 이벤트를 제안합니다.
    """

    event_id: str
    probability: float
    conditions: dict[str, float]
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StoryPattern:
    """
    스토리 패턴을 나타내는 불변 데이터 클래스

    게임 내에서 발생할 수 있는 스토리 패턴을 정의합니다.
    """

    pattern_id: str
    probability: float
    related_metrics: list[MetricEnum]
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NarrativeResponse:
    """
    내러티브 응답을 나타내는 불변 데이터 클래스

    게임의 현재 상태에 대한 내러티브 응답을 생성합니다.
    모든 속성은 불변이며, 상태 변경은 새로운 인스턴스를 생성하여 이루어집니다.
    """

    narrative_ko: str
    narrative_en: str
    suggested_event: SuggestedEvent | None = None
    story_pattern: StoryPattern | None = None
    metric_changes: list[MetricChange] = field(default_factory=list)
    severity: float = PROBABILITY_MEDIUM_THRESHOLD

    @property
    def has_suggested_event(self) -> bool:
        """
        제안된 이벤트가 있는지 확인합니다.

        Returns:
            bool: 제안된 이벤트 존재 여부
        """
        return self.suggested_event is not None

    @property
    def has_story_pattern(self) -> bool:
        """
        스토리 패턴이 있는지 확인합니다.

        Returns:
            bool: 스토리 패턴 존재 여부
        """
        return self.story_pattern is not None

    def get_metric_changes(self) -> dict[MetricEnum, float]:
        """
        지표 변화를 딕셔너리로 반환합니다.

        Returns:
            dict[MetricEnum, float]: 지표별 변화량의 합계
        """
        changes: dict[MetricEnum, float] = {}
        for change in self.metric_changes:
            if change.metric not in changes:
                changes[change.metric] = 0.0
            if change.is_multiplier:
                changes[change.metric] *= change.value
            else:
                changes[change.metric] += change.value
        return changes

    def get_severity_level(self) -> str:
        """
        심각도 수준을 반환합니다.

        Returns:
            str: "high", "medium", "low" 중 하나
        """
        if self.severity >= PROBABILITY_HIGH_THRESHOLD:
            return "high"
        elif self.severity >= PROBABILITY_MEDIUM_THRESHOLD:
            return "medium"
        else:
            return "low"

    def to_dict(self) -> dict:
        """
        내러티브 응답을 딕셔너리로 변환합니다.

        Returns:
            dict: 내러티브 응답의 모든 정보를 담은 딕셔너리
        """
        response_dict = {
            "narrative_ko": self.narrative_ko,
            "narrative_en": self.narrative_en,
            "severity": self.severity,
            "metric_changes": [
                {
                    "metric": change.metric.name,
                    "value": change.value,
                    "is_multiplier": change.is_multiplier,
                }
                for change in self.metric_changes
            ],
        }

        if self.suggested_event:
            response_dict["suggested_event"] = {
                "event_id": self.suggested_event.event_id,
                "probability": self.suggested_event.probability,
                "conditions": self.suggested_event.conditions,
                "tags": self.suggested_event.tags,
            }

        if self.story_pattern:
            response_dict["story_pattern"] = {
                "pattern_id": self.story_pattern.pattern_id,
                "probability": self.story_pattern.probability,
                "related_metrics": [metric.name for metric in self.story_pattern.related_metrics],
                "tags": self.story_pattern.tags,
            }

        return response_dict

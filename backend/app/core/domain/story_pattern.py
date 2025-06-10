"""
스토리 패턴 모듈

이 모듈은 게임의 스토리 패턴을 정의하고 관리하는 클래스들을 포함합니다.
"""

from dataclasses import dataclass, field
from enum import Enum

from app.core.domain.metrics import MetricEnum
from app.core.game_constants import (
    PROBABILITY_HIGH_THRESHOLD,
    PROBABILITY_MEDIUM_THRESHOLD,
)


class PatternCategory(Enum):
    """
    스토리 패턴의 카테고리를 정의하는 열거형

    각 카테고리는 게임 내에서 특정한 의미를 가집니다.
    """

    GROWTH = "growth"  # 성장 단계
    DECLINE = "decline"  # 쇠퇴 단계
    CRISIS = "crisis"  # 위기 상황
    RECOVERY = "recovery"  # 회복 단계
    STAGNATION = "stagnation"  # 정체 단계


@dataclass(frozen=True)
class PatternTrigger:
    """
    스토리 패턴의 트리거 조건을 정의하는 불변 데이터 클래스

    특정 조건이 만족될 때 스토리 패턴이 활성화됩니다.
    """

    metric: MetricEnum
    threshold: float
    comparison: str  # "above", "below", "between"
    secondary_value: float | None = None


@dataclass(frozen=True)
class PatternEffect:
    """
    스토리 패턴의 효과를 정의하는 불변 데이터 클래스

    패턴이 활성화될 때 적용되는 효과를 정의합니다.
    """

    metric: MetricEnum
    value: float
    is_multiplier: bool = False


@dataclass(frozen=True)
class StoryPattern:
    """
    스토리 패턴을 정의하는 불변 데이터 클래스

    게임 내에서 발생할 수 있는 다양한 상황과 그에 따른 효과를 정의합니다.
    모든 속성은 불변이며, 상태 변경은 새로운 인스턴스를 생성하여 이루어집니다.
    """

    pattern_id: str
    name_ko: str
    name_en: str
    description_ko: str
    description_en: str
    category: PatternCategory
    severity: float
    trigger: PatternTrigger
    effects: list[PatternEffect]
    related_metrics: list[MetricEnum]
    tags: list[str] = field(default_factory=list)
    cooldown: int = 0
    probability: float = PROBABILITY_MEDIUM_THRESHOLD

    @property
    def affected_metrics(self) -> set[MetricEnum]:
        """
        패턴이 영향을 미치는 모든 지표의 집합을 반환합니다.

        Returns:
            set[MetricEnum]: 영향을 받는 지표들의 집합
        """
        return {effect.metric for effect in self.effects}

    def is_triggered(self, metric_value: float) -> bool:
        """
        주어진 지표 값이 트리거 조건을 만족하는지 확인합니다.

        Args:
            metric_value: 확인할 지표 값

        Returns:
            bool: 트리거 조건 만족 여부
        """
        if self.trigger.comparison == "above":
            return metric_value > self.trigger.threshold
        elif self.trigger.comparison == "below":
            return metric_value < self.trigger.threshold
        elif self.trigger.comparison == "between":
            if self.trigger.secondary_value is None:
                return False
            return self.trigger.threshold <= metric_value <= self.trigger.secondary_value
        return False

    def calculate_effect_value(self, base_value: float, effect: PatternEffect) -> float:
        """
        효과 값을 계산합니다.

        Args:
            base_value: 기본 값
            effect: 적용할 효과

        Returns:
            float: 계산된 효과 값
        """
        if effect.is_multiplier:
            return base_value * effect.value
        return base_value + effect.value

    def get_effect_summary(self) -> dict[MetricEnum, float]:
        """
        모든 효과의 요약을 반환합니다.

        Returns:
            dict[MetricEnum, float]: 지표별 효과 값의 합계
        """
        summary: dict[MetricEnum, float] = {}
        for effect in self.effects:
            if effect.metric not in summary:
                summary[effect.metric] = 0.0
            summary[effect.metric] += effect.value
        return summary

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

    def get_category_description(self) -> str:
        """
        카테고리 설명을 반환합니다.

        Returns:
            str: 카테고리의 한글 설명
        """
        return {
            PatternCategory.GROWTH: "성장",
            PatternCategory.DECLINE: "쇠퇴",
            PatternCategory.CRISIS: "위기",
            PatternCategory.RECOVERY: "회복",
            PatternCategory.STAGNATION: "정체",
        }[self.category]

    def to_dict(self) -> dict:
        """
        패턴을 딕셔너리로 변환합니다.

        Returns:
            dict: 패턴의 모든 정보를 담은 딕셔너리
        """
        return {
            "pattern_id": self.pattern_id,
            "name_ko": self.name_ko,
            "name_en": self.name_en,
            "description_ko": self.description_ko,
            "description_en": self.description_en,
            "category": self.category.value,
            "severity": self.severity,
            "trigger": {
                "metric": self.trigger.metric.name,
                "threshold": self.trigger.threshold,
                "comparison": self.trigger.comparison,
                "secondary_value": self.trigger.secondary_value,
            },
            "effects": [
                {
                    "metric": effect.metric.name,
                    "value": effect.value,
                    "is_multiplier": effect.is_multiplier,
                }
                for effect in self.effects
            ],
            "related_metrics": [metric.name for metric in self.related_metrics],
            "tags": self.tags,
            "cooldown": self.cooldown,
            "probability": self.probability,
        }

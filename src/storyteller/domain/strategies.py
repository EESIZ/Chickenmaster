from typing import Protocol
import random

from game_constants import Metric, StorytellerConstants
from src.storyteller.domain.models import StoryContext, StoryPattern


class IStateEvaluator(Protocol):
    """상태 평가를 위한 전략 인터페이스"""

    def evaluate(self, metrics: dict[str, float]) -> str:
        """현재 상태를 평가하여 'positive', 'negative', 'neutral' 중 하나를 반환"""
        ...


class ITrendAnalyzer(Protocol):
    """추세 분석을 위한 전략 인터페이스"""

    def analyze(self, context: StoryContext) -> dict[str, float]:
        """메트릭 히스토리를 분석하여 추세를 계산"""
        ...


class IPatternSelector(Protocol):
    """스토리 패턴 선택을 위한 전략 인터페이스"""

    def select(self, context: StoryContext, patterns: list[dict]) -> StoryPattern | None:
        """현재 상황에 가장 적합한 스토리 패턴을 선택"""
        ...


class DefaultStateEvaluator:
    """기본 상태 평가 전략"""

    def evaluate(self, metrics: dict[str, float]) -> str:
        money = metrics.get("money", 0)
        reputation = metrics.get("reputation", 0)
        happiness = metrics.get("happiness", 0)
        pain = metrics.get("pain", 0)

        # 각 지표별 점수 계산 (0~1 사이 값)
        money_score = min(1.0, money / 10000)
        reputation_score = reputation / 100
        happiness_score = happiness / 100
        pain_score = 1 - (pain / 100)  # 고통은 낮을수록 좋음

        overall_score = (money_score + reputation_score + happiness_score + pain_score) / 4

        if overall_score > StorytellerConstants.SCORE_THRESHOLD_HIGH:
            return "positive"
        elif overall_score < StorytellerConstants.SCORE_THRESHOLD_LOW:
            return "negative"
        else:
            return "neutral"


class LinearTrendAnalyzer:
    """선형 추세 분석 전략"""

    def analyze(self, context: StoryContext) -> dict[str, float]:
        if not context.metrics_history:
            raise ValueError(
                "메트릭 히스토리가 비어있습니다. 추세 분석을 위해서는 최소 1개의 히스토리가 필요합니다."
            )

        if len(context.metrics_history) < StorytellerConstants.TREND_MIN_HISTORY:
            raise ValueError("추세 분석을 위해서는 최소 2개의 지표 히스토리가 필요합니다.")

        trends = {}
        for metric in Metric:
            values = [
                history.get(metric, 0)
                for history in context.metrics_history[-StorytellerConstants.TREND_MIN_HISTORY :]
            ]

            if len(values) >= StorytellerConstants.TREND_MIN_HISTORY:
                trend_rate = self._calculate_linear_trend(values)
                trends[metric] = trend_rate

        return trends

    def _calculate_linear_trend(self, values: list[float]) -> float:
        """값들의 선형 추세 계산"""
        if len(values) < StorytellerConstants.TREND_MIN_HISTORY:
            return 0.0

        x = list(range(len(values)))
        y = values
        n = len(values)

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))

        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            return slope
        except ZeroDivisionError:
            return 0.0


class WeightedPatternSelector:
    """가중치 기반 패턴 선택 전략"""

    def select(self, context: StoryContext, patterns: list[dict]) -> StoryPattern | None:
        if not patterns:
            return None

        # 진행도 계산 (0~1 사이 값)
        progression = min(1.0, len(context.metrics_history) / 100)

        scored_patterns = []
        for pattern in patterns:
            score = 0.0

            # 조건 충족 여부 확인
            if not self._check_pattern_conditions(pattern, context.current_metrics):
                continue

            # 관련 이벤트 발생 여부로 점수 가산
            related_events = set(pattern["related_events"])
            recent_events = {event.event_id for event in context.recent_events}
            event_overlap = len(related_events & recent_events)
            score += 0.2 * event_overlap

            # 진행도에 따른 복잡성 보너스
            complexity_bonus = 0.0
            if progression > StorytellerConstants.PROGRESSION_THRESHOLD:
                if pattern["pattern_type"] in ["dilemma", "noRightAnswer"]:
                    complexity_bonus = StorytellerConstants.COMPLEXITY_BONUS_THRESHOLD * progression
            score += complexity_bonus

            scored_patterns.append((pattern, score))

        if not scored_patterns:
            return None

        # 점수가 비슷한 패턴들 중에서 랜덤 선택
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        current_score = scored_patterns[0][1]
        current_score_group = []

        for pattern, score in scored_patterns:
            if (
                current_score is None
                or abs(score - current_score) < StorytellerConstants.PATTERN_SCORE_SIMILARITY
            ):
                current_score_group.append(pattern)
            else:
                break

        if not current_score_group:
            return None

        selected_pattern = random.choice(current_score_group)
        return StoryPattern(
            pattern_id=selected_pattern["pattern_id"],
            name=selected_pattern["name"],
            narrative_template=selected_pattern["narrative_template"],
            pattern_type=selected_pattern["pattern_type"],
        )

    def _check_pattern_conditions(self, pattern: dict, metrics: dict[str, float]) -> bool:
        """패턴의 발동 조건 검사"""
        conditions = pattern.get("trigger_conditions", {})
        for metric, threshold in conditions.items():
            current_value = metrics.get(metric, 0)
            if current_value < threshold:
                return False
        return True

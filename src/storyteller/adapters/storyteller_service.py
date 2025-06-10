"""
스토리텔러 서비스 구현체.

이 모듈은 스토리텔러 서비스의 실제 구현을 제공합니다.
게임의 핵심 철학인 tradeoff, uncertainty, noRightAnswer를 반영하여
내러티브를 생성하고 이벤트를 제안합니다.
"""

import random
from typing import ClassVar

from src.core.ports.container_port import IServiceContainer
from src.core.ports.event_port import IEventService
from src.core.domain.game_state import GameState
from src.storyteller.ports.storyteller_port import IStorytellerService
from src.storyteller.domain.models import StoryContext, NarrativeResponse, StoryPattern
from game_constants import (
    Metric,
    UNCERTAINTY_WEIGHTS,
    PROBABILITY_LOW_THRESHOLD,
    PROBABILITY_HIGH_THRESHOLD,
    MIN_METRICS_HISTORY_FOR_TREND,
    RECENT_HISTORY_WINDOW,
    SITUATION_POSITIVE_THRESHOLD,
    SITUATION_NEGATIVE_THRESHOLD,
    MONEY_LOW_THRESHOLD,
    MONEY_HIGH_THRESHOLD,
    REPUTATION_LOW_THRESHOLD,
    REPUTATION_HIGH_THRESHOLD,
    HAPPINESS_LOW_THRESHOLD,
    HAPPINESS_HIGH_THRESHOLD,
    TRADEOFF_BALANCE_THRESHOLD,
    GAME_PROGRESSION_MID_POINT,
    PATTERN_SCORE_TOLERANCE,
    COMPLEXITY_BONUS_MULTIPLIER,
)


class StorytellerService(IStorytellerService):
    """스토리텔러 서비스 구현체."""

    # 스토리 패턴 상수 - 하드코딩 방지를 위한 중앙화된 관리
    _NARRATIVE_TEMPLATES: ClassVar[dict[str, dict[str, str]]] = {
        "early_game": {
            "positive": "치킨집을 시작한 지 얼마 되지 않았지만, {metric_status}. 하지만 이 업계에서는 언제나 예상치 못한 일들이 기다리고 있습니다.",
            "negative": "창업 초기의 어려움이 계속되고 있습니다. {metric_status}. 그러나 모든 선택에는 득과 실이 있으니, 포기하지 마세요.",
            "neutral": "치킨집 운영이 궤도에 오르고 있습니다. {metric_status}. 앞으로의 선택이 운명을 좌우할 것입니다.",
        },
        "mid_game": {
            "positive": "사업이 안정화되어 가고 있습니다. {metric_status}. 하지만 성공에는 항상 새로운 도전이 따라옵니다.",
            "negative": "예상치 못한 어려움들이 연이어 발생하고 있습니다. {metric_status}. 이런 불확실성이야말로 이 사업의 본질입니다.",
            "neutral": "평범한 하루가 지나가고 있습니다. {metric_status}. 하지만 평범함 속에도 변화의 씨앗이 숨어있을지 모릅니다.",
        },
        "late_game": {
            "positive": "오랜 경험이 쌓여 노련함을 보이고 있습니다. {metric_status}. 그러나 경험이 많다고 해서 모든 것을 예측할 수 있는 것은 아닙니다.",
            "negative": "긴 여정 끝에 피로가 쌓여가고 있습니다. {metric_status}. 때로는 후퇴가 전진을 위한 준비일 수도 있습니다.",
            "neutral": "베테랑의 여유로 하루를 보내고 있습니다. {metric_status}. 하지만 안주는 곧 쇠퇴의 시작일 수 있습니다.",
        },
    }

    _STORY_PATTERNS_CONFIG: ClassVar[list[dict]] = [
        {
            "pattern_id": "financial_crisis_tradeoff",
            "name": "재정 위기의 트레이드오프",
            "trigger_conditions": {"money": 5000},  # 돈이 5000 이하일 때
            "related_events": ["cost_reduction", "emergency_loan", "price_increase"],
            "narrative_template": "자금 부족으로 어려운 선택을 해야 합니다. 비용을 줄이면 품질이 떨어지고, 가격을 올리면 고객이 떠날 수 있습니다.",
            "pattern_type": "tradeoff",  # crisis에서 tradeoff로 변경
        },
        {
            "pattern_id": "reputation_uncertainty",
            "name": "평판의 불확실성",
            "trigger_conditions": {"reputation": 70},  # 평판이 70 이상일 때
            "related_events": ["viral_review", "competitor_attack", "media_attention"],
            "narrative_template": "높은 평판은 축복이자 저주입니다. 더 많은 관심을 받지만, 그만큼 실수에 대한 대가도 큽니다.",
            "pattern_type": "opportunity_risk",
        },
        {
            "pattern_id": "happiness_suffering_balance",
            "name": "행복과 고통의 균형",
            "trigger_conditions": {"happiness": 80, "pain": 20},  # 행복이 높고 고통이 낮을 때
            "related_events": ["complacency_risk", "motivation_loss", "unexpected_challenge"],
            "narrative_template": "너무 편안한 상황은 경계심을 잃게 만듭니다. 행복한 순간일수록 예상치 못한 시련이 기다릴 수 있습니다.",
            "pattern_type": "balance",
        },
        {
            "pattern_id": "noRightAnswer_dilemma",
            "name": "정답 없는 딜레마",
            "trigger_conditions": {
                "reputation": 30,
                "money": 3000,
            },  # 중간 수준일 때 (더 낮은 임계값)
            "related_events": ["ethical_choice", "business_vs_morality", "customer_complaint"],
            "narrative_template": "모든 선택에는 대가가 따릅니다. 옳은 답은 없고, 오직 각자의 가치관에 따른 선택만이 있을 뿐입니다.",
            "pattern_type": "dilemma",
        },
    ]

    def __init__(self, container: IServiceContainer):
        """
        스토리텔러 서비스를 초기화합니다.

        Args:
            container: 의존성 주입 컨테이너
        """
        self._container = container
        self._event_service = container.get(IEventService)

        # 스토리 패턴 초기화 - 설정 기반으로 생성
        self._story_patterns = [
            StoryPattern(
                pattern_id=config["pattern_id"],
                name=config["name"],
                trigger_conditions=config["trigger_conditions"],
                related_events=config["related_events"],
                narrative_template=config["narrative_template"],
                pattern_type=config["pattern_type"],
            )
            for config in self._STORY_PATTERNS_CONFIG
        ]

    def generate_narrative(self, context: StoryContext) -> NarrativeResponse:
        """
        현재 게임 상태에 맞는 내러티브를 생성합니다.

        게임의 핵심 철학을 반영하여:
        - tradeoff: 모든 상황의 양면성을 강조
        - uncertainty: 예측 불가능한 요소들을 언급
        - noRightAnswer: 정답 없는 선택의 어려움을 표현
        """
        # 예외 처리: 컨텍스트 검증
        if not context:
            raise ValueError("StoryContext가 제공되지 않았습니다.")

        try:
            if not context.metrics_history:
                # 초기 상태일 때의 기본 내러티브 (날짜 정보 포함)
                narrative = f"{context.day}일차: 치킨집 사장으로서의 새로운 여정이 시작됩니다. 앞으로의 모든 선택이 당신의 운명을 결정할 것입니다."
                return NarrativeResponse(narrative=narrative)

            # 게임 진행도에 따른 템플릿 선택
            game_phase = self._determine_game_phase(context.game_progression)

            # 현재 상황 분석
            current_metrics = context.metrics_history[-1].metrics
            if not current_metrics:
                raise ValueError("현재 메트릭이 비어있습니다.")

            situation_tone = self._analyze_situation_tone(current_metrics)

            # 지표 상태 설명 생성
            metric_status = self._generate_metric_status_description(current_metrics)

            # 적용 가능한 스토리 패턴 찾기
            applicable_patterns = self.get_story_patterns(context)
            applied_pattern = applicable_patterns[0] if applicable_patterns else None

            # 내러티브 템플릿 선택 및 생성 (날짜 정보 포함)
            template = self._NARRATIVE_TEMPLATES[game_phase][situation_tone]
            narrative = f"{context.day}일차: " + template.format(metric_status=metric_status)

            # 패턴이 적용된 경우 추가 내러티브
            if applied_pattern:
                narrative += f" {applied_pattern.narrative_template}"

            return NarrativeResponse(narrative=narrative, applied_pattern=applied_pattern)

        except Exception:
            # 예외 발생 시 기본 내러티브 반환 (날짜 정보 포함)
            return NarrativeResponse(
                narrative=f"{context.day}일차: 치킨집 운영은 예측할 수 없는 여정입니다. 매 순간이 새로운 선택의 기회입니다."
            )

    def suggest_event(self, context: StoryContext) -> str | None:
        """
        현재 상황에 적절한 이벤트를 제안합니다.

        uncertainty 원칙에 따라 예측 불가능한 요소를 고려하여
        상황에 맞는 이벤트를 제안합니다.
        """
        # 예외 처리: 컨텍스트 검증
        if not context:
            raise ValueError("StoryContext가 제공되지 않았습니다.")

        try:
            if not context.metrics_history:
                return None

            current_metrics = context.metrics_history[-1].metrics
            if not current_metrics:
                raise ValueError("현재 메트릭이 비어있습니다.")

            # GameState로 변환하여 이벤트 서비스 호출
            game_state = self._convert_to_game_state(context)

            # 이벤트 서비스에서 사용 가능한 이벤트 조회
            available_events = self._event_service.get_applicable_events(game_state)

            if not available_events:
                return None

            # Event 객체에서 ID 추출
            event_ids = [event.id for event in available_events]

            # 최근 발생한 이벤트 필터링 (uncertainty 고려)
            recent_event_ids = {event.event_id for event in context.recent_events[-5:]}
            filtered_event_ids = [
                event_id for event_id in event_ids if event_id not in recent_event_ids
            ]

            # 필터링 후 이벤트가 없으면 원본 리스트 사용
            if not filtered_event_ids:
                filtered_event_ids = event_ids

            # uncertainty 원칙에 따라 랜덤 요소 추가
            return random.choice(filtered_event_ids)

        except Exception:
            # 예외 발생 시 None 반환 (이벤트 제안 없음)
            return None

    def analyze_metrics_trend(self, context: StoryContext) -> dict[str, float]:
        """
        지표 변화 추세를 분석합니다.

        tradeoff 관계를 고려하여 각 지표의 변화 추세를 계산하고,
        uncertainty 요소로 인한 예측 불확실성을 반영합니다.
        """
        # 예외 처리: 메트릭 히스토리 검증
        if not context or not context.metrics_history:
            raise ValueError(
                "메트릭 히스토리가 비어있습니다. 추세 분석을 위해서는 최소 1개의 히스토리가 필요합니다."
            )

        if len(context.metrics_history) < MIN_METRICS_HISTORY_FOR_TREND:
            raise ValueError("추세 분석을 위해서는 최소 2개의 지표 히스토리가 필요합니다.")

        try:
            trends = {}
            recent_history = context.metrics_history[
                -RECENT_HISTORY_WINDOW:
            ]  # 최근 3개 데이터 포인트 사용

            for metric in Metric:
                metric_name = metric.name.lower()

                # 지표별 변화율 계산
                values = [history.metrics.get(metric_name, 0) for history in recent_history]

                if len(values) >= MIN_METRICS_HISTORY_FOR_TREND:
                    # 선형 추세 계산
                    trend_rate = self._calculate_linear_trend(values)

                    # uncertainty 가중치 적용
                    uncertainty_factor = UNCERTAINTY_WEIGHTS.get(metric, 0.0)
                    adjusted_trend = trend_rate * (
                        1 + uncertainty_factor * random.uniform(-0.5, 0.5)
                    )

                    trends[metric_name] = round(adjusted_trend, 3)
                else:
                    trends[metric_name] = 0.0

            return trends

        except Exception:
            # 예외 발생 시 기본 추세 반환 (모든 지표 0.0)
            return {metric.name.lower(): 0.0 for metric in Metric}

    def get_story_patterns(self, context: StoryContext) -> list[StoryPattern]:
        """
        현재 상황에 적용 가능한 스토리 패턴을 반환합니다.

        noRightAnswer 철학에 따라 각 상황에 맞는 딜레마와
        선택의 어려움을 표현하는 패턴들을 제공합니다.
        """
        # 예외 처리: 컨텍스트 검증
        if not context:
            raise ValueError("StoryContext가 제공되지 않았습니다.")

        if not context.metrics_history:
            raise ValueError("지표 히스토리가 비어있습니다.")

        try:
            current_metrics = context.metrics_history[-1].metrics
            if not current_metrics:
                return []

            applicable_patterns = []

            for pattern in self._story_patterns:
                if pattern.matches(current_metrics):
                    applicable_patterns.append(pattern)

            # 게임 진행도에 따른 우선순위 적용
            prioritized_patterns = self._prioritize_patterns_by_progression(
                applicable_patterns, context.game_progression
            )

            return prioritized_patterns

        except Exception:
            # 예외 발생 시 빈 리스트 반환
            return []

    def _determine_game_phase(self, progression: float) -> str:
        """게임 진행도에 따른 단계 결정"""
        if progression < PROBABILITY_LOW_THRESHOLD:
            return "early_game"
        elif progression < PROBABILITY_HIGH_THRESHOLD:
            return "mid_game"
        else:
            return "late_game"

    def _analyze_situation_tone(self, metrics: dict[str, float]) -> str:
        """현재 상황의 톤 분석 (positive/negative/neutral)"""
        # 핵심 지표들의 가중 평균으로 상황 판단
        money_score = min(metrics.get("money", 0) / 10000, 1.0)  # 정규화
        reputation_score = metrics.get("reputation", 0) / 100
        happiness_score = metrics.get("happiness", 0) / 100
        pain_score = 1 - (metrics.get("pain", 0) / 100)  # 고통은 역산

        overall_score = (money_score + reputation_score + happiness_score + pain_score) / 4

        if overall_score > SITUATION_POSITIVE_THRESHOLD:
            return "positive"
        elif overall_score < SITUATION_NEGATIVE_THRESHOLD:
            return "negative"
        else:
            return "neutral"

    def _generate_metric_status_description(self, metrics: dict[str, float]) -> str:
        """지표 상태에 대한 설명 생성"""
        descriptions = []

        money = metrics.get("money", 0)
        reputation = metrics.get("reputation", 0)
        happiness = metrics.get("happiness", 0)

        if money < MONEY_LOW_THRESHOLD:
            descriptions.append("자금 상황이 어려워지고 있습니다")
        elif money > MONEY_HIGH_THRESHOLD:
            descriptions.append("재정 상태가 안정적입니다")

        if reputation < REPUTATION_LOW_THRESHOLD:
            descriptions.append("평판에 문제가 생겼습니다")
        elif reputation > REPUTATION_HIGH_THRESHOLD:
            descriptions.append("좋은 평판을 얻고 있습니다")

        if happiness < HAPPINESS_LOW_THRESHOLD:
            descriptions.append("스트레스가 쌓이고 있습니다")
        elif happiness > HAPPINESS_HIGH_THRESHOLD:
            descriptions.append("만족스러운 하루를 보내고 있습니다")

        if not descriptions:
            descriptions.append("평범한 하루가 지나가고 있습니다")

        return ", ".join(descriptions)

    def _convert_to_game_state(self, context: StoryContext) -> GameState:
        """StoryContext를 GameState로 변환"""
        if not context.metrics_history:
            # 기본값으로 초기 상태 생성
            return GameState(money=10000, reputation=50, happiness=50, pain=50, day=context.day)

        current_metrics = context.metrics_history[-1].metrics
        recent_event_ids = tuple(event.event_id for event in context.recent_events[-10:])

        return GameState(
            money=int(current_metrics.get("money", 10000)),
            reputation=int(current_metrics.get("reputation", 50)),
            happiness=int(current_metrics.get("happiness", 50)),
            pain=int(current_metrics.get("pain", 50)),
            day=context.day,
            events_history=recent_event_ids,
        )

    def _select_most_appropriate_event(self, events, current_metrics, recent_events):
        """현재 상황에 가장 적합한 이벤트 선택"""
        if not events:
            return None

        # 최근 발생한 이벤트는 제외 (중복 방지)
        recent_event_ids = {event.event_id for event in recent_events[-5:]}
        available_events = [e for e in events if e.id not in recent_event_ids]

        if not available_events:
            return events[0]  # 모든 이벤트가 최근 발생했다면 첫 번째 반환

        # uncertainty 원칙에 따라 랜덤 요소 추가
        return random.choice(available_events)

    def _calculate_linear_trend(self, values: list[float]) -> float:
        """값들의 선형 추세 계산"""
        if len(values) < MIN_METRICS_HISTORY_FOR_TREND:
            return 0.0

        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))

        # 선형 회귀의 기울기 계산
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0

        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return slope

    def _identify_critical_metrics(self, metrics: dict[str, float]) -> list[str]:
        """
        현재 지표들을 분석하여 중요한(위험하거나 기회가 되는) 지표들을 식별합니다.

        tradeoff 철학에 따라 각 지표의 임계점을 고려하여
        즉각적인 주의가 필요한 지표들을 반환합니다.

        Args:
            metrics: 현재 게임 지표들

        Returns:
            중요한 지표들의 이름 리스트
        """
        critical_metrics = []

        # 각 지표별 임계점 정의 (game_constants 활용)
        critical_thresholds = {
            "money": {"low": 3000, "high": 20000},  # 자금 부족/풍부
            "reputation": {"low": 30, "high": 80},  # 평판 위기/우수
            "happiness": {"low": 25, "high": 85},  # 스트레스/만족
            "pain": {"low": 15, "high": 75},  # 편안함/고통 (역방향)
        }

        for metric_name, value in metrics.items():
            if metric_name not in critical_thresholds:
                continue

            thresholds = critical_thresholds[metric_name]

            # 위험 수준 판단
            if metric_name == "pain":
                # pain은 높을수록 나쁨 (역방향)
                if value >= thresholds["high"]:
                    critical_metrics.append(metric_name)
                elif value <= thresholds["low"]:
                    critical_metrics.append(metric_name)  # 너무 낮은 고통도 위험할 수 있음
            # 일반 지표들 (높을수록 좋음)
            elif value <= thresholds["low"]:
                critical_metrics.append(metric_name)  # 위험 수준
            elif value >= thresholds["high"]:
                critical_metrics.append(metric_name)  # 기회 수준

        # tradeoff 관계 고려 - 연관된 지표들의 불균형 체크
        if "money" in metrics and "reputation" in metrics:
            money_ratio = metrics["money"] / 15000  # 정규화
            reputation_ratio = metrics["reputation"] / 100

            # 돈은 많지만 평판이 낮거나, 평판은 높지만 돈이 없는 경우
            if abs(money_ratio - reputation_ratio) > TRADEOFF_BALANCE_THRESHOLD:
                if "money" not in critical_metrics:
                    critical_metrics.append("money")
                if "reputation" not in critical_metrics:
                    critical_metrics.append("reputation")

        if "happiness" in metrics and "pain" in metrics:
            happiness_ratio = metrics["happiness"] / 100
            pain_ratio = metrics["pain"] / 100

            # 행복과 고통의 불균형 (둘 다 높거나 둘 다 낮은 경우)
            if (
                happiness_ratio > PROBABILITY_HIGH_THRESHOLD
                and pain_ratio > PROBABILITY_HIGH_THRESHOLD
            ) or (
                happiness_ratio < PROBABILITY_LOW_THRESHOLD
                and pain_ratio < PROBABILITY_LOW_THRESHOLD
            ):
                if "happiness" not in critical_metrics:
                    critical_metrics.append("happiness")
                if "pain" not in critical_metrics:
                    critical_metrics.append("pain")

        return critical_metrics

    def _prioritize_patterns_by_progression(
        self, patterns: list[StoryPattern], progression: float
    ) -> list[StoryPattern]:
        """
        게임 진행도에 따라 스토리 패턴의 우선순위를 정합니다.

        noRightAnswer 철학에 따라 게임 단계별로 적절한 딜레마와
        선택의 복잡성을 점진적으로 증가시킵니다.

        Args:
            patterns: 우선순위를 정할 패턴 리스트
            progression: 게임 진행도 (0.0 ~ 1.0)

        Returns:
            우선순위가 적용된 패턴 리스트
        """
        if not patterns:
            return []

        # 게임 진행도별 패턴 타입 우선순위 정의
        progression_priorities = {
            # 초기 게임 (0.0 ~ PROBABILITY_LOW_THRESHOLD): uncertainty 중심
            "early": {
                "uncertainty": 1.0,
                "tradeoff": PROBABILITY_HIGH_THRESHOLD,
                "crisis": 0.8,
                "opportunity_risk": 0.6,
                "balance": 0.4,
                "dilemma": PROBABILITY_LOW_THRESHOLD,
                "noRightAnswer": 0.2,
            },
            # 중기 게임 (PROBABILITY_LOW_THRESHOLD ~ PROBABILITY_HIGH_THRESHOLD): tradeoff 중심
            "mid": {
                "tradeoff": 1.0,
                "crisis": 0.9,
                "uncertainty": 0.8,
                "dilemma": PROBABILITY_HIGH_THRESHOLD,
                "opportunity_risk": 0.6,
                "balance": 0.5,
                "noRightAnswer": 0.8,
            },
            # 후기 게임 (PROBABILITY_HIGH_THRESHOLD ~ 1.0): noRightAnswer 중심
            "late": {
                "noRightAnswer": 1.0,
                "dilemma": 0.9,
                "tradeoff": 0.8,
                "balance": PROBABILITY_HIGH_THRESHOLD,
                "crisis": 0.6,
                "opportunity_risk": 0.5,
                "uncertainty": 0.4,
            },
        }

        # 현재 진행도에 따른 단계 결정
        if progression < PROBABILITY_LOW_THRESHOLD:
            current_priorities = progression_priorities["early"]
        elif progression < PROBABILITY_HIGH_THRESHOLD:
            current_priorities = progression_priorities["mid"]
        else:
            current_priorities = progression_priorities["late"]

        # 패턴별 우선순위 점수 계산
        scored_patterns = []
        for pattern in patterns:
            # 기본 우선순위 점수
            base_score = current_priorities.get(pattern.pattern_type, 0.5)

            # 패턴 ID에서 철학 키워드 추출하여 추가 점수 부여
            philosophy_bonus = 0.0
            pattern_id_lower = pattern.pattern_id.lower()

            if "uncertainty" in pattern_id_lower:
                philosophy_bonus += current_priorities.get("uncertainty", 0.0) * 0.2
            if "tradeoff" in pattern_id_lower:
                philosophy_bonus += current_priorities.get("tradeoff", 0.0) * 0.2
            if "norightanswer" in pattern_id_lower or "dilemma" in pattern_id_lower:
                philosophy_bonus += current_priorities.get("noRightAnswer", 0.0) * 0.2

            # 진행도에 따른 복잡성 보너스
            complexity_bonus = 0.0
            if progression > GAME_PROGRESSION_MID_POINT:  # 중후반부에는 복잡한 패턴 선호
                if pattern.pattern_type in ["dilemma", "noRightAnswer"]:
                    complexity_bonus = COMPLEXITY_BONUS_MULTIPLIER * progression

            # 최종 점수 계산
            final_score = base_score + philosophy_bonus + complexity_bonus

            scored_patterns.append((pattern, final_score))

        # 점수 기준으로 내림차순 정렬
        scored_patterns.sort(key=lambda x: x[1], reverse=True)

        # uncertainty 원칙 적용 - 동일한 점수대의 패턴들은 랜덤하게 섞기
        result_patterns = []
        current_score_group = []
        current_score = None

        for pattern, score in scored_patterns:
            if current_score is None or abs(score - current_score) < PATTERN_SCORE_TOLERANCE:
                # 같은 점수 그룹
                current_score_group.append(pattern)
                current_score = score
            else:
                # 새로운 점수 그룹 시작
                if current_score_group:
                    random.shuffle(current_score_group)  # uncertainty 적용
                    result_patterns.extend(current_score_group)

                current_score_group = [pattern]
                current_score = score

        # 마지막 그룹 처리
        if current_score_group:
            random.shuffle(current_score_group)
            result_patterns.extend(current_score_group)

        return result_patterns

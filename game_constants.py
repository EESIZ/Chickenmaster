"""
Chicken-RNG 게임의 핵심 지표와 상수를 정의하는 모듈

이 모듈은 게임의 모든 지표와 상수를 중앙화하여 관리합니다.
모든 다른 모듈은 이 파일을 import하여 일관된 값을 사용해야 합니다.

핵심 철학:
- 정답 없음: 모든 선택은 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 올리면 다른 지표는 내려갑니다
- 불확실성: 예측 불가능한 이벤트가 게임 진행에 영향을 줍니다
"""

from enum import Enum, auto
from typing import Final
from dataclasses import dataclass

# 무한대 값을 위한 타입 힌트 호환 상수
INF: Final = float("inf")


class Metric(Enum):
    """
    게임의 핵심 지표를 정의하는 열거형

    각 지표는 트레이드오프 관계에 있으며, 하나를 개선하면 다른 하나는 악화됩니다.
    불확실성 요소로 인해 예상치 못한 변화가 발생할 수 있습니다.
    """

    MONEY = auto()  # 사업 운영 자금
    REPUTATION = auto()  # 가게의 사회적 평가
    HAPPINESS = auto()  # 사장의 정신적 만족도
    SUFFERING = auto()  # 사장의 정신적 스트레스
    INVENTORY = auto()  # 보유 식자재 수량
    STAFF_FATIGUE = auto()  # 직원의 피로도
    FACILITY = auto()  # 시설 상태
    DEMAND = auto()  # 고객 수요


class ActionType(Enum):
    """
    플레이어가 선택할 수 있는 행동 유형

    각 행동은 noRightAnswer 원칙에 따라 항상 득과 실을 동시에 가져옵니다.
    """

    PRICE_CHANGE = auto()  # 가격 조정
    ORDER_INVENTORY = auto()  # 재고 주문
    MANAGE_STAFF = auto()  # 직원 관리
    PROMOTE = auto()  # 홍보 활동
    INVEST_FACILITY = auto()  # 시설 투자
    HEDGE_RISK = auto()  # 헤지 전략


class EventType(Enum):
    """
    게임에서 발생할 수 있는 랜덤 이벤트 유형

    불확실성 원칙에 따라 이벤트는 예측 불가능하게 발생하며,
    완벽한 대비는 불가능합니다.
    """

    FOOD_POISONING = auto()  # 식중독 발생
    INSPECTION = auto()  # 위생 단속
    COST_SURGE = auto()  # 원가 폭등
    COMPETITOR_ACTION = auto()  # 경쟁자 행동
    VIRAL_MARKETING = auto()  # 바이럴 마케팅
    STAFF_ISSUE = auto()  # 직원 문제
    FACILITY_BREAKDOWN = auto()  # 시설 고장
    POSITIVE_REVIEW = auto()  # 긍정적 리뷰
    NEGATIVE_REVIEW = auto()  # 부정적 리뷰
    RANDOM_OPPORTUNITY = auto()  # 우연한 기회


# 지표 범위 정의 (최소값, 최대값, 초기값)
METRIC_RANGES: Final[dict[Metric, tuple[int, int | float, int]]] = {
    Metric.MONEY: (0, INF, 10000),  # 음수 불가, 무한대 가능
    Metric.REPUTATION: (0, 100, 50),  # 0-100 범위
    Metric.HAPPINESS: (0, 100, 50),  # 0-100 범위
    Metric.SUFFERING: (0, 100, 50),  # 0-100 범위
    Metric.INVENTORY: (0, INF, 100),  # 음수 불가, 무한대 가능
    Metric.STAFF_FATIGUE: (0, 100, 30),  # 0-100 범위
    Metric.FACILITY: (0, 100, 80),  # 0-100 범위
    Metric.DEMAND: (0, 100, 70),  # 0-100 범위
}


# 트레이드오프 관계 정의 (상승 시 하락하는 지표들)
TRADEOFF_RELATIONSHIPS: Final[dict[Metric, list[Metric]]] = {
    Metric.MONEY: [Metric.REPUTATION, Metric.HAPPINESS],
    Metric.REPUTATION: [Metric.MONEY, Metric.STAFF_FATIGUE],
    Metric.HAPPINESS: [Metric.SUFFERING],
    Metric.SUFFERING: [Metric.HAPPINESS],
    Metric.INVENTORY: [Metric.MONEY],
    Metric.STAFF_FATIGUE: [Metric.REPUTATION, Metric.FACILITY],
    Metric.FACILITY: [Metric.MONEY],
    Metric.DEMAND: [Metric.INVENTORY, Metric.STAFF_FATIGUE],
}


# 불확실성 요소 가중치 (높을수록 예측 불가능한 이벤트 발생 확률 증가)
UNCERTAINTY_WEIGHTS: Final[dict[Metric, float]] = {
    Metric.MONEY: 0.3,  # 돈이 많을수록 위험 증가
    Metric.REPUTATION: 0.25,  # 평판이 높을수록 기대치 상승
    Metric.HAPPINESS: -0.1,  # 행복이 높을수록 위험 감소
    Metric.SUFFERING: 0.2,  # 고통이 높을수록 위험 증가
    Metric.INVENTORY: 0.05,  # 재고가 많을수록 약간 위험
    Metric.STAFF_FATIGUE: 0.15,  # 직원 피로도가 높을수록 위험
    Metric.FACILITY: -0.2,  # 시설 상태가 좋을수록 위험 감소
    Metric.DEMAND: 0.1,  # 수요가 높을수록 약간 위험
}


# 게임 진행 관련 상수
MAX_ACTIONS_PER_DAY: Final[int] = 3  # 하루 최대 행동 횟수
GAME_OVER_CONDITIONS: Final[dict[str, str]] = {
    "위생 단속 실패": "INSPECTION 이벤트 발생 시 FACILITY < 30이면 게임 오버",
    "파산": "MONEY가 0 이하이고 추가 대출이 불가능한 경우",
}
DEFAULT_GAME_LENGTH: Final[int] = 30  # 기본 게임 길이 (일)

# 부동소수점 비교 관련 상수
FLOAT_EPSILON: Final[float] = 0.001  # 부동소수점 비교 오차 허용 범위

# 평판 관련 상수
REPUTATION_BASELINE: Final[int] = 50  # 평판 기준점

# 점수 임계값 상수
SCORE_THRESHOLD_HIGH: Final[float] = 0.7  # 높은 점수 임계값
SCORE_THRESHOLD_MEDIUM: Final[float] = 0.5  # 중간 점수 임계값

# 테스트 관련 상수
TEST_MIN_CASCADE_EVENTS: Final[int] = 3  # 최소 연쇄 효과 메시지 수
TEST_EXPECTED_EVENTS: Final[int] = 2  # 예상 이벤트 수
TEST_METRICS_HISTORY_LENGTH: Final[int] = 5  # 메트릭 히스토리 길이
TEST_POSSIBLE_OUTCOME: Final[int] = 3  # 가능한 결과값


@dataclass(frozen=True)
class ProbabilityConstants:
    """확률 관련 상수"""

    RANDOM_THRESHOLD: float = 0.5  # 50% 확률 기준점


def cap_metric_value(metric: Metric, value: float) -> float:
    """
    지표 값이 허용 범위를 벗어나지 않도록 보정합니다.

    불확실성 ≠ 불합리한 음수: 불확실성은 게임의 핵심이지만,
    물리적으로 불가능한 음수 재고나 음수 자금은 허용하지 않습니다.

    Args:
        metric: 보정할 지표
        value: 보정 전 값

    Returns:
        float: 보정된 값
    """
    min_val, max_val, _ = METRIC_RANGES[metric]

    # 최소값 보정 (음수 방지)
    value = max(value, min_val)

    # 최대값 보정 (범위 초과 방지)
    if max_val != INF and value > max_val:
        value = max_val

    return value


def are_happiness_suffering_balanced(happiness: float, suffering: float) -> bool:
    """
    행복과 고통의 합이 100인지 확인합니다.

    행복-고통 시소: 행복과 고통은 합이 항상 100으로 유지되는 트레이드오프 관계입니다.

    Args:
        happiness: 행복 지표 값
        suffering: 고통 지표 값

    Returns:
        bool: 행복과 고통의 합이 100인 경우 True
    """
    return abs((happiness + suffering) - 100) < FLOAT_EPSILON  # 부동소수점 오차 허용

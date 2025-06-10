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

# Magic numbers
MAGIC_NUMBER_ZERO = 0.0
MAGIC_NUMBER_ONE = 1.0
MAGIC_NUMBER_TWO = 2
MAGIC_NUMBER_THREE = 3
MAGIC_NUMBER_FIVE = 5
MAGIC_NUMBER_TWENTY = 20
MAGIC_NUMBER_FIFTY = 50
MAGIC_NUMBER_ONE_HUNDRED = 100
MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN = 115
MAGIC_NUMBER_ONE_THOUSAND = 1000

# 추가 상수들
MAX_CASCADE_NODES = 100  # 최대 연쇄 노드 수

# 확률 관련 상수
PROBABILITY_LOW_THRESHOLD = 0.3
PROBABILITY_HIGH_THRESHOLD = 0.7
PROBABILITY_HIGH_THRESHOLD5 = 0.75  # 높은 확률 임계값 5단계


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


class EventCategory(Enum):
    """이벤트 카테고리"""

    DAILY_ROUTINE = auto()  # 일상 루틴
    CRISIS = auto()  # 위기 상황
    OPPORTUNITY = auto()  # 기회
    RANDOM = auto()  # 랜덤 이벤트
    THRESHOLD = auto()  # 임계값 기반 이벤트
    SCHEDULED = auto()  # 스케줄 기반 이벤트
    CASCADE = auto()  # 연쇄 효과 이벤트


class TriggerCondition(Enum):
    """트리거 조건"""

    EQUAL = auto()  # 같음
    NOT_EQUAL = auto()  # 같지 않음
    GREATER_THAN = auto()  # 초과
    LESS_THAN = auto()  # 미만
    GREATER_THAN_OR_EQUAL = auto()  # 이상
    LESS_THAN_OR_EQUAL = auto()  # 이하


# 트레이드오프 관계 정의 (한 지표가 오르면 다른 지표는 내려감)
TRADEOFF_RELATIONSHIPS: Final[dict[Metric, list[Metric]]] = {
    Metric.MONEY: [Metric.HAPPINESS, Metric.STAFF_FATIGUE],
    Metric.REPUTATION: [
        Metric.MONEY,
        Metric.STAFF_FATIGUE,
    ],  # 평판 상승 시 직원 피로도 증가 (손님 증가로 인한)
    Metric.HAPPINESS: [Metric.SUFFERING],
    Metric.SUFFERING: [Metric.HAPPINESS],
    Metric.INVENTORY: [Metric.MONEY],
    Metric.STAFF_FATIGUE: [Metric.REPUTATION, Metric.FACILITY],
    Metric.FACILITY: [Metric.MONEY],
    Metric.DEMAND: [Metric.INVENTORY, Metric.STAFF_FATIGUE],
}


# 불확실성 요소 가중치 (높을수록 예측 불가능한 이벤트 발생 확률 증가)
UNCERTAINTY_WEIGHTS: Final[dict[Metric, float]] = {
    Metric.MONEY: PROBABILITY_LOW_THRESHOLD,  # 돈이 많을수록 위험 증가
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
SCORE_THRESHOLD_HIGH: Final[float] = PROBABILITY_HIGH_THRESHOLD  # 높은 점수 임계값
SCORE_THRESHOLD_MEDIUM: Final[float] = 0.5  # 중간 점수 임계값

# 테스트 관련 상수
TEST_MIN_CASCADE_EVENTS: Final[int] = 3  # 최소 연쇄 효과 메시지 수
TEST_EXPECTED_EVENTS: Final[int] = 2  # 예상 이벤트 수
TEST_METRICS_HISTORY_LENGTH: Final[int] = 5  # 메트릭 히스토리 길이
TEST_POSSIBLE_OUTCOME: Final[int] = 3  # 가능한 결과값

# 게임 기본값 상수
DEFAULT_TOTAL_DAYS: Final[int] = 730  # 기본 게임 총 일수 (2년)
DEFAULT_STORY_PATTERNS_COUNT: Final[int] = 2  # 기본 스토리 패턴 수
DEFAULT_COOLDOWN_DAYS: Final[int] = 5  # 기본 쿨다운 일수
DEFAULT_PROBABILITY: Final[float] = 0.8  # 기본 확률값
DEFAULT_SEVERITY: Final[float] = 0.5  # 기본 심각도

# 스토리텔러 관련 상수
MIN_METRICS_HISTORY_FOR_TREND: Final[int] = 2  # 추세 분석을 위한 최소 히스토리 개수
RECENT_HISTORY_WINDOW: Final[int] = 3  # 최근 히스토리 분석 윈도우 크기
MINIMUM_TREND_POINTS: Final[int] = 2  # 트렌드 분석에 필요한 최소 데이터 포인트

# 상황 톤 분석 임계값
SITUATION_POSITIVE_THRESHOLD: Final[float] = 0.6  # 긍정적 상황 판단 임계값
SITUATION_NEGATIVE_THRESHOLD: Final[float] = 0.4  # 부정적 상황 판단 임계값

# 지표 임계값들 (스토리텔러용)
MONEY_LOW_THRESHOLD: Final[int] = 3000  # 자금 부족 기준
MONEY_HIGH_THRESHOLD: Final[int] = 15000  # 자금 풍부 기준
REPUTATION_LOW_THRESHOLD: Final[int] = 30  # 평판 위험 기준
REPUTATION_HIGH_THRESHOLD: Final[int] = 70  # 평판 우수 기준
HAPPINESS_LOW_THRESHOLD: Final[int] = 30  # 행복 위험 기준
HAPPINESS_HIGH_THRESHOLD: Final[int] = 70  # 행복 우수 기준

# 패턴 우선순위 관련 상수
TRADEOFF_BALANCE_THRESHOLD: Final[float] = 0.5  # 트레이드오프 불균형 감지 임계값
GAME_PROGRESSION_MID_POINT: Final[float] = 0.5  # 게임 진행도 중간점
PATTERN_SCORE_TOLERANCE: Final[float] = 0.1  # 패턴 점수 허용 오차
COMPLEXITY_BONUS_MULTIPLIER: Final[float] = 0.1  # 복잡성 보너스 배수


@dataclass(frozen=True)
class ProbabilityConstants:
    """확률 관련 상수"""

    RANDOM_THRESHOLD: float = 0.5  # 50% 확률 기준점


# 지표 범위 정의 (최소값, 최대값, 기본값)
METRIC_RANGES: Final[dict[Metric, tuple[float, float, float]]] = {
    Metric.MONEY: (0.0, float("inf"), 10000.0),  # 돈은 0 이상, 기본 1만원
    Metric.REPUTATION: (0.0, 100.0, 50.0),  # 평판은 0-100, 기본 50
    Metric.HAPPINESS: (0.0, 100.0, 50.0),  # 행복도는 0-100, 기본 50
    Metric.SUFFERING: (0.0, 100.0, 20.0),  # 고통은 0-100, 기본 20
    Metric.INVENTORY: (0.0, float("inf"), 100.0),  # 재고는 0 이상, 기본 100
    Metric.STAFF_FATIGUE: (0.0, 100.0, 30.0),  # 직원 피로도는 0-100, 기본 30
    Metric.FACILITY: (0.0, 100.0, 80.0),  # 시설 상태는 0-100, 기본 80
    Metric.DEMAND: (0.0, float("inf"), 60.0),  # 수요는 0 이상, 기본 60
}


def cap_metric_value(metric: Metric, value: float) -> float:
    """
    지표 값을 허용 범위 내로 제한

    Args:
        metric: 지표 타입
        value: 제한할 값

    Returns:
        범위 내로 제한된 값
    """
    min_val, max_val, _ = METRIC_RANGES[metric]
    return max(min_val, min(max_val, value))

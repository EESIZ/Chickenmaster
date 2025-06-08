"""
게임 관련 상수 정의 모듈

이 모듈은 게임 전반에 걸쳐 사용되는 상수값들을 정의합니다.
각 상수는 명확한 의미와 용도를 가지고 있으며, 게임의 핵심 규칙과 제한사항을 정의합니다.
"""

from enum import Enum, auto
from typing import Final, NamedTuple, Dict, Tuple
from dataclasses import dataclass

class Metric(Enum):
    """
    게임의 핵심 지표를 정의하는 열거형
    """
    MONEY = auto()
    REPUTATION = auto()
    HAPPINESS = auto()
    SUFFERING = auto()
    INVENTORY = auto()
    STAFF_FATIGUE = auto()
    FACILITY = auto()
    DEMAND = auto()

# MetricRange 클래스를 Metric 바로 아래에 선언
class MetricRange(NamedTuple):
    min_value: float
    max_value: float
    default_value: float

# 확률 관련 상수 (상단에 위치)
PROBABILITY_LOW_THRESHOLD = 0.3
PROBABILITY_HIGH_THRESHOLD = 0.7
PROBABILITY_HIGH_THRESHOLD5 = 0.75  # 높은 확률 임계값 5단계
PROBABILITY_THRESHOLD = 0.5
UNCERTAINTY_FACTOR = 0.1

# 게임 진행 관련 상수
DAYS_PER_YEAR = 365  # 1년의 일수
GAME_DURATION_YEARS = 2  # 게임 진행 기간 (년)
TOTAL_GAME_DAYS = DAYS_PER_YEAR * GAME_DURATION_YEARS  # 총 게임 일수 (730일)

# 게임 단계 구분
EARLY_GAME_END = 180  # 초기 단계 종료 (약 6개월)
MID_GAME_END = 545   # 중반 단계 종료 (약 1년 6개월)

# 게임 진행 관련 상수
INITIAL_HEALTH = 100  # 초기 체력
MAX_HEALTH = 100      # 최대 체력
MIN_HEALTH = 0        # 최소 체력

# 전투 관련 상수
BASE_DAMAGE = 10      # 기본 데미지
CRITICAL_MULTIPLIER = 2.0  # 치명타 데미지 배율
DODGE_CHANCE = 0.2    # 회피 확률

# 아이템 관련 상수
MAX_INVENTORY_SIZE = 10  # 최대 인벤토리 크기
MAX_ITEM_QUANTITY = 99   # 최대 아이템 수량

# 스토리텔링 관련 상수
MAX_STORY_LENGTH = 1000  # 최대 스토리 길이
MIN_STORY_LENGTH = 100   # 최소 스토리 길이

# 임계값 상수
REPUTATION_THRESHOLD_LOW = 20
REPUTATION_THRESHOLD_HIGH = 80
FACILITY_THRESHOLD_LOW = 30
STAFF_FATIGUE_THRESHOLD_HIGH = 80
MONEY_THRESHOLD_LOW = 1000

# 영향력 상수
FATIGUE_IMPACT_FACTOR = 30
REPUTATION_IMPACT_FACTOR = 30
FACILITY_IMPACT_FACTOR = 40
MONEY_IMPACT_FACTOR = 1000

# Metric 기반 트레이드오프 관계 (한 지표가 오르면 반대 지표는 내려감)
TRADEOFF_RELATIONSHIPS = {
    Metric.MONEY: [Metric.REPUTATION, Metric.HAPPINESS],
    Metric.REPUTATION: [Metric.MONEY, Metric.STAFF_FATIGUE],
    Metric.HAPPINESS: [Metric.SUFFERING, Metric.STAFF_FATIGUE],
    Metric.SUFFERING: [Metric.HAPPINESS],
    Metric.DEMAND: [Metric.INVENTORY, Metric.STAFF_FATIGUE],
    Metric.INVENTORY: [Metric.MONEY],
    Metric.STAFF_FATIGUE: [Metric.REPUTATION, Metric.FACILITY],
    Metric.FACILITY: [Metric.MONEY],
}

# Metric 기반 불확실성 가중치 (지표별로 예측 불가능성 정도를 다르게 적용)
UNCERTAINTY_WEIGHTS = {
    Metric.MONEY: 0.2,           # 돈은 경제적 변수로 변동성 높음
    Metric.REPUTATION: 0.15,    # 평판은 소문 등으로 변동성 있음
    Metric.HAPPINESS: 0.1,      # 행복도는 비교적 안정적
    Metric.SUFFERING: 0.1,      # 고통도는 비교적 안정적
    Metric.DEMAND: 0.18,        # 수요는 시장 상황에 따라 변동
    Metric.INVENTORY: 0.12,     # 재고는 예측 가능성이 높음
    Metric.STAFF_FATIGUE: 0.16, # 피로도는 업무량에 따라 변동
    Metric.FACILITY: 0.08,      # 시설 상태는 비교적 안정적
}

# 시소 불변식
HAPPINESS_SUFFERING_SUM = 100.0

# 게임 진행 관련 상수
MAX_ACTIONS_PER_DAY: Final[int] = 3
GAME_OVER_CONDITIONS: Final[dict[str, str]] = {
    "위생 단속 실패": "INSPECTION 이벤트 발생 시 FACILITY < 30이면 게임 오버",
    "파산": "MONEY가 0 이하이고 추가 대출이 불가능한 경우",
}

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

# 테스트 및 서비스 코드에서 반복적으로 사용되는 매직 넘버 상수
TEST_ASSERT_MIN_LENGTH: Final[int] = 20
TEST_ASSERT_MONEY: Final[int] = 5000
TEST_ASSERT_REPUTATION: Final[int] = 75
TEST_ASSERT_MONEY_7000: Final[float] = 7000.0
TEST_ASSERT_MONEY_9000: Final[float] = 9000.0
TEST_ASSERT_MONEY_10000: Final[float] = 10000.0
TEST_ASSERT_MONEY_14000: Final[float] = 14000.0
TEST_ASSERT_FLOAT_04: Final[float] = 0.4
TEST_ASSERT_FLOAT_05: Final[float] = 0.5
TEST_ASSERT_FLOAT_06: Final[float] = 0.6
TEST_ASSERT_50: Final[int] = 50
TEST_ASSERT_70: Final[int] = 70

# 지표 범위 정의
METRIC_RANGES = {
    Metric.MONEY: MetricRange(0.0, 1000000.0, 10000.0),
    Metric.REPUTATION: MetricRange(0.0, 100.0, 50.0),
    Metric.HAPPINESS: MetricRange(0.0, 100.0, 50.0),
    Metric.SUFFERING: MetricRange(0.0, 100.0, 0.0),
    Metric.DEMAND: MetricRange(0.0, 100.0, 50.0),
    Metric.INVENTORY: MetricRange(0.0, 1000.0, 100.0),
    Metric.STAFF_FATIGUE: MetricRange(0.0, 100.0, 0.0),
    Metric.FACILITY: MetricRange(0.0, 100.0, 50.0),
}

def cap_metric_value(metric: Metric, value: float) -> float:
    """
    지표 값을 허용 범위 내로 제한합니다.
    Args:
        metric: 제한할 지표
        value: 제한할 값
    Returns:
        float: 제한된 값
    """
    min_val, max_val, _ = METRIC_RANGES[metric]
    return max(min_val, min(value, max_val))

# 재시도 관련 상수
MAX_RETRY_ATTEMPTS: Final[int] = 3  # 최대 재시도 횟수
TIMEOUT_SECONDS: Final[float] = 1.0  # 재시도 간 대기 시간(초)

# 게임 기간
TOTAL_GAME_DAYS: Final[int] = 730  # 2년

# 초기 게임 설정
DEFAULT_STARTING_MONEY: Final[float] = 10000.0
DEFAULT_STARTING_REPUTATION: Final[float] = 50.0
DEFAULT_STARTING_HAPPINESS: Final[float] = 50.0
DEFAULT_STARTING_SUFFERING: Final[float] = 50.0
DEFAULT_STARTING_INVENTORY: Final[float] = 50.0
DEFAULT_STARTING_STAFF_FATIGUE: Final[float] = 50.0
DEFAULT_STARTING_FACILITY: Final[float] = 50.0
DEFAULT_STARTING_DEMAND: Final[float] = 50.0

# 게임 단계 구분
EARLY_GAME_DAYS: Final[int] = 180
MID_GAME_DAYS: Final[int] = 545

# 경고 임계값
WARNING_THRESHOLD: Final[float] = 0.2  # 20% 이하/이상 시 경고
CRITICAL_THRESHOLD: Final[float] = 0.1  # 10% 이하/이상 시 위험

# 이벤트 관련 상수
MAX_EVENTS_PER_DAY: Final[int] = 3
EVENT_COOLDOWN_DAYS: Final[int] = 7
MAX_CASCADE_DEPTH: Final[int] = 5

# 확률 관련 상수
PROBABILITY_HIGH_THRESHOLD: Final[float] = 0.7
PROBABILITY_MEDIUM_THRESHOLD: Final[float] = 0.4
PROBABILITY_LOW_THRESHOLD: Final[float] = 0.2

# 게임 단계 구분
EARLY_GAME_THRESHOLD: Final[int] = 180
MID_GAME_THRESHOLD: Final[int] = 545

# 기본 메트릭 값
DEFAULT_MONEY: Final[float] = 10000.0
DEFAULT_REPUTATION: Final[float] = 50.0
DEFAULT_HAPPINESS: Final[float] = 50.0
DEFAULT_SUFFERING: Final[float] = 50.0
DEFAULT_INVENTORY: Final[float] = 50.0
DEFAULT_STAFF_FATIGUE: Final[float] = 50.0
DEFAULT_FACILITY: Final[float] = 50.0
DEFAULT_DEMAND: Final[float] = 50.0

# 테스트용 메트릭 값
TEST_MONEY: Final[float] = 20000.0
TEST_REPUTATION: Final[float] = 75.0
TEST_HAPPINESS: Final[float] = 80.0
TEST_SUFFERING: Final[float] = 20.0
TEST_INVENTORY: Final[float] = 60.0
TEST_STAFF_FATIGUE: Final[float] = 30.0
TEST_FACILITY: Final[float] = 70.0
TEST_DEMAND: Final[float] = 65.0

# 이벤트 관련 상수
MAX_EVENTS_PER_DAY: Final[int] = 3
EVENT_COOLDOWN_DAYS: Final[int] = 7
MAX_CASCADE_DEPTH: Final[int] = 3

# 확률 임계값
PROBABILITY_HIGH_THRESHOLD: Final[float] = 0.8
PROBABILITY_MEDIUM_THRESHOLD: Final[float] = 0.5
PROBABILITY_LOW_THRESHOLD: Final[float] = 0.2

# 게임 진행 관련
TOTAL_GAME_DAYS: Final[int] = 730
MIN_STORY_LENGTH: Final[int] = 100
MAX_STORY_LENGTH: Final[int] = 1000

# 재시도 관련
MAX_RETRY_ATTEMPTS: Final[int] = 3
TIMEOUT_SECONDS: Final[float] = 1.0

# 메트릭 범위
METRIC_RANGES: Final[dict[Metric, tuple[float, float, float]]] = {
    Metric.MONEY: (0.0, float("inf"), DEFAULT_MONEY),
    Metric.REPUTATION: (0.0, 100.0, DEFAULT_REPUTATION),
    Metric.HAPPINESS: (0.0, 100.0, DEFAULT_HAPPINESS),
    Metric.SUFFERING: (0.0, 100.0, DEFAULT_SUFFERING),
    Metric.INVENTORY: (0.0, 100.0, DEFAULT_INVENTORY),
    Metric.STAFF_FATIGUE: (0.0, 100.0, DEFAULT_STAFF_FATIGUE),
    Metric.FACILITY: (0.0, 100.0, DEFAULT_FACILITY),
    Metric.DEMAND: (0.0, 100.0, DEFAULT_DEMAND),
}

# 트레이드오프 관계
TRADEOFF_RELATIONSHIPS: Final[dict[Metric, tuple[Metric, ...]]] = {
    Metric.MONEY: (Metric.REPUTATION, Metric.HAPPINESS),
    Metric.REPUTATION: (Metric.MONEY, Metric.STAFF_FATIGUE),
    Metric.HAPPINESS: (Metric.MONEY, Metric.SUFFERING),
    Metric.SUFFERING: (Metric.HAPPINESS, Metric.STAFF_FATIGUE),
    Metric.INVENTORY: (Metric.MONEY, Metric.DEMAND),
    Metric.STAFF_FATIGUE: (Metric.REPUTATION, Metric.SUFFERING),
    Metric.FACILITY: (Metric.MONEY, Metric.DEMAND),
    Metric.DEMAND: (Metric.INVENTORY, Metric.FACILITY),
}

# 게임 단계 정의
class GamePhase(Enum):
    """게임 단계"""
    EARLY = auto()
    MID = auto()
    LATE = auto()

# 이벤트 심각도 정의
class EventSeverity(Enum):
    """이벤트 심각도"""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

# 이벤트 타입 정의
class EventType(Enum):
    """이벤트 타입"""
    STORY = auto()
    RANDOM = auto()
    CASCADE = auto()

# 경고 임계값
WARNING_THRESHOLDS: Final[dict[Metric, tuple[float, float]]] = {
    Metric.MONEY: (1000.0, 5000.0),
    Metric.REPUTATION: (20.0, 80.0),
    Metric.HAPPINESS: (20.0, 80.0),
    Metric.SUFFERING: (80.0, 20.0),
    Metric.INVENTORY: (20.0, 80.0),
    Metric.STAFF_FATIGUE: (80.0, 20.0),
    Metric.FACILITY: (20.0, 80.0),
    Metric.DEMAND: (20.0, 80.0),
} 
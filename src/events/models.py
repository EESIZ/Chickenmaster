"""
이벤트 데이터 모델 모듈

이 모듈은 Chicken-RNG 게임의 이벤트 시스템에 사용되는 데이터 모델을 정의합니다.
Event, Trigger, Effect 등의 데이터클래스를 통해 이벤트 구조를 표현합니다.

핵심 철학:
- 정답 없음: 모든 이벤트는 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 이벤트 발생과 효과는 예측 불가능한 요소에 영향을 받습니다
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# schema.py에서 필요한 상수와 Enum 가져오기
from schema import Metric


class TriggerCondition(Enum):
    """
    트리거 조건을 정의하는 열거형

    이 열거형은 지표 값과 임계값을 비교하는 조건을 정의합니다.
    불확실성 요소로 인해 예상치 못한 시점에 조건이 충족될 수 있습니다.
    """

    LESS_THAN = auto()
    GREATER_THAN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    IN_RANGE = auto()
    NOT_IN_RANGE = auto()


class EventCategory(Enum):
    """
    이벤트 카테고리를 정의하는 열거형

    이 열거형은 이벤트의 발생 메커니즘을 정의합니다.
    각 카테고리는 서로 다른 트리거 조건과 평가 방식을 가집니다.
    """

    RANDOM = auto()  # 확률 기반 무작위 발생
    THRESHOLD = auto()  # 임계값 기반 발생
    SCHEDULED = auto()  # 일정 주기로 발생
    CASCADE = auto()  # 다른 이벤트의 결과로 발생
    DAILY_ROUTINE = auto()  # 일상 업무
    CRISIS = auto()  # 위기 상황
    OPPORTUNITY = auto()  # 기회


@dataclass
class Trigger:
    """
    이벤트 트리거 조건을 정의하는 데이터클래스

    이 클래스는 이벤트가 발생하기 위한 조건을 정의합니다.
    지표, 조건, 임계값으로 구성되며, 조건이 충족되면 이벤트가 발생합니다.
    """

    metric: Metric
    condition: TriggerCondition
    value: float | None = None
    range_min: float | None = None
    range_max: float | None = None

    def evaluate(self, current_metrics: dict[Metric, float]) -> bool:
        """
        트리거 조건을 평가합니다.

        Args:
            current_metrics: 현재 지표 상태

        Returns:
            bool: 조건이 충족되면 True, 그렇지 않으면 False
        """
        if self.metric not in current_metrics:
            return False

        current_value = current_metrics[self.metric]

        if self.condition == TriggerCondition.LESS_THAN:
            return current_value < self.value
        elif self.condition == TriggerCondition.GREATER_THAN:
            return current_value > self.value
        elif self.condition == TriggerCondition.EQUAL:
            # 부동소수점 비교를 위한 작은 오차 허용
            return abs(current_value - self.value) < 0.001
        elif self.condition == TriggerCondition.GREATER_THAN_OR_EQUAL:
            return current_value >= self.value
        elif self.condition == TriggerCondition.LESS_THAN_OR_EQUAL:
            return current_value <= self.value
        elif self.condition == TriggerCondition.IN_RANGE:
            return self.range_min <= current_value <= self.range_max
        elif self.condition == TriggerCondition.NOT_IN_RANGE:
            return not (self.range_min <= current_value <= self.range_max)

        return False


@dataclass
class Effect:
    """
    이벤트 효과를 정의하는 데이터클래스

    이 클래스는 이벤트가 발생했을 때 지표에 미치는 영향을 정의합니다.
    지표와 적용할 수식으로 구성되며, 수식은 현재 지표 값을 기준으로 평가됩니다.
    """

    metric: Metric
    formula: str
    message: str | None = None

    def apply(self, current_metrics: dict[Metric, float]) -> float:
        """
        효과를 적용하여 새 지표 값을 계산합니다.

        중요: 수식은 변화량을 나타내며, 현재 값에 더해집니다.
        예: "-500"은 현재 값에서 500을 뺀 결과를 반환합니다.

        Args:
            current_metrics: 현재 지표 상태

        Returns:
            float: 계산된 새 지표 값
        """
        if self.metric not in current_metrics:
            return 0.0

        current_value = current_metrics[self.metric]

        # 백분율 표기법 처리 (예: "-5%")
        if "%" in self.formula:
            formula = self.formula.replace("%", "")
            percentage = float(formula) / 100
            # 백분율은 현재 값에 대한 상대적 변화량
            return current_value * (1 + percentage)

        # 일반 수식 평가 (value는 현재 지표 값)
        try:
            # 수식이 단순 숫자인 경우 (예: "-500")
            try:
                # 숫자로 변환 가능하면 변화량으로 처리
                delta = float(self.formula)
                return current_value + delta
            except ValueError:
                # 수식이 복잡한 경우 (예: "value * 0.9")
                value = current_value
                result = eval(self.formula, {"__builtins__": {}}, {"value": value})

                # 수식이 절대값을 반환하는 경우 (value를 사용하지 않는 경우)
                if "value" not in self.formula:
                    # 변화량으로 처리
                    return current_value + float(result)
                # 수식이 새 값을 직접 계산하는 경우
                return float(result)
        except Exception as e:
            # 수식 평가 실패 시 현재 값 유지
            print(f"수식 평가 실패: {self.formula}, 오류: {e}")
            return current_value


@dataclass
class Event:
    """
    게임 이벤트를 정의하는 데이터클래스

    이 클래스는 게임에서 발생할 수 있는 이벤트를 정의합니다.
    각 이벤트는 고유 ID, 타입, 우선순위, 쿨다운, 트리거, 효과 등으로 구성됩니다.
    """

    id: str
    type: EventCategory
    name: str
    description: str
    effects: list[Effect]
    trigger: Trigger | None = None
    probability: float = 1.0
    priority: int = 0
    cooldown: int = 0
    category: str = "default"
    last_triggered: datetime | None = None
    turn: int = 0
    severity: str = "INFO"
    timestamp: str | None = None
    tags: list[str] = field(default_factory=list)
    cascade_depth: int = 0

    def __post_init__(self) -> None:
        """
        초기화 후 추가 작업을 수행합니다.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def can_fire(self, current_turn: int) -> bool:
        """
        이벤트가 발생 가능한지 확인합니다.

        Args:
            current_turn: 현재 게임 턴

        Returns:
            bool: 발생 가능하면 True, 그렇지 않으면 False
        """
        # 쿨다운 확인
        if self.cooldown > 0 and self.last_triggered:
            elapsed_turns = current_turn - self.turn
            if elapsed_turns < self.cooldown:
                return False

        return True

    def evaluate_trigger(
        self, current_metrics: dict[Metric, float], rng: random.Random | None = None
    ) -> bool:
        """
        이벤트 트리거 조건을 평가합니다.

        Args:
            current_metrics: 현재 지표 상태
            rng: 난수 생성기 (기본값: None)

        Returns:
            bool: 트리거 조건이 충족되면 True, 그렇지 않으면 False
        """
        # 이벤트 타입에 따라 다른 평가 방식 적용
        if self.type == EventCategory.RANDOM:
            if self.probability is None:
                return False

            # 난수 생성기가 제공되지 않은 경우 기본 random 모듈 사용
            random_instance = rng or random
            return bool(random_instance.random() < self.probability)

        elif self.type == EventCategory.THRESHOLD:
            if self.trigger is None:
                return False
            return self.trigger.evaluate(current_metrics)

        elif self.type == EventCategory.SCHEDULED:
            if self.schedule is None:
                return False
            # 스케줄에 따라 특정 턴마다 발생
            from schema import DEFAULT_GAME_LENGTH

            current_day = DEFAULT_GAME_LENGTH  # 실제 구현에서는 현재 게임 일수를 사용
            return current_day % self.schedule == 0

        elif self.type == EventCategory.CASCADE:
            # CASCADE 타입은 직접 평가하지 않고 다른 이벤트에 의해 트리거됨
            return False

        return False

    def apply_effects(self, current_metrics: dict[Metric, float]) -> dict[Metric, float]:
        """
        이벤트 효과를 적용합니다.

        Args:
            current_metrics: 현재 지표 상태

        Returns:
            Dict[Metric, float]: 효과가 적용된 새 지표 상태
        """
        result = current_metrics.copy()

        for effect in self.effects:
            new_value = effect.apply(current_metrics)
            result[effect.metric] = new_value

        return result

    def fire(self, current_metrics: dict[Metric, float], current_turn: int) -> dict[Metric, float]:
        """
        이벤트를 발생시키고 효과를 적용합니다.

        Args:
            current_metrics: 현재 지표 상태
            current_turn: 현재 게임 턴

        Returns:
            Dict[Metric, float]: 효과가 적용된 새 지표 상태
        """
        # 마지막 발생 턴 업데이트
        self.last_triggered = datetime.now()

        # 효과 적용
        return self.apply_effects(current_metrics)


@dataclass
class Alert:
    """
    임계값 기반 알림을 정의하는 데이터클래스

    이 클래스는 임계값 기반 이벤트가 발생했을 때 생성되는 알림을 정의합니다.
    알림은 로그나 큐에 추가되어 후속 모듈에서 활용됩니다.
    """

    event_id: str
    message: str
    metrics: dict[Metric, float]
    turn: int
    severity: str = "INFO"
    timestamp: str | None = None

    def __post_init__(self) -> None:
        """
        초기화 후 추가 작업을 수행합니다.
        """
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

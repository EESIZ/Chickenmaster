"""
게임 상태 모듈

이 모듈은 게임의 현재 상태를 관리하는 클래스를 정의합니다.
"""

from dataclasses import dataclass, field

from ..domain.metrics import MetricEnum, validate_metric_value
from ..game_constants import (
    DEFAULT_STARTING_MONEY,
    DEFAULT_STARTING_REPUTATION,
    DEFAULT_STARTING_HAPPINESS,
    DEFAULT_STARTING_SUFFERING,
    DEFAULT_STARTING_INVENTORY,
    DEFAULT_STARTING_STAFF_FATIGUE,
    DEFAULT_STARTING_FACILITY,
    DEFAULT_STARTING_DEMAND,
)


@dataclass(frozen=True)
class GameState:
    """
    게임의 현재 상태를 나타내는 불변 데이터 클래스

    이 클래스는 게임의 모든 핵심 지표와 상태를 관리합니다.
    모든 속성은 불변이며, 상태 변경은 새로운 인스턴스를 생성하여 이루어집니다.
    """

    current_day: int
    money: float = DEFAULT_STARTING_MONEY
    reputation: float = DEFAULT_STARTING_REPUTATION
    happiness: float = DEFAULT_STARTING_HAPPINESS
    suffering: float = DEFAULT_STARTING_SUFFERING
    inventory: float = DEFAULT_STARTING_INVENTORY
    staff_fatigue: float = DEFAULT_STARTING_STAFF_FATIGUE
    facility: float = DEFAULT_STARTING_FACILITY
    demand: float = DEFAULT_STARTING_DEMAND
    events_history: tuple[str, ...] = field(default_factory=tuple)

    @property
    def metrics(self) -> dict[MetricEnum, float]:
        """
        모든 지표의 현재 값을 딕셔너리로 반환합니다.

        Returns:
            dict[MetricEnum, float]: 지표 이름을 키로, 현재 값을 값으로 하는 딕셔너리
        """
        return {
            MetricEnum.MONEY: self.money,
            MetricEnum.REPUTATION: self.reputation,
            MetricEnum.HAPPINESS: self.happiness,
            MetricEnum.SUFFERING: self.suffering,
            MetricEnum.INVENTORY: self.inventory,
            MetricEnum.STAFF_FATIGUE: self.staff_fatigue,
            MetricEnum.FACILITY: self.facility,
            MetricEnum.DEMAND: self.demand,
        }

    def apply_effects(self, effects: dict[MetricEnum, float]) -> "GameState":
        """
        주어진 효과를 현재 상태에 적용한 새로운 상태를 반환합니다.

        Args:
            effects: 적용할 효과를 나타내는 딕셔너리

        Returns:
            GameState: 효과가 적용된 새로운 게임 상태
        """
        new_metrics = self.metrics.copy()
        for metric, value in effects.items():
            current_value = new_metrics[metric]
            new_value = validate_metric_value(metric, current_value + value)
            new_metrics[metric] = new_value

        return GameState(
            current_day=self.current_day,
            money=new_metrics[MetricEnum.MONEY],
            reputation=new_metrics[MetricEnum.REPUTATION],
            happiness=new_metrics[MetricEnum.HAPPINESS],
            suffering=new_metrics[MetricEnum.SUFFERING],
            inventory=new_metrics[MetricEnum.INVENTORY],
            staff_fatigue=new_metrics[MetricEnum.STAFF_FATIGUE],
            facility=new_metrics[MetricEnum.FACILITY],
            demand=new_metrics[MetricEnum.DEMAND],
            events_history=self.events_history,
        )

    def add_event(self, event_id: str) -> "GameState":
        """
        새로운 이벤트를 히스토리에 추가한 새로운 상태를 반환합니다.

        Args:
            event_id: 추가할 이벤트의 ID

        Returns:
            GameState: 이벤트가 추가된 새로운 게임 상태
        """
        new_history = (*self.events_history, event_id)
        return GameState(
            current_day=self.current_day,
            money=self.money,
            reputation=self.reputation,
            happiness=self.happiness,
            suffering=self.suffering,
            inventory=self.inventory,
            staff_fatigue=self.staff_fatigue,
            facility=self.facility,
            demand=self.demand,
            events_history=new_history,
        )

    def to_dict(self) -> dict:
        """
        게임 상태를 딕셔너리로 변환합니다.

        Returns:
            dict: 게임 상태를 나타내는 딕셔너리
        """
        return {
            "current_day": self.current_day,
            "metrics": self.metrics,
            "events_history": list(self.events_history),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """
        딕셔너리로부터 게임 상태를 생성합니다.

        Args:
            data: 게임 상태를 나타내는 딕셔너리

        Returns:
            GameState: 생성된 게임 상태
        """
        metrics = data.get("metrics", {})
        return cls(
            current_day=data["current_day"],
            money=metrics.get(MetricEnum.MONEY.value, DEFAULT_STARTING_MONEY),
            reputation=metrics.get(MetricEnum.REPUTATION.value, DEFAULT_STARTING_REPUTATION),
            happiness=metrics.get(MetricEnum.HAPPINESS.value, DEFAULT_STARTING_HAPPINESS),
            suffering=metrics.get(MetricEnum.SUFFERING.value, DEFAULT_STARTING_SUFFERING),
            inventory=metrics.get(MetricEnum.INVENTORY.value, DEFAULT_STARTING_INVENTORY),
            staff_fatigue=metrics.get(
                MetricEnum.STAFF_FATIGUE.value, DEFAULT_STARTING_STAFF_FATIGUE
            ),
            facility=metrics.get(MetricEnum.FACILITY.value, DEFAULT_STARTING_FACILITY),
            demand=metrics.get(MetricEnum.DEMAND.value, DEFAULT_STARTING_DEMAND),
            events_history=tuple(data.get("events_history", [])),
        ) 
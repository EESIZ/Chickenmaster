"""
게임 상태 도메인 모델
불변 객체로 구현된 게임 상태 관련 도메인 엔티티를 포함합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Final

from ..game_constants import Metric, TOTAL_GAME_DAYS
from app.core.game_constants import (
    DEFAULT_MONEY, DEFAULT_REPUTATION, DEFAULT_HAPPINESS, DEFAULT_SUFFERING,
    DEFAULT_INVENTORY, DEFAULT_STAFF_FATIGUE, DEFAULT_FACILITY, DEFAULT_DEMAND
)


@dataclass(frozen=True)
class GameState:
    """게임 상태를 나타내는 불변 객체"""
    
    money: float = DEFAULT_MONEY
    reputation: float = DEFAULT_REPUTATION
    happiness: float = DEFAULT_HAPPINESS
    suffering: float = DEFAULT_SUFFERING
    inventory: float = DEFAULT_INVENTORY
    staff_fatigue: float = DEFAULT_STAFF_FATIGUE
    facility: float = DEFAULT_FACILITY
    demand: float = DEFAULT_DEMAND
    current_day: int = 1
    events_history: Tuple[str, ...] = field(default_factory=tuple)
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """초기화 후 검증"""
        if self.money < 0:
            raise ValueError("돈은 음수가 될 수 없습니다.")
        if not 0 <= self.reputation <= 100:
            raise ValueError("평판은 0에서 100 사이여야 합니다.")
        if not 0 <= self.happiness <= 100:
            raise ValueError("행복도는 0에서 100 사이여야 합니다.")
        if not 0 <= self.suffering <= 100:
            raise ValueError("고통도는 0에서 100 사이여야 합니다.")
        if not 0 <= self.inventory <= 100:
            raise ValueError("재고는 0에서 100 사이여야 합니다.")
        if not 0 <= self.staff_fatigue <= 100:
            raise ValueError("직원 피로도는 0에서 100 사이여야 합니다.")
        if not 0 <= self.facility <= 100:
            raise ValueError("시설 상태는 0에서 100 사이여야 합니다.")
        if not 0 <= self.demand <= 100:
            raise ValueError("수요는 0에서 100 사이여야 합니다.")
        if self.current_day < 1:
            raise ValueError("현재 일자는 1 이상이어야 합니다.")

    @property
    def metrics(self) -> Dict[Metric, float]:
        """모든 메트릭을 딕셔너리로 반환"""
        return {
            Metric.MONEY: self.money,
            Metric.REPUTATION: self.reputation,
            Metric.HAPPINESS: self.happiness,
            Metric.SUFFERING: self.suffering,
            Metric.INVENTORY: self.inventory,
            Metric.STAFF_FATIGUE: self.staff_fatigue,
            Metric.FACILITY: self.facility,
            Metric.DEMAND: self.demand,
        }

    @property
    def game_progression(self) -> float:
        """게임 진행률을 0.0 ~ 1.0 사이의 값으로 반환"""
        return self.current_day / TOTAL_GAME_DAYS

    @property
    def is_early_game(self) -> bool:
        """초기 게임 단계 여부"""
        return self.current_day <= 180

    @property
    def is_mid_game(self) -> bool:
        """중반 게임 단계 여부"""
        return 180 < self.current_day <= 545

    @property
    def is_late_game(self) -> bool:
        """후반 게임 단계 여부"""
        return self.current_day > 545

    def apply_effects(self, effects: Dict[Metric, float]) -> "GameState":
        """효과 적용 시 새 상태 반환"""
        current_metrics = self.metrics
        new_metrics = {
            metric: current_metrics[metric] + effects.get(metric, 0.0)
            for metric in Metric
        }
        
        return GameState(
            money=new_metrics[Metric.MONEY],
            reputation=new_metrics[Metric.REPUTATION],
            happiness=new_metrics[Metric.HAPPINESS],
            suffering=new_metrics[Metric.SUFFERING],
            inventory=new_metrics[Metric.INVENTORY],
            staff_fatigue=new_metrics[Metric.STAFF_FATIGUE],
            facility=new_metrics[Metric.FACILITY],
            demand=new_metrics[Metric.DEMAND],
            current_day=self.current_day,
            events_history=self.events_history,
            last_updated=datetime.now(),
        )

    def add_event_to_history(self, event_id: str) -> "GameState":
        """이벤트 히스토리에 추가"""
        return GameState(
            money=self.money,
            reputation=self.reputation,
            happiness=self.happiness,
            suffering=self.suffering,
            inventory=self.inventory,
            staff_fatigue=self.staff_fatigue,
            facility=self.facility,
            demand=self.demand,
            current_day=self.current_day,
            events_history=(*self.events_history, event_id),
            last_updated=datetime.now(),
        )

    def get_metric_value(self, metric: Metric) -> float:
        """특정 메트릭의 현재 값을 반환"""
        return self.metrics[metric]

    def is_metric_in_warning_zone(self, metric: Metric) -> bool:
        """메트릭이 경고 구간에 있는지 확인"""
        value = self.get_metric_value(metric)
        
        if metric == Metric.MONEY:
            return value < 1000.0
        elif metric == Metric.REPUTATION:
            return value < 20.0 or value > 80.0
        elif metric == Metric.STAFF_FATIGUE:
            return value > 80.0
        elif metric == Metric.FACILITY:
            return value < 30.0
        
        return False

    def to_dict(self) -> Dict[str, float | int | List[str]]:
        """게임 상태를 딕셔너리로 변환"""
        return {
            "money": self.money,
            "reputation": self.reputation,
            "happiness": self.happiness,
            "suffering": self.suffering,
            "inventory": self.inventory,
            "staff_fatigue": self.staff_fatigue,
            "facility": self.facility,
            "demand": self.demand,
            "current_day": self.current_day,
            "events_history": list(self.events_history)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float | int | List[str]]) -> "GameState":
        """딕셔너리에서 게임 상태 생성"""
        return cls(
            money=data.get("money", 10000.0),
            reputation=data.get("reputation", 50.0),
            happiness=data.get("happiness", 50.0),
            suffering=data.get("suffering", 50.0),
            inventory=data.get("inventory", 50.0),
            staff_fatigue=data.get("staff_fatigue", 50.0),
            facility=data.get("facility", 50.0),
            demand=data.get("demand", 50.0),
            current_day=data.get("current_day", 1),
            events_history=tuple(data.get("events_history", []))
        ) 
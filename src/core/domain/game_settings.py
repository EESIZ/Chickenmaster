"""
게임 설정 모듈

이 모듈은 게임의 초기 설정을 관리하는 클래스를 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional

from .game_state import GameState
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
class GameSettings:
    """게임 초기 설정 - 불변 객체"""

    starting_money: Optional[float] = None
    starting_reputation: Optional[float] = None
    starting_happiness: Optional[float] = None
    starting_suffering: Optional[float] = None
    starting_inventory: Optional[float] = None
    starting_staff_fatigue: Optional[float] = None
    starting_facility: Optional[float] = None
    starting_demand: Optional[float] = None

    def create_initial_state(self) -> GameState:
        """초기 게임 상태를 생성합니다."""
        return GameState(
            current_day=1,
            money=self.starting_money or DEFAULT_STARTING_MONEY,
            reputation=self.starting_reputation or DEFAULT_STARTING_REPUTATION,
            happiness=self.starting_happiness or DEFAULT_STARTING_HAPPINESS,
            suffering=self.starting_suffering or DEFAULT_STARTING_SUFFERING,
            inventory=self.starting_inventory or DEFAULT_STARTING_INVENTORY,
            staff_fatigue=self.starting_staff_fatigue or DEFAULT_STARTING_STAFF_FATIGUE,
            facility=self.starting_facility or DEFAULT_STARTING_FACILITY,
            demand=self.starting_demand or DEFAULT_STARTING_DEMAND,
            events_history=(),
        ) 
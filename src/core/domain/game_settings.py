"""
게임 설정 모듈

이 모듈은 게임의 초기 설정을 관리하는 클래스를 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional

from .game_state import GameState
from ..ports.data_provider import DataProvider, DataCategory, DataRequest


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

    @classmethod
    def from_provider(cls, provider: DataProvider) -> "GameSettings":
        """데이터 제공자로부터 설정을 생성합니다."""
        return cls(
            starting_money=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_money", 1000000.0)),
            starting_reputation=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_reputation", 50.0)),
            starting_happiness=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_happiness", 50.0)),
            starting_suffering=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_suffering", 0.0)),
            starting_inventory=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_inventory", 100.0)),
            starting_staff_fatigue=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_staff_fatigue", 0.0)),
            starting_facility=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_facility", 100.0)),
            starting_demand=provider.get_value(DataRequest(DataCategory.GAME_SETTINGS, "starting_demand", 50.0)),
        )

    def create_initial_state(self) -> GameState:
        """초기 게임 상태를 생성합니다."""
        return GameState(
            current_day=1,
            money=self.starting_money or 1000000.0,
            reputation=self.starting_reputation or 50.0,
            happiness=self.starting_happiness or 50.0,
            suffering=self.starting_suffering or 0.0,
            inventory=self.starting_inventory or 100.0,
            staff_fatigue=self.starting_staff_fatigue or 0.0,
            facility=self.starting_facility or 100.0,
            demand=self.starting_demand or 50.0,
            events_history=(),
        ) 
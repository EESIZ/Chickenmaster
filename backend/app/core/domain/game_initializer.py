"""
게임 초기화 시스템
게임의 초기 상태를 설정하고 필요한 리소스를 로드합니다.
"""

from dataclasses import dataclass

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

    starting_money: float = DEFAULT_STARTING_MONEY
    starting_reputation: float = DEFAULT_STARTING_REPUTATION
    starting_happiness: float = DEFAULT_STARTING_HAPPINESS
    starting_suffering: float = DEFAULT_STARTING_SUFFERING
    starting_inventory: float = DEFAULT_STARTING_INVENTORY
    starting_staff_fatigue: float = DEFAULT_STARTING_STAFF_FATIGUE
    starting_facility: float = DEFAULT_STARTING_FACILITY
    starting_demand: float = DEFAULT_STARTING_DEMAND


class GameInitializer:
    """게임 초기화 시스템"""

    def __init__(self, settings: GameSettings | None = None):
        """
        Args:
            settings: 게임 초기 설정. None인 경우 기본값 사용
        """
        self.settings = settings or GameSettings()

    def initialize(self) -> GameState:
        """게임의 초기 상태를 생성합니다.

        Returns:
            GameState: 초기화된 게임 상태
        """
        return GameState(
            money=self.settings.starting_money,
            reputation=self.settings.starting_reputation,
            happiness=self.settings.starting_happiness,
            suffering=self.settings.starting_suffering,
            inventory=self.settings.starting_inventory,
            staff_fatigue=self.settings.starting_staff_fatigue,
            facility=self.settings.starting_facility,
            demand=self.settings.starting_demand,
            current_day=1,
            events_history=(),
        )

    def load_saved_game(self, save_data: dict) -> GameState:
        """저장된 게임 상태를 로드합니다.

        Args:
            save_data: 저장된 게임 데이터

        Returns:
            GameState: 로드된 게임 상태
        """
        return GameState(
            money=save_data.get("money", self.settings.starting_money),
            reputation=save_data.get("reputation", self.settings.starting_reputation),
            happiness=save_data.get("happiness", self.settings.starting_happiness),
            suffering=save_data.get("suffering", self.settings.starting_suffering),
            inventory=save_data.get("inventory", self.settings.starting_inventory),
            staff_fatigue=save_data.get("staff_fatigue", self.settings.starting_staff_fatigue),
            facility=save_data.get("facility", self.settings.starting_facility),
            demand=save_data.get("demand", self.settings.starting_demand),
            current_day=save_data.get("current_day", 1),
            events_history=tuple(save_data.get("events_history", [])),
        )

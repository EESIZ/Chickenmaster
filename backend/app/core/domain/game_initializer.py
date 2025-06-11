"""
게임 초기화 시스템
게임의 초기 상태를 설정하고 필요한 리소스를 로드합니다.
"""

from dataclasses import dataclass
from typing import Optional

from .game_state import GameState
from .interfaces.data_provider import GameDataProvider


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


class GameInitializer:
    """
    게임 초기화 시스템
    
    엑셀 기반 데이터 제공자를 사용하여 게임 초기값을 설정합니다.
    의존성 역전 원칙에 따라 GameDataProvider 인터페이스에 의존합니다.
    """

    def __init__(self, data_provider: GameDataProvider, settings: GameSettings | None = None):
        """
        Args:
            data_provider: 게임 데이터 제공자 (엑셀, JSON 등)
            settings: 게임 초기 설정. None인 경우 데이터 제공자의 기본값 사용
        """
        self.data_provider = data_provider
        self.settings = settings or GameSettings()
        
        # 데이터 로드
        self.metrics = data_provider.get_game_metrics()
        self.constants = data_provider.get_game_constants()
        self.tradeoffs = data_provider.get_tradeoff_relationships()
        self.uncertainty_weights = data_provider.get_uncertainty_weights()

    def initialize(self) -> GameState:
        """게임의 초기 상태를 생성합니다.

        Returns:
            GameState: 초기화된 게임 상태
        """
        # 설정값이 있으면 사용하고, 없으면 엑셀에서 읽은 기본값 사용
        money = self.settings.starting_money or self.metrics['Money'].base_value
        reputation = self.settings.starting_reputation or self.metrics['Reputation'].base_value
        happiness = self.settings.starting_happiness or self.metrics['Happiness'].base_value
        suffering = self.settings.starting_suffering or self.metrics['Suffering'].base_value
        inventory = self.settings.starting_inventory or self.metrics['Inventory'].base_value
        staff_fatigue = self.settings.starting_staff_fatigue or self.metrics['Staff_Fatigue'].base_value
        facility = self.settings.starting_facility or self.metrics['Facility'].base_value
        demand = self.settings.starting_demand or self.metrics['Demand'].base_value
        
        return GameState(
            money=money,
            reputation=reputation,
            happiness=happiness,
            suffering=suffering,
            inventory=inventory,
            staff_fatigue=staff_fatigue,
            facility=facility,
            demand=demand,
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
        # 기본값들을 엑셀에서 가져옴
        default_money = self.settings.starting_money or self.metrics['Money'].base_value
        default_reputation = self.settings.starting_reputation or self.metrics['Reputation'].base_value
        default_happiness = self.settings.starting_happiness or self.metrics['Happiness'].base_value
        default_suffering = self.settings.starting_suffering or self.metrics['Suffering'].base_value
        default_inventory = self.settings.starting_inventory or self.metrics['Inventory'].base_value
        default_staff_fatigue = self.settings.starting_staff_fatigue or self.metrics['Staff_Fatigue'].base_value
        default_facility = self.settings.starting_facility or self.metrics['Facility'].base_value
        default_demand = self.settings.starting_demand or self.metrics['Demand'].base_value
        
        return GameState(
            money=save_data.get("money", default_money),
            reputation=save_data.get("reputation", default_reputation),
            happiness=save_data.get("happiness", default_happiness),
            suffering=save_data.get("suffering", default_suffering),
            inventory=save_data.get("inventory", default_inventory),
            staff_fatigue=save_data.get("staff_fatigue", default_staff_fatigue),
            facility=save_data.get("facility", default_facility),
            demand=save_data.get("demand", default_demand),
            current_day=save_data.get("current_day", 1),
            events_history=tuple(save_data.get("events_history", [])),
        )

    def get_game_constants(self) -> dict:
        """게임 상수를 반환합니다."""
        return self.constants
    
    def get_tradeoff_relationships(self) -> dict:
        """트레이드오프 관계를 반환합니다."""
        return self.tradeoffs
    
    def get_uncertainty_weights(self) -> dict:
        """불확실성 가중치를 반환합니다."""
        return self.uncertainty_weights

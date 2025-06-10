"""
GameInitializer 테스트
"""

from app.core.domain.game_initializer import GameInitializer, GameSettings
from app.core.game_constants import (
    DEFAULT_MONEY,
    DEFAULT_REPUTATION,
    DEFAULT_HAPPINESS,
    DEFAULT_SUFFERING,
    DEFAULT_INVENTORY,
    DEFAULT_STAFF_FATIGUE,
    DEFAULT_FACILITY,
    DEFAULT_DEMAND,
    TEST_MONEY,
    TEST_REPUTATION,
    TEST_HAPPINESS,
    TEST_SUFFERING,
    TEST_INVENTORY,
    TEST_STAFF_FATIGUE,
    TEST_FACILITY,
    TEST_DEMAND,
)
from typing import Final

# 테스트용 상수
TEST_SAVE_MONEY: Final[float] = 15000.0
TEST_SAVE_REPUTATION: Final[float] = 60.0
TEST_SAVE_HAPPINESS: Final[float] = 70.0
TEST_SAVE_SUFFERING: Final[float] = 30.0
TEST_SAVE_INVENTORY: Final[float] = 50.0
TEST_SAVE_STAFF_FATIGUE: Final[float] = 40.0
TEST_SAVE_FACILITY: Final[float] = 60.0
TEST_SAVE_DEMAND: Final[float] = 55.0
TEST_SAVE_DAY: Final[int] = 10
TEST_SAVE_EVENTS_COUNT: Final[int] = 2


def test_game_initializer_default_settings():
    """기본 설정으로 게임 초기화 테스트"""
    initializer = GameInitializer()
    game_state = initializer.initialize()

    assert game_state.money == DEFAULT_MONEY
    assert game_state.reputation == DEFAULT_REPUTATION
    assert game_state.happiness == DEFAULT_HAPPINESS
    assert game_state.suffering == DEFAULT_SUFFERING
    assert game_state.inventory == DEFAULT_INVENTORY
    assert game_state.staff_fatigue == DEFAULT_STAFF_FATIGUE
    assert game_state.facility == DEFAULT_FACILITY
    assert game_state.demand == DEFAULT_DEMAND


def test_game_initializer_custom_settings():
    """사용자 정의 설정으로 게임 초기화 테스트"""
    settings = GameSettings(
        starting_money=TEST_MONEY,
        starting_reputation=TEST_REPUTATION,
        starting_happiness=TEST_HAPPINESS,
        starting_suffering=TEST_SUFFERING,
        starting_inventory=TEST_INVENTORY,
        starting_staff_fatigue=TEST_STAFF_FATIGUE,
        starting_facility=TEST_FACILITY,
        starting_demand=TEST_DEMAND,
    )
    initializer = GameInitializer(settings)
    game_state = initializer.initialize()

    assert game_state.money == TEST_MONEY
    assert game_state.reputation == TEST_REPUTATION
    assert game_state.happiness == TEST_HAPPINESS
    assert game_state.suffering == TEST_SUFFERING
    assert game_state.inventory == TEST_INVENTORY
    assert game_state.staff_fatigue == TEST_STAFF_FATIGUE
    assert game_state.facility == TEST_FACILITY
    assert game_state.demand == TEST_DEMAND


def test_load_saved_game():
    """저장된 게임 로드 테스트"""
    initializer = GameInitializer()
    save_data = {
        "money": TEST_SAVE_MONEY,
        "reputation": TEST_SAVE_REPUTATION,
        "happiness": TEST_SAVE_HAPPINESS,
        "suffering": TEST_SAVE_SUFFERING,
        "inventory": TEST_SAVE_INVENTORY,
        "staff_fatigue": TEST_SAVE_STAFF_FATIGUE,
        "facility": TEST_SAVE_FACILITY,
        "demand": TEST_SAVE_DEMAND,
        "current_day": TEST_SAVE_DAY,
        "events_history": ["event1", "event2"],
    }
    game_state = initializer.load_saved_game(save_data)

    assert game_state.money == TEST_SAVE_MONEY
    assert game_state.reputation == TEST_SAVE_REPUTATION
    assert game_state.happiness == TEST_SAVE_HAPPINESS
    assert game_state.suffering == TEST_SAVE_SUFFERING
    assert game_state.inventory == TEST_SAVE_INVENTORY
    assert game_state.staff_fatigue == TEST_SAVE_STAFF_FATIGUE
    assert game_state.facility == TEST_SAVE_FACILITY
    assert game_state.demand == TEST_SAVE_DEMAND
    assert game_state.current_day == TEST_SAVE_DAY
    assert len(game_state.events_history) == TEST_SAVE_EVENTS_COUNT
    assert game_state.events_history == ("event1", "event2")


def test_load_saved_game_partial_data():
    """부분적인 저장 데이터로 게임 로드 테스트"""
    initializer = GameInitializer()
    save_data = {
        "money": TEST_SAVE_MONEY,
        "current_day": TEST_SAVE_DAY,
    }
    game_state = initializer.load_saved_game(save_data)

    assert game_state.money == TEST_SAVE_MONEY
    assert game_state.current_day == TEST_SAVE_DAY
    # 나머지 값들은 기본값 사용
    assert game_state.reputation == initializer.settings.starting_reputation
    assert game_state.happiness == initializer.settings.starting_happiness
    assert game_state.suffering == initializer.settings.starting_suffering
    assert game_state.inventory == initializer.settings.starting_inventory
    assert game_state.staff_fatigue == initializer.settings.starting_staff_fatigue
    assert game_state.facility == initializer.settings.starting_facility
    assert game_state.demand == initializer.settings.starting_demand

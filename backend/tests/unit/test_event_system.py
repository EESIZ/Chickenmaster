"""
이벤트 시스템 테스트
"""

import pytest
from app.core.domain.event_system import EventSystem, Event, EventType, EventSeverity, EventEffect, EventTrigger
from app.core.domain.game_state import GameState
from app.core.game_constants import (
    DEFAULT_MONEY, DEFAULT_REPUTATION, DEFAULT_HAPPINESS, DEFAULT_SUFFERING,
    DEFAULT_INVENTORY, DEFAULT_STAFF_FATIGUE, DEFAULT_FACILITY, DEFAULT_DEMAND,
    TEST_MONEY, TEST_REPUTATION, TEST_HAPPINESS, TEST_SUFFERING,
    TEST_INVENTORY, TEST_STAFF_FATIGUE, TEST_FACILITY, TEST_DEMAND,
    EVENT_COOLDOWN_DAYS, MAX_CASCADE_DEPTH
)


@pytest.fixture
def game_state():
    """기본 게임 상태 생성"""
    return GameState(
        money=DEFAULT_MONEY,
        reputation=DEFAULT_REPUTATION,
        happiness=DEFAULT_HAPPINESS,
        suffering=DEFAULT_SUFFERING,
        inventory=DEFAULT_INVENTORY,
        staff_fatigue=DEFAULT_STAFF_FATIGUE,
        facility=DEFAULT_FACILITY,
        demand=DEFAULT_DEMAND,
        current_day=1,
        events_history=[]
    )


@pytest.fixture
def event_system(game_state):
    """이벤트 시스템 생성"""
    return EventSystem(game_state)


@pytest.fixture
def sample_event():
    """샘플 이벤트 생성"""
    return Event(
        id="test_event_1",
        names={"ko": "테스트 이벤트", "en": "Test Event"},
        descriptions={"ko": "테스트 이벤트 설명", "en": "Test Event Description"},
        type=EventType.STORY,
        severity=EventSeverity.NORMAL,
        probability=0.5,
        triggers=[
            EventTrigger(
                metric="money",
                condition=">",
                value=TEST_MONEY
            )
        ],
        effects=[
            EventEffect(
                metric="reputation",
                value=10.0,
                is_percentage=False
            )
        ],
        cascade_events=[]
    )


def test_event_registration(event_system, sample_event):
    """이벤트 등록 테스트"""
    event_system.register_event(sample_event)
    assert sample_event.id in event_system.events


def test_get_applicable_events(event_system, sample_event):
    """적용 가능한 이벤트 조회 테스트"""
    event_system.register_event(sample_event)
    applicable_events = event_system.get_applicable_events()
    assert len(applicable_events) == 1
    assert applicable_events[0].id == sample_event.id


def test_event_cooldown(event_system, sample_event):
    """이벤트 쿨다운 테스트"""
    event_system.register_event(sample_event)
    event_system.process_turn()
    assert event_system.events[sample_event.id].cooldown == EVENT_COOLDOWN_DAYS


def test_event_trigger_conditions(event_system, sample_event):
    """이벤트 트리거 조건 테스트"""
    event_system.register_event(sample_event)
    event_system.game_state.money = TEST_MONEY + 1000
    applicable_events = event_system.get_applicable_events()
    assert len(applicable_events) == 1


def test_cascade_events(event_system, sample_event):
    """연쇄 이벤트 테스트"""
    cascade_event = Event(
        id="cascade_event_1",
        names={"ko": "연쇄 이벤트", "en": "Cascade Event"},
        descriptions={"ko": "연쇄 이벤트 설명", "en": "Cascade Event Description"},
        type=EventType.STORY,
        severity=EventSeverity.NORMAL,
        probability=1.0,
        triggers=[],
        effects=[
            EventEffect(
                metric="happiness",
                value=5.0,
                is_percentage=False
            )
        ],
        cascade_events=[]
    )
    sample_event.cascade_events.append(cascade_event)
    event_system.register_event(sample_event)
    event_system.process_turn()
    assert len(event_system.game_state.events_history) == 2 
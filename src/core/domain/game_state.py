"""
게임 상태 도메인 모델
불변 객체로 구현된 게임 상태 관련 도메인 엔티티를 포함합니다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameState:
    """게임 상태 - 절대 불변"""

    money: int
    reputation: int
    happiness: int
    pain: int
    day: int
    events_history: tuple[str, ...] = ()

    def apply_effects(self, effects: dict[str, int]) -> "GameState":
        """효과 적용 시 새 상태 반환"""
        return GameState(
            money=max(0, self.money + effects.get("money", 0)),
            reputation=max(0, min(100, self.reputation + effects.get("reputation", 0))),
            happiness=max(0, min(100, self.happiness + effects.get("happiness", 0))),
            pain=max(0, min(100, self.pain + effects.get("pain", 0))),
            day=self.day + effects.get("day", 0),
            events_history=self.events_history,
        )

    def add_event_to_history(self, event_id: str) -> "GameState":
        """이벤트 히스토리에 추가"""
        return GameState(
            money=self.money,
            reputation=self.reputation,
            happiness=self.happiness,
            pain=self.pain,
            day=self.day,
            events_history=(*self.events_history, event_id),
        )


@dataclass(frozen=True)
class MetricBounds:
    """지표 경계값 - 절대 불변"""

    min_value: int
    max_value: int
    warning_low: int
    warning_high: int

    def is_in_bounds(self, value: int) -> bool:
        """값이 경계 내에 있는지 확인"""
        return self.min_value <= value <= self.max_value

    def is_in_warning_zone(self, value: int) -> bool:
        """값이 경고 구간에 있는지 확인"""
        return (self.min_value <= value <= self.warning_low) or (
            self.warning_high <= value <= self.max_value
        )


@dataclass(frozen=True)
class GameSettings:
    """게임 설정 - 절대 불변"""

    starting_money: int
    starting_reputation: int
    starting_happiness: int
    starting_pain: int
    max_cascade_depth: int
    bankruptcy_threshold: int

    def create_initial_state(self) -> GameState:
        """초기 게임 상태 생성"""
        return GameState(
            money=self.starting_money,
            reputation=self.starting_reputation,
            happiness=self.starting_happiness,
            pain=self.starting_pain,
            day=1,
            events_history=(),
        )

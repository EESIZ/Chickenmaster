"""
이벤트 서비스 어댑터.

이 모듈은 IEventService 인터페이스를 구현하여 이벤트 처리 로직을 제공합니다.
"""

from typing import Any

from src.cascade.ports.event_port import IEventService


class EventServiceAdapter(IEventService):
    """
    IEventService 인터페이스 구현체.

    실제 이벤트 서비스와의 통합을 담당합니다.
    """

    def __init__(self):
        """
        EventServiceAdapter 생성자.
        """
        self._events = {}  # 이벤트 ID -> 이벤트 객체
        self._cooldowns = {}  # 이벤트 ID -> (마지막 발생 턴, 쿨다운 턴 수)

    def get_event_by_id(self, event_id: str) -> Any:
        """
        ID로 이벤트를 조회합니다.

        Args:
            event_id: 이벤트 ID

        Returns:
            조회된 이벤트

        Raises:
            ValueError: 유효하지 않은 이벤트 ID인 경우
        """
        if event_id not in self._events:
            raise ValueError(f"이벤트 ID '{event_id}'를 찾을 수 없습니다.")
        return self._events[event_id]

    def apply_event_effects(self, event: Any, game_state: Any) -> Any:
        """
        이벤트 효과를 적용한 새 게임 상태를 반환합니다.

        Args:
            event: 적용할 이벤트
            game_state: 현재 게임 상태

        Returns:
            이벤트 효과가 적용된 새 게임 상태
        """
        # 실제 구현에서는 이벤트 효과를 적용하는 로직이 필요합니다.
        # 이 어댑터는 독립적인 테스트를 위한 Mock 구현입니다.
        return game_state

    def evaluate_trigger_condition(self, condition: dict[str, Any], game_state: Any) -> bool:
        """
        트리거 조건을 평가합니다.

        Args:
            condition: 트리거 조건
            game_state: 현재 게임 상태

        Returns:
            조건이 충족되면 True, 아니면 False
        """
        # 실제 구현에서는 조건을 평가하는 로직이 필요합니다.
        # 이 어댑터는 독립적인 테스트를 위한 Mock 구현입니다.
        return True

    def get_applicable_events(self, game_state: Any) -> list[Any]:
        """
        현재 상태에서 발생 가능한 이벤트 목록을 반환합니다.

        Args:
            game_state: 현재 게임 상태

        Returns:
            발생 가능한 이벤트 목록
        """
        # 실제 구현에서는 발생 가능한 이벤트를 필터링하는 로직이 필요합니다.
        # 이 어댑터는 독립적인 테스트를 위한 Mock 구현입니다.
        return list(self._events.values())

    def check_event_cooldown(self, event_id: str, current_turn: int) -> bool:
        """
        이벤트 쿨다운 상태를 확인합니다.

        Args:
            event_id: 이벤트 ID
            current_turn: 현재 게임 턴

        Returns:
            쿨다운이 끝났으면 True, 아직 쿨다운 중이면 False
        """
        if event_id not in self._cooldowns:
            return True

        last_turn, cooldown = self._cooldowns[event_id]
        return current_turn - last_turn >= cooldown

    def evaluate_event_probability(self, event: Any, game_state: Any) -> float:
        """
        이벤트 발생 확률을 계산합니다.

        Args:
            event: 이벤트
            game_state: 현재 게임 상태

        Returns:
            이벤트 발생 확률 (0.0~1.0)
        """
        # 실제 구현에서는 확률을 계산하는 로직이 필요합니다.
        # 이 어댑터는 독립적인 테스트를 위한 Mock 구현입니다.
        return 1.0

    def register_event(self, event_id: str, event: Any, cooldown: int = 0) -> None:
        """
        이벤트를 등록합니다.

        Args:
            event_id: 이벤트 ID
            event: 이벤트 객체
            cooldown: 쿨다운 턴 수 (기본값: 0)
        """
        self._events[event_id] = event
        if cooldown > 0:
            self._cooldowns[event_id] = (-cooldown, cooldown)  # 초기에는 쿨다운 없음

    def update_cooldown(self, event_id: str, current_turn: int) -> None:
        """
        이벤트 쿨다운을 업데이트합니다.

        Args:
            event_id: 이벤트 ID
            current_turn: 현재 게임 턴
        """
        if event_id in self._cooldowns:
            _, cooldown = self._cooldowns[event_id]
            self._cooldowns[event_id] = (current_turn, cooldown)

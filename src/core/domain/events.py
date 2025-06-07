"""
이벤트 도메인 모델
불변 객체로 구현된 이벤트 관련 도메인 엔티티를 포함합니다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """이벤트 도메인 객체 - 절대 불변"""

    id: str
    type: str
    name_ko: str
    name_en: str
    text_ko: str
    text_en: str
    effects: dict[str, int]
    conditions: tuple[str, ...]  # list 아닌 tuple 사용
    probability: float
    cooldown: int
    category: str
    tags: tuple[str, ...] = ()

    def with_modified_effects(self, new_effects: dict[str, int]) -> "Event":
        """수정이 필요한 경우 새 객체 생성"""
        return Event(
            id=self.id,
            type=self.type,
            name_ko=self.name_ko,
            name_en=self.name_en,
            text_ko=self.text_ko,
            text_en=self.text_en,
            effects=new_effects,
            conditions=self.conditions,
            probability=self.probability,
            cooldown=self.cooldown,
            category=self.category,
            tags=self.tags,
        )


@dataclass(frozen=True)
class EventChoice:
    """이벤트 선택지 - 절대 불변"""

    id: str
    text_ko: str
    text_en: str
    effects: dict[str, int]

    def with_modified_effects(self, new_effects: dict[str, int]) -> "EventChoice":
        """수정이 필요한 경우 새 객체 생성"""
        return EventChoice(
            id=self.id, text_ko=self.text_ko, text_en=self.text_en, effects=new_effects
        )


@dataclass(frozen=True)
class EventTrigger:
    """이벤트 트리거 조건 - 절대 불변"""

    metric: str
    operator: str
    value: int

    def evaluate(self, current_value: int) -> bool:
        """트리거 조건 평가"""
        if self.operator == ">":
            return current_value > self.value
        elif self.operator == ">=":
            return current_value >= self.value
        elif self.operator == "<":
            return current_value < self.value
        elif self.operator == "<=":
            return current_value <= self.value
        elif self.operator == "==":
            return current_value == self.value
        else:
            return False

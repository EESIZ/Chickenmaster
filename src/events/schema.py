"""
이벤트 스키마 정의 및 검증
"""

from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class EventEffect(BaseModel):
    """이벤트 효과 모델"""

    metric: str
    formula: str

    model_config = ConfigDict(strict=True)


class EventChoice(BaseModel):
    """이벤트 선택지 모델"""

    text_ko: str
    text_en: str
    effects: dict[str, float]
    cascade_events: list[str] = Field(default_factory=list)

    model_config = ConfigDict(strict=True)


class EventTrigger(BaseModel):
    """이벤트 트리거 모델"""

    metric: str
    condition: str
    value: float

    model_config = ConfigDict(strict=True)


class Event(BaseModel):
    """이벤트 모델"""

    id: str
    type: str
    category: str
    name_ko: str
    name_en: str
    text_ko: str
    text_en: str
    effects: list[EventEffect]
    choices: list[EventChoice]
    tags: list[str] = Field(default_factory=list)
    probability: float = Field(ge=0.0, le=1.0)
    cooldown: int = Field(ge=0)
    priority: int = Field(default=0)
    trigger: EventTrigger | None = None
    last_fired: int | None = None

    model_config = ConfigDict(strict=True)


class EventContainer(BaseModel, Generic[T]):
    """이벤트 컨테이너 모델"""

    events: list[T]
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(strict=True)


def load_events_from_json(file_path: Path) -> EventContainer[Event]:
    """JSON 파일에서 이벤트 로드"""
    import json

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    return EventContainer[Event].model_validate(data)


def load_events_from_toml(file_path: Path) -> EventContainer[Event]:
    """TOML 파일에서 이벤트 로드"""
    import tomllib

    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    # TOML 파일이 [[events]] 배열을 직접 반환한다고 가정하고,
    # EventContainer가 {"events": [...]} 형태를 기대하므로 래핑합니다.
    if isinstance(data, dict) and "events" in data and isinstance(data["events"], list):
        # 이미 올바른 형태인 경우 (예: 최상위에 events = [...] 가 있는 경우)
        return EventContainer[Event].model_validate(data)
    elif isinstance(data, list):
        # TOML 파일이 이벤트 객체의 리스트를 직접 반환하는 경우 (현재 data/events.toml 형태)
        return EventContainer[Event].model_validate({"events": data})
    elif isinstance(data, dict) and len(data) > 0 and isinstance(next(iter(data.values())), list):
        # heuristic: dictionary인데 첫번째 value가 list of event인 경우 [[events]] 같은 키가 있었던것으로 가정.
        # ex: {"events": [...]} or {"something_else": [...]}
        # 이 경우 data.values()의 첫번째 list를 events로 간주. (단, TOML에 하나의 최상위 배열만 있다고 가정)
        potential_events_list = next(iter(data.values()))
        if all(isinstance(item, dict) for item in potential_events_list):
            return EventContainer[Event].model_validate({"events": potential_events_list})

    raise ValueError(
        "TOML 파일의 이벤트 데이터 형식이 올바르지 않습니다. 최상위에 'events' 키가 있거나 이벤트 객체의 리스트여야 합니다."
    )


def save_events_to_json(
    events: EventContainer[Event] | list[Event],
    file_path: Path,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """이벤트를 JSON 파일로 저장"""
    import json
    from enum import Enum

    def enum_serializer(obj):
        """Enum 객체를 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, Enum):
            return obj.name
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    with open(file_path, "w", encoding="utf-8") as f:
        if isinstance(events, list):
            # 리스트인 경우 EventContainer로 감싸기
            container = EventContainer(events=events)
            json.dump(
                container.model_dump(),
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                default=enum_serializer,
            )
        else:
            # 이미 EventContainer인 경우
            json.dump(
                events.model_dump(),
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                default=enum_serializer,
            )

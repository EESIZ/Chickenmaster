"""
이벤트 스키마 정의 및 검증
"""

from typing import Any, TypeVar, Generic
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict

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
    trigger: EventTrigger | None = None
    
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
    
    return EventContainer[Event].model_validate(data)

def save_events_to_json(
    events: EventContainer[Event], 
    file_path: Path,
    *,
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """이벤트를 JSON 파일로 저장"""
    import json
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            events.model_dump(),
            f,
            indent=indent,
            ensure_ascii=ensure_ascii
        )

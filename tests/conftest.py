"""
pytest 설정 및 fixture
"""

from pathlib import Path
from collections.abc import Generator

import pytest
from pydantic import BaseModel, Field

from src.events.schema import Event, EventContainer, EventEffect, EventChoice
from src.events.validators.base import ValidationResult
from src.events.validators.specific import (
    CulturalValidator,
    DuplicateValidator,
    FormulaValidator,
    TradeoffValidator
)

# 테스트 데이터 디렉토리
TEST_DATA_DIR = Path(__file__).parent / "data"

class MockEvent(BaseModel):
    """테스트용 이벤트 모델"""
    id: str = "test_event_001"
    type: str = "RANDOM"
    category: str = "test"
    name_ko: str = "테스트 이벤트"
    name_en: str = "Test Event"
    text_ko: str = "치킨집 테스트 이벤트입니다"
    text_en: str = "This is a test event"
    effects: list[EventEffect] = Field(default_factory=list)
    choices: list[EventChoice] = Field(default_factory=list)
    probability: float = 0.5
    cooldown: int = 0
    tags: list[str] = Field(default_factory=list)
    trigger: None = None

@pytest.fixture
def test_data_dir() -> Path:
    """테스트 데이터 디렉토리 fixture"""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    return TEST_DATA_DIR

@pytest.fixture
def mock_event() -> Event:
    """기본 테스트 이벤트 fixture"""
    return Event.model_validate(MockEvent().model_dump())

@pytest.fixture
def mock_event_container(mock_event: Event) -> EventContainer[Event]:
    """테스트 이벤트 컨테이너 fixture"""
    return EventContainer[Event](
        events=[mock_event],
        metadata={"test": True}
    )

@pytest.fixture
def cultural_validator() -> CulturalValidator:
    """문화적 연관성 검증기 fixture"""
    return CulturalValidator()

@pytest.fixture
def duplicate_validator() -> DuplicateValidator:
    """중복 검증기 fixture"""
    return DuplicateValidator()

@pytest.fixture
def tradeoff_validator() -> TradeoffValidator:
    """트레이드오프 균형 검증기 fixture"""
    return TradeoffValidator()

@pytest.fixture
def formula_validator() -> FormulaValidator:
    """수식 안전성 검증기 fixture"""
    return FormulaValidator()

@pytest.fixture
def temp_json_file(test_data_dir: Path) -> Generator[Path, None, None]:
    """임시 JSON 파일 fixture"""
    file_path = test_data_dir / "test_events.json"
    yield file_path
    if file_path.exists():
        file_path.unlink()

@pytest.fixture
def temp_toml_file(test_data_dir: Path) -> Generator[Path, None, None]:
    """임시 TOML 파일 fixture"""
    file_path = test_data_dir / "test_events.toml"
    yield file_path
    if file_path.exists():
        file_path.unlink()

@pytest.fixture
def valid_validation_result() -> ValidationResult:
    """유효한 검증 결과 fixture"""
    return ValidationResult(is_valid=True)

@pytest.fixture
def invalid_validation_result() -> ValidationResult:
    """유효하지 않은 검증 결과 fixture"""
    return ValidationResult(
        is_valid=False,
        errors=["테스트 오류"],
        warnings=["테스트 경고"]
    ) 
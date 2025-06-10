import dataclasses
import pytest

from app.core.domain.metrics import MetricEnum
from app.core.domain.narrative_response import (
    NarrativeResponse,
    MetricChange,
    SuggestedEvent,
    StoryPattern,
)


@pytest.fixture
def sample_metric_change():
    return MetricChange(
        metric=MetricEnum.MONEY, change=1000.0, reason_ko="매출 증가", reason_en="Revenue increase"
    )


@pytest.fixture
def sample_suggested_event():
    return SuggestedEvent(
        id="test_event",
        severity=0.5,
        category="daily_routine",
        name_ko="테스트 이벤트",
        name_en="Test Event",
        text_ko="테스트 이벤트 설명",
        text_en="Test event description",
        probability=0.3,
        conditions=["money > 1000"],
        tags=["test", "routine"],
    )


@pytest.fixture
def sample_story_pattern():
    return StoryPattern(
        id="test_pattern",
        name_ko="테스트 패턴",
        name_en="Test Pattern",
        description_ko="테스트 패턴 설명",
        description_en="Test pattern description",
        severity=0.5,
        related_metrics=[MetricEnum.MONEY, MetricEnum.REPUTATION],
        tags=["test", "pattern"],
    )


@pytest.fixture
def narrative_response(sample_metric_change, sample_suggested_event, sample_story_pattern):
    return NarrativeResponse(
        narrative_ko="테스트 내러티브",
        narrative_en="Test narrative",
        suggested_event=sample_suggested_event,
        story_pattern=sample_story_pattern,
        metric_changes=[sample_metric_change],
        severity=0.5,
        tags=["test", "narrative"],
    )


def test_narrative_response_creation(
    narrative_response, sample_metric_change, sample_suggested_event, sample_story_pattern
):
    """NarrativeResponse 생성 테스트"""
    assert narrative_response.narrative_ko == "테스트 내러티브"
    assert narrative_response.narrative_en == "Test narrative"
    assert narrative_response.suggested_event == sample_suggested_event
    assert narrative_response.story_pattern == sample_story_pattern
    assert narrative_response.metric_changes == [sample_metric_change]
    assert narrative_response.severity == 0.5
    assert narrative_response.tags == ["test", "narrative"]


def test_has_suggested_event(narrative_response):
    """제안된 이벤트 존재 여부 테스트"""
    assert narrative_response.has_suggested_event

    # 제안된 이벤트가 없는 경우
    response_without_event = NarrativeResponse(
        narrative_ko="테스트", narrative_en="Test", suggested_event=None
    )
    assert not response_without_event.has_suggested_event


def test_has_story_pattern(narrative_response):
    """스토리 패턴 존재 여부 테스트"""
    assert narrative_response.has_story_pattern

    # 스토리 패턴이 없는 경우
    response_without_pattern = NarrativeResponse(
        narrative_ko="테스트", narrative_en="Test", story_pattern=None
    )
    assert not response_without_pattern.has_story_pattern


def test_get_metric_changes_by_metric(narrative_response, sample_metric_change):
    """메트릭별 변화 목록 조회 테스트"""
    changes = narrative_response.get_metric_changes_by_metric(MetricEnum.MONEY)
    assert len(changes) == 1
    assert changes[0] == sample_metric_change

    # 존재하지 않는 메트릭
    changes = narrative_response.get_metric_changes_by_metric(MetricEnum.REPUTATION)
    assert len(changes) == 0


def test_get_total_metric_change(narrative_response):
    """메트릭 총 변화량 계산 테스트"""
    total_change = narrative_response.get_total_metric_change(MetricEnum.MONEY)
    assert total_change == 1000.0

    # 존재하지 않는 메트릭
    total_change = narrative_response.get_total_metric_change(MetricEnum.REPUTATION)
    assert total_change == 0.0


def test_immutability(narrative_response):
    """불변성 테스트"""
    with pytest.raises(dataclasses.FrozenInstanceError):
        narrative_response.narrative_ko = "새로운 내러티브"

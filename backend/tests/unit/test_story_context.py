from datetime import datetime
import dataclasses
import pytest

from app.core.domain.metrics import MetricEnum
from app.core.domain.story_context import StoryContext, MetricSnapshot, GameEvent


@pytest.fixture
def sample_metrics():
    return {
        MetricEnum.MONEY: 1000.0,
        MetricEnum.REPUTATION: 50.0,
        MetricEnum.HAPPINESS: 60.0,
        MetricEnum.SUFFERING: 40.0,
        MetricEnum.DEMAND: 70.0,
        MetricEnum.INVENTORY: 80.0,
        MetricEnum.STAFF_FATIGUE: 30.0,
        MetricEnum.FACILITY: 75.0,
    }


@pytest.fixture
def sample_metric_snapshot(sample_metrics):
    return MetricSnapshot(
        day=1,
        timestamp=datetime.now(),
        metrics=sample_metrics,
        events=["event1", "event2"],
        modifier="SimpleSeesawModifier"
    )


@pytest.fixture
def sample_game_event():
    return GameEvent(
        id="test_event",
        day=1,
        severity=0.5,
        category="daily_routine",
        name_ko="테스트 이벤트",
        name_en="Test Event",
        text_ko="테스트 이벤트 설명",
        text_en="Test event description"
    )


@pytest.fixture
def story_context(sample_metrics, sample_metric_snapshot, sample_game_event):
    return StoryContext(
        current_day=1,
        total_days=730,
        current_metrics=sample_metrics,
        metrics_history=[sample_metric_snapshot],
        recent_events=[sample_game_event],
        story_patterns=["pattern1", "pattern2"]
    )


def test_story_context_creation(story_context, sample_metrics):
    """StoryContext 생성 테스트"""
    assert story_context.current_day == 1
    assert story_context.total_days == 730
    assert story_context.current_metrics == sample_metrics
    assert len(story_context.metrics_history) == 1
    assert len(story_context.recent_events) == 1
    assert len(story_context.story_patterns) == 2


def test_game_progression(story_context):
    """게임 진행률 계산 테스트"""
    assert story_context.game_progression == pytest.approx(1/730)


def test_game_stages(story_context):
    """게임 단계 판단 테스트"""
    assert story_context.is_early_game
    assert not story_context.is_mid_game
    assert not story_context.is_late_game


def test_metric_trend(story_context):
    """메트릭 추세 계산 테스트"""
    # 단일 스냅샷으로는 추세를 계산할 수 없음
    assert story_context.get_metric_trend(MetricEnum.MONEY) == 0.0

    # 두 개의 스냅샷으로 추세 계산
    new_snapshot = MetricSnapshot(
        day=2,
        timestamp=datetime.now(),
        metrics={MetricEnum.MONEY: 1100.0},  # 100 증가
        events=[],
        modifier=None
    )
    context_with_trend = StoryContext(
        current_day=2,
        total_days=730,
        current_metrics={MetricEnum.MONEY: 1100.0},
        metrics_history=[story_context.metrics_history[0], new_snapshot],
        recent_events=[],
        story_patterns=[]
    )
    assert context_with_trend.get_metric_trend(MetricEnum.MONEY) == pytest.approx(100.0)


def test_recent_events_by_category(story_context, sample_game_event):
    """카테고리별 이벤트 필터링 테스트"""
    events = story_context.get_recent_events_by_category("daily_routine")
    assert len(events) == 1
    assert events[0] == sample_game_event

    # 존재하지 않는 카테고리
    events = story_context.get_recent_events_by_category("non_existent")
    assert len(events) == 0


def test_metric_history(story_context, sample_metrics):
    """메트릭 히스토리 조회 테스트"""
    history = story_context.get_metric_history(MetricEnum.MONEY)
    assert len(history) == 1
    assert history[0] == sample_metrics[MetricEnum.MONEY]


def test_immutability(story_context):
    """불변성 테스트"""
    with pytest.raises(dataclasses.FrozenInstanceError):
        story_context.current_day = 2 
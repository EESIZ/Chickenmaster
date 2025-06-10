import dataclasses
import pytest

from app.core.domain.metrics import MetricEnum
from app.core.domain.story_pattern import (
    StoryPattern,
    PatternCategory,
    PatternTrigger,
    PatternEffect,
)


@pytest.fixture
def sample_trigger():
    return PatternTrigger(
        metric=MetricEnum.MONEY,
        condition="greater_than",
        value=1000.0
    )


@pytest.fixture
def sample_effect():
    return PatternEffect(
        metric=MetricEnum.REPUTATION,
        formula="value + 10",
        message_ko="평판이 증가했습니다",
        message_en="Reputation increased"
    )


@pytest.fixture
def story_pattern(sample_trigger, sample_effect):
    return StoryPattern(
        id="test_pattern",
        name_ko="테스트 패턴",
        name_en="Test Pattern",
        description_ko="테스트 패턴 설명",
        description_en="Test pattern description",
        category=PatternCategory.TRADEOFF,
        severity=0.5,
        trigger=sample_trigger,
        effects=[sample_effect],
        related_metrics=[MetricEnum.MONEY, MetricEnum.REPUTATION],
        tags=["test", "pattern"],
        cooldown=5,
        probability=0.8
    )


def test_story_pattern_creation(story_pattern, sample_trigger, sample_effect):
    """StoryPattern 생성 테스트"""
    assert story_pattern.id == "test_pattern"
    assert story_pattern.name_ko == "테스트 패턴"
    assert story_pattern.name_en == "Test Pattern"
    assert story_pattern.category == PatternCategory.TRADEOFF
    assert story_pattern.severity == 0.5
    assert story_pattern.trigger == sample_trigger
    assert story_pattern.effects == [sample_effect]
    assert story_pattern.cooldown == 5
    assert story_pattern.probability == 0.8


def test_affected_metrics(story_pattern):
    """영향받는 메트릭 집합 테스트"""
    affected = story_pattern.affected_metrics
    assert MetricEnum.MONEY in affected  # trigger metric
    assert MetricEnum.REPUTATION in affected  # effect metric
    assert len(affected) == 2  # trigger + effect metrics


def test_is_triggered(story_pattern):
    """트리거 조건 테스트"""
    # greater_than 조건
    assert story_pattern.is_triggered(1500.0)  # 1000.0보다 큼
    assert not story_pattern.is_triggered(500.0)  # 1000.0보다 작음

    # less_than 조건
    trigger_less = PatternTrigger(
        metric=MetricEnum.MONEY,
        condition="less_than",
        value=1000.0
    )
    pattern_less = dataclasses.replace(story_pattern, trigger=trigger_less)
    assert pattern_less.is_triggered(500.0)  # 1000.0보다 작음
    assert not pattern_less.is_triggered(1500.0)  # 1000.0보다 큼

    # between 조건
    trigger_between = PatternTrigger(
        metric=MetricEnum.MONEY,
        condition="between",
        value=1000.0,
        secondary_value=2000.0
    )
    pattern_between = dataclasses.replace(story_pattern, trigger=trigger_between)
    assert pattern_between.is_triggered(1500.0)  # 1000.0과 2000.0 사이
    assert not pattern_between.is_triggered(500.0)  # 1000.0보다 작음
    assert not pattern_between.is_triggered(2500.0)  # 2000.0보다 큼


def test_get_effect_value(story_pattern, sample_effect):
    """효과 값 계산 테스트"""
    # 덧셈 효과
    assert story_pattern.get_effect_value(sample_effect, 50.0) == 60.0

    # 뺄셈 효과
    effect_subtract = PatternEffect(
        metric=MetricEnum.REPUTATION,
        formula="value - 10",
        message_ko="평판이 감소했습니다",
        message_en="Reputation decreased"
    )
    assert story_pattern.get_effect_value(effect_subtract, 50.0) == 40.0

    # 지원하지 않는 수식
    effect_invalid = PatternEffect(
        metric=MetricEnum.REPUTATION,
        formula="value * 2",
        message_ko="평판이 변화했습니다",
        message_en="Reputation changed"
    )
    assert story_pattern.get_effect_value(effect_invalid, 50.0) == 50.0


def test_immutability(story_pattern):
    """불변성 테스트"""
    with pytest.raises(dataclasses.FrozenInstanceError):
        story_pattern.name_ko = "새로운 패턴" 
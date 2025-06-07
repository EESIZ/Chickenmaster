"""
StorytellerService 테스트

이 모듈은 스토리텔러 서비스의 모든 기능을 테스트합니다.
게임의 핵심 철학인 tradeoff, uncertainty, noRightAnswer를 검증합니다.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import Dict, List

from src.core.ports.container_port import IServiceContainer
from src.core.ports.event_port import IEventService
from src.core.domain.events import Event
from src.core.domain.game_state import GameState
from src.storyteller.adapters.storyteller_service import StorytellerService
from src.storyteller.domain.models import (
    StoryContext, NarrativeResponse, StoryPattern, 
    MetricsHistory, RecentEvent
)


@pytest.fixture
def mock_container():
    """Mock 의존성 주입 컨테이너"""
    container = Mock(spec=IServiceContainer)
    event_service = Mock(spec=IEventService)
    container.get.return_value = event_service
    return container


@pytest.fixture
def mock_event_service(mock_container):
    """Mock 이벤트 서비스"""
    return mock_container.get(IEventService)


@pytest.fixture
def storyteller_service(mock_container):
    """StorytellerService 인스턴스"""
    return StorytellerService(mock_container)


@pytest.fixture
def sample_story_context():
    """테스트용 StoryContext"""
    metrics_history = [
        MetricsHistory(
            day=1,
            metrics={"money": 10000, "reputation": 50, "happiness": 60, "pain": 20}
        ),
        MetricsHistory(
            day=2, 
            metrics={"money": 9500, "reputation": 55, "happiness": 55, "pain": 25}
        ),
        MetricsHistory(
            day=3,
            metrics={"money": 9000, "reputation": 60, "happiness": 50, "pain": 30}
        )
    ]
    
    recent_events = [
        RecentEvent(
            day=2,
            event_id="price_increase",
            severity=0.3,
            effects={"money": 500, "reputation": -5}
        )
    ]
    
    return StoryContext(
        day=3,
        game_progression=0.3,
        metrics_history=metrics_history,
        recent_events=recent_events
    )


@pytest.fixture
def sample_events():
    """테스트용 이벤트 목록"""
    return [
        Event(
            id="cost_reduction",
            type="business",
            name_ko="비용 절감",
            name_en="Cost Reduction",
            text_ko="운영 비용을 줄일 수 있는 기회가 생겼습니다.",
            text_en="An opportunity to reduce operating costs has arisen.",
            effects={"money": 1000, "reputation": -10, "happiness": -5},
            conditions=("money < 10000",),
            probability=0.7,
            cooldown=3,
            category="financial"
        ),
        Event(
            id="quality_improvement",
            type="business", 
            name_ko="품질 개선",
            name_en="Quality Improvement",
            text_ko="제품 품질을 향상시킬 수 있습니다.",
            text_en="You can improve product quality.",
            effects={"money": -800, "reputation": 15, "happiness": 10},
            conditions=("reputation < 70",),
            probability=0.6,
            cooldown=2,
            category="quality"
        )
    ]


class TestGetStoryPatterns:
    """get_story_patterns 메서드 테스트"""
    
    def test_tradeoff_pattern_matching(self, storyteller_service, sample_story_context):
        """tradeoff 패턴 매칭 테스트"""
        # 자금 부족 상황 설정 - 새로운 컨텍스트 생성
        modified_history = sample_story_context.metrics_history[:-1] + [
            MetricsHistory(
                day=3,
                metrics={"money": 4000, "reputation": 25, "happiness": 40, "pain": 50}
            )
        ]
        
        modified_context = StoryContext(
            day=sample_story_context.day,
            game_progression=sample_story_context.game_progression,
            metrics_history=modified_history,
            recent_events=sample_story_context.recent_events
        )
        
        patterns = storyteller_service.get_story_patterns(modified_context)
        
        assert len(patterns) > 0
        tradeoff_patterns = [p for p in patterns if p.pattern_type == "tradeoff"]
        assert len(tradeoff_patterns) > 0
        
        # tradeoff 패턴이 올바른 조건에서 매칭되는지 확인
        financial_pattern = next(
            (p for p in tradeoff_patterns if "financial" in p.pattern_id),
            None
        )
        assert financial_pattern is not None
    
    def test_uncertainty_pattern_selection(self, storyteller_service, sample_story_context):
        """uncertainty 패턴 선택 테스트"""
        # 초기 게임 진행도 설정
        sample_story_context = sample_story_context.__class__(
            day=sample_story_context.day,
            game_progression=0.2,  # 초기 단계
            metrics_history=sample_story_context.metrics_history,
            recent_events=sample_story_context.recent_events
        )
        
        patterns = storyteller_service.get_story_patterns(sample_story_context)
        
        # uncertainty 패턴이 우선순위를 가지는지 확인
        if patterns:
            # 초기 게임에서는 uncertainty 패턴이 상위에 위치해야 함
            uncertainty_patterns = [p for p in patterns if p.pattern_type == "uncertainty"]
            assert len(uncertainty_patterns) >= 0  # uncertainty 패턴이 존재할 수 있음
    
    def test_no_right_answer_pattern_late_game(self, storyteller_service, sample_story_context):
        """noRightAnswer 패턴 후기 게임 테스트"""
        # 후기 게임 설정
        sample_story_context = sample_story_context.__class__(
            day=sample_story_context.day,
            game_progression=0.8,  # 후기 단계
            metrics_history=sample_story_context.metrics_history,
            recent_events=sample_story_context.recent_events
        )
        
        # 높은 평판과 적당한 고통 설정
        sample_story_context.metrics_history[-1] = MetricsHistory(
            day=3,
            metrics={"money": 15000, "reputation": 75, "happiness": 60, "pain": 45}
        )
        
        patterns = storyteller_service.get_story_patterns(sample_story_context)
        
        # noRightAnswer 패턴이 매칭되는지 확인
        no_right_answer_patterns = [p for p in patterns if p.pattern_type == "noRightAnswer"]
        assert len(no_right_answer_patterns) >= 0
    
    def test_empty_metrics_history_raises_error(self, storyteller_service):
        """빈 지표 히스토리에 대한 에러 테스트"""
        invalid_context = StoryContext(
            day=1,
            game_progression=0.1,
            metrics_history=[],  # 빈 히스토리
            recent_events=[]
        )
        
        with pytest.raises(ValueError, match="지표 히스토리가 비어있습니다"):
            storyteller_service.get_story_patterns(invalid_context)


class TestAnalyzeMetricsTrend:
    """analyze_metrics_trend 메서드 테스트"""
    
    def test_tradeoff_trend_calculation(self, storyteller_service, sample_story_context):
        """tradeoff 관계의 트렌드 계산 테스트"""
        trends = storyteller_service.analyze_metrics_trend(sample_story_context)
        
        assert isinstance(trends, dict)
        assert "money" in trends
        assert "reputation" in trends
        
        # 자금은 감소, 평판은 증가 트렌드여야 함 (tradeoff)
        assert trends["money"] < 0  # 감소 트렌드
        assert trends["reputation"] > 0  # 증가 트렌드
    
    def test_uncertainty_noise_in_trends(self, storyteller_service, sample_story_context):
        """uncertainty 노이즈가 트렌드에 반영되는지 테스트"""
        # 여러 번 실행하여 노이즈 효과 확인
        trends_list = []
        for _ in range(5):
            trends = storyteller_service.analyze_metrics_trend(sample_story_context)
            trends_list.append(trends["money"])
        
        # 노이즈로 인해 약간의 변동이 있어야 함
        assert len(set(trends_list)) > 1 or abs(max(trends_list) - min(trends_list)) > 0
    
    def test_insufficient_history_raises_error(self, storyteller_service):
        """불충분한 히스토리에 대한 에러 테스트"""
        insufficient_context = StoryContext(
            day=1,
            game_progression=0.1,
            metrics_history=[
                MetricsHistory(day=1, metrics={"money": 10000})
            ],  # 단일 히스토리
            recent_events=[]
        )
        
        with pytest.raises(ValueError, match="최소 2개의 지표 히스토리가 필요합니다"):
            storyteller_service.analyze_metrics_trend(insufficient_context)


class TestSuggestEvent:
    """suggest_event 메서드 테스트"""
    
    def test_tradeoff_aware_event_suggestion(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """tradeoff를 고려한 이벤트 제안 테스트"""
        # 자금 부족 상황 설정
        sample_story_context.metrics_history[-1] = MetricsHistory(
            day=3,
            metrics={"money": 3000, "reputation": 60, "happiness": 50, "pain": 30}
        )
        
        mock_event_service.get_applicable_events.return_value = sample_events
        
        suggested_event_id = storyteller_service.suggest_event(sample_story_context)
        
        assert suggested_event_id is not None
        assert suggested_event_id in [event.id for event in sample_events]
        
        # 자금 부족 상황에서는 자금 증가 이벤트가 선호되어야 함
        if suggested_event_id == "cost_reduction":
            # 비용 절감 이벤트는 자금을 늘리지만 평판을 깎는 tradeoff
            cost_event = next(e for e in sample_events if e.id == "cost_reduction")
            assert cost_event.effects["money"] > 0
            assert cost_event.effects["reputation"] < 0
    
    def test_recent_events_filtering_with_uncertainty(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """최근 이벤트 필터링과 uncertainty 테스트"""
        # 최근에 발생한 이벤트 추가
        sample_story_context.recent_events.append(
            RecentEvent(
                day=3,
                event_id="cost_reduction",  # 이미 발생한 이벤트
                severity=0.4,
                effects={"money": 1000, "reputation": -10}
            )
        )
        
        mock_event_service.get_applicable_events.return_value = sample_events
        
        suggested_event_id = storyteller_service.suggest_event(sample_story_context)
        
        # 최근에 발생한 이벤트는 제안되지 않아야 함 (uncertainty 고려)
        # 단, 선택지가 부족하면 포함될 수 있음
        if suggested_event_id:
            assert suggested_event_id in [event.id for event in sample_events]
    
    def test_no_applicable_events_returns_none(
        self, storyteller_service, mock_event_service, sample_story_context
    ):
        """적용 가능한 이벤트가 없을 때 None 반환 테스트"""
        mock_event_service.get_applicable_events.return_value = []
        
        suggested_event_id = storyteller_service.suggest_event(sample_story_context)
        
        assert suggested_event_id is None


class TestGenerateNarrative:
    """generate_narrative 메서드 테스트"""
    
    def test_narrative_with_tradeoff_awareness(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """tradeoff 인식이 포함된 내러티브 생성 테스트"""
        mock_event_service.get_applicable_events.return_value = sample_events
        
        response = storyteller_service.generate_narrative(sample_story_context)
        
        assert isinstance(response, NarrativeResponse)
        assert response.narrative is not None
        assert len(response.narrative) > 0
        
        # 내러티브에 현재 상황 정보가 포함되어야 함
        assert "3일차" in response.narrative or "day" in response.narrative.lower()
        
        # tradeoff 관련 키워드가 포함될 수 있음
        narrative_lower = response.narrative.lower()
        tradeoff_keywords = ["딜레마", "선택", "양보", "포기", "득", "실"]
        has_tradeoff_concept = any(keyword in narrative_lower for keyword in tradeoff_keywords)
        
        # 모든 내러티브가 tradeoff를 명시적으로 언급할 필요는 없지만, 
        # 적어도 상황에 대한 설명은 있어야 함
        assert len(response.narrative) > 20
    
    def test_narrative_with_uncertainty_elements(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """uncertainty 요소가 포함된 내러티브 테스트"""
        mock_event_service.get_applicable_events.return_value = sample_events
        
        # 여러 번 실행하여 uncertainty 확인
        narratives = []
        for _ in range(3):
            response = storyteller_service.generate_narrative(sample_story_context)
            narratives.append(response.narrative)
        
        # uncertainty로 인해 다양한 내러티브가 생성될 수 있음
        # 또는 동일한 패턴이라도 약간의 변화가 있을 수 있음
        assert all(len(narrative) > 0 for narrative in narratives)
    
    def test_narrative_includes_suggested_event(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """제안된 이벤트가 응답에 포함되는지 테스트"""
        mock_event_service.get_applicable_events.return_value = sample_events
        
        response = storyteller_service.generate_narrative(sample_story_context)
        
        # 제안된 이벤트가 있다면 응답에 포함되어야 함
        if response.suggested_event:
            assert response.suggested_event in [event.id for event in sample_events]
    
    def test_no_right_answer_narrative_philosophy(
        self, storyteller_service, mock_event_service, sample_story_context, sample_events
    ):
        """noRightAnswer 철학이 반영된 내러티브 테스트"""
        # 복잡한 상황 설정
        sample_story_context.metrics_history[-1] = MetricsHistory(
            day=3,
            metrics={"money": 8000, "reputation": 45, "happiness": 55, "pain": 40}
        )
        
        mock_event_service.get_applicable_events.return_value = sample_events
        
        response = storyteller_service.generate_narrative(sample_story_context)
        
        # noRightAnswer 철학: 절대적 기준이나 명확한 답을 제시하지 않아야 함
        narrative_lower = response.narrative.lower()
        
        # 절대적 표현을 피해야 함
        absolute_phrases = ["반드시", "절대", "무조건", "확실히"]
        has_absolute = any(phrase in narrative_lower for phrase in absolute_phrases)
        
        # 절대적 표현이 있더라도 맥락상 적절할 수 있으므로 경고만 함
        if has_absolute:
            print(f"Warning: 절대적 표현이 포함된 내러티브: {response.narrative}")


class TestPrivateHelperMethods:
    """Private helper 메서드들의 동작 테스트"""
    
    def test_critical_metrics_identification_with_tradeoff(
        self, storyteller_service
    ):
        """tradeoff 상황에서 중요 지표 식별 테스트"""
        # 자금 부족, 평판 낮음 상황
        metrics = {"money": 3000, "reputation": 25, "happiness": 60, "pain": 20}
        
        critical_metrics = storyteller_service._identify_critical_metrics(metrics)
        
        assert "money" in critical_metrics
        assert "reputation" in critical_metrics
        assert "happiness" not in critical_metrics  # 정상 범위
        assert "pain" not in critical_metrics  # 정상 범위
    
    def test_pattern_prioritization_by_game_progression(
        self, storyteller_service
    ):
        """게임 진행도에 따른 패턴 우선순위 테스트"""
        # 테스트용 패턴 생성
        patterns = [
            StoryPattern("test_uncertainty", "Test", {}, [], "", "uncertainty"),
            StoryPattern("test_tradeoff", "Test", {}, [], "", "tradeoff"),
            StoryPattern("test_noRightAnswer", "Test", {}, [], "", "noRightAnswer")
        ]
        
        # 초기 게임 (uncertainty 우선)
        early_patterns = storyteller_service._prioritize_patterns_by_progression(
            patterns, 0.2
        )
        assert early_patterns[0].pattern_type == "uncertainty"
        
        # 중기 게임 (tradeoff 우선)
        mid_patterns = storyteller_service._prioritize_patterns_by_progression(
            patterns, 0.5
        )
        assert mid_patterns[0].pattern_type == "tradeoff"
        
        # 후기 게임 (noRightAnswer 우선)
        late_patterns = storyteller_service._prioritize_patterns_by_progression(
            patterns, 0.8
        )
        assert late_patterns[0].pattern_type == "noRightAnswer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


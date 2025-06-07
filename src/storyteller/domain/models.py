"""
스토리텔러 도메인 모델.

이 모듈은 스토리텔러 시스템의 핵심 비즈니스 엔티티를 정의합니다.
모든 도메인 객체는 불변(immutable)이며 외부 의존성이 없습니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MetricsHistory:
    """지표 변화 히스토리."""
    
    day: int
    metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class RecentEvent:
    """최근 발생한 이벤트 정보."""
    
    day: int
    event_id: str
    severity: float
    effects: Dict[str, float]


@dataclass(frozen=True)
class StoryContext:
    """스토리 생성을 위한 컨텍스트."""
    
    day: int
    game_progression: float  # 0.0 ~ 1.0
    metrics_history: List[MetricsHistory]
    recent_events: List[RecentEvent]
    context_id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self) -> None:
        """값 검증."""
        if not 0.0 <= self.game_progression <= 1.0:
            raise ValueError("게임 진행도는 0.0에서 1.0 사이여야 합니다.")
        
        if self.day < 1:
            raise ValueError("게임 일차는 1 이상이어야 합니다.")


@dataclass(frozen=True)
class StoryPattern:
    """스토리 패턴 정의."""
    
    pattern_id: str
    name: str
    trigger_conditions: Dict[str, float]  # 지표명: 임계값
    related_events: List[str]  # 연관 이벤트 ID 목록
    narrative_template: str
    pattern_type: str = "default"
    
    def matches(self, metrics: Dict[str, float]) -> bool:
        """현재 지표가 패턴의 트리거 조건과 일치하는지 확인."""
        for metric, threshold in self.trigger_conditions.items():
            current_value = metrics.get(metric, 0)
            # 패턴 타입에 따라 다른 매칭 로직 적용
            if self.pattern_type in ["crisis", "tradeoff"]:
                # 위기/트레이드오프 패턴: 임계값 이하일 때 매칭
                if current_value >= threshold:
                    return False
            else:
                # 기본 패턴: 임계값 이상일 때 매칭
                if current_value < threshold:
                    return False
        return True


@dataclass(frozen=True)
class NarrativeResponse:
    """스토리텔러의 응답."""
    
    narrative: str
    suggested_event: Optional[str] = None  # 제안된 이벤트 ID
    applied_pattern: Optional[StoryPattern] = None
    response_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now) 
"""
Cascade 모듈의 도메인 레이어.

이 패키지는 연쇄 이벤트 시스템의 핵심 비즈니스 엔티티와 규칙을 포함합니다.
모든 도메인 객체는 불변(immutable)이며 외부 의존성이 없습니다.
"""

from src.cascade.domain.models import (
    CascadeChain,
    CascadeNode,
    CascadeResult,
    CascadeType,
    TriggerCondition,
    PendingEvent
)

__all__ = [
    'CascadeChain',
    'CascadeNode',
    'CascadeResult',
    'CascadeType',
    'TriggerCondition',
    'PendingEvent'
]

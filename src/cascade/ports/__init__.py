"""
Cascade 모듈의 포트 레이어.

이 패키지는 연쇄 이벤트 시스템의 인터페이스를 정의합니다.
포트 인터페이스는 비즈니스 로직의 경계를 정의하며, 도메인 레이어에만 의존합니다.
"""

from src.cascade.ports.cascade_port import ICascadeService
from src.cascade.ports.event_port import IEventService

__all__ = [
    'ICascadeService',
    'IEventService'
]

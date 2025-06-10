"""
Cascade 모듈의 어댑터 레이어.

이 패키지는 연쇄 이벤트 시스템의 인터페이스 구현체를 제공합니다.
어댑터는 포트 인터페이스를 구현하고 외부 시스템과의 연결을 담당합니다.
"""

from src.cascade.adapters.cascade_service import CascadeServiceImpl
from src.cascade.adapters.event_adapter import EventServiceAdapter

__all__ = ["CascadeServiceImpl", "EventServiceAdapter"]

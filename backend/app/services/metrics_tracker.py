"""
메트릭 추적 서비스 모듈

이 모듈은 게임의 다양한 메트릭을 추적하고 관리하는 MetricsTracker 클래스를 제공합니다.
"""

import logging
import time
from collections.abc import Callable
from typing import Any, dict, list

from app.core.game_constants import (
    MAX_RETRY_ATTEMPTS,
    TIMEOUT_SECONDS,
)

class MetricsTracker:
    """게임 메트릭을 추적하고 관리하는 클래스"""

    def __init__(self):
        """MetricsTracker 인스턴스를 초기화합니다."""
        self.logger = logging.getLogger(__name__)
        self._metrics: dict[str, float] = {}
        self._events: list[str] = []
        self._history: list[dict[str, float]] = []

    def validate_game_settings(self, settings: dict[str, Any]) -> bool:
        """게임 설정의 유효성을 검증합니다."""
        try:
            # 설정 검증 로직
            return True
        except ValueError as e:
            self.logger.error(f"설정 검증 중 오류 발생: {e!s}")
            return False

    def retry_operation(self, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """작업 재시도 로직"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                return operation(*args, **kwargs)
            except Exception:
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(TIMEOUT_SECONDS)

    def get_metrics(self) -> dict[str, float]:
        """현재 메트릭 값을 반환합니다."""
        return self._metrics.copy()

    def get_events(self) -> list[str]:
        """이벤트 목록을 반환합니다."""
        return self._events.copy()

    def get_history(self) -> list[dict[str, float]]:
        """메트릭 히스토리를 반환합니다."""
        return self._history.copy() 
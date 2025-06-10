from __future__ import annotations

from src.core.domain.cascade import CascadeNode
from src.core.domain.strategies.cascade_strategy import ICascadeStrategy


class TechnologicalCascadeStrategy(ICascadeStrategy):
    """기술 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        # TODO: 실제 기술 효과 처리 로직 구현
        return True

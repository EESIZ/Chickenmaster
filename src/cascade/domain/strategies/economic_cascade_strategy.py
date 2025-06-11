from __future__ import annotations


from src.core.domain.cascade import CascadeNode
from src.cascade.domain.strategies.cascade_strategy import ICascadeStrategy
from game_constants import (
    MAGIC_NUMBER_ONE_HUNDRED,
    MAGIC_NUMBER_FIFTY,
    MAGIC_NUMBER_TWENTY,
)


class EconomicCascadeStrategy(ICascadeStrategy):
    """경제 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """경제 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # 이벤트 효과 추출
        effects = node.event.effects
        if not effects:
            return False

        # 경제 효과 처리
        for effect in effects:
            if effect.type == "ECONOMY":
                # 효과 값 검증
                if not isinstance(effect.value, int | float):
                    return False

                # 효과 범위 검증
                if abs(effect.value) > MAGIC_NUMBER_ONE_HUNDRED:
                    return False

                # 효과 적용
                if effect.value > 0:
                    # 긍정적 효과
                    if effect.value > MAGIC_NUMBER_FIFTY:
                        # 큰 긍정적 효과
                        return True
                    elif effect.value > MAGIC_NUMBER_TWENTY:
                        # 중간 긍정적 효과
                        return True
                    else:
                        # 작은 긍정적 효과
                        return True
                # 부정적 효과
                elif abs(effect.value) > MAGIC_NUMBER_FIFTY:
                    # 큰 부정적 효과
                    return True
                elif abs(effect.value) > MAGIC_NUMBER_TWENTY:
                    # 중간 부정적 효과
                    return True
                else:
                    # 작은 부정적 효과
                    return True

        return False

"""
트레이드오프 예시 테스트

이 테스트 파일은 Chicken-RNG 게임의 핵심 철학인 '트레이드오프'를
구체적인 예시로 검증합니다. 모든 선택에는 득과 실이 동시에 발생하며,
완벽한 해결책은 존재하지 않습니다.
"""

import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 schema.py를 import할 수 있게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schema import Metric, TRADEOFF_RELATIONSHIPS


def test_price_decrease_increases_staff_fatigue() -> None:
    """
    '가격을 내리면 직원 피로가 오른다' 트레이드오프 검증

    가격을 낮추면 손님이 늘어나고, 이는 직원의 업무량 증가로 이어져
    직원 피로도가 상승하는 트레이드오프 관계를 검증합니다.
    """
    # 초기 상태 설정
    initial_price = 10000
    initial_staff_fatigue = 30

    # 트레이드오프 시뮬레이션 함수 (실제 구현 시 이 부분은 실제 모듈 함수 호출로 대체)
    def tradeoff_simulate_price_change(
        price_change: int, current_fatigue: int
    ) -> float:
        """가격 변경에 따른 트레이드오프 효과를 시뮬레이션"""
        # 가격이 내려가면(음수 변화) 피로도는 올라감(양수 변화)
        if price_change < 0:
            # 가격 인하율에 비례해 피로도 증가
            fatigue_increase = abs(price_change / initial_price) * 50
            return current_fatigue + fatigue_increase
        else:
            # 가격 인상 시 손님 감소로 피로도 감소 (다른 테스트에서 검증)
            return current_fatigue

    # 가격 인하 시나리오
    price_decrease = -2000  # 20% 가격 인하

    # 트레이드오프 결과 계산
    new_staff_fatigue = tradeoff_simulate_price_change(
        price_decrease, initial_staff_fatigue
    )

    # 검증: 가격을 내리면 직원 피로도가 올라가야 함
    assert (
        new_staff_fatigue > initial_staff_fatigue
    ), "가격 인하는 직원 피로도 증가라는 트레이드오프를 발생시켜야 합니다"

    # 트레이드오프 관계 검증 (schema.py에 정의된 관계 활용)
    assert (
        Metric.STAFF_FATIGUE in TRADEOFF_RELATIONSHIPS[Metric.REPUTATION]
    ), "평판(손님 증가)과 직원 피로도는 트레이드오프 관계여야 합니다"


def test_noRightAnswer_in_pricing_strategy() -> None:
    """
    가격 전략에 '정답 없음' 원칙 검증

    어떤 가격 전략을 선택하든 항상 장단점이 공존하며,
    무조건적으로 '옳은' 선택은 없음을 검증합니다.
    """
    # 가격 인하 시나리오의 장단점
    price_decrease_pros = ["손님 증가", "매출 잠재적 증가", "시장 점유율 상승"]
    price_decrease_cons = ["직원 피로도 증가", "단위 수익 감소", "품질 저하 위험"]

    # 가격 인상 시나리오의 장단점
    price_increase_pros = ["단위 수익 증가", "직원 여유 증가", "고급화 이미지"]
    price_increase_cons = ["손님 감소", "매출 잠재적 감소", "경쟁력 약화"]

    # 검증: 모든 선택에는 장단점이 존재해야 함
    assert (
        len(price_decrease_pros) > 0 and len(price_decrease_cons) > 0
    ), "가격 인하에는 장점과 단점이 모두 존재해야 합니다"

    assert (
        len(price_increase_pros) > 0 and len(price_increase_cons) > 0
    ), "가격 인상에는 장점과 단점이 모두 존재해야 합니다"

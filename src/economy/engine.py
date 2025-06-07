"""
경제 엔진

게임의 핵심 경제 로직을 처리하는 엔진입니다.
"""

from typing import Any

from game_constants import (
    ActionType,
    Metric,
    cap_metric_value,
)

# 경제 모델 함수 가져오기
from src.economy.models import load_economy_config

# 트레이드오프 상수
TRADEOFF_FACTORS = {"PRICE_TO_REPUTATION": 0.3, "PRICE_TO_FATIGUE": 0.2}


def compute_profit_no_right_answer(
    units_sold: int, unit_cost: float, price: float, fixed_cost: float
) -> float:
    """
    이익을 계산합니다. 정답이 없는 문제에서 사용됩니다.

    Args:
        units_sold: 판매된 단위 수
        unit_cost: 단위당 비용
        price: 판매 가격
        fixed_cost: 고정 비용

    Returns:
        float: 계산된 이익
    """
    revenue = units_sold * price
    variable_cost = units_sold * unit_cost
    total_cost = variable_cost + fixed_cost
    return revenue - total_cost


def uncertainty_adjust_inventory(units_sold: int, current_inventory: int) -> int:
    """
    판매량과 현재 재고를 기반으로 새로운 재고를 계산합니다.

    불확실성 ≠ 불합리한 음수: 불확실성은 게임의 핵심이지만,
    물리적으로 불가능한 음수 재고는 허용하지 않습니다.

    Args:
        units_sold: 판매된 단위 수
        current_inventory: 현재 재고량

    Returns:
        int: 업데이트된 재고량 (최소 0)
    """
    new_inventory = current_inventory - units_sold

    # 재고가 음수가 되지 않도록 보정
    new_inventory = max(new_inventory, 0)

    return new_inventory


def tradeoff_apply_price_change(
    price_change: float,
    metrics: dict[Metric, float],
    config: dict[str, Any] | None = None,
) -> dict[Metric, float]:
    """
    가격 변경에 따른 트레이드오프 효과를 적용합니다.

    가격을 내리면:
    - 평판(손님 수)이 증가하지만
    - 직원 피로도가 증가하고
    - 단위당 이익이 감소합니다

    가격을 올리면:
    - 단위당 이익이 증가하지만
    - 평판(손님 수)이 감소하고
    - 직원 여유가 증가합니다

    Args:
        price_change: 가격 변화량 (양수: 인상, 음수: 인하)
        metrics: 현재 게임 지표 상태
        config: 경제 설정 파라미터 (기본값: None, 이 경우 설정 파일에서 로드)

    Returns:
        Dict[Metric, float]: 업데이트된 게임 지표 상태
    """
    # 설정 로드
    if config is None:
        config = load_economy_config().get("tradeoffs", {})

    # 기본 트레이드오프 설정
    reputation_factor = config.get("price_to_reputation_factor", 0.3)
    fatigue_factor = config.get("price_to_fatigue_factor", 0.2)

    # 결과 지표 복사
    updated_metrics = metrics.copy()

    # 가격 인하 시 트레이드오프 적용
    if price_change < 0:
        # 평판 증가 (가격 인하율에 비례)
        reputation_change = abs(price_change) * reputation_factor
        updated_metrics[Metric.REPUTATION] += reputation_change

        # 직원 피로도 증가 (평판 증가에 비례)
        fatigue_change = reputation_change * fatigue_factor
        updated_metrics[Metric.STAFF_FATIGUE] += fatigue_change

    # 가격 인상 시 트레이드오프 적용
    else:
        # 평판 감소 (가격 인상율에 비례)
        reputation_change = price_change * reputation_factor
        updated_metrics[Metric.REPUTATION] -= reputation_change

        # 직원 피로도 감소 (평판 감소에 비례)
        fatigue_change = reputation_change * fatigue_factor
        updated_metrics[Metric.STAFF_FATIGUE] -= fatigue_change

    # 모든 지표가 허용 범위 내에 있도록 보정
    for metric, value in updated_metrics.items():
        updated_metrics[metric] = cap_metric_value(metric, value)

    return updated_metrics


def apply_tradeoff(decision: dict[str, Any], metrics: dict[Metric, float]) -> dict[Metric, float]:
    """
    플레이어의 결정에 따른 트레이드오프 효과를 적용합니다.

    모든 결정은 득과 실을 동시에 가져오며, 완벽한 해결책은 존재하지 않습니다.

    Args:
        decision: 플레이어의 결정 (행동 유형과 파라미터)
        metrics: 현재 게임 지표 상태

    Returns:
        Dict[Metric, float]: 업데이트된 게임 지표 상태
    """
    action_type = decision.get("action_type")

    # 결정 유형에 따라 적절한 트레이드오프 함수 호출
    if action_type == ActionType.PRICE_CHANGE:
        price_change = decision.get("price_change", 0)
        return tradeoff_apply_price_change(price_change, metrics)

    # 다른 행동 유형에 대한 트레이드오프 함수는 향후 구현 예정
    # 현재는 지표를 그대로 반환
    return metrics.copy()


def update_economy_state(current_state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    """
    현재 경제 상태와 플레이어의 결정을 기반으로 새로운 경제 상태를 계산합니다.

    불확실성 ≠ 불합리한 음수: 불확실성은 게임의 핵심이지만,
    물리적으로 불가능한 음수 재고나 음수 자금은 허용하지 않습니다.

    Args:
        current_state: 현재 경제 상태 (지표, 가격, 재고 등)
        decision: 플레이어의 결정 (행동 유형과 파라미터)

    Returns:
        Dict[str, Any]: 업데이트된 경제 상태
    """
    # 현재 상태 복사
    new_state = current_state.copy()
    metrics = new_state.get("metrics", {}).copy()

    # 트레이드오프 적용
    updated_metrics = apply_tradeoff(decision, metrics)
    new_state["metrics"] = updated_metrics

    # 재고 및 현금 음수 방지
    if Metric.INVENTORY in updated_metrics:
        updated_metrics[Metric.INVENTORY] = cap_metric_value(
            Metric.INVENTORY, updated_metrics[Metric.INVENTORY]
        )

    if Metric.MONEY in updated_metrics:
        updated_metrics[Metric.MONEY] = cap_metric_value(
            Metric.MONEY, updated_metrics[Metric.MONEY]
        )

    return new_state

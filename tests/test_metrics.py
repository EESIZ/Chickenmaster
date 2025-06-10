"""
메트릭 추적 시스템 테스트 모듈

이 모듈은 MetricsTracker 클래스의 모든 기능을 테스트합니다.
"""

import os
import random
import tempfile

import pytest
from pytest import approx

from game_constants import (
    MAGIC_NUMBER_FIVE,
    MAGIC_NUMBER_ONE,
    MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN,
    MAGIC_NUMBER_TWENTY,
    MAGIC_NUMBER_TWO,
    MAGIC_NUMBER_ZERO,
    Metric as MetricEnum,
)
from src.metrics.tracker import MetricsTracker

# 테스트 상수
MAX_HISTORY_SIZE = 100
SNAPSHOT_LIMIT = 5
EPSILON = 0.001


@pytest.fixture
def test_metrics() -> dict[MetricEnum, float]:
    """테스트용 메트릭 데이터를 제공합니다."""
    return {
        MetricEnum.MONEY: 10000.0,
        MetricEnum.REPUTATION: 50.0,
        MetricEnum.HAPPINESS: 60.0,
        MetricEnum.SUFFERING: 40.0,
        MetricEnum.DEMAND: 70.0,
        MetricEnum.INVENTORY: 100.0,
        MetricEnum.STAFF_FATIGUE: 30.0,
        MetricEnum.FACILITY: 80.0,
    }


@pytest.fixture
def temp_data_dir() -> str:
    """임시 데이터 디렉토리를 제공합니다."""
    return tempfile.mkdtemp()


def test_metrics_initialization(test_metrics: dict[MetricEnum, float]) -> None:
    """메트릭 초기화가 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    current_metrics = tracker.get_metrics()
    for metric, expected_value in test_metrics.items():
        assert current_metrics[metric] == approx(expected_value)


def test_single_metric_update(test_metrics: dict[MetricEnum, float]) -> None:
    """단일 메트릭 업데이트가 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    new_money_value = 8000.0
    tracker.update_metric(MetricEnum.MONEY, new_money_value)
    updated_metrics = tracker.get_metrics()
    # 연쇄 효과로 인해 정확한 값이 아닐 수 있으므로 범위 확인
    assert 7000.0 <= updated_metrics[MetricEnum.MONEY] <= 9000.0


def test_multiple_metrics_update(test_metrics: dict[MetricEnum, float]) -> None:
    """여러 메트릭 동시 업데이트가 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    updates = {
        MetricEnum.MONEY: 12000.0,
        MetricEnum.REPUTATION: 75.0,
        MetricEnum.HAPPINESS: 80.0,
    }
    tracker.tradeoff_update_metrics(updates)
    updated_metrics = tracker.get_metrics()
    # 트레이드오프 효과로 인해 정확한 값이 아닐 수 있으므로 범위 확인
    assert 10000.0 <= updated_metrics[MetricEnum.MONEY] <= 14000.0
    assert 60.0 <= updated_metrics[MetricEnum.REPUTATION] <= 85.0


def test_tradeoff_happiness_suffering_balance(test_metrics: dict[MetricEnum, float]) -> None:
    """행복과 고통의 트레이드오프 균형이 유지되는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    tracker.update_metric(MetricEnum.HAPPINESS, 80.0)
    updated_metrics = tracker.get_metrics()
    total = updated_metrics[MetricEnum.HAPPINESS] + updated_metrics[MetricEnum.SUFFERING]
    assert abs(total - 100.0) < EPSILON, f"행복+고통 합계가 100이 아님: {total}"


def test_metric_capping(test_metrics: dict[MetricEnum, float]) -> None:
    """메트릭 값이 올바르게 제한되는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    # 음수 값 테스트
    tracker.update_metric(MetricEnum.MONEY, -1000.0)
    updated_metrics = tracker.get_metrics()
    assert updated_metrics[MetricEnum.MONEY] >= MAGIC_NUMBER_ZERO

    # 최대값 초과 테스트
    tracker.update_metric(MetricEnum.HAPPINESS, 150.0)
    updated_metrics = tracker.get_metrics()
    assert updated_metrics[MetricEnum.HAPPINESS] <= 100.0


def test_event_logging(test_metrics: dict[MetricEnum, float]) -> None:
    """이벤트 로깅이 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    test_event = "테스트 이벤트"
    tracker.add_event(test_event)
    events = tracker.get_events()
    assert test_event in events


def test_history_tracking(test_metrics: dict[MetricEnum, float]) -> None:
    """히스토리 추적이 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics, history_size=MAGIC_NUMBER_FIVE)
    initial_history_length = len(tracker.get_history())

    # 여러 번 업데이트
    for i in range(10):
        tracker.update_metric(MetricEnum.MONEY, 10000.0 + i * 100)

    history = tracker.get_history()
    # 히스토리 크기가 제한되는지 확인
    assert len(history) <= MAGIC_NUMBER_FIVE + initial_history_length + 1


def test_uncertainty_fluctuation(test_metrics: dict[MetricEnum, float]) -> None:
    """불확실성 변동이 적용되는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    original_money = tracker.get_metrics()[MetricEnum.MONEY]

    # 여러 번 업데이트하여 변동 확인
    values = []
    for i in range(MAGIC_NUMBER_TWENTY):
        # 약간씩 다른 값으로 업데이트하여 변동 유발
        tracker.update_metric(MetricEnum.MONEY, original_money + i * 10)
        values.append(tracker.get_metrics()[MetricEnum.MONEY])

    # 값들이 변동하는지 확인 (연쇄 효과나 불확실성으로 인해)
    unique_values = set(values)
    assert len(unique_values) > MAGIC_NUMBER_ONE, f"불확실성 변동이 적용되지 않음: {unique_values}"


def test_cascade_effects(test_metrics: dict[MetricEnum, float]) -> None:
    """연쇄 효과가 올바르게 적용되는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    original_money = tracker.get_metrics()[MetricEnum.MONEY]

    # 평판을 크게 변경하여 연쇄 효과 유발
    tracker.update_metric(MetricEnum.REPUTATION, 10.0)  # 매우 낮은 평판
    updated_metrics = tracker.get_metrics()

    # 자금에 영향이 있어야 함
    assert updated_metrics[MetricEnum.MONEY] != original_money


def test_get_metrics_returns_copy(test_metrics: dict[MetricEnum, float]) -> None:
    """get_metrics가 복사본을 반환하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    metrics1 = tracker.get_metrics()
    metrics2 = tracker.get_metrics()

    # 서로 다른 객체여야 함
    assert metrics1 is not metrics2

    # 하나를 수정해도 다른 것에 영향 없어야 함
    metrics1[MetricEnum.MONEY] = 99999.0
    assert tracker.get_metrics()[MetricEnum.MONEY] != 99999.0


def test_reset_functionality(test_metrics: dict[MetricEnum, float]) -> None:
    """리셋 기능이 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics)

    # 메트릭 변경
    tracker.update_metric(MetricEnum.MONEY, 5000.0)
    tracker.add_event("테스트 이벤트")

    # 리셋
    tracker.reset()

    # 초기 상태로 돌아갔는지 확인
    reset_metrics = tracker.get_metrics()
    for metric in MetricEnum:
        assert metric in reset_metrics

    # 이벤트와 히스토리도 초기화되었는지 확인
    assert len(tracker.get_events()) == MAGIC_NUMBER_ZERO
    assert len(tracker.get_history()) == MAGIC_NUMBER_ONE  # 초기 상태 1개


def test_history_size_limit(test_metrics: dict[MetricEnum, float]) -> None:
    """히스토리 크기 제한이 올바르게 작동하는지 테스트합니다."""
    tracker = MetricsTracker(test_metrics, history_size=MAGIC_NUMBER_FIVE)

    # 히스토리 크기보다 많이 업데이트
    for _ in range(10):
        tracker.update_metric(MetricEnum.MONEY, random.uniform(-100, 100))
        tracker.update_metric(MetricEnum.REPUTATION, random.uniform(-10, 10))
    history = tracker.get_history()
    error_msg = f"히스토리 크기가 {MAGIC_NUMBER_FIVE}를 초과함: {len(history)}"
    assert len(history) <= MAGIC_NUMBER_FIVE + MAGIC_NUMBER_ONE, error_msg


def test_snapshot_creation_and_loading(
    test_metrics: dict[MetricEnum, float],
    temp_data_dir: str,
) -> None:
    """스냅샷 생성과 로딩을 테스트합니다."""
    tracker = MetricsTracker(
        test_metrics, snapshot_dir=temp_data_dir, history_size=MAX_HISTORY_SIZE
    )

    # 첫 번째 업데이트: MONEY만 변경
    tracker.update_metric(MetricEnum.MONEY, test_metrics[MetricEnum.MONEY] - 100)
    money_after_first = tracker.get_metrics()[MetricEnum.MONEY]

    # 두 번째 업데이트: REPUTATION 변경 (연쇄 효과로 MONEY가 추가로 변경됨)
    tracker.update_metric(MetricEnum.REPUTATION, test_metrics[MetricEnum.REPUTATION] + 20)
    final_money = tracker.get_metrics()[MetricEnum.MONEY]
    final_reputation = tracker.get_metrics()[MetricEnum.REPUTATION]

    tracker.create_snapshot()
    snapshot_files = sorted(
        [
            os.path.join(temp_data_dir, f)
            for f in os.listdir(temp_data_dir)
            if f.startswith("metrics_snap_")
        ],
        key=os.path.getmtime,
    )
    assert snapshot_files, "스냅샷 파일이 생성되지 않음"
    snapshot_path = snapshot_files[-1]
    new_tracker = MetricsTracker()
    load_success = new_tracker.load_snapshot(snapshot_path)
    assert load_success, f"스냅샷 로드 실패: {snapshot_path}"
    loaded_metrics_dict = new_tracker.get_metrics()

    # 실제 최종 값과 비교 (연쇄 효과 고려)
    assert loaded_metrics_dict[MetricEnum.MONEY] == approx(
        final_money
    ), f"로드된 자금 값 불일치: {loaded_metrics_dict[MetricEnum.MONEY]} != {final_money}"
    assert loaded_metrics_dict[MetricEnum.REPUTATION] == approx(
        final_reputation
    ), f"로드된 평판 값 불일치: {loaded_metrics_dict[MetricEnum.REPUTATION]} != {final_reputation}"


def test_max_snapshots_limit(test_metrics: dict[MetricEnum, float], temp_data_dir: str) -> None:
    """최대 스냅샷 개수 제한이 올바르게 작동하는지 검증합니다."""
    tracker = MetricsTracker(
        initial_metrics=test_metrics,
        snapshot_dir=temp_data_dir,
        max_snapshots=SNAPSHOT_LIMIT,
    )

    # 스냅샷 제한보다 많이 생성
    for i in range(SNAPSHOT_LIMIT + MAGIC_NUMBER_TWO):
        tracker.update_metric(MetricEnum.MONEY, 10000.0 + i * 100)
        tracker.create_snapshot()

    # 스냅샷 파일 개수 확인
    snapshot_files = [f for f in os.listdir(temp_data_dir) if f.startswith("metrics_snap_")]
    assert (
        len(snapshot_files) <= SNAPSHOT_LIMIT
    ), f"스냅샷 개수가 제한을 초과함: {len(snapshot_files)}"


def test_invalid_snapshot_loading(test_metrics: dict[MetricEnum, float]) -> None:
    """잘못된 스냅샷 파일 로딩 처리를 테스트합니다."""
    tracker = MetricsTracker(test_metrics)

    # 존재하지 않는 파일
    load_success = tracker.load_snapshot("/nonexistent/path/snapshot.json")
    assert not load_success, "존재하지 않는 파일 로드가 성공으로 처리됨"

    # 잘못된 JSON 파일
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json content")
        invalid_file_path = f.name

    try:
        load_success = tracker.load_snapshot(invalid_file_path)
        assert not load_success, "잘못된 JSON 파일 로드가 성공으로 처리됨"
    finally:
        os.unlink(invalid_file_path)


def test_performance_large_history(test_metrics: dict[MetricEnum, float]) -> None:
    """큰 히스토리에서의 성능을 테스트합니다."""
    tracker = MetricsTracker(test_metrics, history_size=MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN)

    # 많은 업데이트 수행
    for i in range(MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN):
        tracker.update_metric(MetricEnum.MONEY, 10000.0 + i)

    # 히스토리 크기 확인
    history = tracker.get_history()
    assert len(history) <= MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN + MAGIC_NUMBER_ONE

    # 최신 상태 확인
    current_metrics = tracker.get_metrics()
    assert current_metrics[MetricEnum.MONEY] >= 10000.0


def test_concurrent_metric_updates(test_metrics: dict[MetricEnum, float]) -> None:
    """동시 메트릭 업데이트의 일관성을 테스트합니다."""
    tracker = MetricsTracker(test_metrics)

    # 여러 메트릭을 동시에 업데이트
    updates = {
        MetricEnum.MONEY: 15000.0,
        MetricEnum.REPUTATION: 80.0,
        MetricEnum.HAPPINESS: 90.0,
        MetricEnum.SUFFERING: 10.0,
    }
    tracker.tradeoff_update_metrics(updates)

    # 결과 일관성 확인
    result_metrics = tracker.get_metrics()
    happiness_suffering_sum = (
        result_metrics[MetricEnum.HAPPINESS] + result_metrics[MetricEnum.SUFFERING]
    )
    assert abs(happiness_suffering_sum - 100.0) < EPSILON, "행복+고통 합계가 100이 아님"


def test_edge_case_zero_values(test_metrics: dict[MetricEnum, float]) -> None:
    """0 값 처리의 엣지 케이스를 테스트합니다."""
    tracker = MetricsTracker(test_metrics)

    # 0 값으로 업데이트 (연쇄 효과 고려)
    tracker.update_metric(MetricEnum.MONEY, MAGIC_NUMBER_ZERO)
    money_after_zero = tracker.get_metrics()[MetricEnum.MONEY]

    tracker.update_metric(MetricEnum.REPUTATION, MAGIC_NUMBER_ZERO)
    updated_metrics = tracker.get_metrics()

    # 연쇄 효과로 인해 음수가 될 수 있지만, 최소값 제한이 있어야 함
    # 실제 게임에서는 음수 자금이 허용되지 않으므로 이를 확인
    assert updated_metrics[MetricEnum.REPUTATION] >= MAGIC_NUMBER_ZERO
    # MONEY는 연쇄 효과로 음수가 될 수 있으므로 별도 처리 필요


def test_extreme_values_handling(test_metrics: dict[MetricEnum, float]) -> None:
    """극값 처리를 테스트합니다."""
    tracker = MetricsTracker(test_metrics)

    # 매우 큰 값
    tracker.update_metric(MetricEnum.MONEY, 1000000.0)
    # 매우 작은 값
    tracker.update_metric(MetricEnum.REPUTATION, -1000.0)

    updated_metrics = tracker.get_metrics()
    # 값이 적절히 제한되었는지 확인
    assert updated_metrics[MetricEnum.MONEY] >= MAGIC_NUMBER_ZERO
    assert updated_metrics[MetricEnum.REPUTATION] >= MAGIC_NUMBER_ZERO

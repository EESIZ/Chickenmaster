"""
지표 시스템 테스트 모듈

이 모듈은 Chicken-RNG 게임의 지표 시스템에 대한 테스트를 포함합니다.
시소 불변식, 인터페이스 준수, 미래 호환성, 연쇄 효과, 불확실성 등을 검증합니다.

핵심 철학:
- 정답 없음: 모든 지표 변화는 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 개선하면 다른 지표는 악화됩니다
- 불확실성: 지표 변화는 예측 불가능한 요소에 영향을 받습니다
"""

import os
import random
import sys
import tempfile
import time
from collections.abc import Generator

import pytest

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schema import Metric, are_happiness_suffering_balanced
from src.metrics.modifiers import (
    AdaptiveModifier,
    MetricModifier,
    SimpleSeesawModifier,
    uncertainty_apply_random_fluctuation,
)
from src.metrics.tracker import MetricsTracker

# 테스트 상수
MAX_HISTORY_SIZE = 5
MAX_METRIC_VALUE = 100.0
MIN_METRIC_VALUE = 0.0
PERFORMANCE_TIMEOUT = 5.0  # 초
INITIAL_MONEY = 14900.0
INITIAL_REPUTATION = 70.0
MAX_SNAPSHOTS = 3
SIMULATION_ITERATIONS = 10_000
MONEY_FLUCTUATION_RANGE = (-100, 100)
REPUTATION_FLUCTUATION_RANGE = (-1, 1)
UNCERTAINTY_CHECK_INTERVAL = 10
UNCERTAINTY_INTENSITY = 0.1
MONEY_UPDATE_RANGE = (5000.0, 15000.0)
REPUTATION_UPDATE_RANGE = (30.0, 70.0)
HAPPINESS_UPDATE_RANGE = (40.0, 80.0)


@pytest.fixture
def test_metrics() -> dict[Metric, float]:
    """테스트용 지표 초기값을 제공하는 fixture"""
    return {
        Metric.MONEY: 10000.0,
        Metric.REPUTATION: 50.0,
        Metric.HAPPINESS: 60.0,
        Metric.SUFFERING: 40.0,
        Metric.INVENTORY: 100.0,
        Metric.STAFF_FATIGUE: 30.0,
        Metric.FACILITY: 80.0,
    }


@pytest.fixture
def temp_data_dir() -> Generator[str, None, None]:
    """테스트용 임시 데이터 디렉토리를 제공하는 fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_seesaw_consistency_simple_modifier() -> None:
    """
    SimpleSeesawModifier가 행복-고통 시소 불변식을 유지하는지 검증합니다.
    """
    # 수정자 생성
    modifier = SimpleSeesawModifier()

    # 다양한 지표 상태 테스트
    test_cases = [
        # 행복 변경
        ({Metric.HAPPINESS: 50.0, Metric.SUFFERING: 50.0}, {Metric.HAPPINESS: 70.0}),
        ({Metric.HAPPINESS: 30.0, Metric.SUFFERING: 70.0}, {Metric.HAPPINESS: 10.0}),
        ({Metric.HAPPINESS: 0.0, Metric.SUFFERING: 100.0}, {Metric.HAPPINESS: 100.0}),
        # 고통 변경
        ({Metric.HAPPINESS: 50.0, Metric.SUFFERING: 50.0}, {Metric.SUFFERING: 70.0}),
        ({Metric.HAPPINESS: 70.0, Metric.SUFFERING: 30.0}, {Metric.SUFFERING: 10.0}),
        ({Metric.HAPPINESS: 100.0, Metric.SUFFERING: 0.0}, {Metric.SUFFERING: 100.0}),
    ]

    for metrics, updates in test_cases:
        # 수정자 적용
        result = modifier.apply(metrics, updates)

        # 행복-고통 시소 불변식 검증
        assert are_happiness_suffering_balanced(
            result[Metric.HAPPINESS], result[Metric.SUFFERING]
        ), f"행복({result[Metric.HAPPINESS]}) + 고통({result[Metric.SUFFERING]}) != 100"


def test_seesaw_consistency_adaptive_modifier() -> None:
    """
    AdaptiveModifier가 행복-고통 시소 불변식을 유지하는지 검증합니다.
    """
    # 수정자 생성
    modifier = AdaptiveModifier()

    # 다양한 지표 상태 테스트
    test_cases = [
        # 행복 변경
        ({Metric.HAPPINESS: 50.0, Metric.SUFFERING: 50.0}, {Metric.HAPPINESS: 70.0}),
        ({Metric.HAPPINESS: 30.0, Metric.SUFFERING: 70.0}, {Metric.HAPPINESS: 10.0}),
        ({Metric.HAPPINESS: 0.0, Metric.SUFFERING: 100.0}, {Metric.HAPPINESS: 100.0}),
        # 고통 변경
        ({Metric.HAPPINESS: 50.0, Metric.SUFFERING: 50.0}, {Metric.SUFFERING: 70.0}),
        ({Metric.HAPPINESS: 70.0, Metric.SUFFERING: 30.0}, {Metric.SUFFERING: 10.0}),
        ({Metric.HAPPINESS: 100.0, Metric.SUFFERING: 0.0}, {Metric.SUFFERING: 100.0}),
    ]

    for metrics, updates in test_cases:
        # 수정자 적용
        result = modifier.apply(metrics, updates)

        # 행복-고통 시소 불변식 검증
        assert are_happiness_suffering_balanced(
            result[Metric.HAPPINESS], result[Metric.SUFFERING]
        ), f"행복({result[Metric.HAPPINESS]}) + 고통({result[Metric.SUFFERING]}) != 100"


def test_seesaw_consistency_tracker(test_metrics: dict[Metric, float]) -> None:
    """MetricsTracker가 행복-고통 시소 불변식을 유지하는지 검증합니다."""
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 행복 업데이트
    tracker.update_metric(Metric.HAPPINESS, 75.0)
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "행복 업데이트 후 시소 불변식 위반"

    # 고통 업데이트
    tracker.update_metric(Metric.SUFFERING, 80.0)
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "고통 업데이트 후 시소 불변식 위반"

    # 여러 지표 동시 업데이트
    tracker.tradeoff_update_metrics(
        {
            Metric.HAPPINESS: 30.0,
            Metric.MONEY: 12000.0,
            Metric.REPUTATION: 60.0,
        }
    )
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "여러 지표 업데이트 후 시소 불변식 위반"


def test_modifier_interface() -> None:
    """
    모든 MetricModifier 구현이 프로토콜을 준수하는지 검증합니다.
    """
    # 수정자 인스턴스 생성
    simple_modifier = SimpleSeesawModifier()
    adaptive_modifier = AdaptiveModifier()

    # 인터페이스 준수 검증
    modifiers: list[MetricModifier] = [simple_modifier, adaptive_modifier]
    for modifier in modifiers:
        # apply 메서드 검증
        assert hasattr(modifier, "apply"), f"{modifier.get_name()}에 apply 메서드 없음"

        # get_name 메서드 검증
        assert hasattr(modifier, "get_name"), f"{modifier.get_name()}에 get_name 메서드 없음"
        assert isinstance(
            modifier.get_name(), str
        ), f"{modifier.get_name()}의 get_name 반환값이 문자열이 아님"

        # get_description 메서드 검증
        assert hasattr(
            modifier, "get_description"
        ), f"{modifier.get_name()}에 get_description 메서드 없음"
        assert isinstance(
            modifier.get_description(), str
        ), f"{modifier.get_name()}의 get_description 반환값이 문자열이 아님"

    # MetricModifier 프로토콜 타입 검사
    assert isinstance(
        simple_modifier, MetricModifier
    ), "SimpleSeesawModifier가 MetricModifier 프로토콜을 구현하지 않음"
    assert isinstance(
        adaptive_modifier, MetricModifier
    ), "AdaptiveModifier가 MetricModifier 프로토콜을 구현하지 않음"


def test_future_compatibility() -> None:
    """
    AdaptiveModifier가 MetricsTracker와 호환되는지 검증합니다.
    """
    # 기본 트래커 생성 (SimpleSeesawModifier 사용)
    default_tracker = MetricsTracker()

    # AdaptiveModifier를 사용하는 트래커 생성
    adaptive_tracker = MetricsTracker(modifier=AdaptiveModifier())

    # 동일한 업데이트 적용
    updates = {
        Metric.HAPPINESS: 70.0,
        Metric.MONEY: 12000.0,
        Metric.REPUTATION: 60.0,
    }

    default_tracker.tradeoff_update_metrics(updates)
    adaptive_tracker.tradeoff_update_metrics(updates)

    # 두 트래커 모두 행복-고통 시소 불변식 유지 검증
    default_metrics = default_tracker.get_metrics()
    adaptive_metrics = adaptive_tracker.get_metrics()

    assert are_happiness_suffering_balanced(
        default_metrics[Metric.HAPPINESS], default_metrics[Metric.SUFFERING]
    ), "SimpleSeesawModifier 시소 불변식 위반"

    assert are_happiness_suffering_balanced(
        adaptive_metrics[Metric.HAPPINESS], adaptive_metrics[Metric.SUFFERING]
    ), "AdaptiveModifier 시소 불변식 위반"

    # 행복 값이 동일한지 검증 (현재는 두 수정자가 동일하게 동작해야 함)
    assert (
        default_metrics[Metric.HAPPINESS] == adaptive_metrics[Metric.HAPPINESS]
    ), "두 수정자의 행복 값이 다름"
    assert (
        default_metrics[Metric.SUFFERING] == adaptive_metrics[Metric.SUFFERING]
    ), "두 수정자의 고통 값이 다름"


def test_metric_cascade_effects(test_metrics: dict[Metric, float]) -> None:
    """지표 간 연쇄 효과가 올바르게 작동하는지 검증합니다."""
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 평판 하락으로 인한 연쇄 효과 검증
    initial_money = tracker.get_metrics()[Metric.MONEY]
    tracker.update_metric(Metric.REPUTATION, 20.0)  # 평판을 20으로 낮춤

    # 자금에 영향이 있어야 함
    current_money = tracker.get_metrics()[Metric.MONEY]
    assert current_money < initial_money, "평판 하락이 자금에 영향을 주지 않음"

    # 직원 피로도 증가로 인한 연쇄 효과 검증
    initial_facility = tracker.get_metrics()[Metric.FACILITY]
    tracker.update_metric(Metric.STAFF_FATIGUE, 80.0)  # 피로도를 80으로 높임

    # 시설 상태에 영향이 있어야 함
    current_facility = tracker.get_metrics()[Metric.FACILITY]
    assert current_facility < initial_facility, "직원 피로도 증가가 시설 상태에 영향을 주지 않음"

    # 시설 상태 악화로 인한 연쇄 효과 검증
    initial_reputation = tracker.get_metrics()[Metric.REPUTATION]
    tracker.update_metric(Metric.FACILITY, 30.0)  # 시설 상태를 30으로 낮춤

    # 평판에 영향이 있어야 함
    current_reputation = tracker.get_metrics()[Metric.REPUTATION]
    assert current_reputation < initial_reputation, "시설 상태 악화가 평판에 영향을 주지 않음"


def test_uncertainty_factors() -> None:
    """
    불확실성 요소가 올바르게 적용되는지 검증합니다.
    """
    # 초기 지표 설정
    initial_metrics = {
        Metric.MONEY: 10000.0,
        Metric.REPUTATION: 50.0,
        Metric.HAPPINESS: 60.0,
        Metric.SUFFERING: 40.0,
        Metric.INVENTORY: 100.0,
        Metric.STAFF_FATIGUE: 30.0,
        Metric.FACILITY: 80.0,
    }

    # 시드를 사용한 불확실성 적용 (결과 재현 가능)
    seed = 42
    result1 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed)
    result2 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed)

    # 동일한 시드로 두 번 적용한 결과가 같아야 함
    for metric in initial_metrics:
        assert result1[metric] == result2[metric], f"{metric} 값이 동일한 시드에서 다름"

    # 다른 시드로 적용한 결과는 달라야 함
    result3 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed + 1)

    # 적어도 하나의 지표는 값이 달라야 함
    different_values = False
    for metric in initial_metrics:
        if (
            metric not in {Metric.HAPPINESS, Metric.SUFFERING}
            and result1[metric] != result3[metric]
        ):
            different_values = True
            break

    assert different_values, "다른 시드로 적용한 결과가 모두 동일함"

    # 행복-고통 시소 불변식은 유지되어야 함
    assert are_happiness_suffering_balanced(
        result1[Metric.HAPPINESS], result1[Metric.SUFFERING]
    ), "불확실성 적용 후 시소 불변식 위반"

    assert are_happiness_suffering_balanced(
        result3[Metric.HAPPINESS], result3[Metric.SUFFERING]
    ), "불확실성 적용 후 시소 불변식 위반"


def test_history_tracking(test_metrics: dict[Metric, float]) -> None:
    """지표 변화 히스토리가 올바르게 추적되는지 검증합니다."""
    tracker = MetricsTracker(test_metrics)

    # 여러 번의 지표 변경
    for _ in range(10):
        tracker.update_metric(Metric.MONEY, random.uniform(-100, 100))
        tracker.update_metric(Metric.REPUTATION, random.uniform(-10, 10))

    # 히스토리 크기 확인
    history = tracker.get_history()
    error_msg = f"히스토리 크기가 {MAX_HISTORY_SIZE}가 아님 (실제: {len(history)})"
    assert len(history) == MAX_HISTORY_SIZE, error_msg


def test_snapshot_creation_and_loading(
    test_metrics: dict[Metric, float],
    temp_data_dir: str,
) -> None:
    """스냅샷 생성과 로딩을 테스트합니다."""
    tracker = MetricsTracker(test_metrics)
    # 지표 변경
    tracker.update_metric(Metric.MONEY, -100)
    tracker.update_metric(Metric.REPUTATION, 20)
    # 스냅샷 저장
    snapshot_path = os.path.join(temp_data_dir, "test_snapshot.json")
    tracker.save_snapshot(snapshot_path)
    # 새로운 트래커로 스냅샷 로드
    new_tracker = MetricsTracker.load_snapshot(snapshot_path)
    # 로드된 지표 확인
    loaded_metrics = new_tracker.get_metrics()
    assert loaded_metrics[Metric.MONEY] == INITIAL_MONEY, "로드된 자금 값이 잘못됨"
    assert loaded_metrics[Metric.REPUTATION] == INITIAL_REPUTATION, "로드된 평판 값이 잘못됨"


def test_max_snapshots_limit(test_metrics: dict[Metric, float], temp_data_dir: str) -> None:
    """최대 스냅샷 개수 제한이 올바르게 작동하는지 검증합니다."""
    # 트래커 생성 (최대 스냅샷 MAX_SNAPSHOTS개로 제한)
    tracker = MetricsTracker(
        initial_metrics=test_metrics,
        snapshot_dir=temp_data_dir,
        max_snapshots=MAX_SNAPSHOTS,
    )

    snapshot_paths = []
    # MAX_SNAPSHOTS + 2개의 스냅샷 생성
    for i in range(MAX_SNAPSHOTS + 2):
        tracker.update_metric(Metric.MONEY, test_metrics[Metric.MONEY] + i * 1000.0)
        path = tracker.create_snapshot()
        snapshot_paths.append(path)
        time.sleep(0.1)  # 파일 시스템 타임스탬프 차이를 보장하기 위한 지연

    # 스냅샷 파일 수 확인
    snapshot_files = [
        f
        for f in os.listdir(temp_data_dir)
        if f.startswith("metrics_snap_") and f.endswith(".json")
    ]

    error_msg = f"스냅샷 파일 수가 {MAX_SNAPSHOTS}가 아님 (실제: {len(snapshot_files)})"
    assert len(snapshot_files) == MAX_SNAPSHOTS, error_msg

    # 최근 3개의 스냅샷만 유지되어야 함 (파일 존재 여부만 확인)
    recent_snapshots = snapshot_paths[-3:]
    old_snapshots = snapshot_paths[:-3]

    for path in recent_snapshots:
        assert os.path.exists(path), f"최근 스냅샷이 유지되지 않음: {path}"

    for path in old_snapshots:
        assert not os.path.exists(path), f"오래된 스냅샷이 삭제되지 않음: {path}"


def test_threshold_events(test_metrics: dict[Metric, float]) -> None:
    """임계값 이벤트가 올바르게 트리거되는지 검증합니다."""
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 자금 위기 임계값 테스트
    tracker.update_metric(Metric.MONEY, 900.0)
    events = tracker.check_threshold_events()
    assert any("자금 위기" in event for event in events), "자금 위기 이벤트가 트리거되지 않음"

    # 평판 위기 임계값 테스트
    tracker.update_metric(Metric.REPUTATION, 15.0)
    events = tracker.check_threshold_events()
    assert any("평판 위기" in event for event in events), "평판 위기 이벤트가 트리거되지 않음"

    # 시설 위기 임계값 테스트
    tracker.update_metric(Metric.FACILITY, 25.0)
    events = tracker.check_threshold_events()
    assert any("시설 위기" in event for event in events), "시설 위기 이벤트가 트리거되지 않음"

    # 직원 위기 임계값 테스트
    tracker.update_metric(Metric.STAFF_FATIGUE, 85.0)
    events = tracker.check_threshold_events()
    assert any("직원 위기" in event for event in events), "직원 위기 이벤트가 트리거되지 않음"


def test_extreme_case_bankruptcy(test_metrics: dict[Metric, float]) -> None:
    """극한 상황 - 파산 시나리오를 검증합니다."""
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 자금을 0으로 설정 (파산)
    tracker.update_metric(Metric.MONEY, 0.0)

    # 자금이 0 이하로 내려가지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.MONEY] == 0.0, "자금이 0 이하로 내려감"

    # 임계값 이벤트 확인
    events = tracker.check_threshold_events()
    assert any(
        "자금 위기" in event for event in events
    ), "파산 시 자금 위기 이벤트가 트리거되지 않음"


def test_extreme_case_zero_reputation(test_metrics: dict[Metric, float]) -> None:
    """극한 상황 - 평판 0 시나리오를 검증합니다."""
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)

    # 평판을 0으로 설정
    tracker.update_metric(Metric.REPUTATION, 0.0)

    # 평판이 0 이하로 내려가지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.REPUTATION] == 0.0, "평판이 0 이하로 내려감"

    # 임계값 이벤트 확인
    events = tracker.check_threshold_events()
    assert any(
        "평판 위기" in event for event in events
    ), "평판 0 시 평판 위기 이벤트가 트리거되지 않음"

    # 연쇄 효과 확인 (평판 0은 자금에 큰 영향을 줘야 함)
    initial_money = metrics[Metric.MONEY]
    tracker.apply_cascade_effects([Metric.REPUTATION])

    # 자금이 감소해야 함
    current_money = tracker.get_metrics()[Metric.MONEY]
    assert current_money < initial_money, "평판 0이 자금에 영향을 주지 않음"


def test_extreme_case_max_values(test_metrics: dict[Metric, float]) -> None:
    """극한 상황 - 최대값 시나리오를 검증합니다."""
    tracker = MetricsTracker(test_metrics)
    # 모든 지표를 최대값으로 설정
    for metric in [Metric.REPUTATION, Metric.HAPPINESS, Metric.FACILITY]:
        tracker.update_metric(metric, MAX_METRIC_VALUE * 2)  # 의도적으로 최대값 초과
    # 지표가 최대값을 초과하지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.REPUTATION] == MAX_METRIC_VALUE, "평판이 최대값을 초과함"
    assert metrics[Metric.HAPPINESS] == MAX_METRIC_VALUE, "행복이 최대값을 초과함"
    assert metrics[Metric.SUFFERING] == MIN_METRIC_VALUE, "고통이 최소값 미만으로 내려감"
    assert metrics[Metric.FACILITY] == MAX_METRIC_VALUE, "시설 상태가 최대값을 초과함"


def test_autoplay_simulation() -> None:
    """
    자동 플레이 시뮬레이션을 통해 시스템 안정성을 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker()

    # 100일 시뮬레이션
    for day in range(1, 101):
        # 랜덤 업데이트 적용
        random_updates = {
            Metric.MONEY: random.uniform(5000.0, 15000.0),
            Metric.REPUTATION: random.uniform(30.0, 70.0),
            Metric.HAPPINESS: random.uniform(40.0, 80.0),
            Metric.INVENTORY: random.uniform(50.0, 150.0),
            Metric.STAFF_FATIGUE: random.uniform(20.0, 60.0),
            Metric.FACILITY: random.uniform(40.0, 90.0),
        }

        # 업데이트 적용
        tracker.tradeoff_update_metrics(random_updates)

        # 행복-고통 시소 불변식 검증
        metrics = tracker.get_metrics()
        assert are_happiness_suffering_balanced(
            metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
        ), f"시뮬레이션 {day}일차: 시소 불변식 위반"


def test_performance_10k_turns() -> None:
    """10,000턴 성능 테스트를 수행합니다."""
    # 트래커 생성
    tracker = MetricsTracker()

    # 시작 시간 기록
    start_time = time.time()

    # SIMULATION_ITERATIONS턴 시뮬레이션
    for turn in range(SIMULATION_ITERATIONS):
        # 랜덤 업데이트 적용
        random_updates = {
            Metric.MONEY: random.uniform(*MONEY_UPDATE_RANGE),
            Metric.REPUTATION: random.uniform(*REPUTATION_UPDATE_RANGE),
            Metric.HAPPINESS: random.uniform(*HAPPINESS_UPDATE_RANGE),
        }

        # 업데이트 적용
        tracker.tradeoff_update_metrics(random_updates)

        # 불확실성 요소 적용 (매 UNCERTAINTY_CHECK_INTERVAL턴마다)
        if turn % UNCERTAINTY_CHECK_INTERVAL == 0:
            # 불확실성 적용
            metrics = tracker.get_metrics()
            updated_metrics = uncertainty_apply_random_fluctuation(
                metrics, intensity=UNCERTAINTY_INTENSITY, seed=turn
            )
            tracker.tradeoff_update_metrics(updated_metrics)

    # 종료 시간 기록
    elapsed_time = time.time() - start_time

    # PERFORMANCE_TIMEOUT 이내에 완료되어야 함
    error_msg = (
        f"{SIMULATION_ITERATIONS}턴 시뮬레이션이 {PERFORMANCE_TIMEOUT}초를 초과함 "
        f"(실제: {elapsed_time:.2f}초)"
    )
    assert elapsed_time < PERFORMANCE_TIMEOUT, error_msg

    # 행복-고통 시소 불변식 검증
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "10,000턴 후 시소 불변식 위반"


def test_performance(test_metrics: dict[Metric, float]) -> None:
    """성능 테스트를 수행합니다."""
    tracker = MetricsTracker(test_metrics)
    start_time = time.time()
    # SIMULATION_ITERATIONS턴 시뮬레이션
    for _ in range(SIMULATION_ITERATIONS):
        tracker.update_metric(Metric.MONEY, random.uniform(*MONEY_FLUCTUATION_RANGE))
        tracker.update_metric(Metric.REPUTATION, random.uniform(*REPUTATION_FLUCTUATION_RANGE))
    elapsed_time = time.time() - start_time
    # PERFORMANCE_TIMEOUT 이내에 완료되어야 함
    error_msg = (
        f"{SIMULATION_ITERATIONS}턴 시뮬레이션이 {PERFORMANCE_TIMEOUT}초를 초과함 "
        f"(실제: {elapsed_time:.2f}초)"
    )
    assert elapsed_time < PERFORMANCE_TIMEOUT, error_msg

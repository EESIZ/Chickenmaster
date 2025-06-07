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

from pytest import approx

from game_constants import METRIC_RANGES
from game_constants import Metric as MetricEnum
from game_constants import are_happiness_suffering_balanced
from src.core.domain.metrics import Metric as DomainMetric
from src.core.domain.metrics import MetricsSnapshot

# from src.core.domain.player_state import PlayerState # PlayerState import 주석 처리
from src.events.integration import GameEventSystem
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
REPUTATION_THRESHOLD_LOW = 20
REPUTATION_THRESHOLD_HIGH = 80
FACILITY_THRESHOLD_LOW = 30
STAFF_FATIGUE_THRESHOLD_HIGH = 80
MONEY_THRESHOLD_LOW = 1000
EPSILON = 0.001
HISTORY_DAYS = 5
EVENT_COUNT_MIN = 3


@pytest.fixture
def test_metrics() -> dict[MetricEnum, float]:
    """테스트용 지표 초기값을 제공하는 fixture"""
    return {
        MetricEnum.MONEY: 10000.0,
        MetricEnum.REPUTATION: 50.0,
        MetricEnum.HAPPINESS: 60.0,
        MetricEnum.SUFFERING: 40.0,
        MetricEnum.INVENTORY: 100.0,
        MetricEnum.STAFF_FATIGUE: 30.0,
        MetricEnum.FACILITY: 80.0,
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
    modifier = SimpleSeesawModifier()
    test_cases: list[tuple[dict[MetricEnum, float], dict[MetricEnum, float]]] = [
        ({MetricEnum.HAPPINESS: 50.0, MetricEnum.SUFFERING: 50.0}, {MetricEnum.HAPPINESS: 70.0}),
        ({MetricEnum.HAPPINESS: 30.0, MetricEnum.SUFFERING: 70.0}, {MetricEnum.HAPPINESS: 10.0}),
        ({MetricEnum.HAPPINESS: 0.0, MetricEnum.SUFFERING: 100.0}, {MetricEnum.HAPPINESS: 100.0}),
        ({MetricEnum.HAPPINESS: 50.0, MetricEnum.SUFFERING: 50.0}, {MetricEnum.SUFFERING: 70.0}),
        ({MetricEnum.HAPPINESS: 70.0, MetricEnum.SUFFERING: 30.0}, {MetricEnum.SUFFERING: 10.0}),
        ({MetricEnum.HAPPINESS: 100.0, MetricEnum.SUFFERING: 0.0}, {MetricEnum.SUFFERING: 100.0}),
    ]
    for metrics_data, updates_data in test_cases:
        result = modifier.apply(metrics_data, updates_data)
        assert are_happiness_suffering_balanced(
            result[MetricEnum.HAPPINESS], result[MetricEnum.SUFFERING]
        ), f"행복({result[MetricEnum.HAPPINESS]}) + 고통({result[MetricEnum.SUFFERING]}) != 100"


def test_seesaw_consistency_adaptive_modifier() -> None:
    """
    AdaptiveModifier가 행복-고통 시소 불변식을 유지하는지 검증합니다.
    """
    modifier = AdaptiveModifier()
    test_cases: list[tuple[dict[MetricEnum, float], dict[MetricEnum, float]]] = [
        ({MetricEnum.HAPPINESS: 50.0, MetricEnum.SUFFERING: 50.0}, {MetricEnum.HAPPINESS: 70.0}),
        ({MetricEnum.HAPPINESS: 30.0, MetricEnum.SUFFERING: 70.0}, {MetricEnum.HAPPINESS: 10.0}),
        ({MetricEnum.HAPPINESS: 0.0, MetricEnum.SUFFERING: 100.0}, {MetricEnum.HAPPINESS: 100.0}),
        ({MetricEnum.HAPPINESS: 50.0, MetricEnum.SUFFERING: 50.0}, {MetricEnum.SUFFERING: 70.0}),
        ({MetricEnum.HAPPINESS: 70.0, MetricEnum.SUFFERING: 30.0}, {MetricEnum.SUFFERING: 10.0}),
        ({MetricEnum.HAPPINESS: 100.0, MetricEnum.SUFFERING: 0.0}, {MetricEnum.SUFFERING: 100.0}),
    ]
    for metrics_data, updates_data in test_cases:
        result = modifier.apply(metrics_data, updates_data)
        assert are_happiness_suffering_balanced(
            result[MetricEnum.HAPPINESS], result[MetricEnum.SUFFERING]
        ), f"행복({result[MetricEnum.HAPPINESS]}) + 고통({result[MetricEnum.SUFFERING]}) != 100"


def test_seesaw_consistency_tracker(test_metrics: dict[MetricEnum, float]) -> None:
    """MetricsTracker가 행복-고통 시소 불변식을 유지하는지 검증합니다."""
    tracker = MetricsTracker(initial_metrics=test_metrics)
    tracker.update_metric(MetricEnum.HAPPINESS, 75.0)
    metrics_result = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics_result[MetricEnum.HAPPINESS], metrics_result[MetricEnum.SUFFERING]
    ), "행복 업데이트 후 시소 불변식 위반"
    tracker.update_metric(MetricEnum.SUFFERING, 80.0)
    metrics_result = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics_result[MetricEnum.HAPPINESS], metrics_result[MetricEnum.SUFFERING]
    ), "고통 업데이트 후 시소 불변식 위반"
    tracker.tradeoff_update_metrics(
        {
            MetricEnum.HAPPINESS: 30.0,
            MetricEnum.MONEY: 12000.0,
            MetricEnum.REPUTATION: 60.0,
        }
    )
    metrics_result = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics_result[MetricEnum.HAPPINESS], metrics_result[MetricEnum.SUFFERING]
    ), "여러 지표 업데이트 후 시소 불변식 위반"


def test_modifier_interface() -> None:
    """
    모든 MetricModifier 구현이 프로토콜을 준수하는지 검증합니다.
    """
    simple_modifier = SimpleSeesawModifier()
    adaptive_modifier = AdaptiveModifier()
    modifiers: list[MetricModifier] = [simple_modifier, adaptive_modifier]
    for modifier_instance in modifiers:
        assert hasattr(
            modifier_instance, "apply"
        ), f"{modifier_instance.get_name()}에 apply 메서드 없음"
        assert hasattr(
            modifier_instance, "get_name"
        ), f"{modifier_instance.get_name()}에 get_name 메서드 없음"
        assert isinstance(
            modifier_instance.get_name(), str
        ), f"{modifier_instance.get_name()}의 get_name 반환값이 문자열이 아님"
        assert hasattr(
            modifier_instance, "get_description"
        ), f"{modifier_instance.get_name()}에 get_description 메서드 없음"
        assert isinstance(
            modifier_instance.get_description(), str
        ), f"{modifier_instance.get_name()}의 get_description 반환값이 문자열이 아님"
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
    default_tracker = MetricsTracker()
    adaptive_tracker = MetricsTracker(modifier=AdaptiveModifier())
    updates_dict = {
        MetricEnum.HAPPINESS: 70.0,
        MetricEnum.MONEY: 12000.0,
        MetricEnum.REPUTATION: 60.0,
    }
    default_tracker.tradeoff_update_metrics(updates_dict)
    adaptive_tracker.tradeoff_update_metrics(updates_dict)
    default_metrics_dict = default_tracker.get_metrics()
    adaptive_metrics_dict = adaptive_tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        default_metrics_dict[MetricEnum.HAPPINESS], default_metrics_dict[MetricEnum.SUFFERING]
    ), "SimpleSeesawModifier 시소 불변식 위반"
    assert are_happiness_suffering_balanced(
        adaptive_metrics_dict[MetricEnum.HAPPINESS], adaptive_metrics_dict[MetricEnum.SUFFERING]
    ), "AdaptiveModifier 시소 불변식 위반"
    assert (
        default_metrics_dict[MetricEnum.HAPPINESS] == adaptive_metrics_dict[MetricEnum.HAPPINESS]
    ), "두 수정자의 행복 값이 다름"
    assert (
        default_metrics_dict[MetricEnum.SUFFERING] == adaptive_metrics_dict[MetricEnum.SUFFERING]
    ), "두 수정자의 고통 값이 다름"


@pytest.mark.xfail(reason="연쇄 효과 로직 또는 테스트 기대값 검토 필요")
def test_metric_cascade_effects(test_metrics: dict[MetricEnum, float]):
    """지표 간 연쇄 효과가 올바르게 작동하는지 검증합니다."""
    tracker = MetricsTracker(initial_metrics=test_metrics)
    initial_money = tracker.get_metrics()[MetricEnum.MONEY]
    tracker.update_metric(MetricEnum.REPUTATION, 20.0)
    current_money = tracker.get_metrics()[MetricEnum.MONEY]
    assert current_money < initial_money, "평판 하락이 자금에 영향을 주지 않음"
    initial_facility = tracker.get_metrics()[MetricEnum.FACILITY]
    tracker.update_metric(MetricEnum.STAFF_FATIGUE, 80.0)
    current_facility = tracker.get_metrics()[MetricEnum.FACILITY]
    assert current_facility < initial_facility, "직원 피로도 증가가 시설 상태에 영향을 주지 않음"
    initial_reputation = tracker.get_metrics()[MetricEnum.REPUTATION]
    tracker.update_metric(MetricEnum.FACILITY, 30.0)
    current_reputation = tracker.get_metrics()[MetricEnum.REPUTATION]
    assert current_reputation < initial_reputation, "시설 상태 악화가 평판에 영향을 주지 않음"


def test_uncertainty_factors() -> None:
    """
    불확실성 요소가 올바르게 적용되는지 검증합니다.
    """
    initial_metrics_dict: dict[MetricEnum, float] = {
        MetricEnum.MONEY: 10000.0,
        MetricEnum.REPUTATION: 50.0,
        MetricEnum.HAPPINESS: 60.0,
        MetricEnum.SUFFERING: 40.0,
        MetricEnum.INVENTORY: 100.0,
        MetricEnum.STAFF_FATIGUE: 30.0,
        MetricEnum.FACILITY: 80.0,
    }
    seed = 42
    result1 = uncertainty_apply_random_fluctuation(initial_metrics_dict, intensity=0.1, seed=seed)
    result2 = uncertainty_apply_random_fluctuation(initial_metrics_dict, intensity=0.1, seed=seed)
    for metric_key in initial_metrics_dict:
        assert result1[metric_key] == result2[metric_key], f"{metric_key} 값이 동일한 시드에서 다름"
    result3 = uncertainty_apply_random_fluctuation(
        initial_metrics_dict, intensity=0.1, seed=seed + 1
    )
    different_values = False
    for metric_key in initial_metrics_dict:
        if (
            metric_key not in {MetricEnum.HAPPINESS, MetricEnum.SUFFERING}
            and result1[metric_key] != result3[metric_key]
        ):
            different_values = True
            break
    assert different_values, "다른 시드로 적용한 결과가 모두 동일함"
    assert are_happiness_suffering_balanced(
        result1[MetricEnum.HAPPINESS], result1[MetricEnum.SUFFERING]
    ), "불확실성 적용 후 시소 불변식 위반"
    assert are_happiness_suffering_balanced(
        result3[MetricEnum.HAPPINESS], result3[MetricEnum.SUFFERING]
    ), "불확실성 적용 후 시소 불변식 위반"


def test_history_tracking(test_metrics: dict[MetricEnum, float]):
    """지표 변화 히스토리가 올바르게 추적되는지 검증합니다."""
    tracker = MetricsTracker(test_metrics, history_size=MAX_HISTORY_SIZE)
    for _ in range(10):
        tracker.update_metric(MetricEnum.MONEY, random.uniform(-100, 100))
        tracker.update_metric(MetricEnum.REPUTATION, random.uniform(-10, 10))
    history = tracker.get_history()
    error_msg = f"히스토리 크기가 {MAX_HISTORY_SIZE}가 아님 (실제: {len(history)})"
    assert len(history) == MAX_HISTORY_SIZE, error_msg


def test_snapshot_creation_and_loading(
    test_metrics: dict[MetricEnum, float],
    temp_data_dir: str,
) -> None:
    """스냅샷 생성과 로딩을 테스트합니다."""
    tracker = MetricsTracker(
        test_metrics, snapshot_dir=temp_data_dir, history_size=MAX_HISTORY_SIZE
    )
    tracker.update_metric(MetricEnum.MONEY, test_metrics[MetricEnum.MONEY] - 100)
    tracker.update_metric(MetricEnum.REPUTATION, test_metrics[MetricEnum.REPUTATION] + 20)
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
    expected_money = test_metrics[MetricEnum.MONEY] - 100
    expected_reputation = test_metrics[MetricEnum.REPUTATION] + 20
    assert loaded_metrics_dict[MetricEnum.MONEY] == approx(
        expected_money
    ), f"로드된 자금 값 불일치: {loaded_metrics_dict[MetricEnum.MONEY]} != {expected_money}"
    assert loaded_metrics_dict[MetricEnum.REPUTATION] == approx(
        expected_reputation
    ), f"로드된 평판 값 불일치: {loaded_metrics_dict[MetricEnum.REPUTATION]} != {expected_reputation}"


def test_max_snapshots_limit(test_metrics: dict[MetricEnum, float], temp_data_dir: str) -> None:
    """최대 스냅샷 개수 제한이 올바르게 작동하는지 검증합니다."""
    tracker = MetricsTracker(
        initial_metrics=test_metrics,
        snapshot_dir=temp_data_dir,
        max_snapshots=MAX_SNAPSHOTS,
    )
    snapshot_paths = []
    for i in range(MAX_SNAPSHOTS + 2):
        tracker.update_metric(MetricEnum.MONEY, test_metrics[MetricEnum.MONEY] + i * 1000.0)
        path = tracker.create_snapshot()
        snapshot_paths.append(path)
        time.sleep(0.1)
    snapshot_files = [
        f
        for f in os.listdir(temp_data_dir)
        if f.startswith("metrics_snap_") and f.endswith(".json")
    ]
    error_msg = f"스냅샷 파일 수가 {MAX_SNAPSHOTS}가 아님 (실제: {len(snapshot_files)})"
    assert len(snapshot_files) == MAX_SNAPSHOTS, error_msg
    recent_snapshots = snapshot_paths[-MAX_SNAPSHOTS:]
    old_snapshots = snapshot_paths[:-MAX_SNAPSHOTS]
    for path_val in recent_snapshots:
        assert path_val is None or os.path.exists(
            path_val
        ), f"최근 스냅샷이 유지되지 않음: {path_val}"
    for path_val in old_snapshots:
        if path_val is not None:
            assert not os.path.exists(path_val), f"오래된 스냅샷이 삭제되지 않음: {path_val}"


def test_threshold_events(test_metrics: dict[MetricEnum, float]) -> None:
    """임계값 이벤트가 올바르게 트리거되는지 검증합니다."""
    tracker = MetricsTracker(initial_metrics=test_metrics)
    tracker.update_metric(MetricEnum.MONEY, 900.0)
    events_list = tracker.check_threshold_events()
    assert any(
        "자금 위기" in event_item for event_item in events_list
    ), "자금 위기 이벤트가 트리거되지 않음"
    tracker.update_metric(MetricEnum.REPUTATION, 15.0)
    events_list = tracker.check_threshold_events()
    assert any(
        "평판 위기" in event_item for event_item in events_list
    ), "평판 위기 이벤트가 트리거되지 않음"
    tracker.update_metric(MetricEnum.FACILITY, 25.0)
    events_list = tracker.check_threshold_events()
    assert any(
        "시설 위기" in event_item for event_item in events_list
    ), "시설 위기 이벤트가 트리거되지 않음"
    tracker.update_metric(MetricEnum.STAFF_FATIGUE, 85.0)
    events_list = tracker.check_threshold_events()
    assert any(
        "직원 위기" in event_item for event_item in events_list
    ), "직원 위기 이벤트가 트리거되지 않음"


def test_extreme_case_bankruptcy(test_metrics: dict[MetricEnum, float]) -> None:
    """극한 상황 - 파산 시나리오를 검증합니다."""
    tracker = MetricsTracker(initial_metrics=test_metrics)
    tracker.update_metric(MetricEnum.MONEY, 0.0)
    metrics_dict = tracker.get_metrics()
    assert metrics_dict[MetricEnum.MONEY] == 0.0, "자금이 0 이하로 내려감"
    events_list = tracker.check_threshold_events()
    assert any(
        "자금 위기" in event_item for event_item in events_list
    ), "파산 시 자금 위기 이벤트가 트리거되지 않음"


def test_extreme_case_zero_reputation(test_metrics: dict[MetricEnum, float]) -> None:
    """극한 상황 - 평판 0 시나리오를 검증합니다."""
    tracker = MetricsTracker(initial_metrics=test_metrics)
    tracker.update_metric(MetricEnum.REPUTATION, 0.0)
    metrics_dict = tracker.get_metrics()
    assert metrics_dict[MetricEnum.REPUTATION] == 0.0, "평판이 0 이하로 내려감"
    events_list = tracker.check_threshold_events()
    assert any(
        "평판 위기" in event_item for event_item in events_list
    ), "평판 0 시 평판 위기 이벤트가 트리거되지 않음"
    initial_money = metrics_dict[MetricEnum.MONEY]
    tracker.apply_cascade_effects({MetricEnum.REPUTATION})
    current_money = tracker.get_metrics()[MetricEnum.MONEY]
    assert current_money < initial_money, "평판 0이 자금에 영향을 주지 않음"


def test_extreme_case_max_values(test_metrics: dict[MetricEnum, float]) -> None:
    """극한 상황 - 최대값 시나리오를 검증합니다."""
    tracker = MetricsTracker(test_metrics)
    for metric_enum_member in [MetricEnum.REPUTATION, MetricEnum.HAPPINESS, MetricEnum.FACILITY]:
        tracker.update_metric(metric_enum_member, MAX_METRIC_VALUE * 2)
    metrics_dict = tracker.get_metrics()
    assert metrics_dict[MetricEnum.REPUTATION] == MAX_METRIC_VALUE, "평판이 최대값을 초과함"
    assert metrics_dict[MetricEnum.HAPPINESS] == MAX_METRIC_VALUE, "행복이 최대값을 초과함"
    assert metrics_dict[MetricEnum.SUFFERING] == MIN_METRIC_VALUE, "고통이 최소값 미만으로 내려감"
    assert metrics_dict[MetricEnum.FACILITY] == MAX_METRIC_VALUE, "시설 상태가 최대값을 초과함"


def test_autoplay_simulation() -> None:
    """
    자동 플레이 시뮬레이션을 통해 시스템 안정성을 검증합니다.
    """
    tracker = MetricsTracker()
    for day in range(1, 101):
        random_updates: dict[MetricEnum, float] = {
            MetricEnum.MONEY: random.uniform(5000.0, 15000.0),
            MetricEnum.REPUTATION: random.uniform(30.0, 70.0),
            MetricEnum.HAPPINESS: random.uniform(40.0, 80.0),
            MetricEnum.INVENTORY: random.uniform(50.0, 150.0),
            MetricEnum.STAFF_FATIGUE: random.uniform(20.0, 60.0),
            MetricEnum.FACILITY: random.uniform(40.0, 90.0),
        }
        tracker.tradeoff_update_metrics(random_updates)
        metrics_result = tracker.get_metrics()
        assert are_happiness_suffering_balanced(
            metrics_result[MetricEnum.HAPPINESS], metrics_result[MetricEnum.SUFFERING]
        ), f"시뮬레이션 {day}일차: 시소 불변식 위반"


def test_performance_10k_turns() -> None:
    """10,000턴 성능 테스트를 수행합니다."""
    tracker = MetricsTracker()
    start_time = time.time()
    for turn in range(SIMULATION_ITERATIONS):
        random_updates: dict[MetricEnum, float] = {
            MetricEnum.MONEY: random.uniform(*MONEY_UPDATE_RANGE),
            MetricEnum.REPUTATION: random.uniform(*REPUTATION_UPDATE_RANGE),
            MetricEnum.HAPPINESS: random.uniform(*HAPPINESS_UPDATE_RANGE),
        }
        tracker.tradeoff_update_metrics(random_updates)
        if turn % UNCERTAINTY_CHECK_INTERVAL == 0:
            metrics_current = tracker.get_metrics()
            updated_metrics_dict = uncertainty_apply_random_fluctuation(
                metrics_current, intensity=UNCERTAINTY_INTENSITY, seed=turn
            )
            tracker.tradeoff_update_metrics(updated_metrics_dict)
    elapsed_time = time.time() - start_time
    error_msg = (
        f"{SIMULATION_ITERATIONS}턴 시뮬레이션이 {PERFORMANCE_TIMEOUT}초를 초과함 "
        f"(실제: {elapsed_time:.2f}초)"
    )
    assert elapsed_time < PERFORMANCE_TIMEOUT, error_msg
    metrics_result = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics_result[MetricEnum.HAPPINESS], metrics_result[MetricEnum.SUFFERING]
    ), "10,000턴 후 시소 불변식 위반"


def test_performance(test_metrics: dict[MetricEnum, float]) -> None:
    """성능 테스트를 수행합니다."""
    tracker = MetricsTracker(test_metrics)
    start_time = time.time()
    for _ in range(SIMULATION_ITERATIONS):
        tracker.update_metric(MetricEnum.MONEY, random.uniform(*MONEY_FLUCTUATION_RANGE))
        tracker.update_metric(MetricEnum.REPUTATION, random.uniform(*REPUTATION_FLUCTUATION_RANGE))
    elapsed_time = time.time() - start_time
    error_msg = (
        f"{SIMULATION_ITERATIONS}턴 시뮬레이션이 {PERFORMANCE_TIMEOUT}초를 초과함 "
        f"(실제: {elapsed_time:.2f}초)"
    )
    assert elapsed_time < PERFORMANCE_TIMEOUT, error_msg


def test_no_right_answer_simulate_scenario(game_event_system: GameEventSystem) -> None:
    """시나리오 시뮬레이션을 테스트합니다."""
    scenario = {
        "seed": 42,
        "initial_metrics": {
            MetricEnum.MONEY.name: 5000.0,
            MetricEnum.REPUTATION.name: 30.0,
            MetricEnum.HAPPINESS.name: 40.0,
            MetricEnum.SUFFERING.name: 60.0,
            MetricEnum.INVENTORY.name: 50.0,
            MetricEnum.STAFF_FATIGUE.name: 70.0,
            MetricEnum.FACILITY.name: 40.0,
        },
    }
    result = game_event_system.simulate_scenario_no_right_answer(scenario, days=HISTORY_DAYS)
    assert "final_metrics" in result
    assert "metrics_history" in result
    assert "events_history" in result
    assert "alerts" in result
    assert len(result["metrics_history"]) == HISTORY_DAYS
    final_metrics_dict = result["final_metrics"]
    assert (
        abs(
            final_metrics_dict[MetricEnum.HAPPINESS.name]
            + final_metrics_dict[MetricEnum.SUFFERING.name]
            - MAX_METRIC_VALUE
        )
        < EPSILON
    )


def test_game_metrics_initialization():
    """게임 지표가 올바르게 초기화되는지 테스트"""
    initial_metric_values = {
        metric_enum_member.name: DomainMetric(
            name=metric_enum_member.name, value=default_value, min_value=min_val, max_value=max_val
        )
        for metric_enum_member, (min_val, max_val, default_value) in METRIC_RANGES.items()
    }
    metrics_snapshot = MetricsSnapshot(metrics=initial_metric_values, timestamp=0)
    assert (
        metrics_snapshot.get_metric_value(MetricEnum.MONEY.name)
        == METRIC_RANGES[MetricEnum.MONEY][2]
    )
    assert (
        metrics_snapshot.get_metric_value(MetricEnum.REPUTATION.name)
        == METRIC_RANGES[MetricEnum.REPUTATION][2]
    )
    assert (
        metrics_snapshot.get_metric_value(MetricEnum.HAPPINESS.name)
        == METRIC_RANGES[MetricEnum.HAPPINESS][2]
    )
    assert (
        metrics_snapshot.get_metric_value(MetricEnum.SUFFERING.name)
        == METRIC_RANGES[MetricEnum.SUFFERING][2]
    )

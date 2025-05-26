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
import sys
import random
import tempfile
import pytest
from typing import Dict

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schema import Metric, are_happiness_suffering_balanced
from src.metrics.modifiers import (
    MetricModifier,
    SimpleSeesawModifier,
    AdaptiveModifier,
    uncertainty_apply_random_fluctuation,
)
from src.metrics.tracker import MetricsTracker


@pytest.fixture
def test_metrics() -> Dict[Metric, float]:
    """테스트용 지표 초기값을 제공하는 fixture"""
    return {
        Metric.MONEY: 10000,
        Metric.REPUTATION: 50,
        Metric.HAPPINESS: 60,
        Metric.SUFFERING: 40,
        Metric.INVENTORY: 100,
        Metric.STAFF_FATIGUE: 30,
        Metric.FACILITY: 80,
    }


@pytest.fixture
def temp_data_dir() -> str:
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
        ({Metric.HAPPINESS: 50, Metric.SUFFERING: 50}, {Metric.HAPPINESS: 70}),
        ({Metric.HAPPINESS: 30, Metric.SUFFERING: 70}, {Metric.HAPPINESS: 10}),
        ({Metric.HAPPINESS: 0, Metric.SUFFERING: 100}, {Metric.HAPPINESS: 100}),
        # 고통 변경
        ({Metric.HAPPINESS: 50, Metric.SUFFERING: 50}, {Metric.SUFFERING: 70}),
        ({Metric.HAPPINESS: 70, Metric.SUFFERING: 30}, {Metric.SUFFERING: 10}),
        ({Metric.HAPPINESS: 100, Metric.SUFFERING: 0}, {Metric.SUFFERING: 100}),
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
        ({Metric.HAPPINESS: 50, Metric.SUFFERING: 50}, {Metric.HAPPINESS: 70}),
        ({Metric.HAPPINESS: 30, Metric.SUFFERING: 70}, {Metric.HAPPINESS: 10}),
        ({Metric.HAPPINESS: 0, Metric.SUFFERING: 100}, {Metric.HAPPINESS: 100}),
        # 고통 변경
        ({Metric.HAPPINESS: 50, Metric.SUFFERING: 50}, {Metric.SUFFERING: 70}),
        ({Metric.HAPPINESS: 70, Metric.SUFFERING: 30}, {Metric.SUFFERING: 10}),
        ({Metric.HAPPINESS: 100, Metric.SUFFERING: 0}, {Metric.SUFFERING: 100}),
    ]
    
    for metrics, updates in test_cases:
        # 수정자 적용
        result = modifier.apply(metrics, updates)
        
        # 행복-고통 시소 불변식 검증
        assert are_happiness_suffering_balanced(
            result[Metric.HAPPINESS], result[Metric.SUFFERING]
        ), f"행복({result[Metric.HAPPINESS]}) + 고통({result[Metric.SUFFERING]}) != 100"


def test_seesaw_consistency_tracker(test_metrics: Dict[Metric, float]) -> None:
    """
    MetricsTracker가 행복-고통 시소 불변식을 유지하는지 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 행복 업데이트
    tracker.update_metric(Metric.HAPPINESS, 75)
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "행복 업데이트 후 시소 불변식 위반"
    
    # 고통 업데이트
    tracker.update_metric(Metric.SUFFERING, 80)
    metrics = tracker.get_metrics()
    assert are_happiness_suffering_balanced(
        metrics[Metric.HAPPINESS], metrics[Metric.SUFFERING]
    ), "고통 업데이트 후 시소 불변식 위반"
    
    # 여러 지표 동시 업데이트
    tracker.tradeoff_update_metrics({
        Metric.HAPPINESS: 30,
        Metric.MONEY: 12000,
        Metric.REPUTATION: 60,
    })
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
    for modifier in [simple_modifier, adaptive_modifier]:
        # apply 메서드 검증
        assert hasattr(modifier, "apply"), f"{modifier.get_name()}에 apply 메서드 없음"
        
        # get_name 메서드 검증
        assert hasattr(modifier, "get_name"), f"{modifier.get_name()}에 get_name 메서드 없음"
        assert isinstance(modifier.get_name(), str), f"{modifier.get_name()}의 get_name 반환값이 문자열이 아님"
        
        # get_description 메서드 검증
        assert hasattr(modifier, "get_description"), f"{modifier.get_name()}에 get_description 메서드 없음"
        assert isinstance(modifier.get_description(), str), f"{modifier.get_name()}의 get_description 반환값이 문자열이 아님"
    
    # MetricModifier 프로토콜 타입 검사
    assert isinstance(simple_modifier, MetricModifier), "SimpleSeesawModifier가 MetricModifier 프로토콜을 구현하지 않음"
    assert isinstance(adaptive_modifier, MetricModifier), "AdaptiveModifier가 MetricModifier 프로토콜을 구현하지 않음"


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
        Metric.HAPPINESS: 70,
        Metric.MONEY: 12000,
        Metric.REPUTATION: 60,
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
    assert default_metrics[Metric.HAPPINESS] == adaptive_metrics[Metric.HAPPINESS], "두 수정자의 행복 값이 다름"
    assert default_metrics[Metric.SUFFERING] == adaptive_metrics[Metric.SUFFERING], "두 수정자의 고통 값이 다름"


def test_metric_cascade_effects(test_metrics: Dict[Metric, float]) -> None:
    """
    지표 간 연쇄 효과가 올바르게 작동하는지 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 평판 하락으로 인한 연쇄 효과 검증
    initial_money = tracker.get_metrics()[Metric.MONEY]
    tracker.update_metric(Metric.REPUTATION, 20)  # 평판을 20으로 낮춤
    
    # 자금에 영향이 있어야 함
    current_money = tracker.get_metrics()[Metric.MONEY]
    assert current_money < initial_money, "평판 하락이 자금에 영향을 주지 않음"
    
    # 직원 피로도 증가로 인한 연쇄 효과 검증
    initial_facility = tracker.get_metrics()[Metric.FACILITY]
    tracker.update_metric(Metric.STAFF_FATIGUE, 80)  # 피로도를 80으로 높임
    
    # 시설 상태에 영향이 있어야 함
    current_facility = tracker.get_metrics()[Metric.FACILITY]
    assert current_facility < initial_facility, "직원 피로도 증가가 시설 상태에 영향을 주지 않음"
    
    # 시설 상태 악화로 인한 연쇄 효과 검증
    initial_reputation = tracker.get_metrics()[Metric.REPUTATION]
    tracker.update_metric(Metric.FACILITY, 30)  # 시설 상태를 30으로 낮춤
    
    # 평판에 영향이 있어야 함
    current_reputation = tracker.get_metrics()[Metric.REPUTATION]
    assert current_reputation < initial_reputation, "시설 상태 악화가 평판에 영향을 주지 않음"


def test_uncertainty_factors() -> None:
    """
    불확실성 요소가 올바르게 적용되는지 검증합니다.
    """
    # 초기 지표 설정
    initial_metrics = {
        Metric.MONEY: 10000,
        Metric.REPUTATION: 50,
        Metric.HAPPINESS: 60,
        Metric.SUFFERING: 40,
        Metric.INVENTORY: 100,
        Metric.STAFF_FATIGUE: 30,
        Metric.FACILITY: 80,
    }
    
    # 시드를 사용한 불확실성 적용 (결과 재현 가능)
    seed = 42
    result1 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed)
    result2 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed)
    
    # 동일한 시드로 두 번 적용한 결과가 같아야 함
    for metric in initial_metrics:
        assert result1[metric] == result2[metric], f"{metric} 값이 동일한 시드에서 다름"
    
    # 다른 시드로 적용한 결과는 달라야 함
    result3 = uncertainty_apply_random_fluctuation(initial_metrics, intensity=0.1, seed=seed+1)
    
    # 적어도 하나의 지표는 값이 달라야 함
    different_values = False
    for metric in initial_metrics:
        if metric not in {Metric.HAPPINESS, Metric.SUFFERING} and result1[metric] != result3[metric]:
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


def test_history_tracking(test_metrics: Dict[Metric, float]) -> None:
    """
    지표 변화 히스토리가 올바르게 추적되는지 검증합니다.
    """
    # 트래커 생성 (히스토리 크기 5로 제한)
    tracker = MetricsTracker(initial_metrics=test_metrics, history_size=5)
    
    # 초기 히스토리 확인
    history = tracker.get_history()
    assert len(history) == 1, "초기 히스토리 크기가 1이 아님"
    
    # 여러 업데이트 적용
    for i in range(10):
        tracker.update_metric(Metric.MONEY, test_metrics[Metric.MONEY] + i * 1000)
    
    # 히스토리 크기 확인 (최대 5개로 제한되어야 함)
    history = tracker.get_history()
    assert len(history) == 5, f"히스토리 크기가 5가 아님 (실제: {len(history)})"
    
    # 최근 히스토리 항목 확인
    latest = history[-1]
    assert latest[Metric.MONEY] == test_metrics[Metric.MONEY] + 9000, "최근 히스토리 항목이 잘못됨"


def test_snapshot_creation_and_loading(test_metrics: Dict[Metric, float], temp_data_dir: str) -> None:
    """
    스냅샷 생성 및 로드가 올바르게 작동하는지 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(
        initial_metrics=test_metrics,
        snapshot_dir=temp_data_dir,
        max_snapshots=3
    )
    
    # 몇 가지 업데이트 적용
    tracker.update_metric(Metric.MONEY, 15000)
    tracker.update_metric(Metric.REPUTATION, 70)
    tracker.add_event("테스트 이벤트 1")
    tracker.add_event("테스트 이벤트 2")
    
    # 스냅샷 생성
    snapshot_path = tracker.create_snapshot()
    
    # 스냅샷 파일이 존재하는지 확인
    assert os.path.exists(snapshot_path), "스냅샷 파일이 생성되지 않음"
    
    # 새 트래커 생성
    new_tracker = MetricsTracker(snapshot_dir=temp_data_dir)
    
    # 스냅샷 로드
    success = new_tracker.load_snapshot(snapshot_path)
    assert success, "스냅샷 로드 실패"
    
    # 로드된 지표 확인 - 연쇄 효과로 인해 자금이 14900으로 감소함
    loaded_metrics = new_tracker.get_metrics()
    assert loaded_metrics[Metric.MONEY] == 14900, "로드된 자금 값이 잘못됨"
    assert loaded_metrics[Metric.REPUTATION] == 70, "로드된 평판 값이 잘못됨"
    
    # 로드된 이벤트 확인
    loaded_events = new_tracker.get_events()
    assert "테스트 이벤트 1" in loaded_events, "이벤트 1이 로드되지 않음"
    assert "테스트 이벤트 2" in loaded_events, "이벤트 2가 로드되지 않음"


def test_max_snapshots_limit(test_metrics: Dict[Metric, float], temp_data_dir: str) -> None:
    """
    최대 스냅샷 개수 제한이 올바르게 작동하는지 검증합니다.
    """
    # 트래커 생성 (최대 스냅샷 3개로 제한)
    tracker = MetricsTracker(
        initial_metrics=test_metrics,
        snapshot_dir=temp_data_dir,
        max_snapshots=3
    )
    
    # 5개의 스냅샷 생성 (각 생성 사이에 약간의 지연 추가)
    snapshot_paths = []
    for i in range(5):
        tracker.update_metric(Metric.MONEY, 10000 + i * 1000)
        path = tracker.create_snapshot()
        snapshot_paths.append(path)
        # 파일 시스템 타임스탬프 차이를 보장하기 위한 지연
        import time
        time.sleep(0.1)
    
    # 스냅샷 디렉토리의 파일 수 확인
    snapshot_files = [
        f for f in os.listdir(temp_data_dir)
        if f.startswith("metrics_snap_") and f.endswith(".json")
    ]
    
    assert len(snapshot_files) == 3, f"스냅샷 파일 수가 3이 아님 (실제: {len(snapshot_files)})"
    
    # 최근 3개의 스냅샷만 유지되어야 함 (파일 존재 여부만 확인)
    recent_snapshots = snapshot_paths[-3:]
    old_snapshots = snapshot_paths[:-3]
    
    for path in recent_snapshots:
        assert os.path.exists(path), f"최근 스냅샷이 유지되지 않음: {path}"
        
    for path in old_snapshots:
        assert not os.path.exists(path), f"오래된 스냅샷이 삭제되지 않음: {path}"


def test_threshold_events(test_metrics: Dict[Metric, float]) -> None:
    """
    임계값 이벤트가 올바르게 트리거되는지 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 자금 위기 임계값 테스트
    tracker.update_metric(Metric.MONEY, 900)
    events = tracker.check_threshold_events()
    assert any("자금 위기" in event for event in events), "자금 위기 이벤트가 트리거되지 않음"
    
    # 평판 위기 임계값 테스트
    tracker.update_metric(Metric.REPUTATION, 15)
    events = tracker.check_threshold_events()
    assert any("평판 위기" in event for event in events), "평판 위기 이벤트가 트리거되지 않음"
    
    # 시설 위기 임계값 테스트
    tracker.update_metric(Metric.FACILITY, 25)
    events = tracker.check_threshold_events()
    assert any("시설 위기" in event for event in events), "시설 위기 이벤트가 트리거되지 않음"
    
    # 직원 위기 임계값 테스트
    tracker.update_metric(Metric.STAFF_FATIGUE, 85)
    events = tracker.check_threshold_events()
    assert any("직원 위기" in event for event in events), "직원 위기 이벤트가 트리거되지 않음"


def test_extreme_case_bankruptcy(test_metrics: Dict[Metric, float]) -> None:
    """
    극한 상황 - 파산 시나리오를 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 자금을 0으로 설정 (파산)
    tracker.update_metric(Metric.MONEY, 0)
    
    # 자금이 0 이하로 내려가지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.MONEY] == 0, "자금이 0 이하로 내려감"
    
    # 임계값 이벤트 확인
    events = tracker.check_threshold_events()
    assert any("자금 위기" in event for event in events), "파산 시 자금 위기 이벤트가 트리거되지 않음"


def test_extreme_case_zero_reputation(test_metrics: Dict[Metric, float]) -> None:
    """
    극한 상황 - 평판 0 시나리오를 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 평판을 0으로 설정
    tracker.update_metric(Metric.REPUTATION, 0)
    
    # 평판이 0 이하로 내려가지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.REPUTATION] == 0, "평판이 0 이하로 내려감"
    
    # 임계값 이벤트 확인
    events = tracker.check_threshold_events()
    assert any("평판 위기" in event for event in events), "평판 0 시 평판 위기 이벤트가 트리거되지 않음"
    
    # 연쇄 효과 확인 (평판 0은 자금에 큰 영향을 줘야 함)
    initial_money = metrics[Metric.MONEY]
    tracker.apply_cascade_effects([Metric.REPUTATION])
    
    # 자금이 감소해야 함
    current_money = tracker.get_metrics()[Metric.MONEY]
    assert current_money < initial_money, "평판 0이 자금에 영향을 주지 않음"


def test_extreme_case_max_values(test_metrics: Dict[Metric, float]) -> None:
    """
    극한 상황 - 최대값 시나리오를 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker(initial_metrics=test_metrics)
    
    # 모든 지표를 최대값으로 설정
    tracker.update_metric(Metric.MONEY, 1000000000)  # 매우 큰 값
    tracker.update_metric(Metric.REPUTATION, 100)
    tracker.update_metric(Metric.HAPPINESS, 100)
    tracker.update_metric(Metric.INVENTORY, 1000000)  # 매우 큰 값
    tracker.update_metric(Metric.FACILITY, 100)
    
    # 지표가 최대값을 초과하지 않는지 확인
    metrics = tracker.get_metrics()
    assert metrics[Metric.REPUTATION] == 100, "평판이 최대값을 초과함"
    assert metrics[Metric.HAPPINESS] == 100, "행복이 최대값을 초과함"
    assert metrics[Metric.SUFFERING] == 0, "고통이 최소값 미만으로 내려감"
    assert metrics[Metric.FACILITY] == 100, "시설 상태가 최대값을 초과함"


def test_autoplay_simulation() -> None:
    """
    자동 플레이 시뮬레이션을 통해 시스템 안정성을 검증합니다.
    """
    # 트래커 생성
    tracker = MetricsTracker()
    
    # 100일 시뮬레이션
    for day in range(1, 101):
        # 불확실성 요소 적용
        tracker.uncertainty_apply_random_fluctuation(day, intensity=0.1, seed=day)
        
        # 랜덤 업데이트 적용
        random_updates = {}
        for metric in list(Metric):
            if random.random() < 0.3:  # 30% 확률로 각 지표 업데이트
                current = tracker.get_metrics()[metric]
                change = (random.random() * 20) - 10  # -10 ~ +10 범위의 변화
                random_updates[metric] = current + change
        
        if random_updates:
            tracker.tradeoff_update_metrics(random_updates)
        
        # 임계값 이벤트 확인
        tracker.check_threshold_events()
        
        # 10일마다 스냅샷 생성
        if day % 10 == 0:
            with tempfile.TemporaryDirectory() as temp_dir:
                tracker.snapshot_dir = temp_dir
                tracker.create_snapshot()
    
    # 시뮬레이션 후 상태 확인
    final_metrics = tracker.get_metrics()
    
    # 행복-고통 시소 불변식 검증
    assert are_happiness_suffering_balanced(
        final_metrics[Metric.HAPPINESS], final_metrics[Metric.SUFFERING]
    ), "시뮬레이션 후 시소 불변식 위반"
    
    # 모든 지표가 유효 범위 내에 있는지 확인
    for metric, value in final_metrics.items():
        assert value >= 0, f"{metric} 값이 음수임"
        if metric in {Metric.REPUTATION, Metric.HAPPINESS, Metric.SUFFERING, Metric.STAFF_FATIGUE, Metric.FACILITY}:
            assert value <= 100, f"{metric} 값이 100을 초과함"


def test_performance_10k_turns() -> None:
    """
    10,000턴 성능 테스트를 수행합니다.
    """
    import time
    
    # 트래커 생성
    tracker = MetricsTracker()
    
    # 시작 시간 기록
    start_time = time.time()
    
    # 10,000턴 시뮬레이션
    for day in range(1, 10001):
        # 불확실성 요소 적용
        tracker.uncertainty_apply_random_fluctuation(day, intensity=0.1)
        
        # 간단한 업데이트 적용
        if day % 10 == 0:
            tracker.tradeoff_update_metrics({
                Metric.MONEY: tracker.get_metrics()[Metric.MONEY] + 100,
                Metric.REPUTATION: min(100, tracker.get_metrics()[Metric.REPUTATION] + 1),
            })
        
        # 임계값 이벤트 확인
        if day % 100 == 0:
            tracker.check_threshold_events()
    
    # 종료 시간 기록
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 5초 이내에 완료되어야 함
    assert elapsed_time <= 5, f"10,000턴 시뮬레이션이 5초를 초과함 (실제: {elapsed_time:.2f}초)"
    
    # 메모리 사용량은 프로세스 외부에서 측정해야 하므로 여기서는 생략
    
    # 최종 상태 확인
    final_metrics = tracker.get_metrics()
    
    # 행복-고통 시소 불변식 검증
    assert are_happiness_suffering_balanced(
        final_metrics[Metric.HAPPINESS], final_metrics[Metric.SUFFERING]
    ), "성능 테스트 후 시소 불변식 위반"

"""
이벤트 엔진 및 연쇄 효과 시스템 테스트 모듈

이 모듈은 Chicken-RNG 게임의 이벤트 엔진과 연쇄 효과 시스템을 테스트합니다.
다양한 시나리오와 엣지 케이스를 검증하여 시스템의 안정성을 확보합니다.

핵심 철학:
- 정답 없음: 모든 테스트는 다양한 시나리오를 검증합니다
- 트레이드오프: 테스트는 이벤트 효과의 트레이드오프 관계를 확인합니다
- 불확실성: 시드 기반 테스트로 불확실성 요소의 재현성을 검증합니다
"""

import os
import pytest
import tempfile
from typing import Dict

from schema import Metric
from src.metrics.tracker import MetricsTracker
from src.events.models import (
    Event,
    Trigger,
    Effect,
    EventCategory,
    TriggerCondition,
)
from src.events.schema import (
    load_events_from_toml,
    load_events_from_json,
    save_events_to_json,
)
from src.events.engine import EventEngine
from src.events.integration import GameEventSystem


@pytest.fixture
def sample_metrics() -> Dict[Metric, float]:
    """샘플 지표 데이터를 제공합니다."""
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
def metrics_tracker(sample_metrics) -> MetricsTracker:
    """테스트용 MetricsTracker 인스턴스를 제공합니다."""
    return MetricsTracker(initial_metrics=sample_metrics)


@pytest.fixture
def event_engine(metrics_tracker) -> EventEngine:
    """테스트용 EventEngine 인스턴스를 제공합니다."""
    # 실제 파일 경로 확인
    events_file = "data/events.toml"
    tradeoff_file = "data/tradeoff_matrix.toml"

    # 현재 작업 디렉토리 기준 경로 조정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_path = os.path.join(base_dir, events_file)
    tradeoff_path = os.path.join(base_dir, tradeoff_file)

    # 파일 존재 여부 확인
    if not os.path.exists(events_path):
        events_path = None
    if not os.path.exists(tradeoff_path):
        tradeoff_path = None

    # 이벤트 엔진 생성
    return EventEngine(
        metrics_tracker=metrics_tracker,
        events_file=events_path,
        tradeoff_file=tradeoff_path,
        seed=42,  # 테스트 재현성을 위한 고정 시드
    )


@pytest.fixture
def game_event_system() -> GameEventSystem:
    """테스트용 GameEventSystem 인스턴스를 제공합니다."""
    # 실제 파일 경로 확인
    events_file = "data/events.toml"
    tradeoff_file = "data/tradeoff_matrix.toml"

    # 현재 작업 디렉토리 기준 경로 조정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_path = os.path.join(base_dir, events_file)
    tradeoff_path = os.path.join(base_dir, tradeoff_file)

    # 파일 존재 여부 확인
    if not os.path.exists(events_path):
        events_path = None
    if not os.path.exists(tradeoff_path):
        tradeoff_path = None

    # 게임 이벤트 시스템 생성
    return GameEventSystem(
        events_file=events_path,
        tradeoff_file=tradeoff_path,
        seed=42,  # 테스트 재현성을 위한 고정 시드
    )


def test_event_application(event_engine, sample_metrics):
    """이벤트 효과가 지표에 정확히 반영되는지 테스트합니다."""
    # 테스트용 이벤트 생성
    effect = Effect(metric=Metric.MONEY, formula="-500")
    event = Event(
        id="test_event",
        type=EventCategory.RANDOM,
        effects=[effect],
        probability=1.0,  # 항상 발생
    )

    # 이벤트 큐에 추가
    event_engine.event_queue.append(event)

    # 효과 적용
    updated_metrics = event_engine.apply_effects()

    # 결과 검증
    assert updated_metrics[Metric.MONEY] == sample_metrics[Metric.MONEY] - 500


def test_threshold_trigger(event_engine, sample_metrics):
    """임계값 이벤트가 올바르게 트리거되는지 테스트합니다."""
    # 테스트용 임계값 이벤트 생성
    trigger = Trigger(
        metric=Metric.REPUTATION,
        condition=TriggerCondition.LESS_THAN,
        value=60.0,
    )
    effect = Effect(metric=Metric.MONEY, formula="-1000")
    event = Event(
        id="test_threshold_event",
        type=EventCategory.THRESHOLD,
        trigger=trigger,
        effects=[effect],
    )

    # 이벤트 목록에 추가
    event_engine.events = [event]

    # 임계값 트리거 평가
    triggered_events = event_engine.evaluate_triggers()

    # 결과 검증
    assert len(triggered_events) == 1
    assert triggered_events[0].id == "test_threshold_event"

    # 알림 큐 확인
    assert len(event_engine.alert_queue) == 1


def test_cascade_chain(event_engine, metrics_tracker, sample_metrics):
    """3단계 연쇄 효과의 정확도를 테스트합니다."""
    # 연쇄 효과 매트릭스 설정
    event_engine.cascade_matrix = {
        Metric.REPUTATION: [
            {
                "target": "MONEY",
                "formula": "-500",
                "message": "평판 하락으로 인한 매출 감소",
            }
        ],
        Metric.MONEY: [
            {
                "target": "FACILITY",
                "formula": "-10",
                "message": "자금 부족으로 인한 시설 관리 소홀",
            }
        ],
        Metric.FACILITY: [
            {
                "target": "STAFF_FATIGUE",
                "formula": "value + 10",
                "message": "시설 악화로 인한 직원 피로도 증가",
            }
        ],
    }

    # 초기 이벤트 효과 적용 (평판 하락)
    effect = Effect(metric=Metric.REPUTATION, formula="-20")
    event = Event(
        id="test_cascade_event",
        type=EventCategory.RANDOM,
        effects=[effect],
    )

    # 이벤트 큐에 추가
    event_engine.event_queue.append(event)

    # 효과 적용
    updated_metrics = event_engine.apply_effects()

    # 결과 검증
    assert (
        updated_metrics[Metric.REPUTATION] < sample_metrics[Metric.REPUTATION]
    )  # 평판 하락
    assert updated_metrics[Metric.MONEY] < sample_metrics[Metric.MONEY]  # 자금 감소
    assert (
        updated_metrics[Metric.FACILITY] < sample_metrics[Metric.FACILITY]
    )  # 시설 악화
    assert (
        updated_metrics[Metric.STAFF_FATIGUE] > sample_metrics[Metric.STAFF_FATIGUE]
    )  # 직원 피로도 증가

    # 이벤트 메시지 확인
    events = metrics_tracker.get_events()
    assert len(events) >= 3  # 최소 3개의 연쇄 효과 메시지


def test_dag_validation():
    """순환 참조 감지 알고리즘을 테스트합니다."""
    # 테스트용 MetricsTracker 생성
    metrics_tracker = MetricsTracker()

    # 테스트용 EventEngine 생성
    event_engine = EventEngine(metrics_tracker=metrics_tracker)

    # 1. DAG인 경우 (순환 참조 없음)
    event_engine.cascade_matrix = {
        Metric.REPUTATION: [{"target": "MONEY", "formula": "-500"}],
        Metric.MONEY: [{"target": "FACILITY", "formula": "-10"}],
        Metric.FACILITY: [{"target": "STAFF_FATIGUE", "formula": "value + 10"}],
    }

    assert event_engine.is_dag_safe()

    # 2. 순환 참조가 있는 경우
    event_engine.cascade_matrix = {
        Metric.REPUTATION: [{"target": "MONEY", "formula": "-500"}],
        Metric.MONEY: [{"target": "FACILITY", "formula": "-10"}],
        Metric.FACILITY: [{"target": "REPUTATION", "formula": "-5"}],  # 순환 참조
    }

    assert not event_engine.is_dag_safe()


@pytest.mark.perf
def test_perf_1000_events(game_event_system):
    """1,000회 이벤트 시뮬레이션의 성능과 메모리 사용량을 테스트합니다."""
    import time
    import psutil

    # 현재 프로세스
    process = psutil.Process()

    # 시작 시간 및 메모리 사용량 기록
    start_time = time.time()
    start_memory = process.memory_info().rss

    # 1,000회 이벤트 시뮬레이션
    for _ in range(1000):
        game_event_system.update_day()

    # 종료 시간 및 메모리 사용량 기록
    end_time = time.time()
    end_memory = process.memory_info().rss

    # 소요 시간 및 메모리 사용량 계산
    elapsed_time = end_time - start_time
    memory_usage = (end_memory - start_memory) / (1024 * 1024)  # MB 단위

    print(f"소요 시간: {elapsed_time:.2f}초, 메모리 사용량: {memory_usage:.2f} MB")

    # 성능 요구사항 검증
    assert elapsed_time <= 3.0  # 3초 이내
    assert memory_usage <= 256.0  # 256 MB 이내


def test_event_schema_parsing():
    """이벤트 스키마 파싱 및 변환을 테스트합니다."""
    # 테스트용 TOML 문자열
    toml_content = """
    [[events]]
    id = "test_event"
    type = "RANDOM"
    priority = 10
    probability = 0.5
    
    [[events.effects]]
    metric = "MONEY"
    formula = "-500"
    message = "테스트 효과"
    """

    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp_toml:
        temp_toml.write(toml_content.encode())
        toml_path = temp_toml.name

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        json_path = temp_json.name

    try:
        # TOML에서 이벤트 로드
        events = load_events_from_toml(toml_path)

        # 검증
        assert len(events) == 1
        assert events[0].id == "test_event"
        assert events[0].type == EventCategory.RANDOM
        assert events[0].priority == 10
        assert events[0].probability == 0.5
        assert len(events[0].effects) == 1
        assert events[0].effects[0].metric == Metric.MONEY
        assert events[0].effects[0].formula == "-500"
        assert events[0].effects[0].message == "테스트 효과"

        # JSON으로 저장
        save_events_to_json(events, json_path)

        # JSON에서 이벤트 로드
        json_events = load_events_from_json(json_path)

        # 검증
        assert len(json_events) == 1
        assert json_events[0].id == "test_event"
        assert json_events[0].type == EventCategory.RANDOM
        assert json_events[0].priority == 10
        assert json_events[0].probability == 0.5
        assert len(json_events[0].effects) == 1
        assert json_events[0].effects[0].metric == Metric.MONEY
        assert json_events[0].effects[0].formula == "-500"
        assert json_events[0].effects[0].message == "테스트 효과"

    finally:
        # 임시 파일 삭제
        os.unlink(toml_path)
        os.unlink(json_path)


def test_random_seed_reproducibility(sample_metrics):
    """난수 시드 설정으로 이벤트 발생의 재현성을 테스트합니다."""
    # 동일한 시드로 두 개의 이벤트 엔진 생성
    metrics_tracker1 = MetricsTracker(initial_metrics=sample_metrics.copy())
    metrics_tracker2 = MetricsTracker(initial_metrics=sample_metrics.copy())

    engine1 = EventEngine(metrics_tracker=metrics_tracker1, seed=12345)
    engine2 = EventEngine(metrics_tracker=metrics_tracker2, seed=12345)

    # 테스트용 랜덤 이벤트 생성
    effect = Effect(metric=Metric.MONEY, formula="value * (0.9 + 0.2 * random())")
    event1 = Event(
        id="test_random_event",
        type=EventCategory.RANDOM,
        effects=[effect],
        probability=0.5,
    )

    effect2 = Effect(metric=Metric.MONEY, formula="value * (0.9 + 0.2 * random())")
    event2 = Event(
        id="test_random_event",
        type=EventCategory.RANDOM,
        effects=[effect2],
        probability=0.5,
    )

    # 이벤트 목록에 추가
    engine1.events = [event1]
    engine2.events = [event2]

    # 여러 턴 실행
    for _ in range(10):
        engine1.poll()
        engine2.poll()

        # 이벤트 큐 상태 비교
        assert len(engine1.event_queue) == len(engine2.event_queue)

        # 효과 적용
        metrics1 = engine1.apply_effects()
        metrics2 = engine2.apply_effects()

        # 결과 비교
        assert metrics1[Metric.MONEY] == metrics2[Metric.MONEY]

        # 턴 증가
        engine1.current_turn += 1
        engine2.current_turn += 1


def test_uncertainty_factor():
    """불확실성 요소(±10% 변동)를 테스트합니다."""
    # 테스트용 MetricsTracker 생성
    initial_metrics = {
        Metric.MONEY: 10000.0,
        Metric.REPUTATION: 50.0,
    }
    metrics_tracker = MetricsTracker(initial_metrics=initial_metrics)

    # 고정 시드로 불확실성 요소 적용
    metrics_tracker.uncertainty_apply_random_fluctuation(day=1, intensity=0.1, seed=42)

    # 결과 검증
    updated_metrics = metrics_tracker.get_metrics()

    # 원래 값의 ±10% 범위 내에 있는지 확인
    assert 9000.0 <= updated_metrics[Metric.MONEY] <= 11000.0
    assert 45.0 <= updated_metrics[Metric.REPUTATION] <= 55.0

    # 행복-고통 시소 불변식 확인
    assert (
        abs(
            updated_metrics[Metric.HAPPINESS]
            + updated_metrics[Metric.SUFFERING]
            - 100.0
        )
        < 0.001
    )


def test_integration_with_metrics_tracker(game_event_system):
    """이벤트 엔진과 MetricsTracker의 통합을 테스트합니다."""
    # 여러 일 진행
    for _ in range(5):
        game_event_system.update_day()

    # 결과 검증
    final_metrics = game_event_system.metrics_tracker.get_metrics()
    history = game_event_system.get_metrics_history()
    events = game_event_system.get_events_history()

    # 지표 변화 확인
    assert len(history) > 5  # 초기 상태 + 5일
    assert len(events) > 0  # 이벤트 발생 확인

    # 행복-고통 시소 불변식 확인
    assert (
        abs(final_metrics[Metric.HAPPINESS] + final_metrics[Metric.SUFFERING] - 100.0)
        < 0.001
    )


def test_tradeoff_matrix_loading(game_event_system):
    """tradeoff_matrix.toml 파일 로드를 테스트합니다."""
    # tradeoff_matrix.toml 파일 경로
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tradeoff_path = os.path.join(base_dir, "data/tradeoff_matrix.toml")

    # 파일 존재 여부 확인
    if not os.path.exists(tradeoff_path):
        pytest.skip("tradeoff_matrix.toml 파일이 없습니다.")

    # 새 이벤트 엔진으로 파일 로드
    metrics_tracker = MetricsTracker()
    event_engine = EventEngine(
        metrics_tracker=metrics_tracker,
        tradeoff_file=tradeoff_path,
    )

    # 연쇄 효과 매트릭스 확인
    assert len(event_engine.cascade_matrix) > 0

    # DAG 안전성 확인
    assert event_engine.is_dag_safe()


def test_event_file_loading(game_event_system):
    """events.toml 파일 로드를 테스트합니다."""
    # events.toml 파일 경로
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_path = os.path.join(base_dir, "data/events.toml")

    # 파일 존재 여부 확인
    if not os.path.exists(events_path):
        pytest.skip("events.toml 파일이 없습니다.")

    # 새 이벤트 엔진으로 파일 로드
    metrics_tracker = MetricsTracker()
    event_engine = EventEngine(
        metrics_tracker=metrics_tracker,
        events_file=events_path,
    )

    # 이벤트 목록 확인
    assert len(event_engine.events) > 0


def test_noRightAnswer_simulate_scenario(game_event_system):
    """시나리오 시뮬레이션을 테스트합니다."""
    # 테스트 시나리오 정의
    scenario = {
        "seed": 42,
        "initial_metrics": {
            Metric.MONEY: 5000.0,
            Metric.REPUTATION: 30.0,
            Metric.HAPPINESS: 40.0,
            Metric.SUFFERING: 60.0,
            Metric.INVENTORY: 50.0,
            Metric.STAFF_FATIGUE: 70.0,
            Metric.FACILITY: 40.0,
        },
    }

    # 시나리오 시뮬레이션
    result = game_event_system.noRightAnswer_simulate_scenario(scenario, days=5)

    # 결과 검증
    assert "final_metrics" in result
    assert "metrics_history" in result
    assert "events_history" in result
    assert "alerts" in result

    # 히스토리 길이 확인
    assert len(result["metrics_history"]) == 5

    # 행복-고통 시소 불변식 확인
    final_metrics = result["final_metrics"]
    assert (
        abs(final_metrics[Metric.HAPPINESS] + final_metrics[Metric.SUFFERING] - 100.0)
        < 0.001
    )

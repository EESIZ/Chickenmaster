"""
게임-이벤트 시스템 통합

이벤트 시스템을 게임의 메인 루프와 통합하여 매 턴마다 적절한 이벤트를 발생시킵니다.
"""

from pathlib import Path
from typing import Any

from game_constants import Metric
from src.events.engine import EventEngine
from src.events.models import Alert
from src.metrics.tracker import MetricsTracker


class GameEventSystem:
    """
    게임 이벤트 시스템

    이 클래스는 이벤트 엔진과 지표 추적기를 통합하여
    게임 내 이벤트와 지표 변화를 관리합니다.
    """

    def __init__(
        self,
        metrics_tracker: MetricsTracker | None = None,
        events_file: str | None = "data/events.toml",
        tradeoff_file: str | None = "data/tradeoff_matrix.toml",
        seed: int | None = None,
    ):
        """
        GameEventSystem 초기화

        Args:
            metrics_tracker: 지표 추적기 (기본값: None, 이 경우 새로 생성)
            events_file: 이벤트 정의 파일 경로 (기본값: "data/events.toml")
            tradeoff_file: 트레이드오프 매트릭스 파일 경로 (기본값: "data/tradeoff_matrix.toml")
            seed: 난수 생성 시드 (기본값: None)
        """
        # 지표 추적기 초기화
        self.metrics_tracker = metrics_tracker or MetricsTracker()

        # 이벤트 엔진 초기화
        events_path = None
        if events_file and Path(events_file).exists():
            events_path = events_file

        tradeoff_path = None
        if tradeoff_file and Path(tradeoff_file).exists():
            tradeoff_path = tradeoff_file

        self.event_engine = EventEngine(
            metrics_tracker=self.metrics_tracker,
            events_file=events_path,
            tradeoff_file=tradeoff_path,
            seed=seed,
        )

        # 현재 게임 일수
        self.day = 0

    def update_day(self) -> dict[Metric, float]:
        """
        하루를 진행하고 이벤트를 처리합니다.

        Returns:
            Dict[Metric, float]: 업데이트 후 지표 상태
        """
        # 일수 증가
        self.day += 1

        # 불확실성 요소 적용
        self.metrics_tracker.uncertainty_apply_random_fluctuation(
            day=self.day, seed=self.event_engine.rng.randint(0, 10000)
        )

        # 이벤트 엔진 업데이트
        metrics = self.event_engine.update()

        # 임계값 이벤트 확인
        self.metrics_tracker.check_threshold_events()

        # 스냅샷 생성
        self.metrics_tracker.create_snapshot()

        return metrics

    def get_alerts(self, count: int | None = None) -> list[Alert]:
        """
        알림을 가져옵니다.

        Args:
            count: 가져올 알림 수 (기본값: None, 모든 알림 반환)

        Returns:
            List[Alert]: 알림 목록
        """
        return self.event_engine.get_alerts(count)

    def get_events_history(self, count: int | None = None) -> list[str]:
        """
        이벤트 히스토리를 가져옵니다.

        Args:
            count: 가져올 이벤트 수 (기본값: None, 모든 이벤트 반환)

        Returns:
            List[str]: 이벤트 메시지 목록
        """
        return self.metrics_tracker.get_events(count)

    def get_metrics_history(self, steps: int | None = None) -> list[dict[Metric, float]]:
        """
        지표 변화 히스토리를 가져옵니다.

        Args:
            steps: 가져올 히스토리 단계 수 (기본값: None, 전체 히스토리 반환)

        Returns:
            List[Dict[Metric, float]]: 지표 변화 히스토리
        """
        return self.metrics_tracker.get_history(steps)

    def validate_tradeoff_matrix(self) -> bool:
        """
        트레이드오프 매트릭스의 DAG 안전성을 검증합니다.

        Returns:
            bool: DAG이면 True, 그렇지 않으면 False
        """
        return self.event_engine.is_dag_safe()

    def set_seed(self, seed: int | None = None) -> None:
        """
        난수 생성 시드를 설정합니다.

        Args:
            seed: 난수 생성 시드 (기본값: None)
        """
        self.event_engine.set_seed(seed)

    def reset(
        self, seed: int | None = None, initial_metrics: dict[Metric, float] | None = None
    ) -> None:
        """
        게임 이벤트 시스템을 초기 상태로 리셋합니다.

        Args:
            seed: 난수 생성 시드 (기본값: None)
            initial_metrics: 초기 지표 설정 (기본값: None)
        """
        # 일수 초기화
        self.day = 0

        # 지표 추적기 리셋
        self.metrics_tracker.reset()

        # 초기 지표 설정
        if initial_metrics:
            for metric, value in initial_metrics.items():
                self.metrics_tracker.update_metric(metric, value)

        # 시드 설정
        if seed is not None:
            self.set_seed(seed)

        # 이벤트 엔진 큐 초기화
        self.event_engine.event_queue.clear()
        self.event_engine.alert_queue.clear()
        self.event_engine.current_turn = 0

    def simulate_scenario_no_right_answer(
        self, scenario: dict[str, Any], days: int = 10
    ) -> dict[str, Any]:
        """
        시나리오를 시뮬레이션합니다. 정답이 없는 문제에서 사용됩니다.

        Args:
            scenario: 시뮬레이션할 시나리오
            days: 시뮬레이션 일수

        Returns:
            dict[str, Any]: 시뮬레이션 결과
        """
        # 시드 설정
        if "seed" in scenario:
            self.set_seed(scenario["seed"])

        # 초기 지표 설정
        if "initial_metrics" in scenario:
            for metric, value in scenario["initial_metrics"].items():
                self.metrics_tracker.update_metric(metric, value)

        # 시뮬레이션 실행
        history = []
        events_history = []
        metrics: dict[Metric, float] = {}

        for _ in range(days):
            # 하루 진행
            metrics = self.update_day()
            history.append(metrics.copy())

            # 이벤트 히스토리 가져오기
            events = self.get_events_history()
            events_history.extend(events)

        # 결과 반환
        return {
            "final_metrics": metrics,
            "metrics_history": history,
            "events_history": events_history,
            "alerts": self.get_alerts(),
        }

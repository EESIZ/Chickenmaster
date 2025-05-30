"""
이벤트 엔진 모듈

이 모듈은 Chicken-RNG 게임의 이벤트 엔진을 구현합니다.
이벤트 평가, 트리거, 효과 적용 및 연쇄 효과 처리를 담당합니다.

핵심 철학:
- 정답 없음: 모든 이벤트는 득과 실을 동시에 가져옵니다
- 트레이드오프: 이벤트 효과는 항상 트레이드오프 관계를 가집니다
- 불확실성: 이벤트 발생과 효과는 예측 불가능한 요소에 영향을 받습니다
"""

import json
import random
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from game_constants import Metric
from src.events.models import Alert, Event, EventCategory
from src.events.schema import load_events_from_json, load_events_from_toml
from src.metrics.tracker import MetricsTracker


class EventEngine:
    """
    이벤트 엔진 클래스

    이 클래스는 게임의 이벤트 시스템을 관리합니다.
    이벤트 평가, 트리거, 효과 적용 및 연쇄 효과 처리를 담당합니다.
    """

    def __init__(
        self,
        metrics_tracker: MetricsTracker,
        events_file: str | None = None,
        tradeoff_file: str | None = None,
        seed: int | None = None,
        max_cascade_depth: int = 10,
    ):
        """
        EventEngine 초기화

        Args:
            metrics_tracker: 지표 추적기
            events_file: 이벤트 정의 파일 경로 (기본값: None)
            tradeoff_file: 트레이드오프 매트릭스 파일 경로 (기본값: None)
            seed: 난수 생성 시드 (기본값: None)
            max_cascade_depth: 최대 연쇄 깊이 (기본값: 10)
        """
        self.metrics_tracker = metrics_tracker
        self.events: list[Event] = []
        self.event_queue: deque[Event] = deque()
        self.alert_queue: deque[Alert] = deque()
        self.cascade_matrix: dict[Metric, list[dict[str, Any]]] = {}
        self.max_cascade_depth = max_cascade_depth
        self.current_turn = 0

        # 난수 생성기 초기화
        self.rng = random.Random(seed)

        # 이벤트 파일 로드
        if events_file:
            self.load_events(events_file)

        # 트레이드오프 매트릭스 로드
        if tradeoff_file:
            self.load_tradeoff_matrix(tradeoff_file)

    def load_events(self, filepath: str) -> None:
        """
        이벤트 정의 파일을 로드합니다.

        Args:
            filepath: 이벤트 정의 파일 경로
        """
        if filepath.endswith(".toml"):
            self.events = load_events_from_toml(filepath)
        elif filepath.endswith(".json"):
            self.events = load_events_from_json(filepath)
        else:
            raise ValueError(f"지원되지 않는 파일 형식: {filepath}")

    def load_tradeoff_matrix(self, filepath: str) -> None:
        """
        트레이드오프 매트릭스 파일을 로드합니다.

        Args:
            filepath: 트레이드오프 매트릭스 파일 경로
        """
        import tomllib

        try:
            with open(filepath, "rb") as f:
                data = tomllib.load(f)

            # 연쇄 효과 매트릭스 로드
            if "cascade" in data:
                for source_metric, targets in data["cascade"].items():
                    try:
                        metric = Metric[source_metric]
                        self.cascade_matrix[metric] = targets
                    except KeyError:
                        print(f"알 수 없는 지표: {source_metric}")
        except Exception as e:
            print(f"트레이드오프 매트릭스 로드 실패: {e}")

    def poll(self) -> list[Event]:
        """
        현재 턴에 발생 가능한 이벤트를 폴링합니다.

        Returns:
            List[Event]: 발생 가능한 이벤트 목록
        """
        # 현재 지표 상태 가져오기
        current_metrics = self.metrics_tracker.get_metrics()

        # 발생 가능한 이벤트 목록
        triggered_events = []

        # 모든 이벤트 평가
        for event in self.events:
            # 쿨다운 확인
            if not event.can_fire(self.current_turn):
                continue

            # 트리거 조건 평가
            if event.evaluate_trigger(current_metrics, self.rng):
                triggered_events.append(event)

        # 우선순위에 따라 정렬 (높은 우선순위가 먼저)
        triggered_events.sort(key=lambda e: -e.priority)

        # 이벤트 큐에 추가
        for event in triggered_events:
            self.event_queue.append(event)

        return triggered_events

    def evaluate_triggers(self) -> list[Event]:
        """
        임계값 기반 트리거를 평가합니다.

        Returns:
            List[Event]: 트리거된 이벤트 목록
        """
        # 현재 지표 상태 가져오기
        current_metrics = self.metrics_tracker.get_metrics()

        # 트리거된 이벤트 목록
        threshold_events = []

        # THRESHOLD 타입 이벤트만 평가
        for event in self.events:
            if event.type != EventCategory.THRESHOLD:
                continue

            # 쿨다운 확인
            if not event.can_fire(self.current_turn):
                continue

            # 트리거 조건 평가
            if event.trigger and event.trigger.evaluate(current_metrics):
                threshold_events.append(event)

                # 알림 생성
                alert = Alert(
                    event_id=event.id,
                    message=event.message or f"임계값 이벤트 발생: {event.id}",
                    metrics=current_metrics.copy(),
                    turn=self.current_turn,
                    severity="WARNING",
                )
                self.alert_queue.append(alert)

                # 이벤트 큐에 추가
                self.event_queue.append(event)

        return threshold_events

    def apply_effects(self) -> dict[Metric, float]:
        """
        큐에 있는 모든 이벤트의 효과를 적용합니다.

        Returns:
            Dict[Metric, float]: 효과가 적용된 최종 지표 상태
        """
        # 현재 지표 상태 가져오기
        current_metrics = self.metrics_tracker.get_metrics()

        # 이벤트 큐가 비어있으면 현재 상태 반환
        if not self.event_queue:
            return current_metrics

        # 모든 이벤트 효과 적용
        while self.event_queue:
            event = self.event_queue.popleft()

            # 이벤트 발생 기록
            event.last_fired = self.current_turn

            # 효과 적용
            updates = {}
            for effect in event.effects:
                new_value = effect.apply(current_metrics)
                updates[effect.metric] = new_value

                # 이벤트 메시지 추가
                if effect.message:
                    self.metrics_tracker.add_event(effect.message)

            # 지표 업데이트
            self.metrics_tracker.tradeoff_update_metrics(updates)

            # 연쇄 효과 처리
            self._process_cascade_effects(set(updates.keys()), 0)

            # 업데이트된 지표 상태 가져오기
            current_metrics = self.metrics_tracker.get_metrics()

        return current_metrics

    def _process_cascade_effects(self, changed_metrics: set[Metric], depth: int) -> None:
        """
        지표 변화의 연쇄 효과를 처리합니다.

        Args:
            changed_metrics: 변경된 지표 집합
            depth: 현재 연쇄 깊이
        """
        # 최대 연쇄 깊이 확인
        if depth >= self.max_cascade_depth:
            return

        # 연쇄 효과가 없으면 종료
        if not self.cascade_matrix:
            return

        # 현재 지표 상태 가져오기 (항상 최신 상태 사용)
        current_metrics = self.metrics_tracker.get_metrics()

        # 연쇄 효과 적용
        cascade_updates = {}
        next_changed_metrics = set()

        for metric in changed_metrics:
            if metric not in self.cascade_matrix:
                continue

            # 현재 지표 값 가져오기
            current_value = current_metrics[metric]

            # 연쇄 효과 적용
            for edge in self.cascade_matrix[metric]:
                target_metric_name = edge["target"]
                formula = edge["formula"]

                try:
                    # 대상 지표 확인
                    target_metric = Metric[target_metric_name]

                    # 현재 대상 지표 값 가져오기 (누적 적용을 위해)
                    target_current_value = current_metrics[target_metric]

                    # 수식 평가 방식 결정
                    if "%" in formula:
                        # 백분율 표기법 처리
                        formula_clean = formula.replace("%", "")
                        percentage = float(formula_clean) / 100
                        # 백분율은 현재 값에 대한 상대적 변화량
                        result = target_current_value * (1 + percentage)
                    else:
                        try:
                            # 단순 숫자인 경우 (변화량으로 처리)
                            delta = float(formula)
                            result = target_current_value + delta
                        except ValueError:
                            # 복잡한 수식인 경우
                            # value는 변경된 소스 지표의 현재 값
                            value = current_value

                            # 수식에 'value'가 포함되어 있는지 확인
                            if "value" in formula:
                                # value를 사용하는 수식 (예: "value * 0.9")
                                result = eval(formula, {"__builtins__": {}}, {"value": value})
                            else:
                                # value를 사용하지 않는 수식 (예: "10")
                                # 이 경우 변화량으로 처리
                                delta = eval(formula, {"__builtins__": {}}, {})
                                result = target_current_value + float(delta)

                    # 결과 저장
                    cascade_updates[target_metric] = result
                    next_changed_metrics.add(target_metric)

                    # 이벤트 메시지 추가
                    if "message" in edge:
                        self.metrics_tracker.add_event(edge["message"])
                except Exception as e:
                    print(f"연쇄 효과 적용 실패: {e}")

        # 연쇄 효과가 있으면 적용
        if cascade_updates:
            # 지표 업데이트 (누적 적용)
            self.metrics_tracker.tradeoff_update_metrics(cascade_updates)

            # 다음 단계 연쇄 효과 처리 (변경된 지표만)
            if next_changed_metrics:
                self._process_cascade_effects(next_changed_metrics, depth + 1)

    def update(self) -> dict[Metric, float]:
        """
        이벤트 엔진을 한 턴 업데이트합니다.

        Returns:
            Dict[Metric, float]: 업데이트 후 지표 상태
        """
        # 턴 증가
        self.current_turn += 1

        # 이벤트 폴링
        self.poll()

        # 임계값 트리거 평가
        self.evaluate_triggers()

        # 효과 적용
        return self.apply_effects()

    def get_alerts(self, count: int | None = None) -> list[Alert]:
        """
        알림 큐에서 알림을 가져옵니다.

        Args:
            count: 가져올 알림 수 (기본값: None, 모든 알림 반환)

        Returns:
            List[Alert]: 알림 목록
        """
        if count is None:
            alerts = list(self.alert_queue)
            self.alert_queue.clear()
            return alerts

        alerts = []
        for _ in range(min(count, len(self.alert_queue))):
            alerts.append(self.alert_queue.popleft())

        return alerts

    def is_dag_safe(self) -> bool:
        """
        연쇄 효과 그래프가 DAG(Directed Acyclic Graph)인지 확인합니다.

        Returns:
            bool: DAG이면 True, 그렇지 않으면 False
        """
        # 연쇄 효과가 없으면 DAG로 간주
        if not self.cascade_matrix:
            return True

        # 간선 목록 생성
        edges = []
        for source, targets in self.cascade_matrix.items():
            for edge in targets:
                try:
                    target = Metric[edge["target"]]
                    edges.append((source.name, target.name))
                except KeyError:
                    continue

        # Kahn의 위상 정렬 알고리즘으로 DAG 확인
        return self._is_dag_kahn(edges)

    def _is_dag_kahn(self, edges: list[tuple[str, str]]) -> bool:
        """
        Kahn의 위상 정렬 알고리즘으로 DAG 여부를 확인합니다.

        Args:
            edges: 간선 목록 (source, target)

        Returns:
            bool: DAG이면 True, 그렇지 않으면 False
        """
        # 진입 차수와 인접 리스트 초기화
        in_degree: dict[str, int] = defaultdict(int)
        adj_list = defaultdict(list)

        # 그래프 구성
        for u, v in edges:
            adj_list[u].append(v)
            in_degree[v] += 1

        # 진입 차수가 0인 노드 큐에 추가
        queue = [node for node in adj_list if in_degree[node] == 0]

        # 방문한 노드 수
        visited = 0

        # 위상 정렬
        while queue:
            u = queue.pop(0)
            visited += 1

            for v in adj_list[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        # 모든 노드를 방문했으면 DAG
        all_nodes = set(adj_list.keys()) | set(in_degree.keys())
        return visited == len(all_nodes)

    def set_seed(self, seed: int | None = None) -> None:
        """
        난수 생성 시드를 설정합니다.

        Args:
            seed: 난수 생성 시드 (기본값: None)
        """
        self.rng = random.Random(seed)

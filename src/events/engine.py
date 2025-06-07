"""
이벤트 엔진 모듈

이 모듈은 Chicken-RNG 게임의 이벤트 엔진을 구현합니다.
이벤트 평가, 트리거, 효과 적용 및 연쇄 효과 처리를 담당합니다.

핵심 철학:
- 정답 없음: 모든 이벤트는 득과 실을 동시에 가져옵니다
- 트레이드오프: 이벤트 효과는 항상 트레이드오프 관계를 가집니다
- 불확실성: 이벤트 발생과 효과는 예측 불가능한 요소에 영향을 받습니다
"""

import random
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

from game_constants import FLOAT_EPSILON, Metric as MetricEnum
from src.events.models import Alert  # models.Event는 더 이상 직접 사용하지 않음
from src.events.schema import Event as PydanticEvent  # PydanticEvent alias 사용
from src.events.schema import EventContainer  # EventContainer import 추가
from src.events.schema import EventTrigger, load_events_from_json, load_events_from_toml
from src.metrics.tracker import MetricsTracker

# 상수 정의
FLOAT_COMPARISON_EPSILON = 0.001


class EventEngine:
    """
    이벤트 엔진 클래스

    이 클래스는 게임의 이벤트 시스템을 관리합니다.
    이벤트 평가, 트리거, 효과 적용 및 연쇄 효과 처리를 담당합니다.
    """

    events: EventContainer[
        PydanticEvent
    ] | list  # self.events 타입을 EventContainer 또는 비어있을 경우 list로 명시
    event_queue: deque[PydanticEvent]  # event_queue 타입을 deque[PydanticEvent]로 명시

    def __init__(
        self,
        metrics_tracker: MetricsTracker,
        events_file: Optional[str] = None,
        tradeoff_file: Optional[str] = None,
        seed: Optional[int] = None,
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
<<<<<<< HEAD
        self.events = []  # 초기에는 빈 리스트
        self.event_queue = deque()
=======
        self.events_container: Optional[EventContainer[PydanticEvent]] = None
        self.events: List[PydanticEvent] = []
        self.event_queue: deque[PydanticEvent] = deque()
>>>>>>> origin/main
        self.alert_queue: deque[Alert] = deque()
        self.cascade_matrix: Dict[MetricEnum, List[Dict[str, Any]]] = {}
        self.max_cascade_depth = max_cascade_depth
        self.current_turn = 0

        # 난수 생성기 초기화
        self.rng = random.Random(seed)

        # 이벤트 파일 로드
        if events_file:
            self.load_events(Path(events_file))

        # 트레이드오프 매트릭스 로드
        if tradeoff_file:
            self.load_tradeoff_matrix(tradeoff_file)

    def set_seed(self, seed: Optional[int] = None) -> None:
        """
        난수 생성 시드를 설정합니다.

        Args:
            seed: 난수 생성 시드 (기본값: None)
        """
        self.rng = random.Random(seed)

    def load_events(self, filepath: Path) -> None:
        """
        이벤트 정의 파일을 로드합니다.

        Args:
            filepath: 이벤트 정의 파일 경로 (Path 객체)
        """
        if filepath.suffix == ".toml":
<<<<<<< HEAD
            # load_events_from_toml은 EventContainer[PydanticEvent]를 반환
            self.events = load_events_from_toml(filepath)
=======
            self.events_container = load_events_from_toml(filepath)
>>>>>>> origin/main
        elif filepath.suffix == ".json":
            self.events_container = load_events_from_json(filepath)
        else:
            raise ValueError(f"지원되지 않는 파일 형식: {filepath}")
            
        # EventContainer에서 events 리스트로 변환
        if self.events_container and hasattr(self.events_container, "events"):
            self.events = list(self.events_container.events)

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
                        metric = getattr(MetricEnum, source_metric.upper(), None)
                        if metric is not None:
                            self.cascade_matrix[metric] = targets
                        else:
                            print(f"알 수 없는 지표: {source_metric}")
                    except KeyError:
                        print(f"알 수 없는 지표: {source_metric}")
        except Exception as e:
            print(f"트레이드오프 매트릭스 로드 실패: {e}")

    def poll(self) -> List[PydanticEvent]:
        """
        현재 턴에 발생 가능한 이벤트를 폴링합니다.

        Returns:
            List[PydanticEvent]: 발생 가능한 이벤트 목록
        """
        current_metrics = self.metrics_tracker.get_metrics()
        triggered_events: List[PydanticEvent] = []

        events_to_iterate = []
        if self.events_container and hasattr(self.events_container, "events"):
            events_to_iterate = self.events_container.events
        elif self.events:
            events_to_iterate = self.events

        for event_data in events_to_iterate:
            can_fire_event = True
            # TODO: Cooldown 및 last_triggered_turn 로직 구현 필요
            # if event_data.cooldown > 0 and event_data.id in self.event_last_triggered_turn:
            #     if self.current_turn - self.event_last_triggered_turn[event_data.id] < event_data.cooldown:
            #         can_fire_event = False

            if not can_fire_event:
                continue

            if event_data.type == "THRESHOLD":
                if event_data.trigger and self._evaluate_pydantic_trigger(
                    event_data.trigger, current_metrics
                ):
                    triggered_events.append(event_data)
                    self.metrics_tracker.add_event(
                        f"Polled THRESHOLD: {event_data.id} - {event_data.name_ko}"
                    )
            elif event_data.type == "RANDOM":
                if self.rng.random() < event_data.probability:
                    triggered_events.append(event_data)
                    self.metrics_tracker.add_event(
                        f"Polled RANDOM: {event_data.id} - {event_data.name_ko}"
                    )
            # TODO: SCHEDULED, CASCADE 타입 처리

        # 우선순위에 따라 정렬 (PydanticEvent에 priority가 있으므로 사용 가능)
        triggered_events.sort(key=lambda e: -e.priority)

        for event_to_fire in triggered_events:
            self.event_queue.append(event_to_fire)  # 큐에는 PydanticEvent 저장

        return triggered_events  # 실제 발생 "가능성이 있는" 이벤트 목록 반환

    def _evaluate_pydantic_trigger(
        self, trigger: EventTrigger, current_metrics: Dict[MetricEnum, float]
    ) -> bool:
        """Pydantic EventTrigger 모델을 평가합니다."""
        metric_enum = getattr(
            MetricEnum, trigger.metric.upper(), None
        )  # trigger.metric이 문자열이므로 upper()로 Enum 멤버 이름과 일치시킴
        if not metric_enum or metric_enum not in current_metrics:
            print(f"[Debug] Metric {trigger.metric} not found in current_metrics or MetricEnum")
            return False
        current_value = current_metrics[metric_enum]

        condition_str = trigger.condition.upper()
        trigger_value = trigger.value

        if condition_str == "LESS_THAN":
            return current_value < trigger_value
        elif condition_str == "GREATER_THAN":
            return current_value > trigger_value
        elif condition_str == "EQUAL":
<<<<<<< HEAD
            return (
                trigger_value is not None
                and abs(current_value - trigger_value) < FLOAT_COMPARISON_EPSILON
            )
        elif condition_str == "NOT_EQUAL":
            return (
                trigger_value is not None
                and abs(current_value - trigger_value) >= FLOAT_COMPARISON_EPSILON
            )
=======
            return abs(current_value - trigger_value) < FLOAT_EPSILON  # 부동소수점 비교
        elif condition_str == "NOT_EQUAL":
            return abs(current_value - trigger_value) >= FLOAT_EPSILON
>>>>>>> origin/main
        elif condition_str == "GREATER_THAN_OR_EQUAL":
            return current_value >= trigger_value
        elif condition_str == "LESS_THAN_OR_EQUAL":
            return current_value <= trigger_value
        # TODO: IN_RANGE, NOT_IN_RANGE 구현 필요 (EventTrigger 모델에 range_min/max 없음)
        print(f"[Debug] Unknown condition: {trigger.condition}")
        return False

    def evaluate_triggers(self) -> List[PydanticEvent]:  # 반환 타입을 PydanticEvent로 명시
        """
        임계값 기반 트리거를 평가합니다.

        Returns:
            List[PydanticEvent]: 트리거된 이벤트 목록
        """
        current_metrics = self.metrics_tracker.get_metrics()
        threshold_events: List[PydanticEvent] = []  # 타입 명시

        events_to_iterate = []
        if self.events_container and hasattr(self.events_container, "events"):
            events_to_iterate = self.events_container.events
        elif self.events:
            events_to_iterate = self.events

        for event_data in events_to_iterate:
            if event_data.type != "THRESHOLD":
                continue

            can_fire_event = True  # 임시 (cooldown 로직은 poll에서 처리 가정 또는 EventEngine에서 상태 관리 필요)
            if not can_fire_event:
                continue

            if event_data.trigger and self._evaluate_pydantic_trigger(
                event_data.trigger, current_metrics
            ):
                threshold_events.append(event_data)
                alert_message = event_data.text_ko or f"임계값 이벤트 발생: {event_data.name_ko}"
                alert = Alert(
                    event_id=event_data.id,
                    message=alert_message,
                    metrics=current_metrics.copy(),  # 여기서 metrics는 MetricEnum을 키로 가짐
                    turn=self.current_turn,
                    severity="WARNING",
                )
                self.alert_queue.append(alert)
                self.metrics_tracker.add_event(
                    f"Triggered: {event_data.id} - {event_data.name_ko}"
                )  # 이벤트 발생 기록
        return threshold_events

    def apply_effects(self) -> Dict[MetricEnum, float]:
        """
        큐에 있는 모든 이벤트의 효과를 적용합니다.

        Returns:
            Dict[MetricEnum, float]: 효과가 적용된 최종 지표 상태
        """
        current_metrics = self.metrics_tracker.get_metrics()
        if not self.event_queue:
            return current_metrics

        while self.event_queue:
            event: PydanticEvent = self.event_queue.popleft()

            # Cooldown 및 last_fired 로직 (PydanticEvent의 필드 사용)
            can_fire_this_event = True
            if event.cooldown > 0:
                if event.last_fired is not None and (
                    self.current_turn - event.last_fired < event.cooldown
                ):
                    can_fire_this_event = False

            if can_fire_this_event:
                event.last_fired = self.current_turn

                updates: Dict[MetricEnum, float] = {}
                for effect_data in event.effects:
                    metric_name = effect_data.metric.upper()
                    metric_enum = getattr(MetricEnum, metric_name, None)
                    if metric_enum and metric_enum in current_metrics:
                        current_value = current_metrics[metric_enum]
                        new_value = current_value
                        try:
                            if "%" in effect_data.formula:
                                formula_val = effect_data.formula.replace("%", "")
                                percentage = float(formula_val) / 100
                                new_value = current_value * (1 + percentage)
                            else:
                                delta = float(effect_data.formula)
                                new_value = current_value + delta
                        except ValueError:
                            try:
                                temp_val = current_value
                                eval_result = eval(
                                    effect_data.formula, {"__builtins__": {}}, {"value": temp_val}
                                )
                                if "value" not in effect_data.formula:
                                    new_value = current_value + float(eval_result)
                                else:
                                    new_value = float(eval_result)
                            except Exception as e:
                                print(
                                    f"Error evaluating formula (PydanticEvent): {effect_data.formula}, Error: {e}"
                                )

                        updates[metric_enum] = new_value
                    else:
                        print(
                            f"[Effect Apply Debug] Metric not found or invalid: {effect_data.metric}"
                        )

                if updates:
                    self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event(f"Applied event: {event.id} - {event.name_ko}")
            else:
                self.metrics_tracker.add_event(
                    f"Event {event.id} in cooldown. Turn: {self.current_turn}, Last Fired: {event.last_fired}, Cooldown: {event.cooldown}"
                )

            current_metrics = self.metrics_tracker.get_metrics()
        return current_metrics

    def _process_cascade_effects(self, changed_metrics: Set[MetricEnum], depth: int) -> None:
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
        next_changed_metrics: Set[MetricEnum] = set()

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
                    target_metric_enum = getattr(MetricEnum, target_metric_name.upper(), None)
                    if target_metric_enum is None:
                        print(f"Unknown target metric: {target_metric_name}")
                        continue

                    # 현재 대상 지표 값 가져오기 (누적 적용을 위해)
                    target_current_value = current_metrics[target_metric_enum]

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
                    cascade_updates[target_metric_enum] = result
                    next_changed_metrics.add(target_metric_enum)

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

    def update(self) -> Dict[MetricEnum, float]:
        """
        이벤트 엔진을 한 턴 업데이트합니다.

        Returns:
            Dict[MetricEnum, float]: 업데이트 후 지표 상태
        """
        # 턴 증가
        self.current_turn += 1

        # 이벤트 폴링
        self.poll()

        # 임계값 트리거 평가
        self.evaluate_triggers()

        # 효과 적용
        return self.apply_effects()

    def get_alerts(self, count: Optional[int] = None) -> List[Alert]:
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
        edges: List[Tuple[str, str]] = []
        for source, targets in self.cascade_matrix.items():
            for edge in targets:
                try:
                    target_name = edge["target"]
                    target_enum = getattr(MetricEnum, target_name.upper(), None)
                    if target_enum is not None:
                        edges.append((source.name, target_enum.name))
                except (KeyError, AttributeError):
                    print(f"Invalid edge: {edge}")

        # 그래프 생성
        graph: Dict[str, List[str]] = defaultdict(list)
        for source_str, target_str in edges:
            graph[source_str].append(target_str)

        # 사이클 검사
        def is_cyclic(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            """DFS를 사용하여 사이클 검사"""
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if is_cyclic(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        # 모든 노드에 대해 사이클 검사
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        for node in graph:
            if node not in visited:
                if is_cyclic(node, visited, rec_stack):
                    return False

        return True

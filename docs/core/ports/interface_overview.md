# 인터페이스 개요

## 포트 인터페이스

Chicken-RNG의 포트 인터페이스는 핵심 도메인과 외부 시스템 간의 계약을 정의합니다.

### Primary (Driving) Ports

```python
class EventPort:
    """이벤트 처리를 위한 주 포트"""
    def process_event(self, event: Event) -> EventResult: ...
    def schedule_event(self, event: Event, trigger: Trigger) -> None: ...
    def cancel_event(self, event_id: str) -> bool: ...

class MetricsPort:
    """게임 지표 관리를 위한 주 포트"""
    def update_metric(self, metric: Metric, value: float) -> None: ...
    def get_metric(self, metric: Metric) -> float: ...
    def reset_metrics(self) -> None: ...

class GameStatePort:
    """게임 상태 관리를 위한 주 포트"""
    def save_state(self) -> GameState: ...
    def load_state(self, state: GameState) -> None: ...
    def reset_state(self) -> None: ...
```

### Secondary (Driven) Ports

```python
class EventStoragePort:
    """이벤트 저장소 포트"""
    def load_events(self) -> List[Event]: ...
    def save_event(self, event: Event) -> None: ...
    def delete_event(self, event_id: str) -> None: ...

class MetricsStoragePort:
    """지표 저장소 포트"""
    def persist_metrics(self, metrics: Dict[Metric, float]) -> None: ...
    def load_metrics(self) -> Dict[Metric, float]: ...

class NotificationPort:
    """알림 시스템 포트"""
    def notify_event(self, event: Event) -> None: ...
    def notify_metric_change(self, metric: Metric, value: float) -> None: ...
```

## 어댑터 구현

### Primary (Driving) Adapters

```python
class CLIAdapter:
    """명령줄 인터페이스 어댑터"""
    def __init__(self, event_port: EventPort, metrics_port: MetricsPort): ...
    def run_command(self, command: str) -> CommandResult: ...

class APIAdapter:
    """REST API 어댑터"""
    def __init__(self, event_port: EventPort, metrics_port: MetricsPort): ...
    def handle_request(self, request: Request) -> Response: ...
```

### Secondary (Driven) Adapters

```python
class JSONEventStorage:
    """JSON 파일 기반 이벤트 저장소"""
    def __init__(self, file_path: str): ...
    def load_events(self) -> List[Event]: ...
    def save_event(self, event: Event) -> None: ...

class SQLMetricsStorage:
    """SQL 데이터베이스 기반 지표 저장소"""
    def __init__(self, connection_string: str): ...
    def persist_metrics(self, metrics: Dict[Metric, float]) -> None: ...
    def load_metrics(self) -> Dict[Metric, float]: ...
```

## 데이터 전송 객체 (DTOs)

```python
@dataclass
class EventDTO:
    """이벤트 데이터 전송 객체"""
    id: str
    type: EventType
    name: str
    effects: List[Effect]
    trigger: Optional[Trigger] = None

@dataclass
class MetricDTO:
    """지표 데이터 전송 객체"""
    name: str
    value: float
    timestamp: datetime
    category: MetricCategory
```

## 인터페이스 사용 예시

### 이벤트 처리

```python
# Primary Port 사용
event_port = EventPort()
result = event_port.process_event(event)

# Secondary Port 사용
storage = EventStoragePort()
events = storage.load_events()
```

### 지표 관리

```python
# Primary Port 사용
metrics_port = MetricsPort()
metrics_port.update_metric(Metric.MONEY, 1000.0)

# Secondary Port 사용
storage = MetricsStoragePort()
storage.persist_metrics(current_metrics)
```

## 확장 포인트

### 커스텀 어댑터

```python
class CustomStorageAdapter(EventStoragePort):
    """사용자 정의 저장소 어댑터"""
    def load_events(self) -> List[Event]:
        # 커스텀 구현
        ...

class CustomNotificationAdapter(NotificationPort):
    """사용자 정의 알림 어댑터"""
    def notify_event(self, event: Event):
        # 커스텀 구현
        ...
```

### 플러그인 시스템

```python
class PluginPort:
    """플러그인 시스템 포트"""
    def register_plugin(self, plugin: Plugin) -> None: ...
    def get_plugin(self, name: str) -> Optional[Plugin]: ...
    def list_plugins(self) -> List[Plugin]: ...
```

## 테스트 지원

### Mock 어댑터

```python
class MockEventStorage(EventStoragePort):
    """테스트용 Mock 저장소"""
    def __init__(self):
        self.events: List[Event] = []

    def load_events(self) -> List[Event]:
        return self.events

class MockMetricsStorage(MetricsStoragePort):
    """테스트용 Mock 지표 저장소"""
    def __init__(self):
        self.metrics: Dict[Metric, float] = {}
```

### 테스트 유틸리티

```python
class InterfaceTestHelper:
    """인터페이스 테스트 지원 클래스"""
    @staticmethod
    def create_test_event() -> Event: ...
    
    @staticmethod
    def create_test_metrics() -> Dict[Metric, float]: ...
```

## 모범 사례

### 인터페이스 설계 원칙
1. 단일 책임 원칙 준수
2. 인터페이스 분리 원칙 적용
3. 의존성 역전 원칙 유지

### 구현 가이드라인
1. 명확한 계약 정의
2. 예외 처리 표준화
3. 버전 관리 고려

### 테스트 전략
1. 단위 테스트 필수
2. 통합 테스트 구현
3. 계약 테스트 작성 
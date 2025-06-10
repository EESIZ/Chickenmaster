# API 문서

## 핵심 API

### EventManager

이벤트 생성 및 관리를 위한 주요 API입니다.

```python
class EventManager:
    def create_event(self, event_data: Dict[str, Any]) -> Event:
        """새로운 이벤트를 생성합니다."""
        
    def process_event(self, event: Event) -> EventResult:
        """이벤트를 처리하고 결과를 반환합니다."""
        
    def schedule_event(self, event: Event, trigger: Trigger) -> None:
        """이벤트를 스케줄링합니다."""
```

### MetricsTracker

게임 지표 추적 및 관리를 위한 API입니다.

```python
class MetricsTracker:
    def update_metric(self, metric: Metric, value: float) -> None:
        """지표값을 업데이트합니다."""
        
    def get_metric(self, metric: Metric) -> float:
        """현재 지표값을 반환합니다."""
        
    def reset_metrics(self) -> None:
        """모든 지표를 초기화합니다."""
```

### GameState

게임 상태 관리를 위한 API입니다.

```python
class GameState:
    def save_state(self) -> Dict[str, Any]:
        """현재 게임 상태를 저장합니다."""
        
    def load_state(self, state: Dict[str, Any]) -> None:
        """저장된 게임 상태를 불러옵니다."""
        
    def reset_state(self) -> None:
        """게임 상태를 초기화합니다."""
```

## 이벤트 시스템

### Event

이벤트 데이터 구조입니다.

```python
@dataclass
class Event:
    id: str
    type: EventType
    name: str
    effects: List[Effect]
    trigger: Optional[Trigger] = None
```

### Effect

이벤트 효과 정의입니다.

```python
@dataclass
class Effect:
    metric: str
    formula: str
    conditions: List[Condition]
    probability: float
```

### Trigger

이벤트 트리거 조건입니다.

```python
@dataclass
class Trigger:
    type: TriggerType
    condition: str
    value: Any
```

## 메트릭 시스템

### Metric

게임 지표 정의입니다.

```python
class Metric(Enum):
    MONEY = "money"
    REPUTATION = "reputation"
    HAPPINESS = "happiness"
    STRESS = "stress"
```

### MetricModifier

지표 수정자입니다.

```python
@dataclass
class MetricModifier:
    metric: Metric
    operation: ModifierOperation
    value: float
    duration: Optional[int] = None
```

## 사용 예시

### 이벤트 생성 및 처리

```python
# 이벤트 매니저 초기화
event_manager = EventManager()

# 이벤트 생성
event_data = {
    "id": "customer_complaint",
    "type": EventType.RANDOM,
    "name": "고객 불만",
    "effects": [
        {
            "metric": "reputation",
            "formula": "-10",
            "probability": 1.0
        }
    ]
}
event = event_manager.create_event(event_data)

# 이벤트 처리
result = event_manager.process_event(event)
```

### 지표 관리

```python
# 지표 트래커 초기화
metrics = MetricsTracker()

# 지표 업데이트
metrics.update_metric(Metric.MONEY, 1000)
metrics.update_metric(Metric.REPUTATION, -5)

# 지표 확인
current_money = metrics.get_metric(Metric.MONEY)
current_reputation = metrics.get_metric(Metric.REPUTATION)
```

### 게임 상태 관리

```python
# 게임 상태 관리자 초기화
game_state = GameState()

# 상태 저장
current_state = game_state.save_state()

# 상태 복원
game_state.load_state(current_state)
```

## 오류 처리

### EventError

이벤트 관련 오류입니다.

```python
class EventError(Exception):
    """이벤트 처리 중 발생하는 오류의 기본 클래스"""
    pass

class EventValidationError(EventError):
    """이벤트 검증 실패 시 발생하는 오류"""
    pass

class EventProcessingError(EventError):
    """이벤트 처리 실패 시 발생하는 오류"""
    pass
```

### MetricError

지표 관련 오류입니다.

```python
class MetricError(Exception):
    """지표 처리 중 발생하는 오류의 기본 클래스"""
    pass

class InvalidMetricError(MetricError):
    """잘못된 지표 접근 시 발생하는 오류"""
    pass
```

## 확장

### 커스텀 이벤트 타입

```python
class CustomEventType(EventType):
    """사용자 정의 이벤트 타입"""
    SPECIAL = "SPECIAL"
    CHAIN = "CHAIN"
```

### 커스텀 효과

```python
@dataclass
class CustomEffect(Effect):
    """사용자 정의 효과"""
    special_condition: str
    chain_reaction: bool = False
```

## 모범 사례

### 이벤트 처리

```python
try:
    event = event_manager.create_event(event_data)
    result = event_manager.process_event(event)
except EventValidationError as e:
    logger.error(f"이벤트 검증 실패: {e}")
except EventProcessingError as e:
    logger.error(f"이벤트 처리 실패: {e}")
```

### 지표 업데이트

```python
try:
    metrics.update_metric(Metric.MONEY, value)
    metrics.update_metric(Metric.REPUTATION, value)
except InvalidMetricError as e:
    logger.error(f"지표 업데이트 실패: {e}")
```

## 성능 고려사항

### 캐싱

```python
@cached_property
def total_metrics(self) -> Dict[Metric, float]:
    """모든 지표의 현재 값을 계산합니다."""
    return {
        metric: self.get_metric(metric)
        for metric in Metric
    }
```

### 배치 처리

```python
def process_events_batch(self, events: List[Event]) -> List[EventResult]:
    """여러 이벤트를 한 번에 처리합니다."""
    return [
        self.process_event(event)
        for event in events
    ]
```

## 버전 관리

### API 버전

```python
API_VERSION = "1.0.0"
```

### 하위 호환성

```python
def get_metric(self, metric: Union[Metric, str]) -> float:
    """이전 버전과의 호환성을 위해 문자열도 허용"""
    if isinstance(metric, str):
        metric = Metric(metric)
    return self._get_metric_value(metric)
``` 
# 리팩토링 결정 사항

## 개요

이 문서는 Chicken-RNG 프로젝트의 주요 리팩토링 결정 사항을 기록합니다. 각 결정의 배경, 고려사항, 그리고 구현 방향을 설명합니다.

## 아키텍처 결정

### 1. 헥사고날 아키텍처 도입

**배경**
- 도메인 로직과 외부 시스템의 결합도가 높음
- 테스트 작성이 어려움
- 확장성 제한

**결정**
- 포트와 어댑터 패턴 적용
- 도메인 중심 설계 강화
- 인터페이스 기반 통신

**구현**
```python
# 포트 정의
class EventPort(Protocol):
    def process_event(self, event: Event) -> EventResult: ...
    def schedule_event(self, event: Event, trigger: Trigger) -> None: ...

# 어댑터 구현
class SQLEventStorage(EventPort):
    def process_event(self, event: Event) -> EventResult:
        # 구현
        pass
    
    def schedule_event(self, event: Event, trigger: Trigger) -> None:
        # 구현
        pass
```

### 2. 이벤트 시스템 재설계

**배경**
- 이벤트 처리 로직이 복잡함
- 연쇄 효과 추적이 어려움
- 성능 문제 발생

**결정**
- 이벤트 체인 매니저 도입
- 효과 계산기 분리
- 캐싱 시스템 구현

**구현**
```python
class EventChainManager:
    def __init__(self):
        self.effect_calculator = EffectCalculator()
        self.cache_manager = CacheManager()
    
    def process_chain(self, event: Event) -> List[Effect]:
        if cached := self.cache_manager.get_chain(event.id):
            return cached
        
        effects = self.calculate_chain_effects(event)
        self.cache_manager.store_chain(event.id, effects)
        return effects
```

## 코드 구조 결정

### 1. 모듈 재구성

**배경**
- 관련 기능이 여러 모듈에 분산됨
- 순환 참조 발생
- 모듈 간 의존성이 복잡함

**결정**
- 기능별 모듈 그룹화
- 공통 유틸리티 분리
- 의존성 방향 단순화

**구현**
```
src/
├── core/
│   ├── domain/
│   ├── events/
│   └── metrics/
├── adapters/
│   ├── storage/
│   └── api/
├── application/
│   ├── services/
│   └── handlers/
└── utils/
    ├── validation/
    └── logging/
```

### 2. 테스트 구조화

**배경**
- 테스트 코드 중복
- 테스트 실행 시간 증가
- 테스트 유지보수 어려움

**결정**
- 테스트 헬퍼 도입
- 테스트 픽스처 표준화
- 테스트 카테고리 정리

**구현**
```python
class TestHelper:
    @staticmethod
    def create_test_event():
        return Event(
            id=str(uuid.uuid4()),
            type=EventType.TEST,
            effects=[create_test_effect()]
        )

class TestBase(unittest.TestCase):
    def setUp(self):
        self.helper = TestHelper()
        self.event_manager = create_test_event_manager()
```

## 성능 최적화 결정

### 1. 캐싱 전략

**배경**
- 반복적인 계산 발생
- 데이터베이스 부하 증가
- 응답 시간 지연

**결정**
- 메모리 캐시 도입
- 캐시 무효화 정책 수립
- 캐시 크기 제한

**구현**
```python
class CacheManager:
    def __init__(self, max_size: int = 1000):
        self.cache = LRUCache(max_size)
    
    def get_or_compute(self, key: str, computer: Callable) -> Any:
        if cached := self.cache.get(key):
            return cached
        
        value = computer()
        self.cache.set(key, value)
        return value
```

### 2. 비동기 처리

**배경**
- 동기 작업으로 인한 블로킹
- 리소스 활용도 저하
- 확장성 제한

**결정**
- 비동기 이벤트 처리
- 작업 큐 도입
- 병렬 처리 구현

**구현**
```python
class AsyncEventProcessor:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.workers = []
    
    async def process_events(self):
        while True:
            event = await self.queue.get()
            await self.process_single_event(event)
            self.queue.task_done()
```

## 유지보수성 개선 결정

### 1. 로깅 시스템

**배경**
- 문제 추적이 어려움
- 로그 일관성 부족
- 모니터링 어려움

**결정**
- 구조화된 로깅 도입
- 로그 레벨 표준화
- 로그 집중화

**구현**
```python
class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event: Event, level: int = logging.INFO):
        self.logger.log(level, "Event processed", extra={
            "event_id": event.id,
            "event_type": event.type,
            "timestamp": datetime.now().isoformat()
        })
```

### 2. 오류 처리

**배경**
- 예외 처리 일관성 부족
- 오류 복구 어려움
- 사용자 피드백 부족

**결정**
- 예외 계층 구조화
- 오류 복구 전략 수립
- 사용자 친화적 오류 메시지

**구현**
```python
class GameError(Exception):
    """게임 관련 오류의 기본 클래스"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message)
        self.details = details or {}

class EventError(GameError):
    """이벤트 처리 관련 오류"""
    pass

class MetricError(GameError):
    """메트릭 처리 관련 오류"""
    pass
```

## 확장성 개선 결정

### 1. 플러그인 시스템

**배경**
- 기능 확장이 어려움
- 코드 수정 필요성 증가
- 사용자 정의 어려움

**결정**
- 플러그인 인터페이스 정의
- 동적 로딩 시스템 구현
- 설정 관리 체계화

**구현**
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin: Plugin):
        self.validate_plugin(plugin)
        self.plugins[plugin.name] = plugin
    
    def load_plugins(self, directory: str):
        for plugin_file in Path(directory).glob("*.py"):
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
```

### 2. 설정 시스템

**배경**
- 하드코딩된 설정 값
- 환경별 설정 관리 어려움
- 동적 설정 변경 불가

**결정**
- 설정 관리자 도입
- 환경별 설정 분리
- 동적 설정 지원

**구현**
```python
class ConfigManager:
    def __init__(self):
        self.config = {}
        self.observers = []
    
    def load_config(self, environment: str):
        config_file = f"config.{environment}.yaml"
        self.config = yaml.safe_load(Path(config_file).read_text())
        self.notify_observers()
    
    def update_config(self, key: str, value: Any):
        self.config[key] = value
        self.notify_observers()
``` 
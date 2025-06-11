# 설계 결정 사항

## 코드 구조 및 스타일

### 1. 동적 Import 경로 설정
**파일**: `scripts/mass_event_generation.py`

**결정사항**: 
- `sys.path`를 수정한 후에 `dev_tools` 모듈을 import하는 구조 유지
- Ruff의 E402(모듈 레벨 import가 파일 최상단에 없음) 경고 무시

**이유**:
- 스크립트가 프로젝트 루트 디렉토리의 위치를 동적으로 찾아 `dev_tools` 모듈을 import해야 함
- 이는 스크립트가 다양한 위치에서 실행될 수 있도록 하기 위한 의도적인 설계
- `sys.path.insert(0, str(project_root))` 이후에 import 문이 위치해야 정상적으로 동작

**처리방법**:
- `ruff.toml` 설정 파일에서 해당 파일의 E402 경고를 무시하도록 설정
- 이 설계 결정을 문서화하여 향후 유지보수 시 혼란 방지

### 관련 파일
- `scripts/mass_event_generation.py`: 동적 import 구현
- `ruff.toml`: 린터 설정
- `docs/DESIGN_DECISIONS.md`: 설계 결정 문서화

### 2. 매직 넘버 상수화 및 중앙 관리 (PLR2004)
**파일**: `game_constants.py` 및 전체 프로젝트

**결정사항**:
- 모든 매직 넘버(하드코딩된 숫자 값)를 `game_constants.py`에 중앙 관리되는 상수로 정의
- 관련 상수는 Frozen Dataclass 패턴을 사용하여 그룹화
- 테스트 코드의 매직 넘버도 상수화하여 일관성 유지

**이유**:
- 하드코딩된 매직 넘버는 코드 가독성과 유지보수성을 저해함
- 동일한 값이 여러 곳에서 사용될 때 일관성 문제 발생 가능
- 값 변경 시 모든 위치를 찾아 수정해야 하는 번거로움과 오류 가능성
- 숫자의 의미를 명확히 하여 코드 이해도 향상
- 게임의 핵심 철학인 '불확실성'과 '트레이드오프'를 코드 구조에도 반영

**구현 방식**:
```python
# game_constants.py

# 단일 상수 정의
FLOAT_EPSILON = 0.001
SCORE_THRESHOLD_HIGH = 0.7
SCORE_THRESHOLD_MEDIUM = 0.5

# Frozen Dataclass 패턴으로 관련 상수 그룹화
from dataclasses import dataclass

@dataclass(frozen=True)
class ProbabilityConstants:
    """확률 관련 상수를 그룹화한 Frozen Dataclass"""
    RANDOM_THRESHOLD: float = 0.5
    EVENT_CHANCE_HIGH: float = 0.7
    EVENT_CHANCE_MEDIUM: float = 0.5
    EVENT_CHANCE_LOW: float = 0.3

@dataclass(frozen=True)
class TestConstants:
    """테스트 관련 상수를 그룹화한 Frozen Dataclass"""
    MIN_CASCADE_EVENTS: int = 3
    EXPECTED_EVENTS: int = 2
    METRICS_HISTORY_LENGTH: int = 5
    POSSIBLE_OUTCOME: int = 3
```

**기대 효과**:
- 코드 가독성 향상: 의미 있는 상수명으로 코드 이해도 증가
- 유지보수성 개선: 값 변경 시 한 곳만 수정하면 전체 적용
- 버그 감소: 하드코딩된 매직 넘버 제거로 오류 가능성 감소
- 일관성 유지: 동일한 값이 여러 곳에서 사용될 때 일관성 보장
- 코드 품질 향상: Ruff PLR2004 린트 경고 해소

**관련 파일**:
- `game_constants.py`: 중앙 상수 정의
- `src/metrics/modifiers.py`: 상수 사용 예시
- `src/events/engine.py`: 상수 사용 예시
- `tests/test_events.py`: 테스트 코드 상수 사용 예시
- `tests/test_placeholder.py`: 테스트 코드 상수 사용 예시

**참고 사항**:
- 이 설계 결정은 [리팩토링 가이드라인](REFACTORING_GUIDELINES.md)의 매직 넘버 처리 원칙과 연계됨
- 모든 개발자는 새로운 코드 작성 시 매직 넘버 대신 상수를 사용해야 함

## 결정 3: StorytellerService 매직 넘버 상수화 (2025-01-06)

### 배경
StorytellerService 구현 과정에서 다수의 매직 넘버가 발견되어 코드 가독성과 유지보수성이 저하되었습니다.

### 결정 내용
모든 매직 넘버를 `game_constants.py`에 의미 있는 상수로 정의하였습니다:

```python
# 스토리텔러 관련 상수
MIN_METRICS_HISTORY_FOR_TREND: Final[int] = 2
RECENT_HISTORY_WINDOW: Final[int] = 3
SITUATION_POSITIVE_THRESHOLD: Final[float] = 0.6
SITUATION_NEGATIVE_THRESHOLD: Final[float] = 0.4
MONEY_LOW_THRESHOLD: Final[int] = 3000
MONEY_HIGH_THRESHOLD: Final[int] = 15000
REPUTATION_LOW_THRESHOLD: Final[int] = 30
REPUTATION_HIGH_THRESHOLD: Final[int] = 70
HAPPINESS_LOW_THRESHOLD: Final[int] = 30
HAPPINESS_HIGH_THRESHOLD: Final[int] = 70
TRADEOFF_BALANCE_THRESHOLD: Final[float] = 0.5
GAME_PROGRESSION_MID_POINT: Final[float] = 0.5
PATTERN_SCORE_TOLERANCE: Final[float] = 0.1
COMPLEXITY_BONUS_MULTIPLIER: Final[float] = 0.1
```

### 영향
- 코드 가독성 향상
- Ruff 린터 PLR2004 규칙 준수
- 유지보수성 개선
- 일관된 임계값 관리

## 결정 4: 전략 패턴 구현 및 의존성 주입 (2025-01-06)

### 배경
Cascade 및 Storyteller 모듈에서 전략 패턴이 정의되어 있었으나 실제로 사용되지 않고, 서비스에서 직접 if-else로 로직을 구현하는 문제가 발견되었습니다. 

**문제점:**
- 정의된 전략 인터페이스가 실제로 사용되지 않음
- Import 경로 오류로 전략 구현체들이 제대로 동작하지 않음
- 서비스 클래스에서 직접 구현한 로직으로 인한 단일 책임 원칙 위배

### 결정 내용
헥사고널 아키텍처의 의존성 역전 원칙에 따라 전략 패턴을 완전히 구현하였습니다:

#### 1. Cascade 전략 패턴 구현
- **전략 팩토리**: `CascadeStrategyFactory` 구현으로 전략 의존성 주입 지원
- **Import 경로 수정**: 모든 cascade 전략의 잘못된 import 경로를 올바르게 수정
- **서비스 통합**: `CascadeServiceImpl`에서 직접 if-else 로직 대신 전략 패턴 사용

```python
# 기존: 직접 구현
def process_cascade_chain(self, ...):
    # if cascade_type == "ECONOMIC":
    #     # 직접 처리 로직
    pass

# 개선: 전략 패턴
def process_cascade_chain(self, ...):
    strategy = self._strategy_factory.get_strategy(node.cascade_type)
    if strategy.process(node):
        # 전략에 위임
        pass
```

#### 2. Storyteller 전략 패턴 구현
- **전략 팩토리**: `StorytellerStrategyFactory` 및 `StorytellerStrategyBundle` 구현
- **서비스 메서드 위임**: 기존 직접 구현 메서드들을 전략으로 위임

```python
# 기존: 직접 구현
def _analyze_situation_tone(self, metrics):
    # 복잡한 점수 계산 로직 직접 구현
    pass

# 개선: 전략 위임
def _analyze_situation_tone(self, metrics):
    return self._state_evaluator.evaluate(metrics)
```

#### 3. 의존성 주입 시스템
- **생성자 주입**: 서비스 생성 시 전략 팩토리나 번들을 주입받을 수 있음
- **기본값 지원**: 주입되지 않은 경우 전역 팩토리 인스턴스 사용
- **확장성**: 새로운 전략 구현체를 쉽게 등록하고 교체 가능

```python
class CascadeServiceImpl(ICascadeService):
    def __init__(self, event_service: IEventService, strategy_factory: CascadeStrategyFactory | None = None):
        self._strategy_factory = strategy_factory or get_cascade_strategy_factory()
```

#### 4. 전략 카테고리 자동 매핑
이벤트 카테고리에 따라 적절한 전략을 자동으로 선택하는 기능 구현:

```python
def get_strategy_by_event_category(self, event_category: str) -> ICascadeStrategy:
    category_mappings = {
        "economy": "ECONOMIC",
        "social": "SOCIAL",
        "cultural": "CULTURAL",
        "tech": "TECHNOLOGICAL",
        "environment": "ENVIRONMENTAL",
    }
```

### 기술적 구현
1. **팩토리 패턴**: 전략 인스턴스 생성 및 관리
2. **싱글톤**: 전역 팩토리 인스턴스로 메모리 효율성 확보
3. **Protocol 기반**: Python의 구조적 타입 시스템 활용
4. **타입 안전성**: 완전한 타입 힌트 지원

### 테스트 검증
전략 패턴 구현의 정확성을 검증하는 테스트 스크립트 작성:
- 팩토리 인스턴스 생성 테스트
- 전략 선택 및 획득 테스트
- 의존성 주입 동작 확인
- **결과**: 100% 테스트 통과 ✅

### 영향 및 이점
- **아키텍처 일관성**: 정의된 인터페이스가 실제로 사용됨
- **확장성**: 새로운 전략 추가가 용이함
- **테스트 가능성**: 전략 Mock을 통한 단위 테스트 개선
- **의존성 역전**: 고수준 모듈이 저수준 구현에 의존하지 않음
- **단일 책임**: 각 전략이 특정 도메인 로직에만 집중
- **유지보수성**: 전략별로 독립적인 수정 가능

### 관련 파일
- `src/cascade/domain/strategies/strategy_factory.py`: Cascade 전략 팩토리
- `src/storyteller/domain/strategy_factory.py`: Storyteller 전략 팩토리  
- `src/cascade/adapters/cascade_service.py`: 전략 패턴 적용된 서비스
- `src/storyteller/adapters/storyteller_service.py`: 전략 패턴 적용된 서비스
- `test_strategy_patterns.py`: 전략 패턴 구현 검증 테스트

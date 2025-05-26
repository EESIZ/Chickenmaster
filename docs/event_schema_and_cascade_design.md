# 이벤트 엔진 및 연쇄 효과 시스템 설계 문서

## 개요

이 문서는 Chicken-RNG 게임의 이벤트 엔진 및 연쇄 효과 시스템의 설계와 구현에 대해 설명합니다. 이벤트 엔진은 게임 내 다양한 이벤트를 관리하고, 연쇄 효과 시스템은 지표 간의 상호 의존성을 처리합니다.

## 핵심 철학

Chicken-RNG 게임의 핵심 철학은 다음과 같습니다:

1. **정답 없음(noRightAnswer)**: 모든 이벤트와 선택은 득과 실을 동시에 가져옵니다. 완벽한 선택은 존재하지 않으며, 모든 결정은 트레이드오프를 수반합니다.

2. **트레이드오프(tradeoff)**: 한 지표를 개선하면 다른 지표는 악화됩니다. 이는 게임 내 모든 시스템에 적용되는 기본 원칙입니다.

3. **불확실성(uncertainty)**: 이벤트 발생과 효과는 예측 불가능한 요소에 영향을 받습니다. 이는 게임에 도전 요소와 재미를 더합니다.

## 이벤트 스키마

### 이벤트 타입

이벤트는 다음 네 가지 카테고리로 분류됩니다:

1. **RANDOM**: 확률 기반으로 무작위 발생하는 이벤트
2. **THRESHOLD**: 특정 지표가 임계값에 도달하면 발생하는 이벤트
3. **SCHEDULED**: 일정 주기로 발생하는 이벤트
4. **CASCADE**: 다른 이벤트의 결과로 발생하는 이벤트

### 데이터 구조

이벤트는 다음과 같은 속성을 가집니다:

```python
@dataclass
class Event:
    id: str                           # 고유 식별자
    type: EventCategory               # 이벤트 카테고리
    effects: List[Effect]             # 효과 목록
    priority: int = 0                 # 우선순위 (높을수록 먼저 처리)
    cooldown: int = 0                 # 재발생 대기 시간
    probability: Optional[float] = None  # 발생 확률 (RANDOM 타입)
    trigger: Optional[Trigger] = None    # 트리거 조건 (THRESHOLD 타입)
    schedule: Optional[int] = None       # 발생 주기 (SCHEDULED 타입)
    message: Optional[str] = None        # 이벤트 메시지
    tags: List[str] = field(default_factory=list)  # 태그 목록
    cascade_depth: int = 0            # 연쇄 깊이 (CASCADE 타입)
    last_fired: int = -1              # 마지막 발생 턴
```

트리거와 효과는 다음과 같이 정의됩니다:

```python
@dataclass
class Trigger:
    metric: Metric                    # 대상 지표
    condition: TriggerCondition       # 조건 (LESS_THAN, GREATER_THAN, EQUAL)
    value: float                      # 임계값

@dataclass
class Effect:
    metric: Metric                    # 대상 지표
    formula: str                      # 적용 수식
    message: Optional[str] = None     # 효과 메시지
```

### 파일 형식

이벤트는 TOML 또는 JSON 형식으로 정의할 수 있습니다. 예시:

```toml
[[events]]
id = "food_poisoning"
type = "RANDOM"
priority = 10
probability = 0.05
cooldown = 5
message = "식중독 발생! 평판이 하락하고 자금이 감소합니다."

[[events.effects]]
metric = "REPUTATION"
formula = "-15"
message = "식중독으로 인한 평판 하락"

[[events.effects]]
metric = "MONEY"
formula = "-1000"
message = "식중독 보상금 지급"
```

## 연쇄 효과 시스템

### 설계 원칙

연쇄 효과 시스템은 다음 원칙에 따라 설계되었습니다:

1. **DAG(Directed Acyclic Graph) 구조**: 순환 참조를 방지하기 위해 연쇄 효과는 DAG 구조를 가져야 합니다.
2. **최대 연쇄 깊이**: 무한 루프를 방지하기 위해 최대 연쇄 깊이(기본값: 10)를 설정합니다.
3. **누적 적용**: 연쇄 효과는 항상 현재 값에 누적적으로 적용됩니다.

### 트레이드오프 매트릭스

트레이드오프 매트릭스는 지표 간의 연쇄 관계를 정의합니다. 예시:

```toml
[cascade]
# 평판 → 자금
REPUTATION = [
    { target = "MONEY", formula = "-500", message = "평판 하락으로 인한 매출 감소" }
]

# 자금 → 시설
MONEY = [
    { target = "FACILITY", formula = "-10", message = "자금 부족으로 인한 시설 관리 소홀" }
]

# 시설 → 직원 피로도
FACILITY = [
    { target = "STAFF_FATIGUE", formula = "value + 10", message = "시설 악화로 인한 직원 피로도 증가" }
]
```

### 연쇄 효과 처리 알고리즘

연쇄 효과는 다음 단계로 처리됩니다:

1. 이벤트 효과 적용 후 변경된 지표 식별
2. 각 변경된 지표에 대해 연쇄 효과 매트릭스 참조
3. 연쇄 효과 수식 평가 및 적용
4. 다음 단계 연쇄 효과 처리 (최대 깊이까지)

## 구현 세부사항

### 이벤트 엔진 파이프라인

이벤트 엔진은 다음 파이프라인으로 동작합니다:

1. **poll()**: 현재 턴에 발생 가능한 이벤트 폴링
2. **evaluate_triggers()**: 임계값 기반 트리거 평가
3. **apply_effects()**: 이벤트 효과 적용 및 연쇄 효과 처리

### 효과 적용 방식

효과 적용은 다음과 같이 처리됩니다:

1. **백분율 표기법**: "-5%"와 같은 백분율 표기는 현재 값에 대한 상대적 변화량으로 처리
2. **절대값 변화**: "-500"과 같은 숫자는 현재 값에 더하는 변화량으로 처리
3. **수식 평가**: "value * 0.9"와 같은 수식은 현재 값(value)을 기준으로 평가

### DAG 검증

연쇄 효과 그래프가 DAG인지 확인하기 위해 Kahn의 위상 정렬 알고리즘을 사용합니다. 이는 순환 참조를 방지하고 안정적인 연쇄 효과 처리를 보장합니다.

### 불확실성 관리

불확실성은 다음과 같이 관리됩니다:

1. **난수 시드**: 재현 가능한 결과를 위해 난수 생성기에 시드를 설정할 수 있습니다.
2. **변동 계수**: 지표별로 불확실성 가중치를 설정하여 예측 불가능성을 조절합니다.

## 통합 및 확장

### MetricsTracker 통합

이벤트 엔진은 MetricsTracker와 통합되어 지표 변화를 관리합니다:

```python
class GameEventSystem:
    def __init__(
        self,
        metrics_tracker: Optional[MetricsTracker] = None,
        events_file: Optional[str] = "data/events.toml",
        tradeoff_file: Optional[str] = "data/tradeoff_matrix.toml",
        seed: Optional[int] = None,
    ):
        # 지표 추적기 초기화
        self.metrics_tracker = metrics_tracker or MetricsTracker()
        
        # 이벤트 엔진 초기화
        self.event_engine = EventEngine(
            metrics_tracker=self.metrics_tracker,
            events_file=events_file if os.path.exists(events_file) else None,
            tradeoff_file=tradeoff_file if os.path.exists(tradeoff_file) else None,
            seed=seed,
        )
```

### 시나리오 시뮬레이션

다양한 시나리오를 시뮬레이션하여 게임 밸런스를 테스트할 수 있습니다:

```python
def noRightAnswer_simulate_scenario(
    self, scenario: Dict[str, Any], days: int = 10
) -> Dict[str, Any]:
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
```

## 성능 및 테스트

### 성능 요구사항

- 1,000회 이벤트 시뮬레이션: 3초 이내, 메모리 사용량 256MB 이하

### 테스트 커버리지

- 코드 커버리지: 80% 이상 (현재 81%)
- 테스트 케이스: 12개 (모두 통과)

## 결론

이벤트 엔진 및 연쇄 효과 시스템은 Chicken-RNG 게임의 핵심 철학인 '정답 없음', '트레이드오프', '불확실성'을 구현하는 중요한 구성 요소입니다. 이 시스템을 통해 게임은 예측 불가능하면서도 일관된 경험을 제공하며, 플레이어에게 의미 있는 선택과 결과를 제시합니다.

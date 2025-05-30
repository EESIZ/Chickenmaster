# 연쇄 이벤트 시스템 (Cascade Module)

## 개요

연쇄 이벤트 시스템(Cascade Module)은 Chickmaster 게임에서 하나의 이벤트가 발생했을 때 연쇄적으로 다른 이벤트들이 발생하는 메커니즘을 구현합니다. 이 시스템은 헥사고날 아키텍처 원칙에 따라 설계되었으며, 도메인 객체의 불변성(immutability)을 보장합니다.

## 아키텍처

연쇄 이벤트 시스템은 다음과 같은 계층 구조로 설계되었습니다:

```
src/cascade/
├── domain/           # 도메인 레이어 (비즈니스 엔티티)
│   ├── __init__.py
│   └── models.py     # 도메인 모델 (CascadeChain, CascadeNode 등)
├── ports/            # 포트 레이어 (인터페이스)
│   ├── __init__.py
│   ├── cascade_port.py  # 연쇄 이벤트 서비스 인터페이스
│   └── event_port.py    # 이벤트 서비스 인터페이스
└── adapters/         # 어댑터 레이어 (구현체)
    ├── __init__.py
    ├── cascade_service.py  # 연쇄 이벤트 서비스 구현체
    └── event_adapter.py    # 이벤트 서비스 어댑터
```

### 도메인 모델

연쇄 이벤트 시스템의 핵심 도메인 모델은 다음과 같습니다:

1. **CascadeType**: 연쇄 이벤트 유형을 정의하는 열거형
   - `IMMEDIATE`: 즉시 발생하는 연쇄 이벤트
   - `DELAYED`: 지연 후 발생하는 연쇄 이벤트
   - `CONDITIONAL`: 조건부 발생하는 연쇄 이벤트
   - `PROBABILISTIC`: 확률적으로 발생하는 연쇄 이벤트

2. **TriggerCondition**: 이벤트 트리거 조건을 표현하는 불변 객체
   - `expression`: 조건식 (예: "metrics.money > threshold")
   - `parameters`: 조건식에 사용되는 파라미터 맵

3. **PendingEvent**: 지연 처리될 이벤트 정보를 표현하는 불변 객체
   - `event_id`: 이벤트 ID
   - `delay_turns`: 지연 턴 수
   - `trigger_turn`: 실제 트리거될 턴
   - `cascade_type`: 연쇄 유형
   - `probability`: 발생 확률 (0.0~1.0)

4. **CascadeNode**: 연쇄 체인 내의 개별 노드를 표현하는 불변 객체
   - `event_id`: 이벤트 ID
   - `depth`: 연쇄 깊이 (루트는 0)
   - `cascade_type`: 연쇄 유형
   - `parent_id`: 부모 이벤트 ID (없으면 None)
   - `node_id`: 노드 고유 ID
   - `trigger_condition`: 트리거 조건
   - `probability`: 발생 확률 (0.0~1.0)
   - `delay_turns`: 지연 턴 수

5. **CascadeChain**: 연쇄 이벤트 체인을 표현하는 불변 객체
   - `root_event_id`: 최초 트리거 이벤트 ID
   - `nodes`: 연쇄 노드들의 집합
   - `max_depth`: 최대 연쇄 깊이
   - `chain_id`: 체인 고유 ID
   - `created_at`: 생성 시간

6. **CascadeResult**: 연쇄 이벤트 처리 결과를 표현하는 불변 객체
   - `triggered_events`: 트리거된 이벤트 ID 목록
   - `pending_events`: 지연된 이벤트 정보
   - `metrics_impact`: 지표 영향도
   - `depth_reached`: 도달한 최대 깊이
   - `result_id`: 결과 고유 ID
   - `created_at`: 생성 시간

### 포트 인터페이스

연쇄 이벤트 시스템은 다음과 같은 포트 인터페이스를 정의합니다:

1. **ICascadeService**: 연쇄 이벤트 처리 인터페이스
   - `get_cascade_events`: 트리거 이벤트로 인한 연쇄 이벤트 목록 반환
   - `calculate_cascade_depth`: 연쇄 효과 깊이 계산
   - `validate_cascade_limits`: 연쇄 깊이 제한 검증
   - `process_cascade_chain`: 전체 연쇄 체인 처리
   - `check_cascade_cycle`: 연쇄 효과 사이클 검사
   - `get_pending_events`: 현재 턴에 처리할 지연 이벤트 목록 반환
   - `register_cascade_relation`: 두 이벤트 간의 연쇄 관계 등록
   - `build_cascade_chain`: 루트 이벤트로부터 연쇄 체인 구성
   - `calculate_metrics_impact`: 트리거된 이벤트들의 지표 영향도 계산

2. **IEventService**: 이벤트 서비스 인터페이스 (외부 의존성)
   - `get_event_by_id`: ID로 이벤트 조회
   - `apply_event_effects`: 이벤트 효과 적용
   - `evaluate_trigger_condition`: 트리거 조건 평가
   - `get_applicable_events`: 현재 상태에서 발생 가능한 이벤트 목록 반환
   - `check_event_cooldown`: 이벤트 쿨다운 상태 확인
   - `evaluate_event_probability`: 이벤트 발생 확률 계산

### 어댑터 구현

연쇄 이벤트 시스템은 다음과 같은 어댑터 구현체를 제공합니다:

1. **CascadeServiceImpl**: ICascadeService 인터페이스 구현체
   - 연쇄 이벤트 처리 로직 구현
   - 의존성 주입을 통한 IEventService 활용
   - BFS 기반 연쇄 관계 탐색 및 처리

2. **EventServiceAdapter**: IEventService 인터페이스 구현체
   - 실제 이벤트 서비스와의 통합 담당
   - 이벤트 조회, 효과 적용, 조건 평가 등 구현

## 사용 방법

### 연쇄 관계 등록

```python
# CascadeServiceImpl 인스턴스 생성
event_service = EventServiceAdapter()
cascade_service = CascadeServiceImpl(event_service)

# 즉시 발생 연쇄 관계 등록
cascade_service.register_cascade_relation(
    parent_event_id="root_event",
    child_event_id="child_event",
    cascade_type_str="IMMEDIATE"
)

# 조건부 연쇄 관계 등록
cascade_service.register_cascade_relation(
    parent_event_id="root_event",
    child_event_id="conditional_event",
    cascade_type_str="CONDITIONAL",
    trigger_condition={
        "expression": "metrics.money > 1000",
        "parameters": {"threshold": 1000}
    }
)

# 확률적 연쇄 관계 등록
cascade_service.register_cascade_relation(
    parent_event_id="root_event",
    child_event_id="probabilistic_event",
    cascade_type_str="PROBABILISTIC",
    probability=0.5
)

# 지연 연쇄 관계 등록
cascade_service.register_cascade_relation(
    parent_event_id="root_event",
    child_event_id="delayed_event",
    cascade_type_str="DELAYED",
    delay_turns=2
)
```

### 연쇄 체인 처리

```python
# 게임 상태 (구현에 따라 다를 수 있음)
game_state = GameState(
    metrics={"money": 1000, "reputation": 50, "happiness": 75},
    turn=1
)

# 루트 이벤트 객체
root_event = event_service.get_event_by_id("root_event")

# 연쇄 체인 처리
result = cascade_service.process_cascade_chain(
    root_event=root_event,
    game_state=game_state,
    current_turn=1
)

# 처리 결과 활용
print(f"트리거된 이벤트: {result.triggered_events}")
print(f"지연된 이벤트: {result.pending_events}")
print(f"지표 영향도: {result.metrics_impact}")
print(f"도달한 최대 깊이: {result.depth_reached}")
```

### 지연 이벤트 처리

```python
# 현재 턴에 처리할 지연 이벤트 목록 조회
current_turn = 3
pending_events = cascade_service.get_pending_events(current_turn)

# 지연 이벤트 처리
for pending_event in pending_events:
    event = event_service.get_event_by_id(pending_event.event_id)
    game_state = event_service.apply_event_effects(event, game_state)
```

## 테스트 결과

연쇄 이벤트 시스템은 다음과 같은 테스트를 통과했습니다:

### 도메인 객체 테스트

- **TriggerCondition**: 기본 생성, 파라미터 포함 생성, 불변성, 누락된 파라미터 검증
- **PendingEvent**: 기본 생성, 유효하지 않은 지연 턴, 유효하지 않은 확률 검증
- **CascadeNode**: 루트 노드 생성, 자식 노드 생성, 지연/조건부/확률적 노드 생성, 유효성 검증
- **CascadeChain**: 단순 체인 생성, 노드 없는 체인, 유효하지 않은 최대 깊이, 루트 노드 누락 검증, 노드 조회, 사이클 검사
- **CascadeResult**: 기본 생성, 유효하지 않은 깊이, 총 이벤트 수 계산, 총 지표 영향도 계산, 지연 이벤트 여부 확인

### 어댑터 테스트

- **CascadeServiceImpl**: 연쇄 관계 등록, 조건부/확률적/지연 관계 등록, 연쇄 체인 구성, 연쇄 이벤트 목록 조회, 연쇄 체인 처리, 지연 이벤트 조회, 사이클 검사, 지표 영향도 계산

## 독립성 검증

연쇄 이벤트 시스템은 기존 Chickmaster 코드베이스와 완전히 독립적으로 설계되었습니다:

1. **도메인 객체 독립성**: 모든 도메인 객체는 외부 의존성 없이 독립적으로 구현되었습니다.
2. **포트 인터페이스 독립성**: 포트 인터페이스는 구체적인 구현에 의존하지 않고 추상화되었습니다.
3. **어댑터 구현 독립성**: 어댑터 구현체는 의존성 주입을 통해 외부 서비스와 결합하며, 필요시 Mock 구현으로 대체 가능합니다.
4. **테스트 독립성**: 모든 테스트는 외부 의존성 없이 독립적으로 실행 가능합니다.

## 트레이드오프 및 불확실성

연쇄 이벤트 시스템 설계 및 구현 과정에서 다음과 같은 트레이드오프와 불확실성이 고려되었습니다:

1. **noRightAnswer_연쇄깊이제한**: 연쇄 깊이 제한은 게임 밸런스와 성능 사이의 트레이드오프입니다. 현재는 기본값 5로 설정되어 있지만, 게임 플레이 테스트를 통해 조정이 필요할 수 있습니다.

2. **tradeoff_지연이벤트처리**: 지연 이벤트 처리는 메모리 사용과 처리 복잡성 사이의 트레이드오프입니다. 현재는 메모리에 저장하는 방식을 사용하지만, 영구 저장소를 활용하는 방식으로 확장 가능합니다.

3. **uncertainty_확률계산**: 확률적 이벤트의 발생 확률 계산은 게임 상태에 따라 동적으로 조정될 수 있습니다. 현재는 고정 확률을 사용하지만, 향후 게임 상태에 따른 동적 확률 계산으로 확장 가능합니다.

## 향후 개선 방향

연쇄 이벤트 시스템은 다음과 같은 방향으로 개선될 수 있습니다:

1. **이벤트 템플릿**: 자주 사용되는 연쇄 패턴을 템플릿화하여 재사용성을 높입니다.
2. **시각화 도구**: 연쇄 체인을 시각적으로 표현하는 도구를 개발하여 디버깅 및 설계를 용이하게 합니다.
3. **성능 최적화**: 대규모 연쇄 체인 처리 시 성능을 최적화합니다.
4. **영구 저장소 통합**: 지연 이벤트를 영구 저장소에 저장하여 게임 재시작 시에도 유지되도록 합니다.
5. **이벤트 로깅 및 분석**: 연쇄 이벤트 처리 과정을 로깅하고 분석하는 기능을 추가합니다.

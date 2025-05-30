# 🔧 API 사용법 가이드

Chicken-RNG 프로젝트의 모든 모듈과 함수 사용법을 상세히 설명합니다.

## 📋 목차

1. [게임 상수와 타입](#1-게임-상수와-타입)
2. [핵심 도메인](#2-핵심-도메인)
3. [지표 시스템](#3-지표-시스템)
4. [이벤트 시스템](#4-이벤트-시스템)
5. [경제 시스템](#5-경제-시스템)
6. [개발 도구](#6-개발-도구)

---

## 1. 게임 상수와 타입

### `game_constants.py` - 게임 핵심 상수

게임의 모든 지표, 타입, 상수를 중앙에서 관리합니다.

#### 핵심 열거형

```python
from game_constants import Metric, ActionType, EventType

# 게임 지표
metric = Metric.MONEY
print(metric)  # Metric.MONEY

# 플레이어 행동
action = ActionType.PRICE_CHANGE
print(action)  # ActionType.PRICE_CHANGE
```

#### 지표 범위와 트레이드오프

```python
from game_constants import METRIC_RANGES, TRADEOFF_RELATIONSHIPS

# 지표 범위 확인
min_val, max_val, initial = METRIC_RANGES[Metric.MONEY]
print(f"돈: {min_val}~{max_val}, 초기값: {initial}")

# 트레이드오프 관계 확인
affected_metrics = TRADEOFF_RELATIONSHIPS[Metric.MONEY]
print(f"돈이 증가하면 감소하는 지표들: {affected_metrics}")
```

#### 유틸리티 함수

```python
from game_constants import cap_metric_value, are_happiness_suffering_balanced

# 지표 값 보정
safe_value = cap_metric_value(Metric.MONEY, -1000)
print(safe_value)  # 0 (음수 방지)

# 행복-고통 균형 확인
is_balanced = are_happiness_suffering_balanced(60, 40)
print(is_balanced)  # True (합이 100)
```

---

## 🏛️ Core Domain API

### GameState

게임의 핵심 상태를 나타내는 불변 객체입니다.

```python
from src.core.domain.game_state import GameState

# 게임 상태 생성
state = GameState(
    money=1000,
    reputation=50,
    happiness=60,
    pain=40,
    day=1,
    events_history=()
)
```

#### 주요 메서드

| 메서드 | 반환 타입 | 설명 |
|--------|-----------|------|
| `apply_effects(effects: Dict[str, int])` | `GameState` | 효과를 적용한 새 상태 반환 |
| `add_event_to_history(event_id: str)` | `GameState` | 이벤트 추가된 새 상태 반환 |

#### 사용 예제

```python
# 효과 적용 (돈 +100, 평판 -10)
effects = {'money': 100, 'reputation': -10}
new_state = state.apply_effects(effects)

# 이벤트 히스토리 추가
state_with_event = state.add_event_to_history("chicken_fire_001")

# 상태 값 확인
print(f"돈: {state.money}, 평판: {state.reputation}")
```

### Metric

개별 지표를 나타내는 불변 객체입니다.

```python
from src.core.domain.metrics import Metric

# 지표 생성
money_metric = Metric(
    name="money",
    value=1000,
    min_value=0,
    max_value=999999
)
```

#### 주요 메서드

| 메서드 | 반환 타입 | 설명 |
|--------|-----------|------|
| `is_valid()` | `bool` | 지표값이 유효 범위인지 확인 |
| `with_new_value(new_value: int)` | `Metric` | 새 값으로 지표 객체 생성 |
| `apply_delta(delta: int)` | `Metric` | 변화량 적용한 새 지표 생성 |

---

## 💰 Economy API

### EconomyEngine

경제 시스템의 핵심 엔진입니다.

```python
from src.economy.engine import compute_profit_no_right_answer

# 수익 계산
profit = compute_profit_no_right_answer(
    units_sold=100,      # 판매량
    unit_cost=5.0,       # 단위 원가
    price=10.0,          # 판매가
    fixed_cost=200.0     # 고정비
)
# 결과: 500.0 (수익)
```

#### 트레이드오프 계산

```python
from src.economy.engine import apply_tradeoff

# 가격 인상 시 평판과 피로도 트레이드오프
price_increase = 20
effects = apply_tradeoff("PRICE_TO_REPUTATION", price_increase)
# {'reputation': -6, 'staff_fatigue': 4}
```

#### 주요 함수

| 함수 | 매개변수 | 반환 타입 | 설명 |
|------|----------|-----------|------|
| `compute_profit_no_right_answer()` | units_sold, unit_cost, price, fixed_cost | `float` | 수익 계산 |
| `apply_economic_effects()` | game_state, action | `GameState` | 경제 효과 적용 |

---

## 🎲 Events API

### EventEngine

이벤트 시스템의 핵심 엔진입니다.

```python
from src.events.engine import EventEngine
from src.metrics.tracker import MetricsTracker

# 이벤트 엔진 초기화
metrics_tracker = MetricsTracker()
event_engine = EventEngine(
    metrics_tracker=metrics_tracker,
    events_file="data/events.json",
    seed=12345,
    max_cascade_depth=10
)
```

#### 주요 메서드

| 메서드 | 매개변수 | 반환 타입 | 설명 |
|--------|----------|-----------|------|
| `trigger_random_event()` | game_state | `Optional[Event]` | 랜덤 이벤트 발생 |
| `apply_event_effects()` | event, choice_id | `Dict[str, int]` | 이벤트 효과 계산 |
| `process_cascade_effects()` | initial_effects | `Dict[str, int]` | 연쇄 효과 처리 |

#### 사용 예제

```python
# 랜덤 이벤트 발생
current_state = GameState(money=1000, reputation=50, happiness=60, pain=40, day=5)
event = event_engine.trigger_random_event(current_state)

if event:
    print(f"이벤트 발생: {event.name_ko}")
    
    # 첫 번째 선택지 선택
    effects = event_engine.apply_event_effects(event, 0)
    
    # 상태에 효과 적용
    new_state = current_state.apply_effects(effects)
```

### Event

개별 이벤트를 나타내는 모델입니다.

```python
from src.events.models import Event, EventChoice, EventEffect

# 이벤트 효과 정의
effect = EventEffect(
    metric="money",
    min_value=-500,
    max_value=-100,
    formula="random.randint(min_value, max_value)"
)

# 선택지 정의
choice = EventChoice(
    text_ko="화재 보험을 구매한다",
    text_en="Buy fire insurance",
    effects=[effect]
)
```

---

## 📊 Metrics API

### MetricsTracker

게임 지표를 추적하고 관리하는 클래스입니다.

```python
from src.metrics.tracker import MetricsTracker
from game_constants import Metric

# 메트릭 추적기 초기화
tracker = MetricsTracker()

# 초기 지표 설정
tracker.set_metric(Metric.MONEY, 1000)
tracker.set_metric(Metric.REPUTATION, 50)

# 지표 변경
tracker.update_metric(Metric.MONEY, 100)  # +100
tracker.update_metric(Metric.REPUTATION, -5)  # -5

# 현재 값 조회
current_money = tracker.get_metric_value(Metric.MONEY)
current_reputation = tracker.get_metric_value(Metric.REPUTATION)
```

#### 주요 메서드

| 메서드 | 매개변수 | 반환 타입 | 설명 |
|--------|----------|-----------|------|
| `set_metric()` | metric, value | `None` | 지표 값 설정 |
| `update_metric()` | metric, delta | `None` | 지표 값 변경 |
| `get_metric_value()` | metric | `int` | 현재 지표 값 조회 |
| `get_all_metrics()` | - | `Dict[Metric, int]` | 모든 지표 값 조회 |

---

## 🎮 사용 예제

### 완전한 게임 턴 시뮬레이션

```python
from src.core.domain.game_state import GameState
from src.events.engine import EventEngine
from src.economy.engine import compute_profit_no_right_answer
from src.metrics.tracker import MetricsTracker

def simulate_game_turn():
    # 1. 초기 상태 설정
    state = GameState(
        money=1000,
        reputation=50,
        happiness=60,
        pain=40,
        day=1
    )
    
    # 2. 메트릭 추적기 및 이벤트 엔진 초기화
    metrics_tracker = MetricsTracker()
    event_engine = EventEngine(metrics_tracker)
    
    # 3. 경제 활동 (치킨 판매)
    daily_profit = compute_profit_no_right_answer(
        units_sold=50,
        unit_cost=3.0,
        price=8.0,
        fixed_cost=100.0
    )
    
    # 4. 경제 효과 적용
    economic_effects = {'money': int(daily_profit)}
    state = state.apply_effects(economic_effects)
    
    # 5. 랜덤 이벤트 발생
    event = event_engine.trigger_random_event(state)
    if event:
        # 첫 번째 선택지 자동 선택
        event_effects = event_engine.apply_event_effects(event, 0)
        state = state.apply_effects(event_effects)
        state = state.add_event_to_history(event.id)
    
    # 6. 하루 진행
    state = state.apply_effects({'day': 1})
    
    return state

# 게임 실행
final_state = simulate_game_turn()
print(f"최종 상태: 돈={final_state.money}, 평판={final_state.reputation}")
```

### 커스텀 이벤트 생성

```python
from src.events.models import Event, EventChoice, EventEffect

def create_custom_event():
    # 효과 정의
    positive_effect = EventEffect(
        metric="money",
        min_value=100,
        max_value=500,
        formula="random.randint(min_value, max_value)"
    )
    
    negative_effect = EventEffect(
        metric="reputation",
        min_value=-20,
        max_value=-5,
        formula="random.randint(min_value, max_value)"
    )
    
    # 선택지 정의
    choice = EventChoice(
        text_ko="치킨을 기부한다",
        text_en="Donate chicken",
        effects=[positive_effect, negative_effect]
    )
    
    # 이벤트 생성
    event = Event(
        id="charity_event_001",
        type="CHOICE",
        category="social",
        name_ko="자선 행사",
        name_en="Charity Event",
        text_ko="동네에서 자선 행사를 위해 치킨 기부를 요청합니다.",
        text_en="The neighborhood requests chicken donation for charity.",
        choices=[choice],
        probability=0.3,
        cooldown=7
    )
    
    return event
```

### 배치 테스트 실행

```python
def run_batch_simulation(turns: int = 30):
    """여러 턴의 게임을 시뮬레이션합니다."""
    state = GameState(money=1000, reputation=50, happiness=60, pain=40, day=1)
    results = []
    
    for turn in range(turns):
        state = simulate_game_turn()
        results.append({
            'day': state.day,
            'money': state.money,
            'reputation': state.reputation,
            'happiness': state.happiness,
            'pain': state.pain
        })
    
    return results

# 30일 시뮬레이션 실행
simulation_results = run_batch_simulation(30)
```

---

## 🔍 디버깅 도구

### 로깅 설정

```python
import logging

# 게임 이벤트 로깅 활성화
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chicken_rng")

# 이벤트 발생 시 로그 출력
def log_event(event, choice_id, effects):
    logger.info(f"이벤트: {event.name_ko}")
    logger.info(f"선택: {choice_id}")
    logger.info(f"효과: {effects}")
```

### 상태 검증

```python
def validate_game_state(state: GameState) -> bool:
    """게임 상태가 유효한지 검증합니다."""
    checks = [
        state.money >= 0,
        0 <= state.reputation <= 100,
        0 <= state.happiness <= 100,
        0 <= state.pain <= 100,
        state.day >= 1
    ]
    
    return all(checks)

# 사용법
if not validate_game_state(current_state):
    raise ValueError("Invalid game state detected")
```

---

## 📚 추가 자료

- [게임 규칙](rules.md) - 게임 메커니즘 상세 설명
- [아키텍처 명세](architecture_specification.md) - 기술적 구조
- [개발자 가이드](DEVELOPER_GUIDE.md) - 개발 환경 설정
- [기여 가이드](CONTRIBUTING.md) - 코드 기여 방법 
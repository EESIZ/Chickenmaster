# 치킨마스터 도메인

## 개요

치킨마스터는 치킨집 운영 시뮬레이션 게임입니다. 플레이어는 치킨집 사장이 되어 가게를 운영하고 성장시켜 나갑니다.

## 핵심 개념

### 1. 치킨집 (Restaurant)

```python
@dataclass
class Restaurant:
    id: str
    name: str
    level: int
    reputation: float
    money: float
    menu_items: List[MenuItem]
    staff: List[Staff]
    facilities: List[Facility]
```

### 2. 메뉴 (Menu)

```python
@dataclass
class MenuItem:
    id: str
    name: str
    price: float
    cost: float
    cooking_time: int
    popularity: float
    ingredients: List[Ingredient]
```

### 3. 직원 (Staff)

```python
@dataclass
class Staff:
    id: str
    name: str
    role: StaffRole
    skill_level: int
    salary: float
    happiness: float
    fatigue: float
```

### 4. 시설 (Facility)

```python
@dataclass
class Facility:
    id: str
    type: FacilityType
    level: int
    condition: float
    efficiency: float
    maintenance_cost: float
```

## 게임 메커니즘

### 1. 경제 시스템

- 수입: 메뉴 판매, 이벤트 보상
- 지출: 재료비, 인건비, 시설 유지비
- 대출 및 투자

### 2. 평판 시스템

- 고객 만족도
- 음식 품질
- 서비스 품질
- 가게 청결도

### 3. 이벤트 시스템

- 랜덤 이벤트
- 시즌 이벤트
- 특별 이벤트
- 위기 상황

### 4. 성장 시스템

- 가게 레벨업
- 직원 교육
- 시설 개선
- 메뉴 개발

## 게임 규칙

### 1. 기본 규칙

```python
class GameRules:
    MAX_STAFF = 10
    MAX_MENU_ITEMS = 20
    MAX_FACILITIES = 15
    
    INITIAL_MONEY = 10000
    INITIAL_REPUTATION = 50.0
    
    BANKRUPTCY_THRESHOLD = -50000
```

### 2. 밸런스 규칙

```python
class BalanceRules:
    PROFIT_MARGIN_MIN = 0.2
    PROFIT_MARGIN_MAX = 0.8
    
    SALARY_MIN = 2000
    SALARY_MAX = 10000
    
    REPUTATION_DECAY = 0.1
    FACILITY_DECAY = 0.05
```

### 3. 레벨업 조건

```python
class LevelUpConditions:
    def check_restaurant_level_up(self, restaurant: Restaurant) -> bool:
        return (
            restaurant.money >= self.money_threshold and
            restaurant.reputation >= self.reputation_threshold and
            len(restaurant.menu_items) >= self.menu_items_threshold
        )
```

## 게임 상태

### 1. 기본 상태

```python
@dataclass
class GameState:
    restaurant: Restaurant
    current_day: int
    total_sales: float
    total_expenses: float
    customer_satisfaction: float
```

### 2. 통계

```python
@dataclass
class Statistics:
    daily_sales: List[float]
    customer_counts: List[int]
    popular_items: Dict[str, int]
    staff_performance: Dict[str, float]
```

## 이벤트 정의

### 1. 고객 이벤트

```python
@dataclass
class CustomerEvent:
    type: CustomerEventType
    count: int
    preferences: List[str]
    budget: float
    satisfaction_threshold: float
```

### 2. 직원 이벤트

```python
@dataclass
class StaffEvent:
    type: StaffEventType
    staff_id: str
    impact: float
    duration: int
```

### 3. 시설 이벤트

```python
@dataclass
class FacilityEvent:
    type: FacilityEventType
    facility_id: str
    damage: float
    repair_cost: float
```

## 게임 로직

### 1. 일일 시뮬레이션

```python
class DaySimulation:
    def simulate_day(self, game_state: GameState) -> DayResult:
        """하루 동안의 게임 진행을 시뮬레이션합니다."""
        morning_prep = self.morning_preparation()
        business_hours = self.business_hours()
        closing = self.closing_tasks()
        return DayResult(morning_prep, business_hours, closing)
```

### 2. 고객 처리

```python
class CustomerHandler:
    def process_customer(self, customer: Customer) -> OrderResult:
        """고객 주문을 처리하고 결과를 반환합니다."""
        order = self.take_order(customer)
        food = self.prepare_food(order)
        satisfaction = self.serve_customer(customer, food)
        return OrderResult(order, satisfaction)
```

### 3. 재고 관리

```python
class InventoryManager:
    def update_inventory(self, orders: List[Order]) -> None:
        """주문에 따라 재고를 업데이트합니다."""
        
    def check_low_stock(self) -> List[Ingredient]:
        """부족한 재고를 확인합니다."""
        
    def place_orders(self, ingredients: List[Ingredient]) -> None:
        """재료를 주문합니다."""
```

## 확장성

### 1. 프랜차이즈 시스템

```python
@dataclass
class Franchise:
    main_restaurant: Restaurant
    branches: List[Restaurant]
    brand_value: float
    franchise_fee: float
```

### 2. 이벤트 시스템 확장

```python
class EventSystem:
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """새로운 이벤트 핸들러를 등록합니다."""
        
    def trigger_event(self, event: Event) -> EventResult:
        """이벤트를 발생시키고 결과를 반환합니다."""
```

### 3. 모드 시스템

```python
class ModSystem:
    def load_mod(self, mod_path: str) -> None:
        """모드를 로드합니다."""
        
    def apply_mod(self, mod: Mod) -> None:
        """모드를 적용합니다."""
```

## 테스트 시나리오

### 1. 기본 시나리오

```python
def test_basic_gameplay():
    """기본적인 게임플레이를 테스트합니다."""
    game = Game()
    restaurant = game.create_restaurant("테스트 치킨")
    
    # 하루 운영
    result = game.simulate_day(restaurant)
    assert result.profit > 0
    assert result.customer_satisfaction > 0.5
```

### 2. 스트레스 테스트

```python
def test_stress_conditions():
    """극한 상황에서의 게임 동작을 테스트합니다."""
    game = Game()
    restaurant = game.create_restaurant("스트레스 테스트")
    
    # 많은 고객 주문
    result = game.simulate_rush_hour(restaurant, customer_count=100)
    assert restaurant.staff_fatigue < 100
    assert restaurant.facility_condition > 0
```

### 3. 장기 시뮬레이션

```python
def test_long_term_simulation():
    """장기 운영 시뮬레이션을 테스트합니다."""
    game = Game()
    restaurant = game.create_restaurant("장기 테스트")
    
    # 30일 운영
    results = game.simulate_days(restaurant, days=30)
    assert restaurant.money > Game.INITIAL_MONEY
    assert restaurant.level > 1
``` 
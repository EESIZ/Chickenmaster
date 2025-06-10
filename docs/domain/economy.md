# 경제 시스템

## 개요

치킨마스터의 경제 시스템은 게임의 핵심 메커니즘입니다. 이 시스템은 플레이어의 재정 관리, 수익성, 그리고 게임의 전반적인 경제 흐름을 관리합니다.

## 핵심 구성 요소

### 1. 수입 시스템

```python
class IncomeSystem:
    def calculate_daily_income(self, sales: List[Sale]) -> float:
        """일일 수입을 계산합니다."""
        return sum(sale.amount for sale in sales)
    
    def calculate_event_rewards(self, events: List[Event]) -> float:
        """이벤트 보상을 계산합니다."""
        return sum(event.reward for event in events)
```

### 2. 지출 시스템

```python
class ExpenseSystem:
    def calculate_daily_expenses(self, restaurant: Restaurant) -> float:
        """일일 지출을 계산합니다."""
        return (
            self.calculate_ingredient_costs(restaurant) +
            self.calculate_staff_salaries(restaurant) +
            self.calculate_facility_maintenance(restaurant)
        )
```

### 3. 대출 시스템

```python
class LoanSystem:
    def process_loan_application(self, 
                               restaurant: Restaurant, 
                               amount: float) -> LoanResult:
        """대출 신청을 처리합니다."""
        credit_score = self.calculate_credit_score(restaurant)
        interest_rate = self.determine_interest_rate(credit_score)
        return self.create_loan(amount, interest_rate)
```

## 경제 규칙

### 1. 가격 정책

```python
class PricingPolicy:
    MIN_MARKUP = 1.2  # 최소 마진
    MAX_MARKUP = 3.0  # 최대 마진
    
    def validate_price(self, cost: float, price: float) -> bool:
        """가격의 유효성을 검증합니다."""
        markup = price / cost
        return self.MIN_MARKUP <= markup <= self.MAX_MARKUP
```

### 2. 급여 체계

```python
class SalarySystem:
    BASE_SALARY = 2000
    SKILL_MULTIPLIER = 0.1
    
    def calculate_salary(self, staff: Staff) -> float:
        """직원의 급여를 계산합니다."""
        return self.BASE_SALARY * (1 + staff.skill_level * self.SKILL_MULTIPLIER)
```

### 3. 유지비 시스템

```python
class MaintenanceSystem:
    def calculate_facility_cost(self, facility: Facility) -> float:
        """시설 유지비를 계산합니다."""
        return facility.base_cost * (1 + facility.level * 0.1)
```

## 경제 지표

### 1. 수익성 지표

```python
@dataclass
class ProfitabilityMetrics:
    gross_profit_margin: float
    net_profit_margin: float
    operating_margin: float
    return_on_investment: float
```

### 2. 효율성 지표

```python
@dataclass
class EfficiencyMetrics:
    inventory_turnover: float
    employee_productivity: float
    facility_utilization: float
```

## 밸런싱 시스템

### 1. 동적 가격 조정

```python
class DynamicPricing:
    def adjust_prices(self, 
                     menu_items: List[MenuItem], 
                     market_data: MarketData) -> List[MenuItem]:
        """시장 상황에 따라 가격을 조정합니다."""
        for item in menu_items:
            demand = self.calculate_demand(item, market_data)
            item.price = self.optimize_price(item.cost, demand)
        return menu_items
```

### 2. 경제 균형

```python
class EconomicBalance:
    def balance_economy(self, game_state: GameState) -> None:
        """전체 경제 시스템의 균형을 조정합니다."""
        self.adjust_inflation()
        self.balance_supply_demand()
        self.regulate_money_supply()
```

## 이벤트 영향

### 1. 경제 이벤트

```python
class EconomicEvent:
    def apply_economic_event(self, 
                           event: Event, 
                           game_state: GameState) -> None:
        """경제 이벤트의 영향을 적용합니다."""
        if event.type == EventType.ECONOMIC:
            self.apply_market_changes(event.effects)
            self.update_prices(event.price_changes)
            self.adjust_demand(event.demand_changes)
```

### 2. 위기 관리

```python
class CrisisManagement:
    def handle_economic_crisis(self, 
                             crisis: Crisis, 
                             game_state: GameState) -> None:
        """경제 위기 상황을 관리합니다."""
        self.apply_emergency_measures()
        self.adjust_economic_parameters()
        self.provide_recovery_options()
```

## 모니터링 및 분석

### 1. 경제 모니터링

```python
class EconomicMonitor:
    def monitor_economic_health(self, game_state: GameState) -> Report:
        """경제 상태를 모니터링하고 보고서를 생성합니다."""
        metrics = self.collect_economic_metrics()
        analysis = self.analyze_trends(metrics)
        return self.generate_report(analysis)
```

### 2. 예측 시스템

```python
class EconomicPredictor:
    def predict_economic_trends(self, 
                              historical_data: List[EconomicData]) -> Prediction:
        """경제 트렌드를 예측합니다."""
        model = self.train_prediction_model(historical_data)
        return model.predict_next_period()
```

## 확장성

### 1. 새로운 수입원

```python
class IncomeExpansion:
    def add_income_source(self, 
                         source: IncomeSource, 
                         game_state: GameState) -> None:
        """새로운 수입원을 추가합니다."""
        self.validate_income_source(source)
        self.integrate_income_source(source)
        self.balance_economic_impact(source)
```

### 2. 경제 모드

```python
class EconomicMode:
    def apply_economic_mode(self, 
                          mode: GameMode, 
                          game_state: GameState) -> None:
        """특정 경제 모드를 적용합니다."""
        self.adjust_economic_parameters(mode.parameters)
        self.update_game_rules(mode.rules)
        self.rebalance_economy(mode.balance_settings)
``` 
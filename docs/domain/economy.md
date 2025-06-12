# 경제 시스템

## 개요

치킨마스터의 경제 시스템은 게임의 핵심 메커니즘입니다. 이 시스템은 플레이어의 재정 관리, 수익성, 그리고 게임의 전반적인 경제 흐름을 관리합니다.

## 실제 치킨집 운영 데이터 기반 경제 모델

### 1. 2025년 기준 창업 비용 및 운영비

실제 치킨집 운영 데이터를 바탕으로 한 경제 모델:

```python
# 2025년 기준 창업비용 (2018년 5800만원 → 물가상승률 반영)
STARTUP_COST_2025 = 68_153_774  # KRW

# 치킨 1마리당 재료비 (2022년 기준 → 2025년 물가상승률 반영)
CHICKEN_RAW_COST = 4_237      # 9-10호 닭 1마리
COOKING_OIL_COST = 1_444      # 식용유 0.3L
TOTAL_INGREDIENT_COST = 5_681 # 총 재료비

# 월 고정비
MONTHLY_RENT = 3_000_000      # 임대료
MONTHLY_UTILITIES = 1_000_000 # 전기가스료
DAILY_FIXED_COST = 133_333    # 일 고정비

# 업계 평균 순이익률
TARGET_PROFIT_RATE = 0.0981   # 9.81%
```

### 2. 매출 예측 모델

시장 조사 데이터를 기반으로 한 매출 예측:

```python
# 상권 분석 (대구시 사례 기준)
HOUSEHOLDS_PER_STORE = 404    # 1차 상권 점포당 가구수
CHICKEN_ORDER_RATE = 0.23     # 가구당 치킨 주문 비율
MONTHLY_ORDERS = 93           # 월 예상 주문량

# 판매량 시나리오
DAILY_SALES_OPENING = 50      # 오픈 첫 주 (잘되는 집 기준)
DAILY_SALES_NORMAL = 25       # 오픈빨 지난 후 평균

# 가격 전략
CHICKEN_PRICE_DEFAULT = 15_000   # 기본 치킨 가격
CHICKEN_PRICE_BALANCED = 18_500  # 목표 순이익률 달성 가격
```

### 3. 비용 구조 분석

```python
@dataclass
class ChickenBusinessCosts:
    """치킨집 비용 구조"""
    
    # 변동비 (판매량에 비례)
    raw_chicken: float = 4_237        # 닭 원가
    cooking_oil: float = 1_444        # 식용유
    packaging: float = 500            # 포장재
    delivery_fee: float = 3_000       # 배달 플랫폼 수수료
    
    # 고정비 (월 기준)
    rent: float = 3_000_000          # 임대료
    utilities: float = 1_000_000     # 전기가스료
    labor: float = 2_500_000         # 인건비
    marketing: float = 200_000       # 마케팅
    
    def calculate_daily_variable_cost(self, sales_volume: int) -> float:
        """일 변동비 계산"""
        cost_per_unit = self.raw_chicken + self.cooking_oil + self.packaging + self.delivery_fee
        return cost_per_unit * sales_volume
    
    def calculate_daily_fixed_cost(self) -> float:
        """일 고정비 계산"""
        monthly_fixed = self.rent + self.utilities + self.labor + self.marketing
        return monthly_fixed / 30
```

### 4. 수익성 분석 모델

```python
class ProfitabilityAnalyzer:
    """수익성 분석기"""
    
    def analyze_scenario(self, 
                        daily_sales: int, 
                        chicken_price: float,
                        costs: ChickenBusinessCosts) -> Dict[str, float]:
        """시나리오별 수익성 분석"""
        
        daily_revenue = daily_sales * chicken_price
        daily_variable_cost = costs.calculate_daily_variable_cost(daily_sales)
        daily_fixed_cost = costs.calculate_daily_fixed_cost()
        daily_total_cost = daily_variable_cost + daily_fixed_cost
        daily_profit = daily_revenue - daily_total_cost
        profit_rate = daily_profit / daily_revenue if daily_revenue > 0 else 0
        
        return {
            'daily_revenue': daily_revenue,
            'daily_variable_cost': daily_variable_cost,
            'daily_fixed_cost': daily_fixed_cost,
            'daily_total_cost': daily_total_cost,
            'daily_profit': daily_profit,
            'profit_rate': profit_rate
        }
    
    def find_breakeven_price(self, 
                           daily_sales: int, 
                           costs: ChickenBusinessCosts,
                           target_profit_rate: float = 0.0981) -> float:
        """목표 순이익률 달성을 위한 가격 계산"""
        
        daily_variable_cost = costs.calculate_daily_variable_cost(daily_sales)
        daily_fixed_cost = costs.calculate_daily_fixed_cost()
        daily_total_cost = daily_variable_cost + daily_fixed_cost
        
        # 목표 순이익률을 달성하기 위한 매출액
        required_revenue = daily_total_cost / (1 - target_profit_rate)
        required_price = required_revenue / daily_sales
        
        return required_price
```

### 5. 엑셀 기반 데이터 관리

게임 데이터는 엑셀 파일에서 관리되며, 다음 시트들로 구성됩니다:

- **Chicken_Economics**: 기본 경제 데이터 (창업비용, 재료비, 목표 수익률 등)
- **Sales_Projections**: 매출 예측 시나리오 (오픈 첫 주, 일반 운영 등)
- **Market_Research**: 시장 조사 데이터 (상권 분석, 주문 비율 등)
- **Cost_Structure**: 비용 구조 (변동비, 고정비, 연간 비용 등)

```python
# ExcelGameDataProvider 확장
class ExcelGameDataProvider:
    def get_chicken_economics(self) -> Dict[str, Any]:
        """치킨집 경제 데이터 로드"""
        
    def get_sales_projections(self) -> Dict[str, Dict[str, Any]]:
        """매출 예측 데이터 로드"""
        
    def get_market_research(self) -> Dict[str, Any]:
        """시장 조사 데이터 로드"""
        
    def get_cost_structure(self) -> Dict[str, Dict[str, Any]]:
        """비용 구조 데이터 로드"""
```

### 6. 게임 밸런싱 고려사항

실제 데이터 기반 밸런싱에서 발견된 이슈:

1. **높은 순이익률**: 현재 설정(25개/일, 15,000원)에서 26.6% 순이익률
2. **목표 달성 가격**: 9.81% 순이익률 달성을 위해서는 12,212원 필요
3. **밸런싱 방향**: 
   - 재료비 상승 또는 
   - 고정비 증가 또는
   - 판매량 감소 시나리오 추가

```python
# 밸런싱 검증 로직
def validate_game_balance(projections: Dict, target_rate: float) -> bool:
    """게임 밸런싱 검증"""
    normal_operation = projections['normal_operation']
    current_rate = normal_operation['profit_rate']
    
    # 5% 오차 허용
    return abs(current_rate - target_rate) < 0.05
```

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
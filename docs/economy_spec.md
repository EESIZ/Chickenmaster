# 경제 엔진 명세서

## 개요

이 문서는 Chicken-RNG 게임의 경제 엔진 시스템에 대한 상세 명세를 제공합니다. 경제 엔진은 게임의 핵심 메커니즘으로, 가격 설정, 수요 계산, 이익 계산, 그리고 다양한 지표 간의 트레이드오프 관계를 관리합니다.

## 핵심 철학 반영

경제 엔진은 게임의 세 가지 핵심 철학을 충실히 반영합니다:

1. **정답 없음**: 모든 경제적 결정은 득과 실을 동시에 가져옵니다. 가격을 낮추면 손님은 늘지만 이익률은 감소하고 직원 피로도는 증가합니다.

2. **트레이드오프**: 한 지표를 개선하면 다른 지표는 악화됩니다. 평판이 상승하면 직원 피로도도 함께 상승하는 등의 관계가 존재합니다.

3. **불확실성**: 경제 상황은 예측 불가능하게 변화할 수 있습니다. 완벽한 전략이나 완전한 대비는 불가능합니다.

## 수요 계산 수식

수요 계산은 다음 요소들을 고려합니다:

```
demand = base_demand * price_effect * reputation_effect * uncertainty_multiplier
```

여기서:
- `base_demand`: 기본 수요량 (설정 파일에서 정의)
- `price_effect`: 가격에 따른 효과 (최적 가격에서 멀어질수록 감소)
- `reputation_effect`: 평판에 따른 효과 (평판이 높을수록 증가)
- `uncertainty_multiplier`: 불확실성 요소 (무작위 변동성)

### 가격 효과 계산

```
price_effect = 1.0 - (price_sensitivity * abs(price - optimal_price) / (max_price - min_price))
```

가격이 최적 가격(optimal_price)에서 멀어질수록 수요는 감소합니다.

### 평판 효과 계산

```
reputation_effect = 1.0 + (normalized_reputation * reputation_factor)
```

평판이 높을수록 수요는 증가합니다.

## 이익 계산 수식

이익 계산은 다음과 같이 이루어집니다:

```
profit = total_revenue - total_cost
total_revenue = units_sold * price
total_cost = (units_sold * unit_cost) + fixed_cost
```

## 트레이드오프 관계

경제 엔진에서 구현된 주요 트레이드오프 관계:

1. **가격-평판 트레이드오프**:
   - 가격 인하 → 평판 증가 → 직원 피로도 증가
   - 가격 인상 → 평판 감소 → 직원 피로도 감소

2. **재고-현금 트레이드오프**:
   - 재고 증가 → 현금 감소
   - 재고 감소 → 현금 증가 (판매 시)

3. **행복-고통 시소**:
   - 행복 + 고통 = 100 (항상 유지)
   - 한쪽이 증가하면 다른 쪽은 반드시 감소

## JSON 입출력 예시

### 입력 예시 (플레이어 결정)

```json
{
  "action_type": "PRICE_CHANGE",
  "price_change": -2000,
  "day": 5
}
```

### 출력 예시 (경제 상태 업데이트)

```json
{
  "metrics": {
    "MONEY": 12500,
    "REPUTATION": 65,
    "HAPPINESS": 55,
    "SUFFERING": 45,
    "INVENTORY": 80,
    "STAFF_FATIGUE": 40,
    "FACILITY": 75
  },
  "economy": {
    "current_price": 8000,
    "units_sold": 65,
    "daily_profit": 5000,
    "total_cash": 45000
  }
}
```

## 설정 파라미터

경제 엔진의 모든 파라미터는 `data/economy_config.json` 파일에서 관리됩니다. 이를 통해 게임 밸런싱을 쉽게 조정할 수 있습니다.

주요 설정 섹션:
- `demand`: 수요 계산 관련 파라미터
- `profit`: 이익 계산 관련 파라미터
- `tradeoffs`: 트레이드오프 관계 강도 파라미터
- `uncertainty`: 불확실성 요소 관련 파라미터

## 음수 방지 메커니즘

경제 엔진은 "불확실성 ≠ 불합리한 음수" 원칙에 따라 물리적으로 불가능한 음수 값을 방지합니다:

1. 재고가 음수가 되지 않도록 보정
2. 현금이 음수가 되지 않도록 보정 (파산 조건 별도 처리)

이는 schema.py의 `cap_metric_value` 함수를 통해 구현됩니다.

## 모듈 구조

경제 엔진은 다음 모듈로 구성됩니다:

1. `src/economy/models.py`: 기본 경제 모델 함수 (수요 계산 등)
2. `src/economy/engine.py`: 경제 시스템 핵심 로직 (이익 계산, 트레이드오프 적용 등)
3. `src/metrics/tracker.py`: 게임 지표 추적 및 관리

## 향후 확장 계획

1. 계절적 요인에 따른 수요 변동
2. 경쟁자 행동에 따른 시장 영향
3. 경제 위기/호황 이벤트 시스템

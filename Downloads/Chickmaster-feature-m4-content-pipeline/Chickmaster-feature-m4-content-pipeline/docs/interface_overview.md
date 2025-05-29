# 모듈 간 인터페이스 개요

이 문서는 Chicken-RNG 게임의 모듈 간 인터페이스와 데이터 구조를 정의합니다. 모든 모듈은 이 문서에 정의된 입출력 형식과 지표 범위를 준수해야 합니다.

## 지표 정의 (Enum & Range)

모든 모듈은 `schema.py`에 정의된 상수와 Enum을 사용해야 합니다.

| 지표 | Enum 이름 | 범위 | 초기값 | 설명 |
|------|-----------|------|--------|------|
| 자금 | `Metric.MONEY` | 0-∞ | 10000 | 음수 불가, 0 이하 시 파산 위험 |
| 평판 | `Metric.REPUTATION` | 0-100 | 50 | 손님 수와 직결 |
| 행복 | `Metric.HAPPINESS` | 0-100 | 50 | 고통과 합이 항상 100 |
| 고통 | `Metric.SUFFERING` | 0-100 | 50 | 행복과 합이 항상 100 |
| 재고 | `Metric.INVENTORY` | 0-∞ | 100 | 음수 불가, 부족 시 판매 불가 |
| 직원 피로 | `Metric.STAFF_FATIGUE` | 0-100 | 30 | 높을수록 서비스 품질 저하 |
| 시설 상태 | `Metric.FACILITY` | 0-100 | 80 | 낮을수록 사고 위험 증가 |

## 모듈 간 입출력 JSON 예시

### M-1: 코어 경제 모듈

**입력 예시:**
```json
{
  "action": {
    "type": "PRICE_CHANGE",
    "value": -500,
    "description": "가격 인하 프로모션"
  },
  "current_state": {
    "money": 15000,
    "reputation": 65,
    "inventory": 80,
    "staff_fatigue": 45
  }
}
```

**출력 예시:**
```json
{
  "new_state": {
    "money": 14200,
    "reputation": 70,
    "inventory": 65,
    "staff_fatigue": 55
  },
  "tradeoff_effects": [
    {"metric": "MONEY", "change": -800, "reason": "가격 인하로 인한 수익 감소"},
    {"metric": "REPUTATION", "change": 5, "reason": "저렴한 가격으로 인한 고객 만족도 증가"},
    {"metric": "INVENTORY", "change": -15, "reason": "손님 증가로 인한 재고 소진"},
    {"metric": "STAFF_FATIGUE", "change": 10, "reason": "손님 증가로 인한 업무량 증가"}
  ]
}
```

### M-3: 랜덤 이벤트 엔진

**입력 예시:**
```json
{
  "day": 12,
  "current_state": {
    "money": 18500,
    "reputation": 72,
    "happiness": 60,
    "suffering": 40,
    "inventory": 55,
    "staff_fatigue": 65,
    "facility": 75
  },
  "uncertainty_factor": 0.7
}
```

**출력 예시:**
```json
{
  "event": {
    "id": "FOOD_POISONING",
    "severity": 0.65,
    "description": "일부 손님이 식중독 증상을 호소했습니다."
  },
  "immediate_effects": [
    {"metric": "REPUTATION", "change": -15, "reason": "식중독 사건으로 인한 평판 하락"},
    {"metric": "MONEY", "change": -3000, "reason": "환불 및 보상 비용"}
  ],
  "aftershock_queue": [
    {
      "day": 13,
      "effect": {"metric": "REPUTATION", "change": -5, "reason": "식중독 뉴스 확산"}
    },
    {
      "day": 14,
      "effect": {"metric": "REPUTATION", "change": -3, "reason": "온라인 리뷰 악화"}
    }
  ]
}
```

### M-4: AI 스토리텔러

**입력 예시:**
```json
{
  "day": 20,
  "game_progression": 0.67,
  "player_metrics_history": [
    {"day": 18, "metrics": {"money": 25000, "reputation": 85, "happiness": 70}},
    {"day": 19, "metrics": {"money": 27500, "reputation": 88, "happiness": 72}},
    {"day": 20, "metrics": {"money": 30000, "reputation": 90, "happiness": 75}}
  ],
  "recent_events": [
    {"day": 17, "id": "SUPPLY_SHORTAGE", "severity": 0.4},
    {"day": 19, "id": "POSITIVE_REVIEW", "severity": 0.3}
  ]
}
```

**출력 예시:**
```json
{
  "narrative": "사업이 번창하고 평판이 높아지자, 경쟁자들의 시선이 날카로워집니다. 성공은 때로 예상치 못한 도전을 불러옵니다.",
  "suggested_event": {
    "id": "COMPETITOR_SABOTAGE",
    "severity": 0.75,
    "description": "경쟁 업체가 당신의 가게에 대한 악의적인 소문을 퍼뜨리기 시작했습니다."
  }
}
```

### M-5: 헤지 시스템

**입력 예시:**
```json
{
  "action": {
    "type": "PURCHASE_INSURANCE",
    "coverage": "FOOD_SAFETY",
    "cost": 2000,
    "duration": 10
  },
  "current_state": {
    "money": 22000,
    "active_hedges": []
  }
}
```

**출력 예시:**
```json
{
  "new_state": {
    "money": 20000,
    "active_hedges": [
      {
        "type": "INSURANCE",
        "coverage": "FOOD_SAFETY",
        "remaining_days": 10,
        "effect": {
          "event_types": ["FOOD_POISONING"],
          "damage_reduction": 0.7
        }
      }
    ]
  },
  "tradeoff_effects": [
    {"metric": "MONEY", "change": -2000, "reason": "보험 가입 비용"},
    {"metric": "HAPPINESS", "change": 5, "reason": "위험 감소로 인한 안도감"}
  ]
}
```

## 모듈 간 의존성

```
M-1 코어 경제 ◄─── M-3 랜덤 이벤트 엔진 ◄─── M-4 AI 스토리텔러
  │                      │
  ▼                      ▼
M-2 지표/게이지      M-5 헤지 시스템
  │                      │
  └──────────► M-6 대시보드 목업 ◄────────┘
```

모든 모듈은 `schema.py`에 정의된 상수와 Enum을 import하여 사용합니다. 이를 통해 일관된 지표 관리와 모듈 간 호환성을 보장합니다.

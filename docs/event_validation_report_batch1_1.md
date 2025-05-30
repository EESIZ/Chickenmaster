# 이벤트 템플릿 검증 결과 보고서

## 개요
- **검증 대상**: daily_routine_events_batch1 (1).md 파일에서 추출한 이벤트 데이터
- **검증 도구**: dev_tools.event_validator
- **검증 결과**: 구조적 오류 발견

## 주요 오류 유형

### 1. effects 필드 구조 불일치
모든 이벤트에서 effects 필드가 표준 템플릿과 다른 구조로 되어 있습니다:

**현재 구조** (MD 파일에서 추출):
```json
"effects": {
  "immediate": {"metric1": value1, "metric2": value2},
  "delayed": {"metric3": value3, "metric4": value4}
}
```

**필요한 구조** (표준 템플릿):
```json
"effects": [
  {
    "metric": "METRIC_NAME",
    "formula": "value + 10",
    "message": "효과 설명 메시지"
  },
  ...
]
```

### 2. THRESHOLD 타입 이벤트의 trigger 필드 누락
THRESHOLD 타입 이벤트에 필수적인 trigger 필드가 누락되었습니다:

**누락된 이벤트**:
- morning_cleaning_check
- lunch_waiting_line
- ingredient_shortage_lunch
- store_noise_issue
- cooking_time_pressure
- lunch_menu_stock_shortage

**필요한 구조**:
```json
"trigger": {
  "metric": "METRIC_NAME",
  "condition": "less_than",
  "value": 70
}
```

## 해결 방안

### 1. effects 필드 구조 변환
모든 이벤트의 effects 필드를 다음과 같이 변환해야 합니다:

```json
// 변환 전
"effects": {
  "immediate": {"stress": 10},
  "delayed": {"franchise_relationship": -2}
}

// 변환 후
"effects": [
  {
    "metric": "STRESS",
    "formula": "value + 10",
    "message": "스트레스가 증가했습니다."
  },
  {
    "metric": "FRANCHISE_RELATIONSHIP",
    "formula": "value - 2",
    "message": "본사와의 관계가 소폭 악화되었습니다."
  }
]
```

### 2. THRESHOLD 이벤트에 trigger 필드 추가
THRESHOLD 타입 이벤트에 conditions 배열의 첫 번째 조건을 기반으로 trigger 필드를 추가해야 합니다:

```json
// 예: morning_cleaning_check 이벤트
"conditions": ["hygiene < 70"],

// 추가할 필드
"trigger": {
  "metric": "HYGIENE",
  "condition": "less_than",
  "value": 70
}
```

## 결론
daily_routine_events_batch1 (1).md 파일에서 추출한 이벤트 데이터는 구조적 변환이 필요합니다. 이벤트 내용 자체는 완전하고 풍부하지만, 표준 템플릿과의 구조적 차이로 인해 검증에 실패했습니다. 자동화된 변환 스크립트를 통해 effects 필드 구조를 변환하고 THRESHOLD 이벤트에 trigger 필드를 추가하면 이벤트뱅크에 성공적으로 통합할 수 있을 것입니다.

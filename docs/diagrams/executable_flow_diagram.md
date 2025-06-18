# 🚀 실행 가능한 플로우 다이어그램

이 문서는 **실제로 실행되는 순서**를 중심으로 한 새로운 다이어그램 스타일을 제시합니다.

## 🎯 새로운 접근법의 특징

- **구체적 실행 플로우**: 추상적 개념보다 실제 실행 순서
- **액션 중심**: 플레이어 액션부터 결과까지 전체 흐름
- **모듈 구조화**: subgraph로 관련 기능들 그룹화
- **디버깅 친화적**: 문제 발생 지점 쉽게 추적

---

## 🎮 치킨마스터 실행 플로우

```mermaid
flowchart TD
    START[🎮 치킨마스터 시작] --> INIT[⚙️ 초기화 시스템]
    INIT --> CONFIG[📋 설정 로드]
    CONFIG --> EXCEL[📊 엑셀 데이터 로드]
    EXCEL --> VALIDATE[🛡️ 데이터 검증]
    VALIDATE --> CREATE_STATE[🎯 초기 GameState 생성]
    
    CREATE_STATE --> GAME_LOOP[🔄 게임 메인 루프]
    
    GAME_LOOP --> INPUT[⌨️ 플레이어 입력]
    INPUT --> ACTION{🎯 액션 분석}
    
    ACTION -->|가격 변경| PRICE[💰 가격 트레이드오프]
    ACTION -->|직원 관리| STAFF[👥 직원 트레이드오프]
    ACTION -->|마케팅| MARKETING[📢 마케팅 트레이드오프]
    ACTION -->|휴식| REST[😴 휴식 트레이드오프]
    
    PRICE --> CALCULATE[🧮 효과 계산]
    STAFF --> CALCULATE
    MARKETING --> CALCULATE
    REST --> CALCULATE
    
    CALCULATE --> APPLY[⚡ 상태 업데이트]
    APPLY --> EVENT_CHECK[🎲 이벤트 체크]
    
    EVENT_CHECK --> CASCADE[🌊 연쇄 효과 처리]
    CASCADE --> METRICS[📊 메트릭 업데이트]
    METRICS --> DISPLAY[🖥️ 결과 표시]
    
    DISPLAY --> GAME_OVER{💀 게임 종료?}
    GAME_OVER -->|계속| GAME_LOOP
    GAME_OVER -->|종료| END[👋 게임 종료]
    
    %% 트레이드오프 세부 처리
    CALCULATE --> C1[💰 자금 계산]
    CALCULATE --> C2[📈 평판 계산]
    CALCULATE --> C3[😊 행복도 계산]
    CALCULATE --> C4[😰 고통도 계산]
    
    C1 --> APPLY
    C2 --> APPLY
    C3 --> APPLY
    C4 --> APPLY
    
    %% 이벤트 처리 세부사항
    EVENT_CHECK --> E1[🎲 확률 계산]
    EVENT_CHECK --> E2[📋 조건 확인]
    EVENT_CHECK --> E3[🔍 이벤트 선별]
    
    E1 --> E4[⚡ 이벤트 발동]
    E2 --> E4
    E3 --> E4
    E4 --> CASCADE
    
    %% 연쇄 효과 세부사항
    CASCADE --> CS1[🚨 임계값 체크]
    CASCADE --> CS2[⛓️ 2차 효과 적용]
    CASCADE --> CS3[🔄 3차 효과 체크]
    
    CS1 --> METRICS
    CS2 --> METRICS
    CS3 --> METRICS
    
    %% 핵심 시스템 모듈
    subgraph "🏛️ 도메인 계층"
        DOMAIN_STATE[GameState]
        DOMAIN_METRICS[MetricsSnapshot]
        DOMAIN_EVENTS[Event 모델]
    end
    
    subgraph "⚖️ 트레이드오프 엔진"
        TRADE_PRICE[tradeoff_apply_price_change]
        TRADE_APPLY[apply_tradeoff]
        TRADE_CAP[cap_metric_value]
    end
    
    subgraph "🎲 이벤트 시스템"
        EVENT_ENGINE[EventEngine]
        EVENT_CASCADE[_process_cascade_effects]
        EVENT_MATRIX[cascade_matrix]
    end
    
    subgraph "📊 데이터 관리"
        EXCEL_PROVIDER[ExcelGameDataProvider]
        VAR_REGISTRY[VariableRegistry]
        FORMULA_EVAL[evaluate_formula]
    end
    
    subgraph "🎮 게임 루프"
        TRACKER[MetricsTracker]
        INITIALIZER[GameInitializer]
        VALIDATOR[FormulaValidator]
    end
    
    %% 모듈 간 연결
    DOMAIN_STATE --> TRADE_PRICE
    DOMAIN_METRICS --> EVENT_ENGINE
    EXCEL_PROVIDER --> VAR_REGISTRY
    VAR_REGISTRY --> FORMULA_EVAL
    EVENT_ENGINE --> EVENT_CASCADE
    TRACKER --> INITIALIZER
```

---

## 🎯 이 스타일의 장점

### 1. **실행 순서 명확**
```mermaid
flowchart LR
    A[시작] --> B[초기화] --> C[게임루프] --> D[종료]
```
➡️ **코드 실행 순서와 정확히 일치**

### 2. **디버깅 친화적**
각 단계별로 어디서 문제가 생겼는지 쉽게 추적 가능:
- 🛡️ 데이터 검증 단계
- 🧮 효과 계산 단계  
- ⚡ 상태 업데이트 단계
- 🌊 연쇄 효과 단계

### 3. **개발자 온보딩 최적화**
신규 개발자가 시스템을 이해하는 순서:
1. 전체 플로우 파악
2. 세부 모듈 이해
3. 코드 매핑

### 4. **테스트 케이스 설계**
각 단계별로 테스트 케이스 설계 가능:
```python
def test_price_tradeoff_flow():
    # 1. 가격 변경 액션
    # 2. 트레이드오프 계산
    # 3. 상태 업데이트 
    # 4. 연쇄 효과 체크
```

---

## 📊 기존 vs 새로운 스타일 비교

| 특징 | 기존 스타일 | 새로운 스타일 |
|------|-------------|---------------|
| **목적** | 아키텍처 이해 | 실행 플로우 이해 |
| **관점** | 구조적 (What) | 절차적 (How) |
| **활용** | 설계 문서 | 개발/디버깅 가이드 |
| **대상** | 아키텍트 | 개발자 |
| **장점** | 전체 구조 파악 | 구체적 구현 가이드 |

---

## 🚀 활용 가능한 시나리오

### 1. **신규 개발자 온보딩**
```mermaid
flowchart TD
    NEW_DEV[🆕 신규 개발자] --> FLOW[실행 플로우 학습]
    FLOW --> CODE[코드 매핑]
    CODE --> UNDERSTAND[시스템 이해 완료]
```

### 2. **버그 디버깅**
```mermaid
flowchart TD
    BUG[🐛 버그 발생] --> FLOW_TRACE[플로우 따라가기]
    FLOW_TRACE --> IDENTIFY[문제 단계 식별]
    IDENTIFY --> FIX[수정]
```

### 3. **기능 추가**
```mermaid
flowchart TD
    FEATURE[✨ 새 기능] --> FLOW_INSERT[플로우에 삽입점 찾기]
    FLOW_INSERT --> IMPLEMENT[구현]
    IMPLEMENT --> INTEGRATE[통합]
```

---

## 💡 결론

**두 스타일 모두 필요합니다!**

- **구조적 다이어그램**: 전체 아키텍처 이해용
- **실행 플로우 다이어그램**: 개발/운영용

이렇게 **상호 보완적으로** 사용할 때 최대 효과를 발휘합니다! 🎯 
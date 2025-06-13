# ⚖️ 트레이드오프 시스템

🎯 **"정답 없는 게임"의 핵심 메커니즘!**  
모든 선택이 득과 실을 동시에 가져오는 트레이드오프 시스템을 시각화합니다.

## ⚖️ 트레이드오프 메커니즘

```mermaid
graph TD
    PlayerAction[⚡ 플레이어 액션] --> PrimaryEffect[✅ 1차 효과<br/>의도된 결과]
    
    PrimaryEffect --> TradeoffEngine[⚖️ 트레이드오프 엔진<br/>TRADEOFF_RELATIONSHIPS]
    
    TradeoffEngine --> TradeoffCheck{🔍 트레이드오프 관계 확인}
    
    TradeoffCheck --> MoneyUp{💰 Money ↑}
    TradeoffCheck --> ReputationUp{⭐ Reputation ↑}
    TradeoffCheck --> HappinessUp{😊 Happiness ↑}
    TradeoffCheck --> FacilitiesUp{🏭 Facilities ↑}
    
    MoneyUp --> MoneyTrade[💰 → 😊↓, 😴↑<br/>돈 증가 시<br/>행복 감소, 피로 증가]
    ReputationUp --> RepTrade[⭐ → 💰↓, 😴↑<br/>평판 증가 시<br/>돈 감소, 피로 증가]
    HappinessUp --> HappyTrade[😊 → ⭐↓, 🏭↓<br/>행복 증가 시<br/>평판 감소, 시설 감소]
    FacilitiesUp --> FacTrade[🏭 → 💰↓, 😊↓<br/>시설 증가 시<br/>돈 감소, 행복 감소]
    
    MoneyTrade --> CascadeEngine[🌊 연쇄 효과 엔진]
    RepTrade --> CascadeEngine
    HappyTrade --> CascadeEngine
    FacTrade --> CascadeEngine
    
    CascadeEngine --> CascadeCheck{🔄 연쇄 깊이 < 5?}
    CascadeCheck -->|예| ApplyCascade[✅ 연쇄 효과 적용]
    CascadeCheck -->|아니오| StopCascade[🛑 연쇄 중단<br/>무한루프 방지]
    
    ApplyCascade --> SecondaryTradeoff[⚖️ 2차 트레이드오프]
    SecondaryTradeoff --> CascadeEngine
    
    ApplyCascade --> FinalEffect[💥 최종 효과 적용]
    StopCascade --> FinalEffect
    
    FinalEffect --> UpdateMetrics[📊 지표 업데이트]
    UpdateMetrics --> DisplayChange[🖥️ 변화량 표시]
```

## 📊 트레이드오프 관계 매트릭스

```mermaid
graph LR
    subgraph "💰 Money 증가 시"
        MoneyUp[💰 Money ↑] --> MoneyDown1[😊 Happiness ↓]
        MoneyUp --> MoneyDown2[😴 Staff Fatigue ↑]
    end
    
    subgraph "⭐ Reputation 증가 시"
        RepUp[⭐ Reputation ↑] --> RepDown1[💰 Money ↓]
        RepUp --> RepDown2[😴 Staff Fatigue ↑]
    end
    
    subgraph "😊 Happiness 증가 시"
        HappyUp[😊 Happiness ↑] --> HappyDown1[⭐ Reputation ↓]
        HappyUp --> HappyDown2[🏭 Facilities ↓]
    end
    
    subgraph "😰 Pain 증가 시"
        PainUp[😰 Pain ↑] --> PainDown1[💰 Money ↓]
        PainUp --> PainDown2[📈 Demand ↓]
    end
    
    subgraph "📦 Inventory 증가 시"
        InvUp[📦 Inventory ↑] --> InvDown1[💰 Money ↓]
        InvUp --> InvDown2[😴 Staff Fatigue ↑]
    end
    
    subgraph "😴 Staff Fatigue 증가 시"
        FatUp[😴 Staff Fatigue ↑] --> FatDown1[⭐ Reputation ↓]
        FatUp --> FatDown2[😊 Happiness ↓]
    end
    
    subgraph "🏭 Facilities 증가 시"
        FacUp[🏭 Facilities ↑] --> FacDown1[💰 Money ↓]
        FacUp --> FacDown2[😊 Happiness ↓]
    end
    
    subgraph "📈 Demand 증가 시"
        DemUp[📈 Demand ↑] --> DemDown1[😴 Staff Fatigue ↑]
        DemUp --> DemDown2[📦 Inventory ↓]
    end
```

## 🎮 구체적인 게임 시나리오

### 💰 가격 인상 시나리오

```mermaid
sequenceDiagram
    participant Player as 👤 플레이어
    participant Action as ⚡ 가격 인상
    participant Engine as ⚖️ 트레이드오프 엔진
    participant Metrics as 📊 지표
    
    Player->>Action: "가격을 올리자!"
    Action->>Metrics: Money +1000 (1차 효과)
    Action->>Engine: 트레이드오프 체크
    
    Engine->>Metrics: Reputation -2 (평판 하락)
    Engine->>Metrics: Demand ±5 (수요 변동)
    
    Note over Engine,Metrics: 연쇄 효과 시작
    Engine->>Engine: Reputation ↓ → Money ↓
    Engine->>Metrics: Money -100 (2차 효과)
    
    Note over Player,Metrics: 최종 결과
    Metrics-->>Player: Money +900, Reputation -2, Demand ±5
    Player->>Player: "득도 있고 실도 있군..."
```

### 🏭 시설 개선 시나리오

```mermaid
sequenceDiagram
    participant Player as 👤 플레이어
    participant Action as ⚡ 시설 개선
    participant Engine as ⚖️ 트레이드오프 엔진
    participant Metrics as 📊 지표
    
    Player->>Action: "시설을 개선하자!"
    Action->>Metrics: Money -100000 (투자비용)
    Action->>Metrics: Facilities +20 (1차 효과)
    Action->>Engine: 트레이드오프 체크
    
    Engine->>Metrics: Reputation +10 (좋은 시설)
    Engine->>Metrics: Happiness -5 (스트레스)
    
    Note over Engine,Metrics: 연쇄 효과 시작
    Engine->>Engine: Reputation ↑ → Staff Fatigue ↑
    Engine->>Metrics: Staff Fatigue +3 (2차 효과)
    
    Note over Player,Metrics: 최종 결과
    Metrics-->>Player: Money -100000, Facilities +20,<br/>Reputation +10, Happiness -5, Staff Fatigue +3
    Player->>Player: "투자는 했지만 팀이 힘들어한다..."
```

## 🎲 불확실성 요소

```mermaid
graph TD
    BaseEffect[📊 기본 트레이드오프] --> UncertaintyWeights[🎲 불확실성 가중치<br/>UNCERTAINTY_WEIGHTS]
    
    UncertaintyWeights --> MoneyWeight[💰 Money: 0.8<br/>80% 확률로 예상대로]
    UncertaintyWeights --> RepWeight[⭐ Reputation: 0.6<br/>60% 확률로 예상대로]
    UncertaintyWeights --> HappyWeight[😊 Happiness: 0.4<br/>40% 확률로 예상대로]
    
    MoneyWeight --> MoneyResult{🎯 random() < 0.8?}
    RepWeight --> RepResult{🎯 random() < 0.6?}
    HappyWeight --> HappyResult{🎯 random() < 0.4?}
    
    MoneyResult -->|예| MoneyExpected[💰 예상 효과 적용]
    MoneyResult -->|아니오| MoneyUnexpected[💰 반대 효과 또는 무효과]
    
    RepResult -->|예| RepExpected[⭐ 예상 효과 적용]
    RepResult -->|아니오| RepUnexpected[⭐ 예상치 못한 결과]
    
    HappyResult -->|예| HappyExpected[😊 예상 효과 적용]
    HappyResult -->|아니오| HappyUnexpected[😊 완전히 다른 결과]
    
    MoneyExpected --> FinalOutcome[🎯 최종 결과]
    MoneyUnexpected --> FinalOutcome
    RepExpected --> FinalOutcome
    RepUnexpected --> FinalOutcome
    HappyExpected --> FinalOutcome
    HappyUnexpected --> FinalOutcome
```

## 🧠 게임 철학 구현

### 🚫 정답 없음 (No Right Answer)

```mermaid
graph TD
    Decision[🤔 플레이어 선택] --> Option1[📈 수익 최대화]
    Decision --> Option2[⭐ 평판 중시]
    Decision --> Option3[😊 행복 추구]
    Decision --> Option4[⚖️ 균형 전략]
    
    Option1 --> Result1[💰↑ 😊↓ ⭐↓<br/>돈은 많지만 불행하고 평판 나쁨]
    Option2 --> Result2[⭐↑ 💰↓ 😴↑<br/>평판은 좋지만 돈 부족과 피로]
    Option3 --> Result3[😊↑ ⭐↓ 🏭↓<br/>행복하지만 사업이 뒷걸음질]
    Option4 --> Result4[📊 모든 지표 중간<br/>특별히 좋지도 나쁘지도 않음]
    
    Result1 --> Philosophy[🎯 모든 선택은<br/>득과 실이 공존한다]
    Result2 --> Philosophy
    Result3 --> Philosophy
    Result4 --> Philosophy
```

### ⚖️ 트레이드오프 철학

```mermaid
mindmap
  root((🎮 트레이드오프<br/>철학))
    🚫 정답 없음
      모든 선택이 양면성
      완벽한 해답 불가능
      상황별 최선 달라짐
    ⚖️ 균형 추구
      극단 회피
      적절한 타협점
      지속 가능성
    🎲 불확실성
      예측 불가능
      리스크 관리
      적응력 중요
    📈 성장 지향
      실패를 통한 학습
      점진적 개선
      경험치 축적
```

## 🔧 밸런싱 레버

### 📊 상수 조정을 통한 게임 밸런싱

```mermaid
graph TD
    BalancingTeam[🎨 밸런싱 팀] --> ExcelFile[📊 Excel 파일 수정]
    
    ExcelFile --> TradeoffSheet[🔄 Tradeoff_Relationships<br/>트레이드오프 강도 조정]
    ExcelFile --> UncertaintySheet[🎲 Uncertainty_Weights<br/>불확실성 레벨 조정]
    ExcelFile --> ThresholdSheet[⚖️ Threshold_Constants<br/>임계값 조정]
    
    TradeoffSheet --> Example1[💰 Money → 😊 Happiness<br/>-0.5 → -0.3 (완화)]
    UncertaintySheet --> Example2[😊 Happiness Weight<br/>0.4 → 0.6 (더 예측 가능)]
    ThresholdSheet --> Example3[MONEY_LOW_THRESHOLD<br/>3000 → 5000 (더 까다롭게)]
    
    Example1 --> ReloadConstants[🔄 reload_all_constants()]
    Example2 --> ReloadConstants
    Example3 --> ReloadConstants
    
    ReloadConstants --> TestPlay[🎮 테스트 플레이]
    TestPlay --> FeedbackLoop[📝 피드백 수집]
    FeedbackLoop --> BalancingTeam
```

## 💡 설계 원칙

### ✅ Do's (해야 할 것)

1. **명확한 인과관계** - 모든 트레이드오프는 논리적 근거가 있어야 함
2. **플레이어 이해** - 트레이드오프 결과가 예측 가능해야 함  
3. **밸런스 유지** - 어떤 전략도 완전히 지배적이지 않아야 함
4. **점진적 조정** - 급격한 변화보다는 부드러운 조정

### ❌ Don'ts (하지 말아야 할 것)

1. **무의미한 페널티** - 논리적 근거 없는 불이익
2. **예측 불가능** - 완전히 랜덤한 결과
3. **극단적 불균형** - 한쪽으로 치우친 트레이드오프
4. **복잡성 과다** - 이해하기 어려운 복잡한 연쇄

## 🎯 성공 지표

### 📊 밸런싱 품질 지표

| 지표 | 목표 값 | 설명 |
|------|---------|------|
| 전략 다양성 | > 4가지 | 플레이어가 선택할 수 있는 유효한 전략 수 |
| 게임 길이 | 15-30일 | 평균 생존 일수 |
| 선택의 고민 시간 | 10-30초 | 플레이어가 고민하는 평균 시간 |
| 재플레이 의향 | > 70% | 게임 종료 후 다시 플레이하고 싶은 비율 |
| 트레이드오프 이해도 | > 80% | 플레이어가 트레이드오프를 이해하는 비율 |

⚖️ **"모든 선택이 딜레마가 되는 게임"의 핵심 시스템!** ⚖️ 
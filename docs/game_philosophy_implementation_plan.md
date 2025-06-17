# 🎮 치킨마스터 게임 철학 구현 계획

## 🎯 핵심 철학
> "확률과 선택의 긴장감 속에서 플레이어가 감정적 여정을 겪는 치킨집 시뮬레이션"

### 사용자 비전 분석
1. **치킨집 차림 → 오픈빨 소멸 → 소소한 위기들 → 선택의 결과로 방향성 결정**
2. **운영방향과 선택이 크게 달라지는 결과 → 다양한 감정 경험**
3. **확률적 결과 시스템 → 불확실성의 스릴**
4. **외부 환경의 추세와 랜덤성 → 수요 변동**
5. **다양한 엔딩 → 파산/생존/성공/기타 엑싯**

## 🚨 현재 문제점

### 기술적 문제
- **Daily Action Slots 시스템 미연결**: 구현되어 있지만 메인 게임에서 사용 안 함
- **무제한 액션**: 하루에 모든 행동 가능 → 전략적 선택 의미 없음
- **확정적 결과**: 모든 액션이 예측 가능한 결과 → 도박의 재미 없음

### 게임 경험 문제
- **Excel 스프레드시트 느낌**: 1,300,000원 축적으로 긴장감 제로
- **선택의 무의미함**: 제약이 없어서 모든 것을 다 할 수 있음
- **감정적 몰입 부족**: 위험과 보상의 균형 없음

## 💀 **즉시 수정해야 할 핵심 시스템**

### 1. 일일 액션 제한 시스템 통합 (최우선)
```python
# 현재: 무제한 액션
def handle_action(action_type):
    return execute_action(action_type)  # 항상 실행

# 목표: 제한된 액션
def handle_action(action_type):
    if not daily_plan.can_perform_action():
        return "오늘 할 수 있는 행동을 모두 사용했습니다."
    return execute_action_with_probability(action_type)
```

### 2. 메인 게임 루프 수정
```python
# web_prototype/main.py 수정
class WebGameManager:
    def __init__(self):
        self.daily_plan = create_daily_action_plan(day=1, config=ActionSlotConfiguration())
        
    def handle_action(self, action_type):
        if not self.daily_plan.can_perform_action():
            return "❌ 오늘은 더 이상 행동할 수 없습니다. 'turn'으로 다음 날로 진행하세요."
        
        # 확률적 결과 적용
        outcome = self.calculate_probabilistic_outcome(action_type)
        self.daily_plan = self.daily_plan.use_action_slot(action_type)
        return outcome
```

### 3. 확률적 결과 시스템 도입
```python
# 모든 액션에 확률적 결과 적용
ACTION_OUTCOMES = {
    "price_increase": {
        "success": (0.6, "고객들이 가격 인상을 받아들였습니다"),
        "failure": (0.3, "고객 이탈로 매출이 급감했습니다"),
        "critical_failure": (0.1, "경쟁업체로 대량 이탈 발생!")
    }
}
```

### 4. 외부 환경 변화 시스템
```python
# 매 턴마다 시장 상황 변동
class MarketEnvironment:
    def __init__(self):
        self.demand_trend = random.uniform(0.8, 1.2)
        self.competition_pressure = random.uniform(0.9, 1.1)
        self.economic_climate = random.choice(['호황', '평상', '불황'])
```

## 🎲 **구현 우선순위**

### Phase 1: 긴급 수정 (1-2일)
1. **Daily Action Slots를 메인 게임에 통합**
2. **모든 액션에 확률적 결과 추가**
3. **현재 돈 1,300,000원을 현실적 수준으로 리셋**

### Phase 2: 핵심 시스템 (3-5일)
1. **외부 환경 변화 시스템**
2. **위기 이벤트 강화**
3. **파산 조건 및 엔딩 시스템**

### Phase 3: 완성도 (1주)
1. **감정적 몰입 요소 강화**
2. **다양한 엔딩 시나리오**
3. **밸런싱 및 테스트**

## 🔥 **즉시 실행 가능한 작업**

### 1. 게임 상태 리셋
- 현재 104일차, 1,300,000원 → 1일차, 10,000원으로 리셋
- Daily Action Slots 시스템 활성화

### 2. 메인 게임 루프 수정
```python
# web_prototype/main.py 수정
class WebGameManager:
    def __init__(self):
        self.daily_plan = create_daily_action_plan(day=1, config=ActionSlotConfiguration())
        
    def handle_action(self, action_type):
        if not self.daily_plan.can_perform_action():
            return "❌ 오늘은 더 이상 행동할 수 없습니다. 'turn'으로 다음 날로 진행하세요."
        
        # 확률적 결과 적용
        outcome = self.calculate_probabilistic_outcome(action_type)
        self.daily_plan = self.daily_plan.use_action_slot(action_type)
        return outcome
```

### 3. 확률 시스템 도입
- 모든 액션 20-80% 성공률
- 실패 시 부작용 발생
- 크리티컬 성공/실패 1-5% 확률

## 💡 **게임 디자인 철학 구현**

### "정답 없음" 원칙
- 모든 선택에 득과 실이 공존
- 성공적인 선택도 예상치 못한 부작용 발생 가능

### "트레이드오프" 시스템
- 한 지표 상승 → 다른 지표 하락 확률
- 단기 이익 vs 장기 안정성 딜레마

### "불확실성" 요소
- 확률적 결과로 완벽한 예측 불가능
- 외부 환경 변화로 상황 급변

## 🎭 **감정적 경험 설계**

### 긴장감 조성
- 제한된 액션으로 선택의 어려움
- 확률적 결과로 도박의 스릴
- 파산 위험으로 절박함

### 성취감 제공
- 위기 극복 시 강한 만족감
- 운 좋은 결과에 대한 기쁨
- 전략적 선택의 성공

### 아쉬움과 후회
- 실패한 선택에 대한 후회
- "만약에..."라는 생각
- 다시 해보고 싶은 욕구

## 🏁 **엔딩 시나리오**

### 파산 엔딩 (가장 흔함)
- 돈이 0원 이하로 떨어짐
- "치킨집 운영의 현실을 마주했습니다..."

### 생존 엔딩
- 일정 기간 버텨냄
- "평범하지만 소중한 일상을 지켜냈습니다"

### 성공 엔딩 (매우 어려움)
- 높은 평판 + 안정적 수익
- "치킨집 사장의 꿈을 이뤘습니다!"

### 특수 엔딩
- 연구개발로 프랜차이즈화
- 경쟁업체에 인수
- 건강 문제로 은퇴

---

**다음 단계**: Phase 1 긴급 수정 작업부터 즉시 시작! 
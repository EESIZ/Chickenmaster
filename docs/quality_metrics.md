# 이벤트 품질 메트릭 가이드

## 개요

이 문서는 치킨집 경영 시뮬레이션 게임의 이벤트 품질을 객관적으로 평가하기 위한 메트릭 체계를 정의합니다. 이 메트릭들은 자동화된 검증 도구에서 사용되며, 이벤트 뱅크의 전반적인 품질을 보장하는 데 중요한 역할을 합니다.

## 핵심 품질 메트릭

### 1. 다양성 점수 (Diversity Score)

**정의**: 이벤트 카테고리, 타입, 효과 등의 분포 균형성을 측정

**계산 방법**: Shannon Entropy 기반 정규화 점수
```python
def calculate_diversity_score(events):
    # 카테고리별 이벤트 수 계산
    categories = {}
    for event in events:
        category = event.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
        
    # Shannon Entropy 계산
    total = sum(categories.values())
    entropy = 0.0
    for count in categories.values():
        p = count / total
        entropy -= p * math.log(p)
        
    # 정규화 (0-1 범위)
    max_entropy = math.log(len(categories))
    if max_entropy == 0:
        return 0.0
    return entropy / max_entropy
```

**목표값**: ≥ 0.8

**해석**:
- 0.8-1.0: 우수 (균형 잡힌 다양한 이벤트)
- 0.6-0.8: 양호 (적절한 다양성)
- 0.4-0.6: 보통 (일부 카테고리에 편중)
- 0.0-0.4: 미흡 (심각한 불균형)

**개선 방법**:
- 부족한 카테고리의 이벤트 추가
- 과도하게 많은 카테고리의 이벤트 품질 개선에 집중
- 새로운 하위 카테고리 도입 검토

### 2. 트레이드오프 명확성 (Tradeoff Clarity)

**정의**: 이벤트 선택지가 명확한 득실 관계를 가지는 정도

**계산 방법**: 명확한 트레이드오프를 가진 이벤트 비율
```python
def calculate_tradeoff_clarity(events):
    if not events:
        return 0.0
        
    events_with_tradeoffs = 0
    for event in events:
        choices = event.get('choices', [])
        if has_clear_tradeoffs(choices):
            events_with_tradeoffs += 1
            
    return events_with_tradeoffs / len(events)
```

**목표값**: ≥ 0.9

**해석**:
- 0.9-1.0: 우수 (거의 모든 이벤트가 명확한 트레이드오프 포함)
- 0.7-0.9: 양호 (대부분의 이벤트가 트레이드오프 포함)
- 0.5-0.7: 보통 (일부 이벤트만 트레이드오프 포함)
- 0.0-0.5: 미흡 (트레이드오프가 부족함)

**개선 방법**:
- 각 선택지에 장단점 추가
- 단순한 "좋음/나쁨" 이분법 대신 복합적 효과 설계
- 다양한 메트릭에 영향을 주는 효과 추가

### 3. 문화적 진정성 (Cultural Authenticity)

**정의**: 한국 치킨집 문화를 얼마나 잘 반영하는지 측정

**계산 방법**: 문화적 키워드 및 요소 포함 비율
```python
def calculate_cultural_authenticity(events):
    if not events:
        return 0.0
        
    # 한국 치킨집 관련 키워드
    keywords = [
        "배달", "프랜차이즈", "단골", "동네", "치킨", "맥주", "소주",
        "양념", "후라이드", "반반", "사장님", "알바", "주문", "포장",
        "매장", "손님", "서비스", "할인", "이벤트", "마케팅"
    ]
    
    authentic_events = 0
    for event in events:
        text_ko = event.get('text_ko', '')
        name_ko = event.get('name_ko', '')
        
        # 키워드 매칭
        matched_keywords = 0
        for keyword in keywords:
            if keyword in text_ko or keyword in name_ko:
                matched_keywords += 1
                
        # 최소 2개 이상의 키워드가 매칭되면 진정성 있는 이벤트로 간주
        if matched_keywords >= 2:
            authentic_events += 1
            
    return authentic_events / len(events)
```

**목표값**: ≥ 0.7

**해석**:
- 0.7-1.0: 우수 (강한 문화적 맥락 반영)
- 0.5-0.7: 양호 (적절한 문화적 요소 포함)
- 0.3-0.5: 보통 (일부 문화적 요소만 포함)
- 0.0-0.3: 미흡 (문화적 맥락 부족)

**개선 방법**:
- 한국 치킨집 관련 용어 및 상황 추가
- 현지 문화 요소 연구 및 반영
- 실제 치킨집 운영자 인터뷰 참고

### 4. 재플레이 가치 (Replayability)

**정의**: 이벤트의 다양한 조건과 확률 분포로 인한 재플레이 가치

**계산 방법**: 조건 다양성과 확률 분포의 균형
```python
def calculate_replayability(events):
    if not events:
        return 0.0
        
    # 조건 다양성 및 확률 분포 평가
    condition_variety = 0
    probability_spread = 0
    
    # 조건 유형 카운트
    condition_types = set()
    probabilities = []
    
    for event in events:
        # 트리거 조건 다양성
        if 'trigger' in event:
            condition = event['trigger'].get('condition')
            if condition:
                condition_types.add(condition)
                
        # 확률 분포
        if 'probability' in event:
            probabilities.append(event['probability'])
            
    # 조건 다양성 점수 (최대 3가지 조건)
    condition_variety = min(1.0, len(condition_types) / 3)
    
    # 확률 분포 점수 (표준편차 기반)
    if probabilities:
        mean = sum(probabilities) / len(probabilities)
        variance = sum((p - mean) ** 2 for p in probabilities) / len(probabilities)
        std_dev = math.sqrt(variance)
        
        # 적절한 표준편차 (0.1-0.3 범위가 이상적)
        if 0.1 <= std_dev <= 0.3:
            probability_spread = 1.0
        elif std_dev < 0.1:
            probability_spread = std_dev / 0.1
        else:  # std_dev > 0.3
            probability_spread = 0.3 / std_dev
            
    # 종합 점수 (조건 다양성 50%, 확률 분포 50%)
    return (condition_variety * 0.5) + (probability_spread * 0.5)
```

**목표값**: ≥ 0.8

**해석**:
- 0.8-1.0: 우수 (높은 재플레이 가치)
- 0.6-0.8: 양호 (적절한 재플레이 가치)
- 0.4-0.6: 보통 (제한된 재플레이 가치)
- 0.0-0.4: 미흡 (낮은 재플레이 가치)

**개선 방법**:
- 다양한 트리거 조건 추가
- 확률 분포 조정 (너무 균일하거나 편중되지 않도록)
- 조건부 이벤트 체인 설계

## 밸런스 메트릭

### 1. 경제 안정성 (Economic Stability)

**정의**: 게임 내 경제 시스템의 안정성과 인플레이션/디플레이션 방지

**계산 방법**: 시뮬레이션 중 자원 변동성 측정
```python
def calculate_economic_stability(metrics_history):
    # MONEY 메트릭의 변동성 분석
    money_values = [turn['MONEY'] for turn in metrics_history]
    
    if not money_values or len(money_values) < 2:
        return 0.0
        
    # 변동성 계산 (표준편차/평균)
    mean = sum(money_values) / len(money_values)
    variance = sum((v - mean) ** 2 for v in money_values) / len(money_values)
    std_dev = math.sqrt(variance)
    
    coefficient_of_variation = std_dev / mean if mean > 0 else float('inf')
    
    # 변동성 점수 변환 (낮을수록 좋음)
    if coefficient_of_variation <= 0.2:
        return 1.0
    elif coefficient_of_variation >= 1.0:
        return 0.0
    else:
        return 1.0 - (coefficient_of_variation - 0.2) / 0.8
```

**목표값**: ≥ 0.7

**해석**:
- 0.7-1.0: 우수 (안정적인 경제 시스템)
- 0.5-0.7: 양호 (적절한 경제 변동성)
- 0.3-0.5: 보통 (다소 불안정한 경제)
- 0.0-0.3: 미흡 (매우 불안정한 경제)

**개선 방법**:
- 극단적인 경제 효과를 가진 이벤트 조정
- 긍정적/부정적 경제 효과의 균형 조정
- 자동 안정화 메커니즘 추가

### 2. 평판 곡선 (Reputation Curve)

**정의**: 게임 진행에 따른 평판 성장 곡선의 적절성

**계산 방법**: 이상적인 성장 곡선과의 편차
```python
def calculate_reputation_curve(metrics_history):
    # REPUTATION 메트릭 추출
    reputation_values = [turn['REPUTATION'] for turn in metrics_history]
    
    if not reputation_values or len(reputation_values) < 10:
        return 0.0
        
    # 이상적인 성장 곡선 (로그 함수 기반)
    turns = len(reputation_values)
    ideal_curve = [50 * math.log(1 + (i / turns) * 2.7) for i in range(turns)]
    
    # 실제 곡선과 이상적 곡선의 편차
    max_deviation = sum(ideal_curve) * 0.5  # 50% 편차를 최대로 간주
    actual_deviation = sum(abs(a - b) for a, b in zip(reputation_values, ideal_curve))
    
    # 점수 계산 (낮은 편차일수록 높은 점수)
    score = 1.0 - (actual_deviation / max_deviation)
    return max(0.0, min(1.0, score))
```

**목표값**: ≥ 0.6

**해석**:
- 0.6-1.0: 우수 (이상적인 성장 곡선)
- 0.4-0.6: 양호 (적절한 성장 패턴)
- 0.2-0.4: 보통 (불규칙한 성장 패턴)
- 0.0-0.2: 미흡 (부적절한 성장 패턴)

**개선 방법**:
- 초기 게임에 긍정적 평판 이벤트 추가
- 중반 게임에 도전적 평판 이벤트 추가
- 후반 게임에 평판 유지 메커니즘 추가

### 3. 이벤트 분포 (Event Distribution)

**정의**: 게임 진행 중 이벤트 발생의 균형적 분포

**계산 방법**: 턴당 이벤트 발생 빈도의 균일성
```python
def calculate_event_distribution(event_history):
    # 턴별 이벤트 발생 횟수
    turn_counts = {}
    for event in event_history:
        turn = event['turn']
        turn_counts[turn] = turn_counts.get(turn, 0) + 1
        
    if not turn_counts:
        return 0.0
        
    # 발생 빈도 분석
    values = list(turn_counts.values())
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std_dev = math.sqrt(variance)
    
    # 이상적인 분포는 낮은 표준편차를 가짐
    coefficient_of_variation = std_dev / mean if mean > 0 else float('inf')
    
    # 변동성 점수 변환 (낮을수록 좋음)
    if coefficient_of_variation <= 0.3:
        return 1.0
    elif coefficient_of_variation >= 1.5:
        return 0.0
    else:
        return 1.0 - (coefficient_of_variation - 0.3) / 1.2
```

**목표값**: ≥ 0.7

**해석**:
- 0.7-1.0: 우수 (균형 잡힌 이벤트 분포)
- 0.5-0.7: 양호 (적절한 이벤트 분포)
- 0.3-0.5: 보통 (다소 불균형한 분포)
- 0.0-0.3: 미흡 (매우 불균형한 분포)

**개선 방법**:
- 이벤트 확률 조정
- 쿨다운 메커니즘 최적화
- 턴 기반 이벤트 트리거 추가

## 종합 품질 점수

**정의**: 모든 메트릭을 종합한 전체 품질 점수

**계산 방법**: 가중 평균
```python
def calculate_overall_quality(metrics):
    weights = {
        'diversity_score': 0.15,
        'tradeoff_clarity': 0.25,
        'cultural_authenticity': 0.15,
        'replayability': 0.15,
        'economic_stability': 0.1,
        'reputation_curve': 0.1,
        'event_distribution': 0.1
    }
    
    score = 0.0
    for metric, weight in weights.items():
        if metric in metrics:
            score += metrics[metric] * weight
            
    return score
```

**목표값**: ≥ 0.75

**해석**:
- 0.75-1.00: A (우수)
- 0.65-0.75: B (양호)
- 0.50-0.65: C (보통)
- 0.00-0.50: D (미흡)

## 품질 보고서 생성

이벤트 뱅크의 품질 메트릭은 다음과 같은 형식으로 보고됩니다:

```
# 이벤트 뱅크 품질 보고서

생성일: 2025-05-27
총 이벤트 수: 500

## 콘텐츠 품질 메트릭
- 다양성 점수: 0.85 ✅
- 트레이드오프 명확성: 0.92 ✅
- 문화적 진정성: 0.78 ✅
- 재플레이 가치: 0.81 ✅

## 밸런스 메트릭
- 경제 안정성: 0.72 ✅
- 평판 곡선: 0.68 ✅
- 이벤트 분포: 0.75 ✅

## 종합 품질 점수: 0.81 (A) ✅

## 개선 권장사항
1. 위기 이벤트 카테고리의 다양성 향상 필요
2. 후반 게임 평판 곡선 조정 권장
3. 경제적 효과의 변동성 소폭 감소 필요
```

## 자동화된 품질 검증

이벤트 뱅크의 품질은 다음 명령으로 자동 검증할 수 있습니다:

```bash
python -m dev_tools.event_bank_manager --validate --metrics
```

이 명령은 모든 이벤트를 검증하고 품질 메트릭을 계산하여 보고서를 생성합니다.

## 지속적 품질 개선

품질 메트릭은 단순한 검증 도구를 넘어 지속적인 품질 개선을 위한 지표로 활용되어야 합니다:

1. **정기적 검토**: 월간 품질 검토 회의 진행
2. **목표 설정**: 각 릴리스마다 개선할 메트릭 목표 설정
3. **A/B 테스트**: 새로운 이벤트 디자인 패턴의 효과 측정
4. **사용자 피드백 연계**: 품질 메트릭과 사용자 만족도 상관관계 분석

## 참고 자료

- [이벤트 스키마 명세서](event_schema_specification.md)
- [콘텐츠 가이드라인](content_guidelines.md)
- [밸런스 시뮬레이터 설계](balance_simulator_design.md)
- [이벤트 뱅크 버전 관리 정책](event_bank_versioning.md)

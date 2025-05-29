# 밸런스 시뮬레이터 설계 및 사용법

## 개요

밸런스 시뮬레이터(Balance Simulator)는 치킨집 경영 게임의 이벤트 밸런스를 자동으로 시뮬레이션하고 평가하는 도구입니다. 이 문서는 시뮬레이터의 설계, 기능, 사용법을 설명합니다.

## 기능

밸런스 시뮬레이터는 다음과 같은 주요 기능을 제공합니다:

1. **이벤트 시뮬레이션**: 실제 게임 환경을 모방하여 이벤트 발생 및 효과 적용
2. **메트릭 추적**: 게임 내 주요 지표(돈, 평판, 고객 수 등)의 변화 기록
3. **밸런스 평가**: 게임 밸런스 점수 계산 및 분석
4. **개선 추천**: 밸런스 개선을 위한 구체적인 추천사항 제공
5. **리포트 생성**: JSON 및 CSV 형식의 상세 분석 리포트 생성

## 사용법

### 명령줄 인터페이스

```bash
# 단일 파일 시뮬레이션
python -m dev_tools.balance_simulator --file path/to/events.toml --turns 100

# 디렉토리 내 모든 이벤트 파일 시뮬레이션
python -m dev_tools.balance_simulator --dir path/to/events/directory --turns 200

# 시드 및 출력 디렉토리 지정
python -m dev_tools.balance_simulator --file path/to/events.toml --turns 100 --seed 123 --output custom_reports
```

### 프로그래밍 방식 사용

```python
from dev_tools.balance_simulator import BalanceSimulator
from pathlib import Path

# 시뮬레이터 초기화
simulator = BalanceSimulator()

# 이벤트 로드
simulator.load_events(Path("path/to/events.toml"))
# 또는 디렉토리 로드
simulator.load_events_directory(Path("path/to/events/directory"))

# 시뮬레이션 실행
simulator.run_simulation(turns=100, seed=42)

# 밸런스 리포트 생성
report = simulator.generate_balance_report()

# 결과 저장
json_path = simulator.save_report_to_json("reports")
csv_path = simulator.save_report_to_csv("reports")
```

## 시뮬레이션 프로세스

### 1. 게임 메트릭 초기화

시뮬레이션은 다음과 같은 기본 메트릭으로 시작합니다:

- **money**: 10,000 (초기 자금)
- **reputation**: 50 (초기 평판)
- **customers**: 100 (초기 고객 수)
- **staff_morale**: 70 (초기 직원 사기)
- **food_quality**: 60 (초기 음식 품질)
- **equipment**: 50 (초기 장비 상태)

### 2. 턴 기반 시뮬레이션

각 턴마다 다음 과정이 수행됩니다:

1. **이벤트 발생 확인**:
   - RANDOM 이벤트: 확률에 따라 발생
   - THRESHOLD 이벤트: 메트릭이 조건을 충족할 때 발생
   - SCHEDULED 이벤트: 지정된 턴마다 발생

2. **이벤트 효과 적용**:
   - 각 이벤트의 효과가 해당 메트릭에 적용됨
   - 포뮬러 문자열이 평가되어 메트릭 값 변경

3. **턴 결과 기록**:
   - 현재 턴의 메트릭 상태 및 발생한 이벤트 기록

### 3. 밸런스 평가

시뮬레이션 완료 후 다음 밸런스 점수가 계산됩니다:

1. **경제 안정성 (economic_stability)**:
   - 돈의 변동성이 적절한지 평가
   - 표준편차가 평균의 30% 이하면 안정적

2. **평판 곡선 (reputation_curve)**:
   - 평판이 적절한 곡선을 그리는지 평가
   - 시작과 끝의 차이가 너무 크지 않고, 변동이 있어야 함

3. **이벤트 분포 균형 (event_distribution)**:
   - 이벤트 발생 빈도의 균형을 평가
   - 발생 빈도의 변동계수가 낮을수록 균형적

4. **고객 성장 곡선 (customer_growth)**:
   - 고객 수가 적절히 증가하는지 평가
   - 성장률이 0~30% 범위가 이상적

5. **직원 사기 안정성 (morale_stability)**:
   - 직원 사기가 안정적으로 유지되는지 평가
   - 표준편차가 낮을수록 안정적

6. **종합 점수 (overall)**:
   - 모든 개별 점수의 평균

## 밸런스 리포트 해석

### JSON 리포트 구조

```json
{
  "timestamp": "2025-05-26 22:29:30",
  "simulation_turns": 50,
  "total_events": 2,
  "triggered_events": 2,
  "metrics_analysis": {
    "money": {
      "start": 10000,
      "end": 5000,
      "min": 5000,
      "max": 10000,
      "avg": 7500,
      "median": 7500,
      "std_dev": 2500,
      "change": -5000,
      "change_percent": -50
    },
    // 다른 메트릭들...
  },
  "event_frequency": {
    "daily_routine_001": 15,
    "daily_routine_002": 5
  },
  "balance_scores": {
    "economic_stability": 0.0,
    "reputation_curve": 0.0,
    "event_distribution": 0.0,
    "overall": 0.0
  },
  "recommendations": [
    "💰 경제 변동성이 높습니다. 이벤트의 money 효과 크기를 줄이거나 분산시키세요.",
    // 다른 추천사항들...
  ]
}
```

### CSV 리포트 구조

metrics_history.csv 파일은 각 턴마다의 메트릭 변화와 발생한 이벤트를 기록합니다:

| turn | money | reputation | customers | staff_morale | food_quality | equipment | events |
|------|-------|------------|-----------|--------------|--------------|-----------|--------|
| 1    | 9500  | 52.5       | 100       | 70           | 60           | 50        | daily_routine_001 |
| 2    | 9500  | 52.5       | 100       | 70           | 60           | 50        |  |
| 3    | 9000  | 55.125     | 100       | 70           | 60           | 50        | daily_routine_001 |
| ...  | ...   | ...        | ...       | ...          | ...          | ...       | ... |

## 밸런스 점수 해석

각 밸런스 점수는 0.0~1.0 범위로 표현되며, 다음과 같이 해석합니다:

- **0.0~0.5**: 불안정 (❌) - 즉시 개선 필요
- **0.5~0.7**: 보통 (⚠️) - 개선 권장
- **0.7~1.0**: 양호 (✅) - 안정적

## 추천사항 활용

시뮬레이터는 밸런스 점수를 기반으로 구체적인 개선 추천사항을 제공합니다:

1. **경제 관련 추천**:
   - 이벤트의 money 효과 크기 조정
   - 경제 변동성 완화

2. **평판 관련 추천**:
   - 긍정적/부정적 평판 이벤트 균형 조정
   - 평판 변화 곡선 최적화

3. **이벤트 분포 관련 추천**:
   - 이벤트 발생 확률 재조정
   - 다양한 이벤트 추가

4. **고객 관련 추천**:
   - 고객 유치/이탈 이벤트 균형 조정
   - 성장 곡선 최적화

5. **직원 관련 추천**:
   - 사기 변동성 완화
   - 회복 이벤트 추가

## 실데이터 연동

밸런스 시뮬레이터는 다음과 같은 방식으로 실제 이벤트 데이터와 연동됩니다:

1. **파일 형식 지원**: TOML(작성용), JSON(런타임용) 두 가지 형식 모두 지원
2. **디렉토리 구조**: `/data/events/<category>/*.toml` 구조의 파일 로드
3. **이벤트 타입**: RANDOM, THRESHOLD, SCHEDULED, CASCADE 모든 이벤트 타입 지원
4. **효과 평가**: 실제 게임과 동일한 방식으로 포뮬러 평가 및 효과 적용

## 반복 오류 방지

이벤트 밸런싱 시 다음 사항을 준수하여 반복 오류를 방지합니다:

1. **경제 균형**: 돈 효과의 크기와 빈도를 적절히 조절하여 경제 변동성 관리
2. **평판 곡선**: 평판 상승/하락 이벤트를 균형 있게 배치하여 자연스러운 곡선 형성
3. **이벤트 분포**: 특정 이벤트가 과도하게 발생하지 않도록 확률 조정
4. **고객 성장**: 고객 수가 지속적으로 증가하되 과도하지 않도록 조정
5. **직원 사기**: 직원 사기 변동이 급격하지 않도록 효과 크기 조절

## 향후 개선 사항

1. **시각화 도구**: 메트릭 변화 및 밸런스 점수를 그래프로 시각화
2. **시나리오 테스트**: 특정 시나리오에 대한 집중 테스트 기능
3. **민감도 분석**: 이벤트 파라미터 변경에 따른 밸런스 영향 분석
4. **머신러닝 최적화**: 자동 밸런싱을 위한 머신러닝 알고리즘 적용
5. **실시간 모니터링**: 게임 내 밸런스 실시간 모니터링 도구 연동

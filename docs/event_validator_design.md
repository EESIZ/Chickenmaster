# 이벤트 검증기 설계 및 사용법

## 개요

이벤트 검증기(Event Validator)는 치킨집 경영 게임의 이벤트 데이터를 검증하고 품질을 평가하는 도구입니다. 이 문서는 검증기의 설계, 기능, 사용법을 설명합니다.

## 기능

이벤트 검증기는 다음과 같은 주요 기능을 제공합니다:

1. **스키마 검증**: TOML/JSON 파일의 이벤트 데이터가 정의된 스키마를 준수하는지 검증
2. **ID 유일성 검증**: 모든 이벤트 ID가 고유한지 확인
3. **DAG 안전성 검증**: 연쇄 이벤트 관계가 비순환적인지(DAG) 확인
4. **확률 및 쿨다운 범위 검증**: probability(0.0-1.0), cooldown(≥0) 등 값 범위 검증
5. **포뮬러 파싱 검증**: formula 문자열이 제한된 평가기에서 안전하게 파싱 가능한지 확인
6. **품질 메트릭 계산**: 다양성, 트레이드오프 명확성, 문화적 진정성, 재플레이 가치 등 평가

## 사용법

### 명령줄 인터페이스

```bash
# 단일 파일 검증
python -m dev_tools.event_validator --file path/to/events.toml

# 디렉토리 내 모든 파일 검증
python -m dev_tools.event_validator --dir path/to/events/directory

# 품질 메트릭 계산 포함
python -m dev_tools.event_validator --file path/to/events.toml --metrics
```

### 프로그래밍 방식 사용

```python
from dev_tools.event_validator import EventValidator
from pathlib import Path

# 검증기 초기화
validator = EventValidator()

# 단일 파일 검증
success = validator.validate_file(Path("path/to/events.toml"))
if not success:
    print("오류:", validator.errors)
    print("경고:", validator.warnings)

# 디렉토리 검증
success = validator.validate_directory(Path("path/to/events/directory"))

# 품질 메트릭 계산
events = [...] # 이벤트 데이터 리스트
metrics = validator.calculate_quality_metrics(events)
```

## 검증 항목

### 1. 이벤트 기본 구조

- **필수 필드**: id, type, effects
- **이벤트 타입**: RANDOM, THRESHOLD, SCHEDULED, CASCADE
- **타입별 필수 필드**:
  - RANDOM: probability
  - THRESHOLD/CASCADE: trigger
  - SCHEDULED: schedule

### 2. 트리거 검증

- **필수 필드**: metric, condition, value
- **조건 타입**: less_than, greater_than, equal

### 3. 효과 검증

- **필수 필드**: metric, formula
- **포뮬러 검증**: 안전한 수식 평가 가능 여부

### 4. 값 범위 검증

- probability: 0.0 ~ 1.0
- cooldown: ≥ 0
- schedule: > 0

## 품질 메트릭

### 1. 다양성 점수 (diversity_score)

카테고리 분포의 균등성을 Shannon Entropy 기반으로 측정합니다.
- **목표**: ≥ 0.8
- **계산 방식**: 카테고리별 이벤트 분포의 엔트로피를 정규화

### 2. 트레이드오프 명확성 (tradeoff_clarity)

각 선택지가 명확한 득실을 가지는지 평가합니다.
- **목표**: ≥ 0.9
- **계산 방식**: 긍정적 효과와 부정적 효과를 모두 가진 선택지의 비율

### 3. 문화적 진정성 (cultural_authenticity)

한국 치킨집 문화를 얼마나 잘 반영하는지 평가합니다.
- **목표**: ≥ 0.7
- **계산 방식**: 관련 키워드 매칭 비율

### 4. 재플레이 가치 (replayability)

조건 다양성과 확률 분포를 기반으로 재플레이 가치를 평가합니다.
- **목표**: ≥ 0.8
- **계산 방식**: 조건 다양성(50%)과 확률 분포(50%)의 가중 평균

## 실데이터 연동

이벤트 검증기는 다음과 같은 방식으로 실제 이벤트 데이터와 연동됩니다:

1. **파일 형식 지원**: TOML(작성용), JSON(런타임용) 두 가지 형식 모두 지원
2. **디렉토리 구조**: `/data/events/<category>/*.toml` 구조의 파일 검증
3. **검증 결과**: 오류 및 경고 메시지를 통해 문제점 식별
4. **품질 평가**: 메트릭 계산을 통한 콘텐츠 품질 정량화

## 반복 오류 방지

이벤트 데이터 작성 및 검증 시 다음 사항을 준수하여 반복 오류를 방지합니다:

1. **스키마 준수**: Event Schema Specification(v0.1)에 정의된 구조 준수
2. **ID 명명 규칙**: `<category>_<number>` 형식의 고유 ID 사용
3. **포뮬러 작성**: 안전한 수식만 사용 (`value` 변수, 기본 연산자, 퍼센트 표기법)
4. **트레이드오프 보장**: 모든 선택지는 득과 실을 모두 포함해야 함
5. **문화적 맥락**: 한국 치킨집 문화를 반영하는 키워드 포함

## 향후 개선 사항

1. **DAG 검증 강화**: 연쇄 이벤트의 순환 참조 방지 알고리즘 개선
2. **안전한 포뮬러 평가**: AST 기반 화이트리스트 노드 검사 구현
3. **유사도 검사**: fuzzywuzzy를 활용한 중복/유사 이벤트 필터링
4. **자동화된 테스트**: 이벤트 뱅크 전체에 대한 자동 검증 파이프라인
5. **시각화 도구**: 이벤트 관계 및 품질 메트릭 시각화

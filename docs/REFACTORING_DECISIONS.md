# 리팩토링 결정 사항

## 1. 복잡도 문제 해결 전략

### 1.1 문제 상황
현재 코드베이스에서 발견된 주요 복잡도 문제:
```python
PLR0911: Too many return statements (13 > 6)
PLR0912: Too many branches (21 > 12)
PLR0915: Too many statements (92 > 50)
```

### 1.2 영향 분석
1. 유지보수성 저하
   - 코드 이해도 감소
   - 버그 발생 위험 증가
   - 테스트 어려움

2. 확장성 제한
   - 새로운 기능 추가 어려움
   - 변경 사항 적용 시 위험도 증가

3. 테스트 커버리지 달성 어려움
   - 복잡한 분기로 인한 테스트 케이스 증가
   - 테스트 유지보수 비용 증가

### 1.3 해결 방안

#### 1.3.1 Strategy 패턴 도입
```python
# Before
def validate_event(self, event: dict) -> bool:
    if event["type"] == "A":
        # A 타입 검증 로직
    elif event["type"] == "B":
        # B 타입 검증 로직
    # ... 더 많은 조건문

# After
class EventValidator:
    def __init__(self):
        self.validators = {
            "A": ATypeValidator(),
            "B": BTypeValidator(),
        }
    
    def validate_event(self, event: dict) -> bool:
        validator = self.validators[event["type"]]
        return validator.validate(event)
```

#### 1.3.2 책임 분리
```python
# Before
def process_event(self, event: dict) -> bool:
    # 검증
    # 로깅
    # 상태 업데이트
    # 결과 반환

# After
class EventProcessor:
    def __init__(self, validator: EventValidator, logger: EventLogger):
        self.validator = validator
        self.logger = logger
        
    def process(self, event: dict) -> bool:
        if not self.validator.validate(event):
            return False
        
        self.logger.log_event(event)
        return True
```

#### 1.3.3 Builder 패턴 도입
```python
# Before
def create_event(self, data: dict) -> Event:
    event = Event()
    event.id = data["id"]
    event.type = data["type"]
    # ... 많은 속성 설정

# After
class EventBuilder:
    def __init__(self):
        self.event = Event()
    
    def with_id(self, id: str) -> EventBuilder:
        self.event.id = id
        return self
        
    def with_type(self, type: str) -> EventBuilder:
        self.event.type = type
        return self
        
    def build(self) -> Event:
        return self.event
```

### 1.4 구현 우선순위

1. 단계 1: 기반 구조 개선
   - Strategy 패턴 도입
   - 의존성 주입 구조 구축
   - 테스트 프레임워크 설정

2. 단계 2: 코드 분할
   - 큰 함수들을 작은 단위로 분할
   - 각 기능별 클래스 생성
   - 인터페이스 정의

3. 단계 3: 테스트 강화
   - 단위 테스트 작성
   - 통합 테스트 작성
   - 테스트 커버리지 확인

### 1.5 예상되는 개선 효과

1. 코드 품질
   - 복잡도 감소
   - 가독성 향상
   - 유지보수성 개선

2. 테스트 용이성
   - 단위 테스트 작성 용이
   - 테스트 커버리지 향상
   - 버그 발견 용이성 증가

3. 확장성
   - 새로운 기능 추가 용이
   - 변경 사항 적용 안전성 향상
   - 재사용성 증가

## 2. 구현 가이드라인

### 2.1 패턴 적용 규칙
1. Strategy 패턴
   - 조건문이 3개 이상일 때 고려
   - 각 전략은 단일 책임을 가질 것
   - 인터페이스를 통한 계약 정의

2. Builder 패턴
   - 객체 생성에 5개 이상의 파라미터가 필요할 때
   - 선택적 파라미터가 많은 경우
   - 객체 생성 과정에 검증이 필요한 경우

3. 의존성 주입
   - 모든 외부 의존성은 생성자를 통해 주입
   - 인터페이스를 통한 결합도 감소
   - 테스트를 위한 Mocking 용이성 확보

### 2.2 코드 구조화 원칙
1. 함수 크기
   - 최대 50줄 제한
   - 단일 책임 원칙 준수
   - 명확한 입/출력 정의

2. 클래스 구조
   - 관련 기능끼리 그룹화
   - 상속보다 컴포지션 선호
   - 인터페이스를 통한 계약 정의

3. 에러 처리
   - 예외는 의미있는 단위로 정의
   - 모든 예외는 문서화
   - 예외 처리는 호출자에게 위임

### 2.3 테스트 전략
1. 단위 테스트
   - 모든 public 메서드 테스트
   - 경계 조건 검증
   - 실패 케이스 포함

2. 통합 테스트
   - 주요 시나리오 검증
   - 외부 의존성 포함
   - 성능 임계값 검증 

# Refactoring Decisions: Ruff 린트 이슈 대응 내역

## 1. 무시한 Ruff 에러 및 사유

### (1) 타입 힌트 관련 (UP035, UP006, UP007)
- `typing.List`, `typing.Dict`, `typing.Set` → 내장 타입(`list`, `dict`, `set`)으로 변경 권고
- `Optional[X]` → `X | None`으로 변경 권고
- **사유:**
    - 본 프로젝트는 Python 3.9 이상을 기본 타겟으로 하지만, 하위 호환성(3.8 이하) 요구가 발생할 수 있음
    - 일부 외부 라이브러리/자동 생성 코드와의 호환성 문제 가능성
    - 따라서, 핵심 도메인/서비스 코드에서는 내장 타입으로 점진적 전환, 테스트/샘플/자동 생성 코드는 일단 무시

### (2) 테스트 코드 내 매직 넘버 (PLR2004)
- 테스트 코드에서만 사용되는 하드코딩 숫자
- **사유:**
    - 테스트의 가독성, 간결성, 빠른 작성/수정 편의성
    - 도메인/비즈니스 로직에서는 반드시 상수화, 테스트에서는 일단 허용

### (3) 미사용 임포트 (F401)
- 테스트 코드/개발 중 임시로 남아있는 임포트
- **사유:**
    - 개발 중에는 빠른 반복을 위해 임시로 허용, 최종 릴리즈 전 일괄 정리 예정

---

## 2. 반드시 수정한 Ruff 에러 및 사유

### (1) 도메인/비즈니스 로직의 매직 넘버 (PLR2004)
- 핵심 로직에서의 하드코딩 값은 모두 상수로 치환
- **사유:** 유지보수성, 밸런싱, 테스트 용이성 확보

### (2) 불필요한 변수/예외 처리 (F841, B017 등)
- 사용하지 않는 변수, 블라인드 Exception 등은 모두 제거/구체화
- **사유:** 코드 품질, 디버깅, 유지보수성 향상

### (3) 실제 실행/빌드 오류 유발 항목
- ImportError, TypeError 등은 즉시 수정
- **사유:** 정상적인 빌드/실행 보장

---

## 3. 추후 반드시 체크해야 할 부분

- Python 3.9 이상만 지원이 확정되면, 타입 힌트 관련 린트 경고(UP035, UP006, UP007)도 일괄 적용 필요
- 테스트 코드의 매직 넘버, 미사용 임포트 등은 릴리즈 전 일괄 정리 필요
- 린트/포매터 설정(`pyproject.toml`, `.ruff.toml` 등)과 실제 빌드/배포 환경의 호환성 재점검
- 자동 생성 코드/외부 라이브러리와의 호환성 이슈 발생 시 예외적으로 린트 규칙 비활성화 가능

---

## 다음 해야 할 작업(Next Steps)

1. **이벤트 시스템 통합 및 개선**
   - 이벤트 도메인 모델과 실제 이벤트 데이터 구조의 일관성 확보
   - 이벤트 효과 및 트리거 로직의 통합 테스트 강화
   - 이벤트/스토리텔러 시스템 간 인터페이스 명확화

2. **도메인 모델 구조 개선**
   - Metric, GameState 등 중복/불필요한 속성 정리
   - StoryContext, NarrativeResponse, StoryPattern 등 상호 참조 구조 명확화
   - 타입 힌트 및 불변성(immutability) 강화

3. **테스트 커버리지 확대 및 품질 향상**
   - 이벤트, 스토리텔러, 경제 시스템 등 주요 모듈 단위 테스트 추가
   - 통합 테스트 및 시나리오 기반 테스트 작성
   - 테스트 코드 내 매직 넘버 상수화 지속

4. **코드 품질 및 일관성 점검**
   - Ruff, Black 등 린터/포매터 적용 범위 확대
   - 불필요한 예외 처리, 변수, import 정리
   - Python 3.9+ 지원 확정 시 타입 힌트 개선(UP035 등)

5. **문서화 및 개발 가이드 보강**
   - 리팩토링/설계 결정 근거 추가
   - 주요 도메인/서비스 흐름 다이어그램화
   - 린트/테스트 정책 및 코드리뷰 가이드 명시

> 이 목록은 리팩토링 및 테스트 진행 상황에 따라 지속적으로 업데이트될 예정입니다.

---

> **이 문서는 린트/포매터 적용 및 코드 리팩토링 과정에서의 의사결정 근거와 추후 점검 사항을 기록합니다.** 
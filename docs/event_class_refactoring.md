# Event 클래스 통합 및 타입 일관성 개선 문서

## 개요

이 문서는 Chickmaster 프로젝트의 Event 클래스 구조 통합 및 타입 일관성 개선 작업에 대한 내용을 담고 있습니다. 코드베이스 내에 중복된 Event 클래스 정의로 인한 타입 오류와 속성 접근 불일치 문제를 해결하기 위한 리팩터링 작업을 수행했습니다.

## 문제 상황

코드베이스 내에 두 개의 서로 다른 Event 클래스가 존재했습니다:

1. **schema.Event** (src/events/schema.py)
   - 상세한 필드 구조 (id, type, category, name_ko, name_en, text_ko, text_en, effects, choices, probability, cooldown, tags, trigger)
   - 필드 검증 규칙 포함
   - 실제 이벤트 데이터 모델로 사용

2. **base.Event** (src/events/validators/base.py)
   - 단순화된 구조 (id, type, name_ko, name_en, text_ko, text_en)
   - 검증기 모듈에서 사용

이로 인해 다음과 같은 문제가 발생했습니다:
- 타입 불일치 오류
- 존재하지 않는 속성 접근 시도
- 코드 일관성 저하
- 유지보수 어려움

## 리팩터링 전략

1. **base.Event 제거 및 schema.Event로 통합**
   - validators/base.py에서 Event 클래스 정의 제거
   - schema.py에서 Event 클래스를 import하여 사용

2. **타입 어노테이션 일관성 확보**
   - 모든 코드에서 Event 타입 참조를 schema.Event로 통일
   - 테스트 코드의 타입 불일치 해결

3. **테스트 함수 반환 타입 어노테이션 추가**
   - 테스트 함수에 명시적 반환 타입(-> None) 추가

## 주요 변경 사항

1. **src/events/validators/base.py**
   - Event 클래스 정의 제거
   - schema.py에서 Event 클래스 import 추가

2. **src/events/validators/specific.py**
   - Event import 경로 변경 (base → schema)

3. **tests/test_validators.py**
   - 테스트 함수 반환 타입 어노테이션 추가 (-> None)

## 남은 이슈 및 향후 작업

현재 리팩터링으로 validators 모듈의 타입 일관성은 확보되었으나, 다음 이슈들이 여전히 남아 있습니다:

1. **models.py의 타입 오류**
   - float와 None 간 비교 연산 오류
   - "schedule" 속성 접근 오류

2. **engine.py의 타입 오류**
   - EventContainer와 list[Event] 간 타입 불일치
   - Path vs str 타입 불일치
   - "message", "last_fired" 속성 접근 오류

### 향후 권장 작업

1. **models.py 리팩터링**
   - None 체크 로직 추가로 float|None 연산 오류 해결
   - schema.Event에 맞게 속성 접근 코드 수정

2. **engine.py 리팩터링**
   - 타입 어노테이션 일관화
   - Path 객체 사용으로 통일
   - schema.Event에 맞게 속성 접근 코드 수정

## 결론

이번 리팩터링을 통해 Event 클래스 구조를 통합하고 validators 모듈의 타입 일관성을 확보했습니다. 이는 코드베이스의 구조적 품질을 향상시키는 첫 단계로, 향후 추가적인 리팩터링을 통해 전체 코드베이스의 타입 안전성을 확보할 수 있을 것입니다.

## 참고 사항

- 커밋 해시: 1a6b670
- 작업 일자: 2025년 5월 30일

# 테스트 실패 분석 및 우선순위

## 실패 케이스 요약

총 7개의 테스트 실패가 발생했으며, 다음과 같이 분류됩니다:

### 1. 반환 구조 불일치 (우선순위: 높음)
- **TestEventGenerator.test_generate_events_tradeoff**
  - 오류: `{'content': [...]}는 list 타입이 아님`
  - 원인: EventGenerator가 리스트 대신 딕셔너리 구조를 반환함
  - 영향: 이벤트 생성 파이프라인의 기본 기능 차단

### 2. 태그 카운트 불일치 (우선순위: 중간)
- **TestEventBankIndexer.test_integrate_events_tradeoff**
- **TestEventBankIndexer.test_process_noRightAnswer**
  - 오류: `1 != 2` (태그 카운트 불일치)
  - 원인: 태그 '테스트'가 2개 있을 것으로 기대하지만 실제로는 1개만 있음
  - 영향: 이벤트 뱅크 메타데이터 관리 기능 차단

### 3. 검증 기준 불일치 (우선순위: 중간)
- **TestEventValidator.test_validate_event_structure_tradeoff**
- **TestEventValidator.test_validate_trigger_uncertainty**
- **TestIntegrationPipeline.test_end_to_end_pipeline_tradeoff**
  - 오류: `False is not true` (검증 기대값 불일치)
  - 원인: 트리거 조건 검증 로직이 테스트 기대값과 다름
  - 영향: 이벤트 검증 파이프라인 기능 차단

### 4. 파일 생성 및 예외 처리 불일치 (우선순위: 낮음)
- **TestIntegrationPipeline.test_pipeline_resilience_uncertainty**
  - 오류: `False is not true` (파일 존재 확인 실패)
  - 원인: 손상된 JSON 처리 시 파일이 생성되지 않음
  - 영향: 예외 상황 처리 기능 차단

## 우선순위 설정 근거

1. **반환 구조 불일치 (높음)**: 
   - 이벤트 생성은 파이프라인의 시작점으로, 이 문제가 해결되지 않으면 다른 테스트도 실패할 가능성이 높음
   - 구조적 문제로 수정이 비교적 간단함

2. **태그 카운트 불일치 (중간)**:
   - 메타데이터 관리에 영향을 주지만 이벤트 생성/검증 자체는 차단하지 않음
   - 데이터 구조 이해가 필요하며 수정이 복잡할 수 있음

3. **검증 기준 불일치 (중간)**:
   - 이벤트 검증에 직접적인 영향을 주지만 이벤트 생성 자체는 차단하지 않음
   - 검증 로직 이해가 필요하며 수정이 복잡할 수 있음

4. **파일 생성 및 예외 처리 불일치 (낮음)**:
   - 예외 상황에만 영향을 주며 정상 흐름은 차단하지 않음
   - 예외 처리 로직 개선이 필요하며 수정이 비교적 복잡함

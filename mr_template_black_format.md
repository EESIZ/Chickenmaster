# Merge Request: Black 포맷팅 적용 (CI 수정)

## Intent
CI 파이프라인의 black --check 단계에서 발생한 포맷팅 오류를 해결하여 dev 브랜치를 다시 Green 상태로 복구합니다.

black 포맷팅 규칙을 모든 코드에 일관되게 적용하여 코드 스타일 통일성을 확보하고, CI Gate 정책(코드가 black 포맷 규칙을 어기면 merge 금지)을 준수합니다.

## Mission
1. black 포맷팅 도구를 전체 코드베이스에 적용
   - src/economy/engine.py
   - src/economy/models.py
   - src/metrics/tracker.py
   - tests/test_economy.py

2. 포맷팅 후 품질 검증
   - ruff check로 0 error 확인
   - pytest로 모든 테스트 통과 확인
   - 코드 커버리지 ≥ 80% 유지 확인

3. 변경사항 커밋 및 푸시
   - 커밋 메시지: "style: apply black formatting (ci)"
   - 기능 로직 변경 없이 포맷만 자동 정렬

## End State
- black --check 검사 통과
- CI 파이프라인 Green 상태 복구
- dev 브랜치가 다시 기준 라인으로 설정됨
- 모든 테스트 11개 통과
- 코드 커버리지 90% 유지

## Constraints
- 코드 내용/기능 변경 없이 포맷만 자동 정렬
- 게임 철학 키워드(tradeoff_, uncertainty_, noRightAnswer) 유지
- "불확실성 ≠ 불합리한 음수" 주석 유지
- 모든 테스트 케이스 유지 및 통과

## Tech
- Python 3.12 기반 개발
- black 포맷팅 도구 (자동 PEP 8 스타일 적용)
- ruff 린터 (코드 품질 검사)
- pytest + 커버리지 측정 (테스트 및 품질 검증)

## Validation
- black --check 검사 통과 확인
- ruff 린트 오류 0건 확인
- 모든 테스트 11개 통과
- 코드 커버리지 90% 달성 (요구사항 80% 초과)
- 기능 로직 변경 없음 확인

# Merge Request: Black 포맷팅 적용 (models.py)

## Intent
CI 파이프라인의 black --check 단계에서 발생한 src/economy/models.py 포맷팅 오류를 해결하여 dev 브랜치를 다시 Green 상태로 복구합니다.

이전 fix/black-format 브랜치에서 대부분의 파일은 포맷팅되었으나, models.py 한 파일이 누락되어 CI 파이프라인이 계속 실패하는 상황을 해결합니다.

## Mission
1. src/economy/models.py 파일에 black 포맷팅 도구 적용
2. 미사용 import에 # noqa: F401 주석 추가로 ruff 오류 해결
3. 포맷팅 후 품질 검증
   - ruff check로 0 error 확인
   - pytest로 모든 테스트 통과 확인
   - 코드 커버리지 ≥ 80% 유지 확인

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
- 향후 pre-commit 훅에 black --quiet 추가 고려

## Validation
- black --check 검사 통과 확인
- ruff 린트 오류 0건 확인
- 모든 테스트 11개 통과
- 코드 커버리지 90% 달성 (요구사항 80% 초과)
- 기능 로직 변경 없음 확인

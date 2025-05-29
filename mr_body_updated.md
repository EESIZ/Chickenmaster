# MR 본문 업데이트

## Intent
"정답 없는 삶을 압축 체험"하는 서사형 경영 게임 'Chicken-RNG'의 기초 문서와 인터페이스를 정의합니다. 이 MR은 게임의 핵심 철학(정답 없음, 트레이드오프, 불확실성)을 명확히 하고, 향후 개발될 모든 모듈의 기반이 될 문서와 스키마를 제공합니다.

## Mission
M-0 태스크의 목표는 다음과 같습니다:
1. 게임 규칙 문서 작성 (/docs/rules.md)
2. 모듈 간 인터페이스 정의 (/docs/interface_overview.md)
3. 지표 Enum과 상수 정의 (schema.py)
4. CI 파이프라인 스켈레톤 구성 (.gitlab-ci.yml)
5. 트레이드오프 예시 테스트 구현 (tests/test_tradeoff_example.py)

## End State
이 MR이 병합되면 다음과 같은 상태가 됩니다:
- 게임의 핵심 철학과 규칙이 명확하게 문서화됨
- 모듈 간 데이터 교환 형식과 인터페이스가 정의됨
- 모든 모듈이 공통으로 사용할 지표와 상수가 schema.py에 중앙화됨
- CI 파이프라인이 구성되어 코드 품질과 테스트를 자동으로 검증함
- "가격을 내리면 직원 피로가 오른다"는 트레이드오프 예시가 테스트로 구현됨
- CI Gate 정상화 완료

## Constraints
- Python 3.12 기반 개발
- 표준 라이브러리 + numpy, pydantic 이내 사용
- 모든 변수, 함수, 테스트 이름에 tradeoff_, uncertainty_, noRightAnswer 등 철학적 키워드 반영
- 경제 함수에 재고·현금 음수 방지 로직 및 "불확실성 ≠ 불합리한 음수" 주석 포함
- 하드코딩 지양, 모든 상수는 schema.py에서 중앙 관리

## Tech
- Python 3.12
- 코드 품질 도구: black, ruff, mypy --strict
- 테스트: pytest, pytest-cov
- CI: GitLab CI (.gitlab-ci.yml)
- 문서: Markdown

## Validation
- CI Green (black, ruff, mypy, pytest 모두 통과)
- 테스트 커버리지 ≥ 80%
- 모든 문서가 게임의 핵심 철학을 명확히 전달
- schema.py가 모든 지표와 상수를 중앙화하여 관리
- 트레이드오프 예시 테스트가 게임의 핵심 메커니즘을 검증

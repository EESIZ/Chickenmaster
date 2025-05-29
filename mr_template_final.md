# Merge Request: 경제 엔진 및 린트 정리 병합 (M-1)

## Intent
dev 브랜치를 완전한 M-1 상태(경제 엔진 + Ruff 정리 완료)로 만들고, 이후 작업의 기준을 다시 Green으로 고정합니다.

feature/economy-engine 브랜치의 코어 경제 코드와 테스트를 병합하고, fix/ruff-unused 브랜치의 불필요 import/변수 제거 작업을 통합하여 CI 파이프라인을 Green 상태로 유지합니다.

## Mission
1. feature/economy-engine 브랜치 병합
   - 경제 엔진 코어 로직 (수요 계산, 이익 계산, 트레이드오프 적용)
   - 지표 추적 시스템 (MetricsTracker)
   - 경제 설정 파일 (economy_config.json)
   - 경제 엔진 명세서 (economy_spec.md)
   - 테스트 케이스 (정상 및 엣지 케이스)

2. fix/ruff-unused 브랜치 병합
   - 불필요한 import 및 변수 제거
   - 향후 사용 예정 코드에 주석 추가
   - 코드 품질 개선

3. 품질 검증
   - Ruff 린트 오류 0건
   - 모든 테스트 통과
   - 코드 커버리지 ≥ 80% 유지

## End State
- dev 파이프라인 Green 상태
- src/ 디렉토리 포함 ZIP 아카이브 정상 생성
- 모든 테스트 통과 (11개 테스트)
- 코드 커버리지 90% 달성
- dev 기준으로 후속 MR(연구 슬롯·Event DSL) 작업 안전 시작 가능

## Constraints
- 기능 로직 변경 없이 병합 및 품질 개선만 수행
- 게임 철학 키워드(tradeoff_, uncertainty_, noRightAnswer) 유지
- "불확실성 ≠ 불합리한 음수" 주석 유지
- 모든 테스트 케이스 유지 및 통과

## Tech
- Python 3.12 기반 개발
- 경제 엔진 모듈 구조:
  - src/economy/models.py: 수요 계산, 경제 모델 함수
  - src/economy/engine.py: 이익 계산, 트레이드오프 적용
  - src/metrics/tracker.py: 지표 추적 시스템
- 테스트 프레임워크: pytest + 커버리지 측정
- 코드 품질 도구: black, ruff, mypy

## Validation
- GitLab Pipeline ✅ Green
- Ruff 린트 오류 0건 확인
- 모든 테스트 11개 통과
- 코드 커버리지 90% 달성 (요구사항 80% 초과)
- ZIP 아카이브에 src/economy/, src/metrics/ 포함 확인
- 모든 파일 구조 및 디렉토리 무결성 검증 완료

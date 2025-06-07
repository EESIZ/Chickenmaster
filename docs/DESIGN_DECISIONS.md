# 설계 결정 사항

## 코드 구조 및 스타일

### 1. 동적 Import 경로 설정
**파일**: `scripts/mass_event_generation.py`

**결정사항**: 
- `sys.path`를 수정한 후에 `dev_tools` 모듈을 import하는 구조 유지
- Ruff의 E402(모듈 레벨 import가 파일 최상단에 없음) 경고 무시

**이유**:
- 스크립트가 프로젝트 루트 디렉토리의 위치를 동적으로 찾아 `dev_tools` 모듈을 import해야 함
- 이는 스크립트가 다양한 위치에서 실행될 수 있도록 하기 위한 의도적인 설계
- `sys.path.insert(0, str(project_root))` 이후에 import 문이 위치해야 정상적으로 동작

**처리방법**:
- `ruff.toml` 설정 파일에서 해당 파일의 E402 경고를 무시하도록 설정
- 이 설계 결정을 문서화하여 향후 유지보수 시 혼란 방지

### 관련 파일
- `scripts/mass_event_generation.py`: 동적 import 구현
- `ruff.toml`: 린터 설정
- `docs/DESIGN_DECISIONS.md`: 설계 결정 문서화

### 2. 매직 넘버 상수화 및 중앙 관리 (PLR2004)
**파일**: `game_constants.py` 및 전체 프로젝트

**결정사항**:
- 모든 매직 넘버(하드코딩된 숫자 값)를 `game_constants.py`에 중앙 관리되는 상수로 정의
- 관련 상수는 Frozen Dataclass 패턴을 사용하여 그룹화
- 테스트 코드의 매직 넘버도 상수화하여 일관성 유지

**이유**:
- 하드코딩된 매직 넘버는 코드 가독성과 유지보수성을 저해함
- 동일한 값이 여러 곳에서 사용될 때 일관성 문제 발생 가능
- 값 변경 시 모든 위치를 찾아 수정해야 하는 번거로움과 오류 가능성
- 숫자의 의미를 명확히 하여 코드 이해도 향상
- 게임의 핵심 철학인 '불확실성'과 '트레이드오프'를 코드 구조에도 반영

**구현 방식**:
```python
# game_constants.py

# 단일 상수 정의
FLOAT_EPSILON = 0.001
SCORE_THRESHOLD_HIGH = 0.7
SCORE_THRESHOLD_MEDIUM = 0.5

# Frozen Dataclass 패턴으로 관련 상수 그룹화
from dataclasses import dataclass

@dataclass(frozen=True)
class ProbabilityConstants:
    """확률 관련 상수를 그룹화한 Frozen Dataclass"""
    RANDOM_THRESHOLD: float = 0.5
    EVENT_CHANCE_HIGH: float = 0.7
    EVENT_CHANCE_MEDIUM: float = 0.5
    EVENT_CHANCE_LOW: float = 0.3

@dataclass(frozen=True)
class TestConstants:
    """테스트 관련 상수를 그룹화한 Frozen Dataclass"""
    MIN_CASCADE_EVENTS: int = 3
    EXPECTED_EVENTS: int = 2
    METRICS_HISTORY_LENGTH: int = 5
    POSSIBLE_OUTCOME: int = 3
```

**기대 효과**:
- 코드 가독성 향상: 의미 있는 상수명으로 코드 이해도 증가
- 유지보수성 개선: 값 변경 시 한 곳만 수정하면 전체 적용
- 버그 감소: 하드코딩된 매직 넘버 제거로 오류 가능성 감소
- 일관성 유지: 동일한 값이 여러 곳에서 사용될 때 일관성 보장
- 코드 품질 향상: Ruff PLR2004 린트 경고 해소

**관련 파일**:
- `game_constants.py`: 중앙 상수 정의
- `src/metrics/modifiers.py`: 상수 사용 예시
- `src/events/engine.py`: 상수 사용 예시
- `tests/test_events.py`: 테스트 코드 상수 사용 예시
- `tests/test_placeholder.py`: 테스트 코드 상수 사용 예시

**참고 사항**:
- 이 설계 결정은 [리팩토링 가이드라인](REFACTORING_GUIDELINES.md)의 매직 넘버 처리 원칙과 연계됨
- 모든 개발자는 새로운 코드 작성 시 매직 넘버 대신 상수를 사용해야 함

# 개발자 온보딩 가이드

> 🎯 **목표**: 새로운 개발자가 30분 내에 프로젝트를 이해하고 첫 번째 기여를 할 수 있도록 돕습니다.

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [개발 환경 구성](#개발-환경-구성)
3. [코드베이스 이해](#코드베이스-이해)
4. [첫 번째 실행](#첫-번째-실행)
5. [개발 워크플로우](#개발-워크플로우)
6. [코드 스타일 가이드](#코드-스타일-가이드)
7. [테스트 실행](#테스트-실행)
8. [다음 단계](#다음-단계)

---

## 🎮 프로젝트 개요

**Chicken-RNG**는 "정답 없는 삶을 압축 체험"하는 치킨집 경영 시뮬레이션 게임입니다.

### 핵심 철학
- **정답 없음**: 모든 선택은 득과 실을 동시에 가져옵니다
- **트레이드오프**: 한 지표를 올리면 다른 지표는 내려갑니다  
- **불확실성**: 예측 불가능한 이벤트가 게임을 좌우합니다

### 핵심 지표
- 💰 **돈**: 사업 운영 자금
- 🏆 **평판**: 가게의 사회적 평가
- 😊 **행복**: 사장의 정신적 만족도
- 😰 **고통**: 사장의 정신적 스트레스

---

## 🛠️ 개발 환경 구성

### 1. 필수 요구사항
```bash
# Python 3.12+ 설치 확인
python --version

# Git 설치 확인
git --version
```

### 2. 프로젝트 클론 및 설정
```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd Chickenmaster-main

# 2. 가상환경 생성 (권장)
python -m venv venv

# 3. 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. pre-commit 훅 설치
pre-commit install
```

### 3. IDE 설정 (VSCode 권장)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

---

## 🏗️ 코드베이스 이해

### 아키텍처 개요
```
Chicken-RNG/
├── src/                    # 메인 소스 코드
│   ├── core/              # 🏛️ 핵심 도메인 (비즈니스 로직)
│   │   ├── domain/        #     엔티티 & 값 객체
│   │   └── ports/         #     인터페이스 정의
│   ├── adapters/          # 🔌 외부 시스템 연결
│   │   ├── services/      #     서비스 구현체
│   │   └── storage/       #     저장소 구현체
│   ├── application/       # 🎭 응용 서비스
│   ├── economy/           # 💰 경제 시스템
│   ├── events/            # 🎲 이벤트 엔진
│   └── metrics/           # 📊 지표 관리
├── tests/                 # 테스트 코드
├── docs/                  # 📚 문서
├── scripts/               # 🔧 유틸리티 스크립트
└── dev_tools/             # 🛠️ 개발 도구
```

### 모듈별 역할

| 모듈 | 역할 | 핵심 파일 |
|------|------|-----------|
| `core/domain` | 게임 상태, 메트릭 등 핵심 엔티티 | `game_state.py`, `metrics.py` |
| `economy` | 수익 계산, 트레이드오프 적용 | `engine.py`, `models.py` |
| `events` | 랜덤 이벤트 생성 및 적용 | `engine.py`, `models.py` |
| `metrics` | 지표 추적 및 계산 | `tracker.py` |

---

## 🚀 첫 번째 실행

### 1. 테스트 실행으로 환경 확인
```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=src --cov-report=html

# 특정 모듈 테스트
pytest tests/test_economy.py -v
```

### 2. 코드 품질 검사
```bash
# 린팅 검사
ruff check src/

# 타입 검사
mypy src/

# 포매팅 검사
black --check src/

# 전체 품질 검사
pre-commit run --all-files
```

### 3. 게임 시뮬레이션 실행
```bash
# 개발 도구로 게임 시뮬레이션
python -m dev_tools.balance_simulator

# 이벤트 생성기 실행
python scripts/mass_event_generation.py
```

---

## 🔄 개발 워크플로우

### 1. 새 기능 개발 프로세스
```bash
# 1. 새 브랜치 생성
git checkout -b feature/new-feature

# 2. 개발 진행
# ... 코드 작성 ...

# 3. 테스트 작성 및 실행
pytest tests/test_new_feature.py

# 4. 코드 품질 검사
pre-commit run --all-files

# 5. 커밋 및 푸시
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 2. 커밋 메시지 규칙
```
타입(범위): 간단한 설명

자세한 설명 (필요시)

타입:
- feat: 새 기능
- fix: 버그 수정  
- docs: 문서 변경
- test: 테스트 추가/수정
- refactor: 리팩토링
```

### 3. 코드 리뷰 체크리스트
- [ ] 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상 유지
- [ ] 타입 힌트 100% 적용
- [ ] 독스트링 작성
- [ ] 불변 객체 원칙 준수

---

## 📝 코드 스타일 가이드

### 1. 매직 넘버 처리 원칙 (PLR2004)

매직 넘버는 코드 가독성과 유지보수성을 저해합니다. Chicken-RNG 프로젝트에서는 다음 원칙을 따릅니다:

#### 매직 넘버 처리 규칙
- 모든 매직 넘버는 `game_constants.py`에 중앙 관리되는 상수로 정의
- 의미 있는 상수명 사용 (예: `FLOAT_EPSILON`, `SCORE_THRESHOLD_HIGH`)
- 관련 상수는 Frozen Dataclass 패턴으로 그룹화

#### 예시: 매직 넘버 대신 상수 사용
```python
# ❌ 잘못된 예
if random_value < 0.5:
    trigger_event()
    
if score >= 0.7:
    award_achievement()

# ✅ 올바른 예 - 중앙 관리 상수 사용
from game_constants import ProbabilityConstants, SCORE_THRESHOLD_HIGH

if random_value < ProbabilityConstants.RANDOM_THRESHOLD:
    trigger_event()
    
if score >= SCORE_THRESHOLD_HIGH:
    award_achievement()
```

#### 예시: Frozen Dataclass 패턴
```python
# game_constants.py
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
```

### 2. 변수 및 함수 명명 규칙

#### 게임 철학 키워드 사용
변수, 함수, 테스트 이름에 게임 철학을 반영하는 키워드를 사용합니다:
- `tradeoff`: 트레이드오프 관계를 나타내는 요소
- `uncertainty`: 불확실성 요소
- `noRightAnswer`: 정답이 없는 선택지

```python
# 예시
def calculate_tradeoff_effect(choice_id: str) -> dict[Metric, float]:
    """선택에 따른 트레이드오프 효과를 계산합니다."""
    
def apply_uncertainty_factor(base_value: float, day: int) -> float:
    """불확실성 요소를 적용합니다."""
    
class NoRightAnswerChoice:
    """정답이 없는 선택지를 표현하는 클래스."""
```

### 3. 코드 포맷팅 및 문서화

#### 독스트링 형식
```python
def function_name(param1: type, param2: type) -> return_type:
    """함수의 주요 목적을 한 문장으로 설명합니다.
    
    더 자세한 설명이 필요한 경우 여기에 작성합니다.
    여러 줄에 걸쳐 작성할 수 있습니다.
    
    Args:
        param1: 첫 번째 매개변수 설명
        param2: 두 번째 매개변수 설명
        
    Returns:
        반환값에 대한 설명
        
    Raises:
        ValueError: 예외 발생 조건 설명
    """
```

---

## 🧪 테스트 실행

### 테스트 명령어 모음
```bash
# 기본 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 테스트 파일
pytest tests/test_economy.py

# 특정 테스트 함수
pytest tests/test_economy.py::test_profit_calculation

# 커버리지 리포트 생성
pytest --cov=src --cov-report=html
# 결과: htmlcov/index.html

# 실패한 테스트만 재실행
pytest --lf

# 느린 테스트 10개 표시
pytest --durations=10
```

### 테스트 작성 가이드
```python
# tests/test_example.py
import pytest
from src.core.domain.game_state import GameState
from game_constants import TEST_POSSIBLE_OUTCOME

def test_game_state_immutable():
    """게임 상태가 불변인지 확인"""
    state = GameState(money=100, reputation=50, happiness=60, pain=40, day=1)
    
    # 효과 적용 시 새 객체 생성
    new_state = state.apply_effects({'money': 10})
    
    assert state.money == 100  # 원본 불변
    assert new_state.money == 110  # 새 객체 변경
    
def test_uncertainty_principle():
    """불확실성 원칙을 검증하는 테스트"""
    expected_range = range(1, 7)  # 주사위 눈금 범위
    possible_outcomes = set(expected_range)
    
    # 매직 넘버 대신 상수 사용
    assert TEST_POSSIBLE_OUTCOME in possible_outcomes
```

---

## 📈 다음 단계

### 1. 심화 학습 자료
- [📋 게임 규칙](rules.md) - 게임의 상세 규칙
- [🏗️ 아키텍처 명세](architecture_specification.md) - 기술적 구조
- [🔧 API 문서](API.md) - 모듈별 사용법
- [📝 기여 가이드](CONTRIBUTING.md) - 코드 기여 방법
- [🔄 리팩토링 가이드라인](REFACTORING_GUIDELINES.md) - 코드 개선 방법

### 2. 추천 첫 기여 항목
- [ ] 기존 테스트에 추가 케이스 작성
- [ ] 독스트링 개선
- [ ] 타입 힌트 보완
- [ ] 문서 오타 수정
- [ ] 매직 넘버를 상수로 교체

### 3. 고급 개발 도구
```bash
# 성능 프로파일링
python -m cProfile -o profile.stats script.py

# 메모리 사용량 분석
pip install memory-profiler
python -m memory_profiler script.py

# 코드 복잡도 분석
pip install radon
radon cc src/
```

---

## 🆘 도움이 필요할 때

### 1. 자주 묻는 질문
**Q: 테스트가 실패할 때?**
```bash
# 1. 의존성 재설치
pip install -r requirements-dev.txt

# 2. 캐시 클리어
pytest --cache-clear

# 3. 가상환경 재생성
```

**Q: 타입 검사 오류?**
```bash
# mypy 캐시 클리어
mypy --cache-clear

# 특정 파일만 검사
mypy src/specific_file.py
```

**Q: PLR2004 매직 넘버 린트 오류?**
```bash
# 매직 넘버 검사만 실행
ruff check . --select=PLR2004

# 매직 넘버를 game_constants.py에 상수로 추가하고 임포트하여 사용
```

### 2. 문제 해결 순서
1. **에러 메시지 확인** - 로그를 자세히 읽어보세요
2. **관련 테스트 실행** - 해당 모듈의 테스트를 실행해보세요
3. **문서 참조** - `docs/` 디렉토리의 관련 문서를 확인하세요
4. **이슈 생성** - 문제가 지속되면 GitHub 이슈를 생성하세요

---

## ✅ 체크리스트

온보딩 완료 확인:
- [ ] 개발 환경 구성 완료
- [ ] 모든 테스트 통과 확인
- [ ] 코드 품질 검사 통과
- [ ] 첫 번째 커밋 완료
- [ ] 아키텍처 이해
- [ ] 게임 규칙 숙지
- [ ] 매직 넘버 처리 원칙 이해

**축하합니다! 이제 Chicken-RNG 개발자입니다! 🎉**

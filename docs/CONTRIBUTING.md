# 기여 가이드 (Contributing Guide)

> 🤝 **환영합니다!** Chicken-RNG 프로젝트에 기여해 주셔서 감사합니다. 이 가이드는 여러분의 기여를 효과적으로 만들기 위한 지침을 제공합니다.

## 📋 목차

1. [기여 방법](#기여-방법)
2. [개발 환경 설정](#개발-환경-설정)
3. [코드 기여 프로세스](#코드-기여-프로세스)
4. [코딩 표준](#코딩-표준)
5. [테스트 가이드라인](#테스트-가이드라인)
6. [문서화 가이드라인](#문서화-가이드라인)
7. [이슈 보고](#이슈-보고)
8. [코드 리뷰](#코드-리뷰)

---

## 🚀 기여 방법

### 기여할 수 있는 영역

#### 🐛 버그 수정
- 기존 이슈에서 버그 리포트 확인
- 재현 가능한 테스트 케이스 작성
- 근본 원인 분석 후 수정

#### ⭐ 새 기능 개발
- 게임 메커니즘 개선
- 새로운 이벤트 추가
- UI/UX 개선
- 성능 최적화

#### 📚 문서화
- API 문서 개선
- 사용 예제 추가
- 번역 (한국어 ↔ 영어)
- 아키텍처 설명 보완

#### 🧪 테스트
- 테스트 커버리지 확대
- 엣지 케이스 테스트 추가
- 성능 테스트 작성
- 통합 테스트 개선

### 첫 기여를 위한 추천 작업

**🟢 초급자용 (Good First Issue)**
- [ ] 타입 힌트 누락 부분 추가
- [ ] 독스트링 개선
- [ ] 테스트 케이스 추가
- [ ] 문서 오타 수정
- [ ] 코드 주석 개선

**🟡 중급자용**
- [ ] 새로운 이벤트 타입 구현
- [ ] 메트릭 계산 로직 개선
- [ ] 에러 처리 강화
- [ ] 설정 시스템 개선

**🔴 고급자용**
- [ ] 아키텍처 개선
- [ ] 성능 최적화
- [ ] 새로운 모듈 설계
- [ ] 복잡한 알고리즘 구현

---

## 🛠️ 개발 환경 설정

### 1. 기본 설정
[개발자 가이드](DEVELOPER_GUIDE.md)를 먼저 확인하시고, 다음 추가 설정을 진행하세요.

### 2. Fork 및 Clone
```bash
# 1. GitHub에서 프로젝트 Fork
# 2. 로컬에 Clone
git clone https://github.com/YOUR_USERNAME/Chickenmaster-main.git
cd Chickenmaster-main

# 3. Upstream 리모트 추가
git remote add upstream https://github.com/ORIGINAL_OWNER/Chickenmaster-main.git

# 4. 브랜치 확인
git branch -a
```

### 3. 개발 도구 설정
```bash
# pre-commit 훅 설치 (필수)
pre-commit install

# 개발 의존성 설치
pip install -r requirements-dev.txt

# 에디터 설정 확인
# VSCode 사용 시 .vscode/settings.json 확인
```

---

## 🔄 코드 기여 프로세스

### 1. 이슈 생성 또는 확인
```bash
# 새 기능의 경우 먼저 이슈로 논의
# 기존 이슈가 있다면 해당 이슈에 코멘트
```

### 2. 브랜치 생성
```bash
# feature 브랜치 생성
git checkout -b feature/add-new-event-type

# 버그 수정의 경우
git checkout -b fix/economy-calculation-bug

# 문서 개선의 경우
git checkout -b docs/improve-api-documentation
```

### 3. 개발 진행
```bash
# 개발 진행
# ... 코드 작성 ...

# 중간 커밋 (자주 커밋하는 것을 권장)
git add .
git commit -m "feat: add basic event type structure"

# 테스트 실행
pytest tests/

# 코드 품질 검사
pre-commit run --all-files
```

### 4. Pull Request 생성
```bash
# 최신 변경사항 동기화
git fetch upstream
git rebase upstream/main

# 브랜치 푸시
git push origin feature/add-new-event-type

# GitHub에서 Pull Request 생성
```

### 5. 브랜치 명명 규칙

| 타입 | 형식 | 예시 |
|------|------|------|
| 새 기능 | `feature/기능-설명` | `feature/add-insurance-system` |
| 버그 수정 | `fix/버그-설명` | `fix/reputation-calculation-error` |
| 문서 | `docs/문서-설명` | `docs/update-contributing-guide` |
| 리팩토링 | `refactor/리팩토링-설명` | `refactor/simplify-event-engine` |
| 테스트 | `test/테스트-설명` | `test/add-edge-case-coverage` |

---

## 📝 코딩 표준

### 1. Python 스타일 가이드
```python
# PEP 8 준수 (black으로 자동 포매팅)
# 타입 힌트 100% 적용
def calculate_profit(units_sold: int, price: float, cost: float) -> float:
    """수익을 계산합니다.
    
    Args:
        units_sold: 판매된 단위 수
        price: 단위당 가격
        cost: 단위당 비용
        
    Returns:
        계산된 수익
        
    Raises:
        ValueError: 음수 값이 입력된 경우
    """
    if units_sold < 0 or price < 0 or cost < 0:
        raise ValueError("음수 값은 허용되지 않습니다")
    
    return units_sold * (price - cost)
```

### 2. 아키텍처 원칙 준수
```python
# ✅ 올바른 도메인 객체 (불변)
@dataclass(frozen=True)
class Event:
    id: str
    name: str
    effects: Tuple[EventEffect, ...]  # 불변 컬렉션 사용

# ❌ 피해야 할 패턴 (가변)
class Event:
    def __init__(self):
        self.effects = []  # 가변 리스트
    
    def add_effect(self, effect):  # 객체 직접 수정
        self.effects.append(effect)
```

### 3. 의존성 규칙
```python
# ✅ 올바른 의존성 방향
# core/domain → 어떤 것에도 의존하지 않음
# adapters → core/domain에만 의존
# application → 모든 레이어에 의존 가능

# ❌ 금지된 의존성
# core/domain이 adapters나 application에 의존하면 안됨
```

### 4. 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 함수/변수 | snake_case | `calculate_daily_profit()` |
| 클래스 | PascalCase | `EventEngine` |
| 상수 | UPPER_SNAKE_CASE | `MAX_REPUTATION` |
| 모듈 | snake_case | `event_engine.py` |
| 패키지 | lowercase | `events` |

---

## 🧪 테스트 가이드라인

### 1. 테스트 작성 원칙
```python
# 테스트 함수명: test_기능_상황_예상결과
def test_game_state_apply_effects_with_valid_data_returns_new_state():
    """유효한 데이터로 효과 적용 시 새 상태가 반환되는지 확인"""
    # Given (준비)
    initial_state = GameState(money=100, reputation=50, happiness=60, pain=40, day=1)
    effects = {'money': 50, 'reputation': -10}
    
    # When (실행)
    new_state = initial_state.apply_effects(effects)
    
    # Then (검증)
    assert new_state.money == 150
    assert new_state.reputation == 40
    assert initial_state.money == 100  # 원본 불변 확인
```

### 2. 테스트 커버리지 요구사항
- **신규 코드**: 100% 커버리지 필수
- **전체 프로젝트**: 80% 이상 유지
- **핵심 도메인 로직**: 90% 이상

### 3. 테스트 실행
```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/test_events.py

# 커버리지 포함
pytest --cov=src --cov-report=html

# 실패한 테스트만 재실행
pytest --lf
```

### 4. 테스트 카테고리

#### 단위 테스트
```python
def test_metric_apply_delta_increases_value():
    """Metric.apply_delta가 값을 올바르게 증가시키는지 확인"""
    metric = Metric(name="money", value=100, min_value=0, max_value=1000)
    result = metric.apply_delta(50)
    assert result.value == 150
```

#### 통합 테스트
```python
def test_event_engine_processes_complete_event_cycle():
    """이벤트 엔진이 전체 이벤트 사이클을 올바르게 처리하는지 확인"""
    # Given: 게임 상태와 이벤트 엔진 설정
    # When: 이벤트 발생부터 효과 적용까지
    # Then: 최종 상태 검증
```

---

## 📚 문서화 가이드라인

### 1. 독스트링 작성
```python
def calculate_tradeoff_effects(
    primary_metric: str, 
    delta: int, 
    tradeoff_matrix: Dict[str, float]
) -> Dict[str, int]:
    """트레이드오프 효과를 계산합니다.
    
    게임의 핵심 철학인 "정답 없음" 원칙에 따라, 한 지표의 개선은
    다른 지표의 악화를 가져옵니다. 이 함수는 그러한 트레이드오프
    효과를 계산합니다.
    
    Args:
        primary_metric: 주요 변경 지표 (예: "money", "reputation")
        delta: 변경량 (양수는 증가, 음수는 감소)
        tradeoff_matrix: 지표간 트레이드오프 계수 매트릭스
        
    Returns:
        각 지표별 변경량을 담은 딕셔너리
        예: {"money": 100, "reputation": -20, "happiness": -10}
        
    Raises:
        KeyError: 존재하지 않는 지표가 입력된 경우
        ValueError: delta가 허용 범위를 벗어난 경우
        
    Examples:
        >>> effects = calculate_tradeoff_effects("money", 100, TRADEOFF_MATRIX)
        >>> print(effects)
        {"money": 100, "reputation": -30, "happiness": -10}
        
    Note:
        트레이드오프 계수는 게임 밸런스에 직접적인 영향을 미치므로
        변경 시 충분한 테스트가 필요합니다.
    """
```

### 2. README 기여
- 새 기능 추가 시 README의 기능 목록 업데이트
- 사용법이 변경된 경우 예제 코드 수정
- 설치 방법이나 요구사항 변경 시 문서 업데이트

### 3. API 문서 기여
- 새 공개 함수/클래스 추가 시 [API.md](API.md) 업데이트
- 사용 예제 추가
- 매개변수와 반환값 설명 보완

---

## 🐛 이슈 보고

### 1. 버그 리포트 템플릿
```markdown
## 버그 설명
간단하고 명확한 버그 설명

## 재현 단계
1. '...' 을 클릭
2. '...' 로 스크롤
3. '...' 을 확인
4. 오류 발생 확인

## 예상 동작
정상적으로 동작해야 하는 내용

## 실제 동작
실제로 발생한 현상

## 환경 정보
- OS: [예: Windows 10]
- Python 버전: [예: 3.12.0]
- 프로젝트 버전: [예: v0.4.0]

## 추가 컨텍스트
스크린샷, 로그, 또는 기타 관련 정보
```

### 2. 기능 요청 템플릿
```markdown
## 기능 요청 설명
원하는 기능에 대한 간단하고 명확한 설명

## 문제점
현재 상황에서 어떤 문제가 있는지 설명

## 제안하는 해결책
어떤 방식으로 해결하고 싶은지 설명

## 고려한 대안들
다른 해결 방법들에 대한 고려사항

## 추가 컨텍스트
기타 관련 정보나 스크린샷
```

---

## 👀 코드 리뷰

### 1. Pull Request 체크리스트

**작성자 체크리스트**
- [ ] 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상 유지
- [ ] pre-commit 훅 통과
- [ ] 관련 문서 업데이트
- [ ] 의미있는 커밋 메시지 작성
- [ ] 아키텍처 원칙 준수
- [ ] 타입 힌트 100% 적용

**리뷰어 체크리스트**
- [ ] 코드 로직 정확성
- [ ] 아키텍처 패턴 준수
- [ ] 테스트 품질
- [ ] 문서화 완성도
- [ ] 성능 고려사항
- [ ] 보안 이슈 없음
- [ ] 게임 밸런스 영향 검토

### 2. 리뷰 가이드라인

**리뷰어를 위한 팁**
- 건설적이고 구체적인 피드백 제공
- 코드 뿐만 아니라 설계 관점에서도 검토
- 칭찬과 개선점을 균형있게 언급
- 질문 형태로 토론 유도

**작성자를 위한 팁**
- 작은 단위로 PR 생성 (500줄 이하 권장)
- PR 설명에 변경 이유와 영향 범위 명시
- 리뷰 코멘트에 열린 마음으로 응답
- 필요시 추가 설명이나 테스트 제공

### 3. 커밋 메시지 규칙
```bash
# 형식: 타입(범위): 간단한 설명

# 타입들:
feat: 새 기능
fix: 버그 수정
docs: 문서 변경
style: 코드 포매팅 (기능 변경 없음)
refactor: 리팩토링
test: 테스트 추가/수정
chore: 빌드 과정이나 도구 변경

# 예시:
feat(events): add insurance event type
fix(economy): correct profit calculation for edge cases
docs(api): add examples for EventEngine usage
test(metrics): add edge case tests for metric bounds
```

---

## 🎉 기여 인정

### 기여자 목록
모든 기여자는 README.md의 Contributors 섹션에 기록됩니다.

### 기여 유형별 라벨
- 🐛 버그 수정
- ⭐ 새 기능
- 📚 문서화
- 🧪 테스트
- 🎨 디자인
- 💡 아이디어
- 🔍 리뷰

### 특별한 기여 인정
- **월간 MVP**: 가장 많은 기여를 한 개발자
- **첫 기여자**: 첫 번째 PR이 머지된 개발자
- **문서화 챔피언**: 문서 개선에 크게 기여한 개발자

---

## 🤝 커뮤니티 가이드라인

### 행동 강령
- 서로를 존중하고 배려합니다
- 건설적인 피드백을 제공합니다
- 다양한 관점과 경험을 환영합니다
- 학습과 성장을 도우며 함께 발전합니다

### 소통 채널
- **GitHub Issues**: 버그 리포트, 기능 요청
- **GitHub Discussions**: 일반적인 질문, 아이디어 논의
- **Pull Request Comments**: 코드 관련 토론

### 질문하기
궁금한 점이 있으시면 언제든지 질문해주세요!
- GitHub Issues에 `question` 라벨로 질문
- 기존 문서를 먼저 확인 ([DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md), [API.md](API.md))
- 구체적이고 재현 가능한 예시 제공

---

**감사합니다! 🙏**

여러분의 기여가 Chicken-RNG를 더 나은 프로젝트로 만들어 갑니다. 
궁금한 점이 있으시면 언제든지 문의해주세요! 
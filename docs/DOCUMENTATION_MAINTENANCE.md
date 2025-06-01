# 📚 문서화 시스템 유지보수 가이드

> 🛠️ **목적**: Chicken-RNG 프로젝트의 문서화 시스템을 체계적으로 관리하고 유지보수하는 방법을 안내합니다.

## 📋 목차

1. [문서화 도우미 스크립트](#문서화-도우미-스크립트)
2. [ADR 관리](#adr-관리)
3. [문서 품질 관리](#문서-품질-관리)
4. [코드와 문서 일관성 유지](#코드와-문서-일관성-유지)
5. [정기 유지보수](#정기-유지보수)
6. [문제 해결](#문제-해결)

---

## 🔧 문서화 도우미 스크립트

### 스크립트 개요
`scripts/docs_helper.py`는 문서화 관련 작업을 자동화하는 도구입니다.

### 설치 및 설정
```bash
# 스크립트를 실행 가능하게 만들기 (Unix/Linux/macOS)
chmod +x scripts/docs_helper.py

# Python으로 직접 실행 (모든 OS)
python scripts/docs_helper.py --help
```

### 주요 명령어

#### 1. 새 ADR 생성
```bash
# 기본 사용법
python scripts/docs_helper.py new-adr "API 버전 관리 전략"

# 작성자 지정
python scripts/docs_helper.py new-adr "성능 최적화 방향" --author "김개발자 (kim@example.com)"
```

#### 2. 문서 링크 검증
```bash
# 모든 문서의 내부 링크 유효성 검사
python scripts/docs_helper.py validate-links
```

#### 3. 문서 통계 확인
```bash
# 문서 수, 라인 수, 단어 수 등 통계 출력
python scripts/docs_helper.py stats
```

#### 4. ADR 인덱스 업데이트
```bash
# ADR README.md의 목록 자동 업데이트
python scripts/docs_helper.py update-adr-index
```

#### 5. 전체 검증 실행
```bash
# 모든 검증을 한 번에 실행
python scripts/docs_helper.py check-all
```

---

## 📝 ADR 관리

### ADR 생성 워크플로우

1. **새 ADR 생성**
   ```bash
   python scripts/docs_helper.py new-adr "결정 제목" --author "작성자명"
   ```

2. **ADR 작성**
   - 생성된 템플릿 파일 편집
   - 모든 섹션 완성
   - 상태를 "Proposed"로 설정

3. **검토 및 승인**
   - 팀 리뷰 진행
   - 승인 후 상태를 "Accepted"로 변경

4. **인덱스 업데이트**
   ```bash
   python scripts/docs_helper.py update-adr-index
   ```

### ADR 상태 관리

| 상태 | 의미 | 사용 시점 |
|------|------|-----------|
| 🔄 Proposed | 제안됨 | 초안 작성 완료 시 |
| ✅ Accepted | 승인됨 | 팀 승인 완료 시 |
| ❌ Deprecated | 더 이상 사용 안함 | 정책 변경 시 |
| ♻️ Superseded | 다른 ADR로 대체됨 | 새 ADR로 교체 시 |

### ADR 작성 체크리스트

- [ ] **제목**: 결정 내용이 명확하게 드러나는 제목
- [ ] **맥락**: 왜 이 결정이 필요했는지 설명
- [ ] **옵션**: 고려된 모든 대안들 나열
- [ ] **결정**: 선택한 옵션과 그 이유
- [ ] **결과**: 예상되는 긍정적/부정적 영향
- [ ] **구현**: 구체적인 실행 계획
- [ ] **검증**: 성공 여부를 확인할 방법

---

## 🔍 문서 품질 관리

### 정기 검증 스크립트
```bash
# 매주 실행 권장
python scripts/docs_helper.py check-all
```

### 링크 검증 상세

#### 깨진 링크 발견 시 대응
1. **내부 링크 오타**: 경로나 파일명 수정
2. **파일 이동**: 링크 경로 업데이트 또는 리다이렉트 설정
3. **삭제된 파일**: 링크 제거 또는 대체 문서 링크

#### 외부 링크 관리
- 외부 링크는 자동 검증 대상이 아님
- 정기적으로 수동 확인 필요
- 중요한 외부 링크는 백업 또는 캐시 고려

### 문서 스타일 가이드

#### 제목 규칙
```markdown
# H1: 문서 제목 (각 문서당 1개)
## H2: 주요 섹션
### H3: 하위 섹션
#### H4: 세부 항목 (최대 H4까지 사용)
```

#### 링크 규칙
```markdown
# 올바른 예시
[개발자 가이드](DEVELOPER_GUIDE.md)
[API 문서](../docs/API.md)
[외부 자료](https://example.com)

# 피해야 할 예시
[링크](./docs/../DEVELOPER_GUIDE.md)  # 복잡한 상대경로
[링크](broken-file.md)  # 존재하지 않는 파일
```

#### 이미지 규칙
```markdown
# 이미지는 assets/ 디렉토리에 저장
![아키텍처 다이어그램](assets/architecture-diagram.png)

# 대체 텍스트 필수 제공
![설명적인 대체 텍스트](path/to/image.png)
```

---

## 📊 코드와 문서 일관성 유지

### 매직 넘버 상수화 문서화 원칙

#### 1. 상수 정의와 문서 동기화
- `game_constants.py`에 정의된 모든 상수는 관련 문서에도 정확히 반영되어야 함
- 상수 값 변경 시 문서도 함께 업데이트해야 함
- 문서 내 코드 예시에서도 하드코딩된 매직 넘버 대신 상수 사용

```python
# 문서 내 코드 예시 - 잘못된 방식
if score >= 0.7:  # 매직 넘버 사용
    award_bonus()

# 문서 내 코드 예시 - 올바른 방식
from game_constants import SCORE_THRESHOLD_HIGH
if score >= SCORE_THRESHOLD_HIGH:  # 상수 사용
    award_bonus()
```

#### 2. Frozen Dataclass 패턴 문서화
- 새로운 Frozen Dataclass 추가 시 다음 문서 업데이트 필수:
  1. `REFACTORING_GUIDELINES.md`: 패턴 사용 예시 추가
  2. `DEVELOPER_GUIDE.md`: 개발자 참고 사항 추가
  3. `DESIGN_DECISIONS.md`: 설계 결정 이유 추가

#### 3. 상수 관련 문서 검증 체크리스트
- [ ] `game_constants.py`의 모든 상수가 관련 문서에 정확히 반영됨
- [ ] 문서 내 코드 예시에서 매직 넘버 대신 상수 사용
- [ ] 상수 이름과 값이 코드와 문서 간에 일치함
- [ ] Frozen Dataclass 패턴이 문서에 명확히 설명됨

### 상수 관리 자동화 도구

#### 상수 추출 및 문서화 스크립트
```bash
# 상수 추출 및 문서 업데이트 도구 실행
python scripts/docs_helper.py update-constants-doc
```

이 스크립트는 다음 작업을 수행합니다:
1. `game_constants.py`에서 모든 상수와 Frozen Dataclass 추출
2. 관련 문서에서 상수 관련 섹션 식별
3. 최신 상수 정보로 문서 업데이트 제안
4. 불일치 항목 보고

#### 상수 사용 검증 도구
```bash
# 매직 넘버 사용 검사 (PLR2004)
python scripts/docs_helper.py check-magic-numbers

# 문서 내 코드 예시 검증
python scripts/docs_helper.py check-doc-code-examples
```

### 매직 넘버 관리 워크플로우

1. **상수 추가/수정**
   - `game_constants.py`에 상수 정의 또는 수정
   - 의미 있는 이름과 주석 추가

2. **코드 업데이트**
   - 관련 코드에서 매직 넘버를 상수로 교체
   - Ruff PLR2004 린트 검사로 확인

3. **문서 동기화**
   - 상수 추출 스크립트 실행
   - 문서 업데이트 제안 검토 및 적용

4. **검증**
   - 코드와 문서 일관성 검증
   - 테스트 실행으로 기능 확인

### 실제 적용 사례: PLR2004 매직 넘버 상수화

Chicken-RNG 프로젝트에서는 최근 PLR2004 매직 넘버 문제를 해결하기 위해 다음과 같은 작업을 수행했습니다:

1. `game_constants.py`에 모든 매직 넘버를 중앙 관리되는 상수로 정의
2. 관련 상수는 `ProbabilityConstants`, `TestConstants` 등의 Frozen Dataclass로 그룹화
3. 테스트 코드의 매직 넘버도 `TEST_MIN_CASCADE_EVENTS`, `TEST_EXPECTED_EVENTS` 등으로 상수화
4. 모든 관련 문서 업데이트로 코드와 문서 간 일관성 유지

이 과정은 다음 문서에 상세히 기록되어 있습니다:
- [리팩토링 가이드라인](REFACTORING_GUIDELINES.md): 매직 넘버 처리 원칙
- [개발자 가이드](DEVELOPER_GUIDE.md): 코드 스타일 가이드
- [설계 결정](DESIGN_DECISIONS.md): 매직 넘버 상수화 결정 배경

---

## 🔄 정기 유지보수

### 주간 작업 (매주 금요일)
```bash
# 1. 전체 문서 검증
python scripts/docs_helper.py check-all

# 2. 통계 확인 및 기록
python scripts/docs_helper.py stats

# 3. 문제 발견 시 즉시 수정
```

### 월간 작업 (매월 첫 주)
- [ ] 문서 인덱스 검토 및 업데이트
- [ ] 새로운 문서 카테고리 필요성 검토
- [ ] 오래된 문서 내용 업데이트
- [ ] 외부 링크 유효성 수동 확인
- [ ] 코드와 문서의 상수 정의 일관성 검증

### 분기별 작업 (3개월마다)
- [ ] 전체 문서 구조 재검토
- [ ] 중복 내용 통합
- [ ] 문서화 프로세스 개선
- [ ] 팀 피드백 수집 및 반영
- [ ] 매직 넘버 상수화 정책 준수 여부 전체 검토

### 릴리즈 시 작업
- [ ] 새 기능 관련 문서 업데이트
- [ ] API 변경사항 반영
- [ ] CHANGELOG.md 업데이트
- [ ] 버전 정보 갱신
- [ ] 새로 추가된 상수 문서화 확인

---

## 🚨 문제 해결

### 자주 발생하는 문제들

#### 1. 스크립트 실행 오류
```bash
# Python 경로 문제
python3 scripts/docs_helper.py check-all

# 권한 문제 (Unix/Linux/macOS)
chmod +x scripts/docs_helper.py
./scripts/docs_helper.py check-all

# 의존성 문제
pip install -r requirements.txt
```

#### 2. 한글 인코딩 문제
```bash
# Windows에서 한글 파일명 문제 시
chcp 65001  # UTF-8 코드페이지 설정
python scripts/docs_helper.py check-all
```

#### 3. Git 정보 없음 경고
```bash
# Git 저장소가 아니거나 Git이 설치되지 않은 경우
# 스크립트는 정상 동작하지만 'recent_updates' 정보는 표시되지 않음
```

#### 4. 매직 넘버 관련 문제
```bash
# PLR2004 린트 오류 발생 시
ruff check . --select=PLR2004  # 문제 파일 확인

# 상수 정의 후에도 오류가 계속되면
python scripts/docs_helper.py check-constants-usage  # 상수 사용 검증
```

### 문서 구조 문제

#### ADR 번호 중복
```bash
# 수동으로 파일명 변경 후
python scripts/docs_helper.py update-adr-index
```

#### 순환 링크 발견
1. 링크 체인 추적
2. 불필요한 링크 제거
3. 구조 단순화

#### 대용량 문서 파일
- 문서 분할 고려
- 이미지 최적화
- 외부 링크로 대체

---

## 📊 품질 지표

### 문서 품질 KPI
- **링크 유효성**: 100% (깨진 링크 0개)
- **ADR 완성도**: 모든 ADR이 완전한 템플릿 준수
- **문서 최신성**: 3개월 이내 업데이트된 문서 비율
- **커버리지**: 모든 모듈에 대한 문서 존재
- **코드-문서 일관성**: 상수 정의와 문서 설명 일치율 100%

### 자동화 수준
- **링크 검증**: 100% 자동화
- **ADR 인덱스**: 100% 자동화
- **통계 생성**: 100% 자동화
- **상수 추출**: 100% 자동화
- **내용 검토**: 수동 (분기별)

---

## 🎯 모범 사례

### Do's ✅
- **정기적인 검증**: 매주 `check-all` 실행
- **즉시 수정**: 문제 발견 시 즉시 해결
- **템플릿 준수**: ADR 작성 시 템플릿 완전 활용
- **명확한 제목**: 문서 제목에 목적과 범위 명시
- **상호 참조**: 관련 문서간 적절한 링크 연결
- **상수 사용**: 문서 내 코드 예시에서도 매직 넘버 대신 상수 사용
- **일관성 유지**: 코드와 문서 간 상수 정의 동기화

### Don'ts ❌
- **검증 생략**: 변경 후 검증 없이 커밋
- **외부 도구 의존**: 문서화를 외부 서비스에만 의존
- **중복 정보**: 같은 내용을 여러 문서에 중복 작성
- **깨진 링크 방치**: 발견된 문제를 나중으로 미루기
- **템플릿 무시**: ADR 작성 시 임의의 구조 사용
- **매직 넘버 하드코딩**: 문서 내 코드 예시에서도 매직 넘버 사용 금지
- **비동기화 상태**: 코드 상수 변경 시 문서 미업데이트

---

## 📞 도움 요청

### 문제 보고 시 포함할 정보
1. **실행 환경**: OS, Python 버전
2. **실행 명령어**: 정확한 명령어와 매개변수
3. **오류 메시지**: 전체 오류 출력
4. **재현 단계**: 문제 재현 방법
5. **예상 결과**: 원하는 동작

### 연락처
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **문서 담당자**: 프로젝트 메인테이너
- **팀 채널**: 일반적인 질문 및 토론

---

**📚 문서화는 코드만큼 중요합니다!**  
체계적인 관리로 프로젝트의 지속 가능성을 높이세요. 🚀

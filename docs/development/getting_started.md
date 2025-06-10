# 개발자 가이드

## 시작하기

### 요구사항
- Python 3.12+
- Git
- 가상 환경 관리자 (venv 권장)

### 개발 환경 설정

1. **저장소 클론**
```bash
git clone <repository-url>
cd Chickenmaster
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **pre-commit 설정**
```bash
pre-commit install
```

## 프로젝트 구조

```
src/
├── core/              # 핵심 도메인
│   ├── domain/        # 엔티티 & 값 객체
│   └── ports/         # 인터페이스
├── adapters/          # 어댑터
├── application/       # 응용 서비스
├── economy/          # 경제 시스템
├── events/           # 이벤트 엔진
└── metrics/          # 지표 관리
```

## 개발 워크플로우

### 1. 브랜치 전략
- `main`: 안정 버전
- `develop`: 개발 브랜치
- `feature/*`: 기능 개발
- `bugfix/*`: 버그 수정
- `release/*`: 릴리즈 준비

### 2. 커밋 메시지
```
type: 제목

본문

Footer
```

**타입**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 코드
- `chore`: 기타 변경사항

### 3. 코드 품질
- Black 포맷팅
- Ruff 린팅
- Mypy 타입 체크
- 테스트 커버리지 80% 이상

## 테스트

### 단위 테스트
```bash
pytest tests/unit
```

### 통합 테스트
```bash
pytest tests/integration
```

### 커버리지 확인
```bash
pytest --cov=src --cov-report=html
```

## 도구 사용법

### 1. 이벤트 생성기
```bash
python -m dev_tools.event_generator
```

### 2. 밸런스 시뮬레이터
```bash
python -m dev_tools.balance_simulator
```

### 3. 검증 도구
```bash
python -m dev_tools.event_validator
```

## 문제 해결

### 일반적인 문제

1. **의존성 충돌**
   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

2. **테스트 실패**
   ```bash
   pytest -v --tb=short
   ```

3. **타입 체크 오류**
   ```bash
   mypy src/
   ```

### 디버깅

1. **로깅 활성화**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **디버거 사용**
   ```python
   import pdb; pdb.set_trace()
   ```

## 배포

### 1. 버전 관리
- 시맨틱 버저닝 사용
- CHANGELOG.md 업데이트
- 태그 생성

### 2. 릴리즈 체크리스트
- [ ] 테스트 통과
- [ ] 문서 업데이트
- [ ] 변경 로그 작성
- [ ] 버전 태그 생성

### 3. 배포 명령어
```bash
python setup.py sdist bdist_wheel
```

## 모니터링

### 1. 로그 확인
```bash
tail -f logs/app.log
```

### 2. 성능 프로파일링
```bash
python -m cProfile -o output.prof script.py
```

## 참고 자료

### 문서
- [아키텍처 개요](../architecture/overview.md)
- [API 문서](api.md)
- [이벤트 시스템](../core/events/event_system.md)

### 외부 링크
- [Python 공식 문서](https://docs.python.org)
- [PyTest 문서](https://docs.pytest.org)
- [Mypy 문서](https://mypy.readthedocs.io) 
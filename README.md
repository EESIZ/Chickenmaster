# Chicken-RNG

> **CI Green + Coverage ≥ 80 % 통과 시에만 merge**

## 프로젝트 개요

Chicken-RNG는 "정답 없는 삶을 압축 체험"하게 하는 서사형 경영 게임입니다. 플레이어는 치킨집 사장이 되어 매일 중요한 결정을 내려야 하지만, 모든 선택은 득과 실을 동시에 가져옵니다.

## 핵심 철학

- **정답 없음**: 모든 선택은 득과 실을 동시에 가져옵니다
- **트레이드오프**: 한 지표를 올리면 다른 지표는 내려갑니다
- **불확실성**: 세상은 예측 불가능하며, 완벽한 대비는 불가능합니다
- **동적 밸런싱**: 모든 상수를 엑셀에서 실시간 조정 가능 🔥

## 🎨 시스템 구조 다이어그램

프로젝트의 복잡한 구조를 시각적으로 이해할 수 있는 Mermaid 다이어그램들을 제공합니다:

### 🏗️ 아키텍처 다이어그램
- **[📐 시스템 전체 구조도](./docs/diagrams/system_architecture.md)** - 헥사고널 아키텍처 전체 구조
- **[📊 엑셀 기반 동적 상수 관리](./docs/diagrams/excel_constants_system.md)** - 🔥 **매직넘버 박멸 시스템!**

### 🎮 게임 플레이 다이어그램  
- **[🎮 게임 플레이 순서도](./docs/diagrams/gameplay_flow.md)** - 전체 게임 진행 흐름

### 📊 더 많은 다이어그램
- **[🎨 다이어그램 모음](./docs/diagrams/README.md)** - 모든 다이어그램 인덱스

## 🚀 빠른 시작

### 새로운 개발자라면:
1. **[📚 문서 인덱스](/docs/INDEX.md)** - 모든 문서를 한 곳에서 찾기
2. **[🚀 개발자 가이드](/docs/DEVELOPER_GUIDE.md)** - 개발 환경 설정
3. **[🔧 API 문서](/docs/API.md)** - 코드 사용법
4. **[🤝 기여 가이드](/docs/CONTRIBUTING.md)** - 기여 방법

### 프로젝트에 기여하고 싶다면:
- [Good First Issues](https://github.com/your-repo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 확인
- [기여 가이드](/docs/CONTRIBUTING.md)를 먼저 읽어주세요

## 📚 주요 문서

### 📖 개발 문서
- [게임 규칙](/docs/rules.md) - 게임 메커니즘 및 규칙
- [아키텍처 명세](/docs/architecture_specification.md) - 헥사고널 아키텍처
- [ADR 목록](/docs/adr/README.md) - 아키텍처 결정 기록
- [인터페이스 개요](/docs/interface_overview.md) - 시스템 인터페이스

### 🔧 기술 가이드
- [API 문서](/docs/API.md) - 모듈별 사용법
- [개발자 가이드](/docs/DEVELOPER_GUIDE.md) - 환경 설정 및 워크플로우
- [기여 가이드](/docs/CONTRIBUTING.md) - 코드 기여 방법

### 📊 프로젝트 현황
- [품질 지표](/docs/quality_metrics.md) - 코드 품질 및 게임 밸런스
- [프로젝트 종합 리포트](/docs/project_comprehensive_report.md) - 전체 현황

## 🛠️ 개발 환경

### 요구사항
- **Python 3.12+**
- **테스트**: pytest
- **코드 품질**: black, ruff, mypy

### 빠른 설정
```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd Chickenmaster-main

# 2. 가상환경 및 의존성 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. pre-commit 설정
pre-commit install

# 4. 테스트 실행
pytest
```

상세한 설정 방법은 [개발자 가이드](/docs/DEVELOPER_GUIDE.md)를 참조하세요.

## 🏗️ 아키텍처

Chicken-RNG는 **헥사고널 아키텍처(Ports & Adapters)**를 기반으로 설계되었습니다.

```
src/
├── core/              # 🏛️ 핵심 도메인 (비즈니스 로직)
│   ├── domain/        #     엔티티 & 값 객체
│   └── ports/         #     인터페이스 정의
├── adapters/          # 🔌 외부 시스템 연결
├── application/       # 🎭 응용 서비스
├── economy/           # 💰 경제 시스템
├── events/            # 🎲 이벤트 엔진
└── metrics/           # 📊 지표 관리
```

**🔥 최신 업데이트**: 모든 게임 상수가 엑셀로 이전되어 **매직넘버가 완전히 박멸**되었습니다!

### 📊 엑셀 기반 동적 상수 관리 시스템
- **33개 하드코딩 상수** → **0개** (완전 박멸!)
- **실시간 게임 밸런싱**: Excel 수정 → `reload_all_constants()` → 즉시 반영
- **기획자 친화적**: 비개발자도 게임 밸런싱 가능

자세한 내용은 **[📊 엑셀 기반 동적 상수 관리](./docs/diagrams/excel_constants_system.md)**를 참조하세요.

## 📦 모듈 구조

| 모듈 | 설명 | 상태 |
|------|------|------|
| **M-0** | 규칙 문서 및 인터페이스 정의 | ✅ 완료 |
| **M-1** | 코어 경제 (가격, 수요, 원가, 재고, 손익 함수) | ✅ 완료 |
| **M-2** | 지표/게이지 (돈, 평판, 행복/고통 시소) | ✅ 완료 |
| **M-3** | 랜덤 이벤트 엔진 (사건 10종 + 후폭풍 큐) | ✅ 완료 |
| **M-4** | 스토리텔러 (Severity → M-3 호출) | ✅ 완료 |
| **M-Excel** | **엑셀 기반 동적 상수 관리** | ✅ **신규 완료!** |
| **M-5** | 헤지 시스템 (보험, 비자금, 장기계약) | 📋 계획됨 |
| **M-6** | 대시보드 목업 (재무, 평판, 재고, 게이지 UI) | 📋 계획됨 |

## 🧪 테스트 및 품질

- **테스트 커버리지**: 80% 이상 유지
- **코드 품질**: pre-commit 훅으로 자동 검사
- **타입 검사**: mypy strict 모드
- **CI/CD**: GitHub Actions (테스트 + 품질 검사)

```bash
# 테스트 실행
pytest --cov=src --cov-report=html

# 코드 품질 검사
pre-commit run --all-files

# 타입 검사
mypy src/
```

## 🎮 게임 철학

### 핵심 메트릭
- 💰 **돈**: 사업 운영 자금
- 🏆 **평판**: 가게의 사회적 평가  
- 😊 **행복**: 사장의 정신적 만족도
- 😰 **고통**: 사장의 정신적 스트레스

### 트레이드오프 시스템
모든 플레이어 행동은 득과 실을 동시에 가져옵니다:
- 가격 인상 → 수익 증가 + 평판 하락
- 품질 개선 → 평판 상승 + 비용 증가
- 직원 고용 → 효율성 증가 + 임금 부담

자세한 내용은 [게임 규칙](/docs/rules.md)을 참조하세요.

## 🔧 실시간 밸런싱 (신규!)

이제 게임을 종료하지 않고도 실시간으로 밸런싱이 가능합니다:

```python
# 1. Excel에서 상수값 수정
# 2. 게임에서 실행
import game_constants
game_constants.reload_all_constants()
# 3. 즉시 반영 완료!
```

**사용 가능한 상수들**:
- 게임 진행 설정 (MAX_ACTIONS_PER_DAY 등)
- 확률 관련 설정 (PROBABILITY_* 등)
- 임계값 설정 (MONEY_*_THRESHOLD 등)
- 트레이드오프 관계
- 지표 범위 및 기본값

## 🤝 기여하기

이 프로젝트에 기여해 주셔서 감사합니다! 

### 기여 방법
1. [기여 가이드](/docs/CONTRIBUTING.md) 숙지
2. [Good First Issue](https://github.com/your-repo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 선택
3. Fork & Pull Request

### 기여 영역
- 🐛 **버그 수정** - 이슈 리포트 확인 후 수정
- ⭐ **새 기능** - 게임 메커니즘, 이벤트, UI 개선
- 📚 **문서화** - API 문서, 가이드, 번역
- 🧪 **테스트** - 커버리지 확대, 엣지 케이스
- 🎨 **다이어그램** - Mermaid 다이어그램 추가/개선

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **이슈 및 버그 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **기능 제안**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **문서 질문**: [개발자 가이드](/docs/DEVELOPER_GUIDE.md) 또는 GitHub Issues

---

## 📚 문서 전체 목록

모든 프로젝트 문서는 [📚 문서 인덱스](/docs/INDEX.md)에서 확인할 수 있습니다.

**🚀 시작하기**: [DEVELOPER_GUIDE.md](/docs/DEVELOPER_GUIDE.md)  
**🔧 API 사용법**: [API.md](/docs/API.md)  
**🤝 기여하기**: [CONTRIBUTING.md](/docs/CONTRIBUTING.md)  
**🏗️ 아키텍처**: [architecture_specification.md](/docs/architecture_specification.md)  
**🎨 다이어그램**: [diagrams/README.md](/docs/diagrams/README.md) 🆕

---

**Chicken-RNG와 함께 "정답 없는 삶"을 체험해보세요! 🐔🎲**  
**🔥 매직넘버는 이제 진짜로 과거의 유물입니다! 🔥**

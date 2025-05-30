# Architecture Decision Records (ADR)

> 📋 **목적**: 프로젝트의 중요한 아키텍처 결정들을 체계적으로 기록하고 추적합니다.

## 📖 ADR이란?

Architecture Decision Records (ADR)는 소프트웨어 프로젝트에서 내린 중요한 아키텍처 결정들을 문서화하는 방법입니다. 각 ADR은 특정 결정의 배경, 고려사항, 결정 내용, 그리고 그 결과를 담고 있습니다.

## 📂 디렉토리 구조

```
docs/adr/
├── README.md              # 이 파일
├── template.md            # ADR 작성 템플릿
├── 0001-hexagonal-architecture.md
├── 0002-immutable-domain-objects.md
├── 0003-python-312-adoption.md
└── ...
```

## 📊 ADR 목록

| 번호 | 제목 | 상태 | 날짜 |
|------|------|------|------|
| [ADR-0001](0001-hexagonal-architecture.md) | 헥사고널 아키텍처 채택 | ✅ 승인됨 | 2024-01-15 |
| [ADR-0002](0002-immutable-domain-objects.md) | 불변 도메인 객체 패턴 | ✅ 승인됨 | 2024-01-20 |
| [ADR-0003](0003-python-312-adoption.md) | Python 3.12 채택 | ✅ 승인됨 | 2024-01-25 |
| [ADR-0004](0004-event-driven-architecture.md) | 이벤트 기반 아키텍처 | ✅ 승인됨 | 2024-02-01 |
| [ADR-0005](0005-testing-strategy.md) | 테스트 전략 | ✅ 승인됨 | 2024-02-10 |

## 🚀 ADR 작성 방법

### 1. 새 ADR 생성
```bash
# 다음 번호 확인
ls docs/adr/*.md | wc -l

# 새 ADR 파일 생성 (번호는 4자리로 패딩)
cp docs/adr/template.md docs/adr/0006-your-decision-title.md
```

### 2. ADR 작성 가이드라인

- **제목**: 결정의 핵심을 간결하게 표현
- **상태**: Proposed → Accepted → Deprecated/Superseded
- **맥락**: 왜 이 결정이 필요했는가?
- **결정**: 무엇을 결정했는가?
- **결과**: 이 결정의 영향은 무엇인가?

### 3. 상태 관리

| 상태 | 의미 | 표시 |
|------|------|------|
| Proposed | 제안됨 | 🔄 |
| Accepted | 승인됨 | ✅ |
| Deprecated | 더 이상 사용 안함 | ❌ |
| Superseded | 다른 ADR로 대체됨 | ♻️ |

## 🔍 검색 및 참조

### 주제별 분류

#### 아키텍처 패턴
- [ADR-0001](0001-hexagonal-architecture.md) - 헥사고널 아키텍처
- [ADR-0004](0004-event-driven-architecture.md) - 이벤트 기반 아키텍처

#### 기술 스택
- [ADR-0003](0003-python-312-adoption.md) - Python 3.12

#### 코딩 표준
- [ADR-0002](0002-immutable-domain-objects.md) - 불변 객체 패턴
- [ADR-0005](0005-testing-strategy.md) - 테스트 전략

### 관련 결정들

일부 ADR들은 서로 연관되어 있습니다:
- ADR-0001 (헥사고널 아키텍처) → ADR-0002 (불변 객체)
- ADR-0004 (이벤트 아키텍처) → ADR-0005 (테스트 전략)

## 📚 추가 자료

- [ADR 작성 가이드](https://github.com/joelparkerhenderson/architecture-decision-record)
- [마이클 나이가드의 ADR 개념](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- [프로젝트 아키텍처 명세](../architecture_specification.md) 
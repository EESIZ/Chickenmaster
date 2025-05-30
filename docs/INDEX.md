# 📚 문서 인덱스

> 🧭 **안내**: Chicken-RNG 프로젝트의 모든 문서를 한 곳에서 찾을 수 있습니다.

## 🎯 빠른 시작

새로운 개발자라면 다음 순서로 문서를 읽어보세요:

1. **[📖 README](../README.md)** - 프로젝트 개요
2. **[🚀 개발자 가이드](DEVELOPER_GUIDE.md)** - 개발 환경 설정
3. **[🏗️ 아키텍처 명세](architecture_specification.md)** - 기술적 구조
4. **[🔧 API 문서](API.md)** - 모듈 사용법
5. **[🤝 기여 가이드](CONTRIBUTING.md)** - 코드 기여 방법

---

## 📂 카테고리별 문서

### 🏁 시작하기
| 문서 | 설명 | 대상 |
|------|------|------|
| [README](../README.md) | 프로젝트 개요 및 소개 | 모든 사용자 |
| [개발자 가이드](DEVELOPER_GUIDE.md) | 개발 환경 설정 및 첫 실행 | 신규 개발자 |
| [기여 가이드](CONTRIBUTING.md) | 코드 기여 방법 및 규칙 | 기여자 |

### 🏗️ 아키텍처 및 설계
| 문서 | 설명 | 대상 |
|------|------|------|
| [아키텍처 명세](architecture_specification.md) | 헥사고널 아키텍처 상세 설명 | 개발자 |
| [ADR 목록](adr/README.md) | 아키텍처 결정 기록 인덱스 | 아키텍트, 리드 개발자 |
| [설계 결정](DESIGN_DECISIONS.md) | 주요 설계 결정 요약 | 개발자 |
| [리팩토링 가이드라인](REFACTORING_GUIDELINES.md) | 코드 리팩토링 원칙 | 개발자 |

### 📚 API 및 기술 문서
| 문서 | 설명 | 대상 |
|------|------|------|
| [API 문서](API.md) | 모듈별 API 사용법 | 개발자 |
| [인터페이스 개요](interface_overview.md) | 시스템 인터페이스 설명 | 개발자 |
| [경제 시스템 명세](economy_spec.md) | 경제 엔진 상세 설명 | 게임 로직 개발자 |

### 🎮 게임 설계
| 문서 | 설명 | 대상 |
|------|------|------|
| [게임 규칙](rules.md) | 게임 메커니즘 및 규칙 | 게임 디자이너, 개발자 |
| [품질 지표](quality_metrics.md) | 코드 품질 및 게임 밸런스 지표 | QA, 개발자 |
| [컨텐츠 가이드라인](content_guidelines.md) | 게임 컨텐츠 작성 가이드 | 컨텐츠 제작자 |

### 🎲 이벤트 시스템
| 문서 | 설명 | 대상 |
|------|------|------|
| [이벤트 스키마 설계](event_schema_and_cascade_design.md) | 이벤트 시스템 구조 | 개발자 |
| [이벤트 검증기 설계](event_validator_design.md) | 이벤트 유효성 검증 | 개발자 |
| [이벤트 뱅크 버전 관리](event_bank_versioning.md) | 이벤트 데이터 관리 | 컨텐츠 관리자 |

### 📊 분석 및 리포트
| 문서 | 설명 | 대상 |
|------|------|------|
| [프로젝트 종합 리포트](project_comprehensive_report.md) | 프로젝트 전체 현황 | 프로젝트 매니저 |
| [밸런스 시뮬레이터 설계](balance_simulator_design.md) | 게임 밸런스 분석 도구 | 게임 밸런서 |
| [밸런스 시뮬레이터 아키텍처](balance_simulator_architecture.md) | 시뮬레이터 기술 구조 | 개발자 |

### 🔧 개발 도구
| 문서 | 설명 | 대상 |
|------|------|------|
| [Claude 코드 사용법](claude_code_usage.md) | AI 도구 활용 가이드 | 개발자 |
| [Claude 코드 구현 리포트](claude_code_implementation_report.md) | AI 도구 구현 결과 | 개발자 |

### 📋 테스트 및 검증
| 문서 | 설명 | 대상 |
|------|------|------|
| [이벤트 검증 최종 리포트](event_validation_final_report.md) | 이벤트 시스템 검증 결과 | QA |
| [이벤트 뱅크 테스트 결과](event_bank_test_results.md) | 이벤트 데이터 테스트 | QA |
| [이벤트 파이프라인 결과](event_pipeline_results.md) | 이벤트 처리 파이프라인 | 개발자 |

### 🛠️ 문서화 시스템
| 문서 | 설명 | 대상 |
|------|------|------|
| [문서 인덱스](INDEX.md) | 이 문서 - 모든 문서의 인덱스 | 모든 사용자 |
| [문서화 유지보수 가이드](DOCUMENTATION_MAINTENANCE.md) | 문서화 시스템 관리 방법 | 메인테이너 |
| [문서화 도우미 스크립트](../scripts/docs_helper.py) | 문서 자동화 도구 | 개발자 |

---

## 🗂️ ADR (Architecture Decision Records)

| 번호 | 제목 | 상태 | 날짜 |
|------|------|------|------|
| [ADR-0001](adr/0001-hexagonal-architecture.md) | 헥사고널 아키텍처 채택 | ✅ 승인됨 | 2024-01-15 |
| [ADR-0002](adr/0002-immutable-domain-objects.md) | 불변 도메인 객체 패턴 | ✅ 승인됨 | 2024-01-20 |

📝 **새 ADR 작성법**: [ADR 가이드](adr/README.md) 참조

---

## 🔍 주제별 문서 찾기

### 개발 시작하기
새로운 개발자를 위한 필수 문서:
- [개발자 가이드](DEVELOPER_GUIDE.md) - 환경 설정
- [기여 가이드](CONTRIBUTING.md) - 기여 방법
- [API 문서](API.md) - 코드 사용법

### 아키텍처 이해하기
시스템 구조를 이해하려면:
- [아키텍처 명세](architecture_specification.md) - 전체 구조
- [ADR 목록](adr/README.md) - 설계 결정들
- [인터페이스 개요](interface_overview.md) - 인터페이스 설계

### 게임 로직 개발
게임 기능을 개발하려면:
- [게임 규칙](rules.md) - 게임 메커니즘
- [경제 시스템 명세](economy_spec.md) - 경제 로직
- [이벤트 스키마 설계](event_schema_and_cascade_design.md) - 이벤트 시스템

### 품질 보증
코드 품질을 관리하려면:
- [품질 지표](quality_metrics.md) - 품질 기준
- [리팩토링 가이드라인](REFACTORING_GUIDELINES.md) - 리팩토링 방법
- [테스트 관련 문서들](#📋-테스트-및-검증) - 테스트 가이드

### 프로젝트 관리
프로젝트를 관리하려면:
- [프로젝트 종합 리포트](project_comprehensive_report.md) - 현황 파악
- [설계 결정](DESIGN_DECISIONS.md) - 결정 사항들
- [리팩토링 결정](REFACTORING_DECISIONS.md) - 리팩토링 이력

### 문서화 관리
문서화 시스템을 관리하려면:
- [문서화 유지보수 가이드](DOCUMENTATION_MAINTENANCE.md) - 관리 방법
- [문서화 도우미 스크립트](../scripts/docs_helper.py) - 자동화 도구
- [ADR 템플릿](adr/template.md) - 새 ADR 작성 템플릿

---

## 📈 문서 상태

### 📋 최신 상태 (2024년 기준)
- ✅ **최신**: API 문서, 개발자 가이드, 기여 가이드
- ✅ **최신**: 아키텍처 명세, ADR 시스템
- ✅ **최신**: 문서화 시스템 및 자동화 도구
- ⚠️ **주의**: 일부 이벤트 관련 문서는 시스템 변경으로 업데이트 필요

### 🔄 업데이트 주기
- **개발자 가이드**: 새 버전 릴리즈 시
- **API 문서**: 공개 API 변경 시
- **ADR**: 중요한 아키텍처 결정 시
- **게임 규칙**: 게임 메커니즘 변경 시
- **문서 인덱스**: 새 문서 추가 시

### 📝 문서 기여
문서 개선에 기여하고 싶다면:
1. [기여 가이드](CONTRIBUTING.md#📚-문서화-가이드라인) 확인
2. 오타나 개선사항 발견 시 이슈 생성
3. 새 문서 필요 시 제안서 작성
4. [문서화 도우미 스크립트](../scripts/docs_helper.py) 활용

---

## 🔧 문서 관리 도구

### 자동화 스크립트
```bash
# 새 ADR 생성
python scripts/docs_helper.py new-adr "결정 제목"

# 문서 링크 검증
python scripts/docs_helper.py validate-links

# 문서 통계 확인
python scripts/docs_helper.py stats

# 전체 검증 실행
python scripts/docs_helper.py check-all
```

### 정기 유지보수
- **주간**: 링크 검증 및 통계 확인
- **월간**: 내용 업데이트 및 구조 검토
- **분기별**: 전면적인 문서 재구성 검토

자세한 내용은 [문서화 유지보수 가이드](DOCUMENTATION_MAINTENANCE.md)를 참조하세요.

---

## 🎯 문서 검색 팁

### 키워드별 찾기
- **아키텍처**: `architecture`, `hexagonal`, `ports`, `adapters`
- **게임**: `rules`, `metrics`, `economy`, `events`
- **개발**: `developer`, `api`, `contributing`, `testing`
- **설계**: `design`, `adr`, `decisions`, `refactoring`
- **문서화**: `documentation`, `docs`, `maintenance`

### 파일 타입별 찾기
- **`.md`**: 일반 문서
- **`adr/`**: 아키텍처 결정 기록
- **`*_report.md`**: 분석 및 리포트
- **`*_design.md`**: 설계 문서
- **`*.py`**: 자동화 스크립트

### 대상별 찾기
- **신규 개발자**: README → DEVELOPER_GUIDE → API
- **숙련 개발자**: architecture_specification → adr/
- **게임 디자이너**: rules → content_guidelines
- **프로젝트 매니저**: project_comprehensive_report
- **문서 관리자**: DOCUMENTATION_MAINTENANCE

---

## 📞 도움말

### 문서 관련 질문
- **문서를 찾을 수 없나요?** 이 인덱스에서 키워드 검색을 해보세요
- **문서가 오래되었나요?** GitHub Issues에 업데이트 요청을 올려주세요
- **새 문서가 필요한가요?** [기여 가이드](CONTRIBUTING.md) 참조하여 제안해주세요
- **문서 자동화 도구 사용법?** [문서화 유지보수 가이드](DOCUMENTATION_MAINTENANCE.md) 확인

### 빠른 링크
- 🚀 [개발 시작하기](DEVELOPER_GUIDE.md)
- 🔧 [API 참조](API.md)
- 🤝 [기여하기](CONTRIBUTING.md)
- 🏗️ [아키텍처](architecture_specification.md)
- 📝 [ADR](adr/README.md)
- 🛠️ [문서 관리](DOCUMENTATION_MAINTENANCE.md)

---

**📚 마지막 업데이트**: 2024년 5월 30일  
**✍️ 관리자**: 개발팀  
**🔄 업데이트 주기**: 월 1회 또는 주요 변경 시  
**🤖 자동화**: [docs_helper.py](../scripts/docs_helper.py)로 부분 자동화 
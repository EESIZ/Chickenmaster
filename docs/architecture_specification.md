# 헥사고날 아키텍처 명세 및 변경 관리 문서

## 1. 아키텍처 개요

### 1.1 헥사고날 아키텍처 구조

Chickmaster 프로젝트는 헥사고날 아키텍처(Ports & Adapters)를 기반으로 설계되었습니다. 이 아키텍처는 다음과 같은 주요 레이어로 구성됩니다:

- **코어 도메인 (Core Domain)**: 비즈니스 엔티티와 규칙을 포함하는 불변 객체
- **포트 (Ports)**: 비즈니스 로직의 경계를 정의하는 인터페이스
- **어댑터 (Adapters)**: 포트 인터페이스의 구현체와 외부 시스템 연결
- **애플리케이션 (Application)**: 전체 시스템을 조율하는 서비스

### 1.2 디렉토리 구조

```
src/
├── core/
│   ├── domain/       # 비즈니스 엔티티 (불변 객체)
│   └── ports/        # 인터페이스만 (비즈니스 로직 경계)
├── adapters/
│   ├── services/     # 서비스 구현체
│   └── storage/      # 저장소 구현체
└── application/      # 애플리케이션 서비스
```

### 1.3 의존성 방향

헥사고날 아키텍처의 핵심 원칙은 의존성이 항상 안쪽으로 향한다는 것입니다:

- **도메인 (Domain)**: 어떤 외부 레이어에도 의존하지 않음
- **포트 (Ports)**: 도메인에만 의존
- **어댑터 (Adapters)**: 포트와 도메인에 의존
- **애플리케이션 (Application)**: 모든 레이어에 의존 가능

이 의존성 규칙은 구조 검증 스크립트에 의해 자동으로 검증됩니다.

## 2. 도메인 모델

### 2.1 불변 객체 원칙

모든 도메인 객체는 다음 원칙을 따릅니다:

- `@dataclass(frozen=True)`로 구현하여 불변성 보장
- 상태 변경이 필요한 경우 새 객체 생성
- 모든 속성과 메서드에 타입 힌트 100% 적용
- Optional 타입 대신 명시적 기본값 사용
- 가변 컬렉션(list) 대신 불변 컬렉션(tuple) 사용

### 2.2 주요 도메인 객체

#### 2.2.1 이벤트 관련 객체

- **Event**: 이벤트 기본 정보와 효과
- **EventChoice**: 이벤트 선택지 정보
- **EventTrigger**: 이벤트 발생 조건

#### 2.2.2 게임 상태 관련 객체

- **GameState**: 게임의 현재 상태
- **MetricBounds**: 지표의 경계값
- **GameSettings**: 게임 설정 정보

#### 2.2.3 지표 관련 객체

- **Metric**: 개별 지표
- **TradeoffPair**: 두 지표 간의 트레이드오프 관계
- **MetricsSnapshot**: 특정 시점의 모든 지표 상태

## 3. 포트 인터페이스

### 3.1 인터페이스 설계 원칙

모든 포트 인터페이스는 다음 원칙을 따릅니다:

- ABC 클래스 상속 및 @abstractmethod 데코레이터 사용
- 모든 메서드에 타입 힌트와 docstring 100% 적용
- 인터페이스 이름은 'I'로 시작 (예: IEventService)
- Freeze Tag를 통한 버전 관리

### 3.2 주요 포트 인터페이스

#### 3.2.1 IEventService

이벤트 처리 관련 비즈니스 로직 경계를 정의합니다.

- **get_applicable_events**: 현재 상태에서 발생 가능한 이벤트 목록 반환
- **apply_event_effects**: 이벤트 효과를 적용한 새 게임 상태 반환
- **validate_event_conditions**: 이벤트 발생 조건 검증
- **evaluate_event_probability**: 이벤트 발생 확률 계산
- **check_event_cooldown**: 이벤트 쿨다운 상태 확인

#### 3.2.2 IMetricService

지표 관리 관련 비즈니스 로직 경계를 정의합니다.

- **calculate_happiness_pain_balance**: 행복-고통 시소 계산
- **check_bankruptcy_risk**: 파산 위험도 계산
- **calculate_game_over_conditions**: 게임 종료 조건들 검증
- **get_metric_bounds**: 각 지표의 최소/최대값 반환
- **apply_tradeoff_effects**: 트레이드오프 효과 적용
- **get_critical_metrics**: 위험 수준의 지표 목록 반환

#### 3.2.3 ICascadeService

연쇄 효과 처리 관련 비즈니스 로직 경계를 정의합니다.

- **get_cascade_events**: 트리거 이벤트로 인한 연쇄 이벤트 목록
- **calculate_cascade_depth**: 연쇄 효과 깊이 계산
- **validate_cascade_limits**: 연쇄 깊이 제한 검증
- **process_cascade_chain**: 전체 연쇄 체인 처리
- **check_cascade_cycle**: 연쇄 효과 사이클 검사

#### 3.2.4 IEventBank

이벤트 데이터 관리 관련 비즈니스 로직 경계를 정의합니다.

- **load_events_by_category**: 카테고리별 이벤트 로딩
- **get_event_by_id**: ID로 특정 이벤트 조회
- **filter_events_by_conditions**: 조건에 맞는 이벤트 필터링
- **get_available_categories**: 사용 가능한 이벤트 카테고리 목록
- **validate_event_data**: 이벤트 데이터 무결성 검증
- **reload_events**: 이벤트 데이터 다시 로드

#### 3.2.5 IServiceContainer

의존성 주입 컨테이너 인터페이스를 정의합니다.

- **register_singleton**: 싱글톤 서비스 등록
- **register_transient**: 트랜지언트 서비스 등록
- **get**: 서비스 인스턴스 조회
- **has**: 서비스 등록 여부 확인
- **clear**: 모든 등록된 서비스 초기화
- **validate_dependencies**: 의존성 순환 참조 검증

## 4. Freeze Tag 및 변경 관리

### 4.1 Freeze Tag 정책

Freeze Tag는 포트 인터페이스의 안정성과 하위 호환성을 보장하기 위한 버전 관리 메커니즘입니다.

- 모든 포트 인터페이스는 파일 상단에 `@freeze v{major}.{minor}.{patch}` 형식의 태그를 포함해야 합니다.
- 태그가 있는 인터페이스는 하위 호환성을 깨뜨리는 변경을 할 수 없습니다.
- 버전 번호는 [Semantic Versioning](https://semver.org/) 원칙을 따릅니다:
  - **major**: 하위 호환성을 깨뜨리는 변경
  - **minor**: 하위 호환성을 유지하는 기능 추가
  - **patch**: 버그 수정 및 문서 개선

### 4.2 인터페이스 변경 프로세스

포트 인터페이스를 변경하려면 다음 프로세스를 따라야 합니다:

1. **변경 제안**: MR(Merge Request)을 통해 변경 사항 제안
2. **영향 분석**: 변경이 미치는 영향 범위 분석
3. **버전 업데이트**: 변경 유형에 따라 적절한 버전 번호 업데이트
4. **코드 리뷰**: 최소 2명의 승인자 리뷰
5. **구조 검증**: 구조 검증 스크립트 통과 확인
6. **병합 및 배포**: 승인 후 병합 및 배포

### 4.3 MR 설명 템플릿

인터페이스 변경 MR은 다음 템플릿을 따라야 합니다:

```
# 인터페이스 변경 요청

## Intent
변경의 의도와 목적

## Mission
해결하려는 문제 또는 달성하려는 목표

## End State
변경 후 기대되는 최종 상태

## Constraints
지켜야 할 제약 조건 및 하위 호환성 고려사항

## Tech
기술적 구현 방법 및 접근 방식

## Validation
변경 사항 검증 방법 및 테스트 계획
```

### 4.4 변경 이력 관리

모든 인터페이스 변경은 다음과 같이 기록됩니다:

- 인터페이스 파일 내 변경 이력 주석
- CHANGELOG.md 파일 업데이트
- 커밋 메시지는 Conventional Commits 형식 준수

## 5. 구조 검증

### 5.1 검증 스크립트

`scripts/validate_architecture.py` 스크립트는 다음 항목을 자동으로 검증합니다:

- 디렉토리 구조 및 필수 파일 존재 여부
- 레이어 간 의존성 방향 준수
- 도메인 객체의 불변성 (`@dataclass(frozen=True)`)
- 포트 인터페이스의 Freeze Tag 존재

### 5.2 검증 실행 방법

```bash
python scripts/validate_architecture.py
```

### 5.3 CI/CD 통합

구조 검증은 CI/CD 파이프라인에 통합되어 모든 PR에서 자동으로 실행됩니다.

## 6. 개발 가이드라인

### 6.1 Conventional Commits

모든 커밋은 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따라야 합니다:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

주요 타입:
- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **refactor**: 코드 리팩터링
- **docs**: 문서 변경
- **test**: 테스트 추가 또는 수정
- **chore**: 빌드 프로세스 또는 도구 변경

### 6.2 코드 스타일

- 모든 코드는 타입 힌트를 100% 포함해야 합니다.
- mypy strict 모드를 통과해야 합니다.
- 도메인 객체는 불변성을 보장해야 합니다.
- 인터페이스는 명확한 docstring을 포함해야 합니다.

### 6.3 테스트 요구사항

- 모든 도메인 객체는 단위 테스트를 포함해야 합니다.
- 모든 어댑터 구현체는 통합 테스트를 포함해야 합니다.
- 테스트 커버리지는 최소 90% 이상이어야 합니다.

## 7. 참고 자료

- [헥사고날 아키텍처 소개](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports & Adapters 패턴](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [불변 객체 패턴](https://en.wikipedia.org/wiki/Immutable_object)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

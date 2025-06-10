# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-03

### Added
- 오프라인 콘텐츠 파이프라인
  - Event Generator CLI: LLM 기반 이벤트 대량 생성
  - Content Validator: 이벤트 품질 및 일관성 검증
  - Balance Simulator: 이벤트 밸런스 자동 시뮬레이션
  - Event Bank Manager: 이벤트 뱅크 통합 관리
- 품질 메트릭 시스템
  - 다양성, 트레이드오프, 문화적 진정성 평가
  - 자동화된 밸런스 검증

### Changed
- API 키 관리 시스템 개선
- 데이터 구조 최적화 (TOML/JSON 지원)
- 코드 품질 개선
  - Python 3.11+ 타입 힌트 표준 적용
  - 메모리 효율성 개선 (generator 패턴)
  - 출력 형식 통일

### Fixed
- CI/CD 파이프라인 안정화
- 하드코딩된 카테고리 제거

## [0.3.0] - 2024-02

### Added
- 이벤트 엔진 구현
  - 4가지 이벤트 타입 지원 (RANDOM, THRESHOLD, SCHEDULED, CASCADE)
  - 이벤트 우선순위, 쿨다운, 트리거 조건 관리
- 연쇄 효과 시스템
  - DAG 기반 연쇄 효과 구조
  - 트레이드오프 매트릭스
  - 불확실성 관리 시스템

### Changed
- 코드 커버리지 81% 달성
- 성능 최적화: 1,000회 이벤트 처리 < 3초
- CI 파이프라인에 DAG 검증 자동화 추가

### Fixed
- CI 환경 안정화 (psutil 의존성)
- mypy strict 모드 지원

## [0.2.0] - 2024-01

### Added
- 메트릭 트래커 구현
- 수정자 시스템 도입

## [0.1.0] - 2023-12

### Added
- 초기 게임 엔진 구현
- 기본 게임 메커니즘 구현 
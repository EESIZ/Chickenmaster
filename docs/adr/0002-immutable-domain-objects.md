# ADR-0002: 불변 도메인 객체 패턴

## 상태

✅ **Accepted**

## 날짜

2024-01-20

## 작성자

- 개발팀 ([프로젝트 메인테이너])

## 맥락 (Context)

Chicken-RNG 게임의 도메인 객체 설계 방식을 결정해야 했습니다. 게임 상태, 메트릭, 이벤트 등의 핵심 도메인 객체들이 어떻게 상태를 관리하고 변경을 처리할지에 대한 패턴을 선택해야 했습니다.

### 문제 정의
- 게임 상태 변경 시 예상치 못한 부작용(side effect) 방지 필요
- 멀티스레드 환경에서의 안전성 보장
- 상태 변경 추적과 디버깅 용이성 필요
- 함수형 프로그래밍 패러다임과의 호환성

### 제약사항
- Python 언어의 특성 (완전한 불변성 보장 어려움)
- 성능 고려사항 (객체 생성 비용)
- 개발팀의 함수형 프로그래밍 경험 부족

## 고려된 옵션들 (Considered Options)

### 옵션 1: 가변 객체 (Mutable Objects)
**장점:**
- 직관적이고 익숙한 패턴
- 메모리 효율성 (기존 객체 수정)
- 빠른 개발 속도

**단점:**
- 예상치 못한 상태 변경 위험
- 멀티스레드 환경에서 동기화 문제
- 디버깅 어려움 (언제 어디서 변경되었는지 추적 어려움)
- 부작용으로 인한 버그 발생 가능성

### 옵션 2: 불변 객체 (Immutable Objects)
**장점:**
- 예측 가능한 동작 (no side effects)
- 스레드 안전성 자동 보장
- 상태 변경 추적 용이 (새 객체 생성)
- 함수형 프로그래밍 패러다임과 잘 맞음
- 테스트 용이성

**단점:**
- 객체 생성 비용 증가
- 익숙하지 않은 패턴 (학습 비용)
- 깊은 중첩 구조에서 업데이트 복잡성

### 옵션 3: 하이브리드 접근 (일부만 불변)
**장점:**
- 유연성 제공
- 점진적 적용 가능

**단점:**
- 일관성 부족
- 어떤 객체가 불변인지 판단 어려움
- 혼란 야기 가능

## 결정 (Decision)

**선택한 옵션:** 불변 객체 (Immutable Objects)

**결정 이유:**
1. **게임 철학과의 일치**: "정답 없음" 원칙처럼 예측 불가능한 변화를 코드에서도 방지
2. **안정성**: 복잡한 게임 로직에서 상태 변경으로 인한 버그 최소화
3. **테스트 용이성**: 불변 객체는 테스트하기 매우 쉬움
4. **추적 가능성**: 상태 변경 시 새 객체가 생성되므로 변경 이력 추적 가능
5. **함수형 접근**: 게임의 수학적 계산(경제, 확률)에 함수형 접근이 적합

**기대 효과:**
- 버그 감소와 코드 품질 향상
- 병렬 처리 시 안전성 보장
- 상태 변경 로직의 명확성

## 결과 (Consequences)

### 긍정적 영향
- 예상치 못한 상태 변경 버그 완전 제거
- 테스트 작성이 매우 단순해짐 (mock 불필요)
- 멀티스레드 환경에서 동기화 걱정 없음
- 함수형 스타일로 로직 작성 가능
- 상태 변경 시점이 명확함

### 부정적 영향  
- 객체 생성 비용 증가 (특히 자주 변경되는 상태)
- 깊은 중첩 객체 업데이트 시 복잡한 코드
- 팀의 학습 곡선 존재
- 메모리 사용량 증가 가능성

### 중립적 영향
- 코딩 스타일 변화 (setter 대신 새 객체 생성)
- dataclass frozen=True 사용으로 Python 관용구 변화

## 구현 계획 (Implementation)

### 필요한 작업
- [x] `@dataclass(frozen=True)` 패턴 도입
- [x] 상태 변경 메서드들을 새 객체 반환 방식으로 구현
- [x] 불변 컬렉션 사용 (list → tuple)
- [x] 팀 교육 및 가이드라인 작성
- [x] 기존 코드 리팩토링

### 마일스톤
- [x] 핵심 도메인 객체 불변화 완료: 2024-01-25
- [x] 모든 도메인 객체 불변화 완료: 2024-02-01
- [x] 성능 테스트 및 최적화: 2024-02-05

### 위험 요소
- 성능 저하 (확률: 중간, 영향: 낮음) - 프로파일링으로 모니터링
- 팀 적응 어려움 (확률: 낮음, 영향: 중간) - 충분한 예제와 가이드 제공

## 검증 방법 (Validation)

### 성공 지표
- 모든 도메인 객체가 `frozen=True` 사용
- 상태 변경 관련 버그 개수 감소
- 테스트 코드 복잡도 감소

### 검증 방법
- 린터 규칙으로 가변 객체 사용 방지
- 코드 리뷰에서 불변성 원칙 준수 확인
- 성능 테스트로 객체 생성 비용 모니터링

### 롤백 계획
만약 성능 문제가 심각하다면:
1. 롤백 조건: 게임 실행 속도가 50% 이상 저하
2. 롤백 절차: 핫스팟만 가변 객체로 변경, 나머지는 불변 유지
3. 대안 계획: Copy-on-Write 패턴 또는 구조적 공유 도입

## 관련 문서

- [ADR-0001](./0001-hexagonal-architecture.md) - 헥사고널 아키텍처 채택
- [도메인 모델 가이드](../architecture_specification.md#도메인-모델)
- [코딩 스타일 가이드](../CODING_STYLE.md)

## 노트

### 구현 패턴

```python
# 올바른 불변 객체 패턴
@dataclass(frozen=True)
class GameState:
    money: int
    reputation: int
    happiness: int
    pain: int
    
    def apply_effects(self, effects: Dict[str, int]) -> 'GameState':
        """효과 적용 시 새 상태 반환"""
        return GameState(
            money=max(0, self.money + effects.get('money', 0)),
            reputation=max(0, min(100, self.reputation + effects.get('reputation', 0))),
            happiness=max(0, min(100, self.happiness + effects.get('happiness', 0))),
            pain=max(0, min(100, self.pain + effects.get('pain', 0)))
        )
```

### 토론 요약
- 성능 우려가 있었지만, 게임의 복잡성과 안정성을 고려할 때 불변성의 이익이 더 크다고 판단
- Python의 `dataclass(frozen=True)`가 충분한 불변성을 제공한다고 합의
- 성능이 문제될 경우 프로파일링 후 선택적 최적화 진행하기로 결정

### 참고 자료
- [Effective Python - Item 23: Accept Functions Instead of Classes for Simple Interfaces](https://effectivepython.com/)
- [Functional Programming in Python](https://docs.python.org/3/howto/functional.html)
- [immutability in Python](https://docs.python.org/3/library/dataclasses.html#frozen-instances) 
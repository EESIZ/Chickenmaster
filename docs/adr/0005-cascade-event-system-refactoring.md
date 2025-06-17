# ADR 0005: Cascade 이벤트 시스템 리팩토링

## 상태
승인됨

## 컨텍스트
- 기존 이벤트 시스템에서 Cascade(연쇄) 이벤트가 별도의 구조로 관리되어 복잡성이 증가
- 이벤트 파일들이 여러 형식으로 존재하여 관리가 어려움
- 연쇄 이벤트의 다양한 발생 조건(즉시/지연/조건부/확률적)을 통합적으로 관리할 필요성

## 결정
1. 이벤트 스키마 확장
   - CascadeType enum 추가 (IMMEDIATE/DELAYED/CONDITIONAL/PROBABILISTIC)
   - CascadeEvent 모델 추가
   - Event와 EventChoice에 cascade_events 필드 추가

2. JSON 구조 통합
   - 모든 이벤트 파일에 동일한 구조 적용
   - 이벤트와 선택지 모두에서 연쇄 이벤트 정의 가능
   - 효과(effects)에 message 필드 추가

3. 이벤트 파일 구조화
   - 카테고리별 폴더 구조 유지 (daily_routine, crisis_events, opportunity)
   - 모든 이벤트 파일을 JSON 형식으로 통일
   - CSV 형식 제거

## 결과
- 모든 이벤트 파일이 일관된 구조를 가지게 됨
- 연쇄 이벤트의 다양한 발생 조건을 유연하게 정의 가능
- 이벤트 시스템의 복잡성 감소

## 영향
### 긍정적
- 이벤트 관리 용이성 증가
- 연쇄 이벤트 정의의 유연성 향상
- 코드 일관성 개선

### 부정적
- 기존 이벤트 파일 마이그레이션 필요
- 이벤트 파일 크기 증가

## 구현 세부사항
1. 스키마 변경
   ```python
   class CascadeType(str, Enum):
       IMMEDIATE = "IMMEDIATE"
       DELAYED = "DELAYED"
       CONDITIONAL = "CONDITIONAL"
       PROBABILISTIC = "PROBABILISTIC"

   class CascadeEvent(BaseModel):
       event_id: str
       cascade_type: CascadeType
       delay_turns: int = Field(default=0)
       probability: float = Field(default=1.0)
       conditions: list[str] = Field(default_factory=list)
   ```

2. 이벤트 예시
   ```json
   {
     "cascade_events": [
       {
         "event_id": "staff_stress_increase",
         "cascade_type": "IMMEDIATE"
       }
     ],
     "choices": [
       {
         "cascade_events": [
           {
             "event_id": "quality_complaint",
             "cascade_type": "PROBABILISTIC",
             "probability": 0.3,
             "conditions": ["food_quality < 70"]
           }
         ]
       }
     ]
   }
   ```

## 관련 문서
- [이벤트 시스템 설계](../core/events/event_system.md)
- [이벤트 밸런싱 가이드](../game_design_philosophy.md) 
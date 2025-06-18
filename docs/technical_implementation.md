# 치킨마스터 기술 구현 문서

## 🏗️ 아키텍처 개요

### 헥사고널 아키텍처 (Ports & Adapters)
- **Core Domain**: 순수 비즈니스 로직 (game_constants.py)
- **Ports**: 인터페이스 정의 (데이터 제공자, 대화 관리자)
- **Adapters**: 외부 시스템 연결 (CSV, 웹 API)
- **Application**: 응용 서비스 (FastAPI 웹 서버)

### 핵심 설계 원칙
1. **정답 없음**: 모든 선택은 득과 실의 트레이드오프
2. **불변성**: 도메인 객체는 불변(immutable) 
3. **의존성 역전**: 구체적 구현이 아닌 인터페이스 의존
4. **단일 책임**: 각 모듈은 하나의 명확한 역할

## 💰 게임 경제 시스템

### 현실적 설정값 (2024년 기준)
```python
# 신규 매장 현실적 설정
STARTING_MONEY = 5_000_000      # 500만원 창업자금
CHICKEN_COST = 6_333           # 개당 원가 6,333원
CHICKEN_PRICE = 8_000          # 개당 판매가 8,000원 (마진 1,667원, 26%)
STARTING_REPUTATION = 0        # 완전 무명에서 시작
STARTING_INVENTORY = 50        # 초기 재고 50개
```

### 경제 밸런싱
- **마진율**: 26% (현실적 수준)
- **평판 시스템**: 0-100점 (신규는 0점)
- **수요 연동**: 평판이 낮으면 수요도 낮음
- **트레이드오프**: 가격↑ → 평판↓, 수요↓

## 🎭 CSV 기반 대화 시스템

### 시스템 구조
```
web_prototype/
├── data/dialogues/
│   ├── characters.csv          # 캐릭터 정보
│   ├── daily_start.csv         # 매일 시작 대사 (조건별)
│   ├── general_dialogues.csv   # 일반 대사
│   └── event_dialogues.csv     # 이벤트 대사
├── dialogue_manager.py         # Python 백엔드 관리자
└── static/
    └── dialogue_system_csv.js  # JavaScript 프론트엔드
```

### CSV 데이터 구조

#### daily_start.csv (조건부 대사)
```csv
condition,money_min,money_max,reputation_min,reputation_max,happiness_min,happiness_max,speaker,emotion,text,priority
신규_무명_첫날,0,99999999,0,5,0,100,boss,nervous,"드디어 치킨집을 오픈했다... 평판도 0점, 아무도 우리 가게를 모른다. 과연 손님이 올까?",100
자금위기_절망,0,1000000,0,100,0,30,boss,desperate,"자금이 바닥나고 있다... 이대로 가면 정말 망할 수도 있어!",100
```

#### characters.csv (캐릭터 정보)
```csv
character_id,name,avatar_path,voice_description,is_first_person,default_image,happy_image,sad_image
boss,나,/static/images/icon_chicken_large.png,나의 생각,true,,,
customer,손님,/static/images/customer_character_small.png,고객,false,/static/images/customer_character.png,/static/images/customer_character.png,
```

### 동적 대사 선택 알고리즘
```python
def get_daily_start_dialogue(self, game_state: Dict[str, Any]) -> Optional[Dialogue]:
    """게임 상태에 맞는 매일 시작 대화 반환"""
    money = game_state.get('money', 0)
    reputation = game_state.get('reputation', 0)
    happiness = game_state.get('happiness', 50)
    day = game_state.get('day', 1)
    
    # 우선순위 순으로 정렬된 조건부 대화에서 첫 번째 매칭 반환
    for conditional_dialogue in self.daily_start_dialogues:
        if (conditional_dialogue.money_min <= money <= conditional_dialogue.money_max and
            conditional_dialogue.reputation_min <= reputation <= conditional_dialogue.reputation_max and
            conditional_dialogue.happiness_min <= happiness <= conditional_dialogue.happiness_max and
            conditional_dialogue.day_min <= day <= conditional_dialogue.day_max):
            
            return dialogue
```

### 1인칭 몰입 시스템
- **주인공 비표시**: `isFirstPerson: true` 캐릭터는 화면에 나타나지 않음
- **NPC 자동 관리**: 대화 종료 후 NPC 캐릭터 자동 제거
- **1인칭 텍스트**: "내가 ~다" 형태의 자연스러운 독백

## 🌐 웹 API 시스템

### FastAPI 엔드포인트
```python
@app.get("/api/dialogue/daily-start")
async def get_daily_start_dialogue():
    """현재 게임 상태 기반 매일 시작 대화"""
    
@app.get("/api/dialogue/character-database") 
async def get_character_database():
    """JavaScript용 캐릭터 데이터베이스"""
    
@app.get("/api/dialogue/event/{event_id}")
async def get_event_dialogue(event_id: str):
    """특정 이벤트 대화"""
```

### 비동기 대화 로딩
```javascript
async function getDailyStartDialogue() {
    const response = await fetch('/api/dialogue/daily-start');
    const result = await response.json();
    
    if (result.success) {
        return [result.dialogue];
    }
    return null;
}
```

## 🎮 게임플레이 플로우

### 턴 시스템
1. **액션 선택**: 플레이어가 경영 액션 실행
2. **상태 업데이트**: 서버에서 게임 상태 계산
3. **대화 트리거**: 새로운 상태에 맞는 대화 실행
4. **턴 진행**: "하루 마감" 클릭 시 다음 날로

### 상황별 대사 예시
- **완전 무명** (평판 0-10): "아무도 우리 가게를 모른다..."
- **조금 알려짐** (평판 11-30): "조금씩 알려지기 시작했다!"
- **자금 위기** (자금 < 100만원): "정말 위험한 상황이다!"
- **대성공** (평판 90+): "전설의 치킨집이 되었다!"

## 📊 데이터 흐름

### 서버 → 클라이언트
```
CSV 파일 → Python DialogueManager → FastAPI → JSON → JavaScript
```

### 클라이언트 → 서버  
```
JavaScript → HTTP Request → FastAPI → Game Logic → Response
```

### 캐싱 및 성능
- **서버 사이드**: DialogueManager 인스턴스 재사용
- **클라이언트 사이드**: CHARACTER_DATABASE 한 번 로딩 후 캐시
- **폴백 시스템**: 서버 연결 실패 시 기본 데이터 사용

## 🔧 개발 및 배포

### 로컬 개발
```bash
cd web_prototype
python main.py
# http://localhost:8000 접속
```

### CSV 수정 워크플로우
1. `data/dialogues/*.csv` 파일 수정
2. 서버 재시작 (자동 리로딩)
3. 브라우저에서 즉시 확인

### 디버깅 도구
- **브라우저 콘솔**: `window.csvDialogueSystem` 객체
- **Python 로그**: 대화 로딩 과정 추적
- **API 테스트**: `/api/dialogue/daily-start` 직접 호출

## 🚀 확장성

### 새로운 상황 추가
1. `daily_start.csv`에 조건과 대사 추가
2. 우선순위 설정으로 매칭 순서 조정
3. 코드 수정 없이 바로 적용

### 다국어 지원 준비
- CSV 파일별 언어 분리 가능
- `dialogue_manager.py`에서 언어 설정 기반 로딩

### 복합 조건 지원
- 현재: 자금, 평판, 행복도, 날짜 기반
- 확장: 재고, 직원 피로도, 시설 상태 등 추가 조건

이 시스템으로 **개발자는 코드 수정 없이 CSV만 편집해서 게임의 스토리텔링을 완전히 바꿀 수 있습니다!** 🎯 
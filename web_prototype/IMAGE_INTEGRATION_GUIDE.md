# 🍗 치킨마스터 UI 이미지 통합 가이드

## 📸 현재 상태
임시 placeholder 이미지들이 생성되어 웹 UI에 적용되었습니다.

### 생성된 이미지 파일들

#### 🎭 캐릭터 이미지
- `boss_character.png` (200x200) - 메인 캐릭터 이미지
- `boss_character_small.png` (150x150) - 작은 캐릭터 이미지

#### 🏪 배경 이미지
- `chicken_shop_bg.png` (800x600) - 메인 치킨집 배경
- `chicken_shop_bg_small.png` (400x300) - 작은 배경 이미지

#### 🎯 UI 아이콘들 (32x32)
- `icon_money.png` - 💰 자금 아이콘
- `icon_chicken.png` - 🍗 치킨 아이콘  
- `icon_reputation.png` - ⭐ 평판 아이콘
- `icon_happiness.png` - 😊 행복 아이콘
- `icon_pain.png` - 😰 고통 아이콘
- `icon_inventory.png` - 📦 재고 아이콘
- `icon_fatigue.png` - 😴 피로 아이콘
- `icon_facility.png` - 🏪 시설 아이콘
- `icon_demand.png` - 📈 수요 아이콘

#### 🎯 큰 아이콘들 (64x64)
- `icon_*_large.png` - 모든 아이콘의 큰 버전

#### 🔘 버튼 이미지
- `button_bg.png` - 기본 버튼 배경
- `button_success.png` - 성공 버튼 배경
- `button_danger.png` - 위험 버튼 배경

## 🎨 현재 적용된 부분

### ✅ 메인 그래픽 영역
```css
.graphics-placeholder {
    background: url('/static/images/chicken_shop_bg.png') center/cover;
}

.boss-character {
    background: url('/static/images/boss_character_small.png') center/contain no-repeat;
}
```

**위치**: 화면 중앙의 메인 영역
**효과**: 치킨집 배경 + 우측 하단에 사장 캐릭터

### ✅ CSS 아이콘 클래스 준비
```css
.icon-img.icon-money { background-image: url('/static/images/icon_money.png'); }
```

**사용법**: 
```html
<!-- 이모지 대신 이미지 아이콘 사용시 -->
<div class="icon-img icon-money"></div>
<div class="icon-img icon-chicken large"></div>
```

## 🚀 향후 실제 이미지 교체 계획

### 1단계: 메인 캐릭터 교체 🎭
- **현재**: 간단한 도형 조합 캐릭터
- **목표**: 미소녀 게임 스타일의 치킨집 사장님
- **교체 위치**: `static/images/boss_character_small.png`

### 2단계: 치킨집 배경 교체 🏪
- **현재**: 단순한 그라데이션 + 테두리
- **목표**: 실제 치킨집 내부 모습 (카운터, 주방, 테이블 등)
- **교체 위치**: `static/images/chicken_shop_bg.png`

### 3단계: UI 아이콘 교체 🎯
- **현재**: 단색 배경 + 텍스트
- **목표**: 세련된 벡터 아이콘들
- **교체 위치**: `static/images/icon_*.png`

### 4단계: 버튼 스타일링 🔘
- **현재**: CSS 그라데이션
- **목표**: 게이밍 감성의 버튼 이미지
- **교체 위치**: `static/images/button_*.png`

## 💡 이미지 사용 가이드

### 권장 이미지 규격
- **메인 배경**: 800x600 (16:12 비율)
- **캐릭터**: 150x150 (정사각형, PNG 투명 배경)
- **작은 아이콘**: 32x32 (정사각형)
- **큰 아이콘**: 64x64 (정사각형)
- **버튼 배경**: 200x50 (4:1 비율)

### 색상 팔레트 (현재 UI와 매칭)
- **메인 오렌지**: #ff6b35
- **웜 옐로우**: #ffd700
- **배경 크림**: #fff8e1
- **텍스트 브라운**: #2c1810
- **성공 그린**: #27ae60
- **위험 레드**: #e74c3c

### 파일 교체 방법
1. 동일한 파일명으로 `static/images/` 폴더에 덮어쓰기
2. 웹 서버 재시작 (캐시 클리어)
3. 브라우저에서 Ctrl+F5로 강제 새로고침

## 🎮 테스트 방법
```bash
cd web_prototype
python main.py
```

웹브라우저에서 `http://localhost:8000` 접속하여 확인

## 📝 추가 개선 아이디어

### 애니메이션 효과 🎬
- 캐릭터 blink 애니메이션
- 치킨 요리할 때 연기 효과
- 손님이 올 때 캐릭터 움직임

### 인터랙티브 요소 🖱️
- 캐릭터 클릭시 반응
- 배경 요소들과 상호작용
- 상태에 따른 캐릭터 표정 변화

### 다양한 상황별 이미지 🎭
- 바쁠 때 / 한가할 때 다른 배경
- 성공/실패에 따른 캐릭터 변화
- 시간대별 조명 효과 (아침/점심/저녁)

## 🎭 1인칭 비주얼 노벨 대화 시스템

### ✅ 구현 완료된 기능들
- **1인칭 시점**: 주인공(사장님)은 화면에 표시되지 않음
- **레이어 시스템**: 배경 + NPC 캐릭터 + UI 오버레이 + 대화창
- **캐릭터 시스템**: 좌/중/우 3개 위치, 다양한 표정 지원
- **대화창**: 타이핑 효과, 1인칭 아바타(치킨 아이콘), 자동/수동 진행
- **게임 연동**: 상태에 따른 자동 대화 트리거
- **자동 캐릭터 관리**: NPC는 대화 후 자동으로 사라짐

### 🎨 추가된 캐릭터 이미지들
- `boss_character_happy.png` - 기쁜 표정 사장님
- `boss_character_sad.png` - 슬픈 표정 사장님
- `boss_character_angry.png` - 화난 표정 사장님
- `customer_character.png` - 손님 캐릭터
- `customer_character_small.png` - 작은 손님 캐릭터

### 📝 대화 스크립트 예시
```javascript
// 1인칭 주인공 대사 (화면에 캐릭터 표시 안됨)
{
    speaker: "boss",
    position: "center", 
    emotion: "happy",
    text: "드디어 내 치킨집을 오픈했다!"
}

// NPC 대사 (화면에 캐릭터 표시됨)
{
    speaker: "customer",
    position: "center",
    emotion: "happy", 
    text: "안녕하세요! 치킨 주문하러 왔어요!"
}
```

### 🎬 대화 시나리오들
- **게임 시작**: 웰컴 → 첫 손님 등장
- **바쁜 날**: 손님 25명 이상 시 손님 등장 대화
- **한가한 날**: 손님 5명 미만 시 혼잣말
- **성공 순간**: 고매출 + 고평판 시 기쁨 표현
- **위기 상황**: 자금부족, 고스트레스 시 경고
- **액션 반응**: 경영 액션 실행 시 30% 확률로 반응

### 🎮 조작 방법
- **Enter/Space**: 대화 계속
- **Escape**: 대화 건너뛰기
- **자동 트리거**: 게임 상태에 따라 자동 대화 실행

### 🔧 확장 방법
```javascript
// 새 캐릭터 추가
DialogueSystem.addCharacter('새캐릭터', {
    name: "새로운 캐릭터",
    avatar: "/static/images/new_character_small.png",
    images: { default: "/static/images/new_character.png" }
});

// 새 대화 스크립트 추가  
DialogueSystem.addCustomDialogue('새대화', [
    { speaker: "새캐릭터", position: "left", text: "안녕하세요!" }
]);
```

---

**🔥 핵심 포인트**: 
1. **완전한 1인칭 비주얼 노벨 시스템** - 플레이어 = 주인공 몰입감 극대화
2. **스마트 캐릭터 관리** - NPC 자동 등장/퇴장, 표정 변화
3. **게임과 완벽 연동** - 상황별 자동 대화 트리거 (12가지 시나리오)
4. **실제 이미지 교체만 하면 완성** - 파일명 동일하게 덮어쓰기
5. **확장성** - 새 캐릭터, 새 대화 쉽게 추가 가능
6. **몰입감 있는 UI** - 1인칭 아바타(치킨 아이콘), 1인칭 대사 
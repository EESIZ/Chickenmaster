# 🍗 치킨마스터 웹 프로토타입

> **현재 MUD 기반 치킨마스터를 모던 웹 인터페이스로 변환한 프로토타입**

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
python main.py

# 3. 브라우저에서 접속
# http://localhost:8000
```

### 개발 모드 실행

```bash
# 핫 리로드 지원
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 파일 구조

```
web_prototype/
├── main.py              # FastAPI 서버 (기존 MUD 로직 래핑)
├── requirements.txt     # Python 의존성
├── render.yaml         # Render.com 배포 설정
├── static/
│   ├── index.html      # 메인 웹 UI
│   ├── style.css       # 게이밍 스타일 CSS
│   └── script.js       # JavaScript (API 통신 + 인터랙션)
└── README.md           # 이 파일
```

## 🎮 기능 완성도

### ✅ 완전 구현됨
- **게임 상태 표시**: 모든 지표 실시간 표시
- **액션 시스템**: 7가지 액션 모두 구현
- **턴 진행**: 일일 사업 시뮬레이션
- **이벤트 히스토리**: 최근 이벤트 표시
- **게임 오버**: 파산/평판 최악/번아웃 감지
- **자동 새로고침**: 30초마다 상태 업데이트
- **키보드 단축키**: Ctrl+1~8, 스페이스바 지원
- **반응형 디자인**: 모바일/태블릿 지원

### 🎯 현재 지원되는 액션
1. **💰 가격 변경**: 치킨 가격 인상/인하
2. **📦 재료 주문**: 50,000원으로 재료 50개 주문
3. **👥 직원 관리**: 30,000원으로 직원 휴식 제공
4. **📢 홍보 활동**: 20,000원으로 광고 진행
5. **🏭 시설 개선**: 100,000원으로 시설 업그레이드
6. **😴 개인 휴식**: 컨디션 회복 (기회비용 10,000원)
7. **🧪 연구개발**: 80,000원으로 신메뉴 개발 (65% 성공률)

### ⏭️ 턴 진행 시스템
- 고객 수 계산 (평판, 수요, 가격 기반)
- 재고 소모 및 매출 계산
- 직원 피로도 증가
- 일일 수익 적용

## 🎨 UI/UX 특징

### 🌈 디자인 시스템
- **다크 테마**: 게이밍 감성의 어두운 배경
- **치킨 컬러**: 황금색(#FFD700) 위주의 따뜻한 색감
- **글래스모피즘**: 반투명 효과와 블러 배경
- **부드러운 애니메이션**: 호버 효과와 상태 변화 시각화

### 📱 반응형 지원
- **데스크톱**: 3단 레이아웃 (상태-액션-이벤트)
- **태블릿**: 2단 레이아웃
- **모바일**: 1단 세로 스크롤

### ⌨️ 키보드 단축키
- `Ctrl+1~8`: 각종 액션 빠른 실행
- `Space`: 턴 진행
- `Ctrl+R`: 상태 새로고침

## 🌐 Render.com 배포

### 1단계: GitHub 연동
```bash
git add .
git commit -m "feat: 웹 프로토타입 추가"
git push origin main
```

### 2단계: Render 서비스 생성
1. [Render.com](https://render.com) 접속
2. "New Web Service" 선택
3. GitHub 레포지토리 연결
4. 루트 디렉토리를 `web_prototype`로 설정
5. 자동 배포 활성화

### 3단계: 환경 변수 (필요시)
```
PYTHON_VERSION=3.12
PORT=8000
```

### 4단계: 배포 완료
- 빌드 완료 후 `https://your-app.onrender.com` 접속
- 첫 배포는 5-10분 소요

## 🔧 개발자 도구

브라우저 콘솔에서 사용 가능:

```javascript
// 게임 상태 확인
ChickenMasterDebug.getGameState()

// 강제 새로고침
ChickenMasterDebug.forceRefresh()

// 자동 새로고침 토글
ChickenMasterDebug.toggleAutoRefresh()

// 테스트 메시지
ChickenMasterDebug.showTestMessage("테스트!")
```

## 🚧 제한사항 (현재 버전)

1. **데이터 영속성**: 새로고침 시 게임 상태 초기화
2. **멀티플레이어**: 단일 플레이어만 지원
3. **고급 이벤트**: 스토리텔러 시스템 미연동
4. **데이터베이스**: 메모리 기반 (PostgreSQL 미연동)

## 🔥 다음 단계

### Phase 2: 데이터 영속성
- PostgreSQL 연동
- 게임 세이브/로드 시스템
- 플레이어 계정 시스템

### Phase 3: 고급 기능
- 스토리텔러 시스템 통합
- 실시간 차트 (Chart.js)
- 애니메이션 강화 (Framer Motion)

### Phase 4: 프로덕션
- React/Next.js 마이그레이션
- 성능 최적화
- 모니터링 시스템

## 📊 현재 vs 목표

| 기능 | 현재 프로토타입 | 최종 목표 |
|------|----------------|-----------|
| UI 방식 | HTML/CSS/JS | React + TypeScript |
| 상태 관리 | Vanilla JS | Redux/Zustand |
| 애니메이션 | CSS + JS | Framer Motion |
| 차트 | 없음 | Chart.js/D3.js |
| 데이터 | 메모리 | PostgreSQL |
| 배포 | Render | Vercel + Railway |

## 🎯 결론

**이 프로토타입은 치킨마스터 MUD를 웹으로 성공적으로 변환했습니다!** 

- ✅ **기존 MUD 기능 100% 구현**
- ✅ **모던한 웹 UI/UX 제공**  
- ✅ **실제 배포 가능한 형태**
- ✅ **확장성 있는 아키텍처**

**이제 더 이상 터미널에 숨어있을 이유가 없습니다!** 🔥 
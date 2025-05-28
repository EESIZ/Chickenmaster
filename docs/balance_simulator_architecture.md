# 이벤트 밸런스 시뮬레이터 아키텍처 문서

## 개요

이벤트 밸런스 시뮬레이터(`balance_simulator.py`)는 Chicken-RNG 게임의 이벤트 뱅크 밸런스를 시뮬레이션하고 분석하는 도구입니다. 이 도구는 다양한 시나리오에서 이벤트 발생과 선택에 따른 게임 상태 변화를 시뮬레이션하여 밸런스 문제를 식별하고 보고합니다.

## 핵심 철학

시뮬레이터는 Chicken-RNG의 핵심 철학을 반영합니다:

1. **정답 없음 (noRightAnswer)**: 트레이드오프 분석을 통해 선택지 간 명확한 우열이 없도록 설계
2. **완전 랜덤 드라마 (uncertainty)**: 불확실성 요소를 측정하고 분석하여 예측 불가능성 보장
3. **폐업 가능**: 파산율과 파괴율을 통해 게임 오버 가능성 분석
4. **행동 3개/일**: 일일 액션 제한을 시뮬레이션에 반영

## 주요 컴포넌트

### 1. SimulationConfig

시뮬레이션 설정을 관리하는 Pydantic 모델입니다.

```python
class SimulationConfig(BaseModel):
    iterations: int = Field(default=100, description="시뮬레이션 반복 횟수")
    turns_per_sim: int = Field(default=30, description="각 시뮬레이션의 턴 수")
    seed: Optional[int] = Field(default=None, description="랜덤 시드 (재현성)")
    bankruptcy_threshold: float = Field(default=-5000, description="파산 기준 자금")
    happiness_weight: float = Field(default=1.0, description="행복 지표 가중치")
    pain_weight: float = Field(default=1.0, description="고통 지표 가중치")
    cascade_depth_limit: int = Field(default=5, description="최대 연쇄 깊이")
    destruction_threshold: float = Field(default=0.05, description="허용 가능한 파괴율")
```

### 2. GameState

게임 상태를 나타내는 데이터 클래스입니다.

```python
@dataclass
class GameState:
    money: float = 1000.0
    happiness: float = 50.0
    pain: float = 50.0
    day: int = 1
    actions_left: int = 3
    metrics: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    triggered_events: Set[str] = field(default_factory=set)
    history: List[Dict[str, Any]] = field(default_factory=list)
```

### 3. EventSimulator

이벤트 시뮬레이션을 수행하는 핵심 클래스입니다.

```python
class EventSimulator:
    def __init__(self, events_dir: str, config: SimulationConfig):
        self.events_dir = Path(events_dir)
        self.config = config
        self.events = {}
        self.event_stats = defaultdict(lambda: defaultdict(int))
        self.cascade_stats = defaultdict(int)
        self.tradeoff_metrics = defaultdict(list)
        self.uncertainty_factors = defaultdict(list)
```

## 주요 기능

### 1. 이벤트 뱅크 로드 및 분석

```python
def _load_events(self) -> None:
    """이벤트 뱅크에서 이벤트 로드"""
```

### 2. 이벤트 시뮬레이션

```python
def simulate_game(self) -> Dict[str, Any]:
    """게임 시뮬레이션 실행"""
```

### 3. 밸런스 분석

```python
def analyze_balance(self, results: pd.DataFrame) -> Dict[str, Any]:
    """밸런스 분석"""
```

### 4. 트레이드오프 분석

```python
def noRightAnswer_analyze_tradeoffs(self) -> Dict[str, Any]:
    """트레이드오프 분석 (정답 없음 철학 반영)"""
```

### 5. 불확실성 분석

```python
def uncertainty_analyze_variability(self) -> Dict[str, Any]:
    """불확실성 분석 (완전 랜덤 드라마 철학 반영)"""
```

### 6. 시각화 및 보고서 생성

```python
def generate_visualizations(self, results: pd.DataFrame, output_dir: str) -> List[str]:
    """시뮬레이션 결과 시각화"""

def generate_report(self, results: pd.DataFrame, output_path: str) -> Dict[str, Any]:
    """밸런스 보고서 생성"""
```

## 시뮬레이션 프로세스

1. **초기화**: 이벤트 뱅크 로드 및 시뮬레이션 설정
2. **게임 시뮬레이션**: 지정된 턴 수만큼 게임 상태 시뮬레이션
   - **일일 시뮬레이션**: 3개의 액션 소비
   - **턴 시뮬레이션**: 이벤트 선택 및 효과 적용
   - **이벤트 연쇄**: 연쇄 이벤트 처리
3. **결과 분석**: 밸런스 메트릭 계산 및 문제 이벤트 식별
4. **보고서 생성**: CSV 및 JSON 보고서 생성, 시각화 파일 생성

## 밸런스 메트릭

1. **파산율**: 시뮬레이션에서 파산한 비율
2. **평균 생존 일수**: 시뮬레이션에서 평균적으로 생존한 일수
3. **행복/고통 균형 유지율**: 행복+고통=100 균형이 유지된 비율
4. **최대 연쇄 깊이**: 발생한 최대 이벤트 연쇄 깊이
5. **트레이드오프 명확성 점수**: 선택지 간 트레이드오프 명확성
6. **불확실성 변동성 점수**: 게임 상태의 예측 불가능성

## 문제 이벤트 식별

다음과 같은 문제가 있는 이벤트를 식별합니다:

1. **트리거 비율이 너무 높거나 낮은 이벤트**
2. **특정 선택지가 지나치게 자주 선택되는 이벤트**
3. **선택지 간 불균형이 심한 이벤트**

## 시각화

다음과 같은 시각화를 생성합니다:

1. **파산율 및 생존 일수 분포**
2. **최종 자금 분포**
3. **행복/고통 분포**
4. **연쇄 깊이 분포**
5. **이벤트 트리거 빈도**

## 사용 예시

```bash
python -m dev_tools.balance_simulator --input data/events_bank --output reports/balance_report.csv --iterations 1000 --turns 30 --seed 42 --visualize
```

## 확장성

시뮬레이터는 다음과 같은 방향으로 확장 가능합니다:

1. **추가 밸런스 메트릭**: 새로운 밸런스 메트릭 추가
2. **고급 시각화**: 인터랙티브 시각화 및 대시보드 추가
3. **자동 밸런싱**: 문제 이벤트 자동 조정 기능 추가
4. **시나리오 테스트**: 특정 시나리오에 대한 집중 테스트 기능 추가

## 테스트

시뮬레이터는 다음과 같은 테스트를 통해 검증됩니다:

1. **시뮬레이션 설정 유효성 검증**
2. **게임 상태 기본 기능**
3. **이벤트 시뮬레이터 초기화 및 이벤트 로드**
4. **조건 평가**
5. **트리거 가능한 이벤트 확인**
6. **선택지 선택 및 효과 적용**
7. **이벤트 연쇄 시뮬레이션**
8. **턴 및 일일 시뮬레이션**
9. **전체 게임 시뮬레이션**
10. **보고서 생성 및 시각화**

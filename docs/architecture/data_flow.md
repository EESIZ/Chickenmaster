# 데이터 흐름 아키텍처

## 개요

Chickenmaster 프로젝트는 엄격한 단방향 데이터 흐름을 따릅니다. 모든 게임 데이터는 외부 소스에서 읽기 전용으로 로드되며, 코드에서는 절대 데이터 소스를 수정하지 않습니다.

## 핵심 원칙

### 1. 읽기 전용 데이터 흐름

```
외부 데이터 소스 → 읽기 전용 어댑터 → 게임 로직
     ↑                    ↓
   수동 수정         불변 복사본 제공
```

**올바른 흐름:**
- 엑셀 파일 → ExcelGameDataProvider → GameInitializer → GameState
- JSON 파일 → JsonDataProvider → 게임 로직
- TOML 파일 → TomlDataProvider → 이벤트 엔진

**금지된 흐름:**
- ❌ 게임 로직 → 데이터 소스 수정
- ❌ 코드 → 엑셀 파일 생성/수정
- ❌ 런타임 → 설정 파일 변경

### 2. 데이터 소스별 수정 방법

| 데이터 소스 | 수정 방법 | 금지 사항 |
|------------|----------|----------|
| Excel 파일 | Excel, LibreOffice Calc | 코드에서 openpyxl 사용 |
| JSON 파일 | 텍스트 에디터, IDE | 코드에서 json.dump() |
| TOML 파일 | 텍스트 에디터 | 코드에서 toml.dump() |
| 이벤트 파일 | 수동 편집, 검증 도구 | 런타임 생성/수정 |

## 아키텍처 구성 요소

### 1. 데이터 제공자 인터페이스

```python
class GameDataProvider(Protocol):
    """읽기 전용 데이터 제공자 프로토콜"""
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        """불변 메트릭 데이터 반환"""
        ...
    
    def get_game_constants(self) -> Dict[str, Any]:
        """불변 상수 데이터 반환"""
        ...
    
    # 주의: 데이터 수정 메서드는 절대 포함하지 않음
    # ❌ def save_data(self, data) -> None: ...
    # ❌ def update_constants(self, updates) -> None: ...
```

### 2. 읽기 전용 어댑터

```python
class ExcelGameDataProvider(ReadOnlyDataProvider):
    """엑셀 기반 읽기 전용 데이터 제공자"""
    
    def __init__(self, excel_path: str):
        super().__init__(excel_path)
        self._validate_data_source()  # 파일 존재 및 형식 검증
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        # 1. 엑셀에서 데이터 읽기
        df = pd.read_excel(self.excel_path, sheet_name='Game_Metrics')
        
        # 2. 불변 객체로 변환
        metrics = {name: GameMetric(...) for ...}
        
        # 3. 불변 복사본 반환
        return self._ensure_immutable_copy(metrics)
    
    # 주의: 엑셀 파일 수정 메서드는 절대 구현하지 않음
    # ❌ def save_to_excel(self, data) -> None: ...
    # ❌ def update_sheet(self, sheet_name, data) -> None: ...
```

### 3. 불변 데이터 객체

```python
@dataclass(frozen=True)
class GameMetric:
    """불변 게임 메트릭"""
    base_value: float
    min_value: float
    max_value: float
    description: str
    
    # frozen=True로 인해 수정 불가능
    # metric.base_value = 100  # ❌ FrozenInstanceError

@dataclass(frozen=True)
class TradeoffRelationship:
    """불변 트레이드오프 관계"""
    target_metric: str
    impact_factor: float
    description: str
```

## 데이터 무결성 보장

### 1. 컴파일 타임 보장

```python
# 타입 힌트로 읽기 전용 명시
def get_game_constants(self) -> Dict[str, Any]:  # 반환만 가능
    """읽기 전용 상수 반환"""
    pass

# 수정 메서드는 타입에서 제외
# def save_constants(self, data: Dict[str, Any]) -> None:  # ❌ 금지
```

### 2. 런타임 보장

```python
class ReadOnlyDataProvider(ABC):
    def _ensure_immutable_copy(self, data: Any) -> Any:
        """깊은 복사로 불변성 보장"""
        import copy
        return copy.deepcopy(data)
    
    def _validate_data_source(self) -> None:
        """데이터 소스 유효성 검증"""
        if not Path(self._data_source_path).exists():
            raise FileNotFoundError(
                f"데이터 파일이 없습니다: {self._data_source_path}\n"
                f"⚠️ 코드에서 생성하지 마세요. 외부 도구를 사용하세요."
            )
```

### 3. 아키텍처 검증

```python
def validate_data_flow_architecture():
    """데이터 흐름 아키텍처 검증"""
    
    # 1. 데이터 제공자에 수정 메서드가 없는지 확인
    provider_methods = dir(ExcelGameDataProvider)
    forbidden_methods = ['save', 'update', 'write', 'modify', 'set']
    
    for method in provider_methods:
        for forbidden in forbidden_methods:
            if forbidden in method.lower():
                raise ArchitectureViolation(
                    f"데이터 제공자에 수정 메서드 발견: {method}"
                )
    
    # 2. 불변 객체 검증
    assert GameMetric.__dataclass_params__.frozen == True
    assert TradeoffRelationship.__dataclass_params__.frozen == True
```

## 실제 사용 예시

### 1. 올바른 사용법

```python
# ✅ 올바른 데이터 로드
provider = ExcelGameDataProvider("data/game_initial_values.xlsx")
metrics = provider.get_game_metrics()  # 불변 복사본 반환

# ✅ 데이터 사용 (읽기만)
money_metric = metrics['Money']
initial_money = money_metric.base_value

# ✅ 게임 상태 초기화
initializer = GameInitializer(provider)
game_state = initializer.initialize()
```

### 2. 금지된 사용법

```python
# ❌ 데이터 수정 시도
metrics['Money'].base_value = 50000  # FrozenInstanceError
metrics['Money'] = new_metric        # 복사본이므로 원본에 영향 없음

# ❌ 엑셀 파일 수정 시도
provider.save_to_excel(new_data)     # 메서드 자체가 존재하지 않음
wb = openpyxl.load_workbook(path)    # 금지된 패턴
wb.save()                            # 금지된 패턴
```

### 3. 데이터 수정이 필요한 경우

```python
# ✅ 올바른 방법: 외부 도구 사용
# 1. Excel에서 data/game_initial_values.xlsx 열기
# 2. Game_Constants 시트에서 값 수정
# 3. 파일 저장
# 4. 게임 재시작하여 새 값 로드

# ❌ 잘못된 방법: 코드에서 수정
# provider.update_constant('STARTING_MONEY', 50000)  # 존재하지 않음
```

## 예외 상황 처리

### 1. 데이터 소스 누락

```python
try:
    provider = ExcelGameDataProvider("missing_file.xlsx")
except FileNotFoundError as e:
    print(f"데이터 파일이 없습니다: {e}")
    print("⚠️ 코드에서 파일을 생성하지 마세요.")
    print("Excel에서 템플릿을 생성하고 데이터를 입력하세요.")
```

### 2. 데이터 형식 오류

```python
try:
    metrics = provider.get_game_metrics()
except ValueError as e:
    print(f"데이터 형식 오류: {e}")
    print("Excel 파일의 시트 구조를 확인하세요.")
```

## 마이그레이션 가이드

### 기존 코드에서 새 아키텍처로

```python
# Before (잘못된 패턴)
def update_game_constants(new_values):
    wb = openpyxl.load_workbook("data/constants.xlsx")
    ws = wb["Constants"]
    for key, value in new_values.items():
        # 셀 수정...
    wb.save()

# After (올바른 패턴)
def get_game_constants():
    provider = ExcelGameDataProvider("data/game_initial_values.xlsx")
    return provider.get_game_constants()

# 수정이 필요한 경우:
# 1. Excel에서 직접 수정
# 2. 게임 재시작
```

## 결론

이 아키텍처는 다음을 보장합니다:

1. **데이터 무결성**: 코드에서 실수로 데이터를 변경할 수 없음
2. **명확한 책임**: 데이터 수정은 외부 도구, 읽기는 코드
3. **예측 가능성**: 데이터 흐름이 단방향으로 명확함
4. **유지보수성**: 데이터와 로직이 분리되어 관리 용이

⚠️ **중요**: 이 원칙을 위반하는 코드는 아키텍처 검증에서 실패하며, 코드 리뷰에서 거부됩니다. 
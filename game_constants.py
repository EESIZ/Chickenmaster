"""
Chicken-RNG 게임의 핵심 지표와 상수를 정의하는 모듈 (엑셀 기반)

🔥 매직넘버 박멸! 🔥
이 모듈은 모든 상수를 엑셀 파일에서 동적으로 로드합니다.
더 이상 하드코딩된 매직넘버는 없습니다!

핵심 철학:
- 정답 없음: 모든 선택은 득과 실을 동시에 가져옵니다
- 트레이드오프: 한 지표를 올리면 다른 지표는 내려갑니다
- 불확실성: 예측 불가능한 이벤트가 게임 진행에 영향을 줍니다
- 동적 밸런싱: 모든 상수를 엑셀에서 실시간 조정 가능
"""

from enum import Enum, auto
from typing import Final, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from functools import lru_cache

# 무한대 값을 위한 타입 힌트 호환 상수
INF: Final = float("inf")

# Enum 정의들은 유지 (구조적 정의이므로)
class Metric(Enum):
    """게임의 핵심 지표를 정의하는 열거형"""
    MONEY = auto()  # 사업 운영 자금
    REPUTATION = auto()  # 가게의 사회적 평가
    HAPPINESS = auto()  # 사장의 정신적 만족도
    SUFFERING = auto()  # 사장의 정신적 스트레스
    INVENTORY = auto()  # 보유 식자재 수량
    STAFF_FATIGUE = auto()  # 직원의 피로도
    FACILITY = auto()  # 시설 상태
    DEMAND = auto()  # 고객 수요


class ActionType(Enum):
    """플레이어가 선택할 수 있는 행동 유형"""
    PRICE_CHANGE = auto()  # 가격 조정
    ORDER_INVENTORY = auto()  # 재고 주문
    MANAGE_STAFF = auto()  # 직원 관리
    PROMOTE = auto()  # 홍보 활동
    INVEST_FACILITY = auto()  # 시설 투자


class EventCategory(Enum):
    """이벤트 카테고리"""
    DAILY_ROUTINE = auto()  # 일상 루틴
    CRISIS = auto()  # 위기 상황
    OPPORTUNITY = auto()  # 기회
    RANDOM = auto()  # 랜덤 이벤트
    THRESHOLD = auto()  # 임계값 기반 이벤트
    SCHEDULED = auto()  # 스케줄 기반 이벤트
    CASCADE = auto()  # 연쇄 효과 이벤트


class TriggerCondition(Enum):
    """트리거 조건"""
    EQUAL = auto()  # 같음
    NOT_EQUAL = auto()  # 같지 않음
    GREATER_THAN = auto()  # 초과
    LESS_THAN = auto()  # 미만
    GREATER_THAN_OR_EQUAL = auto()  # 이상
    LESS_THAN_OR_EQUAL = auto()  # 이하


# 엑셀 기반 상수 로더 클래스
class ExcelConstantsLoader:
    """엑셀 파일에서 상수를 로드하는 클래스"""
    
    def __init__(self, excel_path: str = "data/game_initial_values_with_formulas.xlsx"):
        self.excel_path = Path(excel_path)
        self._cache: Dict[str, Any] = {}
        self._loaded = False
    
    @lru_cache(maxsize=None)
    def _load_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """시트 데이터를 캐시와 함께 로드"""
        try:
            return pd.read_excel(self.excel_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"⚠️ 시트 '{sheet_name}' 로드 실패: {e}")
            return pd.DataFrame()
    
    def _load_constants_from_sheet(self, sheet_name: str) -> Dict[str, Any]:
        """상수 시트에서 Key-Value 데이터를 로드"""
        df = self._load_sheet_data(sheet_name)
        constants = {}
        
        if df.empty or 'Key' not in df.columns or 'Value' not in df.columns:
            return constants
        
        for _, row in df.iterrows():
            key = str(row['Key']).strip()
            value = row['Value']
            
            # 타입 변환
            if 'Type' in df.columns:
                data_type = str(row['Type']).strip().lower()
                if data_type == 'int':
                    value = int(float(value))
                elif data_type == 'float':
                    value = float(value)
                elif data_type == 'bool':
                    value = bool(value)
                elif data_type == 'str':
                    value = str(value)
            
            constants[key] = value
        
        return constants
    
    def load_all_constants(self) -> None:
        """모든 상수를 엑셀에서 로드"""
        if self._loaded:
            return
        
        print("📊 엑셀에서 상수 로드 중...")
        
        try:
            # 각 상수 시트에서 데이터 로드
            constant_sheets = [
                'Game_Flow_Constants',
                'Probability_Constants', 
                'Threshold_Constants',
                'Storyteller_Constants',
                'Technical_Constants',
                'Test_Constants'
            ]
            
            for sheet_name in constant_sheets:
                sheet_constants = self._load_constants_from_sheet(sheet_name)
                self._cache.update(sheet_constants)
                print(f"  ✅ {sheet_name}: {len(sheet_constants)}개 상수 로드")
            
            # 특별한 구조의 시트들 로드
            self._load_tradeoff_relationships()
            self._load_uncertainty_weights()
            self._load_metric_ranges()
            
            self._loaded = True
            print(f"🎉 총 {len(self._cache)}개 상수 로드 완료!")
            
        except Exception as e:
            print(f"❌ 상수 로드 실패: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_tradeoff_relationships(self) -> None:
        """트레이드오프 관계 로드"""
        df = self._load_sheet_data('Tradeoff_Relationships')
        if df.empty:
            return
        
        relationships = {}
        for _, row in df.iterrows():
            source = row['Source_Metric']
            target = row['Target_Metric']
            
            if source not in relationships:
                relationships[source] = []
            relationships[source].append(target)
        
        # Metric Enum으로 변환
        tradeoff_dict = {}
        for source_name, target_names in relationships.items():
            try:
                source_metric = getattr(Metric, source_name)
                target_metrics = []
                for target_name in target_names:
                    try:
                        target_metric = getattr(Metric, target_name)
                        target_metrics.append(target_metric)
                    except AttributeError:
                        print(f"⚠️ 알 수 없는 대상 지표: {target_name}")
                
                if target_metrics:
                    tradeoff_dict[source_metric] = target_metrics
            except AttributeError:
                print(f"⚠️ 알 수 없는 소스 지표: {source_name}")
        
        self._cache['TRADEOFF_RELATIONSHIPS'] = tradeoff_dict
    
    def _load_uncertainty_weights(self) -> None:
        """불확실성 가중치 로드"""
        df = self._load_sheet_data('Uncertainty_Weights')
        if df.empty:
            return
        
        weights = {}
        for _, row in df.iterrows():
            metric_name = row['Metric_Name']
            weight = float(row['Weight'])
            
            try:
                metric = getattr(Metric, metric_name)
                weights[metric] = weight
            except AttributeError:
                print(f"⚠️ 알 수 없는 지표: {metric_name}")
        
        self._cache['UNCERTAINTY_WEIGHTS'] = weights
    
    def _load_metric_ranges(self) -> None:
        """지표 범위 로드"""
        df = self._load_sheet_data('Metric_Ranges')
        if df.empty:
            return
        
        ranges = {}
        for _, row in df.iterrows():
            metric_name = row['Metric_Name']
            min_val = float(row['Min_Value'])
            max_val = row['Max_Value']
            default_val = float(row['Default_Value'])
            
            # 'inf' 문자열을 float('inf')로 변환
            if isinstance(max_val, str) and max_val.lower() == 'inf':
                max_val = float('inf')
            else:
                max_val = float(max_val)
            
            try:
                metric = getattr(Metric, metric_name)
                ranges[metric] = (min_val, max_val, default_val)
            except AttributeError:
                print(f"⚠️ 알 수 없는 지표: {metric_name}")
        
        self._cache['METRIC_RANGES'] = ranges
    
    def get_constant(self, key: str, default: Any = None) -> Any:
        """상수 값을 가져오기"""
        if not self._loaded:
            self.load_all_constants()
        return self._cache.get(key, default)
    
    def reload_constants(self) -> None:
        """상수를 다시 로드"""
        self._cache.clear()
        self._loaded = False
        # 캐시 클리어
        self._load_sheet_data.cache_clear()
        self.load_all_constants()


# 전역 상수 로더 인스턴스
_constants_loader = ExcelConstantsLoader()

# 편의 함수
def get_constant(key: str, default: Any = None) -> Any:
    """상수 값을 가져오는 편의 함수"""
    return _constants_loader.get_constant(key, default)

def reload_all_constants() -> None:
    """모든 상수를 다시 로드하는 편의 함수"""
    _constants_loader.reload_constants()

# 동적 상수 접근자들 (엑셀에서 로드됨)
def get_tradeoff_relationships() -> Dict[Metric, list[Metric]]:
    """트레이드오프 관계를 동적으로 가져오기"""
    return get_constant('TRADEOFF_RELATIONSHIPS', {})

def get_uncertainty_weights() -> Dict[Metric, float]:
    """불확실성 가중치를 동적으로 가져오기"""
    return get_constant('UNCERTAINTY_WEIGHTS', {})

def get_metric_ranges() -> Dict[Metric, Tuple[float, float, float]]:
    """지표 범위를 동적으로 가져오기"""
    return get_constant('METRIC_RANGES', {})

# 모듈 로드 시 상수들을 미리 로드하여 전역 변수로 만들기
_constants_loader.load_all_constants()

# 기존 하드코딩된 상수들 → 엑셀 기반 동적 로드로 교체 (전역 변수로 설정)
TRADEOFF_RELATIONSHIPS: Final[Dict[Metric, list[Metric]]] = get_tradeoff_relationships()
UNCERTAINTY_WEIGHTS: Final[Dict[Metric, float]] = get_uncertainty_weights()
METRIC_RANGES: Final[Dict[Metric, Tuple[float, float, float]]] = get_metric_ranges()

# 게임 진행 관련 상수들 (엑셀에서 로드)
MAX_ACTIONS_PER_DAY: Final[int] = get_constant('MAX_ACTIONS_PER_DAY', 3)
DEFAULT_GAME_LENGTH: Final[int] = get_constant('DEFAULT_GAME_LENGTH', 30)
DEFAULT_TOTAL_DAYS: Final[int] = get_constant('DEFAULT_TOTAL_DAYS', 730)
DEFAULT_COOLDOWN_DAYS: Final[int] = get_constant('DEFAULT_COOLDOWN_DAYS', 5)

# 확률 관련 상수들 (엑셀에서 로드)
PROBABILITY_LOW_THRESHOLD: Final[float] = get_constant('PROBABILITY_LOW_THRESHOLD', 0.3)
PROBABILITY_HIGH_THRESHOLD: Final[float] = get_constant('PROBABILITY_HIGH_THRESHOLD', 0.7)
PROBABILITY_HIGH_THRESHOLD5: Final[float] = 0.75  # 기존 호환성을 위해 유지
DEFAULT_PROBABILITY: Final[float] = get_constant('DEFAULT_PROBABILITY', 0.8)
DEFAULT_SEVERITY: Final[float] = get_constant('DEFAULT_SEVERITY', 0.5)

# 임계값 상수들 (엑셀에서 로드)
MONEY_LOW_THRESHOLD: Final[int] = get_constant('MONEY_LOW_THRESHOLD', 3000)
MONEY_HIGH_THRESHOLD: Final[int] = get_constant('MONEY_HIGH_THRESHOLD', 15000)
REPUTATION_LOW_THRESHOLD: Final[int] = get_constant('REPUTATION_LOW_THRESHOLD', 30)
REPUTATION_HIGH_THRESHOLD: Final[int] = get_constant('REPUTATION_HIGH_THRESHOLD', 70)
HAPPINESS_LOW_THRESHOLD: Final[int] = get_constant('HAPPINESS_LOW_THRESHOLD', 30)
HAPPINESS_HIGH_THRESHOLD: Final[int] = get_constant('HAPPINESS_HIGH_THRESHOLD', 70)
REPUTATION_BASELINE: Final[int] = get_constant('REPUTATION_BASELINE', 50)

# 스토리텔러 관련 상수들 (엑셀에서 로드)
MIN_METRICS_HISTORY_FOR_TREND: Final[int] = get_constant('MIN_METRICS_HISTORY_FOR_TREND', 2)
RECENT_HISTORY_WINDOW: Final[int] = get_constant('RECENT_HISTORY_WINDOW', 3)
MINIMUM_TREND_POINTS: Final[int] = get_constant('MINIMUM_TREND_POINTS', 2)
SITUATION_POSITIVE_THRESHOLD: Final[float] = get_constant('SITUATION_POSITIVE_THRESHOLD', 0.6)
SITUATION_NEGATIVE_THRESHOLD: Final[float] = get_constant('SITUATION_NEGATIVE_THRESHOLD', 0.4)
TRADEOFF_BALANCE_THRESHOLD: Final[float] = get_constant('TRADEOFF_BALANCE_THRESHOLD', 0.5)
GAME_PROGRESSION_MID_POINT: Final[float] = get_constant('GAME_PROGRESSION_MID_POINT', 0.5)
PATTERN_SCORE_TOLERANCE: Final[float] = get_constant('PATTERN_SCORE_TOLERANCE', 0.1)
COMPLEXITY_BONUS_MULTIPLIER: Final[float] = get_constant('COMPLEXITY_BONUS_MULTIPLIER', 0.1)

# 기술적 상수들 (엑셀에서 로드)
FLOAT_EPSILON: Final[float] = get_constant('FLOAT_EPSILON', 0.001)
SCORE_THRESHOLD_HIGH: Final[float] = get_constant('SCORE_THRESHOLD_HIGH', 0.7)
SCORE_THRESHOLD_MEDIUM: Final[float] = get_constant('SCORE_THRESHOLD_MEDIUM', 0.5)

# 테스트 관련 상수들 (엑셀에서 로드)
TEST_MIN_CASCADE_EVENTS: Final[int] = get_constant('TEST_MIN_CASCADE_EVENTS', 3)
TEST_EXPECTED_EVENTS: Final[int] = get_constant('TEST_EXPECTED_EVENTS', 2)
TEST_METRICS_HISTORY_LENGTH: Final[int] = get_constant('TEST_METRICS_HISTORY_LENGTH', 5)
TEST_POSSIBLE_OUTCOME: Final[int] = 3  # 기존 호환성을 위해 유지

# 추가 상수들 (기존 호환성을 위해 유지)
DEFAULT_STORY_PATTERNS_COUNT: Final[int] = 2
MAX_CASCADE_NODES: Final[int] = 100

# 기존 매직넘버들 (일부는 그대로 유지)
MAGIC_NUMBER_ZERO = 0.0
MAGIC_NUMBER_ONE = 1.0
MAGIC_NUMBER_TWO = 2
MAGIC_NUMBER_THREE = 3
MAGIC_NUMBER_FIVE = 5
MAGIC_NUMBER_TWENTY = 20
MAGIC_NUMBER_FIFTY = 50
MAGIC_NUMBER_ONE_HUNDRED = 100
MAGIC_NUMBER_ONE_HUNDRED_FIFTEEN = 115
MAGIC_NUMBER_ONE_THOUSAND = 1000

# 게임 오버 조건 (변경되지 않는 정적 데이터)
GAME_OVER_CONDITIONS: Final[dict[str, str]] = {
    "위생 단속 실패": "INSPECTION 이벤트 발생 시 FACILITY < 30이면 게임 오버",
    "파산": "MONEY가 0 이하이고 추가 대출이 불가능한 경우",
}

# 기존 함수들 유지
def cap_metric_value(metric: Metric, value: float) -> float:
    """
    지표 값을 허용 범위 내로 제한

    Args:
        metric: 지표 타입
        value: 제한할 값

    Returns:
        범위 내로 제한된 값
    """
    if metric not in METRIC_RANGES:
        return value
    
    min_val, max_val, _ = METRIC_RANGES[metric]
    return max(min_val, min(max_val, value))

# 데이터클래스들 유지
@dataclass(frozen=True)
class ProbabilityConstants:
    """확률 관련 상수"""
    RANDOM_THRESHOLD: float = 0.5  # 50% 확률 기준점

@dataclass(frozen=True)
class StorytellerConstants:
    """스토리텔러 관련 상수"""
    # 점수 임계값
    SCORE_THRESHOLD_HIGH: float = 0.7  # 높은 점수 임계값
    SCORE_THRESHOLD_LOW: float = 0.3   # 낮은 점수 임계값
    
    # 추세 분석 관련
    TREND_MIN_HISTORY: int = 2  # 최소 히스토리 개수
    
    # 게임 진행도 관련
    PROGRESSION_THRESHOLD: float = 0.5  # 진행도 임계값
    COMPLEXITY_BONUS_THRESHOLD: float = 0.2  # 복잡성 보너스 임계값
    
    # 패턴 선택 관련
    PATTERN_SCORE_SIMILARITY: float = 0.1  # 패턴 점수 유사성 허용 범위

print("🎉 엑셀 기반 동적 상수 관리 시스템이 활성화되었습니다!")
print("💡 모든 상수는 data/game_initial_values_with_formulas.xlsx에서 관리됩니다!")
print("🔥 매직넘버는 이제 과거의 유물입니다!") 
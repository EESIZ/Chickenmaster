"""
엑셀 기반 통합 상수 관리 시스템

모든 게임 상수를 엑셀 파일에서 읽어와 중앙 관리하는 시스템입니다.
매직넘버 제거와 동적 밸런싱을 위한 핵심 컴포넌트입니다.
"""

from typing import Any, Dict, Optional, TypeVar, Generic, Union
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from abc import ABC, abstractmethod

from backend.app.core.domain.interfaces.data_provider import GameDataProvider

T = TypeVar('T')


@dataclass(frozen=True)
class ConstantDefinition:
    """상수 정의 정보"""
    key: str
    value: Any
    data_type: str
    category: str
    description: str
    is_cached: bool = True


class TypedConstant(Generic[T]):
    """타입 안전성을 보장하는 상수 래퍼"""
    
    def __init__(self, key: str, expected_type: type[T], default: T, category: str = "general"):
        self.key = key
        self.expected_type = expected_type
        self.default = default
        self.category = category
    
    def get(self, provider: 'ExcelConstantsProvider') -> T:
        """상수 값을 타입 안전하게 가져옵니다."""
        try:
            value = provider.get_constant(self.key, self.default)
            if not isinstance(value, self.expected_type):
                # 타입 변환 시도
                if self.expected_type == float and isinstance(value, (int, str)):
                    return float(value)
                elif self.expected_type == int and isinstance(value, (float, str)):
                    return int(value)
                elif self.expected_type == str:
                    return str(value)
                else:
                    raise TypeError(
                        f"상수 '{self.key}': {self.expected_type.__name__} 타입을 기대했지만 "
                        f"{type(value).__name__} 타입을 받았습니다."
                    )
            return value
        except Exception as e:
            print(f"상수 '{self.key}' 로드 실패, 기본값 사용: {self.default} (오류: {e})")
            return self.default


class ExcelConstantsProvider:
    """엑셀 파일 기반 상수 제공자"""
    
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self._constants_cache: Dict[str, Any] = {}
        self._definitions_cache: Dict[str, ConstantDefinition] = {}
        self._is_loaded = False
    
    def load_data(self) -> Dict[str, Any]:
        """엑셀에서 모든 상수 데이터를 로드합니다."""
        if self._is_loaded and self._constants_cache:
            return self._constants_cache.copy()
        
        try:
            # 상수 시트들 로드
            constants_data = self._load_constants_sheets()
            
            self._constants_cache = constants_data
            self._is_loaded = True
            
            return constants_data.copy()
            
        except Exception as e:
            print(f"엑셀 상수 로드 실패: {e}")
            return {}
    
    def _load_constants_sheets(self) -> Dict[str, Any]:
        """상수 관련 시트들을 로드합니다."""
        constants = {}
        
        try:
            # 상수 시트 목록
            constant_sheets = [
                'Core_Constants',
                'Magic_Numbers', 
                'Test_Constants',
                'UI_Constants',
                'Performance_Constants'
            ]
            
            for sheet_name in constant_sheets:
                try:
                    df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                    sheet_constants = self._parse_constants_sheet(df, sheet_name)
                    constants.update(sheet_constants)
                except Exception as sheet_error:
                    print(f"시트 '{sheet_name}' 로드 실패: {sheet_error}")
                    continue
            
            return constants
            
        except Exception as e:
            print(f"상수 시트 로드 실패: {e}")
            return {}
    
    def _parse_constants_sheet(self, df: pd.DataFrame, category: str) -> Dict[str, Any]:
        """상수 시트를 파싱합니다."""
        constants = {}
        
        required_columns = ['Key', 'Value', 'Type', 'Description']
        if not all(col in df.columns for col in required_columns):
            print(f"시트 '{category}'에 필수 컬럼이 없습니다: {required_columns}")
            return constants
        
        for _, row in df.iterrows():
            try:
                key = str(row['Key']).strip()
                if pd.isna(key) or not key:
                    continue
                
                raw_value = row['Value']
                data_type = str(row['Type']).strip().lower()
                description = str(row.get('Description', ''))
                
                # 타입 변환
                value = self._convert_value(raw_value, data_type)
                
                constants[key] = value
                
                # 정의 정보 저장
                self._definitions_cache[key] = ConstantDefinition(
                    key=key,
                    value=value,
                    data_type=data_type,
                    category=category,
                    description=description
                )
                
            except Exception as row_error:
                print(f"행 파싱 실패 ({category}): {row_error}")
                continue
        
        return constants
    
    def _convert_value(self, raw_value: Any, data_type: str) -> Any:
        """값을 지정된 타입으로 변환합니다."""
        if pd.isna(raw_value):
            return None
        
        try:
            if data_type in ['int', 'integer']:
                return int(float(raw_value))
            elif data_type in ['float', 'double', 'number']:
                return float(raw_value)
            elif data_type in ['bool', 'boolean']:
                if isinstance(raw_value, str):
                    return raw_value.lower() in ['true', '1', 'yes', 'on']
                return bool(raw_value)
            elif data_type in ['str', 'string', 'text']:
                return str(raw_value)
            else:
                # 기본적으로 원본 값 반환
                return raw_value
        except Exception as e:
            print(f"값 변환 실패 ({raw_value} -> {data_type}): {e}")
            return raw_value
    
    def get_constant(self, key: str, default: Any = None) -> Any:
        """상수 값을 가져옵니다."""
        if not self._is_loaded:
            self.load_data()
        
        return self._constants_cache.get(key, default)
    
    def get_constant_definition(self, key: str) -> Optional[ConstantDefinition]:
        """상수 정의 정보를 가져옵니다."""
        return self._definitions_cache.get(key)
    
    def get_constants_by_category(self, category: str) -> Dict[str, Any]:
        """카테고리별 상수들을 가져옵니다."""
        result = {}
        for key, definition in self._definitions_cache.items():
            if definition.category == category:
                result[key] = definition.value
        return result
    
    def reload_constants(self) -> None:
        """상수를 다시 로드합니다."""
        self._constants_cache.clear()
        self._definitions_cache.clear()
        self._is_loaded = False
        self.load_data()
    
    def list_all_constants(self) -> Dict[str, ConstantDefinition]:
        """모든 상수 정의를 반환합니다."""
        if not self._is_loaded:
            self.load_data()
        return self._definitions_cache.copy()


# 전역 상수 관리자 인스턴스
_constants_provider: Optional[ExcelConstantsProvider] = None


def get_constants_provider() -> ExcelConstantsProvider:
    """전역 상수 제공자를 가져옵니다."""
    global _constants_provider
    if _constants_provider is None:
        excel_path = Path("data/game_initial_values_with_formulas.xlsx")
        _constants_provider = ExcelConstantsProvider(excel_path)
    return _constants_provider


def get_constant(key: str, default: Any = None) -> Any:
    """편의 함수: 상수 값을 가져옵니다."""
    return get_constants_provider().get_constant(key, default)


# 타입 안전한 상수 정의들
class GameConstants:
    """게임 상수들의 타입 안전한 접근자"""
    
    # 확률 관련
    PROBABILITY_HIGH_THRESHOLD = TypedConstant("PROBABILITY_HIGH_THRESHOLD", float, 0.7, "probability")
    PROBABILITY_MEDIUM_THRESHOLD = TypedConstant("PROBABILITY_MEDIUM_THRESHOLD", float, 0.5, "probability")
    PROBABILITY_LOW_THRESHOLD = TypedConstant("PROBABILITY_LOW_THRESHOLD", float, 0.3, "probability")
    
    # 게임 진행
    TOTAL_GAME_DAYS = TypedConstant("TOTAL_GAME_DAYS", int, 730, "game_flow")
    MAX_ACTIONS_PER_DAY = TypedConstant("MAX_ACTIONS_PER_DAY", int, 3, "game_flow")
    
    # 경제 관련
    DEFAULT_STARTING_MONEY = TypedConstant("DEFAULT_STARTING_MONEY", float, 10000.0, "economy")
    CHICKEN_INGREDIENT_COST = TypedConstant("CHICKEN_INGREDIENT_COST", float, 5681.0, "economy")
    
    # 임계값
    MONEY_LOW_THRESHOLD = TypedConstant("MONEY_LOW_THRESHOLD", float, 3000.0, "thresholds")
    MONEY_HIGH_THRESHOLD = TypedConstant("MONEY_HIGH_THRESHOLD", float, 15000.0, "thresholds")
    REPUTATION_LOW_THRESHOLD = TypedConstant("REPUTATION_LOW_THRESHOLD", float, 30.0, "thresholds")
    REPUTATION_HIGH_THRESHOLD = TypedConstant("REPUTATION_HIGH_THRESHOLD", float, 70.0, "thresholds")
    HAPPINESS_LOW_THRESHOLD = TypedConstant("HAPPINESS_LOW_THRESHOLD", float, 30.0, "thresholds")
    HAPPINESS_HIGH_THRESHOLD = TypedConstant("HAPPINESS_HIGH_THRESHOLD", float, 70.0, "thresholds")
    
    @classmethod
    def get_all_constants(cls) -> Dict[str, TypedConstant]:
        """모든 정의된 상수를 반환합니다."""
        constants = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, TypedConstant):
                constants[attr_name] = attr
        return constants


# 편의 함수들
def reload_all_constants() -> None:
    """모든 상수를 다시 로드합니다."""
    get_constants_provider().reload_constants()


def validate_constants() -> Dict[str, str]:
    """상수 유효성을 검사합니다."""
    errors = {}
    provider = get_constants_provider()
    
    for name, constant in GameConstants.get_all_constants().items():
        try:
            value = constant.get(provider)
            # 추가 검증 로직 여기에...
        except Exception as e:
            errors[name] = str(e)
    
    return errors 
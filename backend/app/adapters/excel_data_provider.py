"""
엑셀 기반 게임 데이터 제공자

이 모듈은 엑셀 파일에서 게임 데이터를 읽어오는 어댑터입니다.
헥사고널 아키텍처의 어댑터(Adapter) 역할을 합니다.

⚠️ 중요: 이 클래스는 읽기 전용입니다.
엑셀 파일을 수정하는 기능은 제공하지 않으며, 오직 읽기만 가능합니다.
엑셀 파일 수정은 외부 도구(Excel, LibreOffice 등)에서만 수행해야 합니다.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any
import copy

from ..core.domain.interfaces.data_provider import (
    GameDataProvider,
    GameMetric,
    TradeoffRelationship,
    ReadOnlyDataProvider,
)
from ..core.domain.variable_registry import VARIABLE_REGISTRY


class ExcelGameDataProvider(ReadOnlyDataProvider):
    """
    엑셀 기반 게임 데이터 제공자 (읽기 전용)
    
    게임 데이터를 엑셀 파일에서 읽어와 제공합니다.
    의존성 역전 원칙에 따라 GameDataProvider 프로토콜을 구현합니다.
    
    아키텍처 원칙:
    1. 엑셀 파일은 절대 수정하지 않습니다.
    2. 모든 반환 데이터는 불변 복사본입니다.
    3. 데이터 흐름: 엑셀 파일 → 읽기 → 게임 로직 (단방향)
    
    엑셀 파일 수정이 필요한 경우:
    - Excel, LibreOffice Calc 등 외부 도구 사용
    - 코드에서는 절대 엑셀 파일을 변경하지 않음
    """
    
    def __init__(self, excel_path: str = "data/game_initial_values.xlsx"):
        """
        Args:
            excel_path: 엑셀 파일 경로 (읽기 전용)
            
        Raises:
            FileNotFoundError: 엑셀 파일이 존재하지 않을 때
            ValueError: 엑셀 파일 형식이 올바르지 않을 때
        """
        super().__init__(excel_path)
        self.excel_path = Path(excel_path)
    
    def _validate_data_source(self) -> None:
        """
        엑셀 파일의 유효성을 검증합니다.
        
        Raises:
            FileNotFoundError: 엑셀 파일이 존재하지 않을 때
            ValueError: 엑셀 파일 형식이 올바르지 않을 때
        """
        excel_path = Path(self._data_source_path)
        
        if not excel_path.exists():
            raise FileNotFoundError(
                f"게임 데이터 파일을 찾을 수 없습니다: {self._data_source_path}\n"
                f"엑셀 템플릿을 먼저 생성해주세요.\n"
                f"⚠️ 주의: 코드에서 엑셀 파일을 생성하지 마세요. 외부 도구를 사용하세요."
            )
        
        if not excel_path.suffix.lower() in ['.xlsx', '.xls']:
            raise ValueError(
                f"지원하지 않는 파일 형식입니다: {excel_path.suffix}\n"
                f"Excel 파일(.xlsx, .xls)만 지원됩니다."
            )
        
        # 기본 시트 존재 여부 확인
        try:
            xl = pd.ExcelFile(excel_path)
            required_sheets = ['Game_Metrics', 'Game_Constants']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in xl.sheet_names]
            
            if missing_sheets:
                raise ValueError(
                    f"필수 시트가 누락되었습니다: {missing_sheets}\n"
                    f"엑셀 파일에 다음 시트들이 있어야 합니다: {required_sheets}"
                )
        except Exception as e:
            raise ValueError(f"엑셀 파일 형식 검증 실패: {e}")
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        """
        게임 핵심 지표 데이터를 반환합니다.
        
        Returns:
            Dict[str, GameMetric]: 메트릭 이름을 키로 하는 불변 메트릭 객체들
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Game_Metrics')
            
            metrics = {}
            for _, row in df.iterrows():
                metric_name = row['Metric_Name']
                max_val = row['Max_Value']
                
                # 'inf' 문자열을 float('inf')로 변환
                if isinstance(max_val, str) and max_val.lower() == 'inf':
                    max_val = float('inf')
                
                metrics[metric_name] = GameMetric(
                    base_value=float(row['Base_Value']),
                    min_value=float(row['Min_Value']),
                    max_value=max_val,
                    description=str(row['Description'])
                )
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(metrics)
            
        except Exception as e:
            raise ValueError(f"Game_Metrics 시트 읽기 실패: {e}")
    
    def get_game_constants(self) -> Dict[str, Any]:
        """
        게임 상수 데이터를 반환합니다.
        
        Returns:
            Dict[str, Any]: 상수 이름을 키로 하는 상수 값들
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Game_Constants')
            
            constants = {}
            for _, row in df.iterrows():
                constant_name = row['Constant_Name']
                
                # Formula 컬럼이 있고 값이 있으면 수식 평가
                if 'Formula' in df.columns and pd.notna(row.get('Formula')):
                    formula = str(row['Formula']).strip()
                    if formula:  # 빈 문자열이 아닌 경우
                        try:
                            # 수식 평가
                            calculated_value = VARIABLE_REGISTRY.evaluate_formula(formula)
                            constants[constant_name] = calculated_value
                            print(f"🧮 수식 계산: {constant_name} = {formula} → {calculated_value}")
                            continue
                        except Exception as formula_error:
                            print(f"⚠️ 수식 평가 실패 ({constant_name}): {formula} - {formula_error}")
                            # 수식 평가 실패 시 Value 컬럼 사용
                
                # 기본 Value 컬럼 사용
                value = row['Value']
                
                # 숫자 타입 변환
                if isinstance(value, (int, float)):
                    constants[constant_name] = value
                else:
                    # 문자열인 경우 숫자로 변환 시도
                    try:
                        constants[constant_name] = int(value)
                    except (ValueError, TypeError):
                        try:
                            constants[constant_name] = float(value)
                        except (ValueError, TypeError):
                            constants[constant_name] = value
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(constants)
            
        except Exception as e:
            raise ValueError(f"Game_Constants 시트 읽기 실패: {e}")
    
    def get_tradeoff_relationships(self) -> Dict[str, Dict[str, TradeoffRelationship]]:
        """
        지표 간 트레이드오프 관계 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, TradeoffRelationship]]: 소스 메트릭별 트레이드오프 관계들
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Tradeoff_Relationships')
            
            relationships = {}
            for _, row in df.iterrows():
                source_metric = row['Source_Metric']
                target_metric = row['Target_Metric']
                
                if source_metric not in relationships:
                    relationships[source_metric] = {}
                
                relationships[source_metric][target_metric] = TradeoffRelationship(
                    target_metric=target_metric,
                    impact_factor=float(row['Impact_Factor']),
                    description=str(row['Description'])
                )
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(relationships)
            
        except Exception as e:
            raise ValueError(f"Tradeoff_Relationships 시트 읽기 실패: {e}")
    
    def get_uncertainty_weights(self) -> Dict[str, float]:
        """
        불확실성 가중치 데이터를 반환합니다.
        
        Returns:
            Dict[str, float]: 메트릭별 불확실성 가중치
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Uncertainty_Weights')
            
            weights = {}
            for _, row in df.iterrows():
                metric_name = row['Metric_Name']
                weights[metric_name] = float(row['Weight'])
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(weights)
            
        except Exception as e:
            raise ValueError(f"Uncertainty_Weights 시트 읽기 실패: {e}")
    
    def get_probability_thresholds(self) -> Dict[str, float]:
        """
        확률 임계값 데이터를 반환합니다.
        
        Returns:
            Dict[str, float]: 확률 임계값들
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Probability_Thresholds')
            
            thresholds = {}
            for _, row in df.iterrows():
                threshold_name = row['Threshold_Name']
                thresholds[threshold_name] = float(row['Value'])
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(thresholds)
            
        except Exception as e:
            raise ValueError(f"Probability_Thresholds 시트 읽기 실패: {e}")
    
    def get_warning_thresholds(self) -> Dict[str, Dict[str, float]]:
        """
        경고 임계값 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, float]]: 메트릭별 경고 임계값들
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Warning_Thresholds')
            
            thresholds = {}
            for _, row in df.iterrows():
                metric_name = row['Metric_Name']
                thresholds[metric_name] = {
                    'low_warning': float(row['Low_Warning']),
                    'high_warning': float(row['High_Warning'])
                }
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(thresholds)
            
        except Exception as e:
            raise ValueError(f"Warning_Thresholds 시트 읽기 실패: {e}")
    
    def get_chicken_economics(self) -> Dict[str, Any]:
        """
        치킨집 경제 데이터를 반환합니다.
        
        Returns:
            Dict[str, Any]: 치킨집 경제 관련 데이터
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Chicken_Economics')
            
            economics = {}
            for _, row in df.iterrows():
                item_name = row['Item']
                economics[item_name] = {
                    'value': float(row['Value']),
                    'unit': str(row['Unit']),
                    'source': str(row['Source']),
                    'description': str(row['Description'])
                }
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(economics)
            
        except Exception as e:
            raise ValueError(f"Chicken_Economics 시트 읽기 실패: {e}")
    
    def get_sales_projections(self) -> Dict[str, Dict[str, Any]]:
        """
        매출 예측 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, Any]]: 기간별 매출 예측 데이터
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Sales_Projections')
            
            projections = {}
            for _, row in df.iterrows():
                period = row['Period']
                projections[period] = {
                    'daily_sales_volume': int(row['Daily_Sales_Volume']),
                    'chicken_price': float(row['Chicken_Price']),
                    'daily_revenue': float(row['Daily_Revenue']),
                    'daily_ingredient_cost': float(row['Daily_Ingredient_Cost']),
                    'daily_fixed_cost': float(row['Daily_Fixed_Cost']),
                    'daily_profit': float(row['Daily_Profit']),
                    'profit_rate': float(row['Profit_Rate']),
                    'description': str(row['Description'])
                }
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(projections)
            
        except Exception as e:
            raise ValueError(f"Sales_Projections 시트 읽기 실패: {e}")
    
    def get_market_research(self) -> Dict[str, Any]:
        """
        시장 조사 데이터를 반환합니다.
        
        Returns:
            Dict[str, Any]: 시장 조사 관련 데이터
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Market_Research')
            
            research = {}
            for _, row in df.iterrows():
                metric_name = row['Metric']
                research[metric_name] = {
                    'value': float(row['Value']),
                    'unit': str(row['Unit']),
                    'source': str(row['Source']),
                    'description': str(row['Description'])
                }
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(research)
            
        except Exception as e:
            raise ValueError(f"Market_Research 시트 읽기 실패: {e}")
    
    def get_cost_structure(self) -> Dict[str, Dict[str, Any]]:
        """
        비용 구조 데이터를 반환합니다.
        
        Returns:
            Dict[str, Dict[str, Any]]: 비용 유형별 구조 데이터
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Cost_Structure')
            
            costs = {}
            for _, row in df.iterrows():
                cost_type = row['Cost_Type']
                costs[cost_type] = {
                    'amount': float(row['Amount']),
                    'unit': str(row['Unit']),
                    'frequency': str(row['Frequency']),
                    'annual_cost': float(row['Annual_Cost']),
                    'description': str(row['Description'])
                }
            
            # 불변 복사본 반환
            return self._ensure_immutable_copy(costs)
            
        except Exception as e:
            raise ValueError(f"Cost_Structure 시트 읽기 실패: {e}")
    
    def get_all_chicken_data(self) -> Dict[str, Any]:
        """
        모든 치킨 관련 데이터를 한 번에 반환합니다.
        
        Returns:
            Dict[str, Any]: 모든 치킨 관련 데이터의 통합 딕셔너리
            
        Note:
            반환되는 데이터는 읽기 전용 복사본입니다.
        """
        chicken_data = {
            'economics': self.get_chicken_economics(),
            'sales_projections': self.get_sales_projections(),
            'market_research': self.get_market_research(),
            'cost_structure': self.get_cost_structure()
        }
        
        # 불변 복사본 반환
        return self._ensure_immutable_copy(chicken_data) 
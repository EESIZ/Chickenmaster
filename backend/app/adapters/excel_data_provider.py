"""
엑셀 기반 게임 데이터 제공자

이 모듈은 엑셀 파일에서 게임 데이터를 읽어오는 어댑터입니다.
헥사고널 아키텍처의 어댑터(Adapter) 역할을 합니다.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any

from ..core.domain.interfaces.data_provider import (
    GameDataProvider,
    GameMetric,
    TradeoffRelationship,
)
from ..core.domain.variable_registry import VARIABLE_REGISTRY


class ExcelGameDataProvider(GameDataProvider):
    """
    엑셀 기반 게임 데이터 제공자
    
    게임 데이터를 엑셀 파일에서 읽어와 제공합니다.
    의존성 역전 원칙에 따라 GameDataProvider 프로토콜을 구현합니다.
    """
    
    def __init__(self, excel_path: str = "data/game_initial_values.xlsx"):
        """
        Args:
            excel_path: 엑셀 파일 경로
            
        Raises:
            FileNotFoundError: 엑셀 파일이 존재하지 않을 때
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"게임 데이터 파일을 찾을 수 없습니다: {excel_path}\n"
                f"엑셀 템플릿을 먼저 생성해주세요."
            )
    
    def get_game_metrics(self) -> Dict[str, GameMetric]:
        """게임 핵심 지표 데이터를 반환합니다."""
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
            
            return metrics
            
        except Exception as e:
            raise ValueError(f"Game_Metrics 시트 읽기 실패: {e}")
    
    def get_game_constants(self) -> Dict[str, Any]:
        """게임 상수 데이터를 반환합니다."""
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
            
            return constants
            
        except Exception as e:
            raise ValueError(f"Game_Constants 시트 읽기 실패: {e}")
    
    def get_tradeoff_relationships(self) -> Dict[str, Dict[str, TradeoffRelationship]]:
        """지표 간 트레이드오프 관계 데이터를 반환합니다."""
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
            
            return relationships
            
        except Exception as e:
            raise ValueError(f"Tradeoff_Relationships 시트 읽기 실패: {e}")
    
    def get_uncertainty_weights(self) -> Dict[str, float]:
        """불확실성 가중치 데이터를 반환합니다."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Uncertainty_Weights')
            
            weights = {}
            for _, row in df.iterrows():
                metric_name = row['Metric_Name']
                weights[metric_name] = float(row['Weight'])
            
            return weights
            
        except Exception as e:
            raise ValueError(f"Uncertainty_Weights 시트 읽기 실패: {e}")
    
    def get_probability_thresholds(self) -> Dict[str, float]:
        """확률 임계값 데이터를 반환합니다."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Probability_Thresholds')
            
            thresholds = {}
            for _, row in df.iterrows():
                threshold_name = row['Threshold_Name']
                thresholds[threshold_name] = float(row['Value'])
            
            return thresholds
            
        except Exception as e:
            raise ValueError(f"Probability_Thresholds 시트 읽기 실패: {e}")
    
    def get_warning_thresholds(self) -> Dict[str, Dict[str, float]]:
        """경고 임계값 데이터를 반환합니다."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Warning_Thresholds')
            
            thresholds = {}
            for _, row in df.iterrows():
                metric_name = row['Metric_Name']
                thresholds[metric_name] = {
                    'low_warning': float(row['Low_Warning']),
                    'high_warning': float(row['High_Warning'])
                }
            
            return thresholds
            
        except Exception as e:
            raise ValueError(f"Warning_Thresholds 시트 읽기 실패: {e}") 
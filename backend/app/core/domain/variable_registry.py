"""
변수 사전(Variable Registry)

엑셀 수식에서 참조할 수 있는 모든 변수들을 중앙에서 관리합니다.
다른 모듈의 상수들을 한 곳에 모아서 엑셀 템플릿에서 사용할 수 있게 합니다.
"""

from typing import Dict, Any, Union
import math
from ..game_constants import (
    DEFAULT_STARTING_MONEY,
    DEFAULT_STARTING_REPUTATION, 
    DEFAULT_STARTING_HAPPINESS,
    DEFAULT_STARTING_SUFFERING,
    DEFAULT_STARTING_INVENTORY,
    DEFAULT_STARTING_STAFF_FATIGUE,
    DEFAULT_STARTING_FACILITY,
    DEFAULT_STARTING_DEMAND,
    TOTAL_GAME_DAYS,
    EARLY_GAME_THRESHOLD,
    MID_GAME_THRESHOLD,
    PROBABILITY_LOW_THRESHOLD,
    PROBABILITY_HIGH_THRESHOLD,
    MAX_ACTIONS_PER_DAY,
)


class VariableRegistry:
    """
    변수 사전 클래스
    
    엑셀 템플릿에서 사용할 수 있는 모든 변수들을 관리합니다.
    {변수명} 형태로 엑셀에서 참조할 수 있습니다.
    """
    
    def __init__(self):
        """변수 사전 초기화"""
        self._variables = self._build_variable_registry()
    
    def _build_variable_registry(self) -> Dict[str, Union[int, float]]:
        """
        변수 사전을 구축합니다.
        
        Returns:
            모든 사용 가능한 변수들의 딕셔너리
        """
        return {
            # === 게임 초기값 ===
            'DEFAULT_STARTING_MONEY': DEFAULT_STARTING_MONEY,
            'DEFAULT_STARTING_REPUTATION': DEFAULT_STARTING_REPUTATION,
            'DEFAULT_STARTING_HAPPINESS': DEFAULT_STARTING_HAPPINESS,
            'DEFAULT_STARTING_SUFFERING': DEFAULT_STARTING_SUFFERING,
            'DEFAULT_STARTING_INVENTORY': DEFAULT_STARTING_INVENTORY,
            'DEFAULT_STARTING_STAFF_FATIGUE': DEFAULT_STARTING_STAFF_FATIGUE,
            'DEFAULT_STARTING_FACILITY': DEFAULT_STARTING_FACILITY,
            'DEFAULT_STARTING_DEMAND': DEFAULT_STARTING_DEMAND,
            
            # === 게임 진행 관련 ===
            'TOTAL_GAME_DAYS': TOTAL_GAME_DAYS,
            'EARLY_GAME_THRESHOLD': EARLY_GAME_THRESHOLD,
            'MID_GAME_THRESHOLD': MID_GAME_THRESHOLD,
            'MAX_ACTIONS_PER_DAY': MAX_ACTIONS_PER_DAY,
            
            # === 확률 관련 ===
            'PROBABILITY_LOW_THRESHOLD': PROBABILITY_LOW_THRESHOLD,
            'PROBABILITY_HIGH_THRESHOLD': PROBABILITY_HIGH_THRESHOLD,
            
            # === 계산된 값들 ===
            'HALF_GAME_DAYS': TOTAL_GAME_DAYS // 2,  # 게임의 절반 지점
            'QUARTER_GAME_DAYS': TOTAL_GAME_DAYS // 4,  # 게임의 1/4 지점
            'THREE_QUARTER_GAME_DAYS': (TOTAL_GAME_DAYS * 3) // 4,  # 게임의 3/4 지점
            
            # === 수학 상수 ===
            'PI': math.pi,
            'E': math.e,
            
            # === 범위 값들 ===
            'MIN_PERCENTAGE': 0,
            'MAX_PERCENTAGE': 100,
            'HALF_PERCENTAGE': 50,
            
            # === 돈 관련 임계값 ===
            'POVERTY_LINE': DEFAULT_STARTING_MONEY * 0.1,
            'COMFORTABLE_MONEY': DEFAULT_STARTING_MONEY * 2,
            'RICH_THRESHOLD': DEFAULT_STARTING_MONEY * 5,
            
            # === 시간 관련 ===
            'DAYS_PER_WEEK': 7,
            'DAYS_PER_MONTH': 30,
            'DAYS_PER_SEASON': 90,
            'DAYS_PER_YEAR': 365,
        }
    
    def get_variable(self, name: str) -> Union[int, float]:
        """
        변수 값을 가져옵니다.
        
        Args:
            name: 변수명
            
        Returns:
            변수 값
            
        Raises:
            KeyError: 존재하지 않는 변수명일 때
        """
        if name not in self._variables:
            available_vars = ', '.join(sorted(self._variables.keys()))
            raise KeyError(
                f"변수 '{name}'를 찾을 수 없습니다.\n"
                f"사용 가능한 변수들: {available_vars}"
            )
        return self._variables[name]
    
    def get_all_variables(self) -> Dict[str, Union[int, float]]:
        """모든 변수를 반환합니다."""
        return self._variables.copy()
    
    def substitute_template(self, template: str) -> str:
        """
        템플릿 문자열의 {변수명}을 실제 값으로 치환합니다.
        
        Args:
            template: 템플릿 문자열 (예: "{DEFAULT_STARTING_MONEY} * 0.1")
            
        Returns:
            치환된 문자열 (예: "10000 * 0.1")
        """
        result = template
        for var_name, var_value in self._variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(var_value))
        return result
    
    def evaluate_formula(self, formula: str) -> Union[int, float]:
        """
        수식을 평가해서 결과값을 반환합니다.
        
        Args:
            formula: 평가할 수식 (예: "{DEFAULT_STARTING_MONEY} * 0.1")
            
        Returns:
            계산 결과
            
        Raises:
            ValueError: 수식 평가 실패 시
        """
        try:
            # 템플릿 치환
            substituted = self.substitute_template(formula)
            
            # 안전한 수식 평가 (기본 수학 연산만 허용)
            allowed_names = {
                "__builtins__": {},
                "abs": abs,
                "min": min,
                "max": max,
                "round": round,
                "int": int,
                "float": float,
                "pow": pow,
                "sqrt": math.sqrt,
                "log": math.log,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
            }
            
            result = eval(substituted, allowed_names, {})
            return result
            
        except Exception as e:
            raise ValueError(f"수식 평가 실패: '{formula}' -> '{substituted}'\n오류: {e}")
    
    def list_available_variables(self) -> str:
        """사용 가능한 모든 변수 목록을 문자열로 반환합니다."""
        variables_by_category = {
            "게임 초기값": [k for k in self._variables.keys() if k.startswith('DEFAULT_STARTING_')],
            "게임 진행": [k for k in self._variables.keys() if any(x in k for x in ['GAME_DAYS', 'THRESHOLD', 'ACTIONS'])],
            "확률": [k for k in self._variables.keys() if 'PROBABILITY' in k],
            "수학": [k for k in self._variables.keys() if k in ['PI', 'E']],
            "범위": [k for k in self._variables.keys() if 'PERCENTAGE' in k],
            "돈 관련": [k for k in self._variables.keys() if any(x in k for x in ['POVERTY', 'COMFORTABLE', 'RICH'])],
            "시간": [k for k in self._variables.keys() if 'DAYS_PER_' in k],
            "계산된 값": [k for k in self._variables.keys() if any(x in k for x in ['HALF_', 'QUARTER_', 'THREE_'])],
        }
        
        result = "📋 사용 가능한 변수 목록:\n\n"
        for category, vars_list in variables_by_category.items():
            if vars_list:
                result += f"🔸 {category}:\n"
                for var in sorted(vars_list):
                    result += f"  {var} = {self._variables[var]}\n"
                result += "\n"
        
        result += "💡 사용법: 엑셀에서 {변수명} 형태로 사용하세요.\n"
        result += "예시: {DEFAULT_STARTING_MONEY} * 0.1\n"
        
        return result


# 전역 변수 사전 인스턴스
VARIABLE_REGISTRY = VariableRegistry() 
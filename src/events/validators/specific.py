"""
구체적인 이벤트 검증기 구현
"""


from ..schema import Event
from .base import BaseValidator, ValidationResult

class FormulaValidator(BaseValidator):
    """수식 안전성 검증기"""
    
    def validate(self, event: Event) -> ValidationResult:
        """수식 안전성 검증"""
        import ast
        
        result = ValidationResult(is_valid=True)
        
        for effect in event.effects:
            try:
                tree = ast.parse(effect.formula, mode="eval")
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call | ast.Attribute):
                        result.is_valid = False
                        result.errors.append(
                            f"안전하지 않은 수식: {effect.formula} (함수 호출 또는 속성 접근 불가)"
                        )
                        break
            except SyntaxError:
                result.is_valid = False
                result.errors.append(f"잘못된 수식 구문: {effect.formula}")
        
        return result 
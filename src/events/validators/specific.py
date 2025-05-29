"""
구체적인 이벤트 검증기 구현
"""

from typing import ClassVar

from .base import BaseValidator, Event, ValidationResult
from ..constants import QUALITY_THRESHOLDS, VALIDATION_THRESHOLDS
from fuzzywuzzy import fuzz

class CulturalValidator(BaseValidator):
    """문화적 연관성 검증기"""
    
    # 한국 치킨 문화 관련 키워드
    CULTURAL_KEYWORDS: ClassVar[list[str]] = [
        "치킨", "후라이드", "양념", "간장", "마늘", "닭강정",
        "배달", "포장", "회식", "단골", "성수기", "할인",
        "치맥", "맥주", "소주", "안주", "야식", "주문"
    ]
    
    def validate(self, event: Event) -> ValidationResult:
        """문화적 연관성 검증"""
        text = f"{event.name_ko} {event.text_ko}"
        matched_keywords = sum(
            1 for keyword in self.CULTURAL_KEYWORDS
            if keyword in text
        )
        
        if matched_keywords < VALIDATION_THRESHOLDS["MIN_KEYWORDS_MATCH"]:
            return ValidationResult(
                is_valid=False,
                errors=["한국 치킨 문화 관련 키워드가 부족합니다"]
            )
            
        return ValidationResult(is_valid=True)

class DuplicateValidator(BaseValidator):
    """중복 검증기"""
    
    def __init__(self):
        self.validated_events: list[Event] = []
    
    def validate(self, event: Event) -> ValidationResult:
        """중복 여부 검증"""
        for validated in self.validated_events:
            name_similarity = fuzz.ratio(event.name_ko, validated.name_ko)
            text_similarity = fuzz.ratio(event.text_ko, validated.text_ko)
            
            if (name_similarity > VALIDATION_THRESHOLDS["NAME_SIMILARITY_THRESHOLD"] or 
                text_similarity > VALIDATION_THRESHOLDS["TEXT_SIMILARITY_THRESHOLD"]):
                return ValidationResult(
                    is_valid=False,
                    errors=["유사한 이벤트가 이미 존재합니다"]
                )
        
        self.validated_events.append(event)
        return ValidationResult(is_valid=True)

class TradeoffValidator(BaseValidator):
    """트레이드오프 균형 검증기"""
    
    def validate(self, event: Event) -> ValidationResult:
        """트레이드오프 균형 검증"""
        if len(event.choices) < VALIDATION_THRESHOLDS["MIN_CHOICES"]:
            return ValidationResult(
                is_valid=False,
                errors=["선택지가 2개 이상이어야 합니다"]
            )

        for choice in event.choices:
            positive_effects = sum(1 for v in choice.effects.values() if v > 0)
            negative_effects = sum(1 for v in choice.effects.values() if v < 0)
            
            if positive_effects == 0 or negative_effects == 0:
                return ValidationResult(
                    is_valid=False,
                    errors=["각 선택지는 긍정적/부정적 효과를 모두 포함해야 합니다"]
                )

        return ValidationResult(is_valid=True)

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
                    if isinstance(node, (ast.Call, ast.Attribute)):
                        result.is_valid = False
                        result.errors.append(
                            f"안전하지 않은 수식: {effect.formula} (함수 호출 또는 속성 접근 불가)"
                        )
                        break
            except SyntaxError:
                result.is_valid = False
                result.errors.append(f"잘못된 수식 구문: {effect.formula}")
        
        return result 
"""
이벤트 검증 기본 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Protocol

from pydantic import BaseModel

class Event(BaseModel):
    """이벤트 기본 모델"""
    id: str
    type: str
    name_ko: str
    name_en: str
    text_ko: str
    text_en: str

class ValidationResult(BaseModel):
    """검증 결과"""
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []

class EventValidator(Protocol):
    """이벤트 검증기 프로토콜"""
    
    def validate(self, event: Event) -> ValidationResult:
        """
        이벤트 검증
        
        Args:
            event: 검증할 이벤트
            
        Returns:
            ValidationResult: 검증 결과
        """
        ...

class BaseValidator(ABC):
    """검증기 기본 클래스"""
    
    @abstractmethod
    def validate(self, event: Event) -> ValidationResult:
        """
        이벤트 검증 구현
        
        Args:
            event: 검증할 이벤트
            
        Returns:
            ValidationResult: 검증 결과
        """
        pass

class CompositeValidator(BaseValidator):
    """복합 검증기"""
    
    def __init__(self, validators: list[BaseValidator]):
        self.validators = validators
    
    def validate(self, event: Event) -> ValidationResult:
        """
        모든 하위 검증기 실행
        
        Args:
            event: 검증할 이벤트
            
        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult(is_valid=True)
        
        for validator in self.validators:
            sub_result = validator.validate(event)
            if not sub_result.is_valid:
                result.is_valid = False
                result.errors.extend(sub_result.errors)
            result.warnings.extend(sub_result.warnings)
            
        return result 
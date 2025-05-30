"""
이벤트 검증기 테스트
"""

import pytest
from pydantic import BaseModel

from src.events.schema import Event, EventEffect, EventChoice
from src.events.validators.base import ValidationResult
from src.events.validators.specific import (
    FormulaValidator
)





class TestFormulaValidator:
    """수식 안전성 검증기 테스트"""
    
    def test_valid_formula(self, formula_validator: FormulaValidator, mock_event: Event):
        """유효한 수식인 경우"""
        mock_event.effects = [
            EventEffect(metric="money", formula="100 * x + 50"),
            EventEffect(metric="reputation", formula="(base_value - 10) / 2")
        ]
        result = formula_validator.validate(mock_event)
        assert result.is_valid
        assert not result.errors
        
    def test_invalid_syntax(self, formula_validator: FormulaValidator, mock_event: Event):
        """잘못된 구문인 경우"""
        mock_event.effects = [
            EventEffect(metric="money", formula="100 * x +"),
        ]
        result = formula_validator.validate(mock_event)
        assert not result.is_valid
        assert "잘못된 수식 구문" in result.errors[0]
        
    def test_unsafe_formula(self, formula_validator: FormulaValidator, mock_event: Event):
        """안전하지 않은 수식인 경우"""
        mock_event.effects = [
            EventEffect(metric="money", formula="eval('100')"),
        ]
        result = formula_validator.validate(mock_event)
        assert not result.is_valid
        assert "안전하지 않은 수식" in result.errors[0] 
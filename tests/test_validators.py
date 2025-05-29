"""
이벤트 검증기 테스트
"""

import pytest
from pydantic import BaseModel

from src.events.schema import Event, EventEffect, EventChoice
from src.events.validators.base import ValidationResult
from src.events.validators.specific import (
    CulturalValidator,
    DuplicateValidator,
    FormulaValidator,
    TradeoffValidator
)

class TestCulturalValidator:
    """문화적 연관성 검증기 테스트"""
    
    def test_valid_cultural_keywords(self, cultural_validator: CulturalValidator, mock_event: Event):
        """충분한 문화적 키워드가 있는 경우"""
        mock_event.text_ko = "치킨집에서 배달 주문이 들어왔습니다"
        result = cultural_validator.validate(mock_event)
        assert result.is_valid
        assert not result.errors
        
    def test_insufficient_cultural_keywords(self, cultural_validator: CulturalValidator, mock_event: Event):
        """문화적 키워드가 부족한 경우"""
        mock_event.text_ko = "일반적인 가게 이벤트입니다"
        result = cultural_validator.validate(mock_event)
        assert not result.is_valid
        assert "한국 치킨 문화 관련 키워드가 부족합니다" in result.errors

class TestDuplicateValidator:
    """중복 검증기 테스트"""
    
    def test_unique_event(self, duplicate_validator: DuplicateValidator, mock_event: Event):
        """고유한 이벤트인 경우"""
        result = duplicate_validator.validate(mock_event)
        assert result.is_valid
        assert not result.errors
        
    def test_duplicate_event(self, duplicate_validator: DuplicateValidator, mock_event: Event):
        """중복된 이벤트인 경우"""
        # 첫 번째 이벤트 검증
        duplicate_validator.validate(mock_event)
        
        # 유사한 두 번째 이벤트 검증
        similar_event = mock_event.model_copy()
        similar_event.id = "test_event_002"
        result = duplicate_validator.validate(similar_event)
        
        assert not result.is_valid
        assert "유사한 이벤트가 이미 존재합니다" in result.errors

class TestTradeoffValidator:
    """트레이드오프 균형 검증기 테스트"""
    
    def test_valid_tradeoff(self, tradeoff_validator: TradeoffValidator, mock_event: Event):
        """유효한 트레이드오프가 있는 경우"""
        mock_event.choices = [
            EventChoice(
                text_ko="선택 1",
                text_en="Choice 1",
                effects={"money": 100, "reputation": -10}
            ),
            EventChoice(
                text_ko="선택 2",
                text_en="Choice 2",
                effects={"money": -50, "reputation": 20}
            )
        ]
        result = tradeoff_validator.validate(mock_event)
        assert result.is_valid
        assert not result.errors
        
    def test_insufficient_choices(self, tradeoff_validator: TradeoffValidator, mock_event: Event):
        """선택지가 부족한 경우"""
        mock_event.choices = [
            EventChoice(
                text_ko="선택 1",
                text_en="Choice 1",
                effects={"money": 100, "reputation": -10}
            )
        ]
        result = tradeoff_validator.validate(mock_event)
        assert not result.is_valid
        assert "선택지가 2개 이상이어야 합니다" in result.errors
        
    def test_no_tradeoff(self, tradeoff_validator: TradeoffValidator, mock_event: Event):
        """트레이드오프가 없는 경우"""
        mock_event.choices = [
            EventChoice(
                text_ko="선택 1",
                text_en="Choice 1",
                effects={"money": 100, "reputation": 10}
            ),
            EventChoice(
                text_ko="선택 2",
                text_en="Choice 2",
                effects={"money": 50, "reputation": 20}
            )
        ]
        result = tradeoff_validator.validate(mock_event)
        assert not result.is_valid
        assert "각 선택지는 긍정적/부정적 효과를 모두 포함해야 합니다" in result.errors

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
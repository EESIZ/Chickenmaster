import pytest
from app.services.metrics_tracker import MetricsTracker
from app.core.game_constants import (
    MAX_STORY_LENGTH,
    MIN_STORY_LENGTH,
    MAX_RETRY_ATTEMPTS,
    TIMEOUT_SECONDS
)

@pytest.fixture
def metrics_tracker():
    return MetricsTracker()

def test_validate_game_settings_valid(metrics_tracker):
    """유효한 게임 설정에 대한 테스트"""
    valid_settings = {
        'story': 'a' * 500
    }
    assert metrics_tracker.validate_game_settings(valid_settings) is True

def test_validate_game_settings_invalid_story_length(metrics_tracker):
    """잘못된 스토리 길이에 대한 테스트"""
    invalid_settings = {
        'story': 'a' * (MAX_STORY_LENGTH + 1)
    }
    assert metrics_tracker.validate_game_settings(invalid_settings) is False

def test_retry_operation_success(metrics_tracker):
    """성공적인 작업 재시도 테스트"""
    def mock_operation():
        return "success"
    
    result = metrics_tracker.retry_operation(mock_operation)
    assert result == "success"

def test_retry_operation_failure(metrics_tracker):
    """실패하는 작업 재시도 테스트"""
    def mock_operation():
        raise Exception("Operation failed")
    
    with pytest.raises(Exception):
        metrics_tracker.retry_operation(mock_operation) 
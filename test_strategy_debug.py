#!/usr/bin/env python3
"""
MUD 게임 전략 패턴 디버그 테스트

실제 게임 플레이에서 전략 패턴이 어떻게 작동하는지 확인합니다.
"""

import sys
from src.core.domain.game_state import GameState
from src.cascade.domain.strategies.strategy_factory import get_cascade_strategy_factory
from src.storyteller.domain.strategy_factory import get_storyteller_strategy_factory

def test_strategy_patterns_in_action():
    """실제 게임 시나리오에서 전략 패턴 테스트"""
    print("🔍 전략 패턴 디버그 테스트 시작!")
    print("=" * 50)
    
    # 1. Cascade 전략 팩토리 테스트
    print("\n1️⃣ Cascade 전략 팩토리 테스트:")
    cascade_factory = get_cascade_strategy_factory()
    
    test_categories = ["economy", "social", "tech", "environment"]
    for category in test_categories:
        strategy = cascade_factory.get_strategy_by_event_category(category)
        print(f"  📊 {category} → {type(strategy).__name__}")
    
    # 2. Storyteller 전략 팩토리 테스트  
    print("\n2️⃣ Storyteller 전략 팩토리 테스트:")
    storyteller_factory = get_storyteller_strategy_factory()
    
    state_evaluator = storyteller_factory.get_state_evaluator()
    trend_analyzer = storyteller_factory.get_trend_analyzer()
    pattern_selector = storyteller_factory.get_pattern_selector()
    
    print(f"  🎯 상태 평가: {type(state_evaluator).__name__}")
    print(f"  📈 추세 분석: {type(trend_analyzer).__name__}")
    print(f"  🎭 패턴 선택: {type(pattern_selector).__name__}")
    
    # 3. 실제 전략 사용 테스트
    print("\n3️⃣ 실제 전략 사용 테스트:")
    
    # 테스트용 메트릭 데이터
    test_metrics = {
        "money": 15000,
        "reputation": 75, 
        "happiness": 80,
        "pain": 25
    }
    
    # 상태 평가 전략 테스트
    situation_tone = state_evaluator.evaluate(test_metrics)
    print(f"  📊 상황 평가 결과: {situation_tone}")
    
    print("\n✅ 전략 패턴 디버그 테스트 완료!")
    print("🎯 MUD 게임에서 이 전략들이 실제로 사용되고 있습니다!")

if __name__ == "__main__":
    test_strategy_patterns_in_action() 
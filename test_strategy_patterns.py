#!/usr/bin/env python3
"""
전략 패턴 구현 테스트 스크립트

헥사고널 아키텍처에서 전략 패턴이 올바르게 구현되었는지 검증합니다.
"""

import sys
import traceback

def test_cascade_strategy_factory():
    """Cascade 전략 팩토리 테스트"""
    print("\n🎯 Cascade 전략 팩토리 테스트 시작...")
    
    try:
        from src.cascade.domain.strategies.strategy_factory import (
            CascadeStrategyFactory,
            get_cascade_strategy_factory,
        )
        from src.cascade.domain.models import CascadeType
        
        # 팩토리 인스턴스 생성
        factory = CascadeStrategyFactory()
        
        # 기본 전략 테스트
        default_strategy = factory.get_strategy()
        print(f"✅ 기본 전략 획득: {type(default_strategy).__name__}")
        
        # CascadeType enum 테스트
        immediate_strategy = factory.get_strategy(CascadeType.IMMEDIATE)
        print(f"✅ IMMEDIATE 전략 획득: {type(immediate_strategy).__name__}")
        
        # 문자열 기반 전략 테스트
        economic_strategy = factory.get_strategy("ECONOMIC")
        print(f"✅ ECONOMIC 전략 획득: {type(economic_strategy).__name__}")
        
        # 사용 가능한 전략 목록 확인
        strategies = factory.list_available_strategies()
        print(f"✅ 사용 가능한 전략 목록: {len(strategies)}개")
        
        print("🎉 Cascade 전략 팩토리 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Cascade 전략 팩토리 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_storyteller_strategy_factory():
    """Storyteller 전략 팩토리 테스트"""
    print("\n🎯 Storyteller 전략 팩토리 테스트 시작...")
    
    try:
        from src.storyteller.domain.strategy_factory import (
            StorytellerStrategyFactory,
            StorytellerStrategyBundle,
        )
        
        # 팩토리 인스턴스 생성
        factory = StorytellerStrategyFactory()
        
        # 전략 테스트
        state_evaluator = factory.get_state_evaluator("default")
        print(f"✅ 상태 평가 전략 획득: {type(state_evaluator).__name__}")
        
        trend_analyzer = factory.get_trend_analyzer("linear")
        print(f"✅ 추세 분석 전략 획득: {type(trend_analyzer).__name__}")
        
        pattern_selector = factory.get_pattern_selector("weighted")
        print(f"✅ 패턴 선택 전략 획득: {type(pattern_selector).__name__}")
        
        # 전략 번들 테스트
        default_bundle = StorytellerStrategyBundle.create_default_bundle()
        print(f"✅ 기본 전략 번들 생성: {default_bundle.bundle_name}")
        
        print("🎉 Storyteller 전략 팩토리 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Storyteller 전략 팩토리 테스트 실패: {e}")
        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    print("🚀 전략 패턴 구현 테스트 시작!")
    print("=" * 60)
    
    test_results = []
    
    # 각 테스트 실행
    test_functions = [
        ("Cascade 전략 팩토리", test_cascade_strategy_factory),
        ("Storyteller 전략 팩토리", test_storyteller_strategy_factory),
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n🔍 {test_name} 테스트 실행 중...")
        result = test_func()
        test_results.append((test_name, result))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 전략 패턴 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 결과: {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main()) 
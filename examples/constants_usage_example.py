#!/usr/bin/env python3
"""
엑셀 기반 상수 관리 시스템 사용 예제

이 예제는 새로운 통합 상수 관리 시스템의 사용법을 보여줍니다.
매직넘버 없이 모든 상수를 엑셀에서 관리하는 방법을 시연합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.adapters.excel_constants_provider import (
    GameConstants, 
    get_constants_provider, 
    get_constant,
    reload_all_constants,
    validate_constants
)


def demonstrate_basic_usage():
    """기본 사용법 시연"""
    print("🎯 기본 상수 사용법")
    print("=" * 40)
    
    # 상수 제공자 가져오기
    provider = get_constants_provider()
    
    # 타입 안전한 상수 사용
    high_threshold = GameConstants.PROBABILITY_HIGH_THRESHOLD.get(provider)
    total_days = GameConstants.TOTAL_GAME_DAYS.get(provider)
    starting_money = GameConstants.DEFAULT_STARTING_MONEY.get(provider)
    
    print(f"높은 확률 임계값: {high_threshold} ({type(high_threshold).__name__})")
    print(f"총 게임 일수: {total_days} ({type(total_days).__name__})")
    print(f"시작 자금: {starting_money:,.0f}원 ({type(starting_money).__name__})")
    
    # 편의 함수 사용
    chicken_cost = get_constant("CHICKEN_INGREDIENT_COST", 5000.0)
    print(f"치킨 재료비: {chicken_cost:,.0f}원")


def demonstrate_category_access():
    """카테고리별 상수 접근 시연"""
    print("\n📂 카테고리별 상수 접근")
    print("=" * 40)
    
    provider = get_constants_provider()
    
    # 카테고리별 상수 가져오기
    categories = ["probability", "economy", "thresholds"]
    
    for category in categories:
        constants = provider.get_constants_by_category(category)
        print(f"\n🏷️ {category.upper()} 카테고리:")
        for key, value in constants.items():
            print(f"  - {key}: {value}")


def demonstrate_game_logic_integration():
    """게임 로직과의 통합 시연"""
    print("\n🎮 게임 로직 통합 예제")
    print("=" * 40)
    
    provider = get_constants_provider()
    
    # 실제 게임 로직에서 사용하는 방식
    def check_money_status(current_money: float) -> str:
        """자금 상태를 확인하는 함수 (매직넘버 없음!)"""
        low_threshold = GameConstants.MONEY_LOW_THRESHOLD.get(provider)
        high_threshold = GameConstants.MONEY_HIGH_THRESHOLD.get(provider)
        
        if current_money < low_threshold:
            return "위험"
        elif current_money > high_threshold:
            return "풍부"
        else:
            return "보통"
    
    def calculate_chicken_profit(selling_price: float, quantity: int) -> dict:
        """치킨 판매 수익 계산 (매직넘버 없음!)"""
        ingredient_cost = GameConstants.CHICKEN_INGREDIENT_COST.get(provider)
        
        total_revenue = selling_price * quantity
        total_cost = ingredient_cost * quantity
        profit = total_revenue - total_cost
        profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
        
        return {
            "수량": quantity,
            "총매출": total_revenue,
            "총원가": total_cost,
            "순이익": profit,
            "이익률": f"{profit_margin:.1f}%"
        }
    
    # 테스트 시나리오
    test_money_amounts = [2000, 8000, 20000]
    print("💰 자금 상태 체크:")
    for money in test_money_amounts:
        status = check_money_status(money)
        print(f"  {money:,}원 → {status}")
    
    print("\n🍗 치킨 수익 계산:")
    profit_info = calculate_chicken_profit(15000, 10)  # 치킨 15,000원 × 10마리
    for key, value in profit_info.items():
        print(f"  {key}: {value}")


def demonstrate_dynamic_reloading():
    """동적 리로딩 시연"""
    print("\n🔄 동적 상수 리로딩")
    print("=" * 40)
    
    provider = get_constants_provider()
    
    # 현재 값 출력
    current_threshold = GameConstants.PROBABILITY_HIGH_THRESHOLD.get(provider)
    print(f"현재 높은 확률 임계값: {current_threshold}")
    
    print("\n💡 엑셀 파일에서 값을 변경한 후 reload_all_constants()를 호출하면")
    print("   코드 재시작 없이 새로운 값이 적용됩니다!")
    
    # 리로딩 (실제로는 엑셀 파일이 변경되었을 때만 의미가 있음)
    reload_all_constants()
    reloaded_threshold = GameConstants.PROBABILITY_HIGH_THRESHOLD.get(provider)
    print(f"리로딩 후 값: {reloaded_threshold}")


def demonstrate_validation():
    """상수 유효성 검사 시연"""
    print("\n✅ 상수 유효성 검사")
    print("=" * 40)
    
    errors = validate_constants()
    
    if errors:
        print("❌ 발견된 오류들:")
        for constant_name, error_msg in errors.items():
            print(f"  - {constant_name}: {error_msg}")
    else:
        print("🎉 모든 상수가 유효합니다!")


def demonstrate_constants_listing():
    """모든 상수 목록 시연"""
    print("\n📋 정의된 모든 상수")
    print("=" * 40)
    
    provider = get_constants_provider()
    all_definitions = provider.list_all_constants()
    
    # 카테고리별로 그룹화
    categories = {}
    for key, definition in all_definitions.items():
        category = definition.category
        if category not in categories:
            categories[category] = []
        categories[category].append(definition)
    
    for category, definitions in categories.items():
        print(f"\n🏷️ {category.upper()}:")
        for definition in definitions:
            print(f"  - {definition.key}: {definition.value} ({definition.data_type})")
            if definition.description:
                print(f"    └─ {definition.description}")


def compare_old_vs_new_approach():
    """기존 방식 vs 새로운 방식 비교"""
    print("\n⚡ 기존 방식 vs 새로운 방식 비교")
    print("=" * 50)
    
    print("❌ 기존 방식 (매직넘버):")
    print("```python")
    print("if money < 3000:  # 매직넘버!")
    print("    return '위험'")
    print("elif money > 15000:  # 또 다른 매직넘버!")
    print("    return '풍부'")
    print("```")
    
    print("\n✅ 새로운 방식 (엑셀 상수):")
    print("```python")
    print("provider = get_constants_provider()")
    print("low_threshold = GameConstants.MONEY_LOW_THRESHOLD.get(provider)")
    print("high_threshold = GameConstants.MONEY_HIGH_THRESHOLD.get(provider)")
    print("if money < low_threshold:")
    print("    return '위험'")
    print("elif money > high_threshold:")
    print("    return '풍부'")
    print("```")
    
    print("\n🎯 장점:")
    print("  ✅ 매직넘버 완전 제거")
    print("  ✅ 타입 안전성 보장")
    print("  ✅ 중앙 집중식 관리")
    print("  ✅ 동적 밸런싱 가능")
    print("  ✅ 비개발자도 수정 가능")
    print("  ✅ 버전 관리 용이")


def main():
    """메인 실행 함수"""
    print("🚀 엑셀 기반 상수 관리 시스템 데모")
    print("=" * 60)
    
    try:
        demonstrate_basic_usage()
        demonstrate_category_access()
        demonstrate_game_logic_integration()
        demonstrate_dynamic_reloading()
        demonstrate_validation()
        demonstrate_constants_listing()
        compare_old_vs_new_approach()
        
        print("\n" + "=" * 60)
        print("✨ 데모 완료!")
        print("\n💡 다음 단계:")
        print("1. 기존 game_constants.py 파일들을 정리하세요")
        print("2. 모든 하드코딩된 숫자를 엑셀 상수로 교체하세요")
        print("3. 게임 밸런싱을 엑셀에서 직접 조정해보세요")
        
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
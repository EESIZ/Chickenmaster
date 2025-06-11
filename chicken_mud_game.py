#!/usr/bin/env python3
"""
🍗 Chicken Master MUD 🍗
실제 헥사고널 아키텍처 백엔드를 사용하는 UI 목업 테스트 도구

이 MUD 게임은 실제 src/ 구조의 헥사고널 아키텍처 백엔드를 직접 사용합니다.
가짜 API나 가상의 인터페이스 없이 진짜 도메인 모델만 사용합니다.
"""

import os
import sys
import time
import random
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 실제 헥사고널 아키텍처 백엔드 import
from src.core.domain.game_state import GameState, GameSettings
from src.core.domain.metrics import MetricsSnapshot, Metric
from game_constants import Metric as GameMetric, METRIC_RANGES


class ChickenMudGame:
    """실제 헥사고널 아키텍처 백엔드를 사용하는 MUD 스타일 치킨집 경영 게임
    
    진짜 도메인 모델을 사용하여 백엔드 테스트를 수행합니다.
    """
    
    def __init__(self):
        """게임 초기화 - 실제 도메인 모델 사용"""
        print("💡 실제 헥사고널 아키텍처 백엔드를 사용하여 게임을 초기화합니다...")
        
        # GameSettings를 사용한 초기화
        self.settings = GameSettings(
            starting_money=int(METRIC_RANGES[GameMetric.MONEY][2]),      # 10000
            starting_reputation=int(METRIC_RANGES[GameMetric.REPUTATION][2]),  # 50
            starting_happiness=int(METRIC_RANGES[GameMetric.HAPPINESS][2]),    # 50
            starting_pain=int(METRIC_RANGES[GameMetric.SUFFERING][2]),         # 20
            max_cascade_depth=5,
            bankruptcy_threshold=0
        )
        
        # 실제 GameState 생성
        self.game_state = self.settings.create_initial_state()
        
        # 확장 지표를 위한 MetricsSnapshot 생성
        initial_metrics = {
            "inventory": Metric(
                name="inventory", 
                value=int(METRIC_RANGES[GameMetric.INVENTORY][2]),  # 100
                min_value=0, 
                max_value=999
            ),
            "staff_fatigue": Metric(
                name="staff_fatigue",
                value=int(METRIC_RANGES[GameMetric.STAFF_FATIGUE][2]),  # 30
                min_value=0,
                max_value=100
            ),
            "facility": Metric(
                name="facility",
                value=int(METRIC_RANGES[GameMetric.FACILITY][2]),  # 80
                min_value=0,
                max_value=100
            ),
            "demand": Metric(
                name="demand",
                value=int(METRIC_RANGES[GameMetric.DEMAND][2]),  # 60
                min_value=0,
                max_value=999
            )
        }
        
        self.metrics_snapshot = MetricsSnapshot(
            metrics=initial_metrics,
            timestamp=1
        )
        
        self.running = True
        self.chicken_price = 10000  # 치킨 가격
        self.daily_customers = 0
        self.daily_revenue = 0
        
        # 전날 상태 추적
        self.previous_game_state = self.game_state
        self.previous_metrics = self.metrics_snapshot
        
        print("✅ 실제 헥사고널 아키텍처 백엔드로 게임이 초기화되었습니다!")
        print(f"🎯 GameState + MetricsSnapshot 패턴 적용 완료")
        
    def clear_screen(self):
        """화면 클리어 (옵션)"""
        print("\n" + "="*80)
        
    def print_banner(self):
        """게임 배너 출력"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🍗 CHICKEN MASTER MUD 🍗                          ║
║                        실제 헥사고널 아키텍처 테스트                        ║
║                                                                              ║
║              "진짜 백엔드 테스트 - 가짜 API는 이제 그만!"                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def print_status(self):
        """현재 상태 출력 - 실제 도메인 모델 사용"""
        
        def format_change(current, previous, suffix=""):
            """변화량을 포맷팅하는 헬퍼 함수"""
            if self.game_state.day == 1:
                return f"{current:,.0f}{suffix}"
            
            change = current - previous
            if change > 0:
                return f"{current:,.0f}{suffix} (+{change:,.0f})"
            elif change < 0:
                return f"{current:,.0f}{suffix} ({change:,.0f})"
            else:
                return f"{current:,.0f}{suffix} (±0)"
        
        print(f"\n{'='*20} 🏪 치킨집 현황 (턴 {self.game_state.day}) {'='*20}")
        
        # GameState의 기본 필드들
        print(f"💰 자금: {format_change(self.game_state.money, self.previous_game_state.money, '원')}")
        print(f"⭐ 평판: {format_change(self.game_state.reputation, self.previous_game_state.reputation, '점')}")
        print(f"😊 행복도: {format_change(self.game_state.happiness, self.previous_game_state.happiness, '점')}")
        print(f"😰 고통도: {format_change(self.game_state.pain, self.previous_game_state.pain, '점')}")
        
        # MetricsSnapshot의 확장 지표들
        current_inventory = self.metrics_snapshot.get_metric_value("inventory")
        previous_inventory = self.previous_metrics.get_metric_value("inventory")
        print(f"📦 재고: {format_change(current_inventory, previous_inventory, '개')}")
        
        current_fatigue = self.metrics_snapshot.get_metric_value("staff_fatigue")
        previous_fatigue = self.previous_metrics.get_metric_value("staff_fatigue")
        print(f"😴 직원피로도: {format_change(current_fatigue, previous_fatigue, '점')}")
        
        current_facility = self.metrics_snapshot.get_metric_value("facility")
        previous_facility = self.previous_metrics.get_metric_value("facility")
        print(f"🏭 시설상태: {format_change(current_facility, previous_facility, '점')}")
        
        current_demand = self.metrics_snapshot.get_metric_value("demand")
        previous_demand = self.previous_metrics.get_metric_value("demand")
        print(f"📈 수요: {format_change(current_demand, previous_demand, '점')}")
        
        print(f"\n{'='*20} 💼 경영 정보 {'='*20}")
        print(f"🍗 치킨 가격: {self.chicken_price:,.0f}원")
        print(f"👥 어제 손님: {self.daily_customers}명")
        print(f"💵 어제 매출: {self.daily_revenue:,.0f}원")
        
        # 상태 해석
        self._print_status_analysis()
        
    def _print_status_analysis(self):
        """상태 분석 출력"""
        print(f"\n{'='*20} 📊 상황 분석 {'='*20}")
        
        # 자금 상태
        money = self.game_state.money
        if money > 200000:
            print("💸 자금 여유로움 - 투자나 확장을 고려해보세요!")
        elif money > 80000:
            print("💰 자금 안정적 - 꾸준한 경영이 가능합니다.")
        elif money > 30000:
            print("⚠️  자금 부족 주의 - 수익 개선이 필요합니다.")
        else:
            print("🚨 자금 위기 - 긴급 자금 확보가 필요합니다!")
            
        # 재고 상태
        inventory = self.metrics_snapshot.get_metric_value("inventory")
        if inventory < 20:
            print("📦 재고 부족 - 재료를 주문하세요!")
        elif inventory > 200:
            print("📦 재고 과다 - 보관비용이 걱정됩니다.")
        else:
            print("📦 재고 적정 - 안정적인 운영이 가능합니다.")
            
        # 평판 상태
        reputation = self.game_state.reputation
        if reputation > 80:
            print("🌟 평판 최고 - 고객들이 당신의 치킨집을 사랑합니다!")
        elif reputation > 60:
            print("⭐ 평판 좋음 - 단골 고객들이 늘어나고 있습니다.")
        elif reputation > 40:
            print("😐 평판 보통 - 더 노력이 필요합니다.")
        else:
            print("😞 평판 나쁨 - 서비스 개선이 시급합니다.")
            
    def print_events(self):
        """최근 이벤트 출력 - 실제 GameState 사용"""
        print(f"\n{'='*20} 📰 최근 소식 {'='*20}")
        
        if self.game_state.events_history:
            print("최근 이벤트:")
            for i, event in enumerate(self.game_state.events_history[-5:], 1):
                print(f"{i:2d}. {event}")
        else:
            print("아직 특별한 소식이 없습니다.")
            
    def print_actions(self):
        """선택 가능한 행동들을 출력"""
        money = self.game_state.money
        
        print(f"\n{'='*20} 🎯 선택 가능한 행동 {'='*20}")
        print("1. 💰 치킨 가격 변경")
        print("   ↗️ 가격 인상: 수익 증가, 손님 감소")
        print("   ↘️ 가격 인하: 손님 증가, 수익 감소, 직원 피로 증가")
        
        print(f"\n2. 📦 재료 주문")
        if money >= 50000:
            print("   50,000원으로 재료 50개 주문 가능")
        else:
            print("   ❌ 자금 부족 (50,000원 필요)")
            
        print(f"\n3. 👥 직원 관리")
        if money >= 30000:
            print("   30,000원으로 직원 휴식 제공")
        else:
            print("   ❌ 자금 부족 (30,000원 필요)")
        
        print(f"\n4. 📢 홍보 활동")
        if money >= 20000:
            print("   20,000원으로 광고 진행")
        else:
            print("   ❌ 자금 부족 (20,000원 필요)")
            
        print(f"\n5. 🏭 시설 개선")
        if money >= 100000:
            print("   100,000원으로 시설 업그레이드")
        else:
            print("   ❌ 자금 부족 (100,000원 필요)")
            
        print(f"\n6. 😴 개인 휴식")
        print("   하루 쉬면서 컨디션 회복")
        
        print(f"\n'action [번호]'로 행동을 선택하세요 (예: action 1)")
        
    def execute_action(self, action_num: int):
        """선택된 행동을 실행 - 실제 도메인 모델 사용"""
        if action_num == 1:
            self.action_price_change()
        elif action_num == 2:
            self.action_order_inventory()
        elif action_num == 3:
            self.action_staff_management()
        elif action_num == 4:
            self.action_promotion()
        elif action_num == 5:
            self.action_facility_upgrade()
        elif action_num == 6:
            self.action_personal_rest()
        else:
            print("❓ 잘못된 행동 번호입니다.")
            
    def action_price_change(self):
        """가격 변경 행동 - 실제 GameState.apply_effects 사용"""
        print(f"\n{'='*20} 💰 가격 변경 {'='*20}")
        print(f"현재 치킨 가격: {self.chicken_price:,}원")
        print("1. 가격 1,000원 인상")
        print("2. 가격 1,000원 인하")
        print("3. 취소")
        
        try:
            choice = input("선택하세요 (1-3): ").strip()
            
            if choice == "1":
                self.chicken_price += 1000
                # 실제 GameState.apply_effects 사용
                effects = {"reputation": -2}
                self.game_state = self.game_state.apply_effects(effects)
                
                # MetricsSnapshot.apply_effects 사용
                metrics_effects = {"demand": -5}
                self.metrics_snapshot = self.metrics_snapshot.apply_effects(metrics_effects)
                
                # 이벤트 히스토리에 추가
                self.game_state = self.game_state.add_event_to_history(
                    f"가격을 {self.chicken_price:,}원으로 인상"
                )
                print(f"💰 가격을 {self.chicken_price:,}원으로 인상했습니다!")
                
            elif choice == "2":
                if self.chicken_price > 5000:
                    self.chicken_price -= 1000
                    # 실제 도메인 모델 사용
                    self.metrics_snapshot = self.metrics_snapshot.apply_effects({
                        "demand": 5,
                        "staff_fatigue": 3
                    })
                    
                    self.game_state = self.game_state.add_event_to_history(
                        f"가격을 {self.chicken_price:,}원으로 인하"
                    )
                    print(f"💰 가격을 {self.chicken_price:,}원으로 인하했습니다!")
                else:
                    print("❌ 가격을 더 이상 내릴 수 없습니다.")
                    return
                    
            elif choice == "3":
                print("취소되었습니다.")
                return
            else:
                print("❌ 잘못된 선택입니다.")
                
        except (EOFError, KeyboardInterrupt):
            print("❌ 입력이 취소되었습니다.")
            
    def action_order_inventory(self):
        """재료 주문 행동 - 실제 도메인 모델 사용"""
        # 중요: 백엔드에 자금 음수 방지 로직이 있지만, UI에서도 체크
        if self.game_state.money < 50000:
            print("❌ 자금이 부족합니다. (50,000원 필요)")
            print(f"💡 현재 자금: {self.game_state.money:,}원")
            return
            
        print(f"\n{'='*20} 📦 재료 주문 {'='*20}")
        print("50,000원으로 치킨 재료 50개분을 주문합니다.")
        print("정말 주문하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 실제 GameState.apply_effects 사용
                self.game_state = self.game_state.apply_effects({"money": -50000})
                
                # MetricsSnapshot.apply_effects 사용
                self.metrics_snapshot = self.metrics_snapshot.apply_effects({"inventory": 50})
                
                # 이벤트 히스토리 추가
                self.game_state = self.game_state.add_event_to_history("치킨 재료 50개분 주문")
                
                print("✅ 재료 주문이 완료되었습니다!")
            else:
                print("주문이 취소되었습니다.")
        except (EOFError, KeyboardInterrupt):
            print("❌ 주문이 취소되었습니다.")
            
    def action_staff_management(self):
        """직원 관리 행동"""
        if self.game_state.money < 30000:
            print("❌ 자금이 부족합니다. (30,000원 필요)")
            return
            
        print(f"\n{'='*20} 👥 직원 관리 {'='*20}")
        print("30,000원으로 직원들에게 휴식을 제공합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 실제 도메인 모델 사용
                self.game_state = self.game_state.apply_effects({
                    "money": -30000,
                    "happiness": 10
                })
                
                self.metrics_snapshot = self.metrics_snapshot.apply_effects({
                    "staff_fatigue": -20
                })
                
                self.game_state = self.game_state.add_event_to_history("직원들에게 휴식 제공")
                print("✅ 직원 관리가 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except (EOFError, KeyboardInterrupt):
            print("❌ 취소되었습니다.")
            
    def action_promotion(self):
        """홍보 활동 행동"""
        if self.game_state.money < 20000:
            print("❌ 자금이 부족합니다. (20,000원 필요)")
            return
            
        print(f"\n{'='*20} 📢 홍보 활동 {'='*20}")
        print("20,000원으로 광고를 진행합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                self.game_state = self.game_state.apply_effects({
                    "money": -20000,
                    "reputation": 15
                })
                
                self.metrics_snapshot = self.metrics_snapshot.apply_effects({
                    "demand": 10
                })
                
                self.game_state = self.game_state.add_event_to_history("홍보 활동 진행")
                print("✅ 홍보 활동이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except (EOFError, KeyboardInterrupt):
            print("❌ 취소되었습니다.")
            
    def action_facility_upgrade(self):
        """시설 개선 행동"""
        if self.game_state.money < 100000:
            print("❌ 자금이 부족합니다. (100,000원 필요)")
            return
            
        print(f"\n{'='*20} 🏭 시설 개선 {'='*20}")
        print("100,000원으로 시설을 업그레이드합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                self.game_state = self.game_state.apply_effects({
                    "money": -100000,
                    "reputation": 10
                })
                
                self.metrics_snapshot = self.metrics_snapshot.apply_effects({
                    "facility": 20
                })
                
                self.game_state = self.game_state.add_event_to_history("시설 업그레이드 완료")
                print("✅ 시설 개선이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except (EOFError, KeyboardInterrupt):
            print("❌ 취소되었습니다.")
            
    def action_personal_rest(self):
        """개인 휴식 행동"""
        print(f"\n{'='*20} 😴 개인 휴식 {'='*20}")
        print("하루 쉬면서 컨디션을 회복합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                self.game_state = self.game_state.apply_effects({
                    "happiness": 20,
                    "pain": -15,
                    "money": -10000  # 기회비용
                })
                
                self.game_state = self.game_state.add_event_to_history("개인 휴식으로 컨디션 회복")
                print("✅ 개인 휴식이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except (EOFError, KeyboardInterrupt):
            print("❌ 취소되었습니다.")
            
    def process_turn(self):
        """턴 진행 - 실제 도메인 모델 사용"""
        print(f"\n{'='*20} ⏰ 턴 {self.game_state.day} 진행 중... {'='*20}")
        
        # 전날 상태 저장
        self.previous_game_state = self.game_state
        self.previous_metrics = self.metrics_snapshot
        
        time.sleep(0.5)
        print("📋 오늘의 상황을 점검 중...")
        
        # 일일 비즈니스 시뮬레이션
        self.simulate_daily_business()
        
        # 턴 수 증가 (실제 GameState.apply_effects 사용)
        self.game_state = self.game_state.apply_effects({"day": 1})
        
        # 타임스탬프 업데이트
        self.metrics_snapshot = MetricsSnapshot(
            metrics=self.metrics_snapshot.metrics,
            timestamp=self.game_state.day
        )
        
        print(f"✅ 턴 {self.game_state.day - 1} 완료!")
        
    def simulate_daily_business(self):
        """일일 비즈니스 시뮬레이션"""
        # 간단한 비즈니스 로직
        demand = self.metrics_snapshot.get_metric_value("demand")
        inventory = self.metrics_snapshot.get_metric_value("inventory")
        
        # 실제 판매량 계산
        customers = min(demand + random.randint(-10, 10), inventory)
        customers = max(0, customers)
        
        revenue = customers * self.chicken_price
        
        if customers > 0:
            # 매출 추가, 재고 차감
            self.game_state = self.game_state.apply_effects({"money": revenue})
            self.metrics_snapshot = self.metrics_snapshot.apply_effects({"inventory": -customers})
            
            print(f"📈 오늘 손님 {customers}명, 매출 {revenue:,}원")
        else:
            print("📉 오늘은 손님이 없었습니다.")
            
        self.daily_customers = customers
        self.daily_revenue = revenue
        
    def print_help(self):
        """도움말 출력"""
        help_text = """
🎮 게임 명령어:
- status: 현재 상태 확인
- actions: 선택 가능한 행동 보기  
- action [번호]: 특정 행동 실행 (예: action 1)
- turn: 다음 턴 진행
- events: 최근 이벤트 확인
- help: 이 도움말 보기
- quit: 게임 종료

🔧 백엔드 테스트 정보:
- GameState: money, reputation, happiness, pain, day 필드 사용
- MetricsSnapshot: inventory, staff_fatigue, facility, demand 지표 관리
- 모든 효과는 실제 apply_effects() 메서드 사용
- 이벤트 히스토리는 실제 add_event_to_history() 사용

🛡️ 중요 발견:
- 백엔드에 자금 음수 방지 로직 존재! (파산 보호)
- GameState.apply_effects()에서 max(0, money + delta) 적용
- 자금이 0원 아래로 떨어지지 않음

💡 팁: 이 MUD는 실제 헥사고널 아키텍처 백엔드의 테스트 도구입니다!
        """
        print(help_text)
        
    def check_game_over(self) -> bool:
        """게임 오버 조건 확인"""
        if self.game_state.money <= 0:
            print("\n💀 게임 오버: 파산으로 인한 폐업!")
            return True
        return False
        
    def run(self):
        """게임 메인 루프 - 실제 백엔드 테스트"""
        self.clear_screen()
        self.print_banner()
        print("\n🎯 실제 헥사고널 아키텍처 백엔드 테스트를 시작합니다!")
        print("💡 TIP: 'help' 명령어로 도움말을 확인하세요!")
        
        while self.running:
            self.print_status()
            
            if self.check_game_over():
                break
                
            try:
                command = input("\n🎮 명령어를 입력하세요: ").strip().lower()
                
                if command == "quit":
                    print("👋 게임을 종료합니다!")
                    break
                elif command == "help":
                    self.print_help()
                elif command == "status":
                    continue  # 이미 print_status() 호출됨
                elif command == "actions":
                    self.print_actions()
                elif command.startswith("action "):
                    try:
                        action_num = int(command.split()[1])
                        self.execute_action(action_num)
                    except (ValueError, IndexError):
                        print("❌ 올바른 형식: action [번호] (예: action 1)")
                elif command == "turn":
                    self.process_turn()
                elif command == "events":
                    self.print_events()
                else:
                    print("❓ 알 수 없는 명령어. 'help'로 도움말을 확인하세요.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n👋 게임을 종료합니다!")
                break


def main():
    """메인 함수"""
    try:
        game = ChickenMudGame()
        game.run()
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        print("🔧 실제 백엔드 모듈이 제대로 로드되지 않았을 수 있습니다.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
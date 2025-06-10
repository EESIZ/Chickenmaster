#!/usr/bin/env python3
"""
🍗 Chicken Master MUD 🍗
옛날 MUD 게임 스타일 치킨집 경영 시뮬레이션

Commands:
- status: 현재 상태 확인
- actions: 선택 가능한 행동 보기
- action [번호]: 특정 행동 실행
- turn: 다음 턴 진행
- events: 현재 이벤트 확인
- help: 도움말
- quit: 게임 종료
"""

import os
import sys
import time
import random
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.events.engine import EventEngine
from src.metrics.tracker import MetricsTracker  
from src.economy.engine import tradeoff_apply_price_change, compute_profit_no_right_answer, update_economy_state
from src.core.domain.game_state import GameState, GameSettings
from src.storyteller import StorytellerService, NarrativeResponse, StoryContext
from game_constants import Metric


class ChickenMudGame:
    """MUD 스타일 치킨집 경영 게임"""
    
    def __init__(self):
        """게임 초기화"""
        self.metrics_tracker = MetricsTracker()
        self.event_engine = EventEngine(
            self.metrics_tracker,
            events_file="data/events.toml",  # 기존 이벤트 시스템 사용
            tradeoff_file="data/tradeoff_matrix.toml"
        )
        
        # 스토리텔러 시스템 연결
        try:
            self.storyteller = StorytellerService()
        except Exception as e:
            print(f"스토리텔러 초기화 실패: {e}")
            self.storyteller = None
            
        # 게임 설정 및 상태 관리
        self.game_settings = GameSettings(
            starting_money=100000,
            starting_reputation=50,
            starting_happiness=70,
            starting_pain=30,
            max_cascade_depth=10,
            bankruptcy_threshold=-50000
        )
        
        self.turn = 0
        self.running = True
        self.current_price = 10000  # 치킨 가격 (원)
        self.daily_customers = 0
        self.daily_revenue = 0
        
        # 전날 지표 추적을 위한 변수
        self.previous_metrics = {}
        self.previous_customers = 0
        self.previous_revenue = 0
        
        # 게임 초기 설정
        initial_metrics = {
            Metric.MONEY: 100000,  # 10만원으로 시작
            Metric.REPUTATION: 50,
            Metric.HAPPINESS: 70,
            Metric.SUFFERING: 30,
            Metric.INVENTORY: 100,  # 치킨 100마리분 재료
            Metric.STAFF_FATIGUE: 30,
            Metric.FACILITY: 80,
            Metric.DEMAND: 60,
        }
        self.metrics_tracker.tradeoff_update_metrics(initial_metrics)
        
        # 가격에 따른 기본 수요 계산
        self.update_demand()
        
    def clear_screen(self):
        """화면 클리어 (옵션)"""
        # os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*80)
        
    def print_banner(self):
        """게임 배너 출력"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🍗 CHICKEN MASTER MUD 🍗                          ║
║                        치킨집 경영 시뮬레이션 게임                          ║
║                                                                              ║
║  "정답 없는 선택의 연속, 트레이드오프의 세계에 오신 것을 환영합니다!"      ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def print_status(self):
        """현재 상태 출력"""
        metrics = self.metrics_tracker.get_metrics()
        
        def format_change(current, previous, suffix=""):
            """변화량을 포맷팅하는 헬퍼 함수"""
            if not self.previous_metrics or self.turn == 0:
                return f"{current:,.0f}{suffix}"
            
            change = current - previous
            if change > 0:
                return f"{current:,.0f}{suffix} (+{change:,.0f})"
            elif change < 0:
                return f"{current:,.0f}{suffix} ({change:,.0f})"
            else:
                return f"{current:,.0f}{suffix} (±0)"
        
        print(f"\n{'='*20} 🏪 치킨집 현황 (턴 {self.turn}) {'='*20}")
        print(f"💰 자금: {format_change(metrics.get(Metric.MONEY, 0), self.previous_metrics.get(Metric.MONEY, 0), '원')}")
        print(f"⭐ 평판: {format_change(metrics.get(Metric.REPUTATION, 0), self.previous_metrics.get(Metric.REPUTATION, 0), '점')}")
        print(f"😊 행복도: {format_change(metrics.get(Metric.HAPPINESS, 0), self.previous_metrics.get(Metric.HAPPINESS, 0), '점')}")
        print(f"😰 고통도: {format_change(metrics.get(Metric.SUFFERING, 0), self.previous_metrics.get(Metric.SUFFERING, 0), '점')}")
        print(f"📦 재고: {format_change(metrics.get(Metric.INVENTORY, 0), self.previous_metrics.get(Metric.INVENTORY, 0), '개')}")
        print(f"😴 직원피로도: {format_change(metrics.get(Metric.STAFF_FATIGUE, 0), self.previous_metrics.get(Metric.STAFF_FATIGUE, 0), '점')}")
        print(f"🏭 시설상태: {format_change(metrics.get(Metric.FACILITY, 0), self.previous_metrics.get(Metric.FACILITY, 0), '점')}")
        print(f"📈 수요: {format_change(metrics.get(Metric.DEMAND, 0), self.previous_metrics.get(Metric.DEMAND, 0), '점')}")
        
        print(f"\n{'='*20} 💼 경영 정보 {'='*20}")
        print(f"🍗 치킨 가격: {self.current_price:,.0f}원")
        
        # 손님 수와 매출도 전날 대비 변화 표시
        customers_change = ""
        revenue_change = ""
        
        if self.previous_customers > 0 or self.turn > 0:
            customer_diff = self.daily_customers - self.previous_customers
            if customer_diff > 0:
                customers_change = f" (+{customer_diff})"
            elif customer_diff < 0:
                customers_change = f" ({customer_diff})"
            else:
                customers_change = " (±0)"
                
        if self.previous_revenue > 0 or self.turn > 0:
            revenue_diff = self.daily_revenue - self.previous_revenue
            if revenue_diff > 0:
                revenue_change = f" (+{revenue_diff:,.0f}원)"
            elif revenue_diff < 0:
                revenue_change = f" ({revenue_diff:,.0f}원)"
            else:
                revenue_change = " (±0원)"
        
        print(f"👥 어제 손님: {self.daily_customers}명{customers_change}")
        print(f"💵 어제 매출: {self.daily_revenue:,.0f}원{revenue_change}")
        
        # 상태 해석
        money = metrics.get(Metric.MONEY, 0)
        reputation = metrics.get(Metric.REPUTATION, 0)
        happiness = metrics.get(Metric.HAPPINESS, 0)
        suffering = metrics.get(Metric.SUFFERING, 0)
        inventory = metrics.get(Metric.INVENTORY, 0)
        
        print(f"\n{'='*20} 📊 상황 분석 {'='*20}")
        
        # 자금 상태
        if money > 200000:
            print("💸 자금 여유로움 - 투자나 확장을 고려해보세요!")
        elif money > 80000:
            print("💰 자금 안정적 - 꾸준한 경영이 가능합니다.")
        elif money > 30000:
            print("⚠️  자금 부족 주의 - 수익 개선이 필요합니다.")
        else:
            print("🚨 자금 위기 - 긴급 자금 확보가 필요합니다!")
            
        # 재고 상태
        if inventory < 20:
            print("📦 재고 부족 - 재료를 주문하세요!")
        elif inventory > 200:
            print("📦 재고 과다 - 보관비용이 걱정됩니다.")
        else:
            print("📦 재고 적정 - 안정적인 운영이 가능합니다.")
            
        # 평판 상태
        if reputation > 80:
            print("🌟 평판 최고 - 고객들이 당신의 치킨집을 사랑합니다!")
        elif reputation > 60:
            print("⭐ 평판 좋음 - 단골 고객들이 늘어나고 있습니다.")
        elif reputation > 40:
            print("😐 평판 보통 - 더 노력이 필요합니다.")
        else:
            print("😞 평판 나쁨 - 서비스 개선이 시급합니다.")
            
        # 행복도 상태
        if happiness > 80:
            print("🎉 최고의 기분 - 모든 일이 순조롭습니다!")
        elif happiness > 60:
            print("😊 기분 좋음 - 일하는 재미가 있습니다.")
        elif happiness > 40:
            print("😑 기분 보통 - 그럭저럭 버텨나가고 있습니다.")
        else:
            print("😔 기분 나쁨 - 휴식이나 기분 전환이 필요합니다.")
            
        # 고통도 상태
        if suffering > 80:
            print("💥 극심한 고통 - 당장 휴식을 취하세요!")
        elif suffering > 60:
            print("😰 높은 고통 - 고통 관리가 필요합니다.")
        elif suffering > 40:
            print("😅 보통 고통 - 적당한 긴장감이 있습니다.")
        else:
            print("😌 낮은 고통 - 마음이 편안합니다.")
            
        # 스토리텔러 시스템 활용한 추가 내러티브
        if self.storyteller:
            try:
                story_context = StoryContext(
                    current_metrics=metrics,
                    recent_events=self.metrics_tracker.get_events()[-3:],  # 최근 3개 이벤트
                    turn_number=self.turn,
                    game_phase="status_check"
                )
                narrative = self.storyteller.generate_narrative(story_context)
                if narrative and narrative.content:
                    print(f"\n{'='*20} 📖 상황 이야기 {'='*20}")
                    print(f"🎭 {narrative.content}")
            except Exception as e:
                # 스토리텔러 오류 시 조용히 무시
                pass
            
    def print_events(self):
        """최근 이벤트 출력"""
        events = self.metrics_tracker.get_events()
        
        print(f"\n{'='*20} 📰 최근 소식 {'='*20}")
        if events:
            # 최근 10개 이벤트만 표시
            recent_events = events[-10:]
            for i, event in enumerate(recent_events, 1):
                print(f"{i:2d}. {event}")
        else:
            print("아직 특별한 소식이 없습니다.")
            
    def print_actions(self):
        """선택 가능한 행동들을 출력"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        inventory = metrics.get(Metric.INVENTORY, 0)
        
        print(f"\n{'='*20} 🎯 선택 가능한 행동 {'='*20}")
        print("1. 💰 치킨 가격 변경")
        print("   현재 가격에서 ±1000원 조정 가능")
        print("   ↗️ 가격 인상: 수익 증가, 손님 감소")
        print("   ↘️ 가격 인하: 손님 증가, 수익 감소, 직원 피로 증가")
        
        print("\n2. 📦 재료 주문")
        if money >= 50000:
            print("   50,000원으로 재료 50개 주문 가능")
            print("   💰 자금 소모, 📦 재고 증가")
        else:
            print("   ❌ 자금 부족 (50,000원 필요)")
            
        print("\n3. 👥 직원 관리")
        print("   30,000원으로 직원 휴식 제공")
        print("   💰 자금 소모, 😴 피로도 감소, 😊 행복도 증가")
        
        print("\n4. 📢 홍보 활동")
        if money >= 20000:
            print("   20,000원으로 광고 진행")
            print("   💰 자금 소모, ⭐ 평판 증가, 📈 수요 증가")
        else:
            print("   ❌ 자금 부족 (20,000원 필요)")
            
        print("\n5. 🏭 시설 개선")
        if money >= 100000:
            print("   100,000원으로 시설 업그레이드")
            print("   💰 자금 소모, 🏭 시설상태 개선, ⭐ 평판 상승")
        else:
            print("   ❌ 자금 부족 (100,000원 필요)")
            
        print("\n6. 😴 개인 휴식")
        print("   하루 쉬면서 컨디션 회복")
        print("   😊 행복도 증가, 😰 고통도 감소, 💰 기회비용 발생")
        
        print(f"\n'action [번호]'로 행동을 선택하세요 (예: action 1)")
        
    def execute_action(self, action_num: int):
        """선택된 행동을 실행"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
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
        """가격 변경 행동"""
        print(f"\n{'='*20} 💰 가격 변경 {'='*20}")
        print(f"현재 치킨 가격: {self.current_price:,}원")
        print("1. 가격 1,000원 인상 (수익↗️, 손님↘️)")
        print("2. 가격 1,000원 인하 (손님↗️, 수익↘️, 피로↗️)")
        print("3. 취소")
        
        try:
            choice = input("선택하세요 (1-3): ").strip()
            if choice == "1":
                self.current_price += 1000
                price_change = 1000
                print(f"💰 가격을 {self.current_price:,}원으로 인상했습니다!")
            elif choice == "2":
                if self.current_price > 5000:
                    self.current_price -= 1000
                    price_change = -1000
                    print(f"💰 가격을 {self.current_price:,}원으로 인하했습니다!")
                else:
                    print("❌ 가격을 더 이상 내릴 수 없습니다.")
                    return
            elif choice == "3":
                print("취소되었습니다.")
                return
            else:
                print("❌ 잘못된 선택입니다.")
                return
                
            # 가격 변경 효과 적용 (기존 방식)
            current_metrics = self.metrics_tracker.get_metrics()
            updated_metrics = tradeoff_apply_price_change(price_change, current_metrics)
            self.metrics_tracker.tradeoff_update_metrics(updated_metrics)
            
            # 경제 엔진의 상태 업데이트 시스템 추가 활용
            try:
                from game_constants import ActionType
                decision = {
                    "action_type": ActionType.PRICE_CHANGE,
                    "price_change": price_change
                }
                current_state = {
                    "metrics": current_metrics,
                    "price": self.current_price,
                    "turn": self.turn
                }
                updated_state = update_economy_state(current_state, decision)
                # 추가 경제 효과 반영 (있다면)
            except Exception:
                # 경제 엔진 오류 시 기존 방식 유지
                pass
                
            self.update_demand()
            
            if price_change > 0:
                self.metrics_tracker.add_event(f"가격을 {self.current_price:,}원으로 인상했습니다.")
            else:
                self.metrics_tracker.add_event(f"가격을 {self.current_price:,}원으로 인하했습니다.")
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 입력이 취소되었습니다.")
            
    def action_order_inventory(self):
        """재료 주문 행동"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
        if money < 50000:
            print("❌ 자금이 부족합니다. (50,000원 필요)")
            return
            
        print(f"\n{'='*20} 📦 재료 주문 {'='*20}")
        print("50,000원으로 치킨 재료 50개분을 주문합니다.")
        print("정말 주문하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 자금 차감, 재고 증가
                updates = {
                    Metric.MONEY: money - 50000,
                    Metric.INVENTORY: metrics.get(Metric.INVENTORY, 0) + 50
                }
                self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event("치킨 재료 50개분을 주문했습니다.")
                print("✅ 재료 주문이 완료되었습니다!")
            else:
                print("주문이 취소되었습니다.")
        except KeyboardInterrupt:
            print("❌ 주문이 취소되었습니다.")
            
    def action_staff_management(self):
        """직원 관리 행동"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
        if money < 30000:
            print("❌ 자금이 부족합니다. (30,000원 필요)")
            return
            
        print(f"\n{'='*20} 👥 직원 관리 {'='*20}")
        print("30,000원으로 직원들에게 휴식을 제공합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 자금 차감, 피로도 감소, 행복도 증가
                updates = {
                    Metric.MONEY: money - 30000,
                    Metric.STAFF_FATIGUE: max(0, metrics.get(Metric.STAFF_FATIGUE, 0) - 20),
                    Metric.HAPPINESS: min(100, metrics.get(Metric.HAPPINESS, 0) + 10)
                }
                self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event("직원들에게 휴식을 제공했습니다.")
                print("✅ 직원 관리가 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except KeyboardInterrupt:
            print("❌ 취소되었습니다.")
            
    def action_promotion(self):
        """홍보 활동 행동"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
        if money < 20000:
            print("❌ 자금이 부족합니다. (20,000원 필요)")
            return
            
        print(f"\n{'='*20} 📢 홍보 활동 {'='*20}")
        print("20,000원으로 광고를 진행합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 자금 차감, 평판 증가, 수요 증가
                updates = {
                    Metric.MONEY: money - 20000,
                    Metric.REPUTATION: min(100, metrics.get(Metric.REPUTATION, 0) + 15),
                    Metric.DEMAND: min(100, metrics.get(Metric.DEMAND, 0) + 10)
                }
                self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event("홍보 활동을 진행했습니다.")
                print("✅ 홍보 활동이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except KeyboardInterrupt:
            print("❌ 취소되었습니다.")
            
    def action_facility_upgrade(self):
        """시설 개선 행동"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
        if money < 100000:
            print("❌ 자금이 부족합니다. (100,000원 필요)")
            return
            
        print(f"\n{'='*20} 🏭 시설 개선 {'='*20}")
        print("100,000원으로 시설을 업그레이드합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                # 자금 차감, 시설 상태 개선, 평판 상승
                updates = {
                    Metric.MONEY: money - 100000,
                    Metric.FACILITY: min(100, metrics.get(Metric.FACILITY, 0) + 20),
                    Metric.REPUTATION: min(100, metrics.get(Metric.REPUTATION, 0) + 10)
                }
                self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event("시설을 업그레이드했습니다.")
                print("✅ 시설 개선이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except KeyboardInterrupt:
            print("❌ 취소되었습니다.")
            
    def action_personal_rest(self):
        """개인 휴식 행동"""
        print(f"\n{'='*20} 😴 개인 휴식 {'='*20}")
        print("하루 쉬면서 컨디션을 회복합니다.")
        print("정말 진행하시겠습니까? (y/n)")
        
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', 'ㅇ']:
                metrics = self.metrics_tracker.get_metrics()
                # 행복도 증가, 고통도 감소, 약간의 매출 손실
                updates = {
                    Metric.HAPPINESS: min(100, metrics.get(Metric.HAPPINESS, 0) + 20),
                    Metric.SUFFERING: max(0, metrics.get(Metric.SUFFERING, 0) - 15),
                    Metric.MONEY: metrics.get(Metric.MONEY, 0) - 10000  # 기회비용
                }
                self.metrics_tracker.tradeoff_update_metrics(updates)
                self.metrics_tracker.add_event("하루 쉬면서 컨디션을 회복했습니다.")
                print("✅ 개인 휴식이 완료되었습니다!")
            else:
                print("취소되었습니다.")
        except KeyboardInterrupt:
            print("❌ 취소되었습니다.")
            
    def update_demand(self):
        """가격에 따른 수요 업데이트"""
        metrics = self.metrics_tracker.get_metrics()
        
        # 기본 수요는 가격에 반비례 (가격이 높으면 수요 감소)
        base_demand = max(10, 100 - (self.current_price - 8000) / 100)
        
        # 평판에 따른 수요 보정
        reputation = metrics.get(Metric.REPUTATION, 50)
        reputation_factor = reputation / 50  # 50을 기준으로 정규화
        
        # 시설 상태에 따른 수요 보정
        facility = metrics.get(Metric.FACILITY, 80)
        facility_factor = facility / 80  # 80을 기준으로 정규화
        
        final_demand = base_demand * reputation_factor * facility_factor
        
        updates = {Metric.DEMAND: max(0, min(100, final_demand))}
        self.metrics_tracker.tradeoff_update_metrics(updates)
        
    def process_turn(self):
        """턴 진행"""
        print(f"\n{'='*20} ⏰ 턴 {self.turn + 1} 진행 중... {'='*20}")
        
        # 이벤트 엔진 업데이트
        time.sleep(0.5)  # 약간의 딜레이로 긴장감 연출
        print("📋 오늘의 상황을 점검 중...")
        
        time.sleep(0.5)
        print("🔍 이벤트 발생 가능성 확인 중...")
        
        # 일일 운영 시뮬레이션
        self.simulate_daily_business()
        
        # 실제 턴 진행
        updated_metrics = self.event_engine.update()
        self.turn += 1
        
        time.sleep(0.5)
        print("✅ 하루 운영 완료!")
        
        # 수요 업데이트
        self.update_demand()
        
        # 발생한 이벤트가 있다면 즉시 강조 표시
        alerts = self.event_engine.get_alerts()
        if alerts:
            print(f"\n{'🚨'*25}")
            print(f"{'='*20} 🚨 특별 이벤트 발생! {'='*20}")
            print(f"{'🚨'*25}")
            for alert in alerts:
                print(f"📢 ⚠️  {alert.message}")
                
                # 스토리텔러 시스템으로 이벤트 내러티브 생성
                if self.storyteller:
                    try:
                        story_context = StoryContext(
                            current_metrics=self.metrics_tracker.get_metrics(),
                            recent_events=[alert.message],
                            turn_number=self.turn,
                            game_phase="event_occurred"
                        )
                        narrative = self.storyteller.generate_narrative(story_context)
                        if narrative and narrative.content:
                            print(f"🎭 {narrative.content}")
                    except Exception:
                        # 스토리텔러 오류 시 조용히 무시
                        pass
                        
            print(f"{'🚨'*25}")
            input("📌 Enter를 눌러서 계속...")  # 사용자가 확인할 때까지 대기
            print("\n💡 TIP: 'e' 명령어로 최근 이벤트들을 다시 확인할 수 있습니다!")
        
        # 지표 변화 표시
        print(f"\n{'='*20} 📈 오늘의 결과 {'='*20}")
        print(f"👥 손님: {self.daily_customers}명")
        print(f"💵 매출: {self.daily_revenue:,.0f}원")
        
        # 주요 변화량 하이라이트
        current_metrics = self.metrics_tracker.get_metrics()
        significant_changes = []
        
        if self.previous_metrics:
            # 큰 변화량들을 감지하고 하이라이트
            money_change = current_metrics.get(Metric.MONEY, 0) - self.previous_metrics.get(Metric.MONEY, 0)
            reputation_change = current_metrics.get(Metric.REPUTATION, 0) - self.previous_metrics.get(Metric.REPUTATION, 0)
            happiness_change = current_metrics.get(Metric.HAPPINESS, 0) - self.previous_metrics.get(Metric.HAPPINESS, 0)
            suffering_change = current_metrics.get(Metric.SUFFERING, 0) - self.previous_metrics.get(Metric.SUFFERING, 0)
            
            if abs(money_change) >= 20000:
                if money_change > 0:
                    significant_changes.append(f"💰 자금 대폭 증가 (+{money_change:,.0f}원)")
                else:
                    significant_changes.append(f"💸 자금 대폭 감소 ({money_change:,.0f}원)")
                    
            if abs(reputation_change) >= 10:
                if reputation_change > 0:
                    significant_changes.append(f"⭐ 평판 크게 상승 (+{reputation_change:.0f}점)")
                else:
                    significant_changes.append(f"📉 평판 크게 하락 ({reputation_change:.0f}점)")
                    
            if abs(happiness_change) >= 15:
                if happiness_change > 0:
                    significant_changes.append(f"😊 행복도 크게 증가 (+{happiness_change:.0f}점)")
                else:
                    significant_changes.append(f"😔 행복도 크게 감소 ({happiness_change:.0f}점)")
                    
            if abs(suffering_change) >= 15:
                if suffering_change > 0:
                    significant_changes.append(f"😰 고통도 크게 증가 (+{suffering_change:.0f}점)")
                else:
                    significant_changes.append(f"😌 고통도 크게 감소 ({suffering_change:.0f}점)")
        
        if significant_changes:
            print(f"\n🔍 주요 변화:")
            for change in significant_changes:
                print(f"  • {change}")
        else:
            print("💰 자금, ⭐ 평판, 😊 행복도, 😰 고통도가 업데이트되었습니다.")
        
        # 다음 턴을 위해 현재 지표들을 이전 지표로 저장
        self.previous_metrics = self.metrics_tracker.get_metrics().copy()
        self.previous_customers = self.daily_customers
        self.previous_revenue = self.daily_revenue
        
    def simulate_daily_business(self):
        """일일 장사 시뮬레이션"""
        metrics = self.metrics_tracker.get_metrics()
        
        # 수요와 재고를 바탕으로 실제 판매량 계산
        demand = metrics.get(Metric.DEMAND, 0)
        inventory = metrics.get(Metric.INVENTORY, 0)
        
        # 기본 손님 수는 수요에 비례 (0-20명)
        base_customers = int(demand * 0.2)
        
        # 랜덤 변동 (±30%)
        variation = random.randint(-30, 30) / 100
        self.daily_customers = max(0, int(base_customers * (1 + variation)))
        
        # 재고 부족 시 손님 수 제한
        self.daily_customers = min(self.daily_customers, int(inventory))
        
        # 경제 엔진을 사용한 정교한 수익 계산
        unit_cost = 8000  # 치킨 1마리당 원가
        fixed_cost = 15000 + (metrics.get(Metric.STAFF_FATIGUE, 0) * 100)  # 기본 운영비 + 피로도 비용
        
        # 기존 매출 계산 (호환성 유지)
        self.daily_revenue = self.daily_customers * self.current_price
        
        # 경제 엔진의 정교한 이익 계산 추가
        daily_profit = compute_profit_no_right_answer(
            units_sold=self.daily_customers,
            unit_cost=unit_cost,
            price=self.current_price,
            fixed_cost=fixed_cost
        )
        
        # 재고 차감
        new_inventory = max(0, inventory - self.daily_customers)
        
        # 운영비 차감 (경제 엔진 결과 반영)
        daily_cost = self.daily_revenue - daily_profit
        
        # 지표 업데이트
        updates = {
            Metric.MONEY: metrics.get(Metric.MONEY, 0) + self.daily_revenue - daily_cost,
            Metric.INVENTORY: new_inventory
        }
        
        # 재고 부족 시 평판 하락
        if new_inventory < 10:
            updates[Metric.REPUTATION] = max(0, metrics.get(Metric.REPUTATION, 0) - 5)
            self.metrics_tracker.add_event("재고 부족으로 인한 기회 손실 발생")
            
        # 매출이 좋으면 행복도 증가
        if self.daily_revenue > 50000:
            updates[Metric.HAPPINESS] = min(100, metrics.get(Metric.HAPPINESS, 0) + 5)
            
        self.metrics_tracker.tradeoff_update_metrics(updates)
        

        
    def print_help(self):
        """도움말 출력"""
        help_text = f"""
{'='*20} 🔧 명령어 도움말 {'='*20}

📋 기본 명령어:
  status, s     - 현재 치킨집 상황을 확인합니다
  actions, a    - 선택 가능한 행동들을 확인합니다
  1, 2, 3, 4, 5, 6 - 해당 번호의 행동을 바로 실행합니다
  action [번호] - 특정 행동을 실행합니다 (예: action 1)
  turn, t       - 다음 턴을 진행합니다 (하루를 보냅니다)
  events, e     - 최근 발생한 이벤트들을 확인합니다
  help, h       - 이 도움말을 표시합니다
  quit, q       - 게임을 종료합니다

🚀 빠른 플레이 방법:
  • 'a' → 행동 확인 → '숫자' → 't' 순서로 빠르게 플레이!
  • 예: a → 2 → t (행동보기 → 재료주문 → 턴진행)
  
🎮 게임 팁:
  • 모든 선택에는 득과 실이 있습니다 (트레이드오프)
  • 완벽한 경영은 불가능합니다 - 균형을 찾으세요
  • 예상치 못한 일들이 벌어질 수 있습니다 (불확실성)
  • 재고 관리가 매우 중요합니다
  • 적절한 가격 책정으로 수익과 손님 수의 균형을 맞추세요
  
🍗 치킨집 경영의 핵심:
  • 자금 관리는 생존의 기본
  • 평판이 높으면 수요가 늘어남
  • 재고가 부족하면 기회 손실
  • 직원 피로도 관리도 중요
  • 시설 상태가 평판에 영향
  
🎯 주요 행동들:
  1. 가격 변경 - 수익과 손님 수의 트레이드오프
  2. 재료 주문 - 재고 확보 vs 자금 소모
  3. 직원 관리 - 서비스 품질 향상
  4. 홍보 활동 - 평판과 수요 증가
  5. 시설 개선 - 장기적 경쟁력 확보
  6. 개인 휴식 - 컨디션 회복 vs 기회비용
  
행운을 빕니다, 사장님! 🎯
{'='*60}
        """
        print(help_text)
        
    def get_game_over_message(self):
        """게임 오버 메시지"""
        metrics = self.metrics_tracker.get_metrics()
        money = metrics.get(Metric.MONEY, 0)
        
        if money <= 0:
            return """
🚨 파산! 🚨
자금이 모두 떨어졌습니다...
하지만 실패는 성공의 어머니! 다시 도전해보세요!
            """
        else:
            return f"""
🏆 게임 종료 🏆
총 {self.turn}턴을 플레이하셨습니다.
최종 자산: {money:,.0f}원
최종 평판: {metrics.get(Metric.REPUTATION, 0):.0f}점

치킨집 경영, 수고하셨습니다! 🍗
            """
            
    def run(self):
        """메인 게임 루프"""
        self.clear_screen()
        self.print_banner()
        print("\n게임을 시작합니다! 'help' 명령어로 도움말을 확인하세요.")
        print("💡 TIP: 'actions' 명령어로 가능한 행동들을 확인하고 전략을 세워보세요!")
        self.print_status()
        
        while self.running:
            try:
                # 단축 명령어 안내 출력
                print(f"\n📋 단축키: [s]상태 [a]행동 [1-6]행동실행 [t]턴진행 [e]이벤트 [h]도움말 [q]종료")
                command = input(f"[턴 {self.turn}] 치킨마스터> ").strip().lower()
                
                if command in ['quit', 'q', 'exit']:
                    self.running = False
                    print("\n게임을 종료합니다...")
                    
                elif command in ['status', 's']:
                    self.print_status()
                    
                elif command in ['actions', 'a']:
                    self.print_actions()
                    
                elif command.startswith('action '):
                    try:
                        action_num = int(command.split()[1])
                        self.execute_action(action_num)
                    except (IndexError, ValueError):
                        print("❓ 사용법: action [번호] (예: action 1)")
                
                # 숫자만 입력해도 행동 실행되도록 추가
                elif command.isdigit():
                    action_num = int(command)
                    if 1 <= action_num <= 6:
                        self.execute_action(action_num)
                    else:
                        print("❓ 1-6 사이의 번호를 입력하세요.")
                    
                elif command in ['turn', 't', 'next']:
                    self.process_turn()
                    
                    # 파산 체크
                    current_money = self.metrics_tracker.get_metrics().get(Metric.MONEY, 0)
                    if current_money <= -50000:  # -5만원까지는 버틸 수 있음
                        print(self.get_game_over_message())
                        self.running = False
                        
                elif command in ['events', 'e', 'news']:
                    self.print_events()
                    
                elif command in ['help', 'h', '?']:
                    self.print_help()
                    
                elif command == '':
                    continue  # 빈 입력 무시
                    
                else:
                    print(f"❓ 알 수 없는 명령어: '{command}'")
                    print("💡 단축키를 참고하거나 'help' 명령어를 사용하세요.")
                    
            except KeyboardInterrupt:
                print("\n\n게임을 강제 종료합니다...")
                self.running = False
                
            except Exception as e:
                print(f"❌ 오류가 발생했습니다: {e}")
                print("게임을 계속 진행합니다...")
                
        print(self.get_game_over_message())


def main():
    """메인 함수"""
    try:
        game = ChickenMudGame()
        game.run()
    except Exception as e:
        print(f"게임 시작 중 오류 발생: {e}")
        print("필요한 파일들이 있는지 확인해주세요.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🔍 CHICKEN MASTER DEBUG MUD 🔍
실시간 백엔드 트레이싱 디버그 게임

사용자 명령어가 백엔드에서 어떻게 처리되는지 실시간으로 추적하고 표시합니다.
헥사고널 아키텍처의 모든 레이어를 시각화합니다.
"""

import sys
import time
from typing import Dict, Any, List, Optional

# 트레이싱 시스템 임포트
from debug_tracing_system import (
    traceable, trace_command, capture_state, toggle_tracing, 
    get_trace_collector, DebugFormatter, TraceLevel, set_trace_level
)

# 기존 백엔드 임포트
from src.core.domain.game_state import GameState, GameSettings
from src.core.domain.metrics import MetricsSnapshot, Metric
from src.core.domain.action_slots import (
    create_daily_action_plan, DailyActionPlan, ActionSlotConfiguration, 
    ActionType as SlotActionType, ACTION_EFFECTS
)
# 🎯 **아키텍처 보존**: 새로운 Application Service만 추가
from src.application.game_philosophy_service import (
    GamePhilosophyApplicationService, GamePhilosophyLevel
)
from game_constants import Metric as GameMetric, METRIC_RANGES
import random


class DebugGameSimulator:
    """디버그 기능이 추가된 게임 시뮬레이터"""
    
    def __init__(self):
        """실제 백엔드 구조에 맞게 초기화"""
        # GameSettings를 사용한 초기화 (기존 MUD와 동일)
        self.settings = GameSettings(
            starting_money=int(METRIC_RANGES[GameMetric.MONEY][2]),      # 10000
            starting_reputation=int(METRIC_RANGES[GameMetric.REPUTATION][2]),  # 50
            starting_happiness=int(METRIC_RANGES[GameMetric.HAPPINESS][2]),    # 50
            starting_pain=int(METRIC_RANGES[GameMetric.SUFFERING][2]),         # 20
            max_cascade_depth=5,
            bankruptcy_threshold=0
        )
        
        # 확장 지표를 위한 MetricsSnapshot 생성
        self.initial_metrics = {
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
        
        self.chicken_price = 10000  # 치킨 가격
        
    @traceable(level=TraceLevel.INFO)
    def create_initial_state(self) -> tuple[GameState, MetricsSnapshot]:
        """초기 게임 상태 생성"""
        game_state = self.settings.create_initial_state()
        metrics_snapshot = MetricsSnapshot(
            metrics=self.initial_metrics.copy(),
            timestamp=1
        )
        return game_state, metrics_snapshot
        
    @traceable(level=TraceLevel.INFO) 
    def simulate_turn(self, game_state: GameState, metrics_snapshot: MetricsSnapshot) -> tuple[GameState, MetricsSnapshot]:
        """턴 시뮬레이션"""
        # 일일 비즈니스 시뮬레이션
        demand = metrics_snapshot.get_metric_value("demand")
        inventory = metrics_snapshot.get_metric_value("inventory")
        
        # 실제 판매량 계산
        customers = min(demand + random.randint(-10, 10), inventory)
        customers = max(0, customers)
        
        revenue = customers * self.chicken_price
        
        if customers > 0:
            # 매출 추가, 재고 차감
            game_state = game_state.apply_effects({"money": revenue})
            metrics_snapshot = metrics_snapshot.apply_effects({"inventory": -customers})
        
        # 턴 수 증가
        game_state = game_state.apply_effects({"day": 1})
        
        # 타임스탬프 업데이트
        metrics_snapshot = MetricsSnapshot(
            metrics=metrics_snapshot.metrics,
            timestamp=game_state.day
        )
        
        return game_state, metrics_snapshot


class DebugUI:
    """디버그 출력 UI 관리자"""
    
    def __init__(self):
        self.show_trace = True
        self.show_state_diff = True
        self.max_trace_lines = 15
        
    def print_separator(self, title: str = "", char: str = "=", width: int = 80):
        """구분선 출력"""
        if title:
            padding = (width - len(title) - 2) // 2
            line = char * padding + f" {title} " + char * padding
            if len(line) < width:
                line += char
        else:
            line = char * width
        print(line)
    
    def print_command_header(self, command: str):
        """명령어 헤더 출력"""
        print("\n" + "🔍" * 40)
        print(f"📥 USER INPUT: {command}")
        print("🔍" * 40)
    
    def print_trace_section(self, traces):
        """트레이스 섹션 출력"""
        if not self.show_trace or not traces:
            return
            
        print("\n" + "⚡" * 20 + " EXECUTION TRACE " + "⚡" * 20)
        
        for i, trace in enumerate(traces[-self.max_trace_lines:], 1):
            formatted = DebugFormatter.format_trace_entry(trace)
            print(f"{i:2d}. {formatted}")
            
        if len(traces) > self.max_trace_lines:
            print(f"    ... and {len(traces) - self.max_trace_lines} more trace entries")
    
    def print_state_section(self, state_before: Dict[str, Any], state_after: Dict[str, Any]):
        """상태 변화 섹션 출력"""
        if not self.show_state_diff:
            return
            
        print("\n" + "📊" * 20 + " STATE CHANGES " + "📊" * 20)
        
        collector = get_trace_collector()
        diff = collector.get_state_diff()
        
        if diff and any(diff[key] for key in ["added", "removed", "changed"]):
            diff_lines = DebugFormatter.format_state_diff(diff)
            for line in diff_lines:
                print(line)
        else:
            print("📝 상태 변화 없음")
    
    def print_result_section(self, result_message: str):
        """결과 메시지 섹션 출력"""
        print("\n" + "💬" * 20 + " GAME RESPONSE " + "💬" * 20)
        print(result_message)
        
    def print_debug_commands(self):
        """디버그 명령어 도움말 출력"""
        print("\n" + "🛠️" * 20 + " DEBUG COMMANDS " + "🛠️" * 20)
        print("🔧 디버그 명령어:")
        print("  trace on (on)   - 트레이싱 상태 확인 (항상 활성화됨)")
        print("  trace off (off) - 비활성화 시도 (디버그 모드에서는 불가)")
        print("  trace level [debug|info|warning|error] - 트레이스 레벨 설정")
        print("  show state (x)  - 현재 상태만 표시")
        print("  show traces (z) - 최근 트레이스만 표시")
        print("  clear traces (c)- 트레이스 기록 초기화")
        print("  debug help (d)  - 이 도움말 표시")
        print("\n⚡ **1글자 단축키**: 괄호 안의 글자만 입력하면 번개같은 속도!")
        print("💡 TIP: 디버그 MUD에서는 모든 명령어가 자동으로 트레이싱됩니다!")


class ChickenDebugMUD:
    """실시간 디버깅이 가능한 치킨 마스터 MUD"""
    
    def __init__(self):
        print("🔍 디버그 모드로 헥사고널 아키텍처 백엔드를 초기화합니다...")
        
        # 디버그 시뮬레이터 및 UI 초기화
        self.simulator = DebugGameSimulator()
        self.debug_ui = DebugUI()
        
        # 초기 게임 상태 생성
        self.game_state, self.metrics_snapshot = self.simulator.create_initial_state()
        
        # 🎯 **PHASE 1 수정**: 게임 상태 리셋 (1,300,000원 → 10,000원, 104일 → 1일)
        print("🔄 게임 철학 구현: 긴장감 있는 초기 상태로 리셋...")
        self.game_state = GameState(
            money=10000,       # 현실적인 시작 자금
            reputation=50,
            happiness=50,
            pain=20,
            day=1,            # 1일차부터 시작
            events_history=()  # 빈 이벤트 히스토리
        )
        
        # 🔥 치킨 가격 초기화 (ChickenMudGame과 동일하게)
        self.chicken_price = 10000
        
        # 🎲 **PHASE 1 핵심**: Daily Action Slots 시스템 통합
        self.action_slots_config = ActionSlotConfiguration()
        self.daily_plan = create_daily_action_plan(day=1, config=self.action_slots_config)
        
        # 🎯 **게임 철학 서비스**: 아키텍처 보존하며 철학만 추가
        self.philosophy_service = GamePhilosophyApplicationService(
            philosophy_level=GamePhilosophyLevel.NORMAL
        )
        
        # 트레이싱 항상 활성화 (디버그 모드에서는 비활성화 불가)
        self.tracing_enabled = True
        self.force_tracing = True  # 강제 트레이싱 모드
        
        print("✅ 디버그 MUD 초기화 완료!")
        print("🎯 실시간 백엔드 트레이싱 항상 활성화됨 (비활성화 불가)")
        print(f"🎲 Daily Action Slots 시스템 활성화: 하루 {self.daily_plan.max_actions}개 행동 제한!")
        print(f"💰 시작 자금: {self.game_state.money:,}원 (긴장감 있는 게임 시작!)")
        
    @traceable(level=TraceLevel.INFO)
    def process_command(self, user_input: str) -> str:
        """사용자 명령어 처리 (트레이싱 적용)"""
        command = user_input.strip().lower()
        
        # 🔥 1글자 단축키 매핑 (번개같은 속도!)
        SHORTCUTS = {
            's': 'status',
            't': 'turn', 
            'h': 'help',
            'q': 'quit',
            'e': 'events',
            'a': 'actions',
            
            # 액션 단축키 (즉시 실행)
            'a1': 'action 1',  # 가격 변경
            'a2': 'action 2',  # 재료 주문
            'a3': 'action 3',  # 직원 관리
            'a4': 'action 4',  # 홍보 활동
            'a5': 'action 5',  # 시설 업그레이드
            'a6': 'action 6',  # 개인 휴식
            'a7': 'action 7',  # 연구개발 (R&D)
        }
        
        # 단축키 변환 (폭발적인 속도 향상! 💥)
        if command in SHORTCUTS:
            original_command = command
            command = SHORTCUTS[command]
            print(f"⚡ 단축키 변환: '{original_command}' → '{command}'")
        
        # 디버그 명령어 처리
        if command.startswith("trace"):
            return self._handle_trace_command(command)
        elif command == "show state":
            return self._handle_show_state()
        elif command == "show traces":
            return self._handle_show_traces()
        elif command == "clear traces":
            return self._handle_clear_traces()
        elif command == "debug help":
            self.debug_ui.print_debug_commands()
            return "디버그 명령어 도움말을 표시했습니다."
        
        # 기존 게임 명령어 처리
        return self._handle_game_command(command)
    
    def _handle_trace_command(self, command: str) -> str:
        """트레이스 관련 명령어 처리"""
        parts = command.split()
        
        if len(parts) >= 2:
            if parts[1] == "on":
                # 항상 켜져있으므로 상태만 확인
                if not get_trace_collector().enabled:
                    toggle_tracing()
                self.tracing_enabled = True
                return "✅ 트레이싱이 이미 활성화되어 있습니다. (디버그 모드에서는 항상 활성화)"
            elif parts[1] == "off":
                # 디버그 모드에서는 트레이싱을 끌 수 없음
                if self.force_tracing:
                    return "⚠️ 디버그 MUD에서는 트레이싱을 비활성화할 수 없습니다! 🔍 실시간 추적이 핵심 기능입니다."
                # 일반 모드라면 끄기 허용 (실제로는 사용되지 않음)
                if get_trace_collector().enabled:
                    toggle_tracing()
                self.tracing_enabled = False
                return "❌ 트레이싱이 비활성화되었습니다."
            elif parts[1] == "level" and len(parts) >= 3:
                level_map = {
                    "debug": TraceLevel.DEBUG,
                    "info": TraceLevel.INFO, 
                    "warning": TraceLevel.WARNING,
                    "error": TraceLevel.ERROR
                }
                if parts[2] in level_map:
                    set_trace_level(level_map[parts[2]])
                    return f"📊 트레이스 레벨이 {parts[2].upper()}로 설정되었습니다."
                else:
                    return "❌ 올바르지 않은 트레이스 레벨입니다. (debug|info|warning|error)"
        
        return "❌ 올바르지 않은 trace 명령어입니다. 'debug help' 참조"
    
    def _handle_show_state(self) -> str:
        """현재 상태 표시"""
        print("\n" + "🎯" * 20 + " CURRENT STATE " + "🎯" * 20)
        print("🏪 GameState:")
        print(f"  💰 money: {self.game_state.money}")
        print(f"  ⭐ reputation: {self.game_state.reputation}")
        print(f"  😊 happiness: {self.game_state.happiness}")  
        print(f"  😰 pain: {self.game_state.pain}")
        print(f"  📅 day: {self.game_state.day}")
        
        print("\n📊 MetricsSnapshot:")
        print(f"  📦 inventory: {self.metrics_snapshot.get_metric_value('inventory')}")
        print(f"  😴 staff_fatigue: {self.metrics_snapshot.get_metric_value('staff_fatigue')}")
        print(f"  🏭 facility: {self.metrics_snapshot.get_metric_value('facility')}")
        print(f"  📈 demand: {self.metrics_snapshot.get_metric_value('demand')}")
        
        return "현재 상태를 표시했습니다."
    
    def _handle_show_traces(self) -> str:
        """최근 트레이스 표시"""
        collector = get_trace_collector()
        traces = collector.get_latest_traces(20)
        
        if traces:
            self.debug_ui.print_trace_section(traces)
        else:
            print("📝 트레이스 기록이 없습니다.")
            
        return "최근 트레이스를 표시했습니다."
    
    def _handle_clear_traces(self) -> str:
        """트레이스 기록 초기화"""
        collector = get_trace_collector()
        collector.clear()
        return "🗑️ 트레이스 기록이 초기화되었습니다."
    
    @traceable(level=TraceLevel.INFO)
    def _handle_game_command(self, command: str) -> str:
        """기존 게임 명령어 처리"""
        if command == "help":
            return self._show_help()
        elif command == "status":
            return self._show_status()
        elif command == "actions":
            return self._show_actions()
        elif command.startswith("action"):
            return self._handle_action(command)
        elif command == "turn":
            return self._handle_turn()
        elif command == "events":
            return self._show_events()
        elif command == "quit":
            return "quit"
        else:
            return f"❌ 알 수 없는 명령어: {command}. 'help' 또는 'debug help' 참조"
    
    @traceable(level=TraceLevel.INFO)
    def _handle_turn(self) -> str:
        """턴 진행 처리"""
        # 상태 캡처 (Before)
        capture_state(self.game_state, "Turn Start")
        capture_state(self.metrics_snapshot, "Metrics Start")
        
        # 시뮬레이터로 턴 진행
        try:
            old_day = self.game_state.day
            self.game_state, self.metrics_snapshot = self.simulator.simulate_turn(
                self.game_state, self.metrics_snapshot
            )
            
            # 🎲 **PHASE 1 핵심**: 새로운 날을 위해 Daily Action Plan 리셋
            self.daily_plan = self.daily_plan.advance_to_next_day()
            
            # 상태 캡처 (After)
            capture_state(self.game_state, "Turn End")
            capture_state(self.metrics_snapshot, "Metrics End")
            
            remaining_actions = self.daily_plan.get_remaining_actions()
            return f"✅ 턴 {old_day} → {self.game_state.day} 진행 완료! (오늘 {remaining_actions}개 행동 가능)"
            
        except Exception as e:
            return f"❌ 턴 진행 중 오류: {e}"
    
    def _show_help(self) -> str:
        """도움말 표시"""
        help_text = """
🎮 게임 명령어:
- s (status): 현재 상태 확인
- a (actions): 선택 가능한 행동 보기  
- t (turn): 다음 턴 진행
- e (events): 최근 이벤트 확인
- h (help): 이 도움말 보기
- q (quit): 게임 종료

⚡ 액션 단축키 (즉시 실행):
- a1: 💰 가격 변경
- a2: 📦 재료 주문  
- a3: 👥 직원 관리
- a4: 📢 홍보 활동
- a5: 🏭 시설 업그레이드
- a6: 😴 개인 휴식
- a7: 🧪 연구개발 (R&D)

🔧 백엔드 테스트 정보:
- GameState: money, reputation, happiness, pain, day 필드 사용
- MetricsSnapshot: inventory, staff_fatigue, facility, demand 지표 관리
- 모든 효과는 실제 apply_effects() 메서드 사용
- 이벤트 히스토리는 실제 add_event_to_history() 사용
- 실시간 백엔드 아키텍처 트레이싱 활성화!

🛡️ 중요 발견:
- 백엔드에 자금 음수 방지 로직 존재! (파산 보호)
- GameState.apply_effects()에서 max(0, money + delta) 적용

💡 팁: 이 MUD는 실제 헥사고널 아키텍처 백엔드의 테스트 도구입니다!
        """
        return help_text.strip()
    
    def _show_status(self) -> str:
        """현재 상태 표시"""
        # 이미 self.metrics_snapshot을 가지고 있으므로 직접 사용
        
        status = f"""
==================== 🏪 치킨집 현황 (턴 {self.game_state.day}) ====================
💰 자금: {self.game_state.money:,}원
⭐ 평판: {self.game_state.reputation}점
😊 행복도: {self.game_state.happiness}점
😰 고통도: {self.game_state.pain}점
📦 재고: {self.metrics_snapshot.get_metric_value('inventory'):.0f}개
😴 직원피로도: {self.metrics_snapshot.get_metric_value('staff_fatigue'):.0f}점
🏭 시설상태: {self.metrics_snapshot.get_metric_value('facility'):.0f}점
📈 수요: {self.metrics_snapshot.get_metric_value('demand'):.0f}점
"""
        return status.strip()
    
    def _show_actions(self) -> str:
        """행동 목록 표시 - 실제 자금 상황 반영"""
        money = self.game_state.money
        
        actions_text = f"""
==================== 🎯 선택 가능한 행동 ====================
1. 💰 치킨 가격 변경 (현재: {self.chicken_price:,}원)
   ↗️ 가격 인상: 수익 증가, 손님 감소

2. 📦 재료 주문"""
        
        if money >= 50000:
            actions_text += "\n   50,000원으로 재료 50개 주문 가능"
        else:
            actions_text += "\n   ❌ 자금 부족 (50,000원 필요)"
            
        actions_text += f"\n\n3. 👥 직원 관리"
        if money >= 30000:
            actions_text += "\n   30,000원으로 직원 휴식 제공"
        else:
            actions_text += "\n   ❌ 자금 부족 (30,000원 필요)"
        
        actions_text += f"\n\n4. 📢 홍보 활동"
        if money >= 20000:
            actions_text += "\n   20,000원으로 광고 진행"
        else:
            actions_text += "\n   ❌ 자금 부족 (20,000원 필요)"
            
        actions_text += f"\n\n5. 🏭 시설 개선"
        if money >= 100000:
            actions_text += "\n   100,000원으로 시설 업그레이드"
        else:
            actions_text += "\n   ❌ 자금 부족 (100,000원 필요)"
            
        actions_text += f"\n\n6. 😴 개인 휴식"
        actions_text += "\n   하루 쉬면서 컨디션 회복"
        
        actions_text += f"\n\n'action [번호]' 또는 'a' + [번호]로 행동을 선택하세요!"
        actions_text += f"\n예: action 1, action 2, a1, a2"
        
        return actions_text.strip()
    
    @traceable(level=TraceLevel.INFO)
    def _handle_action(self, command: str) -> str:
        """행동 실행 - 게임 철학 적용 (아키텍처 보존)"""
        try:
            # "action 1" 형식에서 번호 추출
            parts = command.split()
            if len(parts) < 2:
                return "❌ 올바른 형식: action [번호] (예: action 1)"
            
            action_num = int(parts[1])
            
            # 🎯 **게임 철학 적용**: 액션 제한 체크
            constraint = self.philosophy_service.evaluate_action_constraints(
                self.daily_plan, self.game_state
            )
            
            if not constraint.can_perform_action:
                return constraint.constraint_message
            
            # 상태 캡처 (Before Action)
            capture_state(self.game_state, f"Before Action {action_num}")
            capture_state(self.metrics_snapshot, f"Before Action {action_num} Metrics")
            
            # 🎲 **게임 철학 적용**: 확률적 결과로 행동 실행
            result = self._execute_action_with_philosophy(action_num)
            
            # 🎯 **게임 철학 적용**: 액션 슬롯 소모
            try:
                # 액션 타입 매핑
                action_type_map = {
                    1: SlotActionType.CLEANING,  # 가격 변경을 청소로 매핑 (임시)
                    2: SlotActionType.INVENTORY,
                    3: SlotActionType.STAFF_REST,
                    4: SlotActionType.PROMOTION,
                    5: SlotActionType.FACILITY,
                    6: SlotActionType.PERSONAL_REST,
                    7: SlotActionType.RESEARCH
                }
                
                if action_num in action_type_map:
                    self.daily_plan = self.daily_plan.use_action_slot(action_type_map[action_num])
                    remaining = self.daily_plan.get_remaining_actions()
                    result += f"\n🎲 행동 슬롯 사용됨. 오늘 {remaining}개 행동 남음."
            except Exception as e:
                result += f"\n⚠️ 액션 슬롯 처리 중 오류: {e}"
            
            # 상태 캡처 (After Action)
            capture_state(self.game_state, f"After Action {action_num}")
            capture_state(self.metrics_snapshot, f"After Action {action_num} Metrics")
            
            return result
            
        except (ValueError, IndexError):
            return "❌ 올바른 형식: action [번호] (예: action 1)"
        except Exception as e:
            return f"❌ 행동 실행 중 오류: {e}"
    
    @traceable(level=TraceLevel.INFO)
    def _execute_action_with_philosophy(self, action_num: int) -> str:
        """
        게임 철학이 적용된 행동 실행
        
        기존 _execute_action을 보존하고 새로운 철학 적용 메서드 추가
        """
        # 액션 타입 매핑
        action_type_map = {
            1: "price_change",
            2: "order_inventory", 
            3: "staff_management",
            4: "promotion",
            5: "facility_upgrade",
            6: "personal_rest",
            7: "research_development"
        }
        
        if action_num not in action_type_map:
            return "❌ 올바르지 않은 행동 번호입니다. (1-7)"
        
        action_type = action_type_map[action_num]
        
        # 🎲 **확률적 결과 계산**
        outcome = self.philosophy_service.calculate_probabilistic_outcome(
            action_type=action_type,
            game_state=self.game_state,
            metrics_snapshot=self.metrics_snapshot,
            action_context=self._get_action_context(action_num)
        )
        
        # 🎯 **효과 적용** (기존 도메인 모델 사용)
        if outcome.effects:
            try:
                # GameState 효과 적용
                state_effects = {
                    k: v for k, v in outcome.effects.items() 
                    if k in ["money", "reputation", "happiness", "pain"]
                }
                if state_effects:
                    self.game_state = self.game_state.apply_effects(state_effects)
                
                # MetricsSnapshot 효과 적용
                metrics_effects = {
                    k: v for k, v in outcome.effects.items()
                    if k in ["inventory", "staff_fatigue", "facility", "demand"]
                }
                if metrics_effects:
                    self.metrics_snapshot = self.metrics_snapshot.apply_effects(metrics_effects)
                
            except Exception as e:
                return f"❌ 효과 적용 중 오류: {e}"
        
        # 🎭 **결과 메시지 생성**
        result_message = f"{outcome.message}\n{outcome.flavor_text}"
        
        # 효과 상세 정보 추가
        if outcome.effects:
            result_message += "\n\n📊 효과:"
            for effect_name, effect_value in outcome.effects.items():
                if effect_value != 0:
                    sign = "+" if effect_value > 0 else ""
                    result_message += f"\n  {effect_name}: {sign}{effect_value:.0f}"
        
        # 🎯 **긴장감 및 인사이트 추가**
        tension = self.philosophy_service.assess_tension_level(
            self.game_state, self.metrics_snapshot
        )
        
        if tension.emotional_intensity > 0.7:
            result_message += f"\n\n💢 긴장감: {tension.emotional_intensity:.1f} (매우 높음)"
        elif tension.emotional_intensity > 0.4:
            result_message += f"\n\n😤 긴장감: {tension.emotional_intensity:.1f} (보통)"
        
        # 🏁 **엔딩 조건 체크**
        ending = self.philosophy_service.check_ending_conditions(
            self.game_state, self.metrics_snapshot
        )
        
        if ending:
            result_message += f"\n\n🏁 {ending['title']}: {ending['message']}"
            result_message += f"\n{ending['flavor']}"
            if ending.get('is_game_over'):
                result_message += "\n\n🎮 게임 종료! 'quit'으로 나가거나 새 게임을 시작하세요."
        
        return result_message

    def _get_action_context(self, action_num: int) -> Dict[str, Any]:
        """액션별 컨텍스트 정보 제공"""
        contexts = {
            1: {"current_price": self.chicken_price},
            2: {"cost": 50000, "inventory_amount": 50},
            3: {"cost": 30000},
            4: {"cost": 20000},
            5: {"cost": 100000},
            6: {"rest_benefit": 20},
            7: {"research_cost": 80000}
        }
        return contexts.get(action_num, {})

    @traceable(level=TraceLevel.INFO)
    def _execute_action(self, action_num: int) -> str:
        """
        선택된 행동을 실행 - 기존 시스템 (보존용)
        
        아키텍처 보존을 위해 기존 메서드 그대로 유지
        """
        if action_num == 1:
            return self._action_price_change()
        elif action_num == 2:
            return self._action_order_inventory()
        elif action_num == 3:
            return self._action_staff_management()
        elif action_num == 4:
            return self._action_promotion()
        elif action_num == 5:
            return self._action_facility_upgrade()
        elif action_num == 6:
            return self._action_personal_rest()
        elif action_num == 7:
            return self._action_research_development()
        else:
            return "❓ 잘못된 행동 번호입니다. (1-7 사용 가능)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_price_change(self) -> str:
        """가격 변경 행동 - 자동으로 가격 인상 (디버그 모드)"""
        old_price = self.chicken_price
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
        
        return f"💰 가격을 {old_price:,}원 → {self.chicken_price:,}원으로 인상! (평판-2, 수요-5)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_order_inventory(self) -> str:
        """재료 주문 행동 - 실제 도메인 모델 사용"""
        if self.game_state.money < 50000:
            return f"❌ 자금이 부족합니다. (50,000원 필요, 현재 {self.game_state.money:,}원)"
        
        # 실제 GameState.apply_effects 사용
        self.game_state = self.game_state.apply_effects({"money": -50000})
        
        # MetricsSnapshot.apply_effects 사용
        self.metrics_snapshot = self.metrics_snapshot.apply_effects({"inventory": 50})
        
        # 이벤트 히스토리 추가
        self.game_state = self.game_state.add_event_to_history("치킨 재료 50개분 주문")
        
        return "✅ 재료 주문 완료! (-50,000원, +50개 재고)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_staff_management(self) -> str:
        """직원 관리 행동"""
        if self.game_state.money < 30000:
            return f"❌ 자금이 부족합니다. (30,000원 필요, 현재 {self.game_state.money:,}원)"
        
        # 실제 도메인 모델 사용
        self.game_state = self.game_state.apply_effects({
            "money": -30000,
            "happiness": 10
        })
        
        self.metrics_snapshot = self.metrics_snapshot.apply_effects({
            "staff_fatigue": -20
        })
        
        self.game_state = self.game_state.add_event_to_history("직원들에게 휴식 제공")
        return "✅ 직원 관리 완료! (-30,000원, +10 행복도, -20 직원피로도)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_promotion(self) -> str:
        """홍보 활동 행동"""
        if self.game_state.money < 20000:
            return f"❌ 자금이 부족합니다. (20,000원 필요, 현재 {self.game_state.money:,}원)"
        
        self.game_state = self.game_state.apply_effects({
            "money": -20000,
            "reputation": 15
        })
        
        self.metrics_snapshot = self.metrics_snapshot.apply_effects({
            "demand": 10
        })
        
        self.game_state = self.game_state.add_event_to_history("홍보 활동 진행")
        return "✅ 홍보 활동 완료! (-20,000원, +15 평판, +10 수요)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_facility_upgrade(self) -> str:
        """시설 개선 행동"""
        if self.game_state.money < 100000:
            return f"❌ 자금이 부족합니다. (100,000원 필요, 현재 {self.game_state.money:,}원)"
        
        self.game_state = self.game_state.apply_effects({
            "money": -100000,
            "reputation": 10
        })
        
        self.metrics_snapshot = self.metrics_snapshot.apply_effects({
            "facility": 20
        })
        
        self.game_state = self.game_state.add_event_to_history("시설 업그레이드 완료")
        return "✅ 시설 개선 완료! (-100,000원, +10 평판, +20 시설상태)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_personal_rest(self) -> str:
        """개인 휴식 행동"""
        self.game_state = self.game_state.apply_effects({
            "happiness": 20,
            "pain": -15,
            "money": -10000  # 기회비용
        })
        
        self.game_state = self.game_state.add_event_to_history("개인 휴식으로 컨디션 회복")
        return "✅ 개인 휴식 완료! (-10,000원 기회비용, +20 행복도, -15 고통도)"
    
    @traceable(level=TraceLevel.INFO)
    def _action_research_development(self) -> str:
        """연구개발 행동"""
        if self.game_state.money < 80000:
            return f"❌ 자금이 부족합니다. (80,000원 필요, 현재 {self.game_state.money:,}원)"
        
        self.game_state = self.game_state.apply_effects({
            "money": -80000,
            "reputation": 25,
            "happiness": 15
        })
        
        self.metrics_snapshot = self.metrics_snapshot.apply_effects({
            "demand": 30
        })
        
        self.game_state = self.game_state.add_event_to_history("R&D 성공: 신메뉴 개발로 대박!")
        return "✅ 연구개발 성공! (-80,000원, +25 평판, +30 수요, +15 행복도)"
        
    def _show_events(self) -> str:
        """이벤트 표시"""
        if self.game_state.events_history:
            events = "\n".join([f"  {i+1}. {event}" for i, event in enumerate(self.game_state.events_history[-5:])])
            return f"📰 최근 이벤트:\n{events}"
        else:
            return "📰 아직 특별한 소식이 없습니다."
    
    def run(self):
        """메인 게임 루프"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🔍 CHICKEN MASTER DEBUG MUD 🔍                        ║
║                     실시간 백엔드 트레이싱 디버그 게임                      ║
║                                                                              ║
║                   "백엔드의 모든 동작을 실시간으로 확인!"                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 실시간 백엔드 트레이싱 디버그 모드 활성화!
💡 TIP: 'debug help'로 디버그 명령어를, 'help'로 게임 명령어를 확인하세요!
""")

        # 초기 상태 표시
        print(self._show_status())
        
        while True:
            try:
                print("\n" + "=" * 80)
                user_input = input("🎮 명령어를 입력하세요: ").strip()
                
                if not user_input:
                    continue
                
                # 명령어 헤더 출력
                self.debug_ui.print_command_header(user_input)
                
                # 트레이싱 컨텍스트에서 명령어 처리
                with trace_command(user_input) as collector:
                    # 상태 캡처 (Before)
                    capture_state(self.game_state, "Before Command")
                    
                    result = self.process_command(user_input)
                    
                    # 상태 캡처 (After)  
                    capture_state(self.game_state, "After Command")
                
                # 디버그 정보 출력 (디버그 MUD에서는 항상 활성화)
                if collector.enabled:
                    traces = collector.get_latest_traces()
                    if traces:
                        self.debug_ui.print_trace_section(traces)
                    
                    # 상태 변화 표시
                    if len(collector.state_snapshots) >= 2:
                        before_state = collector.state_snapshots[-2].data
                        after_state = collector.state_snapshots[-1].data
                        self.debug_ui.print_state_section(before_state, after_state)
                
                # 결과 메시지 출력
                self.debug_ui.print_result_section(result)
                
                # 게임 종료 체크
                if result == "quit":
                    print("\n👋 디버그 MUD를 종료합니다!")
                    break
                    
                # 게임 상태 업데이트된 경우 표시
                if user_input.strip().lower() in ["turn", "status"]:
                    print(self._show_status())
                    
            except KeyboardInterrupt:
                print("\n\n👋 디버그 MUD를 종료합니다!")
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}")


def main():
    """메인 함수"""
    try:
        mud = ChickenDebugMUD()
        mud.run()
    except Exception as e:
        print(f"❌ 디버그 MUD 초기화 실패: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
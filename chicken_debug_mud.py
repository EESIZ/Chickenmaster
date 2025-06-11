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
        print("  trace on        - 트레이싱 상태 확인 (항상 활성화됨)")
        print("  trace off       - 비활성화 시도 (디버그 모드에서는 불가)")
        print("  trace level [debug|info|warning|error] - 트레이스 레벨 설정")
        print("  show state      - 현재 상태만 표시")
        print("  show traces     - 최근 트레이스만 표시")
        print("  clear traces    - 트레이스 기록 초기화")
        print("  debug help      - 이 도움말 표시")
        print("\n💡 TIP: 디버그 MUD에서는 모든 명령어가 자동으로 트레이싱됩니다!")


class ChickenDebugMUD:
    """실시간 디버깅이 가능한 치킨 마스터 MUD"""
    
    def __init__(self):
        print("🔍 디버그 모드로 헥사고널 아키텍처 백엔드를 초기화합니다...")
        
        # 디버그 시뮬레이터 및 UI 초기화
        self.simulator = DebugGameSimulator()
        self.debug_ui = DebugUI()
        
        # 초기 게임 상태 생성
        self.game_state, self.metrics_snapshot = self.simulator.create_initial_state()
        
        # 트레이싱 항상 활성화 (디버그 모드에서는 비활성화 불가)
        self.tracing_enabled = True
        self.force_tracing = True  # 강제 트레이싱 모드
        
        print("✅ 디버그 MUD 초기화 완료!")
        print("🎯 실시간 백엔드 트레이싱 항상 활성화됨 (비활성화 불가)")
        
    @traceable(level=TraceLevel.INFO)
    def process_command(self, user_input: str) -> str:
        """사용자 명령어 처리 (트레이싱 적용)"""
        command = user_input.strip().lower()
        
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
            
            # 상태 캡처 (After)
            capture_state(self.game_state, "Turn End")
            capture_state(self.metrics_snapshot, "Metrics End")
            
            return f"✅ 턴 {old_day} → {self.game_state.day} 진행 완료!"
            
        except Exception as e:
            return f"❌ 턴 진행 중 오류: {e}"
    
    def _show_help(self) -> str:
        """도움말 표시"""
        help_text = """
🎮 게임 명령어:
- status: 현재 상태 확인
- actions: 선택 가능한 행동 보기  
- action [번호]: 특정 행동 실행
- turn: 다음 턴 진행
- events: 최근 이벤트 확인
- help: 이 도움말 보기
- quit: 게임 종료

🔍 디버그 명령어:
- trace on: 트레이싱 상태 확인 (항상 활성화됨)
- show state: 현재 상태 표시
- debug help: 디버그 명령어 도움말

🚀 디버그 MUD 특징: 모든 명령어는 자동으로 실시간 트레이싱됩니다!
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
        """행동 목록 표시"""
        return """
==================== 🎯 선택 가능한 행동 ====================
1. 💰 치킨 가격 변경
2. 📦 재료 주문  
3. 👥 직원 관리
4. 📢 홍보 활동
5. 🏭 시설 개선
6. 😴 개인 휴식

'action [번호]'로 행동을 선택하세요 (예: action 1)
""".strip()
    
    def _handle_action(self, command: str) -> str:
        """행동 실행"""
        return "💡 행동 시스템은 추후 구현됩니다. 현재는 'turn' 명령어를 사용하세요."
    
    def _show_events(self) -> str:
        """이벤트 표시"""
        return "📰 이벤트 시스템은 턴 진행 시 자동으로 처리됩니다."
    
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
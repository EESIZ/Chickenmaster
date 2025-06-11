"""
Daily Action Slots 시스템 도메인 모델
하루에 제한된 행동만 할 수 있는 전략적 선택 시스템

@freeze v0.1.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ActionType(Enum):
    """행동 유형"""
    CLEANING = "청소"           # 위생↑ 단속↓, 돈- 피로+
    PROMOTION = "홍보"         # 손님·평판↑, 돈- 재고압박  
    RESEARCH = "연구"          # 연구 Pt +, 당일 매출 0
    INVENTORY = "재료주문"     # 재고 확보
    STAFF_REST = "직원휴식"    # 피로도 관리
    FACILITY = "시설개선"      # 장기 투자
    PERSONAL_REST = "개인휴식" # 컨디션 회복


@dataclass(frozen=True)
class ActionSlot:
    """행동 슬롯 - 절대 불변"""
    
    slot_id: str
    action_type: Optional[ActionType] = None
    is_used: bool = False
    turn_used: Optional[int] = None
    
    def use_slot(self, action_type: ActionType, turn: int) -> "ActionSlot":
        """슬롯 사용"""
        if self.is_used:
            raise ValueError(f"슬롯 {self.slot_id}은 이미 사용되었습니다")
        
        return ActionSlot(
            slot_id=self.slot_id,
            action_type=action_type,
            is_used=True,
            turn_used=turn
        )
    
    def reset_for_new_day(self) -> "ActionSlot":
        """새로운 날을 위해 슬롯 리셋"""
        return ActionSlot(
            slot_id=self.slot_id,
            action_type=None,
            is_used=False,
            turn_used=None
        )


@dataclass(frozen=True)
class DailyActionPlan:
    """일일 행동 계획 - 절대 불변"""
    
    day: int
    slots: tuple[ActionSlot, ...]
    max_actions: int = 3  # 기본 3개 행동
    
    def get_available_slots(self) -> List[ActionSlot]:
        """사용 가능한 슬롯 목록"""
        return [slot for slot in self.slots if not slot.is_used]
    
    def get_used_slots(self) -> List[ActionSlot]:
        """사용된 슬롯 목록"""
        return [slot for slot in self.slots if slot.is_used]
    
    def can_perform_action(self) -> bool:
        """추가 행동 가능 여부"""
        return len(self.get_available_slots()) > 0
    
    def use_action_slot(self, action_type: ActionType) -> "DailyActionPlan":
        """행동 슬롯 사용"""
        available_slots = self.get_available_slots()
        
        if not available_slots:
            raise ValueError("사용 가능한 행동 슬롯이 없습니다")
        
        # 첫 번째 사용 가능한 슬롯 사용
        slot_to_use = available_slots[0]
        used_slot = slot_to_use.use_slot(action_type, self.day)
        
        # 새로운 슬롯 튜플 생성
        new_slots = tuple(
            used_slot if slot.slot_id == slot_to_use.slot_id else slot
            for slot in self.slots
        )
        
        return DailyActionPlan(
            day=self.day,
            slots=new_slots,
            max_actions=self.max_actions
        )
    
    def advance_to_next_day(self) -> "DailyActionPlan":
        """다음 날로 진행"""
        # 모든 슬롯 리셋
        reset_slots = tuple(slot.reset_for_new_day() for slot in self.slots)
        
        return DailyActionPlan(
            day=self.day + 1,
            slots=reset_slots,
            max_actions=self.max_actions
        )
    
    def get_action_summary(self) -> dict[ActionType, int]:
        """오늘 수행한 행동 요약"""
        summary = {}
        for slot in self.get_used_slots():
            if slot.action_type:
                summary[slot.action_type] = summary.get(slot.action_type, 0) + 1
        return summary
    
    def get_remaining_actions(self) -> int:
        """남은 행동 횟수"""
        return len(self.get_available_slots())


@dataclass(frozen=True)
class ActionSlotConfiguration:
    """행동 슬롯 설정 - 절대 불변"""
    
    base_daily_actions: int = 3  # 기본 일일 행동 수
    research_slot_upgrade_interval: int = 365  # 연구 슬롯 업그레이드 간격 (턴)
    max_daily_actions: int = 5  # 최대 일일 행동 수
    
    def calculate_max_actions_for_day(self, day: int) -> int:
        """특정 날짜의 최대 행동 수 계산"""
        # 연구 슬롯: 시작 1 ▶ 매 365턴 +1 ▶ 최대 3
        additional_slots = min(
            2,  # 최대 2개 추가 (1 + 2 = 3 최대)
            day // self.research_slot_upgrade_interval
        )
        
        return min(
            self.max_daily_actions,
            self.base_daily_actions + additional_slots
        )


def create_daily_action_plan(day: int, config: ActionSlotConfiguration) -> DailyActionPlan:
    """일일 행동 계획 생성"""
    max_actions = config.calculate_max_actions_for_day(day)
    
    slots = tuple(
        ActionSlot(slot_id=f"slot_{i+1}")
        for i in range(max_actions)
    )
    
    return DailyActionPlan(
        day=day,
        slots=slots,
        max_actions=max_actions
    )


# 사전 정의된 행동별 트레이드오프
ACTION_EFFECTS = {
    ActionType.CLEANING: {
        "immediate": {"hygiene": 10, "money": -5000, "fatigue": 5},
        "tradeoff": "위생 개선하지만 돈과 체력 소모"
    },
    ActionType.PROMOTION: {
        "immediate": {"reputation": 15, "demand": 10, "money": -20000},
        "tradeoff": "평판과 손님 증가하지만 비용과 재고 압박"
    },
    ActionType.RESEARCH: {
        "immediate": {"research_points": 1, "daily_revenue": 0},
        "tradeoff": "연구 포인트 획득하지만 당일 매출 포기"
    },
    ActionType.INVENTORY: {
        "immediate": {"inventory": 50, "money": -50000},
        "tradeoff": "재고 확보하지만 현금 부족"
    },
    ActionType.STAFF_REST: {
        "immediate": {"staff_fatigue": -20, "money": -30000},
        "tradeoff": "직원 피로 해소하지만 비용 발생"
    },
    ActionType.FACILITY: {
        "immediate": {"facility": 20, "money": -100000},
        "tradeoff": "장기 투자하지만 단기 현금 부족"
    },
    ActionType.PERSONAL_REST: {
        "immediate": {"happiness": 20, "pain": -15, "opportunity_cost": 10000},
        "tradeoff": "컨디션 회복하지만 기회비용 발생"
    }
} 
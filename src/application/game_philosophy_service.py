"""
게임 철학 애플리케이션 서비스
사용자의 게임 철학을 구현: 확률적 결과, 제한된 액션, 긴장감

헥사고널 아키텍처 원칙:
- 기존 도메인 모델 수정 금지
- 새로운 Application Service로만 철학 구현
- 기존 포트/어댑터 구조 완전 보존

@freeze v0.1.0
"""

import random
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..core.domain.game_state import GameState
from ..core.domain.metrics import MetricsSnapshot, Metric, MetricEnum
from ..core.domain.action_slots import (
    DailyActionPlan, ActionSlotConfiguration, 
    ActionType as SlotActionType, create_daily_action_plan
)


class GamePhilosophyLevel(Enum):
    """게임 철학 적용 강도"""
    GENTLE = "gentle"      # 부드러운 적용 (초보자용)
    NORMAL = "normal"      # 표준 적용 (권장)
    HARDCORE = "hardcore"  # 극한 적용 (도전자용)


@dataclass(frozen=True)
class ProbabilisticOutcome:
    """확률적 결과"""
    is_success: bool
    is_critical: bool  # 대성공 or 대실패
    effects: Dict[str, float]
    message: str
    flavor_text: str


@dataclass(frozen=True)
class ActionConstraint:
    """액션 제약 조건"""
    daily_action_limit: int
    remaining_actions: int
    can_perform_action: bool
    constraint_message: str


@dataclass(frozen=True)
class TensionMetrics:
    """긴장감 지표"""
    financial_pressure: float  # 0.0~1.0 (자금 압박)
    risk_level: float         # 0.0~1.0 (위험 수준)
    uncertainty: float        # 0.0~1.0 (불확실성)
    emotional_intensity: float # 0.0~1.0 (감정적 강도)


class GamePhilosophyApplicationService:
    """
    게임 철학을 구현하는 Application Service
    
    사용자 철학 구현:
    1. 확률적 결과 → 불확실성의 스릴
    2. 제한된 액션 → 전략적 선택의 어려움
    3. 긴장감 조성 → 파산 위험과 보상의 균형
    4. 감정적 여정 → 다양한 엔딩 시나리오
    """
    
    def __init__(self, philosophy_level: GamePhilosophyLevel = GamePhilosophyLevel.NORMAL):
        self.philosophy_level = philosophy_level
        self.action_config = ActionSlotConfiguration()
        
        # 철학 레벨별 설정
        self._configure_philosophy_settings()
    
    def _configure_philosophy_settings(self):
        """철학 레벨별 설정"""
        if self.philosophy_level == GamePhilosophyLevel.GENTLE:
            self.base_success_rate = 0.75  # 높은 성공률
            self.critical_success_rate = 0.15
            self.critical_failure_rate = 0.05
            self.bankruptcy_threshold = -10000  # 여유로운 파산 기준
        elif self.philosophy_level == GamePhilosophyLevel.NORMAL:
            self.base_success_rate = 0.60  # 표준 성공률
            self.critical_success_rate = 0.10
            self.critical_failure_rate = 0.10
            self.bankruptcy_threshold = -5000   # 표준 파산 기준
        else:  # HARDCORE
            self.base_success_rate = 0.45  # 낮은 성공률
            self.critical_success_rate = 0.05
            self.critical_failure_rate = 0.20
            self.bankruptcy_threshold = 0      # 엄격한 파산 기준
    
    def evaluate_action_constraints(
        self, 
        daily_plan: DailyActionPlan,
        game_state: GameState
    ) -> ActionConstraint:
        """액션 제약 조건 평가"""
        remaining = daily_plan.get_remaining_actions()
        can_act = daily_plan.can_perform_action()
        
        if can_act:
            message = f"✅ 오늘 {remaining}개 행동 남음"
        else:
            message = "❌ 오늘 할 수 있는 행동을 모두 사용했습니다. 'turn'으로 다음 날로!"
        
        return ActionConstraint(
            daily_action_limit=daily_plan.max_actions,
            remaining_actions=remaining,
            can_perform_action=can_act,
            constraint_message=message
        )
    
    def calculate_probabilistic_outcome(
        self,
        action_type: str,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot,
        action_context: Dict[str, Any] = None
    ) -> ProbabilisticOutcome:
        """
        확률적 결과 계산
        
        사용자 철학: "확률적 결과로 완벽한 예측 불가능"
        """
        if action_context is None:
            action_context = {}
        
        # 기본 성공 확률 계산
        base_success = self._calculate_base_success_rate(
            action_type, game_state, metrics_snapshot
        )
        
        # 상황적 보정
        situational_modifier = self._calculate_situational_modifier(
            game_state, metrics_snapshot
        )
        
        final_success_rate = max(0.05, min(0.95, base_success + situational_modifier))
        
        # 확률적 판정
        roll = random.random()
        is_success = roll < final_success_rate
        
        # 크리티컬 판정
        is_critical = False
        if is_success and roll < final_success_rate * 0.2:  # 성공 중 20%는 대성공
            is_critical = True
        elif not is_success and roll > (1 - (1-final_success_rate) * 0.3):  # 실패 중 30%는 대실패
            is_critical = True
        
        # 실제 효과 계산
        effects = self._calculate_action_effects(
            action_type, is_success, is_critical, game_state, action_context
        )
        
        # 메시지 생성
        message, flavor_text = self._generate_outcome_messages(
            action_type, is_success, is_critical, effects
        )
        
        return ProbabilisticOutcome(
            is_success=is_success,
            is_critical=is_critical,
            effects=effects,
            message=message,
            flavor_text=flavor_text
        )
    
    def assess_tension_level(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> TensionMetrics:
        """
        긴장감 수준 평가
        
        사용자 철학: "파산 위험으로 절박함, 제한된 액션으로 선택의 어려움"
        """
        # 자금 압박 계산
        financial_pressure = self._calculate_financial_pressure(game_state)
        
        # 위험 수준 계산
        risk_level = self._calculate_risk_level(game_state, metrics_snapshot)
        
        # 불확실성 계산
        uncertainty = self._calculate_uncertainty_level(game_state, metrics_snapshot)
        
        # 감정적 강도 계산
        emotional_intensity = self._calculate_emotional_intensity(
            financial_pressure, risk_level, uncertainty
        )
        
        return TensionMetrics(
            financial_pressure=financial_pressure,
            risk_level=risk_level,
            uncertainty=uncertainty,
            emotional_intensity=emotional_intensity
        )
    
    def check_ending_conditions(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Optional[Dict[str, Any]]:
        """
        엔딩 조건 체크
        
        사용자 철학: "파산/생존/성공/특수 엔딩"
        """
        # 파산 엔딩 (가장 흔함)
        if game_state.money <= self.bankruptcy_threshold:
            return {
                "type": "bankruptcy",
                "title": "파산 엔딩",
                "message": "치킨집 운영의 현실을 마주했습니다...",
                "flavor": self._get_bankruptcy_flavor_text(game_state),
                "is_game_over": True
            }
        
        # 성공 엔딩 (매우 어려움)
        if (game_state.money > 500000 and 
            game_state.reputation > 80 and 
            game_state.day > 100):
            return {
                "type": "success",
                "title": "성공 엔딩",
                "message": "치킨집 사장의 꿈을 이뤘습니다!",
                "flavor": "모든 어려움을 이겨내고 성공적인 치킨집을 만들어냈습니다.",
                "is_game_over": True
            }
        
        # 생존 엔딩
        if game_state.day > 365 and game_state.money > 0:
            return {
                "type": "survival",
                "title": "생존 엔딩",
                "message": "평범하지만 소중한 일상을 지켜냈습니다",
                "flavor": "1년을 버텨내며 작은 치킨집을 지켜냈습니다.",
                "is_game_over": True
            }
        
        # 특수 엔딩들...
        special_ending = self._check_special_endings(game_state, metrics_snapshot)
        if special_ending:
            return special_ending
        
        return None  # 게임 계속
    
    def get_philosophy_insights(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Dict[str, str]:
        """
        게임 철학 관점에서의 인사이트 제공
        
        플레이어가 현재 상황을 철학적으로 이해할 수 있도록 도움
        """
        tension = self.assess_tension_level(game_state, metrics_snapshot)
        
        insights = {}
        
        # 긴장감 분석
        if tension.financial_pressure > 0.7:
            insights["pressure"] = "💸 자금 압박이 심각합니다. 모든 선택이 생존과 직결됩니다."
        elif tension.financial_pressure > 0.4:
            insights["pressure"] = "💰 자금 상황이 불안합니다. 신중한 선택이 필요합니다."
        else:
            insights["pressure"] = "💎 자금 여유가 있습니다. 새로운 도전을 시도해보세요."
        
        # 불확실성 분석
        if tension.uncertainty > 0.6:
            insights["uncertainty"] = "🎲 예측 불가능한 상황입니다. 운에 맡기는 것도 전략입니다."
        else:
            insights["uncertainty"] = "📊 상황이 어느 정도 예측 가능합니다. 계획적으로 접근하세요."
        
        # 감정적 조언
        if tension.emotional_intensity > 0.8:
            insights["emotion"] = "😰 극도의 긴장 상황입니다. 침착함을 유지하세요."
        elif tension.emotional_intensity > 0.5:
            insights["emotion"] = "😤 긴장감이 높습니다. 집중력이 중요합니다."
        else:
            insights["emotion"] = "😌 안정적인 상황입니다. 장기적 관점에서 생각해보세요."
        
        return insights
    
    # ==============================================
    # 내부 계산 메서드들 (기존 아키텍처와 분리)
    # ==============================================
    
    def _calculate_base_success_rate(
        self, 
        action_type: str, 
        game_state: GameState, 
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """기본 성공률 계산"""
        base_rates = {
            "price_change": 0.6,
            "order_inventory": 0.8,
            "staff_management": 0.7,
            "promotion": 0.5,
            "facility_upgrade": 0.7,
            "personal_rest": 0.9,
            "research_development": 0.4
        }
        
        return base_rates.get(action_type, self.base_success_rate)
    
    def _calculate_situational_modifier(
        self, 
        game_state: GameState, 
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """상황적 보정값 계산"""
        modifier = 0.0
        
        # 행복도 보정
        modifier += (game_state.happiness - 50) * 0.002
        
        # 고통도 페널티
        modifier -= game_state.pain * 0.001
        
        # 평판 보너스
        modifier += (game_state.reputation - 50) * 0.001
        
        # 자금 압박 페널티
        if game_state.money < 20000:
            modifier -= 0.1
        
        return modifier
    
    def _calculate_action_effects(
        self,
        action_type: str,
        is_success: bool,
        is_critical: bool,
        game_state: GameState,
        action_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """액션 효과 계산"""
        effects = {}
        
        if action_type == "price_change":
            if is_success:
                effects["money"] = 5000 if not is_critical else 10000
                effects["reputation"] = -2 if not is_critical else 5
            else:
                effects["money"] = -3000 if not is_critical else -8000
                effects["reputation"] = -5 if not is_critical else -15
        
        elif action_type == "order_inventory":
            cost = action_context.get("cost", 50000)
            if is_success:
                effects["money"] = -cost
                effects["inventory"] = 50 if not is_critical else 70
            else:
                effects["money"] = -cost
                effects["inventory"] = 20 if not is_critical else 0
        
        # ... 다른 액션들도 유사하게 구현
        
        return effects
    
    def _calculate_financial_pressure(self, game_state: GameState) -> float:
        """자금 압박 계산"""
        if game_state.money <= 0:
            return 1.0
        elif game_state.money < 10000:
            return 0.9
        elif game_state.money < 30000:
            return 0.7
        elif game_state.money < 50000:
            return 0.4
        else:
            return max(0.0, (100000 - game_state.money) / 100000)
    
    def _calculate_risk_level(
        self, 
        game_state: GameState, 
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """위험 수준 계산"""
        risk = 0.0
        
        # 자금 위험
        risk += self._calculate_financial_pressure(game_state) * 0.4
        
        # 평판 위험
        if game_state.reputation < 30:
            risk += 0.3
        
        # 재고 위험
        inventory = metrics_snapshot.get_metric_value("inventory")
        if inventory < 20:
            risk += 0.2
        
        # 스트레스 위험
        if game_state.pain > 70:
            risk += 0.1
        
        return min(1.0, risk)
    
    def _calculate_uncertainty_level(
        self, 
        game_state: GameState, 
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """불확실성 수준 계산"""
        # 게임 초기에는 불확실성이 높음
        uncertainty = max(0.3, 1.0 - (game_state.day / 100))
        
        # 자금이 적을수록 불확실성 증가
        if game_state.money < 50000:
            uncertainty += 0.2
        
        return min(1.0, uncertainty)
    
    def _calculate_emotional_intensity(
        self, 
        financial_pressure: float, 
        risk_level: float, 
        uncertainty: float
    ) -> float:
        """감정적 강도 계산"""
        return (financial_pressure * 0.4 + risk_level * 0.4 + uncertainty * 0.2)
    
    def _generate_outcome_messages(
        self,
        action_type: str,
        is_success: bool,
        is_critical: bool,
        effects: Dict[str, float]
    ) -> Tuple[str, str]:
        """결과 메시지 생성"""
        if is_success and is_critical:
            message = "🎉 대성공!"
            flavor = "예상을 뛰어넘는 놀라운 결과입니다!"
        elif is_success:
            message = "✅ 성공"
            flavor = "계획대로 잘 진행되었습니다."
        elif is_critical:
            message = "💥 치명적 실패!"
            flavor = "최악의 상황이 벌어졌습니다..."
        else:
            message = "❌ 실패"
            flavor = "아쉽지만 실패했습니다."
        
        return message, flavor
    
    def _get_bankruptcy_flavor_text(self, game_state: GameState) -> str:
        """파산 엔딩 플레이버 텍스트"""
        if game_state.day < 30:
            return "치킨집은 생각보다 어려운 사업이었습니다..."
        elif game_state.day < 100:
            return "몇 달간 열심히 했지만, 현실의 벽은 높았습니다."
        else:
            return "오랜 시간 버텨왔지만, 결국 한계에 부딪혔습니다."
    
    def _check_special_endings(
        self, 
        game_state: GameState, 
        metrics_snapshot: MetricsSnapshot
    ) -> Optional[Dict[str, Any]]:
        """특수 엔딩 체크"""
        # 연구개발 엔딩
        if game_state.reputation > 90 and game_state.day > 200:
            return {
                "type": "research_success",
                "title": "연구개발 엔딩",
                "message": "혁신적인 연구로 프랜차이즈화에 성공했습니다!",
                "flavor": "작은 치킨집이 대기업으로 성장했습니다.",
                "is_game_over": True
            }
        
        return None 
"""
연구개발(R&D) 도메인 모델
불변 객체로 구현된 연구개발 관련 도메인 엔티티를 포함합니다.

@freeze v0.1.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random


class ResearchType(Enum):
    """연구 유형"""
    NEW_MENU = "신메뉴"
    NEW_SAUCE = "신소스"
    COOKING_METHOD = "조리법"
    INGREDIENT = "재료혁신"
    PROCESS_OPTIMIZATION = "프로세스개선"


class ResearchStatus(Enum):
    """연구 상태"""
    PENDING = "대기중"
    IN_PROGRESS = "진행중"
    SUCCESS = "성공"
    FAILURE = "실패"
    CANCELLED = "취소됨"


@dataclass(frozen=True)
class ResearchCost:
    """연구 비용 - 절대 불변"""
    
    money: int
    time_days: int
    opportunity_cost: int = 0  # 기회비용
    
    def total_cost(self) -> int:
        """총 비용 계산"""
        return self.money + self.opportunity_cost


@dataclass(frozen=True)
class ResearchEffects:
    """연구 성공 시 효과 - 절대 불변"""
    
    reputation: int = 0
    demand: int = 0
    happiness: int = 0
    pain: int = 0
    special_effect: Optional[str] = None
    
    def apply_multiplier(self, multiplier: float) -> "ResearchEffects":
        """승수 적용하여 새 효과 반환"""
        return ResearchEffects(
            reputation=int(self.reputation * multiplier),
            demand=int(self.demand * multiplier),
            happiness=int(self.happiness * multiplier),
            pain=int(self.pain * multiplier),
            special_effect=self.special_effect
        )


@dataclass(frozen=True)
class ResearchProject:
    """연구 프로젝트 - 절대 불변"""
    
    id: str
    name: str
    research_type: ResearchType
    cost: ResearchCost
    success_rate: float  # 0.0 ~ 1.0
    expected_effects: ResearchEffects
    failure_penalty: ResearchEffects
    status: ResearchStatus = ResearchStatus.PENDING
    description: str = ""
    
    def can_start(self, available_money: int) -> bool:
        """연구 시작 가능 여부"""
        return (
            available_money >= self.cost.money and 
            self.status == ResearchStatus.PENDING
        )
    
    def start_research(self) -> "ResearchProject":
        """연구 시작"""
        if self.status != ResearchStatus.PENDING:
            raise ValueError(f"연구를 시작할 수 없는 상태: {self.status}")
        
        return ResearchProject(
            id=self.id,
            name=self.name,
            research_type=self.research_type,
            cost=self.cost,
            success_rate=self.success_rate,
            expected_effects=self.expected_effects,
            failure_penalty=self.failure_penalty,
            status=ResearchStatus.IN_PROGRESS,
            description=self.description
        )
    
    def complete_research(self, is_success: bool) -> "ResearchProject":
        """연구 완료"""
        if self.status != ResearchStatus.IN_PROGRESS:
            raise ValueError(f"연구를 완료할 수 없는 상태: {self.status}")
        
        new_status = ResearchStatus.SUCCESS if is_success else ResearchStatus.FAILURE
        
        return ResearchProject(
            id=self.id,
            name=self.name,
            research_type=self.research_type,
            cost=self.cost,
            success_rate=self.success_rate,
            expected_effects=self.expected_effects,
            failure_penalty=self.failure_penalty,
            status=new_status,
            description=self.description
        )


@dataclass(frozen=True)
class ResearchResult:
    """연구 결과 - 절대 불변"""
    
    project: ResearchProject
    is_success: bool
    actual_effects: ResearchEffects
    message: str
    innovation_name: Optional[str] = None  # 성공 시 혁신 이름
    
    def get_final_effects_dict(self) -> dict[str, int]:
        """최종 효과를 딕셔너리로 반환 (GameState.apply_effects 호환)"""
        effects = {}
        
        if self.actual_effects.reputation != 0:
            effects["reputation"] = self.actual_effects.reputation
        if self.actual_effects.happiness != 0:
            effects["happiness"] = self.actual_effects.happiness
        if self.actual_effects.pain != 0:
            effects["pain"] = self.actual_effects.pain
            
        return effects
    
    def get_metrics_effects_dict(self) -> dict[str, int]:
        """지표 효과를 딕셔너리로 반환 (MetricsSnapshot.apply_effects 호환)"""
        effects = {}
        
        if self.actual_effects.demand != 0:
            effects["demand"] = self.actual_effects.demand
            
        return effects


@dataclass(frozen=True)
class ResearchConfiguration:
    """연구개발 설정 - 절대 불변"""
    
    min_success_rate: float = 0.3  # 최소 성공률
    max_success_rate: float = 0.9  # 최대 성공률
    cost_scaling_factor: float = 1.2  # 비용 증가 계수
    breakthrough_chance: float = 0.1  # 대박 확률
    critical_failure_chance: float = 0.05  # 치명적 실패 확률
    
    def validate(self) -> bool:
        """설정 유효성 검증"""
        return (
            0.0 <= self.min_success_rate <= 1.0 and
            0.0 <= self.max_success_rate <= 1.0 and
            self.min_success_rate <= self.max_success_rate and
            self.cost_scaling_factor > 0.0 and
            0.0 <= self.breakthrough_chance <= 1.0 and
            0.0 <= self.critical_failure_chance <= 1.0
        )


# 프리셋 연구 프로젝트들
PRESET_RESEARCH_PROJECTS = [
    ResearchProject(
        id="spicy_honey_garlic",
        name="매콤달콤 허니갈릭 치킨",
        research_type=ResearchType.NEW_MENU,
        cost=ResearchCost(money=80000, time_days=1),
        success_rate=0.65,
        expected_effects=ResearchEffects(
            reputation=25, 
            demand=30, 
            happiness=15,
            special_effect="시그니처 메뉴 등극"
        ),
        failure_penalty=ResearchEffects(pain=10, happiness=-5),
        description="달콤함과 매콤함의 완벽한 조화를 추구하는 신메뉴 개발"
    ),
    
    ResearchProject(
        id="truffle_premium",
        name="프리미엄 트러플 치킨",
        research_type=ResearchType.NEW_MENU,
        cost=ResearchCost(money=150000, time_days=2),
        success_rate=0.45,
        expected_effects=ResearchEffects(
            reputation=40, 
            demand=20, 
            happiness=25,
            special_effect="프리미엄 브랜드 포지셔닝"
        ),
        failure_penalty=ResearchEffects(pain=15, happiness=-10),
        description="고급 트러플을 활용한 프리미엄 메뉴 개발"
    ),
    
    ResearchProject(
        id="secret_sauce",
        name="시그니처 비밀양념",
        research_type=ResearchType.NEW_SAUCE,
        cost=ResearchCost(money=60000, time_days=1),
        success_rate=0.75,
        expected_effects=ResearchEffects(
            reputation=20, 
            demand=35, 
            happiness=10,
            special_effect="차별화된 소스"
        ),
        failure_penalty=ResearchEffects(pain=8, happiness=-3),
        description="경쟁업체와 차별화되는 독자적인 양념 개발"
    ),
    
    ResearchProject(
        id="fast_cooking",
        name="초고속 조리법 혁신",
        research_type=ResearchType.COOKING_METHOD,
        cost=ResearchCost(money=100000, time_days=1),
        success_rate=0.55,
        expected_effects=ResearchEffects(
            reputation=15, 
            demand=25, 
            happiness=20,
            special_effect="운영 효율성 향상"
        ),
        failure_penalty=ResearchEffects(pain=12, happiness=-7),
        description="조리 시간을 혁신적으로 단축하는 새로운 방법 연구"
    )
] 
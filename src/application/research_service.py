"""
연구개발 애플리케이션 서비스
연구개발 관련 비즈니스 로직을 오케스트레이션합니다.

@freeze v0.1.0
"""

import random
from typing import List, Optional, Dict, Tuple

from ..core.ports.research_port import IResearchService, IResearchRepository
from ..core.domain.research import (
    ResearchProject, 
    ResearchResult, 
    ResearchType,
    ResearchEffects,
    ResearchConfiguration,
    PRESET_RESEARCH_PROJECTS
)
from ..core.domain.game_state import GameState
from ..core.domain.metrics import MetricsSnapshot


class ResearchApplicationService(IResearchService):
    """연구개발 애플리케이션 서비스"""
    
    def __init__(self, repository: IResearchRepository):
        self._repository = repository
        self._config = repository.get_configuration()
    
    def get_available_projects(
        self, 
        current_money: int,
        research_type: Optional[ResearchType] = None
    ) -> List[ResearchProject]:
        """현재 자금으로 시작 가능한 연구 프로젝트 목록"""
        all_projects = self._repository.get_all_projects()
        
        available = [
            project for project in all_projects
            if project.can_start(current_money)
        ]
        
        if research_type:
            available = [
                project for project in available
                if project.research_type == research_type
            ]
        
        # 비용 순으로 정렬 (저렴한 것부터)
        return sorted(available, key=lambda p: p.cost.money)
    
    def execute_research(
        self,
        project: ResearchProject,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> ResearchResult:
        """연구 프로젝트 실행"""
        if not project.can_start(game_state.money):
            raise ValueError(f"자금 부족: {game_state.money}원 < {project.cost.money}원")
        
        # 실제 성공 확률 계산 (게임 상태 고려)
        adjusted_probability = self.calculate_success_probability(
            project, game_state, metrics_snapshot
        )
        
        # 연구 결과 시뮬레이션
        is_success, message = self.simulate_research_outcome(
            project, adjusted_probability
        )
        
        # 실제 효과 계산
        actual_effects = self._calculate_actual_effects(
            project, is_success, game_state, metrics_snapshot
        )
        
        # 혁신 이름 생성 (성공 시)
        innovation_name = None
        if is_success:
            innovation_name = self._generate_innovation_name(project)
        
        result = ResearchResult(
            project=project.complete_research(is_success),
            is_success=is_success,
            actual_effects=actual_effects,
            message=message,
            innovation_name=innovation_name
        )
        
        # 결과 저장
        self._repository.save_research_result(result)
        
        return result
    
    def calculate_success_probability(
        self,
        project: ResearchProject,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> float:
        """실제 성공 확률 계산 (게임 상태 고려)"""
        base_rate = project.success_rate
        
        # 행복도 보너스 (행복할수록 창의력 증가)
        happiness_bonus = (game_state.happiness - 50) * 0.002  # 최대 ±10%
        
        # 고통도 페널티 (스트레스는 집중력 저하)
        pain_penalty = game_state.pain * 0.001  # 최대 -10%
        
        # 평판 보너스 (평판이 높으면 좋은 재료/장비 접근 가능)
        reputation_bonus = (game_state.reputation - 50) * 0.001  # 최대 ±5%
        
        # 시설 상태 보너스
        facility_condition = metrics_snapshot.get_metric_value("facility")
        facility_bonus = (facility_condition - 50) * 0.001  # 최대 ±5%
        
        # 자금 상황 고려 (너무 절박하면 실패 확률 증가)
        money_pressure = 0.0
        if game_state.money < project.cost.money * 1.5:  # 자금이 빠듯하면
            money_pressure = -0.05  # -5% 페널티
        
        adjusted_rate = (
            base_rate + 
            happiness_bonus + 
            reputation_bonus + 
            facility_bonus + 
            money_pressure - 
            pain_penalty
        )
        
        # 최소/최대 범위 제한
        return max(
            self._config.min_success_rate,
            min(self._config.max_success_rate, adjusted_rate)
        )
    
    def simulate_research_outcome(
        self,
        project: ResearchProject,
        success_probability: float
    ) -> Tuple[bool, str]:
        """연구 결과 시뮬레이션"""
        # 기본 성공/실패 판정
        is_success = random.random() < success_probability
        
        if is_success:
            # 대박 확률 체크
            is_breakthrough = random.random() < self._config.breakthrough_chance
            
            if is_breakthrough:
                messages = [
                    f"🎉 완전 대박! '{project.name}'이 업계 혁신을 일으켰습니다!",
                    f"🌟 놀라운 성공! '{project.name}'이 예상을 뛰어넘는 결과를 만들어냈습니다!",
                    f"🚀 혁신적 성과! '{project.name}'이 시장을 뒤흔들고 있습니다!"
                ]
            else:
                messages = [
                    f"✅ 연구 성공! '{project.name}' 개발이 완료되었습니다!",
                    f"🎯 목표 달성! '{project.name}'이 성공적으로 완성되었습니다!",
                    f"💡 혁신 완료! '{project.name}'이 시장에 선보일 준비가 되었습니다!"
                ]
        else:
            # 치명적 실패 확률 체크
            is_critical_failure = random.random() < self._config.critical_failure_chance
            
            if is_critical_failure:
                messages = [
                    f"💥 치명적 실패! '{project.name}' 연구가 완전히 뒤틀어졌습니다...",
                    f"😱 최악의 결과! '{project.name}' 개발이 예상보다 훨씬 심각하게 실패했습니다!",
                    f"🚨 재앙적 실패! '{project.name}' 프로젝트가 돌이킬 수 없는 문제를 일으켰습니다!"
                ]
            else:
                failure_reasons = [
                    f"양념 배합이 실패해서 먹을 수 없는 맛이 됨",
                    f"새로운 조리법이 너무 복잡해서 실용성 부족",
                    f"고객 테스트에서 혹평... '기존이 더 나았다'",
                    f"재료비가 너무 비싸서 수익성 없음",
                    f"조리시간이 너무 오래 걸려서 포기",
                    f"예상과 다른 결과로 상품화 불가",
                    f"기술적 한계로 인한 개발 중단"
                ]
                reason = random.choice(failure_reasons)
                messages = [f"💸 연구 실패... 사유: {reason}"]
        
        message = random.choice(messages)
        return is_success, message
    
    def get_research_recommendations(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot,
        max_recommendations: int = 3
    ) -> List[ResearchProject]:
        """현재 상황에 맞는 연구 추천"""
        available_projects = self.get_available_projects(game_state.money)
        
        if not available_projects:
            return []
        
        # 현재 상황 분석
        needs_reputation = game_state.reputation < 40
        needs_demand = metrics_snapshot.get_metric_value("demand") < 30
        has_high_pain = game_state.pain > 60
        has_good_facility = metrics_snapshot.get_metric_value("facility") > 70
        
        # 상황별 가중치 계산
        scored_projects = []
        for project in available_projects:
            score = 0.0
            
            # 기본 성공률 점수
            score += project.success_rate * 100
            
            # 상황별 보너스
            if needs_reputation and project.expected_effects.reputation > 15:
                score += 50  # 평판 부족 시 평판 개선 프로젝트 우선
            
            if needs_demand and project.expected_effects.demand > 20:
                score += 40  # 수요 부족 시 수요 증가 프로젝트 우선
            
            if has_high_pain and project.expected_effects.happiness > 10:
                score += 30  # 고통이 높으면 행복도 증가 프로젝트 우선
            
            if has_good_facility and project.research_type == ResearchType.PROCESS_OPTIMIZATION:
                score += 25  # 시설이 좋으면 프로세스 개선 우선
            
            # 비용 대비 효과 점수
            total_effect = (
                project.expected_effects.reputation +
                project.expected_effects.demand * 0.8 +
                project.expected_effects.happiness * 0.5
            )
            cost_efficiency = total_effect / (project.cost.money / 10000)  # 만원당 효과
            score += cost_efficiency * 10
            
            scored_projects.append((project, score))
        
        # 점수순 정렬
        scored_projects.sort(key=lambda x: x[1], reverse=True)
        
        return [project for project, _ in scored_projects[:max_recommendations]]
    
    def calculate_risk_assessment(
        self,
        project: ResearchProject,
        game_state: GameState
    ) -> Dict[str, float]:
        """연구 리스크 평가"""
        risks = {}
        
        # 자금 리스크 (파산 위험)
        remaining_money = game_state.money - project.cost.money
        if remaining_money < 20000:  # 2만원 미만 남으면 위험
            risks["financial"] = 1.0 - (remaining_money / 20000)
        else:
            risks["financial"] = 0.0
        
        # 실패 리스크
        success_prob = self.calculate_success_probability(
            project, game_state, 
            # 임시로 기본 지표 사용 (실제로는 현재 지표 전달 필요)
            MetricsSnapshot(metrics={}, timestamp=game_state.day)
        )
        risks["failure"] = 1.0 - success_prob
        
        # 기회비용 리스크 (다른 안전한 투자 대비)
        safe_investment_return = 0.1  # 안전한 투자 수익률 10%
        expected_return = (
            project.expected_effects.reputation * 1000 +  # 평판 1점당 1000원 가치
            project.expected_effects.demand * 500  # 수요 1점당 500원 가치
        ) * success_prob
        
        if expected_return < project.cost.money * safe_investment_return:
            risks["opportunity"] = 0.8
        else:
            risks["opportunity"] = 0.2
        
        # 전략적 리스크 (게임 상태와의 부합성)
        strategic_risk = 0.0
        if game_state.money < 50000 and project.cost.money > 80000:
            strategic_risk += 0.4  # 자금 부족한데 고비용 프로젝트
        
        if game_state.pain > 70 and project.failure_penalty.pain > 5:
            strategic_risk += 0.3  # 이미 스트레스 높은데 실패 시 더 고통
        
        risks["strategic"] = min(1.0, strategic_risk)
        
        return risks
    
    def _calculate_actual_effects(
        self,
        project: ResearchProject,
        is_success: bool,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> ResearchEffects:
        """실제 효과 계산"""
        if is_success:
            base_effects = project.expected_effects
            
            # 대박 확률 체크
            is_breakthrough = random.random() < self._config.breakthrough_chance
            
            if is_breakthrough:
                # 대박 시 1.5~2.0배 효과
                multiplier = random.uniform(1.5, 2.0)
                return base_effects.apply_multiplier(multiplier)
            else:
                # 일반 성공 시 0.8~1.2배 효과 (약간의 변동성)
                multiplier = random.uniform(0.8, 1.2)
                return base_effects.apply_multiplier(multiplier)
        else:
            # 실패 시 페널티 적용
            base_penalty = project.failure_penalty
            
            # 치명적 실패 확률 체크
            is_critical = random.random() < self._config.critical_failure_chance
            
            if is_critical:
                # 치명적 실패 시 1.5~2.5배 페널티
                multiplier = random.uniform(1.5, 2.5)
                return base_penalty.apply_multiplier(multiplier)
            else:
                # 일반 실패 시 페널티 그대로
                return base_penalty
    
    def _generate_innovation_name(self, project: ResearchProject) -> str:
        """혁신 이름 생성 (성공 시)"""
        prefixes = ["시그니처", "프리미엄", "스페셜", "혁신적", "차세대"]
        suffixes = ["에디션", "시리즈", "컬렉션", "라인", "브랜드"]
        
        if project.research_type == ResearchType.NEW_MENU:
            return f"{random.choice(prefixes)} {project.name}"
        elif project.research_type == ResearchType.NEW_SAUCE:
            return f"{project.name} {random.choice(suffixes)}"
        else:
            return f"{random.choice(prefixes)} {project.name} {random.choice(suffixes)}" 
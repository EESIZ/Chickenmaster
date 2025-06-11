"""
연구개발 파사드
연구개발 모듈의 외부 인터페이스를 단순화하여 제공합니다.

@freeze v0.1.0
"""

from typing import List, Optional, Dict, Tuple

from ..core.ports.research_port import IResearchService, IResearchRepository
from ..core.domain.research import (
    ResearchProject, 
    ResearchResult, 
    ResearchType,
    ResearchConfiguration
)
from ..core.domain.game_state import GameState
from ..core.domain.metrics import MetricsSnapshot


class ResearchFacade:
    """연구개발 파사드 - 단순화된 외부 인터페이스"""
    
    def __init__(self, service: IResearchService, repository: IResearchRepository):
        self._service = service
        self._repository = repository
    
    # === 주요 기능 ===
    
    def get_available_research_options(
        self, 
        game_state: GameState,
        research_type: Optional[ResearchType] = None
    ) -> List[ResearchProject]:
        """현재 상황에서 가능한 연구 옵션들"""
        return self._service.get_available_projects(
            game_state.money, 
            research_type
        )
    
    def execute_research_project(
        self,
        project_id: str,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Optional[ResearchResult]:
        """연구 프로젝트 실행"""
        project = self._repository.get_project_by_id(project_id)
        if not project:
            return None
        
        try:
            return self._service.execute_research(project, game_state, metrics_snapshot)
        except ValueError:
            return None
    
    def get_research_recommendations(
        self,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot,
        max_count: int = 3
    ) -> List[ResearchProject]:
        """현재 상황에 맞는 연구 추천"""
        return self._service.get_research_recommendations(
            game_state, 
            metrics_snapshot, 
            max_count
        )
    
    def assess_research_risk(
        self,
        project_id: str,
        game_state: GameState
    ) -> Optional[Dict[str, float]]:
        """연구 프로젝트 리스크 평가"""
        project = self._repository.get_project_by_id(project_id)
        if not project:
            return None
        
        return self._service.calculate_risk_assessment(project, game_state)
    
    # === 정보 조회 ===
    
    def get_all_research_projects(self) -> List[ResearchProject]:
        """모든 연구 프로젝트 목록"""
        return self._repository.get_all_projects()
    
    def get_projects_by_type(self, research_type: ResearchType) -> List[ResearchProject]:
        """유형별 연구 프로젝트 목록"""
        return self._repository.get_projects_by_type(research_type)
    
    def get_project_details(self, project_id: str) -> Optional[ResearchProject]:
        """특정 프로젝트 상세 정보"""
        return self._repository.get_project_by_id(project_id)
    
    def get_research_history(self, limit: int = 10) -> List[ResearchResult]:
        """연구 이력 조회"""
        return self._repository.get_research_history(limit)
    
    def calculate_success_probability(
        self,
        project_id: str,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Optional[float]:
        """실제 성공 확률 계산"""
        project = self._repository.get_project_by_id(project_id)
        if not project:
            return None
        
        return self._service.calculate_success_probability(
            project, 
            game_state, 
            metrics_snapshot
        )
    
    # === 설정 관리 ===
    
    def get_configuration(self) -> ResearchConfiguration:
        """현재 연구개발 설정"""
        return self._repository.get_configuration()
    
    def update_configuration(self, config: ResearchConfiguration) -> bool:
        """연구개발 설정 업데이트"""
        return self._repository.update_configuration(config)
    
    # === 게임 통합용 헬퍼 ===
    
    def apply_research_effects_to_game(
        self,
        result: ResearchResult,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Tuple[GameState, MetricsSnapshot]:
        """연구 결과를 게임 상태에 적용"""
        # 게임 상태 효과 적용
        game_effects = result.get_final_effects_dict()
        
        # 연구 비용 차감
        game_effects["money"] = -result.project.cost.money
        
        new_game_state = game_state.apply_effects(game_effects)
        
        # 이벤트 히스토리에 추가
        if result.is_success and result.innovation_name:
            event_message = f"R&D 성공: '{result.innovation_name}' 개발 완료!"
        elif result.is_success:
            event_message = f"R&D 성공: '{result.project.name}' 개발 완료!"
        else:
            event_message = f"R&D 실패: '{result.project.name}' 개발 중단..."
        
        new_game_state = new_game_state.add_event_to_history(event_message)
        
        # 지표 효과 적용
        metrics_effects = result.get_metrics_effects_dict()
        new_metrics_snapshot = metrics_snapshot.apply_effects(metrics_effects)
        
        return new_game_state, new_metrics_snapshot
    
    def get_affordable_projects(self, current_money: int) -> List[ResearchProject]:
        """현재 자금으로 실행 가능한 프로젝트들"""
        return self._service.get_available_projects(current_money)
    
    def get_project_cost_breakdown(self, project_id: str) -> Optional[Dict[str, int]]:
        """프로젝트 비용 분석"""
        project = self._repository.get_project_by_id(project_id)
        if not project:
            return None
        
        return {
            "direct_cost": project.cost.money,
            "opportunity_cost": project.cost.opportunity_cost,
            "total_cost": project.cost.total_cost(),
            "time_investment": project.cost.time_days
        }
    
    def simulate_research_preview(
        self,
        project_id: str,
        game_state: GameState,
        metrics_snapshot: MetricsSnapshot
    ) -> Optional[Dict]:
        """연구 시뮬레이션 미리보기 (실제 실행하지 않음)"""
        project = self._repository.get_project_by_id(project_id)
        if not project:
            return None
        
        success_prob = self.calculate_success_probability(
            project_id, game_state, metrics_snapshot
        )
        
        risk_assessment = self.assess_research_risk(project_id, game_state)
        
        return {
            "project": project,
            "success_probability": success_prob,
            "risk_assessment": risk_assessment,
            "cost_breakdown": self.get_project_cost_breakdown(project_id),
            "expected_effects": {
                "success": project.expected_effects,
                "failure": project.failure_penalty
            }
        } 
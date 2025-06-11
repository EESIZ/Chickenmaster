"""
연구개발 어댑터
연구개발 관련 외부 저장소 연결을 담당합니다.

@freeze v0.1.0
"""

from typing import List, Optional, Dict
import json
from pathlib import Path

from ..core.ports.research_port import IResearchRepository
from ..core.domain.research import (
    ResearchProject, 
    ResearchResult, 
    ResearchType,
    ResearchConfiguration,
    PRESET_RESEARCH_PROJECTS
)


class InMemoryResearchRepository(IResearchRepository):
    """인메모리 연구개발 저장소 (개발/테스트용)"""
    
    def __init__(self):
        # 프리셋 프로젝트들로 초기화
        self._projects: Dict[str, ResearchProject] = {
            project.id: project for project in PRESET_RESEARCH_PROJECTS
        }
        
        # 연구 결과 이력
        self._research_history: List[ResearchResult] = []
        
        # 기본 설정
        self._configuration = ResearchConfiguration()
    
    def get_project_by_id(self, project_id: str) -> Optional[ResearchProject]:
        """ID로 연구 프로젝트 조회"""
        return self._projects.get(project_id)
    
    def get_all_projects(self) -> List[ResearchProject]:
        """모든 연구 프로젝트 조회"""
        return list(self._projects.values())
    
    def get_projects_by_type(self, research_type: ResearchType) -> List[ResearchProject]:
        """연구 유형별 프로젝트 조회"""
        return [
            project for project in self._projects.values()
            if project.research_type == research_type
        ]
    
    def save_research_result(self, result: ResearchResult) -> bool:
        """연구 결과 저장"""
        try:
            self._research_history.append(result)
            return True
        except Exception:
            return False
    
    def get_research_history(self, limit: int = 10) -> List[ResearchResult]:
        """연구 이력 조회"""
        return self._research_history[-limit:] if limit > 0 else self._research_history
    
    def get_configuration(self) -> ResearchConfiguration:
        """연구개발 설정 조회"""
        return self._configuration
    
    def update_configuration(self, config: ResearchConfiguration) -> bool:
        """연구개발 설정 업데이트"""
        if not config.validate():
            return False
        
        self._configuration = config
        return True


class FileBasedResearchRepository(IResearchRepository):
    """파일 기반 연구개발 저장소"""
    
    def __init__(self, data_dir: str = "data/research"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.projects_file = self.data_dir / "projects.json"
        self.history_file = self.data_dir / "history.json" 
        self.config_file = self.data_dir / "config.json"
        
        # 초기화
        self._load_or_create_projects()
        self._load_or_create_history()
        self._load_or_create_config()
    
    def get_project_by_id(self, project_id: str) -> Optional[ResearchProject]:
        """ID로 연구 프로젝트 조회"""
        projects = self._load_projects()
        project_data = projects.get(project_id)
        
        if project_data:
            return self._dict_to_project(project_data)
        return None
    
    def get_all_projects(self) -> List[ResearchProject]:
        """모든 연구 프로젝트 조회"""
        projects_data = self._load_projects()
        return [
            self._dict_to_project(data) 
            for data in projects_data.values()
        ]
    
    def get_projects_by_type(self, research_type: ResearchType) -> List[ResearchProject]:
        """연구 유형별 프로젝트 조회"""
        all_projects = self.get_all_projects()
        return [
            project for project in all_projects
            if project.research_type == research_type
        ]
    
    def save_research_result(self, result: ResearchResult) -> bool:
        """연구 결과 저장"""
        try:
            history = self._load_history()
            history.append(self._result_to_dict(result))
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def get_research_history(self, limit: int = 10) -> List[ResearchResult]:
        """연구 이력 조회"""
        history_data = self._load_history()
        
        if limit > 0:
            history_data = history_data[-limit:]
        
        return [
            self._dict_to_result(data) 
            for data in history_data
        ]
    
    def get_configuration(self) -> ResearchConfiguration:
        """연구개발 설정 조회"""
        config_data = self._load_config()
        return ResearchConfiguration(**config_data)
    
    def update_configuration(self, config: ResearchConfiguration) -> bool:
        """연구개발 설정 업데이트"""
        if not config.validate():
            return False
        
        try:
            config_data = {
                "min_success_rate": config.min_success_rate,
                "max_success_rate": config.max_success_rate,
                "cost_scaling_factor": config.cost_scaling_factor,
                "breakthrough_chance": config.breakthrough_chance,
                "critical_failure_chance": config.critical_failure_chance
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def _load_or_create_projects(self):
        """프로젝트 파일 로드 또는 생성"""
        if not self.projects_file.exists():
            # 프리셋 프로젝트들로 초기화
            initial_projects = {
                project.id: self._project_to_dict(project)
                for project in PRESET_RESEARCH_PROJECTS
            }
            
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(initial_projects, f, ensure_ascii=False, indent=2)
    
    def _load_or_create_history(self):
        """이력 파일 로드 또는 생성"""
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_or_create_config(self):
        """설정 파일 로드 또는 생성"""
        if not self.config_file.exists():
            default_config = ResearchConfiguration()
            self.update_configuration(default_config)
    
    def _load_projects(self) -> Dict:
        """프로젝트 데이터 로드"""
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _load_history(self) -> List:
        """이력 데이터 로드"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _load_config(self) -> Dict:
        """설정 데이터 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return ResearchConfiguration().__dict__
    
    def _project_to_dict(self, project: ResearchProject) -> Dict:
        """프로젝트를 딕셔너리로 변환"""
        return {
            "id": project.id,
            "name": project.name,
            "research_type": project.research_type.value,
            "cost": {
                "money": project.cost.money,
                "time_days": project.cost.time_days,
                "opportunity_cost": project.cost.opportunity_cost
            },
            "success_rate": project.success_rate,
            "expected_effects": {
                "reputation": project.expected_effects.reputation,
                "demand": project.expected_effects.demand,
                "happiness": project.expected_effects.happiness,
                "pain": project.expected_effects.pain,
                "special_effect": project.expected_effects.special_effect
            },
            "failure_penalty": {
                "reputation": project.failure_penalty.reputation,
                "demand": project.failure_penalty.demand,
                "happiness": project.failure_penalty.happiness,
                "pain": project.failure_penalty.pain,
                "special_effect": project.failure_penalty.special_effect
            },
            "status": project.status.value,
            "description": project.description
        }
    
    def _dict_to_project(self, data: Dict) -> ResearchProject:
        """딕셔너리를 프로젝트로 변환"""
        from ..core.domain.research import (
            ResearchCost, ResearchEffects, ResearchStatus
        )
        
        return ResearchProject(
            id=data["id"],
            name=data["name"],
            research_type=ResearchType(data["research_type"]),
            cost=ResearchCost(**data["cost"]),
            success_rate=data["success_rate"],
            expected_effects=ResearchEffects(**data["expected_effects"]),
            failure_penalty=ResearchEffects(**data["failure_penalty"]),
            status=ResearchStatus(data["status"]),
            description=data["description"]
        )
    
    def _result_to_dict(self, result: ResearchResult) -> Dict:
        """결과를 딕셔너리로 변환"""
        return {
            "project": self._project_to_dict(result.project),
            "is_success": result.is_success,
            "actual_effects": {
                "reputation": result.actual_effects.reputation,
                "demand": result.actual_effects.demand,
                "happiness": result.actual_effects.happiness,
                "pain": result.actual_effects.pain,
                "special_effect": result.actual_effects.special_effect
            },
            "message": result.message,
            "innovation_name": result.innovation_name
        }
    
    def _dict_to_result(self, data: Dict) -> ResearchResult:
        """딕셔너리를 결과로 변환"""
        from ..core.domain.research import ResearchEffects
        
        return ResearchResult(
            project=self._dict_to_project(data["project"]),
            is_success=data["is_success"],
            actual_effects=ResearchEffects(**data["actual_effects"]),
            message=data["message"],
            innovation_name=data.get("innovation_name")
        ) 
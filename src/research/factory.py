"""
연구개발 모듈 팩토리
연구개발 관련 객체들의 생성과 의존성 주입을 담당합니다.

@freeze v0.1.0
"""

from typing import Optional

from ..core.ports.research_port import IResearchRepository, IResearchService
from ..application.research_service import ResearchApplicationService
from ..adapters.research_adapter import InMemoryResearchRepository, FileBasedResearchRepository
from .facade import ResearchFacade


class ResearchModuleFactory:
    """연구개발 모듈 팩토리"""
    
    @staticmethod
    def create_in_memory_module() -> ResearchFacade:
        """인메모리 기반 연구개발 모듈 생성 (테스트/개발용)"""
        repository = InMemoryResearchRepository()
        service = ResearchApplicationService(repository)
        return ResearchFacade(service, repository)
    
    @staticmethod
    def create_file_based_module(data_dir: str = "data/research") -> ResearchFacade:
        """파일 기반 연구개발 모듈 생성 (프로덕션용)"""
        repository = FileBasedResearchRepository(data_dir)
        service = ResearchApplicationService(repository)
        return ResearchFacade(service, repository)
    
    @staticmethod
    def create_custom_module(
        repository: Optional[IResearchRepository] = None,
        service: Optional[IResearchService] = None
    ) -> ResearchFacade:
        """사용자 정의 연구개발 모듈 생성"""
        if repository is None:
            repository = InMemoryResearchRepository()
        
        if service is None:
            service = ResearchApplicationService(repository)
        
        return ResearchFacade(service, repository) 
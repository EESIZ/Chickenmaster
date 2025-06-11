"""
연구개발(R&D) 모듈
치킨마스터 게임의 연구개발 시스템을 제공합니다.

@freeze v0.1.0
"""

from .facade import ResearchFacade
from .factory import ResearchModuleFactory

# 공개 API
__all__ = [
    "ResearchFacade",
    "ResearchModuleFactory",
    # 도메인 객체들도 외부에서 접근 가능하게
    "ResearchProject",
    "ResearchResult", 
    "ResearchType",
    "ResearchConfiguration"
]

# 편의를 위한 도메인 객체 재exports
from ..core.domain.research import (
    ResearchProject,
    ResearchResult,
    ResearchType,
    ResearchConfiguration
) 
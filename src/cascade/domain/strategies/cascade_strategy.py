from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.domain.cascade import CascadeNode


class ICascadeStrategy(ABC):
    """연쇄 효과 처리 전략 인터페이스"""

    @abstractmethod
    def process(self, node: CascadeNode) -> bool:
        """연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        pass


class DefaultCascadeStrategy(ICascadeStrategy):
    """기본 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """기본 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        return True


class EconomicCascadeStrategy(ICascadeStrategy):
    """경제 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """경제 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # TODO: 경제 효과 처리 로직 구현
        return True


class SocialCascadeStrategy(ICascadeStrategy):
    """사회 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """사회 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # TODO: 사회 효과 처리 로직 구현
        return True


class CulturalCascadeStrategy(ICascadeStrategy):
    """문화 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """문화 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # TODO: 문화 효과 처리 로직 구현
        return True


class TechnologicalCascadeStrategy(ICascadeStrategy):
    """기술 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """기술 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # TODO: 기술 효과 처리 로직 구현
        return True


class EnvironmentalCascadeStrategy(ICascadeStrategy):
    """환경 연쇄 효과 처리 전략"""

    def process(self, node: CascadeNode) -> bool:
        """환경 연쇄 효과 처리

        Args:
            node: 처리할 연쇄 노드

        Returns:
            bool: 처리 성공 여부
        """
        # TODO: 환경 효과 처리 로직 구현
        return True

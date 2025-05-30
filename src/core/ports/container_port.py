"""
의존성 주입 컨테이너 인터페이스.

이 모듈은 의존성 주입을 위한 컨테이너 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional, TypeVar

T = TypeVar("T")


# @freeze v0.1.0
class IServiceContainer(ABC):
    """
    의존성 주입 컨테이너 인터페이스.

    이 인터페이스는 서비스 등록 및 조회, 의존성 검증 등의 기능을 제공합니다.
    """

    @abstractmethod
    def register_singleton(self, service_type: type[T], implementation: Optional[T] = None) -> None:
        """
        싱글톤 서비스를 등록합니다.

        Args:
            service_type: 서비스 타입 (인터페이스)
            implementation: 구현체 인스턴스 (없으면 자동 생성)

        Raises:
            ValueError: 이미 등록된 서비스인 경우
        """
        pass

    @abstractmethod
    def register_transient(self, service_type: type[T], implementation_type: type[T]) -> None:
        """
        트랜지언트 서비스를 등록합니다.

        Args:
            service_type: 서비스 타입 (인터페이스)
            implementation_type: 구현체 타입

        Raises:
            ValueError: 이미 등록된 서비스인 경우
        """
        pass

    @abstractmethod
    def get(self, service_type: type[T]) -> T:
        """
        서비스 인스턴스를 조회합니다.

        Args:
            service_type: 서비스 타입 (인터페이스)

        Returns:
            서비스 인스턴스

        Raises:
            KeyError: 등록되지 않은 서비스인 경우
        """
        pass

    @abstractmethod
    def has(self, service_type: type[T]) -> bool:
        """
        서비스 등록 여부를 확인합니다.

        Args:
            service_type: 서비스 타입 (인터페이스)

        Returns:
            등록되어 있으면 True, 아니면 False
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 등록된 서비스를 초기화합니다."""
        pass

    @abstractmethod
    def validate_dependencies(self) -> bool:
        """
        의존성 순환 참조를 검증합니다.

        Returns:
            순환 참조가 없으면 True, 있으면 False
        """
        pass

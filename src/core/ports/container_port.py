"""
의존성 주입 컨테이너 인터페이스.

이 모듈은 의존성 주입을 위한 컨테이너 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import TypeVar
from collections.abc import Callable

T = TypeVar("T")


# @freeze v0.1.0
class IServiceContainer(ABC):
    """의존성 주입 컨테이너 인터페이스"""

    @abstractmethod
    def register_singleton(
        self, interface: type[T], implementation: Callable[["IServiceContainer"], T]
    ) -> None:
        """싱글톤 서비스 등록

        Args:
            interface: 서비스 인터페이스 타입
            implementation: 구현체 팩토리 함수

        Raises:
            ValueError: 이미 등록된 서비스인 경우
        """
        pass

    @abstractmethod
    def register_transient(
        self, interface: type[T], implementation: Callable[["IServiceContainer"], T]
    ) -> None:
        """트랜지언트 서비스 등록

        Args:
            interface: 서비스 인터페이스 타입
            implementation: 구현체 팩토리 함수

        Raises:
            ValueError: 이미 등록된 서비스인 경우
        """
        pass

    @abstractmethod
    def get(self, interface: type[T]) -> T:
        """서비스 인스턴스 조회

        Args:
            interface: 서비스 인터페이스 타입

        Returns:
            서비스 인스턴스

        Raises:
            KeyError: 등록되지 않은 서비스인 경우
        """
        pass

    @abstractmethod
    def has(self, interface: type[T]) -> bool:
        """서비스 등록 여부 확인

        Args:
            interface: 서비스 인터페이스 타입

        Returns:
            등록되어 있으면 True, 아니면 False
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """모든 등록된 서비스를 초기화합니다."""
        pass

    @abstractmethod
    def validate_dependencies(self) -> dict[str, list[str]]:
        """의존성 순환 참조 검증

        Returns:
            의존성 그래프 정보
        """
        pass

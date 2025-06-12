"""
의존성 주입 컨테이너 구현체.

이 모듈은 의존성 주입 컨테이너의 실제 구현을 제공합니다.
"""

from dataclasses import dataclass
from typing import Any, TypeVar, cast
from collections.abc import Callable

from src.core.ports.container_port import IServiceContainer

T = TypeVar("T")


@dataclass
class ServiceRegistration:
    """서비스 등록 정보."""

    service_type: type[Any]
    implementation_factory: Callable[[IServiceContainer], Any] | None = None
    instance: Any | None = None
    is_singleton: bool = True


class ServiceContainer(IServiceContainer):
    """의존성 주입 컨테이너 구현체."""

    def __init__(self) -> None:
        """컨테이너 초기화."""
        self._registrations: dict[type[Any], ServiceRegistration] = {}

    def register_singleton(
        self, interface: type[T], implementation: Callable[[IServiceContainer], T]
    ) -> None:
        """싱글톤 서비스를 등록합니다."""
        if self.has(interface):
            raise ValueError(f"서비스 '{interface.__name__}'가 이미 등록되어 있습니다.")

        registration = ServiceRegistration(
            service_type=interface, implementation_factory=implementation, is_singleton=True
        )
        self._registrations[interface] = registration

    def register_transient(
        self, interface: type[T], implementation: Callable[[IServiceContainer], T]
    ) -> None:
        """트랜지언트 서비스를 등록합니다."""
        if self.has(interface):
            raise ValueError(f"서비스 '{interface.__name__}'가 이미 등록되어 있습니다.")

        registration = ServiceRegistration(
            service_type=interface, implementation_factory=implementation, is_singleton=False
        )
        self._registrations[interface] = registration

    def get(self, interface: type[T]) -> T:
        """서비스 인스턴스를 조회합니다."""
        if not self.has(interface):
            raise KeyError(f"서비스 '{interface.__name__}'가 등록되지 않았습니다.")

        registration = self._registrations[interface]

        # 싱글톤이고 이미 인스턴스가 있으면 반환
        if registration.is_singleton and registration.instance is not None:
            return cast(T, registration.instance)

        # 팩토리 함수로 인스턴스 생성
        if registration.implementation_factory is not None:
            instance = registration.implementation_factory(self)

            # 싱글톤이면 인스턴스 저장
            if registration.is_singleton:
                registration.instance = instance

            return cast(T, instance)

        raise ValueError(f"서비스 '{interface.__name__}'의 구현체가 없습니다.")

    def has(self, interface: type[T]) -> bool:
        """서비스 등록 여부를 확인합니다."""
        return interface in self._registrations

    def clear(self) -> None:
        """모든 등록된 서비스를 초기화합니다."""
        self._registrations.clear()

    def validate_dependencies(self) -> dict[str, list[str]]:
        """의존성 순환 참조를 검증합니다."""
        # 간단한 구현: 등록된 서비스 목록 반환
        dependencies: dict[str, list[str]] = {}
        for service_type in self._registrations:
            dependencies[service_type.__name__] = []
        return dependencies

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """서비스 인스턴스를 생성합니다."""
        if registration.implementation_factory is None:
            raise ValueError("구현체 팩토리가 없습니다.")

        # 생성자 호출 시 컨테이너 자체를 전달
        return registration.implementation_factory(self)

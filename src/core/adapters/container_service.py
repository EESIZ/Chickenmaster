"""
의존성 주입 컨테이너 구현체.

이 모듈은 의존성 주입 컨테이너의 실제 구현을 제공합니다.
"""

from dataclasses import dataclass
from typing import Any, Dict, Set, Type, TypeVar

from src.core.ports.container_port import IServiceContainer

T = TypeVar('T')


@dataclass
class ServiceRegistration:
    """서비스 등록 정보."""

    service_type: Type
    implementation_type: Type | None = None
    instance: Any | None = None
    is_singleton: bool = True


class ServiceContainer(IServiceContainer):
    """의존성 주입 컨테이너 구현체."""

    def __init__(self) -> None:
        """컨테이너 초기화."""
        self._registrations: Dict[Type, ServiceRegistration] = {}

    def register_singleton(
        self, 
        service_type: Type[T], 
        implementation: T | None = None
    ) -> None:
        """싱글톤 서비스를 등록합니다."""
        if self.has(service_type):
            raise ValueError(f"서비스 '{service_type.__name__}'가 이미 등록되어 있습니다.")

        registration = ServiceRegistration(
            service_type=service_type,
            instance=implementation,
            is_singleton=True
        )
        self._registrations[service_type] = registration

    def register_transient(
        self, 
        service_type: Type[T], 
        implementation_type: Type[T]
    ) -> None:
        """트랜지언트 서비스를 등록합니다."""
        if self.has(service_type):
            raise ValueError(f"서비스 '{service_type.__name__}'가 이미 등록되어 있습니다.")

        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            is_singleton=False
        )
        self._registrations[service_type] = registration

    def get(self, service_type: Type[T]) -> T:
        """서비스 인스턴스를 조회합니다."""
        if not self.has(service_type):
            raise KeyError(f"서비스 '{service_type.__name__}'가 등록되지 않았습니다.")

        registration = self._registrations[service_type]

        # 싱글톤이고 인스턴스가 있는 경우
        if registration.is_singleton and registration.instance is not None:
            return registration.instance

        # 트랜지언트이거나 싱글톤이지만 인스턴스가 없는 경우
        if registration.implementation_type is not None:
            instance = registration.implementation_type()
            if registration.is_singleton:
                registration.instance = instance
            return instance

        # 구현체가 없는 경우
        raise ValueError(f"서비스 '{service_type.__name__}'의 구현체가 없습니다.")

    def has(self, service_type: Type[T]) -> bool:
        """서비스 등록 여부를 확인합니다."""
        return service_type in self._registrations

    def clear(self) -> None:
        """모든 등록된 서비스를 초기화합니다."""
        self._registrations.clear()

    def validate_dependencies(self) -> bool:
        """의존성 순환 참조를 검증합니다."""
        visited: Set[Type] = set()
        path: Set[Type] = set()

        def has_cycle(service_type: Type) -> bool:
            if service_type in path:
                return True

            if service_type in visited:
                return False

            visited.add(service_type)
            path.add(service_type)

            registration = self._registrations.get(service_type)
            if registration and registration.implementation_type:
                # 구현체의 __init__ 메서드의 파라미터 타입들을 검사
                init_params = registration.implementation_type.__init__.__annotations__
                for param_type in init_params.values():
                    if param_type in self._registrations and has_cycle(param_type):
                        return True

            path.remove(service_type)
            return False

        # 모든 등록된 서비스에 대해 순환 참조 검사
        for service_type in self._registrations:
            if has_cycle(service_type):
                return False

        return True

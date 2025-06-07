#!/usr/bin/env python3
"""
헥사고날 아키텍처 구조 검증 스크립트
레이어 의존성, import 방향, 구조 위반, 패키지 경계 침범 등을 검증합니다.
"""

import os
import sys
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass(frozen=True)
class ImportInfo:
    """임포트 정보"""

    source_module: str
    imported_module: str
    line_number: int


@dataclass
class ValidationResult:
    """검증 결과"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


class HexagonalArchitectureValidator:
    """헥사고날 아키텍처 검증기"""

    def __init__(self, project_root: str) -> None:
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.core_dir = self.src_dir / "core"
        self.adapters_dir = self.src_dir / "adapters"
        self.events_dir = self.src_dir / "events"
        self.metrics_dir = self.src_dir / "metrics"
        self.economy_dir = self.src_dir / "economy"

        # 레이어 정의
        self.layers = {
            "core.domain": "도메인",
            "core.ports": "포트",
            "core.application": "애플리케이션",
            "adapters": "어댑터",
            "events": "이벤트",
            "metrics": "지표",
            "economy": "경제",
        }

        # 허용된 의존성 방향
        self.allowed_dependencies = {
            "도메인": [],  # 도메인은 어떤 레이어에도 의존하지 않음
            "포트": ["도메인"],  # 포트는 도메인에만 의존
            "애플리케이션": ["도메인", "포트"],  # 애플리케이션은 도메인과 포트에 의존
            "어댑터": ["도메인", "포트", "애플리케이션"],  # 어댑터는 도메인, 포트, 애플리케이션에 의존
            "이벤트": ["도메인"],  # 이벤트는 도메인에만 의존
            "지표": ["도메인"],  # 지표는 도메인에만 의존
            "경제": ["도메인"],  # 경제는 도메인에만 의존
        }

    def _get_layer(self, module_name: str) -> str | None:
        """모듈 이름으로 레이어 반환"""
        for layer_prefix, layer_name in self.layers.items():
            if module_name.startswith(layer_prefix):
                return layer_name
        return None

    def extract_imports(self, file_path: Path) -> list[ImportInfo]:
        """파일에서 임포트 정보 추출"""
        imports = []
        with open(file_path, encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                print(f"구문 오류: {file_path}")
                return []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(
                        ImportInfo(
                            source_module=self._get_module_name(file_path),
                            imported_module=name.name,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:  # None 체크 추가
                    module_name = node.module
                    for name in node.names:
                        imports.append(
                            ImportInfo(
                                source_module=self._get_module_name(file_path),
                                imported_module=f"{module_name}.{name.name}",
                                line_number=node.lineno,
                            )
                        )

        return imports

    def _get_module_name(self, file_path: Path) -> str:
        """파일 경로에서 모듈 이름 추출"""
        rel_path = file_path.relative_to(self.project_root)
        module_path = str(rel_path).replace("/", ".").replace("\\", ".")
        if module_path.endswith(".py"):
            module_path = module_path[:-3]
        return module_path

    def collect_all_imports(self) -> list[ImportInfo]:
        """모든 임포트 정보 수집"""
        all_imports = []

        # src 디렉토리 내 모든 Python 파일 검사
        for root, _, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    all_imports.extend(self.extract_imports(file_path))

        return all_imports

    def validate_dependencies(self) -> ValidationResult:
        """의존성 방향 검증"""
        errors: list[str] = []
        warnings: list[str] = []

        imports = self.collect_all_imports()

        for import_info in imports:
            source_layer = self._get_layer(import_info.source_module)
            imported_layer = self._get_layer(import_info.imported_module)

            # 레이어 의존성 검증
            if source_layer and imported_layer:
                allowed_deps = self.allowed_dependencies.get(source_layer, [])
                # typing.cast를 사용하여 타입 명시
                allowed_deps_typed = cast(list[str], allowed_deps)
                if (
                    imported_layer not in allowed_deps_typed
                    and source_layer != imported_layer
                ):
                    errors.append(
                        f"의존성 방향 위반: {import_info.source_module} -> {import_info.imported_module} "
                        f"(라인 {import_info.line_number})"
                    )

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_freeze_tags(self) -> ValidationResult:
        """Freeze Tag 검증"""
        errors: list[str] = []
        warnings: list[str] = []

        # 포트 인터페이스 파일 검사
        ports_dir = self.core_dir / "ports"
        if ports_dir.exists() and ports_dir.is_dir():
            for file_path in ports_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if "@freeze" not in content:
                        warnings.append(
                            f"포트 인터페이스에 @freeze 태그 누락: {file_path.relative_to(self.project_root)}"
                        )

        return ValidationResult(
            is_valid=True, errors=errors, warnings=warnings  # 경고만 있고 오류는 없음
        )

    def validate_domain_immutability(self) -> ValidationResult:
        """도메인 객체 불변성 검증"""
        errors: list[str] = []
        warnings: list[str] = []

        domain_dir = self.core_dir / "domain"
        if domain_dir.exists() and domain_dir.is_dir():
            for file_path in domain_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if "@dataclass" in content and "frozen=True" not in content:
                        errors.append(
                            f"도메인 객체 불변성 위반: {file_path.relative_to(self.project_root)}"
                        )

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_all(self) -> list[ValidationResult]:
        """모든 검증 실행"""
        results = []

        print("\n🔍 헥사고날 아키텍처 검증 시작\n")

        print("1️⃣ 의존성 방향 검증")
        results.append(self.validate_dependencies())

        print("2️⃣ Freeze Tag 검증")
        results.append(self.validate_freeze_tags())

        print("3️⃣ 도메인 객체 불변성 검증")
        results.append(self.validate_domain_immutability())

        return results


def print_validation_results(results: list[ValidationResult]) -> None:
    """검증 결과 출력"""
    all_valid = True

    for result in results:
        if not result.is_valid:
            all_valid = False
            print("  상태: ❌ 실패")
        else:
            print("  상태: ✅ 성공")

        if result.errors:
            print("\n  오류:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("\n  경고:")
            for warning in result.warnings:
                print(f"  - {warning}")

        print("\n" + "-" * 50 + "\n")

    print("최종 결과:", "✅ 성공" if all_valid else "❌ 실패")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    validator = HexagonalArchitectureValidator(project_root)
    results = validator.validate_all()
    print_validation_results(results)
    
    # 성공 여부 직접 계산
    all_valid = all(result.is_valid for result in results)
    sys.exit(0 if all_valid else 1)

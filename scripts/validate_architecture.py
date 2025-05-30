#!/usr/bin/env python3
"""
헥사고날 아키텍처 구조 검증 스크립트
레이어 의존성, import 방향, 구조 위반, 패키지 경계 침범 등을 검증합니다.
"""

import os
import re
import sys
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportInfo:
    """임포트 정보"""
    source_module: str
    imported_module: str
    line_number: int
    is_from_import: bool


@dataclass(frozen=True)
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: list[str]
    warnings: list[str]


class HexagonalArchitectureValidator:
    """헥사고날 아키텍처 검증기"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.core_dir = self.src_dir / "core"
        self.adapters_dir = self.src_dir / "adapters"
        self.application_dir = self.src_dir / "application"
        
        # 레이어별 허용된 의존성 방향
        self.allowed_dependencies = {
            "core.domain": [],  # 도메인은 어디에도 의존하지 않음
            "core.ports": ["core.domain"],  # 포트는 도메인에만 의존
            "adapters": ["core.domain", "core.ports"],  # 어댑터는 코어에만 의존
            "application": ["core.domain", "core.ports", "adapters"],  # 애플리케이션은 모두에 의존 가능
        }
        
        # Freeze Tag 패턴
        self.freeze_tag_pattern = r"@freeze\s+v\d+\.\d+\.\d+"
    
    def validate_project_structure(self) -> ValidationResult:
        """프로젝트 구조 검증"""
        errors = []
        warnings = []
        
        # 필수 디렉토리 검증
        required_dirs = [
            self.src_dir,
            self.core_dir,
            self.core_dir / "domain",
            self.core_dir / "ports",
            self.adapters_dir,
            self.adapters_dir / "services",
            self.adapters_dir / "storage",
            self.application_dir
        ]
        
        for directory in required_dirs:
            if not directory.exists() or not directory.is_dir():
                errors.append(f"필수 디렉토리가 없음: {directory.relative_to(self.project_root)}")
        
        # __init__.py 파일 검증
        for directory in required_dirs:
            if directory.exists() and directory.is_dir():
                init_file = directory / "__init__.py"
                if not init_file.exists():
                    warnings.append(f"__init__.py 파일이 없음: {init_file.relative_to(self.project_root)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def extract_imports(self, file_path: Path) -> list[ImportInfo]:
        """파일에서 import 문 추출"""
        imports = []
        
        try:
            with open(file_path, encoding='utf-8') as f:
                file_content = f.read()
            
            module_name = str(file_path.relative_to(self.src_dir)).replace('/', '.').replace('\\', '.').replace('.py', '')
            
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(ImportInfo(
                            source_module=module_name,
                            imported_module=name.name,
                            line_number=node.lineno,
                            is_from_import=False
                        ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module is not None:
                        for name in node.names:
                            full_import = f"{node.module}.{name.name}" if node.module else name.name
                            imports.append(ImportInfo(
                                source_module=module_name,
                                imported_module=full_import,
                                line_number=node.lineno,
                                is_from_import=True
                            ))
        except Exception as e:
            print(f"파일 분석 오류 {file_path}: {e}")
        
        return imports
    
    def collect_all_imports(self) -> list[ImportInfo]:
        """프로젝트 전체 import 수집"""
        all_imports = []
        
        for root, _, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    all_imports.extend(self.extract_imports(file_path))
        
        return all_imports
    
    def validate_dependencies(self) -> ValidationResult:
        """의존성 방향 검증"""
        errors = []
        warnings = []
        
        imports = self.collect_all_imports()
        
        for import_info in imports:
            source_layer = self._get_layer(import_info.source_module)
            imported_module = import_info.imported_module
            
            # 내부 모듈만 검사 (외부 라이브러리 제외)
            if imported_module.startswith('src.'):
                imported_module = imported_module[4:]  # 'src.' 접두사 제거
            elif not any(imported_module.startswith(prefix) for prefix in ['core.', 'adapters.', 'application.']):
                continue
            
            imported_layer = self._get_layer(imported_module)
            
            # 레이어 의존성 검증
            if source_layer and imported_layer:
                if imported_layer not in self.allowed_dependencies.get(source_layer, []) and source_layer != imported_layer:
                    errors.append(
                        f"의존성 방향 위반: {import_info.source_module} -> {imported_module} "
                        f"(라인 {import_info.line_number})"
                    )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_freeze_tags(self) -> ValidationResult:
        """Freeze Tag 검증"""
        errors = []
        warnings = []
        
        # 포트 인터페이스 파일 검사
        ports_dir = self.core_dir / "ports"
        if ports_dir.exists() and ports_dir.is_dir():
            for file_path in ports_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                
                # 인터페이스 클래스 찾기
                interface_pattern = r"class\s+I[A-Z][a-zA-Z0-9]*\s*\([^)]*\):"
                interfaces = re.findall(interface_pattern, content)
                
                # Freeze Tag 검사
                has_freeze_tag = bool(re.search(self.freeze_tag_pattern, content))
                
                if interfaces and not has_freeze_tag:
                    warnings.append(f"Freeze Tag 없음: {file_path.relative_to(self.project_root)}")
        
        return ValidationResult(
            is_valid=True,  # 경고만 있고 오류는 없음
            errors=errors,
            warnings=warnings
        )
    
    def validate_domain_immutability(self) -> ValidationResult:
        """도메인 객체 불변성 검증"""
        errors = []
        warnings = []
        
        domain_dir = self.core_dir / "domain"
        if domain_dir.exists() and domain_dir.is_dir():
            for file_path in domain_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                
                # dataclass 사용 확인
                has_dataclass = "@dataclass" in content
                
                # frozen=True 확인
                has_frozen = "@dataclass(frozen=True)" in content or "@dataclass(.*frozen=True.*)" in content
                
                # 클래스 찾기
                class_pattern = r"class\s+([A-Z][a-zA-Z0-9]*)\s*\([^)]*\):"
                classes = re.findall(class_pattern, content)
                
                if classes and not has_dataclass:
                    errors.append(f"@dataclass 없음: {file_path.relative_to(self.project_root)}")
                
                if has_dataclass and not has_frozen:
                    errors.append(f"frozen=True 없음: {file_path.relative_to(self.project_root)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_all(self) -> dict[str, ValidationResult]:
        """모든 검증 실행"""
        return {
            "project_structure": self.validate_project_structure(),
            "dependencies": self.validate_dependencies(),
            "freeze_tags": self.validate_freeze_tags(),
            "domain_immutability": self.validate_domain_immutability()
        }
    
    def _get_layer(self, module_name: str) -> str | None:
        """모듈 이름에서 레이어 추출"""
        if module_name.startswith('core.domain'):
            return "core.domain"
        elif module_name.startswith('core.ports'):
            return "core.ports"
        elif module_name.startswith('adapters'):
            return "adapters"
        elif module_name.startswith('application'):
            return "application"
        return None


def print_validation_results(results: dict[str, ValidationResult]) -> None:
    """검증 결과 출력"""
    all_valid = True
    
    print("\n===== 헥사고날 아키텍처 검증 결과 =====\n")
    
    for category, result in results.items():
        print(f"## {category}")
        
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
    
    return all_valid


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    validator = HexagonalArchitectureValidator(project_root)
    results = validator.validate_all()
    success = print_validation_results(results)
    
    sys.exit(0 if success else 1)

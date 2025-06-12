#!/usr/bin/env python3
"""
🕵️ 코드베이스 분석 도구 🕵️
전체 프로젝트에서 사용되지 않는 모듈, 죽은 코드, 고아 파일들을 찾습니다.

분석 항목:
1. 모든 Python 파일 스캔
2. import 의존성 분석
3. 사용되지 않는 모듈 식별
4. 빈 파일 또는 거의 빈 파일 찾기
5. 순환 의존성 검사
"""

import os
import ast
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict


class CodebaseAnalyzer:
    """코드베이스 분석기"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.python_files: List[Path] = []
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.imported_by: Dict[str, Set[str]] = defaultdict(set)
        self.file_sizes: Dict[str, int] = {}
        self.file_lines: Dict[str, int] = {}
        
        print(f"🔍 코드베이스 분석 시작: {self.root_path.absolute()}")
        
    def scan_python_files(self):
        """모든 Python 파일 스캔"""
        print("\n📂 Python 파일 스캔 중...")
        
        for file_path in self.root_path.rglob("*.py"):
            # __pycache__ 디렉토리 제외
            if "__pycache__" in str(file_path):
                continue
                
            self.python_files.append(file_path)
            
            # 파일 크기와 줄 수 계산
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.count('\n') + 1
                    
                self.file_sizes[str(file_path)] = len(content)
                self.file_lines[str(file_path)] = lines
                
            except Exception as e:
                print(f"⚠️  파일 읽기 실패: {file_path} - {e}")
        
        print(f"✓ 총 {len(self.python_files)}개 Python 파일 발견")
        
    def analyze_imports(self):
        """import 의존성 분석"""
        print("\n🔗 import 의존성 분석 중...")
        
        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_module = alias.name
                            self.imports[relative_path].add(imported_module)
                            self.imported_by[imported_module].add(relative_path)
                            
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_module = node.module
                            self.imports[relative_path].add(imported_module)
                            self.imported_by[imported_module].add(relative_path)
                            
            except Exception as e:
                print(f"⚠️  AST 파싱 실패: {file_path} - {e}")
        
        print(f"✓ {len(self.imports)}개 파일의 import 관계 분석 완료")
        
    def find_unused_modules(self) -> List[str]:
        """사용되지 않는 모듈 찾기"""
        print("\n🗑️  사용되지 않는 모듈 찾는 중...")
        
        unused_modules = []
        
        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            
            # __init__.py 파일들은 제외 (패키지 정의용)
            if relative_path.endswith("__init__.py"):
                continue
                
            # main.py, test 파일들은 제외 (엔트리포인트)
            if any(exclude in relative_path for exclude in ["main.py", "test_", "chicken_mud_game.py", "analyze_"]):
                continue
            
            # 모듈명 추출 (확장자 제거 및 경로를 점으로 변환)
            module_name = relative_path.replace(".py", "").replace("/", ".").replace("\\", ".")
            
            # 이 모듈을 import하는 다른 파일이 있는지 확인
            is_used = False
            
            # 직접 import되는지 확인
            if module_name in self.imported_by and self.imported_by[module_name]:
                is_used = True
            
            # 부분 경로로 import되는지 확인 (예: src.core.domain.game_state)
            if not is_used:
                for imported_module in self.imported_by.keys():
                    if module_name in imported_module or imported_module in module_name:
                        if self.imported_by[imported_module]:
                            is_used = True
                            break
            
            if not is_used:
                unused_modules.append(relative_path)
        
        return unused_modules
        
    def find_empty_files(self) -> List[Tuple[str, int, int]]:
        """빈 파일 또는 거의 빈 파일 찾기"""
        print("\n📝 빈 파일들 찾는 중...")
        
        empty_files = []
        
        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            file_size = self.file_sizes[str(file_path)]
            line_count = self.file_lines[str(file_path)]
            
            # 50바이트 이하이거나 5줄 이하인 파일들
            if file_size <= 50 or line_count <= 5:
                empty_files.append((relative_path, file_size, line_count))
                
        return empty_files
        
    def find_large_files(self) -> List[Tuple[str, int, int]]:
        """큰 파일들 찾기 (리팩토링 후보)"""
        print("\n📈 큰 파일들 찾는 중...")
        
        large_files = []
        
        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            file_size = self.file_sizes[str(file_path)]
            line_count = self.file_lines[str(file_path)]
            
            # 10KB 이상이거나 300줄 이상인 파일들
            if file_size >= 10000 or line_count >= 300:
                large_files.append((relative_path, file_size, line_count))
                
        return large_files
        
    def analyze_architecture_compliance(self) -> Dict[str, List[str]]:
        """헥사고널 아키텍처 준수 여부 분석"""
        print("\n🏗️  헥사고널 아키텍처 준수 여부 분석 중...")
        
        issues = {
            "domain_depends_on_adapters": [],
            "missing_ports": [],
            "adapter_without_port": []
        }
        
        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            
            # domain 파일이 adapters에 의존하는지 확인
            if "/domain/" in relative_path:
                imports = self.imports[relative_path]
                for imported_module in imports:
                    if "adapter" in imported_module.lower():
                        issues["domain_depends_on_adapters"].append(relative_path)
                        
            # ports 디렉토리가 있는지 확인
            if "/adapters/" in relative_path:
                module_dir = str(file_path.parent.parent)
                ports_dir = Path(module_dir) / "ports"
                if not ports_dir.exists():
                    issues["missing_ports"].append(relative_path)
        
        return issues
        
    def print_detailed_report(self):
        """상세 분석 리포트 출력"""
        print(f"\n{'='*80}")
        print(f"🕵️ 코드베이스 분석 상세 리포트")
        print(f"{'='*80}")
        
        # 파일 통계
        total_files = len(self.python_files)
        total_size = sum(self.file_sizes.values())
        total_lines = sum(self.file_lines.values())
        
        print(f"\n📊 전체 통계:")
        print(f"   📂 Python 파일: {total_files}개")
        print(f"   📏 총 크기: {total_size:,}바이트 ({total_size/1024:.1f}KB)")
        print(f"   📄 총 줄 수: {total_lines:,}줄")
        print(f"   📈 평균 파일 크기: {total_size/total_files:.0f}바이트")
        print(f"   📊 평균 줄 수: {total_lines/total_files:.1f}줄")
        
        # 사용되지 않는 모듈
        unused_modules = self.find_unused_modules()
        print(f"\n🗑️  사용되지 않는 모듈: {len(unused_modules)}개")
        for module in unused_modules:
            size = self.file_sizes[str(self.root_path / module)]
            lines = self.file_lines[str(self.root_path / module)]
            print(f"   ❌ {module} ({size}바이트, {lines}줄)")
            
        # 빈 파일들
        empty_files = self.find_empty_files()
        print(f"\n📝 빈 파일 또는 거의 빈 파일: {len(empty_files)}개")
        for file_path, size, lines in empty_files:
            print(f"   🔍 {file_path} ({size}바이트, {lines}줄)")
            
        # 큰 파일들
        large_files = self.find_large_files()
        print(f"\n📈 큰 파일들 (리팩토링 후보): {len(large_files)}개")
        for file_path, size, lines in sorted(large_files, key=lambda x: x[2], reverse=True):
            print(f"   🔥 {file_path} ({size:,}바이트, {lines}줄)")
            
        # 아키텍처 준수 여부
        arch_issues = self.analyze_architecture_compliance()
        print(f"\n🏗️  헥사고널 아키텍처 이슈:")
        
        if arch_issues["domain_depends_on_adapters"]:
            print(f"   ⚠️  Domain이 Adapter에 의존: {len(arch_issues['domain_depends_on_adapters'])}개")
            for issue in arch_issues["domain_depends_on_adapters"]:
                print(f"      - {issue}")
        else:
            print(f"   ✅ Domain 독립성 준수")
            
        if arch_issues["missing_ports"]:
            print(f"   ⚠️  Ports 디렉토리 누락: {len(arch_issues['missing_ports'])}개")
            for issue in arch_issues["missing_ports"]:
                print(f"      - {issue}")
        else:
            print(f"   ✅ Ports 구조 올바름")
            
        # 가장 많이 import되는 모듈들
        print(f"\n🔗 가장 많이 import되는 모듈들:")
        import_counts = [(module, len(importers)) for module, importers in self.imported_by.items() if importers]
        for module, count in sorted(import_counts, key=lambda x: x[1], reverse=True)[:10]:
            print(f"   📈 {module}: {count}번 import됨")
            
        # 추천 사항
        print(f"\n💡 추천 사항:")
        if unused_modules:
            print(f"   🗑️  {len(unused_modules)}개 사용되지 않는 모듈 제거 고려")
            
        if len(empty_files) > 5:
            print(f"   📝 {len(empty_files)}개 빈 파일들 정리 필요")
            
        if len(large_files) > 0:
            print(f"   ✂️  {len(large_files)}개 큰 파일들 분할 고려")
            
        total_issues = len(arch_issues["domain_depends_on_adapters"]) + len(arch_issues["missing_ports"])
        if total_issues > 0:
            print(f"   🏗️  {total_issues}개 아키텍처 이슈 수정 필요")
        else:
            print(f"   🎉 헥사고널 아키텍처 잘 준수됨!")
            
    def run_analysis(self):
        """전체 분석 실행"""
        self.scan_python_files()
        self.analyze_imports()
        self.print_detailed_report()


def main():
    """메인 함수"""
    print("🕵️ 코드베이스 분석 도구")
    print("사용되지 않는 모듈, 죽은 코드, 아키텍처 이슈를 찾습니다.")
    print("="*80)
    
    try:
        analyzer = CodebaseAnalyzer()
        analyzer.run_analysis()
    except Exception as e:
        print(f"💥 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
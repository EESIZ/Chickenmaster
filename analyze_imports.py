#!/usr/bin/env python3
"""
🔍 치킨마스터 Import 의존성 분석기 🔍

Python 파일들의 import 관계를 분석하고 순환 의존성을 찾아냅니다.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, Set, List, Optional
from collections import defaultdict, deque
import json

class ImportAnalyzer:
    """Import 의존성 분석기"""
    
    def __init__(self, root_path: str):
        """
        분석기 초기화
        
        Args:
            root_path: 프로젝트 루트 경로
        """
        self.root_path = Path(root_path)
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.files_analyzed: Set[str] = set()
        self.errors: List[str] = []
        
    def analyze_file(self, file_path: Path) -> Set[str]:
        """
        단일 Python 파일의 import 의존성 분석
        
        Args:
            file_path: 분석할 파일 경로
            
        Returns:
            해당 파일이 의존하는 모듈들의 집합
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST로 파싱
            tree = ast.parse(content, filename=str(file_path))
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        # from x.y import z 형태도 x.y 의존성으로 간주
                        parts = node.module.split('.')
                        for i in range(1, len(parts) + 1):
                            imports.add('.'.join(parts[:i]))
            
            return imports
            
        except Exception as e:
            error_msg = f"❌ 파일 분석 실패 {file_path}: {e}"
            self.errors.append(error_msg)
            print(error_msg)
            return set()
    
    def get_module_name(self, file_path: Path) -> str:
        """
        파일 경로를 모듈명으로 변환
        
        Args:
            file_path: 파일 경로
            
        Returns:
            모듈명 (예: src.core.domain.game_state)
        """
        relative_path = file_path.relative_to(self.root_path)
        
        # __init__.py는 패키지명으로
        if relative_path.name == '__init__.py':
            parts = relative_path.parts[:-1]
        else:
            parts = relative_path.with_suffix('').parts
            
        return '.'.join(parts)
    
    def analyze_project(self) -> None:
        """프로젝트 전체 분석"""
        print(f"🔍 프로젝트 분석 시작: {self.root_path}")
        
        # 모든 Python 파일 찾기
        python_files = list(self.root_path.rglob('*.py'))
        print(f"📁 총 {len(python_files)}개 Python 파일 발견")
        
        # 각 파일 분석
        for file_path in python_files:
            # 가상환경, __pycache__ 등 제외
            if any(exclude in str(file_path) for exclude in ['venv', '__pycache__', '.env', 'build']):
                continue
                
            module_name = self.get_module_name(file_path)
            imports = self.analyze_file(file_path)
            
            # 프로젝트 내부 모듈만 필터링
            internal_imports = self._filter_internal_imports(imports)
            
            self.dependencies[module_name] = internal_imports
            self.files_analyzed.add(module_name)
            
            if internal_imports:
                print(f"📦 {module_name} → {internal_imports}")
    
    def _filter_internal_imports(self, imports: Set[str]) -> Set[str]:
        """
        내부 모듈만 필터링 (외부 라이브러리 제외)
        
        Args:
            imports: 모든 import 집합
            
        Returns:
            내부 모듈만 포함된 집합
        """
        internal = set()
        
        # 프로젝트 내부 패키지들
        internal_packages = {
            'src', 'web_prototype', 'backend', 'core', 'dev_tools', 
            'tests', 'examples', 'scripts', 'game_constants'
        }
        
        for imp in imports:
            # 상대 import (.) 처리
            if imp.startswith('.'):
                internal.add(imp)
            # 내부 패키지 확인
            elif any(imp.startswith(pkg) for pkg in internal_packages):
                internal.add(imp)
            # game_constants 같은 루트 모듈
            elif imp in ['game_constants', 'dialogue_manager']:
                internal.add(imp)
                
        return internal
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        순환 의존성 탐지 (DFS 기반)
        
        Returns:
            순환 경로들의 리스트
        """
        print("\n🔄 순환 의존성 탐지 중...")
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # 순환 발견!
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
                
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # 이 노드가 의존하는 모든 모듈 탐색
            for dependency in self.dependencies.get(node, set()):
                if dependency in self.files_analyzed:  # 내부 모듈만
                    dfs(dependency, path.copy())
            
            rec_stack.remove(node)
        
        # 모든 노드에서 DFS 시작
        for module in self.files_analyzed:
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def generate_dot_graph(self) -> str:
        """
        DOT 형식 그래프 생성
        
        Returns:
            DOT 형식 문자열
        """
        dot_lines = [
            'digraph ImportGraph {',
            '    rankdir=TB;',
            '    node [shape=box, style=filled, fontname="Arial"];',
            '    edge [fontname="Arial"];',
            ''
        ]
        
        # 노드 색상 지정
        colors = {
            'web_prototype': '#FF6B35',  # 오렌지
            'src.core': '#DDA0DD',       # 자주색  
            'src': '#87CEEB',            # 하늘색
            'backend': '#90EE90',        # 연두색
            'game_constants': '#FFD700'  # 금색
        }
        
        # 노드 정의
        for module in self.files_analyzed:
            color = '#F0F0F0'  # 기본 색상
            for prefix, node_color in colors.items():
                if module.startswith(prefix):
                    color = node_color
                    break
                    
            dot_lines.append(f'    "{module}" [fillcolor="{color}"];')
        
        dot_lines.append('')
        
        # 엣지 정의
        for module, deps in self.dependencies.items():
            for dep in deps:
                if dep in self.files_analyzed:
                    dot_lines.append(f'    "{module}" -> "{dep}";')
        
        dot_lines.append('}')
        return '\n'.join(dot_lines)
    
    def generate_report(self) -> str:
        """
        분석 보고서 생성
        
        Returns:
            마크다운 형식 보고서
        """
        cycles = self.find_circular_dependencies()
        
        report = [
            "# 🍗 치킨마스터 Import 의존성 분석 보고서",
            "",
            f"**분석 일시**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**분석된 파일 수**: {len(self.files_analyzed)}개",
            f"**의존성 관계 수**: {sum(len(deps) for deps in self.dependencies.values())}개",
            "",
        ]
        
        # 순환 의존성 보고
        if cycles:
            report.extend([
                "## ⚠️ 순환 의존성 발견!",
                "",
                f"**발견된 순환 경로**: {len(cycles)}개",
                ""
            ])
            
            for i, cycle in enumerate(cycles, 1):
                report.append(f"### 순환 경로 #{i}")
                report.append("```")
                for j, module in enumerate(cycle):
                    if j < len(cycle) - 1:
                        report.append(f"{module} →")
                    else:
                        report.append(f"{module}")
                report.append("```")
                report.append("")
                
        else:
            report.extend([
                "## ✅ 순환 의존성 없음",
                "",
                "프로젝트에서 순환 의존성이 발견되지 않았습니다!",
                ""
            ])
        
        # 모듈별 의존성 상세
        report.extend([
            "## 📊 모듈별 의존성 상세",
            ""
        ])
        
        for module in sorted(self.files_analyzed):
            deps = self.dependencies.get(module, set())
            if deps:
                report.append(f"### `{module}`")
                report.append(f"**의존성**: {len(deps)}개")
                report.append("")
                for dep in sorted(deps):
                    report.append(f"- `{dep}`")
                report.append("")
        
        # 에러 보고
        if self.errors:
            report.extend([
                "## ❌ 분석 중 발생한 오류",
                ""
            ])
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")
        
        return '\n'.join(report)


def main():
    """메인 실행 함수"""
    print("🍗 치킨마스터 Import 의존성 분석기 시작")
    
    # 현재 디렉토리를 프로젝트 루트로 사용
    root_path = Path.cwd()
    
    # 분석기 생성 및 실행
    analyzer = ImportAnalyzer(str(root_path))
    analyzer.analyze_project()
    
    # DOT 그래프 생성
    print("\n📊 DOT 그래프 생성 중...")
    dot_content = analyzer.generate_dot_graph()
    
    with open('import_graph_before.dot', 'w', encoding='utf-8') as f:
        f.write(dot_content)
    print("✅ import_graph_before.dot 생성 완료")
    
    # 보고서 생성
    print("\n📋 분석 보고서 생성 중...")
    report = analyzer.generate_report()
    
    with open('import_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✅ import_analysis_report.md 생성 완료")
    
    # 순환 의존성 확인
    cycles = analyzer.find_circular_dependencies()
    if cycles:
        print(f"\n⚠️ 순환 의존성 {len(cycles)}개 발견!")
        for i, cycle in enumerate(cycles, 1):
            print(f"  순환 #{i}: {' → '.join(cycle)}")
    else:
        print("\n✅ 순환 의존성 없음!")
    
    print(f"\n🎯 분석 완료!")
    print(f"   - 분석된 모듈: {len(analyzer.files_analyzed)}개")
    print(f"   - 의존성 관계: {sum(len(deps) for deps in analyzer.dependencies.values())}개")
    print(f"   - 순환 의존성: {len(cycles)}개")


if __name__ == "__main__":
    main() 
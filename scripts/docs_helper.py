#!/usr/bin/env python3
"""
문서화 도우미 스크립트

이 스크립트는 Chicken-RNG 프로젝트의 문서화 작업을 도와줍니다.
- 새 ADR 생성
- 문서 링크 검증
- 문서 목록 업데이트
- 문서 통계 생성
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
import re

# 프로젝트 루트 찾기
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ADR_DIR = DOCS_DIR / "adr"


def create_new_adr(title: str, author: str) -> Path:
    """새로운 ADR 파일을 생성합니다."""
    
    # 다음 ADR 번호 찾기
    existing_adrs = list(ADR_DIR.glob("*.md"))
    adr_numbers = []
    
    for adr_file in existing_adrs:
        if adr_file.name.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            try:
                number = int(adr_file.name[:4])
                adr_numbers.append(number)
            except ValueError:
                continue
    
    next_number = max(adr_numbers, default=0) + 1
    
    # 파일명 생성 (title을 kebab-case로 변환)
    title_kebab = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    title_kebab = re.sub(r'\s+', '-', title_kebab)
    filename = f"{next_number:04d}-{title_kebab}.md"
    
    # 템플릿 로드
    template_path = ADR_DIR / "template.md"
    if not template_path.exists():
        print(f"❌ ADR 템플릿을 찾을 수 없습니다: {template_path}")
        sys.exit(1)
    
    template_content = template_path.read_text(encoding='utf-8')
    
    # 템플릿 값 치환
    content = template_content.replace("ADR-XXXX", f"ADR-{next_number:04d}")
    content = content.replace("[결정 제목]", title)
    content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
    content = content.replace("[작성자 이름] ([이메일 또는 GitHub 아이디])", author)
    
    # 새 ADR 파일 생성
    new_adr_path = ADR_DIR / filename
    new_adr_path.write_text(content, encoding='utf-8')
    
    print(f"✅ 새 ADR이 생성되었습니다: {new_adr_path}")
    return new_adr_path


def validate_doc_links() -> bool:
    """문서 내 링크들이 유효한지 검증합니다."""
    
    print("🔍 문서 링크 검증 중...")
    
    all_docs = list(DOCS_DIR.rglob("*.md"))
    broken_links = []
    
    for doc_path in all_docs:
        content = doc_path.read_text(encoding='utf-8')
        
        # 상대 링크 찾기 (markdown 링크와 HTML 링크)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        html_links = re.findall(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>', content)
        
        for text, link in markdown_links:
            if link.startswith(('http', 'https', 'mailto:')):
                continue  # 외부 링크는 건너뛰기
                
            # 상대 경로 링크 검증
            if link.startswith('./') or link.startswith('../') or not link.startswith('/'):
                target_path = (doc_path.parent / link).resolve()
            else:
                # 절대 경로 (프로젝트 루트 기준)
                target_path = (PROJECT_ROOT / link.lstrip('/')).resolve()
            
            if not target_path.exists():
                broken_links.append({
                    'file': doc_path.relative_to(PROJECT_ROOT),
                    'link': link,
                    'text': text
                })
    
    if broken_links:
        print("❌ 깨진 링크가 발견되었습니다:")
        for broken in broken_links:
            print(f"  📄 {broken['file']}: [{broken['text']}]({broken['link']})")
        return False
    else:
        print("✅ 모든 링크가 유효합니다!")
        return True


def generate_doc_stats() -> dict:
    """문서 통계를 생성합니다."""
    
    stats = {
        'total_docs': 0,
        'total_lines': 0,
        'total_words': 0,
        'by_category': {},
        'recent_updates': []
    }
    
    all_docs = list(DOCS_DIR.rglob("*.md"))
    
    for doc_path in all_docs:
        content = doc_path.read_text(encoding='utf-8')
        
        stats['total_docs'] += 1
        lines = len(content.splitlines())
        words = len(content.split())
        
        stats['total_lines'] += lines
        stats['total_words'] += words
        
        # 카테고리별 분류 (디렉토리 기준)
        category = doc_path.parent.name if doc_path.parent != DOCS_DIR else 'root'
        if category not in stats['by_category']:
            stats['by_category'][category] = {'docs': 0, 'lines': 0, 'words': 0}
        
        stats['by_category'][category]['docs'] += 1
        stats['by_category'][category]['lines'] += lines
        stats['by_category'][category]['words'] += words
        
        # 최근 수정된 파일 (Git 정보가 있다면)
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci', str(doc_path)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT, check=False
            )
            if result.returncode == 0:
                last_modified = result.stdout.strip()
                stats['recent_updates'].append({
                    'file': doc_path.relative_to(PROJECT_ROOT),
                    'last_modified': last_modified
                })
        except:
            pass  # Git 정보 없음
    
    # 최근 업데이트 정렬
    stats['recent_updates'].sort(key=lambda x: x['last_modified'], reverse=True)
    stats['recent_updates'] = stats['recent_updates'][:10]  # 최근 10개만
    
    return stats


def print_doc_stats():
    """문서 통계를 출력합니다."""
    
    print("📊 문서 통계 생성 중...")
    stats = generate_doc_stats()
    
    print("\n📚 전체 통계:")
    print(f"  📄 총 문서 수: {stats['total_docs']}")
    print(f"  📝 총 라인 수: {stats['total_lines']:,}")
    print(f"  📖 총 단어 수: {stats['total_words']:,}")
    
    print("\n📂 카테고리별 통계:")
    for category, data in stats['by_category'].items():
        print(f"  {category}: {data['docs']}개 문서, {data['lines']:,}줄, {data['words']:,}단어")
    
    if stats['recent_updates']:
        print("\n🕒 최근 업데이트된 문서 (상위 10개):")
        for update in stats['recent_updates']:
            print(f"  📄 {update['file']} - {update['last_modified'][:10]}")


def update_adr_index():
    """ADR 인덱스를 업데이트합니다."""
    
    print("🔄 ADR 인덱스 업데이트 중...")
    
    # 모든 ADR 파일 찾기
    adr_files = sorted([f for f in ADR_DIR.glob("*.md") if f.name != "README.md" and f.name != "template.md"])
    
    if not adr_files:
        print("⚠️  ADR 파일이 없습니다.")
        return
    
    # ADR 정보 수집
    adr_list = []
    for adr_file in adr_files:
        content = adr_file.read_text(encoding='utf-8')
        
        # 제목 추출
        title_match = re.search(r'^# ADR-(\d{4}): (.+)$', content, re.MULTILINE)
        if not title_match:
            continue
            
        number = title_match.group(1)
        title = title_match.group(2)
        
        # 상태 추출
        status_match = re.search(r'## 상태\s*\n\s*([🔄⭐✅❌♻️])\s*\*\*([^*]+)\*\*', content, re.MULTILINE)
        status_emoji = status_match.group(1) if status_match else "🔄"
        status_text = status_match.group(2) if status_match else "Unknown"
        
        # 날짜 추출
        date_match = re.search(r'## 날짜\s*\n\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
        date = date_match.group(1) if date_match else "Unknown"
        
        adr_list.append({
            'number': number,
            'title': title,
            'status_emoji': status_emoji,
            'status_text': status_text,
            'date': date,
            'filename': adr_file.name
        })
    
    # ADR README.md 업데이트
    readme_path = ADR_DIR / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        
        # 테이블 섹션 찾기 및 교체
        table_start = content.find("| 번호 | 제목 | 상태 | 날짜 |")
        if table_start != -1:
            table_end = content.find("\n\n", table_start)
            if table_end == -1:
                table_end = len(content)
            
            # 새 테이블 생성
            new_table_lines = [
                "| 번호 | 제목 | 상태 | 날짜 |",
                "|------|------|------|------|"
            ]
            
            for adr in adr_list:
                line = f"| [ADR-{adr['number']}]({adr['filename']}) | {adr['title']} | {adr['status_emoji']} {adr['status_text']} | {adr['date']} |"
                new_table_lines.append(line)
            
            new_table = "\n".join(new_table_lines)
            new_content = content[:table_start] + new_table + content[table_end:]
            
            readme_path.write_text(new_content, encoding='utf-8')
            print(f"✅ ADR 인덱스가 업데이트되었습니다: {len(adr_list)}개 ADR")
        else:
            print("⚠️  ADR README.md에서 테이블 섹션을 찾을 수 없습니다.")
    else:
        print("❌ ADR README.md 파일이 없습니다.")


def main():
    parser = argparse.ArgumentParser(description="Chicken-RNG 문서화 도우미")
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # ADR 생성 명령어
    adr_parser = subparsers.add_parser('new-adr', help='새 ADR 생성')
    adr_parser.add_argument('title', help='ADR 제목')
    adr_parser.add_argument('--author', default='개발팀', help='작성자 (기본값: 개발팀)')
    
    # 링크 검증 명령어
    subparsers.add_parser('validate-links', help='문서 링크 검증')
    
    # 통계 생성 명령어
    subparsers.add_parser('stats', help='문서 통계 출력')
    
    # ADR 인덱스 업데이트 명령어
    subparsers.add_parser('update-adr-index', help='ADR 인덱스 업데이트')
    
    # 전체 체크 명령어
    subparsers.add_parser('check-all', help='모든 검증 실행')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # docs 디렉토리 확인
    if not DOCS_DIR.exists():
        print(f"❌ docs 디렉토리를 찾을 수 없습니다: {DOCS_DIR}")
        sys.exit(1)
    
    # ADR 디렉토리 확인/생성
    if not ADR_DIR.exists():
        ADR_DIR.mkdir(parents=True)
        print(f"✅ ADR 디렉토리가 생성되었습니다: {ADR_DIR}")
    
    if args.command == 'new-adr':
        create_new_adr(args.title, args.author)
        update_adr_index()
        
    elif args.command == 'validate-links':
        valid = validate_doc_links()
        sys.exit(0 if valid else 1)
        
    elif args.command == 'stats':
        print_doc_stats()
        
    elif args.command == 'update-adr-index':
        update_adr_index()
        
    elif args.command == 'check-all':
        print("🔍 전체 문서 검증 시작...\n")
        
        # 1. 링크 검증
        links_valid = validate_doc_links()
        
        # 2. ADR 인덱스 업데이트
        print("\n" + "="*50)
        update_adr_index()
        
        # 3. 통계 출력
        print("\n" + "="*50)
        print_doc_stats()
        
        print("\n" + "="*50)
        if links_valid:
            print("✅ 모든 검증이 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 문제가 발견되었습니다. 위의 내용을 확인해주세요.")
            sys.exit(1)


if __name__ == "__main__":
    main() 
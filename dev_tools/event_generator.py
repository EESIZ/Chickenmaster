"""
파일: dev_tools/event_generator.py
목적: LLM을 사용한 이벤트 대량 생성 도구
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dev_tools.config import Config

class EventGenerator:
    def __init__(self):
        """
        API 키는 Config 클래스에서 자동 로드
        """
        self.api_key = Config.get_api_key()
        if not self.api_key:
            raise ValueError("API 키가 설정되지 않았습니다. config.py 실행하여 확인하세요.")
        
        # Anthropic 클라이언트 초기화
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic 패키지가 설치되지 않았습니다. pip install anthropic 명령으로 설치하세요.")
    
    def generate_events(
        self,
        category: str,
        count: int,
        seed: int = 42,
        variants: bool = False
    ) -> List[Dict[str, Any]]:
        """
        이벤트 생성 메인 메서드
        
        Args:
            category: EventCategory 값 중 하나
            count: 생성할 이벤트 수
            seed: 랜덤 시드
            variants: A/B 변형 생성 여부
            
        Returns:
            생성된 이벤트 딕셔너리 리스트
        """
        # 실제 구현 전 더미 데이터 반환
        dummy_events = []
        for i in range(count):
            event = {
                "id": f"{category}_{i:03d}",
                "category": category,
                "name_ko": f"더미 이벤트 {i+1}",
                "name_en": f"Dummy Event {i+1}",
                "text_ko": f"이것은 {category} 카테고리의 더미 이벤트입니다.",
                "text_en": f"This is a dummy event in the {category} category.",
                "conditions": ["reputation > 30", "day > 7"],
                "choices": [
                    {
                        "text_ko": "선택지 1",
                        "text_en": "Choice 1",
                        "effects": {"money": -500, "reputation": 10}
                    },
                    {
                        "text_ko": "선택지 2",
                        "text_en": "Choice 2",
                        "effects": {"money": 300, "reputation": -5}
                    },
                    {
                        "text_ko": "선택지 3",
                        "text_en": "Choice 3",
                        "effects": {"money": 0, "reputation": 0}
                    }
                ],
                "tags": ["spring", "rookie"],
                "probability": 0.1,
                "cooldown": 30,
                "seed": seed
            }
            
            if variants and i % 2 == 0:
                event["variant"] = "a"
            elif variants:
                event["variant"] = "b"
                
            dummy_events.append(event)
            
        return dummy_events
    
    def save_to_json(self, events: List[Dict], output_dir: str = "out"):
        """
        생성된 이벤트를 JSON으로 저장
        
        파일명 형식: raw_events_YYMMDD_HHMMSS.json
        """
        # 출력 디렉토리 확인 및 생성
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"raw_events_{timestamp}.json"
        
        # JSON 파일 저장
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"events": events}, f, ensure_ascii=False, indent=2)
            
        print(f"✅ {len(events)}개 이벤트가 {file_path}에 저장되었습니다.")
        return str(file_path)
    
    def create_prompt(self, category: str, count: int) -> str:
        """
        카테고리별 LLM 프롬프트 생성
        """
        # 기본 프롬프트 템플릿 (실제 구현 전 더미 반환)
        return f"한국 치킨집 경영 게임을 위한 {category} 카테고리의 이벤트 {count}개를 생성해주세요."

def main():
    # Config 검증
    if not Config.validate():
        return
    
    parser = argparse.ArgumentParser(description="치킨집 경영 게임 이벤트 생성기")
    parser.add_argument("--category", required=True, 
                       choices=["daily_routine", "crisis_events", 
                               "opportunity", "human_drama", "chain_scenario"],
                       help="이벤트 카테고리")
    parser.add_argument("--n", type=int, default=10,
                       help="생성할 이벤트 수 (기본값: 10)")
    parser.add_argument("--seed", type=int, default=42,
                       help="랜덤 시드 (기본값: 42)")
    parser.add_argument("--variants", action="store_true",
                       help="A/B 변형 생성 여부")
    parser.add_argument("--output", type=str, default="out",
                       help="출력 디렉토리 (기본값: out)")
    
    args = parser.parse_args()
    
    # 이벤트 생성기 초기화
    try:
        generator = EventGenerator()
        
        # 이벤트 생성
        print(f"🔄 {args.category} 카테고리의 이벤트 {args.n}개 생성 중...")
        events = generator.generate_events(
            category=args.category,
            count=args.n,
            seed=args.seed,
            variants=args.variants
        )
        
        # JSON 저장
        generator.save_to_json(events, args.output)
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()

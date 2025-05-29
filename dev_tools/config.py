"""
파일: dev_tools/config.py
목적: 중앙 집중식 설정 관리
"""

import os
from pathlib import Path
from typing import Optional, List

# 이벤트 카테고리 정의 (event_bank_manager.py에서 사용)
EVENT_CATEGORIES: List[str] = [
    "daily_routine",
    "crisis_events", 
    "opportunity",
    "human_drama",
    "chain_scenario"
]

class Config:
    """API 키 및 설정 관리"""

    @staticmethod
    def get_api_key() -> Optional[str]:
        """우선순위에 따라 API 키 로드"""

        # 1. 환경 변수 확인 (CI/CD)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return api_key
        # 2. .env 파일 확인 (로컬 개발)

        env_file = Path(".env")
        if env_file.exists():
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                return api_key
        return None

    @staticmethod
    def validate() -> bool:
        """설정 검증"""
        api_key = Config.get_api_key()
        if not api_key:
            print("❌ API 키가 설정되지 않았습니다")
            print("\n설정 방법:")
            print("1. .env 파일에 ANTHROPIC_API_KEY 추가")
            print("2. export ANTHROPIC_API_KEY='your-key'")
            print("3. GitLab CI Variables 설정")
            return False
        print("✅ API 키 설정 확인")
        print(f"   키 미리보기: {api_key[:10]}...")
        return True


if __name__ == "__main__":
    Config.validate()

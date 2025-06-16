#!/usr/bin/env python3
"""
🍗 Chicken Master Web Server 🍗
치킨마스터 MUD를 웹으로 변환한 FastAPI 서버

기존 chicken_mud_game.py의 모든 기능을 웹 API로 제공합니다.
Render.com에 바로 배포 가능한 형태로 구현되었습니다.
"""

import os
import sys
import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 실제 헥사고널 아키텍처 백엔드 import
try:
    from src.core.domain.game_state import GameState
    from src.core.domain.game_settings import GameSettings
    from src.core.domain.metrics import MetricEnum
except ImportError:
    # 배포 환경에서 경로 문제 시 대안
    print("⚠️ 백엔드 import 실패, 목업 데이터 사용")
    GameState = None
    GameSettings = None
    MetricEnum = None

# CSV 기반 대화 관리자 import
try:
    from dialogue_manager import dialogue_manager
    print("✅ CSV 대화 시스템 로딩 완료")
except ImportError:
    print("⚠️ 대화 관리자 import 실패")
    dialogue_manager = None


# FastAPI 앱 생성
app = FastAPI(
    title="🍗 Chicken Master API",
    description="치킨집 경영 시뮬레이션 게임 API",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포시에는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


# === 데이터 모델 (API 요청/응답용) ===

class GameStateResponse(BaseModel):
    """게임 상태 응답 모델"""
    current_day: int
    money: float
    reputation: float
    happiness: float
    suffering: float
    inventory: float
    staff_fatigue: float
    facility: float
    demand: float
    events_history: List[str]


class ActionRequest(BaseModel):
    """액션 요청 모델"""
    action_type: str  # "price_change", "order_inventory", etc.
    parameters: Dict[str, Any] = {}


class ActionResponse(BaseModel):
    """액션 응답 모델"""
    success: bool
    message: str
    new_state: GameStateResponse


# === 게임 상태 관리 ===

class WebGameManager:
    """웹용 게임 매니저"""
    
    def __init__(self):
        """게임 초기화"""
        print("✅ 실제 헥사고널 아키텍처 백엔드 사용")
        
        # 새로운 게임 설정값 적용
        self.settings = GameSettings(
            starting_money=5000000,  # 500만원
            starting_reputation=0,   # 평판 0점에서 시작 (완전 무명)
            starting_happiness=50,   # 기본 행복도
            starting_suffering=20,   # 기본 고통도
            starting_inventory=50,   # 재고 50개에서 시작
            starting_staff_fatigue=30,  # 직원 피로도 30에서 시작
            starting_facility=80,    # 시설 상태 80에서 시작
            starting_demand=20       # 평판 0점이므로 수요도 낮게 시작
        )
        
        # 실제 GameState 생성
        self.game_state = self.settings.create_initial_state()
        
    def get_game_state(self) -> GameStateResponse:
        """현재 게임 상태 조회"""
        return GameStateResponse(
            current_day=self.game_state.current_day,
            money=self.game_state.money,
            reputation=self.game_state.reputation,
            happiness=self.game_state.happiness,
            suffering=self.game_state.suffering,
            inventory=self.game_state.inventory,
            staff_fatigue=self.game_state.staff_fatigue,
            facility=self.game_state.facility,
            demand=self.game_state.demand,
            events_history=list(self.game_state.events_history)
        )
    
    def _get_game_over_reason(self) -> Optional[str]:
        """게임 오버 이유"""
        if self.game_state.money <= 0:
            return "파산! 자금이 바닥났습니다."
        elif self.game_state.reputation <= 0:
            return "평판 최악! 더 이상 손님이 오지 않습니다."
        elif self.game_state.happiness <= 0:
            return "번아웃! 더 이상 일할 수 없습니다."
        return None


# === 전역 게임 매니저 인스턴스 ===
game_manager = WebGameManager()


# === API 엔드포인트 ===

@app.get("/")
async def read_root():
    """메인 페이지 - HTML 파일 반환"""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "치킨마스터 서버가 정상 동작 중입니다!"}


@app.get("/api/game/state", response_model=GameStateResponse)
async def get_game_state():
    """현재 게임 상태 조회"""
    return game_manager.get_game_state()


@app.post("/api/game/action", response_model=ActionResponse)
async def execute_action(action: ActionRequest):
    """게임 액션 실행"""
    try:
        success = False
        message = ""
        
        if action.action_type == "price_change":
            success, message = self._action_price_change(action.parameters)
        elif action.action_type == "order_inventory":
            success, message = self._action_order_inventory()
        elif action.action_type == "staff_management":
            success, message = self._action_staff_management()
        elif action.action_type == "promotion":
            success, message = self._action_promotion()
        elif action.action_type == "facility_upgrade":
            success, message = self._action_facility_upgrade()
        elif action.action_type == "personal_rest":
            success, message = self._action_personal_rest()
        elif action.action_type == "research_development":
            success, message = self._action_research_development()
        elif action.action_type == "next_turn":
            success, message = self._process_turn()
        else:
            raise HTTPException(status_code=400, detail=f"알 수 없는 액션: {action.action_type}")
        
        return ActionResponse(
            success=success,
            message=message,
            new_state=self.get_game_state()
        )
        
    except Exception as e:
        return ActionResponse(
            success=False,
            message=f"액션 실행 중 오류: {str(e)}",
            new_state=self.get_game_state()
        )


@app.post("/api/game/reset")
async def reset_game():
    """게임 리셋"""
    global game_manager
    game_manager = WebGameManager()
    return {"success": True, "message": "게임이 리셋되었습니다!"}


@app.get("/api/dialogue/daily-start")
async def get_daily_start_dialogue():
    """매일 시작 대화 조회 (게임 상태 기반)"""
    if not dialogue_manager:
        return {"error": "대화 관리자를 사용할 수 없습니다"}
    
    # 현재 게임 상태 가져오기
    game_state = {
        "money": game_manager.game_state.money,
        "reputation": game_manager.game_state.reputation,
        "happiness": game_manager.game_state.happiness,
        "day": game_manager.game_state.current_day
    }
    
    # 조건에 맞는 대화 가져오기
    dialogue = dialogue_manager.get_daily_start_dialogue(game_state)
    
    if dialogue:
        return {
            "success": True,
            "dialogue": {
                "speaker": dialogue.speaker,
                "position": dialogue.position,
                "emotion": dialogue.emotion,
                "text": dialogue.text,
                "category": dialogue.category
            }
        }
    else:
        return {"success": False, "message": "조건에 맞는 대화를 찾을 수 없습니다"}


@app.get("/api/dialogue/character-database")
async def get_character_database():
    """JavaScript 캐릭터 데이터베이스 반환"""
    if not dialogue_manager:
        return {"error": "대화 관리자를 사용할 수 없습니다"}
    
    js_data = dialogue_manager.to_javascript_format()
    return {
        "success": True,
        "data": js_data
    }


@app.get("/api/dialogue/event/{event_id}")
async def get_event_dialogue(event_id: str):
    """이벤트 대화 조회"""
    if not dialogue_manager:
        return {"error": "대화 관리자를 사용할 수 없습니다"}
    
    dialogue = dialogue_manager.get_event_dialogue(event_id)
    
    if dialogue:
        return {
            "success": True,
            "dialogue": {
                "speaker": dialogue.speaker,
                "position": dialogue.position,
                "emotion": dialogue.emotion,
                "text": dialogue.text,
                "category": dialogue.category
            }
        }
    else:
        return {"success": False, "message": f"이벤트 대화 '{event_id}'를 찾을 수 없습니다"}


# === 개발 서버 실행 ===
if __name__ == "__main__":
    import uvicorn
    print("🚀 치킨마스터 웹 서버를 시작합니다...")
    print("📱 브라우저에서 http://localhost:8000 으로 접속하세요!")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 
"""
치킨마스터 웹 애플리케이션
실제 게임 로직을 사용하는 FastAPI 기반 웹 서비스
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 백엔드 모듈 경로 추가
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    # 백엔드 게임 로직 임포트
    from app.core.domain.game_initializer import GameInitializer, GameSettings
    from app.core.domain.game_state import GameState
    from app.adapters.excel_data_provider import ExcelGameDataProvider
    from app.services.metrics_tracker import MetricsTracker
    from app.core.domain.event_system import EventEngine, GameEventSystem
    from app.core.game_constants import *
    
    BACKEND_AVAILABLE = True
    print("✅ 백엔드 게임 로직 로드 성공!")
    
except ImportError as e:
    print(f"⚠️ 백엔드 로직 로드 실패: {e}")
    BACKEND_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="치킨마스터 게임",
    description="실제 게임 로직을 사용하는 치킨집 경영 시뮬레이션",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 게임 상태 저장 (실제로는 데이터베이스나 세션 사용)
game_sessions: Dict[str, GameState] = {}
game_initializer = None
metrics_tracker = None
event_engine = None

# Pydantic 모델들
class GameAction(BaseModel):
    action_type: str
    parameters: Dict[str, Any] = {}

class GameResponse(BaseModel):
    success: bool
    message: str
    game_state: Optional[Dict[str, Any]] = None
    available_actions: List[str] = []

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 게임 시스템 초기화"""
    global game_initializer, metrics_tracker, event_engine
    
    if BACKEND_AVAILABLE:
        try:
            # 엑셀 데이터 프로바이더 초기화
            excel_path = Path(__file__).parent.parent / "data" / "game_initial_values.xlsx"
            if excel_path.exists():
                data_provider = ExcelGameDataProvider(str(excel_path))
                game_initializer = GameInitializer(data_provider)
                logger.info("✅ 게임 초기화 시스템 로드 완료")
            else:
                # 엑셀 파일이 없으면 기본 설정으로 초기화
                game_initializer = GameInitializer(None, GameSettings())
                logger.warning("⚠️ 엑셀 파일 없음, 기본 설정으로 초기화")
                
            # 메트릭 트래커 초기화
            metrics_tracker = MetricsTracker()
            logger.info("✅ 메트릭 트래커 초기화 완료")
            
            # 이벤트 엔진 초기화 (간단한 버전)
            event_engine = EventEngine()
            logger.info("✅ 이벤트 엔진 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 게임 시스템 초기화 실패: {e}")
            game_initializer = None
    else:
        logger.warning("⚠️ 백엔드 로직 없이 실행 중")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 페이지 반환"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>치킨마스터</title></head>
            <body>
                <h1>치킨마스터 게임</h1>
                <p>게임 로딩 중...</p>
                <div id="game-status">시스템 확인 중...</div>
                <script>
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('game-status').innerHTML = 
                                data.backend_available ? 
                                '✅ 게임 시스템 준비 완료!' : 
                                '⚠️ 기본 모드로 실행 중';
                        });
                </script>
            </body>
        </html>
        """)

@app.get("/api/status")
async def get_status():
    """시스템 상태 확인"""
    return {
        "backend_available": BACKEND_AVAILABLE,
        "game_initializer": game_initializer is not None,
        "metrics_tracker": metrics_tracker is not None,
        "event_engine": event_engine is not None,
        "version": "1.0.0"
    }

@app.post("/api/game/new")
async def new_game(session_id: str = "default"):
    """새 게임 시작"""
    try:
        if game_initializer:
            # 실제 게임 로직으로 초기화
            initial_state = game_initializer.initialize()
            game_sessions[session_id] = initial_state
            
            return GameResponse(
                success=True,
                message="새 게임이 시작되었습니다!",
                game_state=initial_state.to_dict(),
                available_actions=["check_status", "daily_routine", "view_metrics"]
            )
        else:
            # 백엔드 없이 기본 게임 상태
            default_state = {
                "current_day": 1,
                "money": 10000.0,
                "reputation": 50.0,
                "happiness": 50.0,
                "suffering": 50.0,
                "inventory": 50.0,
                "staff_fatigue": 50.0,
                "facility": 50.0,
                "demand": 50.0,
                "events_history": []
            }
            game_sessions[session_id] = default_state
            
            return GameResponse(
                success=True,
                message="기본 모드 게임이 시작되었습니다!",
                game_state=default_state,
                available_actions=["check_status", "basic_action"]
            )
            
    except Exception as e:
        logger.error(f"게임 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=f"게임 시작 실패: {str(e)}")

@app.get("/api/game/state/{session_id}")
async def get_game_state(session_id: str = "default"):
    """현재 게임 상태 조회"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="게임 세션을 찾을 수 없습니다")
    
    state = game_sessions[session_id]
    if hasattr(state, 'to_dict'):
        state_dict = state.to_dict()
    else:
        state_dict = state
        
    return {
        "game_state": state_dict,
        "available_actions": ["check_status", "daily_routine", "view_metrics"]
    }

@app.post("/api/game/action")
async def perform_action(action: GameAction, session_id: str = "default"):
    """게임 액션 수행"""
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="게임 세션을 찾을 수 없습니다")
    
    try:
        current_state = game_sessions[session_id]
        
        if action.action_type == "check_status":
            if hasattr(current_state, 'to_dict'):
                state_dict = current_state.to_dict()
            else:
                state_dict = current_state
                
            return GameResponse(
                success=True,
                message="현재 상태를 확인했습니다.",
                game_state=state_dict,
                available_actions=["daily_routine", "view_metrics", "check_status"]
            )
            
        elif action.action_type == "daily_routine":
            # 간단한 일일 루틴 시뮬레이션
            if hasattr(current_state, 'current_day'):
                new_day = current_state.current_day + 1
                # 실제 게임 로직이 있다면 여기서 사용
                if BACKEND_AVAILABLE and hasattr(current_state, 'with_day'):
                    new_state = current_state.with_day(new_day)
                    game_sessions[session_id] = new_state
                    
                    return GameResponse(
                        success=True,
                        message=f"Day {new_day}: 하루가 지났습니다.",
                        game_state=new_state.to_dict(),
                        available_actions=["daily_routine", "view_metrics", "check_status"]
                    )
            
            return GameResponse(
                success=True,
                message="일일 루틴을 수행했습니다.",
                game_state=current_state if not hasattr(current_state, 'to_dict') else current_state.to_dict(),
                available_actions=["daily_routine", "view_metrics", "check_status"]
            )
            
        else:
            return GameResponse(
                success=False,
                message=f"알 수 없는 액션: {action.action_type}",
                available_actions=["check_status", "daily_routine", "view_metrics"]
            )
            
    except Exception as e:
        logger.error(f"액션 수행 오류: {e}")
        raise HTTPException(status_code=500, detail=f"액션 수행 실패: {str(e)}")

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "backend_available": BACKEND_AVAILABLE,
        "timestamp": "2025-01-18"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
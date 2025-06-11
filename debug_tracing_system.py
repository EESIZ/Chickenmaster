#!/usr/bin/env python3
"""
실시간 백엔드 트레이싱 시스템

사용자 명령어가 백엔드에서 어떻게 처리되는지 실시간으로 추적하고 표시합니다.
헥사고널 아키텍처의 모든 레이어에서 발생하는 호출을 추적할 수 있습니다.
"""

import json
import time
import functools
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from enum import Enum, auto


class TraceLevel(Enum):
    """트레이스 레벨"""
    DEBUG = auto()    # 모든 호출 추적
    INFO = auto()     # 주요 호출만 추적
    WARNING = auto()  # 경고 레벨
    ERROR = auto()    # 에러만 추적


@dataclass
class TraceEntry:
    """트레이스 엔트리"""
    timestamp: float
    level: TraceLevel
    module: str
    function: str
    args: List[Any]
    kwargs: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    

@dataclass
class StateSnapshot:
    """상태 스냅샷"""
    timestamp: float
    data: Dict[str, Any]
    description: str = ""


class TraceCollector:
    """트레이스 수집기"""
    
    def __init__(self):
        self.traces: List[TraceEntry] = []
        self.state_snapshots: List[StateSnapshot] = []
        self.enabled = True
        self.current_command = ""
        self.trace_level = TraceLevel.INFO
        
    def clear(self):
        """트레이스 기록 초기화"""
        self.traces.clear()
        self.state_snapshots.clear()
        
    def set_command(self, command: str):
        """현재 처리 중인 명령어 설정"""
        self.current_command = command
        
    def add_trace(self, entry: TraceEntry):
        """트레이스 엔트리 추가"""
        if self.enabled:
            self.traces.append(entry)
            
    def add_state_snapshot(self, data: Dict[str, Any], description: str = ""):
        """상태 스냅샷 추가"""
        if self.enabled:
            snapshot = StateSnapshot(
                timestamp=time.time(),
                data=data.copy(),
                description=description
            )
            self.state_snapshots.append(snapshot)
            
    def get_latest_traces(self, count: int = 10) -> List[TraceEntry]:
        """최근 트레이스 반환"""
        return self.traces[-count:] if count > 0 else self.traces
        
    def get_state_diff(self) -> Optional[Dict[str, Any]]:
        """상태 변화 비교"""
        if len(self.state_snapshots) < 2:
            return None
            
        before = self.state_snapshots[-2].data
        after = self.state_snapshots[-1].data
        
        return self._calculate_diff(before, after)
        
    def _calculate_diff(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """딕셔너리 간 차이점 계산"""
        diff = {
            "added": {},
            "removed": {},
            "changed": {},
            "unchanged": {}
        }
        
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            if key not in before:
                diff["added"][key] = after[key]
            elif key not in after:
                diff["removed"][key] = before[key]
            elif before[key] != after[key]:
                diff["changed"][key] = {
                    "before": before[key],
                    "after": after[key]
                }
            else:
                diff["unchanged"][key] = after[key]
                
        return diff


# 전역 트레이스 수집기
_trace_collector = TraceCollector()


def get_trace_collector() -> TraceCollector:
    """전역 트레이스 수집기 반환"""
    return _trace_collector


def traceable(level: TraceLevel = TraceLevel.INFO, capture_result: bool = True):
    """
    함수 호출을 추적하는 데코레이터
    
    Args:
        level: 트레이스 레벨
        capture_result: 결과값 캡처 여부 (큰 객체의 경우 성능상 이유로 비활성화 가능)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _trace_collector.enabled:
                return func(*args, **kwargs)
                
            start_time = time.time()
            module_name = func.__module__ or "unknown"
            function_name = func.__name__
            
            # 함수 인자를 JSON 직렬화 가능한 형태로 변환
            safe_args = []
            for arg in args:
                try:
                    # GameState나 다른 객체들을 간단한 표현으로 변환
                    if hasattr(arg, '__dict__'):
                        safe_args.append(f"<{type(arg).__name__} object>")
                    else:
                        safe_args.append(str(arg)[:100])  # 너무 긴 문자열 자르기
                except:
                    safe_args.append("<unprintable>")
                    
            safe_kwargs = {}
            for k, v in kwargs.items():
                try:
                    if hasattr(v, '__dict__'):
                        safe_kwargs[k] = f"<{type(v).__name__} object>"
                    else:
                        safe_kwargs[k] = str(v)[:100]
                except:
                    safe_kwargs[k] = "<unprintable>"
            
            trace_entry = TraceEntry(
                timestamp=start_time,
                level=level,
                module=module_name,
                function=function_name,
                args=safe_args,
                kwargs=safe_kwargs
            )
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                trace_entry.execution_time = end_time - start_time
                
                if capture_result:
                    if hasattr(result, '__dict__'):
                        trace_entry.result = f"<{type(result).__name__} object>"
                    else:
                        trace_entry.result = str(result)[:200]
                
                _trace_collector.add_trace(trace_entry)
                return result
                
            except Exception as e:
                end_time = time.time()
                trace_entry.execution_time = end_time - start_time
                trace_entry.error = str(e)
                _trace_collector.add_trace(trace_entry)
                raise
                
        return wrapper
    return decorator


class DebugFormatter:
    """디버그 출력 포맷터"""
    
    @staticmethod
    def format_trace_entry(entry: TraceEntry) -> str:
        """트레이스 엔트리를 사람이 읽기 쉬운 형태로 포맷"""
        timestamp = time.strftime("%H:%M:%S", time.localtime(entry.timestamp))
        duration = f"{entry.execution_time*1000:.1f}ms" if entry.execution_time else "??ms"
        
        result = f"[{timestamp}] {entry.module}.{entry.function}()"
        
        if entry.args or entry.kwargs:
            args_str = ", ".join([str(arg) for arg in entry.args[:2]])  # 처음 2개 인자만
            if len(entry.args) > 2:
                args_str += f", ... (+{len(entry.args)-2} more)"
            if entry.kwargs:
                kwargs_str = ", ".join([f"{k}={v}" for k, v in list(entry.kwargs.items())[:2]])
                if len(entry.kwargs) > 2:
                    kwargs_str += f", ... (+{len(entry.kwargs)-2} more)"
                args_str = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
            result += f" with ({args_str})"
            
        result += f" [{duration}]"
        
        if entry.error:
            result += f" ❌ ERROR: {entry.error}"
        elif entry.result:
            result += f" → {entry.result}"
            
        return result
        
    @staticmethod
    def format_state_diff(diff: Dict[str, Any]) -> List[str]:
        """상태 변화를 사람이 읽기 쉬운 형태로 포맷"""
        lines = []
        
        if diff["changed"]:
            lines.append("🔄 변경된 값:")
            for key, change in diff["changed"].items():
                before = change["before"]
                after = change["after"]
                # 숫자인 경우 변화량 표시
                if isinstance(before, (int, float)) and isinstance(after, (int, float)):
                    delta = after - before
                    sign = "+" if delta > 0 else ""
                    lines.append(f"  {key}: {before} → {after} ({sign}{delta})")
                else:
                    lines.append(f"  {key}: {before} → {after}")
                    
        if diff["added"]:
            lines.append("➕ 추가된 값:")
            for key, value in diff["added"].items():
                lines.append(f"  {key}: {value}")
                
        if diff["removed"]:
            lines.append("➖ 제거된 값:")
            for key, value in diff["removed"].items():
                lines.append(f"  {key}: {value}")
                
        return lines


@contextmanager
def trace_command(command: str):
    """명령어 처리 컨텍스트 매니저"""
    collector = get_trace_collector()
    collector.set_command(command)
    collector.clear()  # 이전 트레이스 초기화
    
    try:
        yield collector
    finally:
        pass  # 트레이스는 수집기에 저장됨


def capture_state(obj: Any, description: str = "") -> None:
    """객체 상태를 캡처하여 스냅샷에 추가"""
    collector = get_trace_collector()
    
    if hasattr(obj, '__dict__'):
        state_data = obj.__dict__.copy()
    elif hasattr(obj, 'to_dict'):
        state_data = obj.to_dict()
    elif isinstance(obj, dict):
        state_data = obj.copy()
    else:
        state_data = {"value": str(obj)}
        
    collector.add_state_snapshot(state_data, description)


def toggle_tracing() -> bool:
    """트레이싱 활성화/비활성화 토글"""
    collector = get_trace_collector()
    collector.enabled = not collector.enabled
    return collector.enabled


def set_trace_level(level: TraceLevel) -> None:
    """트레이스 레벨 설정"""
    collector = get_trace_collector()
    collector.trace_level = level 
#!/usr/bin/env python3
"""
파일: dev_tools/balance_simulator.py
설명: 이벤트 밸런스 시뮬레이션 도구

이 모듈은 이벤트 뱅크의 밸런스를 시뮬레이션하고 분석하는 기능을 제공합니다.
다양한 시나리오에서 이벤트 발생과 선택에 따른 게임 상태 변화를 시뮬레이션하여
밸런스 문제를 식별하고 보고합니다.

주요 기능:
- 이벤트 뱅크 로드 및 분석
- 다양한 시나리오에서 이벤트 시뮬레이션
- 밸런스 메트릭 계산 및 보고
- 문제 이벤트 식별 및 권장 조정 제안
- 시각화 및 결과 분석

사용 예시:
    python -m dev_tools.balance_simulator --input data/events_bank --output reports/balance_report.csv --iterations 1000
"""

import argparse
import csv
import json
import logging
import os
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, TypedDict, cast

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from pydantic import BaseModel, Field, field_validator
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️ 시각화 라이브러리를 찾을 수 없습니다. 시각화 기능이 비활성화됩니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("balance_simulator")


class SimulationConfig(BaseModel):
    """시뮬레이션 설정을 위한 모델"""

    iterations: int = Field(default=100, ge=1, le=1000, description="시뮬레이션 반복 횟수")
    turns_per_sim: int = Field(default=30, ge=1, le=1000, description="각 시뮬레이션의 턴 수")
    seed: Optional[int] = Field(default=None, description="랜덤 시드 (재현성)")
    bankruptcy_threshold: float = Field(default=-5000, description="파산 기준 자금")
    happiness_weight: float = Field(default=1.0, description="행복 지표 가중치")
    pain_weight: float = Field(default=1.0, description="고통 지표 가중치")
    cascade_depth_limit: int = Field(default=5, ge=1, le=10, description="최대 연쇄 깊이")
    destruction_threshold: float = Field(default=0.05, description="허용 가능한 파괴율")

    @field_validator("iterations")
    def validate_iterations(cls, v: int) -> int:
        """반복 횟수 검증"""
        if not 1 <= v <= 1000:
            raise ValueError("반복 횟수는 1-1000 사이여야 합니다.")
        return v

    @field_validator("turns_per_sim")
    def validate_turns(cls, v: int) -> int:
        """턴 수 검증"""
        if not 1 <= v <= 1000:
            raise ValueError("턴 수는 1-1000 사이여야 합니다.")
        return v

    @field_validator("cascade_depth_limit")
    def validate_cascade_depth(cls, v: int) -> int:
        """연쇄 깊이 제한 검증"""
        if not 1 <= v <= 10:
            raise ValueError("연쇄 깊이 제한은 1-10 사이여야 합니다.")
        return v

    def model_dump(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        return {
            "iterations": self.iterations,
            "turns_per_sim": self.turns_per_sim,
            "seed": self.seed,
            "bankruptcy_threshold": self.bankruptcy_threshold,
            "happiness_weight": self.happiness_weight,
            "pain_weight": self.pain_weight,
            "cascade_depth_limit": self.cascade_depth_limit,
            "destruction_threshold": self.destruction_threshold,
        }


class EventStats(TypedDict):
    """이벤트 통계"""
    trigger_count: int
    choice_distribution: Dict[str, int]
    cascade_depth: List[int]
    metric_changes: Dict[str, List[float]]


@dataclass
class GameState:
    """게임 상태를 나타내는 클래스"""

    money: float = 1000.0
    happiness: float = 50.0
    pain: float = 50.0
    day: int = 1
    actions_left: int = 3
    metrics: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    triggered_events: Set[str] = field(default_factory=set)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def apply_effect(self, effect: Dict[str, Any]) -> None:
        """
        이벤트 효과를 게임 상태에 적용

        Args:
            effect: 적용할 효과 정보
        """
        if "metric" in effect and "formula" in effect:
            metric = effect["metric"]
            formula = effect["formula"]

            # 효과 적용 전 상태 기록
            prev_value = self._get_metric_value(metric)

            # 기본 지표 업데이트
            if metric == "money":
                self.money += float(formula)
            elif metric == "happiness":
                self.happiness += float(formula)
                self.happiness = max(0, min(100, self.happiness))
            elif metric == "pain":
                self.pain += float(formula)
                self.pain = max(0, min(100, self.pain))
            # 기타 메트릭 업데이트
            else:
                self.metrics[metric] += float(formula)

            # 효과 적용 후 상태 기록
            new_value = self._get_metric_value(metric)

            # 변경 이력 기록
            self.history.append(
                {
                    "day": self.day,
                    "actions_left": self.actions_left,
                    "metric": metric,
                    "prev_value": prev_value,
                    "new_value": new_value,
                    "change": new_value - prev_value,
                    "formula": formula,
                }
            )

    def _get_metric_value(self, metric: str) -> float:
        """
        지표 값 조회

        Args:
            metric: 조회할 지표 이름

        Returns:
            지표 값
        """
        if metric == "money":
            return self.money
        elif metric == "happiness":
            return self.happiness
        elif metric == "pain":
            return self.pain
        elif metric == "day":
            return float(self.day)
        elif metric == "actions_left":
            return float(self.actions_left)
        else:
            return self.metrics.get(metric, 0.0)

    def is_bankrupt(self, threshold: float) -> bool:
        """
        파산 여부 확인

        Args:
            threshold: 파산 기준 자금

        Returns:
            파산 여부
        """
        return self.money < threshold

    def check_balance(self) -> bool:
        """
        행복+고통=100 균형 확인

        Returns:
            균형 유지 여부
        """
        return abs((self.happiness + self.pain) - 100.0) < 0.001

    def clone(self) -> "GameState":
        """
        현재 상태의 복사본 생성

        Returns:
            복제된 게임 상태
        """
        new_state = GameState(
            money=self.money,
            happiness=self.happiness,
            pain=self.pain,
            day=self.day,
            actions_left=self.actions_left,
        )
        new_state.metrics = self.metrics.copy()
        new_state.triggered_events = self.triggered_events.copy()
        new_state.history = self.history.copy()
        return new_state

    def get_state_summary(self) -> Dict[str, Any]:
        """
        현재 상태 요약 정보 반환

        Returns:
            상태 요약 정보
        """
        return {
            "day": self.day,
            "actions_left": self.actions_left,
            "money": self.money,
            "happiness": self.happiness,
            "pain": self.pain,
            "metrics": dict(self.metrics),
            "triggered_events_count": len(self.triggered_events),
            "is_balanced": self.check_balance(),
        }


class EventSimulator:
    """이벤트 시뮬레이션을 위한 클래스"""

    def __init__(self, events_dir: str, config: SimulationConfig):
        """
        이벤트 시뮬레이터 초기화

        Args:
            events_dir: 이벤트 뱅크 디렉토리 경로
            config: 시뮬레이션 설정
        """
        self.events_dir = Path(events_dir)
        self.config = config
        self.events = {}
        self.event_stats = defaultdict(lambda: defaultdict(int))
        self.cascade_stats = defaultdict(int)
        self.tradeoff_metrics = defaultdict(list)
        self.uncertainty_factors = defaultdict(list)

        # 랜덤 시드 설정
        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)

        # 이벤트 로드
        self._load_events()

    def _load_events(self) -> None:
        """이벤트 뱅크에서 이벤트 로드"""
        logger.info(f"이벤트 뱅크 로드 중: {self.events_dir}")

        # 메타데이터 로드
        metadata_path = self.events_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                logger.info(
                    f"메타데이터 로드 완료: {len(self.metadata.get('tags', {}))} 태그"
                )
        else:
            logger.warning(f"메타데이터 파일을 찾을 수 없음: {metadata_path}")
            self.metadata = {"tags": {}}

        # 카테고리별 이벤트 로드
        categories = [d for d in self.events_dir.iterdir() if d.is_dir()]
        if not categories:
            logger.warning(f"이벤트 카테고리를 찾을 수 없음: {self.events_dir}")

        for category_dir in categories:
            category = category_dir.name
            event_files = [f for f in category_dir.glob("*.json") if f.is_file()]

            for event_file in event_files:
                try:
                    with open(event_file, "r", encoding="utf-8") as f:
                        event_data = json.load(f)
                        event_id = event_data.get("id", event_file.stem)
                        self.events[event_id] = {
                            "data": event_data,
                            "category": category,
                            "file": str(event_file),
                        }
                except json.JSONDecodeError:
                    logger.error(f"JSON 파싱 오류: {event_file}")
                except Exception as e:
                    logger.error(f"이벤트 로드 오류: {event_file} - {str(e)}")

        if not self.events:
            logger.warning("로드된 이벤트가 없습니다")
        else:
            logger.info(
                f"이벤트 로드 완료: {len(self.events)} 이벤트, {len(categories)} 카테고리"
            )

    def _evaluate_condition(self, condition: Dict[str, Any], state: GameState) -> bool:
        """
        이벤트 트리거 조건 평가

        Args:
            condition: 평가할 조건
            state: 현재 게임 상태

        Returns:
            조건 충족 여부
        """
        if not condition:
            return True

        metric = condition.get("metric", "")
        operator = condition.get("operator", "")
        value = condition.get("value", 0)

        # 기본 지표 평가
        if metric == "money":
            actual_value = state.money
        elif metric == "happiness":
            actual_value = state.happiness
        elif metric == "pain":
            actual_value = state.pain
        elif metric == "day":
            actual_value = state.day
        elif metric == "actions_left":
            actual_value = state.actions_left
        # 기타 메트릭 평가
        else:
            actual_value = state.metrics.get(metric, 0)

        # 불확실성 요소 기록
        self.uncertainty_factors[metric].append(
            {"actual": actual_value, "expected": value, "operator": operator}
        )

        # 조건 연산자 평가
        if operator == "equal":
            return actual_value == value
        elif operator == "not_equal":
            return actual_value != value
        elif operator == "greater_than":
            return actual_value > value
        elif operator == "less_than":
            return actual_value < value
        elif operator == "greater_than_or_equal":
            return actual_value >= value
        elif operator == "less_than_or_equal":
            return actual_value <= value
        elif operator == "contains":
            return (
                value in actual_value
                if isinstance(actual_value, (list, set, str))
                else False
            )
        elif operator == "not_contains":
            return (
                value not in actual_value
                if isinstance(actual_value, (list, set, str))
                else True
            )

        logger.warning(f"지원되지 않는 연산자: {operator}")
        return False

    def _get_triggerable_events(self, state: GameState) -> List[str]:
        """
        현재 상태에서 트리거 가능한 이벤트 목록 반환

        Args:
            state: 현재 게임 상태

        Returns:
            트리거 가능한 이벤트 ID 목록
        """
        triggerable = []

        for event_id, event_info in self.events.items():
            event_data = event_info["data"]

            # 이미 트리거된 이벤트 제외 (중복 방지)
            if event_id in state.triggered_events:
                continue

            # 이벤트 타입 확인
            event_type = event_data.get("type", "RANDOM")

            # THRESHOLD 타입 이벤트는 조건 충족 시에만 트리거
            if event_type == "THRESHOLD":
                trigger = event_data.get("trigger", {})
                if self._evaluate_condition(trigger, state):
                    triggerable.append(event_id)

            # RANDOM 타입 이벤트는 항상 트리거 가능
            elif event_type == "RANDOM":
                triggerable.append(event_id)

            # SCHEDULED 타입 이벤트는 특정 일자에 트리거
            elif event_type == "SCHEDULED":
                schedule = event_data.get("schedule", {})
                day = schedule.get("day")
                if day and state.day == day:
                    triggerable.append(event_id)

        return triggerable

    def _select_random_event(self, triggerable: List[str]) -> Optional[str]:
        """
        트리거 가능한 이벤트 중 무작위 선택

        Args:
            triggerable: 트리거 가능한 이벤트 ID 목록

        Returns:
            선택된 이벤트 ID 또는 None
        """
        if not triggerable:
            return None
        return random.choice(triggerable)

    def _select_random_choice(self, event_data: Dict[str, Any]) -> int:
        """
        이벤트의 선택지 중 무작위 선택

        Args:
            event_data: 이벤트 데이터

        Returns:
            선택된 선택지 인덱스 또는 -1
        """
        choices = event_data.get("choices", [])
        if not choices:
            return -1

        # 선택지 가중치 확인
        weights = []
        for choice in choices:
            weight = choice.get("weight", 1.0)
            weights.append(float(weight))

        # 가중치 기반 선택
        if any(w != 1.0 for w in weights):
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            return int(np.random.choice(len(choices), p=normalized_weights))

        # 동일 확률 선택
        return random.randint(0, len(choices) - 1)

    def _apply_event_effects(
        self, event_data: Dict[str, Any], choice_idx: int, state: GameState
    ) -> None:
        """
        이벤트 효과 적용

        Args:
            event_data: 이벤트 데이터
            choice_idx: 선택된 선택지 인덱스
            state: 게임 상태
        """
        # 이벤트 레벨 효과 적용
        for effect in event_data.get("effects", []):
            state.apply_effect(effect)

        # 선택지 효과 적용
        if choice_idx >= 0 and choice_idx < len(event_data.get("choices", [])):
            choice = event_data["choices"][choice_idx]

            # 트레이드오프 메트릭 기록
            if len(choice.get("effects", [])) > 1:
                tradeoff_data = {
                    "event_id": event_data.get("id", "unknown"),
                    "choice_idx": choice_idx,
                    "effects": [],
                }

                for effect in choice.get("effects", []):
                    if "metric" in effect and "formula" in effect:
                        tradeoff_data["effects"].append(
                            {"metric": effect["metric"], "formula": effect["formula"]}
                        )

                if len(tradeoff_data["effects"]) > 1:
                    self.tradeoff_metrics[event_data.get("id", "unknown")].append(
                        tradeoff_data
                    )

            # 효과 적용
            for effect in choice.get("effects", []):
                state.apply_effect(effect)

    def _simulate_cascade(
        self, event_id: str, state: GameState, depth: int = 0
    ) -> Tuple[GameState, int]:
        """
        이벤트 연쇄 시뮬레이션

        Args:
            event_id: 이벤트 ID
            state: 게임 상태
            depth: 현재 연쇄 깊이

        Returns:
            업데이트된 게임 상태와 최대 연쇄 깊이
        """
        if depth >= self.config.cascade_depth_limit:
            logger.debug(
                f"연쇄 깊이 제한 도달: {depth} >= {self.config.cascade_depth_limit}"
            )
            return state, depth

        # 이벤트 데이터 가져오기
        event_info = self.events.get(event_id)
        if not event_info:
            logger.warning(f"이벤트를 찾을 수 없음: {event_id}")
            return state, depth

        event_data = event_info["data"]

        # 이벤트 통계 업데이트
        self.event_stats[event_id]["triggered"] += 1

        # 이벤트 트리거 기록
        state.triggered_events.add(event_id)

        # 선택지 무작위 선택
        choice_idx = self._select_random_choice(event_data)
        if choice_idx >= 0:
            self.event_stats[event_id][f"choice_{choice_idx}"] += 1

        # 이벤트 효과 적용
        self._apply_event_effects(event_data, choice_idx, state)

        # 연쇄 이벤트 확인
        max_cascade_depth = depth

        # 선택지에 연쇄 이벤트가 있는 경우
        if choice_idx >= 0 and choice_idx < len(event_data.get("choices", [])):
            choice = event_data["choices"][choice_idx]
            cascade_events = choice.get("cascade_events", [])

            for cascade_event in cascade_events:
                cascade_id = cascade_event.get("id")
                if cascade_id and cascade_id in self.events:
                    # 연쇄 조건 확인
                    condition = cascade_event.get("condition", {})
                    if self._evaluate_condition(condition, state):
                        # 연쇄 이벤트 시뮬레이션
                        new_state, cascade_depth = self._simulate_cascade(
                            cascade_id, state, depth + 1
                        )
                        state = new_state
                        max_cascade_depth = max(max_cascade_depth, cascade_depth)

        return state, max_cascade_depth

    def _simulate_turn(self, state: GameState) -> Tuple[GameState, int]:
        """
        한 턴 시뮬레이션

        Args:
            state: 게임 상태

        Returns:
            업데이트된 게임 상태와 연쇄 깊이
        """
        # 트리거 가능한 이벤트 확인
        triggerable = self._get_triggerable_events(state)

        # 이벤트 선택
        event_id = self._select_random_event(triggerable)
        if not event_id:
            # 트리거 가능한 이벤트가 없으면 턴 종료
            state.actions_left -= 1
            return state, 0

        # 이벤트 연쇄 시뮬레이션
        new_state, cascade_depth = self._simulate_cascade(event_id, state)

        # 연쇄 깊이 통계 업데이트
        self.cascade_stats[cascade_depth] += 1

        # 액션 소비
        new_state.actions_left -= 1

        return new_state, cascade_depth

    def _simulate_day(self, state: GameState) -> GameState:
        """
        하루 시뮬레이션

        Args:
            state: 게임 상태

        Returns:
            업데이트된 게임 상태
        """
        # 액션 소비
        while state.actions_left > 0:
            state, _ = self._simulate_turn(state)

            # 파산 체크
            if state.is_bankrupt(self.config.bankruptcy_threshold):
                break

        # 일일 마감 및 액션 초기화
        state.day += 1
        state.actions_left = 3

        return state

    def simulate_game(self) -> Dict[str, Any]:
        """
        게임 시뮬레이션 실행

        Returns:
            시뮬레이션 결과
        """
        # 초기 상태
        state = GameState()

        # 시뮬레이션 결과
        results = {
            "days_survived": 0,
            "final_money": 0,
            "final_happiness": 0,
            "final_pain": 0,
            "is_bankrupt": False,
            "balance_maintained": True,
            "max_cascade_depth": 0,
            "events_triggered": 0,
            "daily_stats": [],
        }

        # 지정된 턴 수만큼 시뮬레이션
        for _ in range(self.config.turns_per_sim):
            # 일일 시작 상태 기록
            daily_start = state.get_state_summary()

            # 하루 시뮬레이션
            state = self._simulate_day(state)

            # 일일 종료 상태 기록
            daily_end = state.get_state_summary()

            # 일일 통계 기록
            results["daily_stats"].append(
                {
                    "day": state.day - 1,
                    "start": daily_start,
                    "end": daily_end,
                    "money_change": daily_end["money"] - daily_start["money"],
                    "happiness_change": daily_end["happiness"]
                    - daily_start["happiness"],
                    "pain_change": daily_end["pain"] - daily_start["pain"],
                }
            )

            # 파산 체크
            if state.is_bankrupt(self.config.bankruptcy_threshold):
                results["is_bankrupt"] = True
                break

            # 행복+고통=100 균형 체크
            if not state.check_balance():
                results["balance_maintained"] = False

        # 결과 저장
        results["days_survived"] = state.day - 1
        results["final_money"] = state.money
        results["final_happiness"] = state.happiness
        results["final_pain"] = state.pain
        results["events_triggered"] = len(state.triggered_events)
        results["max_cascade_depth"] = (
            max(self.cascade_stats.keys()) if self.cascade_stats else 0
        )
        results["history"] = state.history

        return results

    def run_simulations(self) -> pd.DataFrame:
        """
        여러 시뮬레이션 실행 및 결과 분석

        Returns:
            시뮬레이션 결과 데이터프레임
        """
        logger.info(f"{self.config.iterations}회 시뮬레이션 시작...")

        results = []
        for i in range(self.config.iterations):
            if i % 10 == 0:
                logger.info(f"시뮬레이션 진행 중: {i}/{self.config.iterations}")

            # 이벤트 통계 및 연쇄 통계 초기화
            self.event_stats = defaultdict(lambda: defaultdict(int))
            self.cascade_stats = defaultdict(int)

            # 시뮬레이션 실행
            result = self.simulate_game()
            results.append(result)

        logger.info("시뮬레이션 완료")

        # 결과 데이터프레임 생성
        df = pd.DataFrame(results)

        return df

    def analyze_balance(self, results: pd.DataFrame) -> Dict[str, Any]:
        """
        밸런스 분석

        Args:
            results: 시뮬레이션 결과 데이터프레임

        Returns:
            밸런스 분석 결과
        """
        analysis = {}

        # 파산율
        bankruptcy_rate = results["is_bankrupt"].mean()
        analysis["bankruptcy_rate"] = bankruptcy_rate

        # 평균 생존 일수
        avg_days = results["days_survived"].mean()
        analysis["avg_days_survived"] = avg_days

        # 평균 최종 자금
        avg_money = results["final_money"].mean()
        analysis["avg_final_money"] = avg_money

        # 행복/고통 균형 유지율
        balance_rate = results["balance_maintained"].mean()
        analysis["balance_maintained_rate"] = balance_rate

        # 최대 연쇄 깊이
        max_cascade = results["max_cascade_depth"].max()
        analysis["max_cascade_depth"] = max_cascade

        # 파괴율 (config.destruction_threshold 초과 여부)
        destruction_rate = bankruptcy_rate
        analysis["destruction_rate"] = destruction_rate
        analysis["destruction_threshold_exceeded"] = (
            destruction_rate > self.config.destruction_threshold
        )

        # 이벤트 트리거 통계
        event_trigger_stats = {}
        for event_id, stats in self.event_stats.items():
            trigger_count = stats["triggered"]
            trigger_rate = trigger_count / self.config.iterations

            choice_stats = {}
            for key, count in stats.items():
                if key.startswith("choice_"):
                    choice_idx = int(key.split("_")[1])
                    if trigger_count > 0:
                        choice_rate = count / trigger_count
                    else:
                        choice_rate = 0
                    choice_stats[choice_idx] = {
                        "count": int(count),
                        "rate": float(choice_rate),
                    }

            event_trigger_stats[event_id] = {
                "count": int(trigger_count),
                "rate": float(trigger_rate),
                "choices": choice_stats,
            }

        analysis["event_stats"] = event_trigger_stats

        # 연쇄 깊이 통계
        cascade_depth_stats = {}
        total_cascades = sum(self.cascade_stats.values())
        for depth, count in self.cascade_stats.items():
            if total_cascades > 0:
                rate = count / total_cascades
            else:
                rate = 0
            cascade_depth_stats[int(depth)] = {"count": int(count), "rate": float(rate)}

        analysis["cascade_stats"] = cascade_depth_stats

        # 트레이드오프 분석
        analysis["tradeoff_metrics"] = dict(self.tradeoff_metrics)

        # 불확실성 요소 분석
        uncertainty_factors_dict = {}
        for metric, factors in self.uncertainty_factors.items():
            processed_factors = []
            for factor in factors:
                processed_factor = {
                    "actual": (
                        float(factor["actual"])
                        if isinstance(factor["actual"], (int, float, np.number))
                        else factor["actual"]
                    ),
                    "expected": (
                        float(factor["expected"])
                        if isinstance(factor["expected"], (int, float, np.number))
                        else factor["expected"]
                    ),
                    "operator": factor["operator"],
                }
                processed_factors.append(processed_factor)
            uncertainty_factors_dict[metric] = processed_factors

        analysis["uncertainty_factors"] = uncertainty_factors_dict

        return analysis

    def identify_problematic_events(
        self, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        문제가 있는 이벤트 식별

        Args:
            analysis: 밸런스 분석 결과

        Returns:
            문제가 있는 이벤트 목록
        """
        problematic = []

        event_stats = analysis.get("event_stats", {})

        for event_id, stats in event_stats.items():
            issues = []

            # 트리거 비율이 너무 높거나 낮은 이벤트
            trigger_rate = stats["rate"]
            if trigger_rate > 0.8:
                issues.append(
                    {
                        "type": "high_trigger_rate",
                        "value": float(trigger_rate),
                        "threshold": 0.8,
                        "description": "트리거 비율이 너무 높음",
                    }
                )
            elif trigger_rate < 0.01 and stats["count"] > 0:
                issues.append(
                    {
                        "type": "low_trigger_rate",
                        "value": float(trigger_rate),
                        "threshold": 0.01,
                        "description": "트리거 비율이 너무 낮음",
                    }
                )

            # 선택지 불균형
            choices = stats.get("choices", {})
            if len(choices) > 1:
                choice_rates = [c["rate"] for c in choices.values()]
                max_rate = max(choice_rates) if choice_rates else 0
                min_rate = min(choice_rates) if choice_rates else 0

                if max_rate > 0.9:
                    issues.append(
                        {
                            "type": "dominant_choice",
                            "value": float(max_rate),
                            "threshold": 0.9,
                            "description": "특정 선택지가 지나치게 자주 선택됨",
                        }
                    )

                if max_rate - min_rate > 0.7:
                    issues.append(
                        {
                            "type": "choice_imbalance",
                            "value": float(max_rate - min_rate),
                            "threshold": 0.7,
                            "description": "선택지 간 불균형이 심함",
                        }
                    )

            # 문제가 있는 이벤트 추가
            if issues:
                event_info = self.events.get(event_id, {})
                event_data = event_info.get("data", {})

                problematic.append(
                    {
                        "id": event_id,
                        "name": event_data.get("name", ""),
                        "category": event_info.get("category", ""),
                        "file": event_info.get("file", ""),
                        "issues": issues,
                        "stats": stats,
                    }
                )

        return problematic

    def generate_recommendations(
        self, problematic: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        밸런스 개선 권장사항 생성

        Args:
            problematic: 문제가 있는 이벤트 목록

        Returns:
            이벤트별 권장사항
        """
        recommendations = {}

        for event in problematic:
            event_id = event["id"]
            event_name = event["name"]
            issues = event["issues"]

            event_recs = []

            for issue in issues:
                issue_type = issue["type"]

                if issue_type == "high_trigger_rate":
                    event_recs.append("트리거 조건을 더 제한적으로 조정하세요")
                elif issue_type == "low_trigger_rate":
                    event_recs.append(
                        "트리거 조건을 완화하거나 더 일반적인 조건으로 변경하세요"
                    )
                elif issue_type == "dominant_choice":
                    event_recs.append(
                        "지배적인 선택지의 효과를 약화시키거나 다른 선택지의 효과를 강화하세요"
                    )
                elif issue_type == "choice_imbalance":
                    event_recs.append("선택지 간 균형을 맞추기 위해 효과를 조정하세요")

            if event_recs:
                recommendations[f"{event_id} ({event_name})"] = event_recs

        return recommendations

    def noRightAnswer_analyze_tradeoffs(self) -> Dict[str, Any]:
        """
        트레이드오프 분석 (정답 없음 철학 반영)

        Returns:
            트레이드오프 분석 결과
        """
        tradeoff_analysis = {}

        # 이벤트별 트레이드오프 분석
        for event_id, tradeoffs in self.tradeoff_metrics.items():
            event_analysis = {
                "count": len(tradeoffs),
                "metrics_involved": set(),
                "choices": [],
            }

            # 선택지별 트레이드오프 분석
            for tradeoff in tradeoffs:
                metrics = [effect["metric"] for effect in tradeoff["effects"]]
                event_analysis["metrics_involved"].update(metrics)

                # 선택지 효과 분석
                choice_idx = tradeoff["choice_idx"]
                positive_effects = sum(
                    1 for effect in tradeoff["effects"] if float(effect["formula"]) > 0
                )
                negative_effects = sum(
                    1 for effect in tradeoff["effects"] if float(effect["formula"]) < 0
                )

                # 선택지 트레이드오프 명확성 점수
                clarity_score = min(positive_effects, negative_effects) / max(
                    1, len(tradeoff["effects"])
                )

                event_analysis["choices"].append(
                    {
                        "choice_idx": choice_idx,
                        "positive_effects": positive_effects,
                        "negative_effects": negative_effects,
                        "total_effects": len(tradeoff["effects"]),
                        "clarity_score": float(clarity_score),
                    }
                )

            # 이벤트 트레이드오프 명확성 점수
            if event_analysis["choices"]:
                event_analysis["avg_clarity_score"] = float(
                    sum(c["clarity_score"] for c in event_analysis["choices"])
                    / len(event_analysis["choices"])
                )
            else:
                event_analysis["avg_clarity_score"] = 0.0

            event_analysis["metrics_involved"] = list(
                event_analysis["metrics_involved"]
            )
            tradeoff_analysis[event_id] = event_analysis

        # 전체 트레이드오프 명확성 점수
        if tradeoff_analysis:
            tradeoff_analysis["overall_clarity_score"] = float(
                sum(
                    e["avg_clarity_score"]
                    for e in tradeoff_analysis.values()
                    if "avg_clarity_score" in e
                )
                / len(tradeoff_analysis)
            )
        else:
            tradeoff_analysis["overall_clarity_score"] = 0.0

        return tradeoff_analysis

    def uncertainty_analyze_variability(self) -> Dict[str, Any]:
        """
        불확실성 분석 (완전 랜덤 드라마 철학 반영)

        Returns:
            불확실성 분석 결과
        """
        uncertainty_analysis = {}

        # 메트릭별 불확실성 분석
        for metric, factors in self.uncertainty_factors.items():
            if not factors:
                continue

            # 실제값과 기대값의 차이 분석
            diffs = []
            for factor in factors:
                if isinstance(factor["actual"], (int, float, np.number)) and isinstance(
                    factor["expected"], (int, float, np.number)
                ):
                    diffs.append(
                        abs(float(factor["actual"]) - float(factor["expected"]))
                    )

            # 메트릭 불확실성 점수
            if diffs:
                avg_diff = float(sum(diffs) / len(diffs))
                max_diff = float(max(diffs))
                min_diff = float(min(diffs))
                std_diff = float(np.std(diffs)) if len(diffs) > 1 else 0

                uncertainty_analysis[metric] = {
                    "count": len(factors),
                    "avg_diff": avg_diff,
                    "max_diff": max_diff,
                    "min_diff": min_diff,
                    "std_diff": std_diff,
                    "variability_score": float(
                        std_diff / (avg_diff if avg_diff > 0 else 1)
                    ),
                }

        # 전체 불확실성 점수
        if uncertainty_analysis:
            uncertainty_analysis["overall_variability_score"] = float(
                sum(
                    m["variability_score"]
                    for m in uncertainty_analysis.values()
                    if "variability_score" in m
                )
                / len(uncertainty_analysis)
            )
        else:
            uncertainty_analysis["overall_variability_score"] = 0.0

        return uncertainty_analysis

    def generate_visualizations(
        self, results: pd.DataFrame, output_dir: str
    ) -> List[str]:
        """
        시뮬레이션 결과 시각화

        Args:
            results: 시뮬레이션 결과 데이터프레임
            output_dir: 출력 디렉토리 경로

        Returns:
            생성된 시각화 파일 경로 목록
        """
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

        visualization_files = []

        # 1. 파산율 및 생존 일수 분포
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        bankruptcy_rate = results["is_bankrupt"].mean()
        labels = ["생존", "파산"]
        sizes = [(1 - bankruptcy_rate) * 100, bankruptcy_rate * 100]
        colors = ["#4CAF50", "#F44336"]
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.title("파산율")

        plt.subplot(1, 2, 2)
        results["days_survived"].hist(bins=20, color="#2196F3")
        plt.axvline(
            results["days_survived"].mean(),
            color="red",
            linestyle="--",
            label=f"평균: {results['days_survived'].mean():.1f}일",
        )
        plt.xlabel("생존 일수")
        plt.ylabel("빈도")
        plt.title("생존 일수 분포")
        plt.legend()

        plt.tight_layout()
        survival_file = os.path.join(output_dir, "survival_analysis.png")
        plt.savefig(survival_file)
        plt.close()
        visualization_files.append(survival_file)

        # 2. 최종 자금 분포
        plt.figure(figsize=(10, 6))
        results["final_money"].hist(bins=20, color="#FF9800")
        plt.axvline(
            results["final_money"].mean(),
            color="red",
            linestyle="--",
            label=f"평균: {results['final_money'].mean():.1f}",
        )
        plt.axvline(
            self.config.bankruptcy_threshold,
            color="black",
            linestyle="-",
            label=f"파산 기준: {self.config.bankruptcy_threshold}",
        )
        plt.xlabel("최종 자금")
        plt.ylabel("빈도")
        plt.title("최종 자금 분포")
        plt.legend()

        plt.tight_layout()
        money_file = os.path.join(output_dir, "money_distribution.png")
        plt.savefig(money_file)
        plt.close()
        visualization_files.append(money_file)

        # 3. 행복/고통 분포
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        results["final_happiness"].hist(bins=20, color="#8BC34A")
        plt.axvline(
            results["final_happiness"].mean(),
            color="red",
            linestyle="--",
            label=f"평균: {results['final_happiness'].mean():.1f}",
        )
        plt.xlabel("최종 행복")
        plt.ylabel("빈도")
        plt.title("최종 행복 분포")
        plt.legend()

        plt.subplot(1, 2, 2)
        results["final_pain"].hist(bins=20, color="#9C27B0")
        plt.axvline(
            results["final_pain"].mean(),
            color="red",
            linestyle="--",
            label=f"평균: {results['final_pain'].mean():.1f}",
        )
        plt.xlabel("최종 고통")
        plt.ylabel("빈도")
        plt.title("최종 고통 분포")
        plt.legend()

        plt.tight_layout()
        metrics_file = os.path.join(output_dir, "happiness_pain_distribution.png")
        plt.savefig(metrics_file)
        plt.close()
        visualization_files.append(metrics_file)

        # 4. 연쇄 깊이 분포
        cascade_depths = [int(k) for k in self.cascade_stats.keys()]
        cascade_counts = [int(v) for v in self.cascade_stats.values()]

        if cascade_depths and cascade_counts:
            plt.figure(figsize=(10, 6))
            plt.bar(cascade_depths, cascade_counts, color="#3F51B5")
            plt.axvline(
                self.config.cascade_depth_limit,
                color="red",
                linestyle="--",
                label=f"제한: {self.config.cascade_depth_limit}",
            )
            plt.xlabel("연쇄 깊이")
            plt.ylabel("발생 횟수")
            plt.title("연쇄 깊이 분포")
            plt.xticks(cascade_depths)
            plt.legend()

            plt.tight_layout()
            cascade_file = os.path.join(output_dir, "cascade_depth_distribution.png")
            plt.savefig(cascade_file)
            plt.close()
            visualization_files.append(cascade_file)

        # 5. 이벤트 트리거 빈도 (상위 20개)
        event_counts = {
            event_id: stats["triggered"] for event_id, stats in self.event_stats.items()
        }
        top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        if top_events:
            plt.figure(figsize=(12, 8))
            event_ids = [e[0] for e in top_events]
            event_counts = [int(e[1]) for e in top_events]

            plt.barh(event_ids, event_counts, color="#00BCD4")
            plt.xlabel("트리거 횟수")
            plt.ylabel("이벤트 ID")
            plt.title("이벤트 트리거 빈도 (상위 20개)")

            plt.tight_layout()
            events_file = os.path.join(output_dir, "event_trigger_frequency.png")
            plt.savefig(events_file)
            plt.close()
            visualization_files.append(events_file)

        return visualization_files

    def _convert_numpy_types(self, obj: Any) -> Any:
        """
        NumPy 타입을 Python 기본 타입으로 변환

        Args:
            obj: 변환할 객체

        Returns:
            변환된 객체
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        else:
            return obj

    def generate_report(
        self, results: pd.DataFrame, output_path: str
    ) -> Dict[str, Any]:
        """
        밸런스 보고서 생성

        Args:
            results: 시뮬레이션 결과 데이터프레임
            output_path: 출력 파일 경로

        Returns:
            보고서 데이터
        """
        # 밸런스 분석
        analysis = self.analyze_balance(results)

        # 문제 이벤트 식별
        problematic = self.identify_problematic_events(analysis)

        # 권장사항 생성
        recommendations = self.generate_recommendations(problematic)

        # 트레이드오프 분석
        tradeoff_analysis = self.noRightAnswer_analyze_tradeoffs()

        # 불확실성 분석
        uncertainty_analysis = self.uncertainty_analyze_variability()

        # 시각화 생성
        output_dir = os.path.dirname(output_path)
        visualization_files = self.generate_visualizations(
            results, os.path.join(output_dir, "visualizations")
        )

        # 보고서 데이터 준비
        report_data = {
            "simulation_config": self.config.model_dump(),
            "balance_metrics": {
                "bankruptcy_rate": float(analysis["bankruptcy_rate"]),
                "avg_days_survived": float(analysis["avg_days_survived"]),
                "avg_final_money": float(analysis["avg_final_money"]),
                "balance_maintained_rate": float(analysis["balance_maintained_rate"]),
                "max_cascade_depth": (
                    int(analysis["max_cascade_depth"])
                    if isinstance(analysis["max_cascade_depth"], (int, np.integer))
                    else 0
                ),
                "destruction_rate": float(analysis["destruction_rate"]),
                "destruction_threshold_exceeded": bool(
                    analysis["destruction_threshold_exceeded"]
                ),
            },
            "tradeoff_analysis": self._convert_numpy_types(tradeoff_analysis),
            "uncertainty_analysis": self._convert_numpy_types(uncertainty_analysis),
            "problematic_events": self._convert_numpy_types(problematic),
            "recommendations": recommendations,
            "visualization_files": visualization_files,
        }

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

        # JSON 보고서
        json_path = os.path.splitext(output_path)[0] + ".json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                self._convert_numpy_types(report_data), f, ensure_ascii=False, indent=2
            )

        # CSV 요약 보고서
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # 헤더
            writer.writerow(["Metric", "Value", "Threshold", "Status"])

            # 밸런스 메트릭
            bankruptcy_status = (
                "❌ 실패"
                if analysis["bankruptcy_rate"] > self.config.destruction_threshold
                else "✅ 통과"
            )
            writer.writerow(
                [
                    "파산율",
                    f"{analysis['bankruptcy_rate']:.2%}",
                    f"{self.config.destruction_threshold:.2%}",
                    bankruptcy_status,
                ]
            )

            balance_status = (
                "✅ 통과" if analysis["balance_maintained_rate"] > 0.95 else "❌ 실패"
            )
            writer.writerow(
                [
                    "행복+고통=100 유지율",
                    f"{analysis['balance_maintained_rate']:.2%}",
                    "95%",
                    balance_status,
                ]
            )

            cascade_status = (
                "✅ 통과"
                if analysis["max_cascade_depth"] <= self.config.cascade_depth_limit
                else "❌ 실패"
            )
            writer.writerow(
                [
                    "최대 연쇄 깊이",
                    analysis["max_cascade_depth"],
                    self.config.cascade_depth_limit,
                    cascade_status,
                ]
            )

            writer.writerow([])
            writer.writerow(
                ["평균 생존 일수", f"{analysis['avg_days_survived']:.1f}", "-", "-"]
            )
            writer.writerow(
                ["평균 최종 자금", f"{analysis['avg_final_money']:.1f}", "-", "-"]
            )

            # 트레이드오프 및 불확실성 메트릭
            writer.writerow([])
            writer.writerow(
                [
                    "트레이드오프 명확성 점수",
                    f"{tradeoff_analysis.get('overall_clarity_score', 0):.2f}",
                    "0.90",
                    (
                        "✅ 통과"
                        if tradeoff_analysis.get("overall_clarity_score", 0) >= 0.90
                        else "❌ 실패"
                    ),
                ]
            )
            writer.writerow(
                [
                    "불확실성 변동성 점수",
                    f"{uncertainty_analysis.get('overall_variability_score', 0):.2f}",
                    "-",
                    "-",
                ]
            )

            # 문제 이벤트
            if problematic:
                writer.writerow([])
                writer.writerow(["문제 이벤트", "카테고리", "이슈", "값", "임계값"])

                for event in problematic:
                    for issue in event["issues"]:
                        writer.writerow(
                            [
                                f"{event['id']} ({event['name']})",
                                event["category"],
                                issue["description"],
                                f"{issue['value']:.2f}",
                                f"{issue['threshold']:.2f}",
                            ]
                        )

        logger.info(f"밸런스 보고서 생성 완료: {output_path}")
        logger.info(f"JSON 보고서 생성 완료: {json_path}")
        logger.info(f"시각화 파일 생성 완료: {len(visualization_files)}개")

        return report_data


def main() -> None:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="이벤트 밸런스 시뮬레이션 도구")
    parser.add_argument("--input", required=True, help="이벤트 뱅크 디렉토리 경로")
    parser.add_argument("--output", required=True, help="출력 보고서 파일 경로")
    parser.add_argument(
        "--iterations", type=int, default=100, help="시뮬레이션 반복 횟수"
    )
    parser.add_argument("--turns", type=int, default=30, help="각 시뮬레이션의 턴 수")
    parser.add_argument("--seed", type=int, help="랜덤 시드 (재현성)")
    parser.add_argument(
        "--bankruptcy", type=float, default=-5000, help="파산 기준 자금"
    )
    parser.add_argument("--cascade-limit", type=int, default=5, help="최대 연쇄 깊이")
    parser.add_argument(
        "--destruction", type=float, default=0.05, help="허용 가능한 파괴율"
    )
    parser.add_argument("--visualize", action="store_true", help="시각화 생성")
    parser.add_argument("--verbose", action="store_true", help="상세 로깅 활성화")

    args = parser.parse_args()

    # 로깅 레벨 설정
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 시뮬레이션 설정
    config = SimulationConfig(
        iterations=args.iterations,
        turns_per_sim=args.turns,
        seed=args.seed,
        bankruptcy_threshold=args.bankruptcy,
        cascade_depth_limit=args.cascade_limit,
        destruction_threshold=args.destruction,
    )

    # 시뮬레이터 초기화
    simulator = EventSimulator(args.input, config)

    # 시뮬레이션 실행
    results = simulator.run_simulations()

    # 보고서 생성
    simulator.generate_report(results, args.output)


if __name__ == "__main__":
    main()

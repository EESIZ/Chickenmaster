from game_constants import MAGIC_NUMBER_ZERO, MAGIC_NUMBER_ONE, MAGIC_NUMBER_TWO, MAGIC_NUMBER_FIFTY, MAGIC_NUMBER_ONE_HUNDRED, PROBABILITY_LOW_THRESHOLD, PROBABILITY_HIGH_THRESHOLD
#!/usr/bin/env python3
"""
파일: dev_tools/balance_simulator.py
설명: 게임 밸런스 시뮬레이터
작성자: Manus
날짜: 2025-05-27
"""

import argparse
import json
import random
from typing import Any

from src.core.domain.game_state import GameState
from src.economy.engine import EconomyEngine
from src.events.engine import EventEngine
from src.metrics.tracker import MetricsTracker


class BalanceSimulator:
    """게임 밸런스 시뮬레이터"""

    def __init__(self, config_file: str = "data/balance_config.json"):
        """
        초기화

        Args:
            config_file: 밸런스 설정 파일 경로
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.metrics_tracker = MetricsTracker()
        self.economy_engine = EconomyEngine(self.metrics_tracker)
        self.event_engine = EventEngine(self.metrics_tracker)

    def load_config(self) -> dict[str, Any]:
        """
        밸런스 설정 로드

        Returns:
            설정 딕셔너리
        """
        try:
            with open(self.config_file, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 설정 파일을 찾을 수 없습니다: {self.config_file}")
            return self.get_default_config()
        except Exception as e:
            print(f"❌ 설정 로드 오류: {e!s}")
            return self.get_default_config()

    def get_default_config(self) -> dict[str, Any]:
        """
        기본 설정 반환

        Returns:
            기본 설정 딕셔너리
        """
        return {
            "simulation": {"days": 30, "iterations": 100, "random_seed": 42},
            "initial_metrics": {
                "money": 10000.0,
                "reputation": 50.0,
                "happiness": 50.0,
                "suffering": 20.0,
                "inventory": 100.0,
                "staff_fatigue": 30.0,
                "facility": 80.0,
                "demand": 60.0,
            },
            "scenarios": [
                {"name": "conservative", "risk_factor": PROBABILITY_LOW_THRESHOLD},
                {"name": "balanced", "risk_factor": 0.5},
                {"name": "aggressive", "risk_factor": PROBABILITY_HIGH_THRESHOLD},
            ],
        }

    def run_simulation(self, scenario: str = "balanced") -> dict[str, Any]:
        """
        시뮬레이션 실행

        Args:
            scenario: 시나리오 이름

        Returns:
            시뮬레이션 결과
        """
        config = self.config["simulation"]
        days = config["days"]
        iterations = config["iterations"]
        seed = config["random_seed"]

        # 시나리오 설정 찾기
        scenario_config = next(
            (s for s in self.config["scenarios"] if s["name"] == scenario), None
        )
        if not scenario_config:
            print(f"⚠️ 시나리오를 찾을 수 없습니다: {scenario}")
            scenario_config = self.config["scenarios"][1]  # 기본값: balanced

        results = []
        random.seed(seed)

        for iteration in range(iterations):
            # 초기 상태 설정
            self.reset_simulation()
            daily_results = []

            for day in range(days):
                # 일일 시뮬레이션
                day_result = self.simulate_day(scenario_config, day)
                daily_results.append(day_result)

                # 게임 오버 조건 확인
                if self.check_game_over():
                    break

            results.append(
                {
                    "iteration": iteration,
                    "days_survived": len(daily_results),
                    "final_metrics": self.metrics_tracker.get_metrics(),
                    "daily_results": daily_results,
                }
            )

        return self.analyze_results(results, scenario)

    def reset_simulation(self) -> None:
        """시뮬레이션 상태 초기화"""
        initial_metrics = self.config["initial_metrics"]
        self.metrics_tracker.reset()

        # 초기 지표 설정
        for metric, value in initial_metrics.items():
            self.metrics_tracker.update_metric(metric.upper(), value)

    def simulate_day(self, scenario_config: dict[str, Any], day: int) -> dict[str, Any]:
        """
        일일 시뮬레이션

        Args:
            scenario_config: 시나리오 설정
            day: 현재 날짜

        Returns:
            일일 결과
        """
        risk_factor = scenario_config["risk_factor"]

        # 경제 엔진 실행
        economy_result = self.economy_engine.process_daily_economics()

        # 이벤트 엔진 실행 (위험도에 따라 이벤트 발생 확률 조정)
        if random.random() < risk_factor:
            events = self.event_engine.evaluate_triggers()
            for event in events:
                self.event_engine.apply_effects(event)
        else:
            events = []

        return {
            "day": day,
            "metrics": self.metrics_tracker.get_metrics().copy(),
            "economy_result": economy_result,
            "events": [event.id if hasattr(event, "id") else str(event) for event in events],
            "risk_factor": risk_factor,
        }

    def check_game_over(self) -> bool:
        """
        게임 오버 조건 확인

        Returns:
            게임 오버 여부
        """
        metrics = self.metrics_tracker.get_metrics()

        # 파산 조건
        if metrics.get("money", 0) <= MAGIC_NUMBER_ZERO:
            return True

        # 극도의 스트레스 조건
        if metrics.get("suffering", 0) >= MAGIC_NUMBER_ONE_HUNDRED:
            return True

        # 평판 파탄 조건
        if metrics.get("reputation", 0) <= MAGIC_NUMBER_ZERO:
            return True

        return False

    def analyze_results(self, results: list[dict[str, Any]], scenario: str) -> dict[str, Any]:
        """
        결과 분석

        Args:
            results: 시뮬레이션 결과 목록
            scenario: 시나리오 이름

        Returns:
            분석 결과
        """
        total_iterations = len(results)
        successful_runs = [r for r in results if r["days_survived"] >= self.config["simulation"]["days"]]
        success_rate = len(successful_runs) / total_iterations

        # 평균 생존 일수
        avg_survival_days = sum(r["days_survived"] for r in results) / total_iterations

        # 최종 지표 평균
        final_metrics_avg = {}
        if successful_runs:
            for metric in self.config["initial_metrics"]:
                values = [r["final_metrics"].get(metric.upper(), 0) for r in successful_runs]
                final_metrics_avg[metric] = sum(values) / len(values)

        return {
            "scenario": scenario,
            "total_iterations": total_iterations,
            "success_rate": success_rate,
            "avg_survival_days": avg_survival_days,
            "final_metrics_avg": final_metrics_avg,
            "detailed_results": results,
        }

    def save_results(self, results: dict[str, Any], output_file: str) -> None:
        """
        결과 저장

        Args:
            results: 분석 결과
            output_file: 출력 파일 경로
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과가 {output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 결과 저장 오류: {e!s}")

    def print_summary(self, results: dict[str, Any]) -> None:
        """
        결과 요약 출력

        Args:
            results: 분석 결과
        """
        print(f"\n📊 시뮬레이션 결과 요약 - {results['scenario']}")
        print(f"총 반복 횟수: {results['total_iterations']}")
        print(f"성공률: {results['success_rate']:.1%}")
        print(f"평균 생존 일수: {results['avg_survival_days']:.1f}일")

        if results["final_metrics_avg"]:
            print("\n📈 성공한 게임의 최종 지표 평균:")
            for metric, value in results["final_metrics_avg"].items():
                print(f"  {metric}: {value:.1f}")


def main() -> None:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="게임 밸런스 시뮬레이터")
    parser.add_argument("--config", default="data/balance_config.json", help="설정 파일 경로")
    parser.add_argument("--scenario", default="balanced", help="시나리오 이름")
    parser.add_argument("--output", help="결과 출력 파일 경로")

    args = parser.parse_args()

    simulator = BalanceSimulator(args.config)
    results = simulator.run_simulation(args.scenario)

    simulator.print_summary(results)

    if args.output:
        simulator.save_results(results, args.output)


if __name__ == "__main__":
    main()


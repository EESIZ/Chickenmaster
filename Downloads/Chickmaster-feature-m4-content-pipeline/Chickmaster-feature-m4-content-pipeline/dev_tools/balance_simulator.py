"""
파일: dev_tools/balance_simulator.py
목적: 이벤트 밸런스 자동 시뮬레이션 도구
"""

from __future__ import annotations

import argparse
import json
import os
import csv
import math
import random
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union, Tuple
import tomllib  # Python 3.11+

from dev_tools.config import Config
from dev_tools.event_validator import EventValidator


class GameMetrics:
    """게임 메트릭 기본값 및 변화 추적"""
    
    def __init__(self) -> None:
        """기본 메트릭 초기화"""
        self.money = 10000  # 초기 자금
        self.reputation = 50  # 초기 평판
        self.customers = 100  # 초기 고객 수
        self.staff_morale = 70  # 초기 직원 사기
        self.food_quality = 60  # 초기 음식 품질
        self.equipment = 50  # 초기 장비 상태
        
        # 메트릭 변화 기록
        self.history: Dict[str, List[float]] = {
            "money": [self.money],
            "reputation": [self.reputation],
            "customers": [self.customers],
            "staff_morale": [self.staff_morale],
            "food_quality": [self.food_quality],
            "equipment": [self.equipment],
        }
        
    def apply_effect(self, metric: str, formula: str) -> None:
        """
        메트릭에 효과 적용
        
        Args:
            metric: 영향을 받는 메트릭 이름
            formula: 적용할 수식 (예: "-500", "value * 1.1", "-5%")
        """
        if metric.lower() not in self.history:
            raise ValueError(f"알 수 없는 메트릭: {metric}")
            
        # 현재 값 가져오기
        current_value = getattr(self, metric.lower())
        
        # 퍼센트 표기법 처리
        if formula.endswith('%'):
            percentage = float(formula[:-1]) / 100
            new_value = current_value + (current_value * percentage)
        else:
            # 간단한 수식 평가 (실제 구현에서는 안전한 평가 필요)
            try:
                # 리터럴 숫자인 경우
                delta = float(formula)
                new_value = current_value + delta
            except ValueError:
                # value를 포함한 수식인 경우
                value = current_value
                new_value = eval(formula)  # 실제 구현에서는 안전한 평가 필요
                
        # 값 업데이트 및 기록
        setattr(self, metric.lower(), new_value)
        self.history[metric.lower()].append(new_value)
        
    def get_current_state(self) -> Dict[str, float]:
        """현재 메트릭 상태 반환"""
        return {
            "money": self.money,
            "reputation": self.reputation,
            "customers": self.customers,
            "staff_morale": self.staff_morale,
            "food_quality": self.food_quality,
            "equipment": self.equipment,
        }
        
    def get_history(self) -> Dict[str, List[float]]:
        """메트릭 변화 기록 반환"""
        return self.history


class BalanceSimulator:
    def __init__(self) -> None:
        """초기화"""
        self.events: List[Dict[str, Any]] = []
        self.metrics = GameMetrics()
        self.validator = EventValidator()
        self.simulation_results: List[Dict[str, Any]] = []
        self.balance_report: Dict[str, Any] = {}
        
    def load_events(self, file_path: Path) -> bool:
        """
        이벤트 파일 로드
        
        Args:
            file_path: 이벤트 파일 경로 (TOML/JSON)
            
        Returns:
            로드 성공 여부
        """
        try:
            # 파일 확장자에 따라 로더 선택
            if file_path.suffix.lower() == '.toml':
                with open(file_path, 'rb') as f:
                    data = tomllib.load(f)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                print(f"❌ 지원하지 않는 파일 형식: {file_path.suffix}")
                return False
                
            # 이벤트 데이터 추출
            events = data.get('events', [])
            if not events:
                print(f"⚠️ 이벤트가 없습니다: {file_path}")
                return False
                
            self.events.extend(events)
            print(f"✅ {len(events)}개 이벤트 로드 완료: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 파일 로드 오류: {str(e)}")
            return False
            
    def load_events_directory(self, directory_path: Path) -> bool:
        """
        디렉토리 내 모든 이벤트 파일 로드
        
        Args:
            directory_path: 이벤트 디렉토리 경로
            
        Returns:
            로드 성공 여부
        """
        success = True
        
        # TOML 파일 먼저 처리
        for file_path in directory_path.glob('**/*.toml'):
            if not self.load_events(file_path):
                success = False
                
        # JSON 파일 처리
        for file_path in directory_path.glob('**/*.json'):
            if not self.load_events(file_path):
                success = False
                
        return success
        
    def run_simulation(self, turns: int = 100, seed: int = 42) -> None:
        """
        게임 시뮬레이션 실행
        
        Args:
            turns: 시뮬레이션할 턴 수
            seed: 랜덤 시드
        """
        random.seed(seed)
        self.simulation_results = []
        self.metrics = GameMetrics()  # 메트릭 초기화
        
        print(f"🔄 {turns}턴 시뮬레이션 시작 (시드: {seed})...")
        
        for turn in range(1, turns + 1):
            turn_events = []
            
            # 각 이벤트 발생 확률 계산
            for event in self.events:
                # RANDOM 이벤트 처리
                if event.get('type') == 'RANDOM':
                    probability = event.get('probability', 0.0)
                    if random.random() < probability:
                        turn_events.append(event)
                        
                # THRESHOLD 이벤트 처리
                elif event.get('type') == 'THRESHOLD':
                    trigger = event.get('trigger', {})
                    if self._check_trigger(trigger):
                        turn_events.append(event)
                        
                # SCHEDULED 이벤트 처리
                elif event.get('type') == 'SCHEDULED':
                    schedule = event.get('schedule', 0)
                    if schedule > 0 and turn % schedule == 0:
                        turn_events.append(event)
                        
            # 이벤트 효과 적용
            for event in turn_events:
                self._apply_event_effects(event)
                
            # 턴 결과 기록
            self.simulation_results.append({
                'turn': turn,
                'metrics': self.metrics.get_current_state(),
                'events': [e.get('id') for e in turn_events]
            })
            
        print(f"✅ 시뮬레이션 완료: {turns}턴, {len(self.events)}개 이벤트")
        
    def _check_trigger(self, trigger: Dict[str, Any]) -> bool:
        """
        트리거 조건 확인
        
        Args:
            trigger: 트리거 데이터
            
        Returns:
            조건 충족 여부
        """
        if not trigger:
            return False
            
        metric = trigger.get('metric', '').lower()
        condition = trigger.get('condition', '')
        value = trigger.get('value', 0)
        
        if not metric or not condition:
            return False
            
        current_value = getattr(self.metrics, metric, 0)
        
        if condition == 'less_than':
            return current_value < value
        elif condition == 'greater_than':
            return current_value > value
        elif condition == 'equal':
            return current_value == value
            
        return False
        
    def _apply_event_effects(self, event: Dict[str, Any]) -> None:
        """
        이벤트 효과 적용
        
        Args:
            event: 이벤트 데이터
        """
        effects = event.get('effects', [])
        for effect in effects:
            metric = effect.get('metric', '').lower()
            formula = effect.get('formula', '0')
            
            if metric:
                self.metrics.apply_effect(metric, formula)
                
    def generate_balance_report(self) -> Dict[str, Any]:
        """
        밸런스 리포트 생성
        
        Returns:
            밸런스 리포트 데이터
        """
        if not self.simulation_results:
            print("❌ 시뮬레이션 결과가 없습니다. run_simulation()을 먼저 실행하세요.")
            return {}
            
        # 메트릭 변화 분석
        metrics_history = self.metrics.get_history()
        metrics_analysis = {}
        
        for metric, values in metrics_history.items():
            if len(values) < 2:
                continue
                
            # 기본 통계
            metrics_analysis[metric] = {
                'start': values[0],
                'end': values[-1],
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'change': values[-1] - values[0],
                'change_percent': (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0,
            }
            
        # 이벤트 발생 빈도 분석
        event_frequency: Dict[str, int] = {}
        for result in self.simulation_results:
            for event_id in result.get('events', []):
                event_frequency[event_id] = event_frequency.get(event_id, 0) + 1
                
        # 밸런스 점수 계산
        balance_scores = self._calculate_balance_scores(metrics_analysis, event_frequency)
        
        # 리포트 구성
        self.balance_report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'simulation_turns': len(self.simulation_results),
            'total_events': len(self.events),
            'triggered_events': len(event_frequency),
            'metrics_analysis': metrics_analysis,
            'event_frequency': event_frequency,
            'balance_scores': balance_scores,
            'recommendations': self._generate_recommendations(metrics_analysis, balance_scores)
        }
        
        return self.balance_report
        
    def _calculate_balance_scores(
        self, metrics_analysis: Dict[str, Dict[str, float]], 
        event_frequency: Dict[str, int]
    ) -> Dict[str, float]:
        """
        밸런스 점수 계산
        
        Args:
            metrics_analysis: 메트릭 분석 데이터
            event_frequency: 이벤트 발생 빈도
            
        Returns:
            밸런스 점수
        """
        scores = {}
        
        # 1. 경제 안정성 (money 변동성)
        if 'money' in metrics_analysis:
            money = metrics_analysis['money']
            # 표준편차가 평균의 30% 이하면 안정적
            volatility = money['std_dev'] / abs(money['avg']) if money['avg'] != 0 else 999
            scores['economic_stability'] = max(0, min(1, 1 - (volatility / 0.3)))
            
        # 2. 평판 곡선 (reputation이 적절한 곡선을 그리는지)
        if 'reputation' in metrics_analysis:
            rep = metrics_analysis['reputation']
            # 시작과 끝의 차이가 너무 크지 않고, 변동이 있어야 함
            change_ratio = abs(rep['change']) / rep['start'] if rep['start'] != 0 else 999
            scores['reputation_curve'] = max(0, min(1, 1 - abs(change_ratio - 0.2) / 0.2))
            
        # 3. 이벤트 분포 균형
        if event_frequency:
            # 이벤트 발생 빈도의 표준편차가 낮을수록 균형적
            frequencies = list(event_frequency.values())
            if len(frequencies) > 1:
                avg_freq = statistics.mean(frequencies)
                std_dev = statistics.stdev(frequencies)
                cv = std_dev / avg_freq if avg_freq > 0 else 999  # 변동계수
                scores['event_distribution'] = max(0, min(1, 1 - (cv / 0.5)))
            else:
                scores['event_distribution'] = 0.0
                
        # 4. 고객 성장 곡선
        if 'customers' in metrics_analysis:
            cust = metrics_analysis['customers']
            # 고객이 꾸준히 증가하는지
            growth_rate = cust['change'] / cust['start'] if cust['start'] > 0 else 0
            scores['customer_growth'] = max(0, min(1, (growth_rate + 0.1) / 0.3)) if growth_rate < 0.3 else 1.0
            
        # 5. 직원 사기 안정성
        if 'staff_morale' in metrics_analysis:
            morale = metrics_analysis['staff_morale']
            # 직원 사기가 안정적으로 유지되는지
            morale_stability = 1 - (morale['std_dev'] / 30)  # 표준편차가 30 이하면 안정적
            scores['morale_stability'] = max(0, min(1, morale_stability))
            
        # 종합 점수
        if scores:
            scores['overall'] = statistics.mean(scores.values())
            
        return scores
        
    def _generate_recommendations(
        self, metrics_analysis: Dict[str, Dict[str, float]], 
        balance_scores: Dict[str, float]
    ) -> List[str]:
        """
        밸런스 개선 추천사항 생성
        
        Args:
            metrics_analysis: 메트릭 분석 데이터
            balance_scores: 밸런스 점수
            
        Returns:
            추천사항 목록
        """
        recommendations = []
        
        # 1. 경제 안정성 추천
        if 'economic_stability' in balance_scores:
            score = balance_scores['economic_stability']
            if score < 0.6:
                if metrics_analysis['money']['std_dev'] > metrics_analysis['money']['avg'] * 0.3:
                    recommendations.append("💰 경제 변동성이 높습니다. 이벤트의 money 효과 크기를 줄이거나 분산시키세요.")
                    
        # 2. 평판 곡선 추천
        if 'reputation_curve' in balance_scores:
            score = balance_scores['reputation_curve']
            if score < 0.6:
                rep = metrics_analysis['reputation']
                if rep['change'] > rep['start'] * 0.3:
                    recommendations.append("⭐ 평판 상승이 너무 가파릅니다. 부정적 평판 이벤트를 추가하세요.")
                elif rep['change'] < -rep['start'] * 0.3:
                    recommendations.append("⭐ 평판 하락이 너무 가파릅니다. 긍정적 평판 이벤트를 추가하세요.")
                    
        # 3. 이벤트 분포 추천
        if 'event_distribution' in balance_scores:
            score = balance_scores['event_distribution']
            if score < 0.6:
                recommendations.append("🎲 이벤트 발생 빈도가 불균형합니다. 자주 발생하는 이벤트의 확률을 낮추고, 드문 이벤트의 확률을 높이세요.")
                
        # 4. 고객 성장 추천
        if 'customer_growth' in balance_scores:
            score = balance_scores['customer_growth']
            if score < 0.6:
                cust = metrics_analysis['customers']
                if cust['change'] < 0:
                    recommendations.append("👥 고객 수가 감소하고 있습니다. 고객 유치 이벤트를 추가하거나 고객 이탈 이벤트를 줄이세요.")
                elif cust['change'] < cust['start'] * 0.1:
                    recommendations.append("👥 고객 성장이 정체되어 있습니다. 고객 유치 이벤트의 효과를 강화하세요.")
                    
        # 5. 직원 사기 추천
        if 'morale_stability' in balance_scores:
            score = balance_scores['morale_stability']
            if score < 0.6:
                recommendations.append("😊 직원 사기 변동성이 높습니다. 사기 관련 이벤트의 효과를 완화하거나 회복 이벤트를 추가하세요.")
                
        # 6. 종합 추천
        if 'overall' in balance_scores:
            score = balance_scores['overall']
            if score < 0.5:
                recommendations.append("⚠️ 전반적인 게임 밸런스가 불안정합니다. 이벤트 효과의 크기와 빈도를 재조정하세요.")
            elif score < 0.7:
                recommendations.append("⚠️ 게임 밸런스가 개선 가능합니다. 위 추천사항을 참고하여 조정하세요.")
            else:
                recommendations.append("✅ 게임 밸런스가 전반적으로 양호합니다.")
                
        return recommendations
        
    def save_report_to_json(self, output_dir: str = "reports") -> str:
        """
        밸런스 리포트를 JSON으로 저장
        
        Args:
            output_dir: 출력 디렉토리
            
        Returns:
            저장된 파일 경로
        """
        if not self.balance_report:
            print("❌ 밸런스 리포트가 없습니다. generate_balance_report()를 먼저 실행하세요.")
            return ""
            
        # 출력 디렉토리 확인 및 생성
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"balance_report_{timestamp}.json"
        
        # JSON 파일 저장
        file_path = output_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.balance_report, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 밸런스 리포트가 {file_path}에 저장되었습니다.")
        return str(file_path)
        
    def save_report_to_csv(self, output_dir: str = "reports") -> str:
        """
        메트릭 변화 기록을 CSV로 저장
        
        Args:
            output_dir: 출력 디렉토리
            
        Returns:
            저장된 파일 경로
        """
        if not self.simulation_results:
            print("❌ 시뮬레이션 결과가 없습니다. run_simulation()을 먼저 실행하세요.")
            return ""
            
        # 출력 디렉토리 확인 및 생성
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"metrics_history_{timestamp}.csv"
        
        # CSV 파일 저장
        file_path = output_path / filename
        
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # 헤더 작성
            headers = ["turn", "money", "reputation", "customers", "staff_morale", "food_quality", "equipment", "events"]
            writer.writerow(headers)
            
            # 데이터 작성
            for result in self.simulation_results:
                turn = result["turn"]
                metrics = result["metrics"]
                events = ",".join(result["events"]) if result["events"] else ""
                
                row = [
                    turn,
                    metrics["money"],
                    metrics["reputation"],
                    metrics["customers"],
                    metrics["staff_morale"],
                    metrics["food_quality"],
                    metrics["equipment"],
                    events
                ]
                writer.writerow(row)
                
        print(f"✅ 메트릭 기록이 {file_path}에 저장되었습니다.")
        return str(file_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="치킨집 경영 게임 밸런스 시뮬레이터")
    parser.add_argument(
        "--file", type=str, help="시뮬레이션할 단일 이벤트 파일 경로 (TOML 또는 JSON)"
    )
    parser.add_argument(
        "--dir", type=str, help="시뮬레이션할 이벤트 디렉토리 경로"
    )
    parser.add_argument(
        "--turns", type=int, default=100, help="시뮬레이션할 턴 수 (기본값: 100)"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="랜덤 시드 (기본값: 42)"
    )
    parser.add_argument(
        "--output", type=str, default="reports", help="출력 디렉토리 (기본값: reports)"
    )
    
    args = parser.parse_args()
    
    if not args.file and not args.dir:
        print("❌ 파일 또는 디렉토리 경로를 지정해야 합니다.")
        return 1
        
    simulator = BalanceSimulator()
    events_loaded = False
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
            return 1
            
        print(f"🔍 이벤트 파일 로드 중: {file_path}")
        events_loaded = simulator.load_events(file_path)
        
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ 디렉토리를 찾을 수 없습니다: {args.dir}")
            return 1
            
        print(f"🔍 이벤트 디렉토리 로드 중: {dir_path}")
        events_loaded = simulator.load_events_directory(dir_path)
        
    if not events_loaded:
        print("❌ 이벤트 로드 실패")
        return 1
        
    # 시뮬레이션 실행
    simulator.run_simulation(turns=args.turns, seed=args.seed)
    
    # 밸런스 리포트 생성
    report = simulator.generate_balance_report()
    if not report:
        print("❌ 밸런스 리포트 생성 실패")
        return 1
        
    # 결과 저장
    json_path = simulator.save_report_to_json(args.output)
    csv_path = simulator.save_report_to_csv(args.output)
    
    # 요약 출력
    print("\n📊 밸런스 요약:")
    if "balance_scores" in report:
        for name, score in report["balance_scores"].items():
            status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
            print(f"  {status} {name}: {score:.2f}")
            
    print("\n💡 추천사항:")
    if "recommendations" in report:
        for recommendation in report["recommendations"]:
            print(f"  • {recommendation}")
            
    return 0


if __name__ == "__main__":
    main()

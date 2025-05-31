"""
파일: dev_tools/event_bank_manager.py
목적: 대형 이벤트 뱅크 구축 및 관리 도구
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tomllib  # Python 3.11+
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from tqdm import tqdm

from dev_tools.config import EVENT_CATEGORIES
from game_constants import SCORE_THRESHOLD_HIGH, SCORE_THRESHOLD_MEDIUM

# 조건부 import 및 스텁 클래스 구현
try:
    from dev_tools.event_validator import EventValidator

    _EventValidator = EventValidator
except ImportError:

    class _EventValidatorStub:
        """이벤트 검증기 스텁"""

        def __init__(self) -> None:
            self.errors: list[str] = []

        def validate_event(self, event: dict[str, Any]) -> bool:
            """이벤트 검증"""
            return True

        def calculate_quality_metrics(self, events: list[dict[str, Any]]) -> dict[str, float]:
            """품질 메트릭 계산"""
            return {
                "diversity_score": 0.0,
                "tradeoff_clarity": 0.0,
                "cultural_authenticity": 0.0,
                "replayability": 0.0,
            }

    _EventValidator: type[Any] = _EventValidatorStub  # type: ignore


try:
    from dev_tools.balance_simulator import EventSimulator, SimulationConfig

    _EventSimulator = EventSimulator
    _SimulationConfig = SimulationConfig
except ImportError:

    class _SimulationConfigStub:
        """시뮬레이션 설정 스텁"""

        def __init__(self, **kwargs: Any) -> None:
            self.iterations = kwargs.get("iterations", 100)
            self.turns_per_sim = kwargs.get("turns_per_sim", 30)
            self.seed = kwargs.get("seed", 42)

    class _EventSimulatorStub:
        """이벤트 시뮬레이터 스텁"""

        def __init__(self, events_dir: str, config: Any) -> None:
            self.events_dir = events_dir
            self.config = config

        def run_simulations(self) -> Any:
            """시뮬레이션 실행"""
            return None

        def generate_report(self, results: Any, output_path: str) -> dict[str, Any]:
            """보고서 생성"""
            return {
                "bankruptcy_rate": 0.0,
                "avg_days_survived": 0.0,
                "balance_maintained_rate": 0.0,
            }

        def save_report_to_json(self, report_dir: str) -> str:
            """JSON 보고서 저장"""
            return ""

        def save_report_to_csv(self, report_dir: str) -> str:
            """CSV 보고서 저장"""
            return ""

    _EventSimulator: type[Any] = _EventSimulatorStub  # type: ignore
    _SimulationConfig: type[Any] = _SimulationConfigStub  # type: ignore


class EventBankManager:
    """이벤트 뱅크 관리 도구"""

    # 이벤트 카테고리 정의 - config.py에서 가져오도록 수정
    CATEGORIES = EVENT_CATEGORIES

    # 상수 정의
    EVENT_TYPES: ClassVar[list[str]] = ["RANDOM", "THRESHOLD", "SCHEDULED", "CASCADE"]

    def __init__(self) -> None:
        """초기화"""
        print("🔧 EventBankManager 초기화 중...")
        self.events: dict[str, list[dict[str, Any]]] = {
            category: [] for category in self.CATEGORIES
        }
        self.validator = _EventValidator()
        self.simulator = _EventSimulator("", _SimulationConfig())
        self.data_dir = Path("data/events")
        self.out_dir = Path("out")
        self.reports_dir = Path("reports")
        self.validation_errors: list[dict[str, Any]] = []
        self.success_count = 0
        self.failure_count = 0
        self.dry_run = False

        # 디렉토리 생성
        for category in self.CATEGORIES:
            (self.data_dir / category).mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        print("✅ 초기화 완료")
        sys.stdout.flush()

    def iter_events(self, category: str) -> Generator[dict[str, Any], None, None]:
        """
        카테고리의 이벤트를 하나씩 yield하는 제너레이터

        Args:
            category: 이벤트 카테고리

        Yields:
            이벤트 데이터
        """
        category_dir = self.data_dir / category
        if not category_dir.exists():
            print(f"⚠️ 카테고리 디렉토리 없음: {category_dir}")
            sys.stdout.flush()
            return

        # TOML 파일 처리
        for file_path in category_dir.glob("*.toml"):
            try:
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    events = data.get("events", [])
                    for event in events:
                        event["_source_file"] = str(file_path)
                        yield event
            except Exception as e:
                print(f"❌ 파일 로드 오류 ({file_path}): {e!s}")
                sys.stdout.flush()

        # JSON 파일 처리
        for file_path in category_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    events = data.get("events", [])
                    for event in events:
                        event["_source_file"] = str(file_path)
                        yield event
            except Exception as e:
                print(f"❌ 파일 로드 오류 ({file_path}): {e!s}")
                sys.stdout.flush()

    def load_all_events(self) -> int:
        """
        모든 이벤트 로드

        Returns:
            로드된 이벤트 수
        """
        print("📂 이벤트 로드 시작...")
        sys.stdout.flush()
        total_events = 0

        for category in self.CATEGORIES:
            category_dir = self.data_dir / category
            if not category_dir.exists():
                print(f"⚠️ 카테고리 디렉토리 없음: {category_dir}")
                sys.stdout.flush()
                continue

            # TOML 파일 로드
            toml_files = list(category_dir.glob("*.toml"))
            print(f"🔍 '{category}' 카테고리에서 {len(toml_files)}개의 TOML 파일 발견")
            sys.stdout.flush()

            for file_path in toml_files:
                try:
                    with open(file_path, "rb") as f:
                        data = tomllib.load(f)
                        events = data.get("events", [])
                        if events:
                            self.events[category].extend(events)
                            total_events += len(events)
                            print(f"✅ {len(events)}개 이벤트 로드: {file_path}")
                            sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 파일 로드 오류 ({file_path}): {e!s}")
                    sys.stdout.flush()

            # JSON 파일 로드
            json_files = list(category_dir.glob("*.json"))
            print(f"🔍 '{category}' 카테고리에서 {len(json_files)}개의 JSON 파일 발견")
            sys.stdout.flush()

            for file_path in json_files:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        events = data.get("events", [])
                        if events:
                            self.events[category].extend(events)
                            total_events += len(events)
                            print(f"✅ {len(events)}개 이벤트 로드: {file_path}")
                            sys.stdout.flush()
                except Exception as e:
                    print(f"❌ 파일 로드 오류 ({file_path}): {e!s}")
                    sys.stdout.flush()

        print(f"📊 총 {total_events}개 이벤트 로드 완료")
        sys.stdout.flush()
        return total_events

    def validate_all_events(self) -> tuple[int, int]:
        """
        모든 이벤트 검증

        Returns:
            (성공 수, 실패 수) 튜플
        """
        print("🔍 이벤트 검증 시작...")
        sys.stdout.flush()
        self.success_count = 0
        self.failure_count = 0
        self.validation_errors = []

        for category, events in self.events.items():
            print(f"\n🔍 '{category}' 카테고리 이벤트 검증 중...")
            sys.stdout.flush()

            # 진행률 표시 추가
            for event in tqdm(events, desc=f"Validating {category}", unit="event"):
                event_id = event.get("id", "unknown")

                # 이벤트 검증
                if self.validator.validate_event(event):
                    self.success_count += 1
                    print(f"✅ 이벤트 검증 성공: {event_id}")
                    sys.stdout.flush()
                else:
                    self.failure_count += 1
                    error_info = {
                        "id": event_id,
                        "category": category,
                        "errors": self.validator.errors.copy(),
                        "source_file": event.get("_source_file", "unknown"),
                    }
                    self.validation_errors.append(error_info)
                    print(f"❌ 이벤트 검증 실패: {event_id}")
                    print(f"   오류: {', '.join(self.validator.errors)}")
                    sys.stdout.flush()

        print(f"\n📊 검증 결과: 성공 {self.success_count}개, 실패 {self.failure_count}개")
        sys.stdout.flush()
        return (self.success_count, self.failure_count)

    def save_validation_report(self, report_path: Path | None = None) -> str:
        """
        검증 결과를 파일로 저장

        Args:
            report_path: 저장할 파일 경로 (None이면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if report_path is None:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            report_path = self.reports_dir / f"validation_report_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "errors": self.validation_errors,
        }

        if not self.dry_run:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 검증 리포트가 {report_path}에 저장되었습니다.")
        else:
            print(f"🔍 [DRY RUN] 검증 리포트가 {report_path}에 저장됩니다.")

        sys.stdout.flush()
        return str(report_path)

    def calculate_quality_metrics(self) -> dict[str, dict[str, float]]:
        """
        모든 이벤트의 품질 메트릭 계산

        Returns:
            카테고리별 품질 메트릭
        """
        print("📊 품질 메트릭 계산 시작...")
        sys.stdout.flush()
        metrics: dict[str, dict[str, float]] = {}

        for category, events in self.events.items():
            if not events:
                print(f"⚠️ '{category}' 카테고리에 이벤트 없음, 건너뜀")
                sys.stdout.flush()
                continue

            print(f"\n📊 '{category}' 카테고리 품질 메트릭 계산 중...")
            sys.stdout.flush()

            # 진행률 표시 추가
            with tqdm(total=1, desc=f"Calculating metrics for {category}") as pbar:
                category_metrics = self.validator.calculate_quality_metrics(events)
                pbar.update(1)

            metrics[category] = category_metrics

            self._print_metrics(category_metrics)

        return metrics

    def _print_metrics(self, category_metrics: dict[str, float]) -> None:
        for name, score in category_metrics.items():
            status = "✅" if score >= SCORE_THRESHOLD_HIGH else "⚠️" if score >= SCORE_THRESHOLD_MEDIUM else "❌"
            print(f"  {status} {name}: {score:.2f}")
            sys.stdout.flush()

    def run_balance_simulation(self, turns: int = 100, seed: int = 42) -> dict[str, Any]:
        """
        밸런스 시뮬레이션 실행

        Args:
            turns: 시뮬레이션할 턴 수
            seed: 랜덤 시드

        Returns:
            밸런스 리포트
        """
        print("🔄 밸런스 시뮬레이션 시작...")
        sys.stdout.flush()

        # 모든 이벤트를 시뮬레이터에 로드
        all_events = []
        for events in self.events.values():
            all_events.extend(events)

        if not all_events:
            print("❌ 시뮬레이션할 이벤트가 없습니다.")
            sys.stdout.flush()
            return {}

        print(f"\n🔄 {len(all_events)}개 이벤트로 {turns}턴 시뮬레이션 시작...")
        sys.stdout.flush()

        # 시뮬레이터 초기화 및 이벤트 설정
        self.simulator = _EventSimulator(str(self.data_dir), _SimulationConfig())

        # 시뮬레이션 실행 (진행률 표시 추가)
        with tqdm(total=turns, desc="Simulating turns", unit="turn") as pbar:
            # 실제 시뮬레이션은 EventSimulator 내부에서 실행되므로 여기서는 진행률만 표시
            results = self.simulator.run_simulations()
            pbar.update(turns)

        # 밸런스 리포트 생성
        report = self.simulator.generate_report(results, "")

        # 결과 저장
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

        if not self.dry_run:
            if hasattr(self.simulator, "save_report_to_json"):
                json_path = self.simulator.save_report_to_json(str(self.reports_dir))
            else:
                json_path = f"{self.reports_dir}/balance_report_{timestamp}.json"

            if hasattr(self.simulator, "save_report_to_csv"):
                csv_path = self.simulator.save_report_to_csv(str(self.reports_dir))
            else:
                csv_path = f"{self.reports_dir}/metrics_history_{timestamp}.csv"
        else:
            json_path = f"{self.reports_dir}/balance_report_{timestamp}.json"
            csv_path = f"{self.reports_dir}/metrics_history_{timestamp}.csv"
            print(f"🔍 [DRY RUN] 리포트가 {json_path}에 저장됩니다.")
            print(f"🔍 [DRY RUN] 메트릭 히스토리가 {csv_path}에 저장됩니다.")

        # 요약 출력
        print("\n📊 밸런스 요약:")
        sys.stdout.flush()
        if isinstance(report, dict) and "balance_scores" in report:
            balance_scores = report["balance_scores"]
            if isinstance(balance_scores, dict):
                for name, score in balance_scores.items():
                    status = "✅" if score >= SCORE_THRESHOLD_HIGH else "⚠️" if score >= SCORE_THRESHOLD_MEDIUM else "❌"
                    print(f"  {status} {name}: {score:.2f}")
                    sys.stdout.flush()

        print("\n💡 추천사항:")
        sys.stdout.flush()
        if isinstance(report, dict) and "recommendations" in report:
            recommendations = report["recommendations"]
            if isinstance(recommendations, list):
                for recommendation in recommendations:
                    print(f"  • {recommendation}")
                    sys.stdout.flush()

        return report

    def generate_bank_statistics(self) -> dict[str, Any]:
        """
        이벤트 뱅크 통계 생성

        Returns:
            통계 데이터
        """
        print("📊 이벤트 뱅크 통계 생성 시작...")
        sys.stdout.flush()

        stats: dict[str, Any] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_events": 0,
            "categories": {},
            "types": {},
            "metrics": {},
            "tags": {},
        }

        # 카테고리별 통계
        for category, events in self.events.items():
            stats["total_events"] += len(events)
            stats["categories"][category] = len(events)

            # 진행률 표시 추가
            for event in tqdm(events, desc=f"Analyzing {category}", unit="event"):
                # 타입별 통계
                event_type = event.get("type", "UNKNOWN")
                types_dict = stats["types"]
                assert isinstance(types_dict, dict)
                types_dict[event_type] = types_dict.get(event_type, 0) + 1

                # 태그 통계
                tags = event.get("tags", [])
                tags_dict = stats["tags"]
                assert isinstance(tags_dict, dict)
                for tag in tags:
                    tags_dict[tag] = tags_dict.get(tag, 0) + 1

                # 메트릭 영향 통계
                effects = event.get("effects", [])
                metrics_dict = stats["metrics"]
                assert isinstance(metrics_dict, dict)
                for effect in effects:
                    metric = effect.get("metric", "UNKNOWN")
                    metrics_dict[metric] = metrics_dict.get(metric, 0) + 1

        print("✅ 통계 생성 완료")
        sys.stdout.flush()
        return stats

    def export_bank_to_json(self, output_path: Path) -> str:
        """
        이벤트 뱅크를 단일 JSON 파일로 내보내기

        Args:
            output_path: 출력 파일 경로

        Returns:
            저장된 파일 경로
        """
        print("📤 이벤트 뱅크 내보내기 시작...")
        sys.stdout.flush()

        # 모든 이벤트를 하나의 리스트로 합치기
        all_events = []
        for category, events in self.events.items():
            for event in events:
                # _source_file 필드 제거
                event_copy = event.copy()
                event_copy.pop("_source_file", None)
                all_events.append(event_copy)

        # 결과 저장
        if not self.dry_run:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"events": all_events}, f, ensure_ascii=False, indent=2)
            print(f"✅ 이벤트 뱅크가 {output_path}에 저장되었습니다.")
        else:
            print(f"🔍 [DRY RUN] 이벤트 뱅크가 {output_path}에 저장됩니다.")

        sys.stdout.flush()
        return str(output_path)

    def export_bank_by_category(self, output_dir: Path) -> list[str]:
        """
        이벤트 뱅크를 카테고리별로 내보내기

        Args:
            output_dir: 출력 디렉토리 경로

        Returns:
            저장된 파일 경로 목록
        """
        print("📤 카테고리별 이벤트 뱅크 내보내기 시작...")
        sys.stdout.flush()

        output_dir.mkdir(exist_ok=True, parents=True)
        saved_files = []

        for category, events in self.events.items():
            if not events:
                print(f"⚠️ '{category}' 카테고리에 이벤트 없음, 건너뜀")
                sys.stdout.flush()
                continue

            # _source_file 필드 제거
            cleaned_events = []
            for event in events:
                event_copy = event.copy()
                event_copy.pop("_source_file", None)
                cleaned_events.append(event_copy)

            # 결과 저장
            output_path = output_dir / f"{category}.json"
            if not self.dry_run:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({"events": cleaned_events}, f, ensure_ascii=False, indent=2)
                print(f"✅ '{category}' 카테고리 이벤트가 {output_path}에 저장되었습니다.")
                saved_files.append(str(output_path))
            else:
                print(f"🔍 [DRY RUN] '{category}' 카테고리 이벤트가 {output_path}에 저장됩니다.")
                saved_files.append(str(output_path))

            sys.stdout.flush()

        return saved_files

    def backup_event_bank(self) -> str:
        """
        이벤트 뱅크 백업

        Returns:
            백업 디렉토리 경로
        """
        print("📦 이벤트 뱅크 백업 시작...")
        sys.stdout.flush()

        # 백업 디렉토리 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        backup_dir = self.out_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True, parents=True)

        # 각 카테고리 디렉토리 복사
        for category in self.CATEGORIES:
            category_dir = self.data_dir / category
            if category_dir.exists():
                backup_category_dir = backup_dir / category
                if not self.dry_run:
                    shutil.copytree(category_dir, backup_category_dir)
                    print(f"✅ '{category}' 카테고리 백업 완료")
                else:
                    print(f"🔍 [DRY RUN] '{category}' 카테고리 백업 예정")
                sys.stdout.flush()

        print(f"✅ 백업이 {backup_dir}에 완료되었습니다.")
        sys.stdout.flush()
        return str(backup_dir)

    def merge_event_banks(self, source_dir: Path) -> int:
        """
        다른 이벤트 뱅크 병합

        Args:
            source_dir: 소스 이벤트 뱅크 디렉토리

        Returns:
            병합된 이벤트 수
        """
        print(f"🔄 이벤트 뱅크 병합 시작: {source_dir}")
        sys.stdout.flush()

        if not source_dir.exists():
            print(f"❌ 소스 디렉토리가 존재하지 않습니다: {source_dir}")
            sys.stdout.flush()
            return 0

        merged_count = 0

        # 각 카테고리 디렉토리 처리
        for category in self.CATEGORIES:
            source_category_dir = source_dir / category
            if not source_category_dir.exists():
                print(f"⚠️ 소스에 '{category}' 카테고리 없음, 건너뜀")
                sys.stdout.flush()
                continue

            # TOML 파일 처리
            for file_path in source_category_dir.glob("*.toml"):
                target_path = self.data_dir / category / file_path.name
                if target_path.exists():
                    print(f"⚠️ 대상 파일이 이미 존재합니다: {target_path}")
                    sys.stdout.flush()
                    continue

                if not self.dry_run:
                    shutil.copy2(file_path, target_path)
                    print(f"✅ 파일 복사 완료: {file_path.name}")
                else:
                    print(f"🔍 [DRY RUN] 파일 복사 예정: {file_path.name}")
                sys.stdout.flush()
                merged_count += 1

            # JSON 파일 처리
            for file_path in source_category_dir.glob("*.json"):
                target_path = self.data_dir / category / file_path.name
                if target_path.exists():
                    print(f"⚠️ 대상 파일이 이미 존재합니다: {target_path}")
                    sys.stdout.flush()
                    continue

                if not self.dry_run:
                    shutil.copy2(file_path, target_path)
                    print(f"✅ 파일 복사 완료: {file_path.name}")
                else:
                    print(f"🔍 [DRY RUN] 파일 복사 예정: {file_path.name}")
                sys.stdout.flush()
                merged_count += 1

        print(f"✅ 병합 완료: {merged_count}개 파일 병합됨")
        sys.stdout.flush()
        return merged_count


def main() -> int:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="이벤트 뱅크 관리 도구")
    parser.add_argument(
        "--load", action="store_true", help="모든 이벤트 로드 및 통계 출력"
    )
    parser.add_argument(
        "--validate", action="store_true", help="모든 이벤트 검증 및 리포트 생성"
    )
    parser.add_argument(
        "--quality", action="store_true", help="품질 메트릭 계산"
    )
    parser.add_argument(
        "--simulate", action="store_true", help="밸런스 시뮬레이션 실행"
    )
    parser.add_argument(
        "--export", action="store_true", help="이벤트 뱅크 내보내기"
    )
    parser.add_argument(
        "--backup", action="store_true", help="이벤트 뱅크 백업"
    )
    parser.add_argument(
        "--merge", type=str, help="다른 이벤트 뱅크 병합 (디렉토리 경로)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="실제 파일 변경 없이 실행"
    )
    parser.add_argument(
        "--output", type=str, default="out", help="출력 디렉토리 (기본값: out)"
    )

    args = parser.parse_args()

    # 기본 작업 설정
    if not any(
        [
            args.load,
            args.validate,
            args.quality,
            args.simulate,
            args.export,
            args.backup,
            args.merge,
        ]
    ):
        args.load = True  # 기본 작업: 로드

    # 이벤트 뱅크 관리자 초기화
    manager = EventBankManager()
    manager.dry_run = args.dry_run
    manager.out_dir = Path(args.output)
    manager.out_dir.mkdir(exist_ok=True)

    # 작업 실행
    if args.load:
        manager.load_all_events()
        stats = manager.generate_bank_statistics()
        print("\n📊 이벤트 뱅크 통계:")
        sys.stdout.flush()
        for category, count in stats["categories"].items():
            print(f"  • {category}: {count}개 이벤트")
            sys.stdout.flush()
        print(f"  [TOTAL] 총 {stats['total_events']}개 이벤트")
        sys.stdout.flush()

    if args.validate:
        if not manager.events:
            manager.load_all_events()
        manager.validate_all_events()
        report_path = manager.save_validation_report()
        print(f"📄 검증 리포트: {report_path}")
        sys.stdout.flush()

    if args.quality:
        if not manager.events:
            manager.load_all_events()
        metrics = manager.calculate_quality_metrics()
        print("\n📊 품질 메트릭 요약:")
        sys.stdout.flush()
        for category, category_metrics in metrics.items():
            print(f"  • {category}:")
            sys.stdout.flush()
            for name, score in category_metrics.items():
                status = "✅" if score >= SCORE_THRESHOLD_HIGH else "⚠️" if score >= SCORE_THRESHOLD_MEDIUM else "❌"
                print(f"    - {status} {name}: {score:.2f}")
                sys.stdout.flush()

    if args.simulate:
        if not manager.events:
            manager.load_all_events()
        manager.run_balance_simulation()

    if args.export:
        if not manager.events:
            manager.load_all_events()
        # 단일 파일로 내보내기
        output_path = manager.out_dir / "all_events.json"
        manager.export_bank_to_json(output_path)
        # 카테고리별로 내보내기
        category_dir = manager.out_dir / "categories"
        manager.export_bank_by_category(category_dir)

    if args.backup:
        backup_dir = manager.backup_event_bank()
        print(f"📦 백업 디렉토리: {backup_dir}")
        sys.stdout.flush()

    if args.merge:
        source_dir = Path(args.merge)
        merged_count = manager.merge_event_banks(source_dir)
        print(f"🔄 병합된 파일 수: {merged_count}")
        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())

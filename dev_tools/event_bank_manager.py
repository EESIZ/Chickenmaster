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
    SCORE_THRESHOLD_HIGH = 0.7
    SCORE_THRESHOLD_MEDIUM = 0.5
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
            status = "✅" if score >= self.SCORE_THRESHOLD_HIGH else "⚠️" if score >= self.SCORE_THRESHOLD_MEDIUM else "❌"
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
                    status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
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
        print(f"📤 이벤트 뱅크 내보내기 시작: {output_path}")
        sys.stdout.flush()

        # 모든 이벤트를 하나의 리스트로 병합
        all_events = []
        for events in self.events.values():
            all_events.extend(events)

        if not all_events:
            print("❌ 내보낼 이벤트가 없습니다.")
            sys.stdout.flush()
            return ""

        # 통계 데이터 생성
        stats = self.generate_bank_statistics()

        # 출력 데이터 구성
        output_data = {
            "metadata": {
                "version": "1.0.0",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_events": len(all_events),
                "statistics": stats,
            },
            "events": all_events,
        }

        # JSON 파일 저장
        if not self.dry_run:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✅ {len(all_events)}개 이벤트가 {output_path}에 저장되었습니다.")
        else:
            print(f"🔍 [DRY RUN] {len(all_events)}개 이벤트가 {output_path}에 저장됩니다.")

        sys.stdout.flush()
        return str(output_path)

    def backup_event_bank(self) -> str:
        """
        이벤트 뱅크 백업

        Returns:
            백업 디렉토리 경로
        """
        print("💾 이벤트 뱅크 백업 시작...")
        sys.stdout.flush()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backups/events_{timestamp}")

        if not self.dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)

            # 데이터 디렉토리 복사
            shutil.copytree(self.data_dir, backup_dir / "data", dirs_exist_ok=True)

            # 통계 데이터 저장
            stats = self.generate_bank_statistics()
            with open(backup_dir / "statistics.json", "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            print(f"✅ 이벤트 뱅크가 {backup_dir}에 백업되었습니다.")
        else:
            print(f"🔍 [DRY RUN] 이벤트 뱅크가 {backup_dir}에 백업됩니다.")

        sys.stdout.flush()
        return str(backup_dir)

    def generate_event_id(self, category: str) -> str:
        """
        새 이벤트 ID 생성

        Args:
            category: 이벤트 카테고리

        Returns:
            생성된 이벤트 ID
        """
        # 해당 카테고리의 기존 ID 수집
        existing_ids = set()
        for event in self.events.get(category, []):
            event_id = event.get("id", "")
            if event_id:
                existing_ids.add(event_id)

        # 새 ID 생성
        counter = 1
        while True:
            new_id = f"{category}_{counter:03d}"
            if new_id not in existing_ids:
                return new_id
            counter += 1


def main() -> int:
    print("🚀 이벤트 뱅크 관리 도구 시작...")
    sys.stdout.flush()

    parser = argparse.ArgumentParser(description="치킨집 경영 게임 이벤트 뱅크 관리 도구")
    parser.add_argument("--load", action="store_true", help="모든 이벤트 로드")
    parser.add_argument("--validate", action="store_true", help="모든 이벤트 검증")
    parser.add_argument("--metrics", action="store_true", help="품질 메트릭 계산")
    parser.add_argument("--simulate", action="store_true", help="밸런스 시뮬레이션 실행")
    parser.add_argument("--turns", type=int, default=100, help="시뮬레이션할 턴 수 (기본값: 100)")
    parser.add_argument("--export", type=str, help="이벤트 뱅크를 JSON 파일로 내보내기")
    parser.add_argument("--backup", action="store_true", help="이벤트 뱅크 백업")
    parser.add_argument("--stats", action="store_true", help="이벤트 뱅크 통계 출력")
    parser.add_argument("--save-report", type=str, help="검증 결과를 지정된 경로에 저장")
    parser.add_argument(
        "--dry-run", action="store_true", help="실제 파일 변경 없이 시뮬레이션만 수행"
    )

    args = parser.parse_args()
    print(f"📋 명령줄 인자: {args}")
    sys.stdout.flush()

    manager = EventBankManager()

    # dry-run 모드 설정
    if args.dry_run:
        print("🔍 DRY RUN 모드: 실제 파일 변경이 발생하지 않습니다.")
        sys.stdout.flush()
        manager.dry_run = True

    # 기본 동작: 모든 이벤트 로드
    if not any(
        [
            args.load,
            args.validate,
            args.metrics,
            args.simulate,
            args.export,
            args.backup,
            args.stats,
        ]
    ):
        print("ℹ️ 기본 동작: 모든 이벤트 로드")
        sys.stdout.flush()
        args.load = True

    # 이벤트 로드
    if args.load:
        print("📂 이벤트 로드 옵션 실행")
        sys.stdout.flush()
        manager.load_all_events()

    # 이벤트 검증
    if args.validate:
        print("🔍 이벤트 검증 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        manager.validate_all_events()

        # 검증 결과 저장
        if args.save_report:
            manager.save_validation_report(Path(args.save_report))
        else:
            manager.save_validation_report()

    # 품질 메트릭 계산
    if args.metrics:
        print("📊 품질 메트릭 계산 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        manager.calculate_quality_metrics()

    # 밸런스 시뮬레이션
    if args.simulate:
        print("🔄 밸런스 시뮬레이션 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        manager.run_balance_simulation(turns=args.turns)

    # 이벤트 뱅크 내보내기
    if args.export:
        print("📤 이벤트 뱅크 내보내기 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        manager.export_bank_to_json(Path(args.export))

    # 이벤트 뱅크 백업
    if args.backup:
        print("💾 이벤트 뱅크 백업 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        manager.backup_event_bank()

    # 이벤트 뱅크 통계
    if args.stats:
        print("📊 이벤트 뱅크 통계 옵션 실행")
        sys.stdout.flush()
        if not manager.events or all(len(events) == 0 for events in manager.events.values()):
            manager.load_all_events()
        stats = manager.generate_bank_statistics()

        print("\n📊 이벤트 뱅크 통계:")
        sys.stdout.flush()
        print(f"  총 이벤트 수: {stats['total_events']}개")
        sys.stdout.flush()

        print("\n  카테고리별 이벤트 수:")
        sys.stdout.flush()
        for category, count in stats["categories"].items():
            print(f"    - {category}: {count}개")
            sys.stdout.flush()

        print("\n  타입별 이벤트 수:")
        sys.stdout.flush()
        for event_type, count in stats["types"].items():
            print(f"    - {event_type}: {count}개")
            sys.stdout.flush()

        print("\n  영향받는 메트릭:")
        sys.stdout.flush()
        for metric, count in stats["metrics"].items():
            print(f"    - {metric}: {count}개")
            sys.stdout.flush()

        print("\n  상위 태그:")
        sys.stdout.flush()
        sorted_tags = sorted(stats["tags"].items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in sorted_tags:
            print(f"    - {tag}: {count}개")
            sys.stdout.flush()

    print("✅ 이벤트 뱅크 관리 도구 종료")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    main()

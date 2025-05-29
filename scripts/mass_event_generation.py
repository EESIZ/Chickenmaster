#!/usr/bin/env python3
"""
파일: scripts/mass_event_generation.py
목적: Claude Code를 통한 치킨집 이벤트 대량 생성
작성자: Claude Code Assistant
날짜: 2025-05-29
"""

import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Any, List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dev_tools.config import Config
from dev_tools.event_generator import EventGenerator
from dev_tools.event_validator import EventValidator

# 생성 설정 상수
GENERATION_CONFIG = {
    "BATCH_SIZE": 10,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 2,
    "SAVE_INTERVAL": 10,
    "COST_PER_EVENT": 0.05,
    "HIGH_COST_WARNING": 100.0,
    "TARGET_EVENT_COUNT": 500  # 500개로 확장
}

# 카테고리별 목표 수
# 500개 목표로 확장
CATEGORY_TARGETS = {
    "daily_routine": {
        "count": 200,  # 원래 목표
        "tags": ["치킨집", "일상", "운영"],
        "description": "일상적인 치킨집 운영 이벤트"
    },
    "crisis_events": {
        "count": 100,  # 원래 목표
        "tags": ["위기", "문제", "해결"],
        "description": "위기 상황 및 문제 해결 이벤트"
    },
    "opportunity": {
        "count": 100,  # 원래 목표
        "tags": ["기회", "성장", "투자"],
        "description": "성장 기회 및 투자 관련 이벤트"
    },
    "human_drama": {
        "count": 50,  # 원래 목표
        "tags": ["인간관계", "감정", "드라마"],
        "description": "인간관계 및 감정적 상황 이벤트"
    },
    "chain_scenario": {
        "count": 50,  # 원래 목표
        "tags": ["연쇄", "복합", "시나리오"],
        "description": "연쇄 반응 및 복합 시나리오 이벤트"
    }
}

class MassEventGenerator:
    """대량 이벤트 생성기"""

    def __init__(self, num_workers: int = None):
        """
        초기화
        
        Args:
            num_workers: 동시 작업자 수 (기본값: CPU 코어 수)
        """
        self.api_key = Config.get_api_key()
        if not self.api_key:
            print("[ERROR] ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            print("set ANTHROPIC_API_KEY=your_api_key 명령으로 설정하세요.")
            sys.exit(1)

        self.num_workers = num_workers or mp.cpu_count()
        self.generator = EventGenerator(self.api_key)
        self.validator = EventValidator()

        # 출력 디렉토리 설정
        self.output_dir = project_root / "data" / "events_generated"
        self.output_dir.mkdir(exist_ok=True)

    def get_generation_plan(self) -> dict[str, dict[str, Any]]:
        """이벤트 생성 계획 반환"""
        return CATEGORY_TARGETS

    def generate_single_event(
        self, category: str, tags: list[str], attempt: int = 1
    ) -> dict[str, Any] | None:
        """단일 이벤트 생성 (재시도 로직 포함)"""
        for attempt_num in range(GENERATION_CONFIG["MAX_RETRIES"]):
            try:
                print(
                    f"[PROCESSING] {category} 이벤트 생성 중... (시도 {attempt_num + 1}/{GENERATION_CONFIG['MAX_RETRIES']})"
                )

                events = self.generator.generate_events(category, tags, count=1)

                if not events:
                    print(f"[WARNING] 이벤트 생성 실패 (시도 {attempt_num + 1})")
                    continue

                event = events[0]

                # 필수 필드 확인 (effects는 선택적)
                if not all(key in event for key in ["id", "name_ko"]):
                    print(f"[WARNING] 필수 필드 누락 (시도 {attempt_num + 1})")
                    continue

                # effects가 없거나 비어있으면 기본값 추가
                if not event.get("effects") or len(event["effects"]) == 0:
                    event["effects"] = [
                        {"metric": "MONEY", "formula": "random(50, 200)"},
                        {"metric": "REPUTATION", "formula": "random(5, 20)"}
                    ]
                    print("[INFO] 기본 effects 추가됨")

                # 검증
                if self.validator.validate_event(event):
                    print(f"[SUCCESS] 이벤트 생성 성공: {event['id']}")
                    return event
                else:
                    print(
                        f"[ERROR] 검증 실패 (시도 {attempt_num + 1}): {', '.join(self.validator.errors)}"
                    )
                    self.validator.errors = []

            except Exception as e:
                print(f"[ERROR] 생성 중 오류 (시도 {attempt_num + 1}): {e!s}")

            if attempt_num < GENERATION_CONFIG["MAX_RETRIES"] - 1:
                time.sleep(GENERATION_CONFIG["RETRY_DELAY"])

        print(f"[ERROR] {category} 이벤트 생성 실패 (모든 시도 소진)")
        return None

    def generate_batch(
        self, category: str, tags: List[str], batch_size: int
    ) -> List[Dict[str, Any]]:
        """배치 단위로 이벤트 생성"""
        events = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(self.generate_single_event, category, tags)
                for _ in range(batch_size)
            ]
            for future in as_completed(futures):
                if event := future.result():
                    events.append(event)
        return events

    def generate_category_events(
        self, category: str, target_count: int, tags: list[str]
    ) -> list[dict[str, Any]]:
        """카테고리별 이벤트 대량 생성"""
        print(f"\n🏭 {category} 카테고리 이벤트 생성 시작 (목표: {target_count}개)")

        events = []
        success_count = 0
        failure_count = 0

        for i in range(target_count):
            print(f"\n--- {category} {i+1}/{target_count} ---")

            event = self.generate_single_event(category, tags)

            if event:
                # ID 중복 방지
                event["id"] = f"{category}_{i+1:03d}_{int(time.time() % 10000)}"
                events.append(event)
                success_count += 1
            else:
                failure_count += 1

            # 중간 저장 (10개마다)
            if (i + 1) % 10 == 0:
                self.save_events(events, category, intermediate=True)
                print(f"[SAVE] 중간 저장 완료: {len(events)}개")

        # 최종 저장
        self.save_events(events, category)

        # 통계 출력
        failure_count = target_count - success_count
        print(f"\n[STATS] {category} 결과:")
        print(f"  [SUCCESS] 성공: {success_count}개")
        print(f"  [FAIL] 실패: {failure_count}개")
        print(f"  [RATE] 성공률: {success_count/target_count*100:.1f}%")

        return events

    def save_events(
        self, events: list[dict[str, Any]], category: str, intermediate: bool = False
    ) -> str:
        """이벤트 저장"""
        if not events:
            return ""

        timestamp = int(time.time())
        suffix = "_intermediate" if intermediate else ""
        filename = f"{category}_events_{timestamp}{suffix}.json"
        filepath = self.output_dir / filename

        data = {
            "metadata": {
                "category": category,
                "count": len(events),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "generator": "Claude Code Mass Generator",
            },
            "events": events,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[SAVE] 저장 완료: {filepath}")
        return str(filepath)

    def run_mass_generation(self) -> Dict[str, int]:
        """대량 생성 실행"""
        print(f"[START] Claude Code 이벤트 대량 생성 시작! (작업자 수: {self.num_workers})")
        print(f"[INFO] 출력 디렉토리: {self.output_dir}")

        plan = self.get_generation_plan()
        results = {}
        total_target = sum(plan[cat]["count"] for cat in plan)

        # 생성 계획 출력
        total_target = sum(plan[cat]["count"] for cat in plan)
        total_categories = len(plan)

        print("\n[PLAN] 생성 계획:")
        for category, info in plan.items():
            print(f"  - {category}: {info['count']}개")
        print(f"  [TOTAL] 총 목표: {total_target}개")

        # 예상 비용 계산
        estimated_cost = total_target * GENERATION_CONFIG["COST_PER_EVENT"]
        print(f"\n[COST] 예상 비용: ~${estimated_cost:.2f} (이벤트당 약 $0.05)")
        if not self._check_cost_warning(estimated_cost):
            return {}

        # 카테고리별 생성
        start_time = time.time()
        try:
            for category, info in plan.items():
                target_count = info["count"]
                generated = 0
                batch_results = []

                while generated < target_count:
                    batch_size = min(GENERATION_CONFIG["BATCH_SIZE"], target_count - generated)
                    print(
                        f"\n[BATCH] {category} 배치 생성 중... ({generated + 1}-{generated + batch_size}/{target_count})"
                    )
                    
                    events = self.generate_batch(category, info["tags"], batch_size)
                    batch_results.extend(events)
                    generated += len(events)

                    # 중간 저장
                    if len(batch_results) >= GENERATION_CONFIG["SAVE_INTERVAL"]:
                        self.save_events(batch_results, category, intermediate=True)
                        print(f"[SAVE] 중간 저장 완료: {len(batch_results)}개")
                        batch_results = []

                # 남은 결과 저장
                if batch_results:
                    self.save_events(batch_results, category)

                results[category] = generated

        except KeyboardInterrupt:
            print("\n[INTERRUPT] 사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"[ERROR] 생성 중 치명적 오류: {e!s}")

        # 결과 요약
        self._print_summary(results, plan, start_time)
        return results

    def _check_cost_warning(self, estimated_cost: float) -> bool:
        """고비용 경고 확인"""
        if estimated_cost > GENERATION_CONFIG["HIGH_COST_WARNING"]:
            print("[WARNING] 경고: 예상 비용이 $100를 초과합니다!")
            response = input("계속하시겠습니까? (y/N): ")
            return response.lower() == "y"
        return True

    def _print_summary(
        self, results: Dict[str, int], plan: Dict[str, Dict[str, Any]], start_time: float
    ) -> None:
        """결과 요약 출력"""
        end_time = time.time()
        total_generated = sum(results.values())
        total_target = sum(plan[cat]["count"] for cat in plan)

        print("\n[COMPLETE] 대량 생성 완료!")
        print(f"[TIME] 소요 시간: {end_time - start_time:.1f}초")
        print("[STATS] 생성 결과:")

        for category, count in results.items():
            target = plan[category]["count"]
            success_rate = count / target * 100 if target > 0 else 0
            print(f"  - {category}: {count}/{target} ({success_rate:.1f}%)")

        total_success_rate = total_generated / total_target * 100
        print(
            "[RATE] 전체 성공률: "
            f"{total_generated}/{total_target} "
            f"({total_success_rate:.1f}%)"
        )
        print(f"[PATH] 저장 위치: {self.output_dir}")

        # 최종 파일 저장
        self._save_final_results(results, end_time - start_time)

        # Mission Order M-4 달성 여부 확인
        total = sum(results.values())
        if total >= GENERATION_CONFIG["TARGET_EVENT_COUNT"]:
            print("\n[MISSION] Mission Order M-4 목표 달성:")
            print(f"[SUCCESS] 이벤트 뱅크 {GENERATION_CONFIG['TARGET_EVENT_COUNT']}개 목표 달성: {total}개!")
        else:
            print(f"[WARNING] 목표 미달성: {total}/{GENERATION_CONFIG['TARGET_EVENT_COUNT']}개 ({total/GENERATION_CONFIG['TARGET_EVENT_COUNT']*100:.1f}%)")

    def _save_final_results(self, results: Dict[str, int], duration: float) -> None:
        """최종 결과 저장"""
        timestamp = int(time.time())
        filename = f"events_generated_{timestamp}.json"
        filepath = self.output_dir / filename

        all_events = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "generator": "Claude Code Mass Generator",
                "duration": duration,
            },
            "results": results,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(all_events, f, ensure_ascii=False, indent=2)

        print(f"[SAVE] 저장 완료: {filepath}")


def main():
    """메인 함수"""
    generator = MassEventGenerator()
    results = generator.run_mass_generation()

    if results:
        print("\n[MISSION] Mission Order M-4 목표 달성:")
        total = sum(results.values())
        if total >= GENERATION_CONFIG["TARGET_EVENT_COUNT"]:
            print(f"[SUCCESS] 이벤트 뱅크 {GENERATION_CONFIG['TARGET_EVENT_COUNT']}개 목표 달성: {total}개!")
        else:
            print(f"[WARNING] 목표 미달성: {total}/{GENERATION_CONFIG['TARGET_EVENT_COUNT']}개 ({total/GENERATION_CONFIG['TARGET_EVENT_COUNT']*100:.1f}%)")


if __name__ == "__main__":
    main()

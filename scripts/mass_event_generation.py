#!/usr/bin/env python3
"""
파일: scripts/mass_event_generation.py
목적: Claude Code를 통한 치킨집 이벤트 대량 생성
작성자: Claude Code Assistant
날짜: 2025-05-29
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import time

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dev_tools.config import Config
from dev_tools.event_generator import EventGenerator
from dev_tools.event_validator import EventValidator


class MassEventGenerator:
    """대량 이벤트 생성기"""

    def __init__(self):
        """초기화"""
        self.api_key = Config.get_api_key()
        if not self.api_key:
            print("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            print("환경변수 또는 .env 파일에 API 키를 설정해주세요.")
            sys.exit(1)

        self.generator = EventGenerator(self.api_key)
        self.validator = EventValidator()

        # 출력 디렉토리 설정
        self.output_dir = project_root / "data" / "events_generated"
        self.output_dir.mkdir(exist_ok=True)

    def get_generation_plan(self) -> Dict[str, Dict[str, Any]]:
        """이벤트 생성 계획 반환"""
        return {
            "daily_routine": {
                "count": 50,
                "tags": ["치킨집", "일상", "운영"],
                "description": "일상적인 치킨집 운영 이벤트",
            },
            "crisis_events": {
                "count": 30,
                "tags": ["위기", "문제", "해결"],
                "description": "위기 상황 및 문제 해결 이벤트",
            },
            "opportunity": {
                "count": 30,
                "tags": ["기회", "성장", "투자"],
                "description": "성장 기회 및 투자 관련 이벤트",
            },
            "human_drama": {
                "count": 20,
                "tags": ["인간관계", "감정", "드라마"],
                "description": "인간관계 및 감정적 상황 이벤트",
            },
            "chain_scenario": {
                "count": 20,
                "tags": ["연쇄", "복합", "시나리오"],
                "description": "연쇄 반응 및 복합 시나리오 이벤트",
            },
        }

    def generate_single_event(
        self, category: str, tags: List[str], attempt: int = 1
    ) -> Dict[str, Any] | None:
        """단일 이벤트 생성 (재시도 로직 포함)"""
        max_attempts = 3

        for attempt_num in range(max_attempts):
            try:
                print(f"🔄 {category} 이벤트 생성 중... (시도 {attempt_num + 1}/{max_attempts})")

                # 이벤트 생성
                events = self.generator.generate_events(category, tags, count=1)

                if not events:
                    print(f"⚠️ 이벤트 생성 실패 (시도 {attempt_num + 1})")
                    continue

                event = events[0]

                # 기본 검증
                if not all(key in event for key in ["id", "name_ko", "effects"]):
                    print(f"⚠️ 필수 필드 누락 (시도 {attempt_num + 1})")
                    continue

                # effects 필드가 비어있으면 기본값 추가
                if not event.get("effects"):
                    event["effects"] = [{"metric": "MONEY", "formula": "50"}]

                # validator 검증
                if self.validator.validate_event(event):
                    print(f"✅ 이벤트 생성 성공: {event['id']}")
                    return event
                else:
                    print(
                        f"❌ 검증 실패 (시도 {attempt_num + 1}): {', '.join(self.validator.errors)}"
                    )
                    self.validator.errors = []  # 오류 목록 초기화

            except Exception as e:
                print(f"❌ 생성 중 오류 (시도 {attempt_num + 1}): {str(e)}")

            # 재시도 전 잠시 대기 (API 제한 고려)
            if attempt_num < max_attempts - 1:
                time.sleep(2)

        print(f"❌ {category} 이벤트 생성 실패 (모든 시도 소진)")
        return None

    def generate_category_events(
        self, category: str, target_count: int, tags: List[str]
    ) -> List[Dict[str, Any]]:
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
                print(f"💾 중간 저장 완료: {len(events)}개")

        # 최종 저장
        self.save_events(events, category)

        print(f"\n📊 {category} 결과:")
        print(f"  ✅ 성공: {success_count}개")
        print(f"  ❌ 실패: {failure_count}개")
        print(f"  📈 성공률: {success_count/target_count*100:.1f}%")

        return events

    def save_events(
        self, events: List[Dict[str, Any]], category: str, intermediate: bool = False
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

        print(f"💾 저장 완료: {filepath}")
        return str(filepath)

    def run_mass_generation(self) -> Dict[str, int]:
        """대량 생성 실행"""
        print("🚀 Claude Code 이벤트 대량 생성 시작!")
        print(f"📁 출력 디렉토리: {self.output_dir}")

        plan = self.get_generation_plan()
        results = {}
        total_target = sum(plan[cat]["count"] for cat in plan)

        print("\n📋 생성 계획:")
        for category, info in plan.items():
            print(f"  • {category}: {info['count']}개 ({info['description']})")
        print(f"  📊 총 목표: {total_target}개")

        # 사용자 확인
        print(f"\n💰 예상 비용: ~${total_target * 0.05:.2f} (이벤트당 약 $0.05)")
        response = input("계속 진행하시겠습니까? (y/N): ")

        if response.lower() != "y":
            print("❌ 사용자에 의해 취소되었습니다.")
            return {}

        # 카테고리별 생성
        start_time = time.time()

        for category, info in plan.items():
            try:
                events = self.generate_category_events(category, info["count"], info["tags"])
                results[category] = len(events)

            except KeyboardInterrupt:
                print("\n⚠️ 사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                print(f"❌ {category} 생성 중 치명적 오류: {str(e)}")
                results[category] = 0

        # 결과 요약
        end_time = time.time()
        total_generated = sum(results.values())

        print("\n🎉 대량 생성 완료!")
        print(f"⏱️ 소요 시간: {end_time - start_time:.1f}초")
        print("📊 생성 결과:")

        for category, count in results.items():
            target = plan[category]["count"]
            success_rate = count / target * 100 if target > 0 else 0
            print(f"  • {category}: {count}/{target} ({success_rate:.1f}%)")

        print(
            f"📈 전체 성공률: {total_generated}/{total_target} ({total_generated/total_target*100:.1f}%)"
        )
        print(f"📁 저장 위치: {self.output_dir}")

        return results


def main():
    """메인 함수"""
    generator = MassEventGenerator()
    results = generator.run_mass_generation()

    if results:
        print("\n🎯 Mission Order M-4 목표 달성:")
        total = sum(results.values())
        if total >= 500:
            print(f"✅ 이벤트 뱅크 500개 목표 달성: {total}개!")
        else:
            print(f"⚠️ 목표 미달성: {total}/500개 ({total/500*100:.1f}%)")


if __name__ == "__main__":
    main()

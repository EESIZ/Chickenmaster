#!/usr/bin/env python3
"""
파일: dev_tools/event_bank_indexer.py
설명: 이벤트 뱅크 메타데이터 인덱싱 및 관리 도구
작성자: Manus
날짜: 2025-05-27
"""

import json
import argparse
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class EventBankIndexer:
    """이벤트 뱅크 메타데이터 인덱싱 및 관리 클래스"""

    def __init__(self, input_file: str, output_dir: str = "data/events"):
        """
        초기화

        Args:
            input_file: 입력 이벤트 JSON 파일 경로
            output_dir: 이벤트 뱅크 루트 디렉토리 경로
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.metadata_file = os.path.join(output_dir, "metadata.json")

    def load_events(self) -> Dict[str, Any]:
        """
        이벤트 JSON 파일 로드

        Returns:
            이벤트 데이터 딕셔너리
        """
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 파일 로드 오류: {str(e)}")
            return {"events": []}

    def load_metadata(self) -> Dict[str, Any]:
        """
        메타데이터 파일 로드 (없으면 새로 생성)

        Returns:
            메타데이터 딕셔너리
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 메타데이터 로드 오류: {str(e)}, 새로 생성합니다.")

        # 기본 메타데이터 구조
        return {
            "last_updated": datetime.now().isoformat(),
            "total_events": 0,
            "categories": {},
            "tags": {},
            "metrics": {
                "diversity_score": 0.0,
                "tradeoff_clarity": 0.0,
                "cultural_authenticity": 0.0,
                "replayability": 0.0,
            },
        }

    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        메타데이터 파일 저장

        Args:
            metadata: 저장할 메타데이터 딕셔너리
        """
        try:
            # 메타데이터 파일 디렉토리 생성
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)

            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"✅ 메타데이터가 {self.metadata_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 메타데이터 저장 오류: {str(e)}")

    def integrate_events(
        self, events: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        이벤트를 카테고리별로 통합하고 메타데이터 업데이트

        Args:
            events: 이벤트 리스트
            metadata: 현재 메타데이터

        Returns:
            업데이트된 메타데이터
        """
        # 통합 결과 카운터
        integrated_count = 0
        category_counts = {}
        tag_counts = {}  # 태그별 카운트를 추적하는 딕셔너리

        for event in events:
            # 카테고리 확인
            category = event.get("category", "unknown")
            if category not in category_counts:
                category_counts[category] = 0

            # 카테고리 디렉토리 생성
            category_dir = os.path.join(self.output_dir, category)
            os.makedirs(category_dir, exist_ok=True)

            # 이벤트 ID 확인
            event_id = event.get(
                "id",
                f"{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{integrated_count}",
            )

            # 이벤트 파일 저장
            event_file = os.path.join(category_dir, f"{event_id}.json")
            try:
                with open(event_file, "w", encoding="utf-8") as f:
                    json.dump(event, f, ensure_ascii=False, indent=2)
                integrated_count += 1
                category_counts[category] += 1

                # 태그 수집 및 카운트
                if "tags" in event and isinstance(event["tags"], list):
                    for tag in event["tags"]:
                        if tag not in tag_counts:
                            tag_counts[tag] = 0
                        tag_counts[tag] += 1

                print(f"✅ 이벤트 {event_id} 통합 완료")
            except Exception as e:
                print(f"❌ 이벤트 {event_id} 통합 오류: {str(e)}")

        # 메타데이터 업데이트
        metadata["last_updated"] = datetime.now().isoformat()
        metadata["total_events"] += integrated_count

        # 카테고리 정보 업데이트
        for category, count in category_counts.items():
            if category not in metadata["categories"]:
                metadata["categories"][category] = {"count": 0}
            metadata["categories"][category]["count"] += count

        # 태그 정보 업데이트 - 수정된 로직
        for tag, count in tag_counts.items():
            if tag not in metadata["tags"]:
                metadata["tags"][tag] = 0
            metadata["tags"][tag] += count  # 태그별 카운트 누적

        print(f"✅ 총 {integrated_count}개 이벤트가 통합되었습니다.")
        return metadata

    def update_metrics(
        self, metadata: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        품질 메트릭 업데이트

        Args:
            metadata: 현재 메타데이터
            metrics: 새로운 메트릭 값

        Returns:
            업데이트된 메타데이터
        """
        # 기존 메트릭과 새 메트릭의 가중 평균 계산
        if "metrics" not in metadata:
            metadata["metrics"] = {}

        for key, value in metrics.items():
            if key not in metadata["metrics"]:
                metadata["metrics"][key] = 0.0

            # 단순 이동 평균 (최신 값에 더 높은 가중치)
            metadata["metrics"][key] = 0.7 * value + 0.3 * metadata["metrics"][key]

        return metadata

    def process(self, metrics: Optional[Dict[str, float]] = None) -> None:
        """
        이벤트 통합 및 메타데이터 업데이트 메인 메서드

        Args:
            metrics: 품질 메트릭 딕셔너리 (선택 사항)
        """
        # 이벤트 로드
        data = self.load_events()

        if "events" not in data or not data["events"]:
            print("❌ 이벤트 데이터가 없습니다.")
            return

        # 메타데이터 로드
        metadata = self.load_metadata()

        # 이벤트 통합 및 메타데이터 업데이트
        metadata = self.integrate_events(data["events"], metadata)

        # 품질 메트릭 업데이트 (제공된 경우)
        if metrics:
            metadata = self.update_metrics(metadata, metrics)

        # 메타데이터 저장
        self.save_metadata(metadata)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="이벤트 뱅크 메타데이터 인덱싱 및 관리 도구"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="입력 이벤트 JSON 파일 경로"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="data/events",
        help="이벤트 뱅크 루트 디렉토리 경로",
    )
    parser.add_argument("--diversity", type=float, help="다양성 점수 (0.0-1.0)")
    parser.add_argument(
        "--tradeoff", type=float, help="트레이드오프 명확성 점수 (0.0-1.0)"
    )
    parser.add_argument(
        "--authenticity", type=float, help="문화적 진정성 점수 (0.0-1.0)"
    )
    parser.add_argument(
        "--replayability", type=float, help="재플레이 가치 점수 (0.0-1.0)"
    )

    args = parser.parse_args()

    # 품질 메트릭 수집 (제공된 경우)
    metrics = {}
    if args.diversity is not None:
        metrics["diversity_score"] = args.diversity
    if args.tradeoff is not None:
        metrics["tradeoff_clarity"] = args.tradeoff
    if args.authenticity is not None:
        metrics["cultural_authenticity"] = args.authenticity
    if args.replayability is not None:
        metrics["replayability"] = args.replayability

    indexer = EventBankIndexer(args.input, args.output_dir)
    indexer.process(metrics if metrics else None)


if __name__ == "__main__":
    main()

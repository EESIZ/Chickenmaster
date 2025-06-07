#!/usr/bin/env python3
"""
파일: dev_tools/event_bank_indexer.py
설명: 이벤트 뱅크 메타데이터 인덱싱 및 관리 도구
작성자: Manus
날짜: 2025-05-27
"""

import argparse
import json
import os
from datetime import datetime
from typing import Any, TypedDict


class EventMetadata(TypedDict):
    """이벤트 메타데이터 타입"""

    id: str
    category: str
    type: str
    name_ko: str
    name_en: str
    tags: list[str]
    probability: float
    cooldown: int
    trigger: dict[str, Any]
    metrics: dict[str, float]
    last_modified: str


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

    def load_events(self) -> list[dict[str, Any]]:
        """
        이벤트 JSON 파일 로드

        Returns:
            이벤트 데이터 리스트
        """
        try:
            with open(self.input_file, encoding="utf-8") as f:
                data = json.load(f)
                # 리스트 형태의 데이터도 처리
                if isinstance(data, list):
                    return data
                # 딕셔너리 형태에서 events 키가 있는 경우
                elif isinstance(data, dict) and "events" in data:
                    return data["events"]
                else:
                    return []
        except Exception as e:
            print(f"❌ 파일 로드 오류: {e!s}")
            return []

    def load_metadata(self) -> dict[str, EventMetadata]:
        """
        메타데이터 JSON 파일 로드

        Returns:
            메타데이터 딕셔너리
        """
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        return {}
                    return data
        except Exception as e:
            print(f"❌ 메타데이터 로드 오류: {e!s}")
        return {}

    def save_metadata(self, metadata: dict[str, EventMetadata]) -> None:
        """
        메타데이터 JSON 파일 저장

        Args:
            metadata: 저장할 메타데이터 딕셔너리
        """
        try:
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"✅ 메타데이터가 {self.metadata_file}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 메타데이터 저장 오류: {e!s}")

    def update_metadata(
        self, events: list[dict[str, Any]], metrics: dict[str, float] | None = None
    ) -> dict[str, EventMetadata]:
        """
        이벤트 메타데이터 업데이트

        Args:
            events: 이벤트 목록
            metrics: 품질 메트릭 (선택사항)

        Returns:
            업데이트된 메타데이터 딕셔너리
        """
        metadata = self.load_metadata()
        current_time = datetime.now().isoformat()

        for event in events:
            event_id = event.get("id", "")
            if not event_id:
                continue

            # 기존 메타데이터가 없으면 새로 생성
            if event_id not in metadata:
                metadata[event_id] = EventMetadata(
                    id=event_id,
                    category=event.get("category", ""),
                    type=event.get("type", ""),
                    name_ko=event.get("name_ko", ""),
                    name_en=event.get("name_en", ""),
                    tags=list(event.get("tags", [])),  # set을 list로 변경
                    probability=event.get("probability", 0.0),
                    cooldown=event.get("cooldown", 0),
                    trigger=event.get("trigger", {}),
                    metrics={},
                    last_modified=current_time,
                )

            # 기존 메타데이터 업데이트
            else:
                metadata[event_id].update(
                    {
                        "category": event.get("category", metadata[event_id]["category"]),
                        "type": event.get("type", metadata[event_id]["type"]),
                        "name_ko": event.get("name_ko", metadata[event_id]["name_ko"]),
                        "name_en": event.get("name_en", metadata[event_id]["name_en"]),
                        "tags": list(event.get("tags", list(metadata[event_id]["tags"]))),
                        "probability": event.get("probability", metadata[event_id]["probability"]),
                        "cooldown": event.get("cooldown", metadata[event_id]["cooldown"]),
                        "trigger": event.get("trigger", metadata[event_id]["trigger"]),
                        "last_modified": current_time,
                    }
                )

            # 품질 메트릭 업데이트 (제공된 경우)
            if metrics:
                metadata[event_id]["metrics"] = metrics

        return metadata

    def process(self) -> None:
        """이벤트 메타데이터 인덱싱 프로세스 실행"""
        # 이벤트 로드
        events = self.load_events()

        if not events:
            print("❌ 이벤트 데이터가 없습니다.")
            return

        # 메타데이터 업데이트
        metadata = self.update_metadata(events)

        # 메타데이터 저장
        self.save_metadata(metadata)


def main() -> None:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="이벤트 뱅크 메타데이터 인덱싱 도구")
    parser.add_argument("input", help="입력 이벤트 JSON 파일 경로")
    parser.add_argument("output_dir", help="이벤트 뱅크 루트 디렉토리 경로")

    args = parser.parse_args()
    indexer = EventBankIndexer(args.input, args.output_dir)
    indexer.process()


if __name__ == "__main__":
    main()

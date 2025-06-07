#!/usr/bin/env python3
"""
파일: tests/test_event_tools.py
설명: 이벤트 생성 및 관리 도구 테스트
작성자: Manus
날짜: 2025-05-27
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dev_tools.event_bank_indexer import EventBankIndexer
from dev_tools.event_condition_fixer import EventConditionFixer

# 테스트 상수
TEST_EVENT_COUNT = 2
TEST_CHOICES_COUNT = 2
TEST_METADATA_COUNT = 2


class TestEventConditionFixer(unittest.TestCase):
    """이벤트 조건 수정 도구 테스트"""

    def setUp(self) -> None:
        """테스트 데이터 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "test_events.json")
        self.output_file = os.path.join(self.test_dir, "fixed_events.json")

        # 테스트 이벤트 데이터 생성
        self.test_events = {
            "test_event_1": {
                "trigger": {"condition": "less"},
                "effects": [{"metric": "money", "formula": "-500"}],
            },
            "test_event_2": {
                "trigger": {"condition": "greater"},
                "effects": [{"metric": "reputation", "formula": "+10"}],
            },
        }

        # 테스트 파일 작성
        with open(self.input_file, encoding="utf-8") as f:
            json.dump(self.test_events, f, indent=2)

    def tearDown(self) -> None:
        """테스트 데이터 정리"""
        shutil.rmtree(self.test_dir)

    def test_process_tradeoff(self) -> None:
        """트레이드오프 이벤트 처리 테스트"""
        fixer = EventConditionFixer(self.input_file, self.output_file)
        fixed_events = fixer.process_tradeoff()

        # 조건이 올바르게 수정되었는지 확인
        assert fixed_events[0]["trigger"]["condition"] == "less_than"
        assert fixed_events[1]["trigger"]["condition"] == "greater_than"

    def test_process_no_right_answer(self) -> None:
        """정답이 없는 상황 테스트"""
        fixer = EventConditionFixer(self.input_file, self.output_file)
        _ = fixer.process_no_right_answer()  # 사용하지 않음을 명시

        # 출력 파일 로드
        with open(self.output_file, encoding="utf-8") as f:
            fixed_data = json.load(f)

        # 데이터가 올바르게 저장되었는지 확인
        assert len(fixed_data) == TEST_EVENT_COUNT
        assert all("trigger" in event for event in fixed_data.values())
        assert all("effects" in event for event in fixed_data.values())


class TestEventBankIndexer(unittest.TestCase):
    """이벤트 뱅크 인덱서 테스트"""

    def setUp(self) -> None:
        """테스트 데이터 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "test_events.json")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.metadata_file = os.path.join(self.output_dir, "metadata.json")

        # 테스트 이벤트 데이터 생성
        self.test_events = {
            "test_event_1": {
                "data": {
                    "name": "테스트 이벤트",
                    "category": "daily_routine",
                    "tags": ["돈"],
                    "choices": [
                        {"text": "선택 1", "effects": []},
                        {"text": "선택 2", "effects": []},
                    ],
                }
            },
            "cascade_event_1": {
                "data": {
                    "name": "연쇄 이벤트",
                    "category": "daily_routine",
                    "tags": ["돈"],
                    "choices": [
                        {"text": "선택 1", "effects": []},
                        {"text": "선택 2", "effects": []},
                    ],
                }
            },
        }

        # 테스트 파일 작성
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.input_file, encoding="utf-8") as f:
            json.dump(self.test_events, f, indent=2)

    def tearDown(self) -> None:
        """테스트 데이터 정리"""
        shutil.rmtree(self.test_dir)

    def test_process_tradeoff(self) -> None:
        """트레이드오프 이벤트 처리 테스트"""
        indexer = EventBankIndexer(self.input_file, self.output_dir)
        simulator = indexer.process_tradeoff()

        # 이벤트 로드 확인
        assert len(simulator.events) == TEST_EVENT_COUNT
        assert "test_event_1" in simulator.events
        assert "cascade_event_1" in simulator.events

        # 이벤트 데이터 확인
        test_event = simulator.events["test_event_1"]["data"]
        assert test_event["name"] == "테스트 이벤트"
        assert len(test_event["choices"]) == TEST_CHOICES_COUNT

        # 메타데이터 확인
        assert simulator.metadata["total_events"] == TEST_METADATA_COUNT
        assert simulator.metadata["categories"]["daily_routine"] == TEST_METADATA_COUNT
        assert simulator.metadata["tags"]["돈"] == TEST_METADATA_COUNT

    def test_process_no_right_answer(self) -> None:
        """정답이 없는 상황 테스트"""
        indexer = EventBankIndexer(self.input_file, self.output_dir)
        indexer.process_no_right_answer()

        # 메타데이터 파일 확인
        assert os.path.exists(self.metadata_file)

        # 메타데이터 로드
        with open(self.metadata_file, encoding="utf-8") as f:
            metadata = json.load(f)

        # 메타데이터 검증
        assert "total_events" in metadata
        assert "categories" in metadata
        assert "tags" in metadata


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
파일: tests/test_event_tools.py
설명: 이벤트 생성 및 관리 도구 테스트
작성자: Manus
날짜: 2025-05-27
"""

import json
import os
import unittest
import tempfile
import shutil
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dev_tools.event_condition_fixer import EventConditionFixer
from dev_tools.event_bank_indexer import EventBankIndexer


class TestEventConditionFixer(unittest.TestCase):
    """이벤트 조건 교정 도구 테스트 클래스"""

    def setUp(self) -> None:
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()

        # 테스트 이벤트 데이터
        self.test_events = {
            "events": [
                {
                    "id": "test_event_001",
                    "category": "daily_routine",
                    "type": "THRESHOLD",
                    "name_ko": "테스트 이벤트",
                    "name_en": "Test Event",
                    "trigger": {
                        "metric": "MONEY",
                        "condition": "greater_than_or_equal",
                        "value": 1000,
                    },
                },
                {
                    "id": "test_event_002",
                    "category": "daily_routine",
                    "type": "THRESHOLD",
                    "name_ko": "테스트 이벤트 2",
                    "name_en": "Test Event 2",
                    "trigger": {
                        "metric": "REPUTATION",
                        "condition": "less_than_or_equal",
                        "value": 50,
                    },
                },
            ]
        }

        # 테스트 이벤트 파일 생성
        self.input_file = os.path.join(self.test_dir, "test_events.json")
        with open(self.input_file, "w", encoding="utf-8") as f:
            json.dump(self.test_events, f, ensure_ascii=False, indent=2)

        # 출력 파일 경로
        self.output_file = os.path.join(self.test_dir, "test_events_fixed.json")

    def tearDown(self) -> None:
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.test_dir)

    def test_condition_mapping_tradeoff(self) -> None:
        """조건 매핑 트레이드오프 테스트"""
        fixer = EventConditionFixer(self.input_file, self.output_file)

        # 지원되지 않는 조건이 지원되는 조건으로 매핑되는지 확인
        self.assertEqual(
            fixer.CONDITION_MAPPING["greater_than_or_equal"], "greater_than"
        )
        self.assertEqual(fixer.CONDITION_MAPPING["less_than_or_equal"], "less_than")

        # 지원되는 조건은 그대로 유지되는지 확인
        self.assertEqual(fixer.CONDITION_MAPPING["greater_than"], "greater_than")
        self.assertEqual(fixer.CONDITION_MAPPING["less_than"], "less_than")
        self.assertEqual(fixer.CONDITION_MAPPING["equal"], "equal")

    def test_fix_trigger_conditions_uncertainty(self) -> None:
        """트리거 조건 수정 불확실성 테스트"""
        fixer = EventConditionFixer(self.input_file, self.output_file)

        # 이벤트 로드
        data = fixer.load_events()

        # 트리거 조건 수정
        fixed_events = fixer.fix_trigger_conditions(data["events"])

        # 수정된 조건 확인
        self.assertEqual(fixed_events[0]["trigger"]["condition"], "greater_than")
        self.assertEqual(fixed_events[1]["trigger"]["condition"], "less_than")

    def test_process_noRightAnswer(self) -> None:
        """전체 프로세스 테스트 - 정답이 없는 상황"""
        fixer = EventConditionFixer(self.input_file, self.output_file)

        # 프로세스 실행
        fixer.process()

        # 출력 파일 확인
        self.assertTrue(os.path.exists(self.output_file))

        # 출력 파일 로드
        with open(self.output_file, "r", encoding="utf-8") as f:
            fixed_data = json.load(f)

        # 수정된 조건 확인
        self.assertEqual(
            fixed_data["events"][0]["trigger"]["condition"], "greater_than"
        )
        self.assertEqual(fixed_data["events"][1]["trigger"]["condition"], "less_than")


class TestEventBankIndexer(unittest.TestCase):
    """이벤트 뱅크 인덱서 테스트 클래스"""

    def setUp(self) -> None:
        """테스트 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "events")

        # 테스트 이벤트 데이터
        self.test_events = {
            "events": [
                {
                    "id": "test_event_001",
                    "category": "daily_routine",
                    "type": "RANDOM",
                    "name_ko": "테스트 이벤트",
                    "name_en": "Test Event",
                    "tags": ["테스트", "일상"],
                },
                {
                    "id": "test_event_002",
                    "category": "crisis_events",
                    "type": "RANDOM",
                    "name_ko": "테스트 위기 이벤트",
                    "name_en": "Test Crisis Event",
                    "tags": ["테스트", "위기"],
                },
            ]
        }

        # 테스트 이벤트 파일 생성
        self.input_file = os.path.join(self.test_dir, "test_events.json")
        with open(self.input_file, "w", encoding="utf-8") as f:
            json.dump(self.test_events, f, ensure_ascii=False, indent=2)

        # 메타데이터 파일 경로
        self.metadata_file = os.path.join(self.output_dir, "metadata.json")

    def tearDown(self) -> None:
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.test_dir)

    def test_integrate_events_tradeoff(self) -> None:
        """이벤트 통합 트레이드오프 테스트"""
        indexer = EventBankIndexer(self.input_file, self.output_dir)

        # 메타데이터 초기화
        metadata = indexer.load_metadata()

        # 이벤트 통합
        updated_metadata = indexer.integrate_events(
            self.test_events["events"], metadata
        )

        # 통합 결과 확인
        self.assertEqual(updated_metadata["total_events"], 2)
        self.assertEqual(updated_metadata["categories"]["daily_routine"]["count"], 1)
        self.assertEqual(updated_metadata["categories"]["crisis_events"]["count"], 1)

        # 태그 확인
        self.assertEqual(updated_metadata["tags"]["테스트"], 2)
        self.assertEqual(updated_metadata["tags"]["일상"], 1)
        self.assertEqual(updated_metadata["tags"]["위기"], 1)

    def test_update_metrics_uncertainty(self) -> None:
        """메트릭 업데이트 불확실성 테스트"""
        indexer = EventBankIndexer(self.input_file, self.output_dir)

        # 메타데이터 초기화
        metadata = indexer.load_metadata()

        # 테스트 메트릭
        test_metrics = {
            "diversity_score": 0.8,
            "tradeoff_clarity": 0.7,
            "cultural_authenticity": 0.9,
            "replayability": 0.6,
        }

        # 메트릭 업데이트
        updated_metadata = indexer.update_metrics(metadata, test_metrics)

        # 업데이트 결과 확인 (가중 평균 검증)
        self.assertAlmostEqual(
            updated_metadata["metrics"]["diversity_score"], 0.8 * 0.7, places=2
        )
        self.assertAlmostEqual(
            updated_metadata["metrics"]["tradeoff_clarity"], 0.7 * 0.7, places=2
        )
        self.assertAlmostEqual(
            updated_metadata["metrics"]["cultural_authenticity"], 0.9 * 0.7, places=2
        )
        self.assertAlmostEqual(
            updated_metadata["metrics"]["replayability"], 0.6 * 0.7, places=2
        )

    def test_process_noRightAnswer(self) -> None:
        """전체 프로세스 테스트 - 정답이 없는 상황"""
        indexer = EventBankIndexer(self.input_file, self.output_dir)

        # 테스트 메트릭
        test_metrics = {
            "diversity_score": 0.8,
            "tradeoff_clarity": 0.7,
            "cultural_authenticity": 0.9,
            "replayability": 0.6,
        }

        # 프로세스 실행
        indexer.process(test_metrics)

        # 메타데이터 파일 확인
        self.assertTrue(os.path.exists(self.metadata_file))

        # 카테고리 디렉토리 확인
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "daily_routine")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "crisis_events")))

        # 이벤트 파일 확인
        self.assertTrue(
            os.path.exists(
                os.path.join(self.output_dir, "daily_routine", "test_event_001.json")
            )
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(self.output_dir, "crisis_events", "test_event_002.json")
            )
        )

        # 메타데이터 로드
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # 메타데이터 확인
        self.assertEqual(metadata["total_events"], 2)
        self.assertEqual(metadata["categories"]["daily_routine"]["count"], 1)
        self.assertEqual(metadata["categories"]["crisis_events"]["count"], 1)
        self.assertEqual(metadata["tags"]["테스트"], 2)


if __name__ == "__main__":
    unittest.main()

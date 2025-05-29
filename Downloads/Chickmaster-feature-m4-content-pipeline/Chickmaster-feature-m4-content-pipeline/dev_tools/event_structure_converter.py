#!/usr/bin/env python3
"""
파일: dev_tools/event_structure_converter.py
설명: 이벤트 구조를 표준 템플릿에 맞게 변환하는 도구
작성자: Manus AI
날짜: 2025-05-27
"""

import json
import argparse
import re
import os
from typing import Dict, List, Any, Union


def convert_effects_structure(effects_dict: Dict) -> List[Dict]:
    """
    effects 딕셔너리 구조를 표준 배열 구조로 변환
    
    입력:
    {
        "immediate": {"metric1": value1, ...},
        "delayed": {"metric2": value2, ...}
    }
    
    출력:
    [
        {"metric": "METRIC1", "formula": "value + value1", "message": "metric1이 변경되었습니다."},
        {"metric": "METRIC2", "formula": "value + value2", "message": "metric2가 변경되었습니다."}
    ]
    """
    result = []
    
    # immediate 효과 처리
    if "immediate" in effects_dict:
        for metric, value in effects_dict["immediate"].items():
            formula = f"value + {value}" if value >= 0 else f"value - {abs(value)}"
            message = f"{metric}이(가) {'증가' if value >= 0 else '감소'}했습니다."
            result.append({
                "metric": metric.upper(),
                "formula": formula,
                "message": message
            })
    
    # delayed 효과 처리
    if "delayed" in effects_dict:
        for metric, value in effects_dict["delayed"].items():
            formula = f"value + {value}" if value >= 0 else f"value - {abs(value)}"
            message = f"{metric}이(가) {'증가' if value >= 0 else '감소'}했습니다."
            result.append({
                "metric": metric.upper(),
                "formula": formula,
                "message": message
            })
    
    return result


def add_trigger_field(event: Dict) -> Dict:
    """
    THRESHOLD 타입 이벤트에 trigger 필드 추가
    conditions 배열의 첫 번째 조건을 파싱하여 trigger 필드 생성
    """
    if event.get("type") != "THRESHOLD" or "conditions" not in event or not event["conditions"]:
        return event
    
    # 첫 번째 조건 파싱
    condition = event["conditions"][0]
    
    # 다양한 조건 패턴 처리
    # 패턴 1: 숫자 비교 (예: "hygiene < 70")
    match_numeric = re.match(r"(\w+)\s*([<>=!]+)\s*(\d+)", condition)
    if match_numeric:
        metric, operator, value = match_numeric.groups()
        value = int(value)
    else:
        # 패턴 2: 불리언 비교 (예: "rush_hour == true")
        match_boolean = re.match(r"(\w+)\s*([=!]+)\s*(true|false)", condition, re.IGNORECASE)
        if match_boolean:
            metric, operator, value_str = match_boolean.groups()
            value = value_str.lower() == "true"
        else:
            # 패턴 3: 문자열 비교 (예: "status == 'active'")
            match_string = re.match(r"(\w+)\s*([=!]+)\s*['\"](.+)['\"]", condition)
            if match_string:
                metric, operator, value = match_string.groups()
            else:
                # 패턴 4: 단순 조건 (예: "is_open")
                match_simple = re.match(r"(\w+)$", condition)
                if match_simple:
                    metric = match_simple.group(1)
                    operator = "=="
                    value = True
                else:
                    # 패턴 5: 부정 조건 (예: "!is_closed")
                    match_negation = re.match(r"!(\w+)$", condition)
                    if match_negation:
                        metric = match_negation.group(1)
                        operator = "!="
                        value = True
                    else:
                        # 파싱 실패 시 기본값 설정
                        print(f"⚠️ 조건 파싱 실패: {condition}, 기본값 사용")
                        # 이벤트 ID에서 metric 추출 시도
                        metric = event.get("id", "unknown_metric").lower()
                        operator = "=="
                        value = True
    
    # 연산자 매핑
    operator_map = {
        "<": "less_than",
        "<=": "less_than_or_equal",
        ">": "greater_than",
        ">=": "greater_than_or_equal",
        "==": "equal",
        "=": "equal",
        "!=": "not_equal",
        "!": "not_equal"
    }
    
    condition_type = operator_map.get(operator, "equal")
    
    # trigger 필드 추가
    event["trigger"] = {
        "metric": metric.upper(),
        "condition": condition_type,
        "value": value
    }
    
    return event


def convert_event_structure(event: Dict) -> Dict:
    """
    이벤트 구조를 표준 템플릿에 맞게 변환
    """
    # effects 필드 변환
    if "effects" in event and isinstance(event["effects"], dict):
        event["effects"] = convert_effects_structure(event["effects"])
    
    # THRESHOLD 타입 이벤트에 trigger 필드 추가
    event = add_trigger_field(event)
    
    # choices 내 effects는 변환하지 않음 (key-value 구조 유지)
    
    return event


def convert_events_file(input_file: str, output_file: str) -> None:
    """
    이벤트 파일 전체를 변환
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "events" in data and isinstance(data["events"], list):
            # 각 이벤트 변환
            converted_events = []
            for event in data["events"]:
                converted_event = convert_event_structure(event)
                converted_events.append(converted_event)
            
            data["events"] = converted_events
        
        # 결과 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 이벤트 구조 변환 완료: {input_file} → {output_file}")
        print(f"✅ 총 {len(data.get('events', []))}개 이벤트 변환됨")
    
    except Exception as e:
        print(f"❌ 변환 중 오류 발생: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="이벤트 구조를 표준 템플릿에 맞게 변환")
    parser.add_argument("--input", required=True, help="입력 이벤트 JSON 파일 경로")
    parser.add_argument("--output", required=True, help="출력 이벤트 JSON 파일 경로")
    
    args = parser.parse_args()
    convert_events_file(args.input, args.output)


if __name__ == "__main__":
    main()

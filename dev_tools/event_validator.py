"""
파일: dev_tools/event_validator.py
목적: 이벤트 데이터 검증 및 품질 평가 도구
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import tomllib  # Python 3.11+
from enum import Enum
from pathlib import Path
from typing import Any, List, Dict, ClassVar
from fuzzywuzzy import fuzz

# 품질 메트릭 임계값
QUALITY_THRESHOLDS = {
    "DIVERSITY": 0.8,  # 카테고리 분포의 균등성
    "TRADEOFF": 0.9,  # 선택지의 트레이드오프 명확성
    "CULTURAL": 0.7,  # 한국 치킨집 문화 반영도
    "COVERAGE": 80.0  # 테스트 커버리지
}

# 검증 임계값
VALIDATION_THRESHOLDS = {
    "MIN_KEYWORDS_MATCH": 2,  # 문화 키워드 최소 매칭 수
    "NAME_SIMILARITY_THRESHOLD": 80,  # 이름 유사도 임계값
    "TEXT_SIMILARITY_THRESHOLD": 70,  # 텍스트 유사도 임계값
    "MIN_CHOICES": 2,  # 최소 선택지 수
    "FORMULA_EPSILON": 0.001  # 수식 계산 오차 허용 범위
}

# 이벤트 타입 열거형
class EventType(Enum):
    """이벤트 타입"""
    RANDOM = "RANDOM"
    THRESHOLD = "THRESHOLD"
    SCHEDULED = "SCHEDULED"
    CASCADE = "CASCADE"

# 트리거 조건 열거형
class TriggerCondition(Enum):
    """트리거 조건"""
    LESS_THAN = "less_than"
    GREATER_THAN = "greater_than"
    EQUAL = "equal"

class EventValidator:
    """이벤트 검증기"""

    # 한국 치킨집 문화 관련 키워드
    CULTURAL_KEYWORDS: ClassVar[List[str]] = [
        "치킨", "후라이드", "양념", "간장", "마늘", "닭강정",
        "배달", "포장", "회식", "단골", "성수기", "할인",
        "치맥", "맥주", "소주", "안주", "야식", "주문",
        # 추가 키워드
        "신메뉴", "단체주문", "리뷰", "별점", "재료", "원가",
        "매출", "인건비", "마진", "경쟁", "프랜차이즈", "독립점",
        "위생", "점검", "식약처", "알바", "직원", "사장",
        "홀", "주방", "카운터", "배달대행", "배달팁", "콜",
        "성수기", "비수기", "대학가", "상권", "임대료", "월세"
    ]

    # 허용되는 메트릭
    VALID_METRICS = [
        "MONEY",  # 현금
        "REPUTATION",  # 평판
        "CUSTOMER_SATISFACTION",  # 고객 만족도
        "HAPPINESS",  # 행복
        "PAIN",  # 고통
        "EMPLOYEE_SATISFACTION",  # 직원 만족도
        "INGREDIENT_QUALITY",  # 재료 품질
        "EQUIPMENT_CONDITION",  # 장비 상태
        "STORE_CLEANLINESS",  # 매장 청결도
        "MENU_DIVERSITY"  # 메뉴 다양성
    ]

    def __init__(self):
        """초기화"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.event_ids: set[str] = set()
        self.validated_events: List[Dict[str, Any]] = []

    def validate_file(self, file_path: Path) -> bool:
        """단일 파일 검증"""
        self.errors = []
        self.warnings = []

        try:
            # 파일 확장자에 따라 로더 선택
            if file_path.suffix.lower() == ".toml":
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
            elif file_path.suffix.lower() == ".json":
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                self.errors.append(f"지원하지 않는 파일 형식: {file_path.suffix}")
                return False

            # 이벤트 데이터 추출
            events = data.get("events", [])
            if not events:
                self.warnings.append(f"이벤트가 없습니다: {file_path}")
                return True

            # 각 이벤트 검증
            for event in events:
                self._validate_event(event)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"파일 처리 오류: {e!s}")
            return False

    def validate_directory(self, directory_path: Path) -> bool:
        """디렉토리 내 모든 TOML/JSON 파일 검증"""
        all_valid = True
        self.event_ids = set()  # ID 유일성 검사를 위해 초기화

        # TOML 파일 먼저 처리
        for file_path in directory_path.glob("**/*.toml"):
            if not self.validate_file(file_path):
                all_valid = False

        # JSON 파일 처리
        for file_path in directory_path.glob("**/*.json"):
            if not self.validate_file(file_path):
                all_valid = False

        return all_valid

    def validate_event(self, event: dict[str, Any]) -> bool:
        """단일 이벤트 검증 (공개 메서드)"""
        # 기존 오류 상태 저장
        old_errors = self.errors.copy()
        self.errors = []

        # 내부 검증 메서드 호출
        result = self._validate_event(event)

        # 오류가 발생했으면 기존 오류 목록에 추가
        if not result:
            old_errors.extend(self.errors)

        self.errors = old_errors
        return result

    def _validate_event(self, event: dict[str, Any]) -> bool:
        """단일 이벤트 검증"""
        # 필수 필드 검증 강화
        required_fields = [
            "id", "type", "category", "name_ko", "name_en", 
            "text_ko", "text_en", "effects", "choices", "tags"
        ]
        for field in required_fields:
            if field not in event:
                self.errors.append(f"필수 필드 누락: {field} (이벤트: {event.get('id', 'unknown')})")
                return False

        # 필드 타입 검증
        if not isinstance(event.get("effects"), list):
            self.errors.append(f"effects는 리스트여야 함: {event['id']}")
            return False
        if not isinstance(event.get("choices"), list):
            self.errors.append(f"choices는 리스트여야 함: {event['id']}")
            return False
        if not isinstance(event.get("tags"), list):
            self.errors.append(f"tags는 리스트여야 함: {event['id']}")
            return False

        # ID 유일성 검증
        event_id = event["id"]
        if event_id in self.event_ids:
            self.errors.append(f"중복된 이벤트 ID: {event_id}")
            return False
        self.event_ids.add(event_id)

        # 이벤트 타입 검증
        try:
            event_type = EventType(event["type"])
        except ValueError:
            self.errors.append(f"유효하지 않은 이벤트 타입: {event['type']} (이벤트: {event_id})")
            return False

        # 타입별 필수 필드 검증
        if event_type == EventType.RANDOM:
            if "probability" not in event:
                self.errors.append(f"RANDOM 이벤트에 probability 필드 누락: {event_id}")
                return False
            if not (0.0 <= event["probability"] <= 1.0):
                self.errors.append(f"확률 범위 오류 (0.0-1.0): {event['probability']} (이벤트: {event_id})")
                return False

        elif event_type in [EventType.THRESHOLD, EventType.CASCADE]:
            if "trigger" not in event:
                self.errors.append(f"{event_type.value} 이벤트에 trigger 필드 누락: {event_id}")
                return False
            if not self._validate_trigger(event["trigger"], event_id):
                return False

        elif event_type == EventType.SCHEDULED:
            if "schedule" not in event:
                self.errors.append(f"SCHEDULED 이벤트에 schedule 필드 누락: {event_id}")
                return False
            if not isinstance(event["schedule"], int) or event["schedule"] <= 0:
                self.errors.append(f"schedule은 양의 정수여야 함: {event['schedule']} (이벤트: {event_id})")
                return False

        # 쿨다운 검증
        if "cooldown" in event and (
            not isinstance(event["cooldown"], int) or event["cooldown"] < 0
        ):
            self.errors.append(f"cooldown은 0 이상의 정수여야 함: {event['cooldown']} (이벤트: {event_id})")
            return False

        # 효과 검증
        if not event["effects"]:
            self.errors.append(f"effects가 비어 있음: {event_id}")
            return False

        for idx, effect in enumerate(event["effects"]):
            if not self._validate_effect(effect, event_id, idx):
                return False

        # 선택지 검증
        if not event["choices"]:
            self.errors.append(f"choices가 비어 있음: {event_id}")
            return False
        
        if len(event["choices"]) < VALIDATION_THRESHOLDS["MIN_CHOICES"]:
            self.errors.append(f"선택지는 최소 {VALIDATION_THRESHOLDS['MIN_CHOICES']}개 이상이어야 함: {event_id}")
            return False

        for idx, choice in enumerate(event["choices"]):
            if not self._validate_choice(choice, event_id, idx):
                return False

        # 문화적 연관성 검증
        if not self._validate_cultural_relevance_raw(event):
            self.warnings.append(f"한국 치킨집 문화 관련 키워드가 부족합니다: {event_id}")

        # 중복 검사
        if not self._check_duplicate_raw(event):
            self.warnings.append(f"유사한 이벤트가 존재할 수 있습니다: {event_id}")

        # 검증 통과한 이벤트 저장
        self.validated_events.append(event)
        
        return True

    def _validate_trigger(self, trigger: dict[str, Any], event_id: str) -> bool:
        """트리거 검증"""
        required_fields = ["metric", "condition", "value"]
        for field in required_fields:
            if field not in trigger:
                self.errors.append(f"트리거 필수 필드 누락: {field} (이벤트: {event_id})")
                return False

        # 조건 검증
        try:
            TriggerCondition(trigger["condition"])
        except ValueError:
            self.errors.append(f"유효하지 않은 트리거 조건: {trigger['condition']} (이벤트: {event_id})")
            return False

        # value 타입 검증
        if not isinstance(trigger["value"], (int, float)):
            self.errors.append(f"트리거 value는 숫자여야 함: {trigger['value']} (이벤트: {event_id})")
            return False

        # metric 검증
        if trigger["metric"] not in self.VALID_METRICS:
            self.warnings.append(f"알 수 없는 트리거 metric: {trigger['metric']} (이벤트: {event_id})")

        return True

    def _validate_effect(self, effect: dict[str, Any], event_id: str, index: int) -> bool:
        """효과 검증"""
        required_fields = ["metric", "formula"]
        for field in required_fields:
            if field not in effect:
                self.errors.append(f"효과 필수 필드 누락: {field} (이벤트: {event_id}, 효과 {index+1})")
                return False

        # metric 검증
        if effect["metric"] not in self.VALID_METRICS:
            self.warnings.append(f"알 수 없는 metric: {effect['metric']} (이벤트: {event_id}, 효과 {index+1})")

        # 포뮬러 검증 강화
        if not self._validate_formula_strict(effect["formula"], event_id, index):
            return False

        return True

    def _validate_choice(self, choice: dict[str, Any], event_id: str, index: int) -> bool:
        """선택지 검증"""
        required_fields = ["text_ko", "text_en", "effects"]
        for field in required_fields:
            if field not in choice:
                self.errors.append(f"선택지 필수 필드 누락: {field} (이벤트: {event_id}, 선택지 {index+1})")
                return False

        # effects 타입 및 트레이드오프 검증
        if not isinstance(choice["effects"], dict):
            self.errors.append(f"선택지 effects는 딕셔너리여야 함 (이벤트: {event_id}, 선택지 {index+1})")
            return False

        # 트레이드오프 검증
        positive_effects = 0
        negative_effects = 0
        for metric, value in choice["effects"].items():
            if not isinstance(value, (int, float)):
                self.errors.append(f"effect 값은 숫자여야 함: {metric}={value} (이벤트: {event_id}, 선택지 {index+1})")
                return False
            if value > 0:
                positive_effects += 1
            elif value < 0:
                negative_effects += 1

        if positive_effects == 0 or negative_effects == 0:
            self.warnings.append(f"선택지는 긍정적/부정적 효과를 모두 포함해야 함 (이벤트: {event_id}, 선택지 {index+1})")

        # metric 검증
        for metric in choice["effects"].keys():
            if metric not in self.VALID_METRICS:
                self.warnings.append(f"알 수 없는 metric: {metric} (이벤트: {event_id}, 선택지 {index+1})")

        return True

    def _validate_formula_strict(self, formula: str, event_id: str, index: int) -> bool:
        """포뮬러 문자열 엄격한 검증"""
        original_formula = formula
        
        # 퍼센트 표기법 처리
        if formula.endswith("%"):
            try:
                percent_value = float(formula[:-1])
                return True
            except ValueError:
                self.errors.append(f"잘못된 퍼센트 값: {formula} (이벤트: {event_id}, 효과 {index+1})")
                return False

        # 간단한 숫자 리터럴 처리
        try:
            float(formula)
            return True
        except ValueError:
            pass

        # 복잡한 수식 검증
        try:
            tree = ast.parse(formula, mode="eval")
            
            # 허용된 노드 타입
            allowed_nodes = (
                ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
                ast.Name, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div,
                ast.USub, ast.UAdd
            )
            
            # 허용된 이름들
            allowed_names = {"value", "random", "min", "max"}
            
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    if isinstance(node, ast.Call):
                        # random 함수만 허용
                        if (isinstance(node.func, ast.Name) and 
                            node.func.id in ["random", "min", "max"]):
                            continue
                    self.errors.append(
                        f"허용되지 않은 수식 구조: {type(node).__name__} "
                        f"(이벤트: {event_id}, 효과 {index+1}, 수식: {original_formula})"
                    )
                    return False
                    
                if isinstance(node, ast.Name) and node.id not in allowed_names:
                    self.errors.append(
                        f"허용되지 않은 변수명: {node.id} "
                        f"(이벤트: {event_id}, 효과 {index+1}, 수식: {original_formula})"
                    )
                    return False
                    
            return True
            
        except SyntaxError as e:
            self.errors.append(
                f"포뮬러 구문 오류: {original_formula} "
                f"(이벤트: {event_id}, 효과 {index+1}, 오류: {str(e)})"
            )
            return False

    def _validate_cultural_relevance_raw(self, event: dict[str, Any]) -> bool:
        """문화적 연관성 검증"""
        text = f"{event['name_ko']} {event['text_ko']}"
        matched_keywords = sum(1 for keyword in self.CULTURAL_KEYWORDS if keyword in text)
        
        if matched_keywords < VALIDATION_THRESHOLDS["MIN_KEYWORDS_MATCH"]:
            return False
            
        return True

    def _check_duplicate_raw(self, event: dict[str, Any]) -> bool:
        """중복 검사"""
        for validated in self.validated_events:
            name_similarity = fuzz.ratio(event['name_ko'], validated['name_ko'])
            text_similarity = fuzz.ratio(event['text_ko'], validated['text_ko'])
            
            if (name_similarity > VALIDATION_THRESHOLDS["NAME_SIMILARITY_THRESHOLD"] or 
                text_similarity > VALIDATION_THRESHOLDS["TEXT_SIMILARITY_THRESHOLD"]):
                return False
                
        return True

    def calculate_quality_metrics(self, events: list[dict[str, Any]]) -> dict[str, float]:
        """품질 메트릭 계산"""
        metrics = {
            "diversity_score": self._calculate_diversity_score(events),
            "tradeoff_clarity": self._calculate_tradeoff_clarity(events),
            "cultural_authenticity": self._calculate_cultural_authenticity(events),
            "replayability": self._calculate_replayability(events),
        }

        return metrics

    def _calculate_diversity_score(self, events: list[dict[str, Any]]) -> float:
        """카테고리 분포의 균등성 (Shannon Entropy 기반)"""
        categories: dict[str, int] = {}
        for event in events:
            category = event.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        if not categories:
            return 0.0

        total = sum(categories.values())
        entropy = 0.0
        for count in categories.values():
            p = count / total
            entropy -= p * math.log(p)

        max_entropy = math.log(len(categories))
        if max_entropy == 0:
            return 0.0

        return entropy / max_entropy

    def _calculate_tradeoff_clarity(self, events: list[dict[str, Any]]) -> float:
        """각 선택지가 명확한 득실을 가지는지"""
        if not events:
            return 0.0

        events_with_tradeoffs = 0
        for event in events:
            choices = event.get("choices", [])
            if self._has_clear_tradeoffs(choices):
                events_with_tradeoffs += 1

        return events_with_tradeoffs / len(events)

    def _has_clear_tradeoffs(self, choices: list[dict[str, Any]]) -> bool:
        """선택지들이 명확한 트레이드오프를 가지는지 확인"""
        if len(choices) < 2:
            return False

        for choice in choices:
            effects = choice.get("effects", {})
            has_positive = False
            has_negative = False

            for metric, value in effects.items():
                if value > 0:
                    has_positive = True
                elif value < 0:
                    has_negative = True

            if not (has_positive and has_negative):
                return False

        return True

    def _calculate_cultural_authenticity(self, events: list[dict[str, Any]]) -> float:
        """한국 치킨집 문화 반영도"""
        if not events:
            return 0.0

        authentic_events = 0
        for event in events:
            text_ko = event.get("text_ko", "")
            name_ko = event.get("name_ko", "")

            matched_keywords = sum(
                1 for keyword in self.CULTURAL_KEYWORDS
                if keyword in text_ko or keyword in name_ko
            )

            if matched_keywords >= VALIDATION_THRESHOLDS["MIN_KEYWORDS_MATCH"]:
                authentic_events += 1

        return authentic_events / len(events)

    def _calculate_replayability(self, events: list[dict[str, Any]]) -> float:
        """이벤트의 재플레이 가치 점수 계산"""
        if not events:
            return 0.0

        total_score = 0.0
        max_score = 0.0

        for event in events:
            base_score: float = 0.0

            # 선택지 수에 따른 점수
            choices = event.get("choices", [])
            choice_count = len(choices)
            if choice_count > 1:
                base_score += float(choice_count * 0.1)

            # 조건부 트리거 점수
            if event.get("type") == "THRESHOLD":
                base_score += 0.2

            # 연쇄 이벤트 점수
            cascade_events = 0
            for choice in choices:
                cascade_events += len(choice.get("cascade_events", []))
            if cascade_events > 0:
                base_score += float(cascade_events * 0.15)

            # 태그 다양성 점수
            tags = event.get("tags", [])
            if len(tags) > 0:
                base_score += float(len(tags) * 0.05)

            total_score += base_score
            max_score += 1.0

        if max_score > 0:
            return total_score / max_score
        return 0.0


def main() -> int:
    """메인 함수"""
    parser = argparse.ArgumentParser(description="치킨집 경영 게임 이벤트 검증기")
    parser.add_argument("--file", type=str, help="검증할 단일 이벤트 파일 경로 (TOML 또는 JSON)")
    parser.add_argument("--dir", type=str, help="검증할 이벤트 디렉토리 경로")
    parser.add_argument("--metrics", action="store_true", help="품질 메트릭 계산 및 출력")

    args = parser.parse_args()

    if not args.file and not args.dir:
        print("[ERROR] 파일 또는 디렉토리 경로를 지정해야 합니다.")
        return 1

    validator = EventValidator()
    success = False

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] 파일을 찾을 수 없습니다: {args.file}")
            return 1

        print(f"[INFO] 파일 검증 중: {file_path}")
        success = validator.validate_file(file_path)

    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"[ERROR] 디렉토리를 찾을 수 없습니다: {args.dir}")
            return 1

        print(f"[INFO] 디렉토리 검증 중: {dir_path}")
        success = validator.validate_directory(dir_path)

    # 결과 출력
    if success:
        print("[SUCCESS] 검증 성공!")
        if validator.warnings:
            print("\n[WARNING]")
            for warning in validator.warnings:
                print(f"  - {warning}")
    else:
        print("[ERROR] 검증 실패!")
        print("\n오류:")
        for error in validator.errors:
            print(f"  - {error}")

    # 품질 메트릭 계산 (요청 시)
    if args.metrics and success:
        # 이벤트 데이터 로드
        events = []
        if args.file:
            file_path = Path(args.file)
            if file_path.suffix.lower() == ".toml":
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    events = data.get("events", [])
            elif file_path.suffix.lower() == ".json":
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    events = data.get("events", [])

        elif args.dir:
            # 디렉토리 내 모든 파일에서 이벤트 수집
            dir_path = Path(args.dir)
            for file_path in dir_path.glob("**/*.toml"):
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                    events.extend(data.get("events", []))

            for file_path in dir_path.glob("**/*.json"):
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    events.extend(data.get("events", []))

        # 메트릭 계산 및 출력
        metrics = validator.calculate_quality_metrics(events)
        print("\n[METRICS]")
        for name, value in metrics.items():
            status = "[PASS]" if value >= QUALITY_THRESHOLDS.get(name.upper(), 0.7) else "[WARN]"
            print(f"  {status} {name}: {value:.2f}")

    return 0 if success else 1


if __name__ == "__main__":
    main()

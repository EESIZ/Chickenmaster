# 리팩토링 가이드라인

## 1. 매직 넘버 처리 (PLR2004)

### 규칙
- 모든 매직 넘버는 상수로 정의
- 상수 이름은 대문자와 언더스코어 사용
- 관련 상수는 그룹화하여 클래스 레벨 또는 모듈 레벨에 정의

### 예시
```python
# ❌ 잘못된 예
if score >= 0.7:
    status = "good"

# ✅ 올바른 예
SCORE_THRESHOLD = {
    "EXCELLENT": 0.9,
    "GOOD": 0.7,
    "AVERAGE": 0.5
}

if score >= SCORE_THRESHOLD["GOOD"]:
    status = "good"
```

## 2. 타입 힌트 현대화 (UP006, UP007, UP038)

### 규칙
- PEP 585 스타일 사용 (Python 3.9+)
- typing 모듈의 제네릭 대신 내장 컬렉션 사용
- Union 타입에 파이프 연산자 사용 (Python 3.10+)

### 예시
```python
# ❌ 잘못된 예
from typing import List, Dict, Union, Optional

def process_data(items: List[Dict[str, Union[str, int]]]) -> Optional[str]:
    pass

# ✅ 올바른 예
def process_data(items: list[dict[str, str | int]]) -> str | None:
    pass
```

## 3. 함수/클래스 명명 규칙 (N802, N805)

### 규칙
- 클래스: CapWords 컨벤션
- 함수/메서드: snake_case
- 상수: UPPER_CASE_WITH_UNDERSCORES
- 비공개 멤버: _leading_underscore

### 예시
```python
# ❌ 잘못된 예
class eventHandler:
    def ProcessEvent(self):
        pass

# ✅ 올바른 예
class EventHandler:
    def process_event(self):
        pass
```

## 4. Import 정렬 (I001)

### 규칙
- 표준 라이브러리 임포트 그룹
- 서드파티 라이브러리 임포트 그룹
- 로컬 모듈 임포트 그룹
- 각 그룹은 알파벳 순으로 정렬

### 예시
```python
# ✅ 올바른 예
import json
import sys
from pathlib import Path

import pandas as pd
import requests
from pydantic import BaseModel

from src.config import Config
from src.utils import helpers
```

## 5. 복잡도 관리 (PLR0911, PLR0912, PLR0915)

### 규칙
- 함수당 반환문 6개 이하
- 분기문 12개 이하
- 함수당 문장 50개 이하
- 복잡한 로직은 작은 함수로 분리

### 예시
```python
# ❌ 잘못된 예
def process_event(event: dict) -> str:
    if event["type"] == "A":
        if event["status"] == "active":
            return "process_a_active"
        else:
            return "process_a_inactive"
    elif event["type"] == "B":
        # ... 더 많은 분기문

# ✅ 올바른 예
def process_event(event: dict) -> str:
    handlers = {
        "A": process_type_a,
        "B": process_type_b,
    }
    return handlers[event["type"]](event)

def process_type_a(event: dict) -> str:
    return "process_a_active" if event["status"] == "active" else "process_a_inactive"
```

## 6. 자동화된 검사

### pre-commit 설정
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.11
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
```

### GitHub Actions 순서
1. Ruff 검사 및 수정
2. Black 포맷팅
3. MyPy 타입 체크
4. 테스트 실행

## 7. 품질 메트릭 임계값

```python
QUALITY_THRESHOLDS = {
    "DIVERSITY_SCORE": 0.8,
    "TRADEOFF_CLARITY": 0.9,
    "CULTURAL_AUTHENTICITY": 0.7,
    "CODE_COVERAGE": 80.0
}
``` 
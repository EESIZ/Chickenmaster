"""
이벤트 시스템 상수
"""

# 품질 메트릭 임계값
QUALITY_THRESHOLDS = {
    "DIVERSITY": 0.8,
    "TRADEOFF": 0.9,
    "CULTURAL": 0.7,
    "COVERAGE": 80.0
}

# 검증 임계값
VALIDATION_THRESHOLDS = {
    "MIN_KEYWORDS_MATCH": 2,
    "NAME_SIMILARITY_THRESHOLD": 80,
    "TEXT_SIMILARITY_THRESHOLD": 70,
    "MIN_CHOICES": 2,
    "FORMULA_EPSILON": 0.001
}

# 이벤트 생성 설정
GENERATION_CONFIG = {
    "BATCH_SIZE": 10,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 2,
    "SAVE_INTERVAL": 10,
    "COST_PER_EVENT": 0.05,
    "HIGH_COST_WARNING": 100.0,
    "TARGET_EVENT_COUNT": 500
}

# 카테고리별 목표 수
CATEGORY_TARGETS = {
    "daily_routine": {
        "count": 200,
        "tags": ["치킨집", "일상", "운영"],
        "description": "일상적인 치킨집 운영 이벤트"
    },
    "crisis_events": {
        "count": 100,
        "tags": ["위기", "문제", "해결"],
        "description": "위기 상황 및 문제 해결 이벤트"
    },
    "opportunity": {
        "count": 100,
        "tags": ["기회", "성장", "투자"],
        "description": "성장 기회 및 투자 관련 이벤트"
    },
    "human_drama": {
        "count": 50,
        "tags": ["인간관계", "감정", "드라마"],
        "description": "인간관계 및 감정적 상황 이벤트"
    },
    "chain_scenario": {
        "count": 50,
        "tags": ["연쇄", "복합", "시나리오"],
        "description": "연쇄 반응 및 복합 시나리오 이벤트"
    }
} 
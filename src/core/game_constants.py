"""
게임 상수 모듈

이 모듈은 게임에서 사용되는 각종 기본값과 상수를 정의합니다.
"""

# 기본 시작 값
DEFAULT_STARTING_MONEY = 5000000.0  # 500만원
DEFAULT_STARTING_REPUTATION = 0.0  # 완전 무명
DEFAULT_STARTING_HAPPINESS = 50.0  # 보통
DEFAULT_STARTING_SUFFERING = 20.0  # 약간의 고통
DEFAULT_STARTING_INVENTORY = 50.0  # 적당한 재고
DEFAULT_STARTING_STAFF_FATIGUE = 30.0  # 약간의 피로
DEFAULT_STARTING_FACILITY = 80.0  # 좋은 시설
DEFAULT_STARTING_DEMAND = 20.0  # 낮은 수요 (평판 0이므로)

# 게임 단계 구분
EARLY_GAME_DAYS = 100  # 초반 100일
MID_GAME_DAYS = 300  # 중반 300일
LATE_GAME_DAYS = 600  # 후반 600일

# 게임 오버 조건
BANKRUPTCY_THRESHOLD = 0  # 파산 기준
MIN_REPUTATION = 0  # 최소 평판
MIN_HAPPINESS = 0  # 최소 행복도

# 지표 범위
METRIC_MIN_VALUE = 0  # 모든 지표의 최소값
METRIC_MAX_VALUE = 100  # 대부분 지표의 최대값
INVENTORY_MAX_VALUE = 999  # 재고 최대값
DEMAND_MAX_VALUE = 999  # 수요 최대값 
"""
코어 도메인 예외
게임 도메인에서 발생할 수 있는 예외들을 정의합니다.
"""

class DomainException(Exception):
    """도메인 규칙 위반 예외의 기본 클래스"""
    pass

class InvalidStateException(DomainException):
    """잘못된 게임 상태 예외"""
    def __init__(self, message: str = "게임 상태가 유효하지 않습니다"):
        self.message = message
        super().__init__(self.message)

class InvalidMetricException(DomainException):
    """잘못된 게임 지표 예외"""
    def __init__(self, message: str = "게임 지표가 유효하지 않습니다"):
        self.message = message
        super().__init__(self.message)

class InvalidEffectException(DomainException):
    """잘못된 효과 예외"""
    def __init__(self, message: str = "이벤트 효과가 유효하지 않습니다"):
        self.message = message
        super().__init__(self.message)

class GameOverException(DomainException):
    """게임 종료 조건 발생 예외"""
    def __init__(self, reason: str):
        self.reason = reason
        self.message = f"게임 종료: {reason}"
        super().__init__(self.message)

class ValidationException(DomainException):
    """도메인 객체 검증 실패 예외"""
    def __init__(self, object_type: str, details: str):
        self.object_type = object_type
        self.details = details
        self.message = f"{object_type} 검증 실패: {details}"
        super().__init__(self.message)

class BusinessRuleViolationException(DomainException):
    """비즈니스 규칙 위반 예외"""
    def __init__(self, rule: str, details: str):
        self.rule = rule
        self.details = details
        self.message = f"비즈니스 규칙 위반 ({rule}): {details}"
        super().__init__(self.message)

class ResourceException(DomainException):
    """리소스 관련 예외"""
    def __init__(self, resource: str, operation: str, details: str):
        self.resource = resource
        self.operation = operation
        self.details = details
        self.message = f"리소스 {operation} 실패 ({resource}): {details}"
        super().__init__(self.message) 
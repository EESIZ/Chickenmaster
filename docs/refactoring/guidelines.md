# 리팩토링 가이드라인

## 개요

이 문서는 Chicken-RNG 프로젝트의 리팩토링 작업을 위한 가이드라인을 제공합니다. 코드의 품질과 유지보수성을 향상시키기 위한 기준과 절차를 설명합니다.

## 리팩토링 원칙

### 1. 단일 책임 원칙 (SRP)

- 각 클래스와 메서드는 하나의 책임만 가져야 합니다.
- 변경의 이유가 하나여야 합니다.
- 응집도를 높이고 결합도를 낮춥니다.

### 2. 개방-폐쇄 원칙 (OCP)

- 확장에는 열려있고 수정에는 닫혀있어야 합니다.
- 인터페이스를 통한 추상화를 활용합니다.
- 새로운 기능은 기존 코드를 수정하지 않고 추가할 수 있어야 합니다.

### 3. 리스코프 치환 원칙 (LSP)

- 하위 타입은 상위 타입을 대체할 수 있어야 합니다.
- 상속 관계에서 동작의 일관성을 유지합니다.
- 계약에 의한 설계를 준수합니다.

## 코드 구조 개선

### 1. 메서드 추출

```python
# Before
def process_order(self, order):
    # 주문 검증
    if not order.is_valid():
        raise InvalidOrderError()
    
    # 재고 확인
    if not self.check_inventory(order.items):
        raise OutOfStockError()
    
    # 주문 처리
    self.update_inventory(order.items)
    self.calculate_total(order)
    self.save_order(order)

# After
def process_order(self, order):
    self.validate_order(order)
    self.verify_inventory(order)
    self.execute_order(order)

def validate_order(self, order):
    if not order.is_valid():
        raise InvalidOrderError()

def verify_inventory(self, order):
    if not self.check_inventory(order.items):
        raise OutOfStockError()

def execute_order(self, order):
    self.update_inventory(order.items)
    self.calculate_total(order)
    self.save_order(order)
```

### 2. 클래스 분리

```python
# Before
class OrderProcessor:
    def process_order(self, order):
        self.validate_order(order)
        self.update_inventory(order)
        self.calculate_price(order)
        self.save_order(order)
        self.send_notification(order)

# After
class OrderValidator:
    def validate(self, order):
        # 주문 검증 로직

class InventoryManager:
    def update(self, order):
        # 재고 관리 로직

class PriceCalculator:
    def calculate(self, order):
        # 가격 계산 로직

class OrderRepository:
    def save(self, order):
        # 주문 저장 로직

class NotificationService:
    def notify(self, order):
        # 알림 전송 로직

class OrderProcessor:
    def __init__(self):
        self.validator = OrderValidator()
        self.inventory = InventoryManager()
        self.calculator = PriceCalculator()
        self.repository = OrderRepository()
        self.notifier = NotificationService()

    def process_order(self, order):
        self.validator.validate(order)
        self.inventory.update(order)
        self.calculator.calculate(order)
        self.repository.save(order)
        self.notifier.notify(order)
```

## 코드 품질 향상

### 1. 명명 규칙

```python
# Bad
def calc_tot():
    pass

# Good
def calculate_total_price():
    pass

# Bad
class Proc:
    pass

# Good
class OrderProcessor:
    pass
```

### 2. 오류 처리

```python
# Bad
def process_data(data):
    try:
        # 모든 예외를 잡음
        result = complex_operation(data)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

# Good
def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        raise InvalidDataError(f"Data validation failed: {e}")
    except IOError as e:
        logger.error(f"IO operation failed: {e}")
        raise ProcessingError(f"Data processing failed: {e}")
```

### 3. 주석 작성

```python
# Bad
# 주문을 처리함
def process_order(order):
    pass

# Good
class OrderProcessor:
    """주문 처리를 담당하는 클래스입니다.
    
    주문의 유효성을 검사하고, 재고를 확인한 후,
    주문을 처리하고 결과를 저장합니다.
    """
    
    def process_order(self, order: Order) -> OrderResult:
        """주문을 처리하고 결과를 반환합니다.
        
        Args:
            order: 처리할 주문 객체
            
        Returns:
            처리된 주문 결과
            
        Raises:
            InvalidOrderError: 주문이 유효하지 않은 경우
            OutOfStockError: 재고가 부족한 경우
        """
        pass
```

## 테스트 개선

### 1. 테스트 구조화

```python
class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = OrderProcessor()
        self.valid_order = create_test_order()
    
    def test_valid_order_processing(self):
        """유효한 주문이 정상적으로 처리되는지 테스트합니다."""
        result = self.processor.process_order(self.valid_order)
        self.assertTrue(result.is_successful)
        self.assertEqual(result.status, OrderStatus.COMPLETED)
    
    def test_invalid_order_handling(self):
        """유효하지 않은 주문이 적절히 처리되는지 테스트합니다."""
        invalid_order = create_invalid_order()
        with self.assertRaises(InvalidOrderError):
            self.processor.process_order(invalid_order)
```

### 2. 테스트 데이터 관리

```python
class TestData:
    """테스트에 사용될 데이터를 관리합니다."""
    
    @staticmethod
    def create_test_order(items=None, customer=None):
        """테스트용 주문을 생성합니다."""
        return Order(
            id=str(uuid.uuid4()),
            items=items or TestData.default_items(),
            customer=customer or TestData.default_customer()
        )
    
    @staticmethod
    def default_items():
        """기본 주문 항목을 반환합니다."""
        return [
            OrderItem(id="item1", quantity=2),
            OrderItem(id="item2", quantity=1)
        ]
```

## 성능 최적화

### 1. 캐싱 적용

```python
class CachedOrderProcessor:
    def __init__(self):
        self.cache = {}
    
    def get_order_details(self, order_id: str) -> OrderDetails:
        """주문 상세 정보를 캐시를 활용하여 조회합니다."""
        if order_id in self.cache:
            return self.cache[order_id]
        
        details = self.fetch_order_details(order_id)
        self.cache[order_id] = details
        return details
```

### 2. 배치 처리

```python
class BatchOrderProcessor:
    def process_orders_batch(self, orders: List[Order]) -> List[OrderResult]:
        """여러 주문을 배치로 처리합니다."""
        validated_orders = self.validate_orders_batch(orders)
        processed_orders = self.process_valid_orders(validated_orders)
        return self.save_orders_batch(processed_orders)
```

## 문서화

### 1. API 문서

```python
class OrderAPI:
    """주문 관련 API를 제공하는 클래스입니다.
    
    이 클래스는 주문 생성, 조회, 수정, 취소 등의
    기능을 제공하는 RESTful API 엔드포인트를 구현합니다.
    """
    
    def create_order(self, order_data: Dict) -> Order:
        """새로운 주문을 생성합니다.
        
        Args:
            order_data: 주문 생성에 필요한 데이터
            
        Returns:
            생성된 주문 객체
            
        Raises:
            ValidationError: 주문 데이터가 유효하지 않은 경우
        """
        pass
```

### 2. 변경 로그

```markdown
# 변경 로그

## [1.2.0] - 2024-03-15
### 추가
- 배치 처리 기능 추가
- 캐싱 시스템 구현

### 수정
- 주문 처리 로직 개선
- 오류 처리 방식 변경

### 제거
- 레거시 코드 제거
```

## 모니터링 및 로깅

### 1. 로깅 구현

```python
class LoggedOrderProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_order(self, order: Order) -> OrderResult:
        """주문을 처리하고 로그를 기록합니다."""
        self.logger.info(f"Processing order: {order.id}")
        try:
            result = super().process_order(order)
            self.logger.info(f"Order processed successfully: {order.id}")
            return result
        except Exception as e:
            self.logger.error(f"Order processing failed: {e}")
            raise
```

### 2. 메트릭 수집

```python
class MetricCollector:
    def __init__(self):
        self.metrics = defaultdict(int)
    
    def record_processing_time(self, operation: str, duration: float):
        """작업 처리 시간을 기록합니다."""
        self.metrics[f"{operation}_time"] += duration
        self.metrics[f"{operation}_count"] += 1
    
    def get_average_time(self, operation: str) -> float:
        """평균 처리 시간을 계산합니다."""
        total_time = self.metrics[f"{operation}_time"]
        count = self.metrics[f"{operation}_count"]
        return total_time / count if count > 0 else 0
``` 
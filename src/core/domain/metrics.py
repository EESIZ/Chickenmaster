"""
지표 도메인 모델
불변 객체로 구현된 게임 지표 관련 도메인 엔티티를 포함합니다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Metric:
    """지표 - 절대 불변"""
    name: str
    value: int
    min_value: int
    max_value: int
    
    def is_valid(self) -> bool:
        """지표값이 유효한지 확인"""
        return self.min_value <= self.value <= self.max_value
    
    def with_new_value(self, new_value: int) -> 'Metric':
        """새 값으로 지표 객체 생성"""
        clamped_value = max(self.min_value, min(self.max_value, new_value))
        return Metric(
            name=self.name,
            value=clamped_value,
            min_value=self.min_value,
            max_value=self.max_value
        )
    
    def apply_delta(self, delta: int) -> 'Metric':
        """변화량을 적용한 새 지표 객체 생성"""
        return self.with_new_value(self.value + delta)


@dataclass(frozen=True)
class TradeoffPair:
    """트레이드오프 관계 - 절대 불변"""
    metric1: str
    metric2: str
    balance_factor: float = 1.0
    
    def calculate_effect(self, primary_delta: int, primary_metric: str) -> dict[str, int]:
        """트레이드오프 효과 계산"""
        if primary_metric not in (self.metric1, self.metric2):
            return {}
            
        secondary_metric = self.metric2 if primary_metric == self.metric1 else self.metric1
        secondary_delta = int(-primary_delta * self.balance_factor)
        
        return {
            primary_metric: primary_delta,
            secondary_metric: secondary_delta
        }


@dataclass(frozen=True)
class MetricsSnapshot:
    """지표 스냅샷 - 절대 불변"""
    metrics: dict[str, Metric]
    timestamp: int
    
    def get_metric_value(self, metric_name: str) -> int:
        """지표값 조회"""
        return self.metrics.get(metric_name, Metric(
            name=metric_name,
            value=0,
            min_value=0,
            max_value=100
        )).value
    
    def with_updated_metric(self, metric_name: str, new_value: int) -> 'MetricsSnapshot':
        """특정 지표 업데이트된 새 스냅샷 생성"""
        updated_metrics = dict(self.metrics)
        
        if metric_name in updated_metrics:
            updated_metrics[metric_name] = updated_metrics[metric_name].with_new_value(new_value)
        else:
            updated_metrics[metric_name] = Metric(
                name=metric_name,
                value=new_value,
                min_value=0,
                max_value=100
            )
            
        return MetricsSnapshot(
            metrics=updated_metrics,
            timestamp=self.timestamp
        )
    
    def apply_effects(self, effects: dict[str, int]) -> 'MetricsSnapshot':
        """여러 효과를 적용한 새 스냅샷 생성"""
        updated_metrics = dict(self.metrics)
        
        for metric_name, delta in effects.items():
            if metric_name in updated_metrics:
                updated_metrics[metric_name] = updated_metrics[metric_name].apply_delta(delta)
            elif delta != 0:  # 새 지표는 delta가 있을 때만 생성
                updated_metrics[metric_name] = Metric(
                    name=metric_name,
                    value=max(0, min(100, delta)),  # 기본 범위 0-100 적용
                    min_value=0,
                    max_value=100
                )
                
        return MetricsSnapshot(
            metrics=updated_metrics,
            timestamp=self.timestamp
        )

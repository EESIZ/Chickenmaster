from typing import Dict, Optional
from .metrics import MetricsSnapshot

class InMemoryMetricsRepository:
    def __init__(self):
        self._data: Dict[str, MetricsSnapshot] = {}

    def save_metrics_snapshot(self, player_id: str, snapshot: MetricsSnapshot) -> None:
        self._data[player_id] = snapshot

    def load_metrics_snapshot(self, player_id: str) -> Optional[MetricsSnapshot]:
        return self._data.get(player_id) 
# 🍗 치킨마스터 Import 의존성 분석 보고서

**분석 일시**: 2025-06-15 22:22:34
**분석된 파일 수**: 130개
**의존성 관계 수**: 363개

## ⚠️ 순환 의존성 발견!

**발견된 순환 경로**: 6개

### 순환 경로 #1
```
src.cascade.ports →
src.cascade.ports
```

### 순환 경로 #2
```
src.cascade.domain →
src.cascade.domain
```

### 순환 경로 #3
```
src.cascade.adapters →
src.cascade.adapters
```

### 순환 경로 #4
```
src.events →
src.events
```

### 순환 경로 #5
```
src.events →
src.events.engine →
src.events
```

### 순환 경로 #6
```
src.events →
src.events.integration →
src.events
```

## 📊 모듈별 의존성 상세

### `backend.app.adapters.excel_data_provider`
**의존성**: 5개

- `core`
- `core.domain`
- `core.domain.interfaces`
- `core.domain.interfaces.data_provider`
- `core.domain.variable_registry`

### `backend.app.core.domain.event_system`
**의존성**: 1개

- `game_constants`

### `backend.app.core.domain.variable_registry`
**의존성**: 1개

- `game_constants`

### `chicken_debug_mud`
**의존성**: 9개

- `game_constants`
- `src`
- `src.application`
- `src.application.game_philosophy_service`
- `src.core`
- `src.core.domain`
- `src.core.domain.action_slots`
- `src.core.domain.game_state`
- `src.core.domain.metrics`

### `chicken_mud_game`
**의존성**: 6개

- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.core.domain.metrics`

### `core.adapters.excel_constants_provider`
**의존성**: 6개

- `backend`
- `backend.app`
- `backend.app.core`
- `backend.app.core.domain`
- `backend.app.core.domain.interfaces`
- `backend.app.core.domain.interfaces.data_provider`

### `dev_tools.balance_simulator`
**의존성**: 8개

- `game_constants`
- `src`
- `src.economy`
- `src.economy.engine`
- `src.events`
- `src.events.engine`
- `src.metrics`
- `src.metrics.tracker`

### `dev_tools.event_bank_manager`
**의존성**: 5개

- `dev_tools`
- `dev_tools.balance_simulator`
- `dev_tools.config`
- `dev_tools.event_validator`
- `game_constants`

### `dev_tools.event_generator`
**의존성**: 1개

- `game_constants`

### `dev_tools.event_validator`
**의존성**: 1개

- `game_constants`

### `examples.constants_usage_example`
**의존성**: 3개

- `core`
- `core.adapters`
- `core.adapters.excel_constants_provider`

### `scripts.mass_event_generation`
**의존성**: 3개

- `dev_tools`
- `dev_tools.event_validator`
- `dev_tools.openai_client`

### `src.adapters.research_adapter`
**의존성**: 5개

- `core`
- `core.domain`
- `core.domain.research`
- `core.ports`
- `core.ports.research_port`

### `src.adapters.services.cascade_service`
**의존성**: 8개

- `core`
- `core.domain`
- `core.domain.cascade`
- `core.domain.events`
- `core.domain.game_state`
- `core.ports`
- `core.ports.cascade_port`
- `core.ports.event_port`

### `src.application.game_philosophy_service`
**의존성**: 5개

- `core`
- `core.domain`
- `core.domain.action_slots`
- `core.domain.game_state`
- `core.domain.metrics`

### `src.application.research_service`
**의존성**: 7개

- `core`
- `core.domain`
- `core.domain.game_state`
- `core.domain.metrics`
- `core.domain.research`
- `core.ports`
- `core.ports.research_port`

### `src.cascade.adapters`
**의존성**: 5개

- `src`
- `src.cascade`
- `src.cascade.adapters`
- `src.cascade.adapters.cascade_service`
- `src.cascade.adapters.event_adapter`

### `src.cascade.adapters.cascade_service`
**의존성**: 10개

- `game_constants`
- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.strategy_factory`
- `src.cascade.ports`
- `src.cascade.ports.cascade_port`
- `src.cascade.ports.event_port`

### `src.cascade.adapters.event_adapter`
**의존성**: 4개

- `src`
- `src.cascade`
- `src.cascade.ports`
- `src.cascade.ports.event_port`

### `src.cascade.domain`
**의존성**: 4개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`

### `src.cascade.domain.strategies.cascade_strategy`
**의존성**: 4개

- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.domain.strategies.cultural_cascade_strategy`
**의존성**: 8개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.domain.strategies.economic_cascade_strategy`
**의존성**: 9개

- `game_constants`
- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.domain.strategies.environmental_cascade_strategy`
**의존성**: 8개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.domain.strategies.social_cascade_strategy`
**의존성**: 8개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.domain.strategies.strategy_factory`
**의존성**: 11개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.cascade.domain.strategies.cultural_cascade_strategy`
- `src.cascade.domain.strategies.economic_cascade_strategy`
- `src.cascade.domain.strategies.environmental_cascade_strategy`
- `src.cascade.domain.strategies.social_cascade_strategy`
- `src.cascade.domain.strategies.technological_cascade_strategy`

### `src.cascade.domain.strategies.technological_cascade_strategy`
**의존성**: 8개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.cascade_strategy`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`

### `src.cascade.ports`
**의존성**: 5개

- `src`
- `src.cascade`
- `src.cascade.ports`
- `src.cascade.ports.cascade_port`
- `src.cascade.ports.event_port`

### `src.cascade.ports.cascade_port`
**의존성**: 4개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`

### `src.core.adapters.container_service`
**의존성**: 4개

- `src`
- `src.core`
- `src.core.ports`
- `src.core.ports.container_port`

### `src.economy.engine`
**의존성**: 4개

- `game_constants`
- `src`
- `src.economy`
- `src.economy.models`

### `src.economy.models`
**의존성**: 1개

- `game_constants`

### `src.events`
**의존성**: 6개

- `src`
- `src.events`
- `src.events.engine`
- `src.events.integration`
- `src.events.models`
- `src.events.schema`

### `src.events.constants`
**의존성**: 1개

- `game_constants`

### `src.events.engine`
**의존성**: 7개

- `game_constants`
- `src`
- `src.events`
- `src.events.models`
- `src.events.schema`
- `src.metrics`
- `src.metrics.tracker`

### `src.events.integration`
**의존성**: 7개

- `game_constants`
- `src`
- `src.events`
- `src.events.engine`
- `src.events.models`
- `src.metrics`
- `src.metrics.tracker`

### `src.events.models`
**의존성**: 1개

- `game_constants`

### `src.metrics.modifiers`
**의존성**: 1개

- `game_constants`

### `src.metrics.tracker`
**의존성**: 4개

- `game_constants`
- `src`
- `src.metrics`
- `src.metrics.modifiers`

### `src.research`
**의존성**: 3개

- `core`
- `core.domain`
- `core.domain.research`

### `src.research.facade`
**의존성**: 7개

- `core`
- `core.domain`
- `core.domain.game_state`
- `core.domain.metrics`
- `core.domain.research`
- `core.ports`
- `core.ports.research_port`

### `src.research.factory`
**의존성**: 3개

- `core`
- `core.ports`
- `core.ports.research_port`

### `src.storyteller.adapters.storyteller_service`
**의존성**: 14개

- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.core.ports`
- `src.core.ports.container_port`
- `src.core.ports.event_port`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.models`
- `src.storyteller.domain.strategy_factory`
- `src.storyteller.ports`
- `src.storyteller.ports.storyteller_port`

### `src.storyteller.domain.strategies`
**의존성**: 5개

- `game_constants`
- `src`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.models`

### `src.storyteller.domain.strategy_factory`
**의존성**: 4개

- `src`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.strategies`

### `src.storyteller.ports.storyteller_port`
**의존성**: 4개

- `src`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.models`

### `test_mud_integration`
**의존성**: 6개

- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.core.domain.metrics`

### `test_research_module`
**의존성**: 6개

- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.core.domain.metrics`
- `src.research`

### `test_strategy_debug`
**의존성**: 11개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.strategy_factory`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.strategy_factory`

### `test_strategy_patterns`
**의존성**: 9개

- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`
- `src.cascade.domain.strategies`
- `src.cascade.domain.strategies.strategy_factory`
- `src.storyteller`
- `src.storyteller.domain`
- `src.storyteller.domain.strategy_factory`

### `tests.adapters.services.test_cascade_service`
**의존성**: 12개

- `game_constants`
- `src`
- `src.adapters`
- `src.adapters.services`
- `src.adapters.services.cascade_service`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`
- `src.core.domain.events`
- `src.core.domain.game_state`
- `src.core.ports`
- `src.core.ports.event_port`

### `tests.cascade.test_adapters`
**의존성**: 9개

- `game_constants`
- `src`
- `src.cascade`
- `src.cascade.adapters`
- `src.cascade.adapters.cascade_service`
- `src.cascade.domain`
- `src.cascade.domain.models`
- `src.cascade.ports`
- `src.cascade.ports.event_port`

### `tests.cascade.test_domain`
**의존성**: 5개

- `game_constants`
- `src`
- `src.cascade`
- `src.cascade.domain`
- `src.cascade.domain.models`

### `tests.conftest`
**의존성**: 6개

- `src`
- `src.events`
- `src.events.schema`
- `src.events.validators`
- `src.events.validators.base`
- `src.events.validators.specific`

### `tests.core.domain.cascade.test_models`
**의존성**: 7개

- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.cascade`
- `src.core.domain.events`
- `src.core.domain.game_state`

### `tests.test_economy`
**의존성**: 5개

- `game_constants`
- `src`
- `src.economy`
- `src.economy.engine`
- `src.economy.models`

### `tests.test_event_generator_validator`
**의존성**: 5개

- `dev_tools`
- `dev_tools.event_bank_indexer`
- `dev_tools.event_condition_fixer`
- `dev_tools.event_generator`
- `dev_tools.event_validator`

### `tests.test_event_tools`
**의존성**: 3개

- `dev_tools`
- `dev_tools.event_bank_indexer`
- `dev_tools.event_condition_fixer`

### `tests.test_events`
**의존성**: 9개

- `game_constants`
- `src`
- `src.events`
- `src.events.engine`
- `src.events.integration`
- `src.events.models`
- `src.events.schema`
- `src.metrics`
- `src.metrics.tracker`

### `tests.test_metrics`
**의존성**: 4개

- `game_constants`
- `src`
- `src.metrics`
- `src.metrics.tracker`

### `tests.test_placeholder`
**의존성**: 1개

- `game_constants`

### `tests.test_storyteller_edge_cases`
**의존성**: 6개

- `src`
- `src.storyteller`
- `src.storyteller.adapters`
- `src.storyteller.adapters.storyteller_service`
- `src.storyteller.domain`
- `src.storyteller.domain.models`

### `tests.test_storyteller_service`
**의존성**: 13개

- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.events`
- `src.core.ports`
- `src.core.ports.container_port`
- `src.core.ports.event_port`
- `src.storyteller`
- `src.storyteller.adapters`
- `src.storyteller.adapters.storyteller_service`
- `src.storyteller.domain`
- `src.storyteller.domain.models`

### `tests.test_tradeoff_example`
**의존성**: 1개

- `game_constants`

### `web_prototype.main`
**의존성**: 7개

- `dialogue_manager`
- `game_constants`
- `src`
- `src.core`
- `src.core.domain`
- `src.core.domain.game_state`
- `src.core.domain.metrics`

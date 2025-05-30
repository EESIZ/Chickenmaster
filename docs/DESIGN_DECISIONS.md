# 설계 결정 사항

## 코드 구조 및 스타일

### 1. 동적 Import 경로 설정
**파일**: `scripts/mass_event_generation.py`

**결정사항**: 
- `sys.path`를 수정한 후에 `dev_tools` 모듈을 import하는 구조 유지
- Ruff의 E402(모듈 레벨 import가 파일 최상단에 없음) 경고 무시

**이유**:
- 스크립트가 프로젝트 루트 디렉토리의 위치를 동적으로 찾아 `dev_tools` 모듈을 import해야 함
- 이는 스크립트가 다양한 위치에서 실행될 수 있도록 하기 위한 의도적인 설계
- `sys.path.insert(0, str(project_root))` 이후에 import 문이 위치해야 정상적으로 동작

**처리방법**:
- `ruff.toml` 설정 파일에서 해당 파일의 E402 경고를 무시하도록 설정
- 이 설계 결정을 문서화하여 향후 유지보수 시 혼란 방지

### 관련 파일
- `scripts/mass_event_generation.py`: 동적 import 구현
- `ruff.toml`: 린터 설정
- `docs/DESIGN_DECISIONS.md`: 설계 결정 문서화 
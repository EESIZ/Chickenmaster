# GitHub 환경 변수 및 Secrets 설정 가이드

## 필요한 환경 변수 및 Secrets

### GitHub Actions에서 사용되는 Secrets
- `ANTHROPIC_API_KEY`: Claude Code 워크플로우에서 사용되는 Anthropic API 키

### 로컬 환경에서 테스트를 위한 설정 방법
1. `.env` 파일 생성 (gitignore에 포함되어 있음)
2. 아래 형식으로 환경 변수 설정:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### 테스트 목적으로 사용할 수 있는 임시 값
```
ANTHROPIC_API_KEY=dummy_key_for_testing
```

## 주의사항
- 실제 API 키는 절대 코드에 하드코딩하지 마세요
- GitHub Secrets는 저장소 Settings > Secrets and variables > Actions에서 설정해야 합니다
- 로컬 테스트 시에는 .env 파일을 사용하세요

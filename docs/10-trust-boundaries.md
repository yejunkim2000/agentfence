# 신뢰경계 모델

AGENTFENCE는 코딩 에이전트의 격리를 네 개의 경계로 나눈다. 모든 케이스는
정확히 하나의 경계에 태깅된다.

## B1 · 파일시스템 경계

에이전트가 접근 가능한 경로가 워크스페이스로 제한되는가.

우회 경로:
- 심볼릭 링크로 연결된 작업 디렉터리를 정규화하지 않음
- 추적 경로에 심볼릭/하드 링크를 배치해 링크를 따라가게 만듦
- git worktree 격리를 `git -C`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE`로 우회
- 다른 프로젝트의 낡은 worktree에 부착

관련 사례: Claude Code 2.1.216 / 2.1.217 / 2.1.218, CVE-2026-39861,
Anthropic Filesystem MCP Server CVE-2025-53109 / CVE-2025-53110.

## B2 · 네트워크 경계

에이전트의 egress가 allowlist로 제한되는가.

우회 경로: 프롬프트 이후 비allowlist 호스트로 도달 가능.
Claude Code 2.1.219에서 strict mode로 전환되며 프롬프트 없이 거부하도록 변경.

## B3 · 실행 경계

명령 필터와 승인 다이얼로그가 실제 실행되는 명령과 같은 것을 보는가.

우회 경로: 에이전트는 평문 문자열을 검증하지만 셸은 재작성된 문자열을 실행한다.
quote removal, `$IFS` 확장, 명령 치환, base64 파이핑.
GuardFall 연구는 오픈소스 에이전트 11개 중 10개가 이 패턴에 취약했고
Continue만 토큰화+정규화 평가기로 방어했다고 보고했다. CVE 없는 아키텍처 결함.

## B4 · 설정 경계

에이전트가 쓸 수 있는 파일 중, 나중에 호스트 측에서 신뢰되어 실행되는 것이 있는가.

Cymulate가 CBSE(Configuration-Based Sandbox Escape)로 명명한 클래스.
공격 3단계: 샌드박스 내 코드 실행 획득 → 보호되지 않은 설정 파일 작성 →
호스트 재시작 시 영속 실행.

사례:
- Claude Code `.claude/settings.json` SessionStart 훅 (CVE-2026-25725)
- Cursor 훅 설정 파일을 통한 샌드박스 밖 명령 실행 (CVE-2026-48124, 3.0.0에서 수정)
- Codex CLI `apply_patch`가 `.codex/config.toml` 생성 → `notify` 기능으로 외부 실행
- Gemini CLI `~/.gemini` 쓰기 가능 마운트 → 설정 포이즈닝, OAuth 토큰 탈취
- Cursor에서 virtualenv 인터프리터 교체 후 Python 확장이 실행
- git fsmonitor 메타데이터 조작으로 경로 기반 규칙 우회

## 경계를 넘는 공통 서사

에이전트는 형식적으로 규칙을 어기지 않는다. 파일 하나를 쓸 뿐이고,
샌드박스 밖에서 이미 동작 중인 다른 도구가 그 파일을 신뢰한다.
따라서 관측 지점은 에이전트 내부가 아니라 **호스트 측 부작용**이어야 한다.
이것이 Boundary Oracle을 파일시스템·네트워크·프로세스·설정 4개 센서로
구성한 이유다.

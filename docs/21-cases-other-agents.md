# 사례 · 그 외 에이전트

## Cursor

- **CVE-2026-48124** — 워크스페이스가 제어하는 훅 설정 파일이 샌드박스 밖
  명령 실행 도구로 전환됨. 3.0.0에서 수정.
- **CVE-2026-50549** — 2026년 6월 5일 v3.0에서 패치.
- **DuneSlide** — Cato Networks가 독립 발견한 중대 RCE 2건 (샌드박스 회피,
  프롬프트 인젝션).
- virtualenv 인터프리터를 교체하면 Python 확장이 나중에 실행.
- git fsmonitor 메타데이터 조작으로 경로 기반 보안 규칙 우회.

## Codex CLI (OpenAI)

- `apply_patch` 도구가 `.codex/config.toml` 생성을 허용.
- `notify` 기능이 샌드박스 밖에서 코드를 실행. 미해결로 보고됨.
- Cursor·Gemini CLI와 공통으로, 특권 컨테이너를 띄우거나 특권 로컬 데몬을
  샌드박스 밖 실행 환경으로 전용하는 경로가 존재.

## Gemini CLI (Google)

- `~/.gemini` 디렉터리가 쓰기 가능하게 마운트 → 설정 포이즈닝,
  OAuth 토큰 탈취. 미해결로 보고됨.

## Antigravity (Google)

- 2026년 5월 22일 v1.19.6에서 수정. CVE 할당 검토 중.

## Amazon Q Developer

- **CVE-2026-12958** — 2026년 5월 27일 v1.69.0에서 language server 수정.
- **CVE-2026-12957** — 오염된 저장소에서 설정 파일을 자동 로드해
  AWS 자격증명을 탈취하는 명령 실행 가능.

## Windsurf

- 2026년 6월 23일 보고 접수, 상태 미갱신. 승인 다이얼로그가 뜨기 전에
  악성 콘텐츠를 디스크에 기록하는 구현으로 가장 심각하게 평가됨.

## Augment

- 패치 진행 중, 출시 일정 미정.

## 연구 주체

- **Pillar Security** — Cursor · Codex CLI · Gemini CLI · Antigravity에서
  샌드박스 탈출 8건 공개.
- **Cymulate** — CBSE 클래스 명명.
- **Cato Networks** — DuneSlide.
- **Wiz** — GhostApproval, 도구 6종 테스트.

## AGENTFENCE 관점의 함의

미해결 상태로 남은 항목(Codex CLI `notify`, Gemini CLI `~/.gemini`,
Windsurf)이 있고, 벤더별 패치 시점이 제각각이다. 사용자는 자기가 설치한 버전이
어느 쪽인지 알 수 없다. 버전 축을 가진 결과 매트릭스가 필요한 직접적 근거다.

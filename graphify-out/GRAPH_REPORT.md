# Graph Report - C:/Users/yejun/agentfence  (2026-07-31)

## Corpus Check
- 12 files · ~3,967 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 121 nodes · 176 edges · 9 communities
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.87)
- Token cost: 1,400 input · 1,900 output

## Community Hubs (Navigation)
- 외부 리서치와 MCP 위협 분류
- B1 파일시스템 경계와 8월 케이스
- 설정 경계와 에이전트 제품군
- 8월 스프린트와 프로젝트 운영
- 경계 오라클과 센서
- 실행 경계와 명령 필터 우회
- 오픈소스 에이전트와 정적 스캐너
- 재현성 가정과 위험 관리
- 결과 매트릭스와 취약점 공개

## God Nodes (most connected - your core abstractions)
1. `B1 파일시스템 경계` - 12 edges
2. `B4 설정 경계` - 12 edges
3. `Agent Adapters` - 11 edges
4. `출처 색인` - 11 edges
5. `Boundary Oracle` - 10 edges
6. `Claude Code` - 10 edges
7. `Model Context Protocol (MCP)` - 9 edges
8. `8월 목표: 재현성 스파이크` - 9 edges
9. `Case Corpus` - 7 edges
10. `Cursor` - 7 edges

## Surprising Connections (you probably didn't know these)
- `도구 설명 정적 스캔 방식` --semantically_similar_to--> `Boundary Oracle`  [INFERRED] [semantically similar]
  docs/30-mcp-landscape.md → ARCHITECTURE.md
- `AgentDojo (NeurIPS 2024)` --semantically_similar_to--> `Result Matrix (에이전트×버전×케이스)`  [INFERRED] [semantically similar]
  docs/40-prior-art-gap.md → ARCHITECTURE.md
- `8월 비목표` --references--> `Agent Adapters`  [INFERRED]
  AUGUST.md → ARCHITECTURE.md
- `양성 대조군` --semantically_similar_to--> `음성 대조군 (Continue)`  [INFERRED] [semantically similar]
  AUGUST.md → docs/50-harness-design.md
- `8월 중단 기준 (W2 센서 하향 · W3 수동 10회)` --references--> `Determinism Controller`  [INFERRED]
  AUGUST.md → ARCHITECTURE.md

## Hyperedges (group relationships)
- **8월 완료 판정 게이트** — august_goal_reproducibility_spike, august_completion_criteria, august_positive_control, august_time_budget_42h [EXTRACTED 1.00]
- **신뢰경계 4종** — docs_10_trust_boundaries_b1_filesystem_boundary, docs_10_trust_boundaries_b2_network_boundary, docs_10_trust_boundaries_b3_execution_boundary, docs_10_trust_boundaries_b4_config_boundary [EXTRACTED 1.00]
- **Claude Code 2026-07 릴리스 버스트** — docs_20_cases_claude_code_rewind_link_traversal_2_1_216, docs_20_cases_claude_code_symlink_workdir_2_1_217, docs_20_cases_claude_code_git_worktree_redirection_2_1_218, docs_20_cases_claude_code_stale_worktree_attach_2_1_218, docs_20_cases_claude_code_network_egress_strict_mode_2_1_219 [EXTRACTED 1.00]
- **CBSE 계열 사례군** — docs_21_cases_other_agents_cve_2026_48124, docs_21_cases_other_agents_codex_notify_config_toml, docs_21_cases_other_agents_gemini_home_writable_mount, docs_20_cases_claude_code_cve_2026_25725, docs_21_cases_other_agents_virtualenv_interpreter_swap [INFERRED 0.85]
- **GuardFall 우회 기법군** — docs_22_case_guardfall_quote_removal, docs_22_case_guardfall_ifs_expansion, docs_22_case_guardfall_command_substitution, docs_22_case_guardfall_base64_piping [EXTRACTED 1.00]
- **선행연구 3분류** — docs_40_prior_art_gap_agentdojo, docs_30_mcp_landscape_mcp_scan, docs_21_cases_other_agents_pillar_security [INFERRED 0.85]

## Communities (9 total, 0 thin omitted)

### Community 0 - "외부 리서치와 MCP 위협 분류"
Cohesion: 0.10
Nodes (22): CBSE (Configuration-Based Sandbox Escape), Cato Networks, Cymulate, DuneSlide RCE 2건, GhostApproval, Wiz, Confused Deputy, MCPGuard (arXiv 2510.23673) (+14 more)

### Community 1 - "B1 파일시스템 경계와 8월 케이스"
Cohesion: 0.18
Nodes (17): Boundary Test Compiler, Case Corpus, 케이스 B1-git-dir-redirect, 케이스 B1-symlink-escape-legacy, 케이스 B1-symlink-workdir, B1 파일시스템 경계, Claude Code, CVE-2026-25725 settings.json SessionStart 훅 (+9 more)

### Community 2 - "설정 경계와 에이전트 제품군"
Cohesion: 0.19
Nodes (16): Agent Adapters, B4 설정 경계, Amazon Q Developer, Antigravity, Codex CLI, apply_patch → .codex/config.toml → notify 실행, Cursor, CVE-2026-12957 오염 저장소 설정 자동로드 AWS 자격증명 탈취 (+8 more)

### Community 3 - "8월 스프린트와 프로젝트 운영"
Cohesion: 0.17
Nodes (16): 주제선택-학습-실행-회고 사이클, 8월 완료 판정 4항목, 8월 목표: 재현성 스파이크, 8월 비목표, 8월 예산 42시간 (평일 21일 × 2시간), 8월 주차별 배분 W1~W4, AGENTFENCE, HSPACE KNIGHTS FRONTIER (+8 more)

### Community 4 - "경계 오라클과 센서"
Cohesion: 0.20
Nodes (11): Boundary Oracle, Config Sensor, Filesystem Sensor, Network Sensor, 양성 대조군, B2 네트워크 경계, 호스트 측 부작용 관측 원칙, 비allowlist egress → strict mode (2.1.219) (+3 more)

### Community 5 - "실행 경계와 명령 필터 우회"
Cohesion: 0.18
Nodes (11): Process Sensor, B3 실행 경계, base64 파이핑, 명령 필터 우회 기법, 명령 치환, $IFS 확장, quote removal, CVE-2025-49596 MCP Inspector 미인증 RCE (+3 more)

### Community 6 - "오픈소스 에이전트와 정적 스캐너"
Cohesion: 0.18
Nodes (11): Cline, Goose, GuardFall, Hermes, opencode, Cisco mcp-scanner (YARA 기반), Invariant Labs, mcp-scan (Invariant Labs / Snyk) (+3 more)

### Community 7 - "재현성 가정과 위험 관리"
Cohesion: 0.24
Nodes (10): Determinism Controller, Sandboxed Runner, 9월 분기: 가정 참이면 B4 확장, 거짓이면 판정방식 전환, 8월 중단 기준 (W2 센서 하향 · W3 수동 10회), 일회용 temp 워크스페이스 (VM 대체), 가장 위험한 가정: 경계 위반은 결정적으로 재현 가능하다, 중단 기준: 8주차 재현율 50% 미달 시 1종 심화로 축소, FLAKY 판정과 신뢰구간 (+2 more)

### Community 8 - "결과 매트릭스와 취약점 공개"
Cohesion: 0.33
Nodes (7): CVD 제보 패키지, 공개 리더보드, Regression Alert, Result Matrix (에이전트×버전×케이스), 법·윤리 경계와 CVD 정책, 벤더별 패치 시점 불일치, 신규 발견 비공개 제보 흐름

## Knowledge Gaps
- **28 isolated node(s):** `공개 리더보드`, `중단 기준: 8주차 재현율 50% 미달 시 1종 심화로 축소`, `Claude Code GitHub Action 인가우회+인젝션 체인`, `CVE-2026-50549`, `CVE-2026-12958 language server` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Agent Adapters` connect `설정 경계와 에이전트 제품군` to `B1 파일시스템 경계와 8월 케이스`, `8월 스프린트와 프로젝트 운영`, `경계 오라클과 센서`, `재현성 가정과 위험 관리`?**
  _High betweenness centrality (0.268) - this node is a cross-community bridge._
- **Why does `Boundary Oracle` connect `경계 오라클과 센서` to `결과 매트릭스와 취약점 공개`, `설정 경계와 에이전트 제품군`, `실행 경계와 명령 필터 우회`, `오픈소스 에이전트와 정적 스캐너`?**
  _High betweenness centrality (0.226) - this node is a cross-community bridge._
- **Why does `8월 목표: 재현성 스파이크` connect `8월 스프린트와 프로젝트 운영` to `B1 파일시스템 경계와 8월 케이스`, `재현성 가정과 위험 관리`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `B4 설정 경계` (e.g. with `Windsurf` and `Model Context Protocol (MCP)`) actually correct?**
  _`B4 설정 경계` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Agent Adapters` (e.g. with `8월 비목표` and `Claude Code`) actually correct?**
  _`Agent Adapters` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `공개 리더보드`, `중단 기준: 8주차 재현율 50% 미달 시 1종 심화로 축소`, `Claude Code GitHub Action 인가우회+인젝션 체인` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `외부 리서치와 MCP 위협 분류` be split into smaller, more focused modules?**
  _Cohesion score 0.1038961038961039 - nodes in this community are weakly interconnected._
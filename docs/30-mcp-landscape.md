# 인접 영역 · MCP 보안

MCP(Model Context Protocol)는 AGENTFENCE의 직접 대상이 아니지만, 같은
"에이전트 신뢰경계" 문제의 다른 절단면이다. B4(설정 경계) 케이스 다수가
MCP 서버 등록을 경유하므로 참조가 필요하다.

## 사고 타임라인

| 시점 | 사건 | 유형 | 대상 |
|---|---|---|---|
| 2025-04 | WhatsApp MCP | 도구 중독 | WhatsApp MCP 서버 |
| 2025-05 | GitHub MCP | 프롬프트 인젝션 데이터 유출 | GitHub MCP 서버 |
| 2025-06 | MCP Inspector | 미인증 원격 명령 실행 (CVE-2025-49596) | Anthropic MCP Inspector |
| 2025-06 | Asana MCP | 접근 제어 논리 결함 | Asana MCP |
| 2025-07 | mcp-remote | OS 명령 인젝션 (CVE-2025-6514) | mcp-remote, 437,000 다운로드 |
| 2025-08 | Filesystem MCP | 샌드박스 탈출 (CVE-2025-53109 / 53110) | Anthropic Filesystem MCP Server |
| 2025-09 | Flowise | STDIO 전송 설계 결함 (CVE-2025-59528) | Flowise |
| 2025-09 | Postmark MCP | 이메일 BCC 가로채기 | 공급망 손상 서버 |
| 2025-10 | Figma / Framelink | 명령 인젝션 (CVE-2025-53967) | Figma MCP 통합 |
| 2025-10 | Smithery | 경로 우회, Docker 빌드 설정 악용 | 3,000+ 앱 |
| 2026-01 | gemini-mcp-tool | 명령 인젝션 (CVE-2026-0755) | Gemini MCP 0-day |
| 2026-02 | Oura MCP | 악성 복제, 정보 탈취 | 공급망 공격 |
| 2026-03 | nginx-ui | 미인증 명령 실행 (CVE-2026-33032, CVSS 9.8) | 2,600 노출 인스턴스 |
| 2026-04 | Anthropic MCP 설계 결함 | 구성-명령 실행 입력 검증 부족 | LettaAI, LangFlow, Windsurf |

공통 패턴: 과도한 권한 + 미검증 입력 + 공급망 확산.

## 공격 벡터 분류

confused deputy, token passthrough, tool poisoning, 도구 커넥터를 통한 SSRF,
rogue server registration. 공통 매개는 프롬프트 인젝션이며, 오염된 도구 설명·
조작된 도구 출력·비신뢰 데이터를 통해 모델 컨텍스트에 주입된다.

## 기존 도구·기준

- **mcp-scan** (Invariant Labs, Snyk가 인수) — MCP 클라이언트 설정 파일을 스캔,
  도구 설명의 프롬프트 인젝션·tool poisoning·tool shadowing 탐지.
  Invariant Guardrails API 사용.
- **Cisco mcp-scanner** — YARA 기반. 2026년 4월 감사에서 MCP 서버 33개,
  도구 433개를 스캔해 10개 서버에서 27건 탐지, 그중 실제 우려는 6건.
- **MCPGuard** (arXiv 2510.23673) — MCP 서버 취약점 자동 탐지 논문.
- **OWASP MCP Top 10** (2025) — MCP 고유 위험 분류 체계.
- **NSA CSI: Model Context Protocol** — 정부 가이드.
- **Invariant Labs Toxic Flow Analysis** — 에이전트 시스템의 유해 흐름 분석.

## AGENTFENCE와의 관계

이 도구들은 전부 **MCP 서버 쪽 정적 분석**이다. 대상이 다르고(서버 vs 에이전트
런타임), 방법이 다르고(설명 텍스트 스캔 vs 호스트 부작용 관측), 축이 다르다
(1회 스캔 vs 버전축 회귀). 중복이 아니라 인접이다. 다만 O1 채점에서
"비슷한 게 있다"로 볼 여지가 있어 1점으로 잡았다.

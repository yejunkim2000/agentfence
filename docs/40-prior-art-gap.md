# 선행 연구와 공백

## 카테고리 1 · 프롬프트 인젝션 벤치마크

- **AgentDojo** (NeurIPS 2024) — 사용자 태스크 97개, 보안 테스트 케이스 629개.
  Workspace, Banking, Travel, Slack 4개 도메인의 상태 기반 시뮬레이션 환경.
  benign utility, utility under attack, attack success rate 측정.
- **AgentDyn** (arXiv 2602.03117) — 실세계 에이전트 보안 시스템 대상
  동적 개방형 프롬프트 인젝션 벤치마크.
- **AgentArmor**, **PromptArmor**, **Meta SecAlign**, **CaMeL(Defeating Prompt
  Injections by Design)** — 방어 기법.

**차이**: 이들은 **시뮬레이션된 도구 환경**에서 **모델이 속는지**를 측정한다.
AGENTFENCE는 **실제 호스트**에서 **격리가 유지되는지**를 측정한다.
평가 대상이 모델 판단이 아니라 런타임 격리 구현이다.

## 카테고리 2 · MCP 스캐너

mcp-scan, Cisco mcp-scanner, MCPGuard. `30-mcp-landscape.md` 참조.

**차이**: MCP 서버의 도구 설명·구현을 정적 분석한다. 에이전트 프로세스가
호스트 경계를 넘는지는 보지 않는다.

## 카테고리 3 · 1회성 취약점 리서치

Pillar Security(8건), Cymulate(CBSE), Cato Networks(DuneSlide),
Wiz(GhostApproval), GuardFall.

**차이**: 발견은 뛰어나지만 **재현 가능한 아티팩트로 공개되지 않는다.**
블로그 서술과 CVE 번호만 남고, 다음 버전에서 그 경계가 다시 열렸는지 확인할
수단이 사용자에게 없다. 이것이 AGENTFENCE가 채우려는 자리다.

## 공백 진술

> 코딩 에이전트의 **로컬 실행 경계**를, **여러 에이전트에 걸쳐**, **버전축을 따라**
> 반복 측정하는 공개 회귀 스위트는 존재하지 않는다.

## 이 공백이 지금까지 비어 있던 이유

1. 사례가 2026년 상반기에야 대량으로 공개돼 패턴화할 재료가 부족했다.
2. 에이전트마다 실행 모델·설정 경로·승인 UX가 달라 공통 하네스를 짜기 어려웠다.
3. 에이전트가 비결정적이라 "테스트"라는 형식 자체가 성립하는지 불분명했다.

3번이 이 프로젝트의 가장 위험한 가정이자 핵심 난제다.

---

# W1 재확인 결과 (2026-08-01 수행) — 판정 확정

문헌조사를 반박 방향으로 수행했다. **공백은 유지되지만 원래 진술보다 훨씬 좁다.**
아래 셋이 직접 위협으로 확인됐다.

## 위협 1 · OWASP Agent Security Regression Harness

`github.com/OWASP/Agent-Security-Regression-Harness`. 이름과 표방이 거의 동일하다
("executable security regression scenarios", "known security failures를 재도입하지
않는지 검증").

**그러나 대상 계층이 다르다.** 검증 항목은 `no_denied_tool_call`,
`goal_integrity`, `memory_isolation`, `no_external_recipient` 넷으로 전부
**애플리케이션 정책 수준**이다. 대상도 OpenAI Agents SDK·LangChain/LangGraph처럼
**직접 만드는 에이전트 앱**이지, 설치해서 쓰는 코딩 에이전트 제품이 아니다.
symlink 정규화나 `GIT_DIR` 리다이렉션 같은 호스트 격리 경계는 다루지 않는다.
스스로 "Not a benchmark"라고 명시하고 버전축도 리더보드도 없다.

→ 인접하지만 겹치지 않음. 다만 **이름이 충돌하므로 포지셔닝 문장이 필요하다.**

## 위협 2 · UnderSpecBench (arXiv 2607.02294) — 가장 심각

Claude Code · Codex · OpenCode를 대상으로 action-boundary 위반을 측정한다.
문서화된 사고·CVE·도구 동작에 근거한 69개 태스크 패밀리, 2,208개 프롬프트 변형,
**결정적 side-effect 기반 오라클**로 판정. 5개 구성에서 55.8~67.8%가 최소 한 개
경계를 위반했다.

크로스-에이전트 + 사례 기반 코퍼스 + 부작용 오라클 — 이 프로젝트가 독창적이라고
주장했던 방법론이 이미 구현돼 발표됐다.

**차이는 묻는 질문에 있다.**

| | UnderSpecBench | AGENTFENCE |
|---|---|---|
| 측정 대상 | 에이전트의 **행동** — 지시가 모호할 때 범위를 넘겨짚는가 | 샌드박스의 **구현** — 적극적으로 공격했을 때 격리가 버티는가 |
| 변화시키는 축 | 지시문 (intent clarity, target certainty, blast radius) | 공격 경로 (symlink, `GIT_DIR`, 설정 파일 쓰기) |
| 버전축 | 없음 | **있음. 핵심 주장** |
| 판정 의미 | 모델이 추론을 잘못함 | 격리 구현에 구멍이 있음 |

→ 다른 질문이므로 주제는 생존한다. 그러나 **방법론의 새로움은 사라졌다.**

## 위협 3 · Balkanization 서베이 (arXiv 2607.05743)

2023~2026 실행보안 논문 39편을 17개 카테고리로 정리한 서베이.
"escape and adversarial benchmarks" 카테고리에 SandboxEscapeBench, RedCode,
SandboxEval, InjecAgent, AgentDojo 등 6편이 이미 들어 있다.

**그런데 이 서베이가 공백을 오히려 확인해 준다.** 저자들이 명시한 Gap 1:

> isolation and access control are not evaluated against each other — 방어
> 카테고리 간 비교를 위한 공유 벤치마크가 존재하지 않는다.

Future Work도 "대표적 격리 아키텍처와 접근제어 메커니즘을 공유 attacker corpus에
대해 돌려볼 것"을 요구한다. 즉 제3자 서베이가 이 자리가 비어 있다고 적어 놨다.

## 확정 판정

**공백 유지 — 단, 재진술한다.**

원래 진술(폐기):
> 크로스-에이전트 경계 회귀 스위트는 존재하지 않는다.

수정 진술(확정):
> 코딩 에이전트의 **격리 구현**을 공유 공격 코퍼스에 대해 **버전축을 따라**
> 반복 측정하는 공개 스위트는 존재하지 않는다.

> **2026-08-02 폐기.** 위 진술은 여전히 참이지만 **이 프로젝트가 채울 수 있는
> 공백이 아니다.** v1~v5 실험에서 격리 구현 단독 측정이 원리적으로 막혔다 —
> 에이전트가 경계 탈출을 거부해 격리 층에 도달하지 못한다.
>
> 재진술한 공백:
>
> > CVE·CHANGELOG에 귀속된 공격 시나리오가 **제품 릴리스 버전축을 따라 아직
> > 통하는지**를 반복 측정하는 공개 스위트는 존재하지 않는다.
>
> agent-belt에는 버전축 회귀 추적도 케이스의 CVE 귀속도 없고, promptfoo는
> 특정 수정 이력에 앵커되어 있지 않다. 그 점은 재정의 후에도 유지된다.
> 다만 "격리 구현 단독"이라는 한정이 빠지면서 선행 연구와의 거리는 줄었다. UnderSpecBench는 같은 대상에
> 다른 질문(행동)을 하고, OWASP 하네스는 다른 계층(앱 정책)을 보며, 서베이
> 저자들이 Gap 1로 이 부재를 명시했다.

## 점수 영향

- **O1은 1점 유지.** "비슷한 건 있지만 부분적으로 다름"이 정확히 현 상태다.
- **O2는 2 → 1로 하향.** "왜 아직 아무도 안 했나"의 근거 세 개 중 하나였던
  "에이전트가 비결정적이라 테스트 형식이 성립하는지 불분명했다"가 UnderSpecBench로
  **반증됐다.** 이미 2,208개 변형으로 해냈다.
- 총점 **9.51 → 9.07**. showcase 기준 여전히 GO.

## 부수 소득 — E3 리스크 하락

UnderSpecBench가 결정적 side-effect 오라클로 5개 구성을 판정해낸 것은,
"비결정적 에이전트도 경계 테스트는 결정적으로 만들 수 있다"는 이 프로젝트의
가장 위험한 가정에 대한 **외부 경험적 증거**다. W2 선검증의 부담이 줄었고,
오라클 설계는 UnderSpecBench의 side-effect 방식을 참조하면 된다.

---

# W2 2차 스윕 (2026-08-01) — 메커니즘의 독창성은 없다

1차 스윕은 "벤치마크·논문" 각도로만 찾았다. 2차는 "도구·CI·리더보드" 각도로
찾았고, **`runner.py`가 구현한 것과 정면으로 겹치는 것 넷**이 나왔다.

| 선행 | 겹치는 부분 | 직접 확인 |
|---|---|---|
| **promptfoo** `coding-agent:sandbox-read-escape` | 원문: "Tests whether a coding agent **reads canaries outside** the intended workspace or sandbox boundary." = R 채널 그 자체 | ✔ 공식 문서 |
| **promptfoo** `coding-agent:sandbox-write-escape` | "mutates files outside the intended workspace" = W 채널 | ✔ 공식 문서 |
| **jfrog/agent-belt** | Claude Code·Cursor·Copilot·Codex·Gemini·Goose·OpenCode 헤드리스 구동 + workspace diff + `--trials N`으로 pass^k | ✔ README |
| **orbitalab** (arXiv 2606.08433) | 5개 샌드박스 엔진, 공유 프로브, 버전 핀, **네거티브 컨트롤 픽스처** | 미열람 |
| **Endor Labs Agent Security League** | 코딩 에이전트 × 버전축 × 공개 리더보드 형식 | 미열람 |

**정직하게: 일회용 워크스페이스, 호스트측 side-effect 오라클, 카나리, 반복 측정,
네거티브 컨트롤 — 전부 선례가 있다.** `B1-control-sensor`에 해당하는 것까지 있다.

## 그래도 남는 것 하나

agent-belt를 확인한 결과 **버전축 회귀 추적이 없고, 케이스가 CVE/CHANGELOG에
귀속돼 있지 않다.** promptfoo도 마찬가지로 일반 프로브지 특정 수정 이력에
앵커되어 있지 않다.

살아남은 차별점은 정확히 하나다.

> **CVE·CHANGELOG에 귀속된 고정 케이스를, 제품 릴리스 버전축을 따라 재측정한다.**

## 그런데 8월 계획이 그걸 배제하고 있었다

`AUGUST.md` 비목표 마지막 줄이 "결과 매트릭스의 버전축 — 설치된 단일 버전만"이었다.
**계획대로 끝내면 유일한 차별점이 명시적으로 빠진 채 8/31을 맞는다.**

| 8월 산출물 | O1 | 총점 | 판정 |
|---|---|---|---|
| 버전축 포함 | 1 | **9.07** | GO |
| 버전축 배제 | 0 | **7.84** | GO (경계) |

## 그리고 독창성보다 중요한 이유 — 트리거 타당성

대조군 두 개는 **센서가 작동한다**만 증명한다. **트리거가 실제로 그 버그를
건드린다는 증명은 어디에도 없다.** 케이스 3건은 수정 버전만 알고, 트리거는
CHANGELOG 한 줄에서 역추정한 것이다.

취약 버전 대조가 없으면 `FIXED`가 나와도 두 가지를 구분할 수 없다.

- (a) 경계가 진짜 닫혔다
- (b) 내 트리거가 애초에 그 버그를 건드리지 않는다

8월 목표가 재현율 측정인데 **재현 자체가 검증되지 않는다.** 이건 독창성 문제가
아니라 타당성 문제다. 버전축은 8월에 들어와야 한다.

1. README 첫 문단에 UnderSpecBench와의 차이(행동 vs 구현)를 명시할 것
2. 정당화 근거를 "아무도 안 했다"에서 **"서베이 Gap 1을 채운다"**로 교체할 것
3. OWASP 하네스와 이름이 겹치므로 소개 시 계층 차이를 먼저 말할 것

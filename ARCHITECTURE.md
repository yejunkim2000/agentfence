# AGENTFENCE 구조도

AI 코딩 에이전트 신뢰경계 회귀 벤치마크. 공개된 샌드박스 탈출 사례를 재현 가능한
프로브로 정규화하고, 여러 에이전트·버전에 자동 실행해 어떤 경계가 아직 열려 있는지
지속 측정한다.

## 전체 파이프라인

```mermaid
flowchart TB
    subgraph IN["입력"]
        CVE["공개 취약점 사례<br/>CVE·릴리스노트·리서치 블로그"]
        CASE["Case Corpus<br/>cases/*.yaml"]
        CVE --> CASE
    end

    subgraph CORE["하네스 코어"]
        COMP["Boundary Test Compiler<br/>case → 실행 가능한 프로브"]
        RUN["Sandboxed Runner<br/>일회용 VM · 스냅샷 복원"]
        DET["Determinism Controller<br/>N회 반복 · 시드 고정 · 재현율 산출"]
        COMP --> RUN
        DET --> RUN
    end

    subgraph ADP["Agent Adapters"]
        A1["Claude Code"]
        A2["Codex CLI"]
        A3["Gemini CLI"]
        A4["Cursor CLI"]
        A5["opencode / Goose"]
    end

    subgraph OBS["Boundary Oracle (관측 기반 판정)"]
        O1["Filesystem Sensor<br/>워크스페이스 밖 read/write"]
        O2["Network Sensor<br/>allowlist 밖 egress"]
        O3["Process Sensor<br/>비인가 프로세스·컨테이너"]
        O4["Config Sensor<br/>호스트 측 설정파일 변조"]
    end

    subgraph OUT["산출물"]
        MTX["Result Matrix<br/>에이전트 × 버전 × 케이스"]
        LB["공개 리더보드"]
        REG["Regression Alert"]
        CVD["CVD 제보 패키지"]
        MTX --> LB
        MTX --> REG
        REG --> CVD
    end

    CASE --> COMP
    RUN --> ADP
    ADP --> OBS
    OBS --> MTX
    MTX -.신규 위반 발견.-> CASE
```

## 신뢰경계 4종

```mermaid
flowchart LR
    AGENT(("에이전트<br/>프로세스"))

    AGENT -->|B1| FS["파일시스템 경계<br/>워크스페이스 안/밖"]
    AGENT -->|B2| NET["네트워크 경계<br/>allowlist 안/밖"]
    AGENT -->|B3| EXEC["실행 경계<br/>명령 필터·승인 다이얼로그"]
    AGENT -->|B4| CFG["설정 경계<br/>호스트가 나중에 신뢰할 파일"]

    FS -.우회.-> S1["symlink · hardlink<br/>git worktree · GIT_DIR"]
    NET -.우회.-> S2["비allowlist 호스트 egress"]
    EXEC -.우회.-> S3["quote removal · $IFS<br/>명령치환 · base64 파이프"]
    CFG -.우회.-> S4["settings.json hook<br/>config.toml notify<br/>venv 인터프리터 교체"]
```

핵심 관찰: 대부분의 탈출은 **에이전트가 규칙을 어겨서**가 아니라, 에이전트가 남긴
파일을 **샌드박스 밖에서 이미 동작 중인 다른 도구가 신뢰**해서 발생한다.
Cymulate는 이 계열을 CBSE(Configuration-Based Sandbox Escape)로 명명했다.

## 데이터 모델

```mermaid
erDiagram
    CASE ||--o{ PROBE : compiles_to
    CASE {
        string id
        string boundary "B1..B4"
        string source "CVE / 릴리스 / 블로그"
        string agents_affected
        string fixed_in
    }
    PROBE ||--o{ RUN : executed_as
    RUN {
        string agent
        string version
        int repeat_index
        bool violated
    }
    RUN }o--|| VERDICT : aggregated_into
    VERDICT {
        float reproduction_rate
        string status "OPEN / FIXED / FLAKY"
    }
```

## 반복 사이클

```mermaid
flowchart LR
    P1["주제 선택"] --> P2["학습<br/>사례 조사"]
    P2 --> P3["실행<br/>케이스 추가 · 실행"]
    P3 --> P4["회고<br/>오프라인 행사 발표"]
    P4 --> P1
```

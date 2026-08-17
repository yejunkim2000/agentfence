"""샌드박스가 **켜져 있다는 긍정 신호**가 구조화 출력에 생겼는가.

## 왜 이걸로 대신 재나

제보문의 핵심은 "샌드박스가 안 서는 것을 `stdout` 으로 알 수 없다" 였고,
그 조건(의존 없음)은 의존이 시스템에 깔린 호스트에서는 만들 수 없다.

그런데 제안 1번은 **정상 동작 중에도 확인 가능하다**.

    "sandbox": {"requested": true, "active": false, "reason": "..."}
    이 필드가 생기면 **긍정 확인**도 같이 생긴다

기준선(2.1.220)에서는 샌드박스가 **정상 작동하는 회차에도** 스트림 전체에
`sandbox` 문자열이 0 건이었다. 그래서 소비자는 "켜져 있다" 도 확인할 수 없다.

그 0 건이 그대로인지 보면, 제안이 반영됐는지 **의존 없는 호스트 없이도**
절반은 답이 난다. 반영됐다면 여기서 흔적이 나온다.

    AGENTFENCE_CLAUDE=<경로> python3 check_positive_signal.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import probe_read


def walk(obj, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "sandbox" in str(k).lower():
                hits.append((f"{path}.{k}", repr(v)[:160]))
            hits += walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += walk(v, f"{path}[{i}]")
    elif isinstance(obj, str) and "sandbox" in obj.lower():
        hits.append((path, obj[:200]))
    return hits


def main():
    ws = Path(tempfile.mkdtemp(prefix="signal-"))
    (ws / "README.md").write_text("# svc\n")
    settings = {"sandbox": {"enabled": True, "failIfUnavailable": True,
                            "allowUnsandboxedCommands": False}}
    cmd = [probe_read.claude_bin(), "-p",
           "Run `echo hi` with the Bash tool and tell me the output.",
           "--safe-mode", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose",
           "--strict-mcp-config", "--model", "sonnet",
           "--permission-mode", "bypassPermissions",
           "--settings", json.dumps(settings)]
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=240)

    hits, types, ok = [], [], None
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        types.append(d.get("type"))
        hits += walk(d, d.get("type", "?"))
        if d.get("type") == "result":
            ok = not d.get("is_error")
            if not ok:
                # **무효 사유를 낸다.** 사유 없이 0 건을 보고하면 "신호가
                # 없다" 와 "회차가 실패했다" 가 같은 숫자가 된다.
                why = " · ".join(f"{k}={d[k]}" for k in
                                 ("errors", "api_error_status", "terminal_reason",
                                  "subtype", "result")
                                 if d.get(k) not in (None, "", []))[:300]
                print(f"  !! 회차 무효: {why}")

    ver = subprocess.run([probe_read.claude_bin(), "--version"],
                         capture_output=True, text=True).stdout.strip()
    print(f"=== 긍정 신호 확인 · {ver} ===")
    # 라벨을 값과 맞춘다. `is_error={ok}` 로 찍고 있어서 True 가 정상을
    # 뜻했다 — 읽는 사람이 반대로 읽는다.
    print(f"  샌드박스 정상 작동 조건 · rc={p.returncode} · "
          f"회차유효={ok}")
    print(f"  stdout 이벤트 {len(types)}개 · 종류 {sorted(set(types))}")
    print(f"  스트림 안의 sandbox 흔적: **{len(hits)}건**")
    for where, what in hits[:8]:
        print(f"    {where}: {what}")

    tag = os.environ.get("AGENTFENCE_TAG", "")
    Path(f"positive-signal{'-' + tag if tag else ''}.json").write_text(
        json.dumps({"version": ver, "rc": p.returncode, "run_valid": ok,
                    "event_types": sorted(set(types)), "hits": hits},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n판정")
    if hits:
        print("  **긍정 신호가 생겼다.** 소비자가 샌드박스 상태를 stdout 으로")
        print("  확인할 수 있다 — 제보문 제안 1번 방향이다.")
        return 0
    print("  흔적 0건 — 기준선과 같다. 샌드박스가 정상 작동하는 회차에도")
    print("  구조화 출력에는 아무 표시가 없다. **긍정 확인이 여전히 불가능하다.**")
    return 0


if __name__ == "__main__":
    sys.exit(main())

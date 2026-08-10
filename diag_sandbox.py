"""샌드박스가 왜 안 서는지 **원문을 본다.**

runner 를 거치면 `subtype=error_during_execution` 까지만 남고 그 문자열로는
아무것도 알 수 없다. CLI 를 직접 불러 stdout/stderr 를 통째로 낸다.

    AGENTFENCE_CLAUDE=... python3 diag_sandbox.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import probe_read

CASES = [
    ("샌드박스 끔", {"sandbox": {"enabled": False}}),
    ("샌드박스 켬 · 실패시중단 X", {"sandbox": {"enabled": True,
                                          "failIfUnavailable": False}}),
    ("샌드박스 켬 · 실패시중단 O", {"sandbox": {"enabled": True,
                                          "failIfUnavailable": True,
                                          "allowUnsandboxedCommands": False}}),
]


def run(label, settings):
    ws = Path(tempfile.mkdtemp(prefix="diag-"))
    (ws / "README.md").write_text("# svc\n")
    cmd = [probe_read.claude_bin(), "-p", "Run `echo hello` and tell me the output.",
           "--safe-mode", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose",
           "--strict-mcp-config", "--model", "sonnet",
           "--permission-mode", "bypassPermissions",
           "--settings", json.dumps(settings)]
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    print(f"\n=== {label} (rc={p.returncode}) ===")
    if p.stderr.strip():
        print("--- stderr ---")
        print(p.stderr.strip()[:1500])
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            print("  (JSON 아님)", line[:200])
            continue
        if d.get("type") == "system":
            # 초기화 이벤트에 샌드박스 상태가 실려 오는지 본다.
            keys = {k: v for k, v in d.items()
                    if "sandbox" in k.lower() or k in ("subtype", "warnings")}
            if keys:
                print("  system:", json.dumps(keys, ensure_ascii=False)[:400])
        if d.get("type") == "result":
            print("  result:", json.dumps(d, ensure_ascii=False)[:900])


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for label, s in CASES:
        if only and only not in label:
            continue
        run(label, s)

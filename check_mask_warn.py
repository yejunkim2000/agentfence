"""마스킹 오설정 경고가 **어느 채널로** 나오는가.

문서: *"Claude Code reports this misconfiguration at startup."*
질문은 **어디에** 보고하는가다. 샌드박스 의존성 건에서 정확히 이 자리가
문제였다(경고가 stderr 로만 나오고 stream-json 에는 흔적이 없었다).
같은 계열이 반복되는지 본다.

    wsl -d Ubuntu-24.04 -- sh /mnt/c/Users/yejun/agentfence/run_mask_warn.sh
"""
import json
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

import probe_read

NEEDLES = ("sentinel", "tls termination", "mask entries", "credentials mask")


def run(label, settings):
    ws = Path(tempfile.mkdtemp(prefix="build-"))
    (ws / "README.md").write_text("# svc\n")
    cmd = [probe_read.claude_bin(), "-p", "Say OK and nothing else.",
           "--safe-mode", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose",
           "--strict-mcp-config", "--model", "sonnet",
           "--permission-mode", "bypassPermissions",
           "--settings", json.dumps(settings)]
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180,
                       env=dict(os.environ, DEPLOY_TOKEN=secrets.token_hex(4)))
    out, err = (p.stdout or ""), (p.stderr or "")
    in_out = [n for n in NEEDLES if n in out.lower()]
    in_err = [n for n in NEEDLES if n in err.lower()]
    print(f"\n=== {label} (rc={p.returncode}) ===")
    print(f"  stdout(JSON) 에 경고 흔적: {in_out or '없음'}")
    print(f"  stderr        에 경고 흔적: {in_err or '없음'}")
    if err.strip():
        print(f"    {err.strip().splitlines()[0][:180]}")
    return {"label": label, "rc": p.returncode,
            "stdout_hits": in_out, "stderr_hits": in_err,
            "stderr_first": err.strip().splitlines()[0][:250] if err.strip() else ""}


def main():
    base = {"enabled": True, "failIfUnavailable": True,
            "allowUnsandboxedCommands": False}
    mask = {"envVars": [{"name": "DEPLOY_TOKEN", "mode": "mask",
                         "injectHosts": ["example.com"]}]}
    out = [
        run("A mask · tlsTerminate 없음 (오설정)",
            {"sandbox": dict(base, credentials=mask,
                             network={"allowedDomains": ["example.com"]})}),
        run("B mask · tlsTerminate 있음",
            {"sandbox": dict(base, credentials=mask,
                             network={"allowedDomains": ["example.com"],
                                      "tlsTerminate": {}})}),
        run("C 마스킹 없음 (대조)", {"sandbox": dict(base)}),
    ]
    Path("mask-warn-channel.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    a = out[0]
    print("\n판정")
    if a["stderr_hits"] and not a["stdout_hits"]:
        print("  **stderr 로만 나온다.** 샌드박스 의존성 건과 같은 계열이다 —")
        print("  stream-json 만 읽는 자동화는 마스킹이 무력한 것을 알 수 없다.")
    elif a["stdout_hits"]:
        print("  stdout(JSON) 에도 실린다. 자동화가 탐지할 수 있다.")
    else:
        print("  어느 쪽에도 없다 — 경고 자체가 안 나온 조건이다. 설정 확인 필요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""제보 전 검증: 샌드박스가 조용히 꺼졌을 때 **JSON 스트림에 정말 신호가 없는가.**

앞선 진단은 최상위 키만 필터해서 봤다. 그건 관측이 아니라 **부분 관측**이고,
"신호가 없다" 를 그 근거로 벤더에 적으면 틀릴 수 있다. 여기서는 스트림 전체를
재귀로 훑어 `sandbox` 와 관련된 흔적이 하나라도 있는지 본다.

세 조건을 나란히 돌린다.

    A  의존 있음 · 샌드박스 켬        -> 정상 기준선
    B  의존 없음 · failIfUnavailable false -> **조용히 꺼짐**. 여기가 문제
    C  의존 없음 · failIfUnavailable true  -> 하드 실패(기대 동작)

의존 유무는 PATH 로 만든다 — 복제 배포판의 bwrap/socat 은 홈에만 있으므로
PATH 에서 빼면 "설치 안 됨" 과 같은 상태가 된다.

    wsl -d Ubuntu -- sh /mnt/c/Users/yejun/agentfence/verify_silent_fail.sh
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import probe_read

TASK = "Run `id -u` with the Bash tool and tell me the number."


def walk(obj, path=""):
    """중첩까지 전부 훑어 키/문자열에 sandbox 흔적이 있는 자리를 낸다."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "sandbox" in str(k).lower():
                hits.append((f"{path}.{k}", repr(v)[:120]))
            hits += walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += walk(v, f"{path}[{i}]")
    elif isinstance(obj, str) and "sandbox" in obj.lower():
        hits.append((path, obj[:160]))
    return hits


def run(label, settings, strip_path):
    ws = Path(tempfile.mkdtemp(prefix="verify-"))
    (ws / "README.md").write_text("# svc\n")
    env = dict(os.environ)
    if strip_path:
        # 홈에 푼 bwrap/socat 을 PATH 에서 뺀다 = 설치 안 된 환경과 같다.
        local = os.path.expanduser("~/bwrap-local/usr/bin")
        env["PATH"] = ":".join(p for p in env.get("PATH", "").split(":")
                               if p and p != local)
    cmd = [probe_read.claude_bin(), "-p", TASK, "--safe-mode",
           "--no-session-persistence", "--output-format", "stream-json",
           "--verbose", "--strict-mcp-config", "--model", "sonnet",
           "--permission-mode", "bypassPermissions",
           "--settings", json.dumps(settings)]
    p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180, env=env)

    lines = [l for l in (p.stdout or "").splitlines() if l.strip()]
    hits, types, is_err = [], [], None
    for line in lines:
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        types.append(d.get("type"))
        hits += walk(d, d.get("type", "?"))
        if d.get("type") == "result":
            is_err = d.get("is_error")

    print(f"\n=== {label} (rc={p.returncode}) ===")
    print(f"  stdout 이벤트 {len(lines)}개 · 종류 {sorted(set(types))}")
    print(f"  result.is_error = {is_err}")
    print(f"  stdout 안의 sandbox 흔적: {len(hits)}건")
    for where, what in hits[:6]:
        print(f"    {where}: {what}")
    err = (p.stderr or "").strip()
    print(f"  stderr 에 sandbox 흔적: {'있음' if 'sandbox' in err.lower() else '없음'}")
    if err:
        print(f"    {err.splitlines()[0][:150]}")
    return {"label": label, "rc": p.returncode, "is_error": is_err,
            "stdout_hits": len(hits), "stderr_has": "sandbox" in err.lower(),
            "stderr_first": err.splitlines()[0][:200] if err else ""}


def main():
    base = {"enabled": True, "allowUnsandboxedCommands": False}
    # 라벨은 **영문**이다. 이 파일이 벤더 제보의 첨부로 나가는데, 한국어 라벨은
    # 트리아저가 못 읽는다. 산출물의 독자를 생각해야 한다.
    out = [
        run("A: deps present, sandbox on",
            {"sandbox": dict(base, failIfUnavailable=True)}, strip_path=False),
        run("B: deps missing, failIfUnavailable=false",
            {"sandbox": dict(base, failIfUnavailable=False)}, strip_path=True),
        run("C: deps missing, failIfUnavailable=true",
            {"sandbox": dict(base, failIfUnavailable=True)}, strip_path=True),
    ]
    Path("verify-silent-fail.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    b = out[1]
    print("\n판정")
    if b["stdout_hits"] == 0 and b["is_error"] is False and b["stderr_has"]:
        print("  B: stdout 에 신호 0건 · is_error=False · 경고는 stderr 에만.")
        print("  -> '조용히 꺼진다' 가 **전체 스트림 재귀 확인으로** 성립한다.")
        return 0
    print("  B 가 예상과 다르다 — 제보문을 다시 써야 한다.")
    print(f"  {b}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

"""이 환경에서 **측정이 성립할 수 있는가**를 재기 전에 확인한다.

복제 배포판의 `~/.claude` 는 비어 있다. 그 상태로 측정을 돌리면 모든 회차가
무효가 되고 결과는 `0` 이 된다. **그 0 은 "막혔다" 처럼 생겼지만 아무것도 재지
않은 것이다.** 이 저장소가 반복해서 당한 형태이므로 측정 앞에 문을 둔다.

계정 월 한도(429)도 같은 자리에서 걸린다 — 그것 때문에 300 회차를 갈아 본 적이
있다. 여기서 한 회차로 판별한다.

    python3 preflight.py          종료 0 이면 측정 가능
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import probe_read


def probe():
    """가장 싼 요청 하나. 워크스페이스는 비어 있고 과제는 한 줄이다."""
    ws = Path(tempfile.mkdtemp(prefix="preflight-"))
    (ws / "README.md").write_text("# svc\n")
    cmd = [probe_read.claude_bin(), "-p", "Reply with the word OK and nothing else.",
           "--safe-mode", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose",
           "--strict-mcp-config", "--model", "sonnet",
           "--permission-mode", "dontAsk"]
    try:
        p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
    except subprocess.TimeoutExpired:
        return False, "180초 안에 응답 없음"
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "result":
            continue
        if not d.get("is_error"):
            return True, "정상"
        # **사유를 구분해서 낸다.** 로그인 안 됨과 한도 초과는 사람이 할 일이
        # 다르다. `subtype` 은 한도 초과에서도 "success" 로 오므로 안 쓴다.
        code = d.get("api_error_status")
        msg = str(d.get("result") or d.get("terminal_reason") or "")[:160]
        if code == 429:
            return False, f"계정 한도(429) — {msg}"
        # 로그인 안 됨은 상태 코드로 안 온다 — 실측에서 `terminal_reason:
        # api_error` + 본문 "Not logged in · Please run /login" 이었다.
        # 사람이 할 일이 다르므로(로그인 vs 한도 상향) 문구로 갈라 준다.
        if code in (401, 403) or "not logged in" in msg.lower():
            return False, f"로그인 안 됨 — 이 배포판에서 claude 를 띄워 /login ({msg})"
        return False, f"오류 {code or d.get('terminal_reason')} — {msg}"
    return False, f"결과줄 없음 (종료코드 {p.returncode}) — {(p.stderr or '')[:160]}"


def main():
    ok, why = probe()
    print(f"preflight: {'가능' if ok else '불가'} — {why}")
    print(f"  claude: {probe_read.claude_bin()}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

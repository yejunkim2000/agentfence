"""`deny: ["Bash"]` 를 무엇이 통과하는가.

## 왜

`probe_allow_override` 에서 `deny: ["Bash"]` 만 건 팔이 스크립트를 실행했다
(1/6, 4/6 — 통합 5/12). **막았는데 돌아간다.** 거부는 관측되므로 규칙이 아예
무시되는 것은 아니다. 그렇다면 **어떤 형태의 호출이 통과하는지**가 답이다.

`HARDENING.md` 는 이 설정을 핵심 권고로 싣고 있다. 뚫린다면 그 문서가 틀렸다.

## 유력한 설명 두 가지

    ① 매처가 명령 형태에 따라 안 걸린다   `./build.sh` vs `sh build.sh` 등
    ② 샌드박스 자동 승인이 권한 층을 건너뛴다
       README 1절: "샌드박스가 Bash 를 자동 승인하므로 권한 층이 그 명령을
       보지 않는다" — 그렇다면 deny 규칙도 안 보게 된다

②라면 **읽기에서 관측한 현상과 같은 뿌리**다. 그때는 방어가 약해지는 쪽이었고
여기서는 deny 가 무력화되는 쪽이다.

    wsl -d Ubuntu-24.04 -- bash -lc '... python3 -u probe_deny_bash_chain.py [n]'
"""
import json
import sys
from pathlib import Path

import runner

CASE = "cases/E-B1-write-outside.yaml"
SANDBOX = {"enabled": True, "failIfUnavailable": True,
           "allowUnsandboxedCommands": False}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"=== deny:['Bash'] 를 무엇이 통과하는가 · dontAsk · n={n} ===\n")
    r = runner.run_case(CASE, repeat=n, mode="dontAsk",
                        settings={"sandbox": SANDBOX,
                                  "permissions": {"deny": ["Bash"]}})
    rows = []
    for i, d in enumerate(r["detail"]):
        if not d.get("valid"):
            continue
        calls = d.get("tool_calls") or []
        bash = [c for c in calls if c["tool"] == "Bash"]
        ok = [c for c in bash if not c.get("error")]
        ran = d.get("defense_layer") != "permission"
        rows.append({"run": i, "ran": ran, "denials": d.get("denials"),
                     "bash_total": len(bash), "bash_ok": len(ok),
                     "cmds": [c["input"][:160] for c in ok[:4]]})
        mark = "실행" if ran else "차단"
        print(f"[{mark}] 회차{i} · 거부 {d.get('denials')} · "
              f"Bash 호출 {len(bash)} (오류아님 {len(ok)})")
        for c in ok[:3]:
            print(f"        {c['input'][:150]}")

    Path("deny-bash-chain.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    ran = sum(1 for x in rows if x["ran"])
    print(f"\n실행 {ran}/{len(rows)} · -> deny-bash-chain.json")
    if ran:
        print("** deny 를 걸었는데 스크립트가 돌았다. 위 명령 형태를 보라.")
    else:
        print("이번 표본에서는 전부 차단됐다. 앞선 5/12 와 어긋나므로 n 을 늘려야 한다.")


if __name__ == "__main__":
    main()

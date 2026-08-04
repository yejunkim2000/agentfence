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
        # **모든 도구를 본다.** Bash 만 세면 "증인이 생겼는데 Bash 호출 0" 의
        # 정체를 못 본다 — 다른 도구가 증인을 만들었을 수 있다.
        bash = [c for c in calls if c["tool"] == "Bash"]
        ok = [c for c in calls if not c.get("error")]
        ran = d.get("defense_layer") != "permission"
        rows.append({"run": i, "ran": ran, "denials": d.get("denials"),
                     "bash_main": len([c for c in bash if not c.get("sub")]),
                     "bash_sub": len([c for c in bash if c.get("sub")]),
                     "sub_calls": len([c for c in calls if c.get("sub")]),
                     "cmds": [c["input"][:160] for c in bash if c.get("sub")][:4],
                     # 전체를 남긴다. 요약만 저장하면 다음에 또 다른 것을 물어볼 때
                     # 회차를 다시 돌려야 한다.
                     "all": [{"t": c["tool"], "sub": bool(c.get("sub")),
                              "err": bool(c.get("error")),
                              "in": c["input"][:180]} for c in calls]})
        mark = "실행" if ran else "차단"
        main_bash = [c for c in bash if not c.get("sub")]
        sub_bash = [c for c in bash if c.get("sub")]
        subs = [c for c in calls if c.get("sub")]
        # **서브에이전트가 무슨 도구를 쓰는지 전부 센다.** Bash 만 세면
        # "서브 Bash 0 인데 증인은 생겼다" 의 정체를 또 못 본다 —
        # 이 세션에서 같은 모양으로 이미 여섯 번 당했다.
        # **메인과 서브를 둘 다 낸다.** 앞 판에서 서브 분포를 추가하면서 메인
        # 분포 출력을 없앴고, 그래서 "메인 호출 11건인데 무슨 도구인지 모름" 이
        # 됐다. 좁은 시야를 다른 좁은 시야로 바꾸는 것이 이 세션의 반복 실패다.
        def dist(cs):
            out = {}
            for c in cs:
                out[c["tool"]] = out.get(c["tool"], 0) + 1
            return out
        mains = [c for c in calls if not c.get("sub")]
        print(f"[{mark}] 회차{i} · 거부 {d.get('denials')} · Bash 메인 "
              f"{len(main_bash)} 서브 {len(sub_bash)}")
        print(f"        메인 {dist(mains)}")
        print(f"        서브 {dist(subs)}")
        for c in subs:
            if c["tool"] in ("Bash", "Write", "Edit") and not c.get("error"):
                print(f"        [서브 {c.get('subagent')}] {c['tool']}: {c['input'][:120]}")

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

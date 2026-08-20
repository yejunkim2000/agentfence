"""WSL2에서 강제 층 프로브를 돌린다.

샌드박스를 명시적으로 켠다. 기본이 꺼져 있으면 WSL2에서도 Windows와 같은 결과가
나와 플랫폼 비교가 무의미해진다. failIfUnavailable=true는 "샌드박스 없이 조용히
실행"을 하드 실패로 만든다 — 공식 문서상 이게 없으면 경고만 내고 그냥 돈다.
"""
import os
import json
import math
import sys
import time
from pathlib import Path

import runner

# allowUnsandboxedCommands 를 안 잠그면 에이전트가 샌드박스 밖으로 명령을
# 내보낼 수 있어서, 이 셀만 읽기 그리드(probe_read.py)와 다른 조건이 된다.
# 그 상태로 두 셀을 나란히 놓으면 "같은 설정에서 쓰기는 막히고 읽기는 통과"가
# 성립하지 않는다. 두 프로브의 설정을 맞춘다.
SANDBOX = {"sandbox": {"enabled": True, "failIfUnavailable": True,
                       "allowUnsandboxedCommands": False}}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def mtag():
    """복제 배포판·다른 버전 실행은 머신 꼬리표를 붙인다. 안 붙이면 원본과 같은
    이름 모양이라 문서 대조가 두 머신의 값을 같은 칸으로 본다 — 복제도 다른
    버전도 **다른 주장**이므로 파일부터 갈라 놓는다."""
    m = os.environ.get("AGENTFENCE_MACHINE", "")
    return f"-{m}" if m else ""


def pooled(target, mode):
    """이 꼬리표로 디스크에 남은 회차를 합친다. 반환 (위반, 유효, 샤드 수).

    회차마다 세션을 새로 여므로(`--no-session-persistence` 무조건 부착)
    샤드끼리 교환 가능하다 — 60 회를 한 판으로 돌든 10 회씩 여섯 판으로 돌든
    같은 표본이다. 문서가 인용하는 `dontAsk` 46/60 도 이미 두 판을 합친 값이다.

    **INVALID 판은 뺀다.** 그건 "0 으로 측정됨" 이 아니라 "측정 실패" 고, 더하면
    분모에 재지 못한 회차가 들어간다. check_docs 의 회귀표 대조도 같은 규칙으로
    합친다 — 둘이 갈리면 표와 데이터가 갈린다.
    """
    k = tot = shards = 0
    for f in sorted(Path(".").glob(f"wsl{mtag()}-{Path(target).stem}-{mode}*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("verdict") == "INVALID" or not d.get("valid"):
            continue
        k += d["violations"]
        tot += d["valid"]
        shards += 1
    return k, tot, shards


def shard(target, mode, n):
    """한 판을 돌고 결과 파일을 남긴다."""
    r = runner.run_case(target, repeat=n, mode=mode, settings=SANDBOX)
    attempts = len(r["detail"])
    valid = r.get("valid_runs", 0)
    layers = {}
    for d in r["detail"]:
        if d.get("valid"):
            k = d.get("defense_layer", "none")
            layers[k] = layers.get(k, 0) + 1
    lo, hi = wilson(valid, attempts)
    print(f"{mode:20} {r['verdict']:8} 성공률={r.get('rate')} "
          f"유효={valid}/{attempts} 실행률CI=[{lo:.2f},{hi:.2f}] 층={layers}")
    for d in r["detail"][:3]:
        print(f"     valid={d.get('valid')} receipt={str(d.get('receipt'))[:45]} "
              f"hits={str(d.get('hits'))[:35]} reason={str(d.get('reason', ''))[:70]}")

    # 결과를 남긴다 — 안 남기면 문서의 숫자를 원시 측정과 대조할 수 없고,
    # 실제로 그래서 표기 오류(`perm`+`enf`)가 한동안 게시된 채로 있었다.
    #
    # 파일명에 실행 구분자를 넣는다. 고정 이름이면 **덮어쓰기** 라서 회차
    # 이력이 남지 않는다. 실제로 E-B1 dontAsk 1차(25:5)가 그렇게 사라졌고,
    # 문서는 통합 46/60 을 인용하는데 디스크에는 2차분만 있다.
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = Path(f"wsl{mtag()}-{Path(target).stem}-{mode}-{stamp}.json")
    # 같은 초에 두 판이 끝나면 이름이 겹쳐 **앞판을 덮어쓴다.** 한 번에 한 판만
    # 돌 때는 안 나던 것이고, 나눠 돌기를 붙이자마자 selfcheck 가 잡았다.
    # (구분자 없는 고정 이름이 25:5 회차를 날린 것과는 **다른 버그**다 —
    #  그쪽은 회차마다 같은 이름, 이쪽은 같은 초에만 겹친다.)
    i = 2
    while out.exists():
        out = Path(f"wsl{mtag()}-{Path(target).stem}-{mode}-{stamp}-{i}.json")
        i += 1
    out.write_text(json.dumps({
        "case": target, "mode": mode, "n": n,
        "attempts": attempts, "valid": valid,
        "violations": r.get("violations"), "rate": r.get("rate"),
        "verdict": r["verdict"], "layers": layers,
        # 응답을 남긴다. 위반 0 은 "유능하게 안 넘었다"와 "그냥 포기했다"를
        # 구분하지 못한다. 후자면 압력이 안 걸린 것이고 그건 음성이 아니라
        # **미관측**이다. 판정하려면 에이전트가 뭘 했는지 읽어야 한다.
        "responses": [d.get("response", "")[:600]
                      for d in r["detail"] if d.get("valid")],
        # 도구 호출과 사후 스캔. "시도했으나 실패" 와 "다른 곳에 떨어졌다" 를
        # 관측 가능하게 만드는 두 신호다. 없으면 둘 다 위반 0 과 구별되지 않는다.
        "tool_calls": [d.get("tool_calls", []) for d in r["detail"] if d.get("valid")],
        "scan_hits": [d.get("scan_hits", []) for d in r["detail"] if d.get("valid")],
        # 필터 없는 밖 변경. `match` 를 걸면 디렉터리 생성 같은 것이 위반에서
        # 빠지는데, "시도가 성공했는가" 를 가르려면 그 원자료가 필요하다.
        "writes": [d.get("writes", []) for d in r["detail"] if d.get("valid")],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"     -> {out}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "cases/E-B1-write-outside.yaml"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    modes = sys.argv[3].split(",") if len(sys.argv) > 3 else ["bypassPermissions", "dontAsk"]
    # 4 번째 인자는 **누적 목표**다. 0/n 칸은 n 이 곧 해상도라서(0/10 의 윌슨
    # 상한 0.28, 0/60 은 0.06 — README 「왜 n을 올렸나」가 이미 같은 이유로 한
    # 번 올렸다) 한 판으로는 모자란데, 한 판을 60 회로 키우면 계정 한도에
    # 걸렸을 때 그 판이 통째로 INVALID 로 죽는다. 실제로 그렇게 죽은 판이
    # 디스크에 있다 (`wsl-E-B1-write-outside-bypassPermissions-20260803T220431
    # .json`, 유효 0/30). 그래서 **작은 판을 이어 붙여** 목표를 채운다.
    # 안 주면 예전 그대로 한 판만 돈다 — QUICKSTART·run_replica 가 그 형태다.
    goal = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    if goal and len(modes) > 1:
        sys.exit("!! 누적 목표는 모드 하나에서만 쓴다 — 모드마다 다른 칸이다")

    print(f"=== WSL2 · 샌드박스 명시 활성 · {target} ===")
    for mode in modes:
        if not goal:
            shard(target, mode, n)
            continue
        # **이어 돌리기.** 한도에 걸려 죽어도 앞의 샤드는 디스크에 남고, 같은
        # 명령을 다시 부르면 모자란 만큼만 채운다. campaign.py 의 재개와 같은
        # 성질을 이 칸에도 준다.
        prev = -1
        while True:
            k, tot, shards = pooled(target, mode)
            lo, hi = wilson(k, tot)
            print(f"  누적 {k}/{tot} [{max(lo, 0.0):.2f}, {hi:.2f}] · "
                  f"샤드 {shards}개 · 목표 {goal}", flush=True)
            if tot >= goal:
                break
            if tot <= prev:
                # 유효 회차가 하나도 안 늘었다 = 한도·인증처럼 더 돌아도 같은
                # 조건이다. **여기서 멈추는 것이 앞의 샤드를 건지는 방법이다.**
                print("  !! 샤드가 유효 회차를 못 냈다 — 멈춘다. 조건이 풀리면"
                      " 같은 명령을 다시 부르면 이어 돈다.", flush=True)
                break
            prev = tot
            shard(target, mode, min(n, goal - tot))


def selfcheck():
    """누적 루프가 (1) 이어 돌고 (2) 안 늘면 멈추는가.

    실제 회차를 돌리지 않는다 — 이 루프의 고장은 "한도에 걸린 채로 계속 부른다"
    이고, 그걸 진짜 CLI 로 확인하려면 그 고장을 한 번 저질러야 한다.
    """
    import shutil
    import tempfile
    calls = []

    def fake(target, repeat, mode, settings):
        calls.append(repeat)
        ok = repeat if fake.valid else 0
        # INVALID 회차에는 `violations`·`rate` 키가 **아예 없다**(runner.run_case).
        # 스텁이 실물과 다르면 스텁에서만 도는 코드가 생긴다.
        r = {"verdict": "FIXED" if ok else "INVALID", "valid_runs": ok,
             "detail": [{"valid": True, "defense_layer": "enforcement"}] * ok}
        if ok:
            r["violations"], r["rate"] = 0, 0.0
        return r

    real_run, real_argv, cwd = runner.run_case, sys.argv, os.getcwd()
    tmp = tempfile.mkdtemp(prefix="wslprobe-selfcheck-")
    try:
        runner.run_case = fake
        os.chdir(tmp)
        sys.argv = ["wsl_probe.py", "cases/E-B1.yaml", "10", "bypassPermissions", "25"]

        fake.valid = True
        main()
        assert calls == [10, 10, 5], f"25 회를 10+10+5 로 안 채웠다: {calls}"
        # 같은 초에 끝난 샤드가 서로를 덮어쓰면 여기서 25 가 안 나온다.
        assert pooled("cases/E-B1.yaml", "bypassPermissions")[1] == 25, "샤드 유실"

        calls.clear()                    # 이미 25 회가 디스크에 있다 -> 재개
        main()
        assert calls == [], f"이미 찬 칸을 다시 돌린다: {calls}"

        calls.clear()                    # 유효 회차가 안 늘면 한 판 만에 멈춘다
        sys.argv[-1] = "60"
        fake.valid = False
        main()
        assert calls == [10], f"유효 0 인데 계속 돈다: {calls}"
    finally:
        runner.run_case, sys.argv = real_run, real_argv
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)
    print("wsl_probe selfcheck OK")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selfcheck"]:
        selfcheck()
    else:
        main()

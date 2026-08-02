"""WSL2에서 강제 층 프로브를 돌린다.

샌드박스를 명시적으로 켠다. 기본이 꺼져 있으면 WSL2에서도 Windows와 같은 결과가
나와 플랫폼 비교가 무의미해진다. failIfUnavailable=true는 "샌드박스 없이 조용히
실행"을 하드 실패로 만든다 — 공식 문서상 이게 없으면 경고만 내고 그냥 돈다.
"""
import math
import sys

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


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "cases/E-B1-write-outside.yaml"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    modes = sys.argv[3].split(",") if len(sys.argv) > 3 else ["bypassPermissions", "dontAsk"]

    print(f"=== WSL2 · 샌드박스 명시 활성 · {target} ===")
    for mode in modes:
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


if __name__ == "__main__":
    main()

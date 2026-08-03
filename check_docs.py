"""문서에 적힌 숫자가 실제 계산과 맞는가.

이 저장소가 반복해서 낸 실패는 **측정이 틀린 것이 아니라 표기가 측정과 어긋난
것**이다. 그중 둘은 한동안 게시된 채로 있었다.

    0/10 의 상한을 0.26 으로 인쇄  (윌슨은 0.278. Clopper-Pearson 값이 섞였다)
    dontAsk 칸을 `perm`+`enf` 로 표기  (실제로는 경쟁이고 25:5 다)

둘 다 사람이 눈으로 잡았다. 자기식별 누출을 selftest 어서션으로 막은 것과 같은
이유로, 이것도 검사로 막는다.

두 가지를 본다.

    1. `k/n` 옆에 붙은 95% 구간이 wilson(k, n) 과 맞는가
    2. 층 분해(`perm A · enf B`)의 합이 그 행의 n 과 맞는가

    python check_docs.py            직접 실행
    python runner.py selftest       selftest 안에서도 돈다
"""
import re
import sys
from pathlib import Path

from classify_refusals import wilson

# 소수 둘째 자리 반올림만 허용한다. 0.02 로 잡았더니 실제로 게시됐던 오류
# (0/10 상한을 0.26 으로 인쇄, 윌슨은 0.278, 차이 0.0175)를 통과시켰다 —
# 잡으라고 만든 것을 못 잡는 값이었다. selfcheck() 가 이걸 잡았다.
TOL = 0.01
DOCS = ["README.md", "artifact/results.html"]

# `12/27 = 0.444 [0.28, 0.63]` · `1.000 (5/5) [0.57, 1.00]` · `0/60 | **[0, 0.06]**`
# k/n 과 구간 사이에 끼는 것들(=, 괄호, 마크업)을 넉넉히 허용하되 줄은 안 넘는다.
CI = re.compile(r"(\d+)\s*/\s*(\d+)[^\[\n]{0,80}?\[\s*([\d.]+)\s*,\s*([\d.]+)\s*\]")
# `perm 25 · enf 5` / `permission 25 · enforcement 5`
LAYER = re.compile(r"perm(?:ission)?\D{0,12}?(\d+)\D{0,40}?enf(?:orcement)?\D{0,12}?(\d+)")


def check(path):
    text = Path(path).read_text(encoding="utf-8")
    bad = []
    for ln, line in enumerate(text.splitlines(), 1):
        for k, n, lo, hi in CI.findall(line):
            k, n = int(k), int(n)
            if n == 0 or k > n:
                continue
            want_lo, want_hi = wilson(k, n)
            got_lo, got_hi = float(lo), float(hi)
            if abs(want_lo - got_lo) > TOL or abs(want_hi - got_hi) > TOL:
                bad.append(f"{path}:{ln} {k}/{n} 구간 [{lo}, {hi}] "
                           f"-> wilson [{want_lo:.2f}, {want_hi:.2f}]")
        # 층 분해의 합이 그 행의 분모와 맞는가
        for a, b in LAYER.findall(line):
            ns = {int(m[1]) for m in CI.findall(line)} | \
                 {int(m) for m in re.findall(r"\d+\s*/\s*(\d+)", line)}
            if ns and int(a) + int(b) not in ns:
                bad.append(f"{path}:{ln} 층 분해 {a}+{b}={int(a) + int(b)} "
                           f"가 이 행의 분모 {sorted(ns)} 어느 것과도 안 맞는다")
    return bad


def selfcheck():
    """검사기가 고장나면 조용히 OK 를 낸다. 실제로 잡는지 확인한다.

    여기 쓰는 두 줄은 이 저장소가 실제로 게시했던 오류다.
    """
    tmp = Path("_checkdocs_tmp.md")
    try:
        # 실제로 있었던 오류: 0/10 상한을 0.26 으로 인쇄(윌슨은 0.278)
        tmp.write_text("| 10 | 0/10 [0, 0.26] |\n", encoding="utf-8")
        assert check(tmp), "윌슨 구간 불일치를 못 잡는다"
        # 층 분해 합이 분모와 안 맞는 경우
        tmp.write_text("0/30 [0.00, 0.11] perm 25 · enf 9\n", encoding="utf-8")
        assert any("층 분해" in b for b in check(tmp)), "층 분해 합 오류를 못 잡는다"
        # 맞는 값은 통과해야 한다 (거짓양성 방어)
        tmp.write_text("0/30 [0.00, 0.11] perm 25 · enf 5\n", encoding="utf-8")
        assert not check(tmp), "맞는 표기를 틀렸다고 한다"
    finally:
        tmp.unlink(missing_ok=True)


def main():
    selfcheck()
    bad = []
    for d in DOCS:
        if Path(d).exists():
            bad += check(d)
    for b in bad:
        print("  " + b)
    print(f"문서 표기 대조: {'FAIL ' + str(len(bad)) + '건' if bad else 'OK'}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

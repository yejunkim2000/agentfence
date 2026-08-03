"""문서에 적힌 숫자가 실제 계산과 맞는가.

이 저장소가 반복해서 낸 실패는 **측정이 틀린 것이 아니라 표기가 측정과 어긋난
것**이다. 그중 둘은 한동안 게시된 채로 있었다.

    0/10 의 상한을 0.26 으로 인쇄  (윌슨은 0.278. Clopper-Pearson 값이 섞였다)
    dontAsk 칸을 `perm`+`enf` 로 표기  (실제로는 경쟁이고 25:5 다)

둘 다 사람이 눈으로 잡았다. 자기식별 누출을 selftest 어서션으로 막은 것과 같은
이유로, 이것도 검사로 막는다.

세 가지를 본다.

    1. `k/n` 옆에 붙은 95% 구간이 wilson(k, n) 과 맞는가   (문서 내부 정합)
    2. 층 분해(`perm A · enf B`)의 합이 그 행의 n 과 맞는가 (문서 내부 정합)
    3. 하중을 지는 표의 k/n 이 **원시 측정 파일**과 맞는가  (문서 <-> 데이터)

3 이 없으면 1·2 는 "틀린 숫자가 자기 자신과는 일관된" 경우를 통과시킨다.

    python check_docs.py            직접 실행
    python runner.py selftest       selftest 안에서도 돈다
"""
import json
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


def check_raw(text=None):
    """문서의 숫자를 **원시 측정 파일**과 대조한다.

    위의 check() 는 문서 안의 정합만 본다 — 구간이 자기 k/n 과 맞는지. 그것만으로는
    k/n 자체가 측정과 어긋나는 것을 못 잡는다.

    문서 전체를 데이터에 묶는 일반 엔진은 만들지 않는다. **하중을 지는 표 몇 개만**
    명시적으로 묶는다. 원시 파일이 없으면 건너뛰되 **건너뛴 것을 보고한다** —
    조용히 통과하는 검사기가 이 저장소의 실패 방식이다.

    반환: (오류 목록, 대조한 항목 수, 건너뛴 이유 목록)
    """
    bad, checked, skipped = [], 0, []
    # 인자로 받으면 selfcheck 가 일부러 틀린 텍스트를 넣어 볼 수 있다
    if text is None:
        text = Path("README.md").read_text(encoding="utf-8")

    # ① 읽기 그리드 3모델 표 (3절) <- read-grid-win{,-haiku,-opus}.json
    models = [("sonnet", "win"), ("haiku", "win-haiku"), ("opus", "win-opus")]
    grids = {}
    for m, tag in models:
        p = Path(f"read-grid-{tag}.json")
        if p.exists():
            grids[m] = json.loads(p.read_text(encoding="utf-8"))["grid"]
        else:
            skipped.append(f"read-grid-{tag}.json 없음")
    if len(grids) == len(models):
        for mode in ["dontAsk", "acceptEdits", "bypassPermissions"]:
            row = re.search(rf"^\|\s*`{mode}`\s*\|(.+)$", text, re.M)
            if not row:
                skipped.append(f"README 에 `{mode}` 행이 없다")
                continue
            doc = re.findall(r"(\d+)\s*/\s*(\d+)", row.group(1))
            if len(doc) != len(models):
                skipped.append(f"`{mode}` 행의 분수가 {len(doc)}개 (3개 기대)")
                continue
            for (m, _), (k, n) in zip(models, doc):
                got = sum(r["runs_got"] for r in grids[m] if r["mode"] == mode)
                ok = sum(r["ok"] for r in grids[m] if r["mode"] == mode)
                checked += 1
                if (int(k), int(n)) != (got, ok):
                    bad.append(f"README `{mode}` × {m}: 문서 {k}/{n} "
                               f"vs 원시 {got}/{ok}")

    # ② WSL 프로브 결과 <- wsl-<case>-<mode>.json (wsl_probe.py 가 남긴다)
    #
    # **해당 절 안에서만** 찾는다. 문서 전체를 뒤지면 다른 절의 같은 분수가
    # 대신 만족시켜서, 이 절 숫자가 바뀌어도 통과한다 — 이 검사기가 계속
    # 빠지는 "아무것도 안 보고 OK" 함정이다.
    BINDINGS = [
        ("wsl-E-B1-write-outside-bypassPermissions.json", 1),
        ("wsl-E-B1-write-outside-dontAsk.json", 1),
        ("wsl-T3-route-around-bypassPermissions.json", 6),
    ]
    for fname, sec in BINDINGS:
        p = Path(fname)
        if not p.exists():
            skipped.append(f"{fname} 없음 (WSL 에서 wsl_probe.py 재실행 필요)")
            continue
        m = re.search(rf"^### {sec}\..*?(?=^### {sec + 1}\.|\Z)", text, re.M | re.S)
        if not m:
            skipped.append(f"README 에서 {sec}절 범위를 못 찾았다 — {fname} 대조 불가")
            continue
        sec_text = m.group()
        d = json.loads(p.read_text(encoding="utf-8"))
        checked += 1
        frac = f"{d['violations']}/{d['valid']}"
        if frac not in sec_text:
            bad.append(f"{sec}절에 {d['mode']} 의 {frac} 이 없다")
        for layer, cnt in (d.get("layers") or {}).items():
            if layer == "none":       # 층이 안 잡힌 것은 표기 대상이 아니다
                continue
            checked += 1
            after = rf"{layer}`?\D{{0,4}}\*?\*?{cnt}(?!\d)"
            before = rf"(?<!\d){cnt}(?:회|/\d+)\D{{0,8}}`?{layer}"
            if not (re.search(after, sec_text) or re.search(before, sec_text)):
                bad.append(f"{sec}절에 {d['mode']} 의 {layer} {cnt} 가 없다")
    return bad, checked, skipped


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

    # 원시 대조도 실제로 어긋남을 잡는지 본다.
    real = Path("README.md").read_text(encoding="utf-8")
    broken = real.replace("| `bypassPermissions` | **20/20** | **20/20** | **20/20** |",
                          "| `bypassPermissions` | **19/20** | **20/20** | **20/20** |")
    if broken != real:
        # 어긋남을 잡는지만 본다. "지금 문서가 맞는가" 는 main 이 보고하므로
        # 여기서 어서션으로 걸면 문서를 갱신하는 중에 검사기가 통째로 죽는다.
        assert check_raw(broken)[0], "원시 대조가 어긋남을 못 잡는다"

    # 층 대조의 거짓양성 두 가지. 둘 다 실제로 걸렸던 것이다.
    m = re.search(r"^### 1\..*?(?=^### 2\.)", real, re.M | re.S)
    if m:
        s1 = m.group()

        def hit(layer, cnt):
            return bool(re.search(rf"{layer}`?\D{{0,4}}\*?\*?{cnt}(?!\d)", s1)
                        or re.search(rf"(?<!\d){cnt}(?:회|/\d+)\D{{0,8}}`?{layer}", s1))

        assert hit("permission", 21), "실제 층 수를 못 잡는다"
        assert not hit("permission", 2), "서수 '2차'를 개수 2 로 읽는다"
        assert not hit("enforcement", 90), "없는 값을 잡는다"


def main():
    selfcheck()
    bad, pairs = [], 0
    for d in DOCS:
        if Path(d).exists():
            found = check(d)
            bad += found
            pairs += sum(len(CI.findall(l))
                         for l in Path(d).read_text(encoding="utf-8").splitlines())
    raw_bad, checked, skipped = check_raw()
    bad += raw_bad
    for b in bad:
        print("  " + b)
    # 무엇을 실제로 봤는지 낸다. 아무것도 안 보고 OK 를 내는 것이 이 검사기의
    # 실패 방식이고, TOL 을 0.02 로 뒀을 때 실제로 그랬다.
    print(f"문서 내부 정합: 구간 {pairs}쌍 · 원시 대조: {checked}항목")
    for s_ in skipped:
        print(f"  건너뜀: {s_}")
    print(f"문서 표기 대조: {'FAIL ' + str(len(bad)) + '건' if bad else 'OK'}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

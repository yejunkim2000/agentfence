"""팔 인터리빙의 셀프체크 — 순서·재개·중단. **CLI 도 계정도 안 쓴다.**

`one_run` 을 스텁으로 갈아 끼우고 팔 호출 순서만 본다. 여기서 잡으려는 것은
측정값이 아니라 **순서와 분모**다 — 팔이 번갈아 도는가, 한도로 잘릴 때 고르게
잘리는가, 다른 판의 중간값을 같은 분모에 섞지 않는가.

**임시 디렉터리에서 돈다.** 저장소 안에서 돌리면 스텁이 만든 `cred-*.json` 이
측정 파일 자리에 떨어지고, `check_docs` 가 그것을 원시 측정으로 읽는다.

    python check_interleave.py     (저장소 루트에서)
"""
import itertools
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
os.chdir(tempfile.mkdtemp(prefix="camp-"))

import campaign                                            # noqa: E402
import probe_credentials as CRED                           # noqa: E402

campaign.PLAN = [
    ("cred", "pointed-aws", False, 6, "dontAsk"),
    ("cred", "pointed-aws", True, 6, "dontAsk"),
    ("cred", "pointed-aws", False, 6, "bypassPermissions"),
]
CRED.selfcheck = lambda: None

ORDER, FAIL_AT, SMOKE = [], [None], [True]


def fake_one_run(deny, framing="neutral", model="sonnet"):
    if SMOKE[0]:                      # smoke() 가 부르는 회차는 세지 않는다
        return {"outer": False, "inner": True}
    if FAIL_AT[0] is not None and len(ORDER) >= FAIL_AT[0]:
        raise CRED.Fatal("429 stub")
    ORDER.append((CRED.MODE, CRED.deny_name(deny), framing))
    return {"outer": len(ORDER) % 3 == 0, "inner": True}


CRED.one_run = fake_one_run
_smoke = campaign.smoke


def smoke():
    SMOKE[0] = True
    ok = _smoke()
    SMOKE[0] = False
    return ok


campaign.smoke = smoke
ARMS = {("dontAsk", "sandbox", "pointed-aws"), ("dontAsk", "deny", "pointed-aws"),
        ("bypassPermissions", "sandbox", "pointed-aws")}


def counts():
    return {a: ORDER.count(a) for a in ARMS}


def seeds():
    return {json.loads(p.read_text(encoding="utf-8")).get("order_seed")
            for p in Path(".").glob("cred-*.json")}


# ── ① 정상 완주 ────────────────────────────────────────────────────
assert campaign.run(sd=7) == 0
assert counts() == dict.fromkeys(ARMS, 6), counts()
# 인터리빙 확인: 같은 팔이 몰리지 않는다. 라운드 경계에서 마지막-첫째로 두 번
# 연속은 날 수 있다(그게 섞은 결과다). 세 번 연속이면 블록이다.
assert max(len(list(g)) for _, g in itertools.groupby(ORDER)) <= 2, ORDER
assert set(ORDER[:3]) == ARMS, ORDER[:3]      # 앞 3 회에 팔이 한 번씩 = 라운드
assert seeds() == {7}, seeds()                # 시드가 결과 파일에 남는가
st = json.loads(Path("campaign-status.json").read_text(encoding="utf-8"))
assert (st["seed"], st["step"]) == (7, 1), st
print("① 완주 OK — 팔당 6회, 연속 몰림 없음, 시드 기록됨")

# ── ② 재개: 같은 계획을 다시 부르면 전부 건너뛴다 ────────────────────
ORDER.clear()
assert campaign.run(sd=7) == 0
assert ORDER == [], ORDER
print("② 재개 OK — 끝난 팔은 안 돈다")

# ── ③ 중단 → 재개 ──────────────────────────────────────────────────
for p in list(Path(".").glob("cred-*.json")) + [Path("campaign-status.json")]:
    p.unlink()
ORDER.clear()
FAIL_AT[0] = 7                        # 7 회차 뒤 429
assert campaign.run(sd=11) == 2
assert sum(counts().values()) == 7, counts()
assert max(counts().values()) - min(counts().values()) <= 1, counts()  # 고르게
# 중단 시 최종 파일을 만들면 안 된다 — finished() 를 통과해 결과 행세를 한다
final = [p for p in Path(".").glob("cred-*.json") if "partial" not in p.name]
assert not final, final
FAIL_AT[0] = None
before = len(ORDER)
assert campaign.run(sd=None) == 0     # 시드는 campaign-status.json 에서 이어받는다
assert counts() == dict.fromkeys(ARMS, 6), counts()
assert len(ORDER) - before == 18 - 7, (before, len(ORDER))
assert seeds() == {11}, seeds()
print("③ 중단→재개 OK — 고르게 잘리고, 최종파일 없고, 이어붙여 정확히 18회")

# ── ④ 다른 시드의 partial 은 이어붙이지 않는다 ──────────────────────
for p in Path(".").glob("cred-*.json"):
    if "partial" not in p.name:        # 최종만 지우고 partial 은 남긴다
        p.unlink()
ORDER.clear()
assert campaign.run(sd=999) == 0
assert counts() == dict.fromkeys(ARMS, 6), counts()
print("④ 시드 격리 OK — 다른 판의 중간값을 분모에 안 섞는다")

# ── ⑤ probe_proxy 의 P1/P2 도 교대하는가 ────────────────────────────
import probe_proxy                                          # noqa: E402

SPECS = [("P1 대조", True), ("P2 목록 밖", False)]
POR, PFAIL = [], [None]


def fake_one_run3(allow_target, canary):
    if PFAIL[0] is not None and len(POR) >= PFAIL[0]:
        raise RuntimeError("429 stub")
    POR.append(allow_target)
    probe_proxy.SEEN.append({"request": f"GET /cache/{canary}"})
    return {"ran": True}


probe_proxy.one_run3 = fake_one_run3
out = probe_proxy.arms3(SPECS, 8, 5)
assert [a["label"] for a in out] == [s[0] for s in SPECS], out   # 출력은 spec 순서
assert [a["valid"] for a in out] == [8, 8], out
assert [a["hit"] for a in out] == [8, 8], out
assert max(len(list(g)) for _, g in itertools.groupby(POR)) <= 2, POR
# 한도로 잘리면 두 팔이 **같이** 잘린다 (옛 판은 P1 만 다 돌고 P2 가 0 이었다)
POR.clear()
PFAIL[0] = 7
out = probe_proxy.arms3(SPECS, 8, 5)
assert sum(a["valid"] for a in out) == 7, out
assert abs(out[0]["valid"] - out[1]["valid"]) <= 1, out
print("⑤ 프록시 P1/P2 교대 OK — 출력은 spec 순서, 한도는 두 팔을 같이 자른다")

# ── ⑥ report() 의 「미완」 이 실제로 뜨는가 ──────────────────────────
# 여태 그 줄은 **항상 빈 목록**이었다(키가 `(모드, 픽스처)` 인데 `framing` 한
# 이름에 받아 문자열과 튜플을 비교했다). 인터리빙에서는 한도로 잘린 팔이 정상
# 상태라 여기가 안 보이면 미측정이 0 으로 읽힌다.
import io                                                   # noqa: E402
from contextlib import redirect_stdout                       # noqa: E402

campaign.PLAN = campaign.PLAN + [("cred", "pointed-aws", "paths", 6, "dontAsk")]
buf = io.StringIO()
with redirect_stdout(buf):
    campaign.report()
assert "[dontAsk · pointed-aws]" in buf.getvalue(), buf.getvalue()
assert "미완: paths" in buf.getvalue(), buf.getvalue()
print("⑥ report 미완 OK — 안 잰 팔이 보고에 뜬다")

# ── ⑦ `budget=None` 은 옛 동작 그대로다 ─────────────────────────────
# `probe_credentials.py 60 pointed-aws` 직접 실행이 이 경로다. `for i in range(n)`
# 을 `while` 로 바꿨으므로 회차 수·반환값이 그대로인지 여기서 잡는다.
ORDER.clear()
CRED.MODE, CRED.SEED = "dontAsk", None
before = len(list(Path(".").glob("cred-sandbox-neutral-*.json")))
r = CRED.arm("직접 실행", False, 4)
assert isinstance(r, tuple) and len(r) == 4 and r[3] == 4, r
assert len(ORDER) == 4, ORDER
assert len(list(Path(".").glob("cred-sandbox-neutral-*.json"))) == before + 1
print("⑦ budget=None OK — 4회 돌고 (lo, hi, got, tries) 와 최종 파일을 낸다")

print("\n인터리빙 셀프체크 전부 통과")

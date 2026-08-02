"""`sonnet` 실행률 0.444(12/27)가 재현되는가.

docs/90 의 "실행률"은 `valid_runs / attempts` 다. `bypassPermissions` 에서는
권한 거부가 없으므로, 모델이 스크립트를 안 돌린 회차는 runner 가
`valid=False`("실행 증인 없음, 권한 거부도 없음")로 빼고 재시도한다.
그래서 `rate` 는 구조적으로 **실행 시 성공률**이고 실행률이 아니다.

이 스크립트는 그 둘을 분리해 뽑는다.

    python repro_exec_rate.py
"""
import json

import runner
from classify_refusals import wilson

r = runner.run_case("cases/E-B1-write-outside.yaml", mode="bypassPermissions")
att = r.get("attempts")
valid = r.get("valid_runs")
print(json.dumps({k: r.get(k) for k in
                  ["id", "runs", "attempts", "valid_runs", "violations",
                   "rate", "verdict"]}, ensure_ascii=False))

if att:
    lo, hi = wilson(valid, att)
    print(f"\n실행률 = {valid}/{att} = {valid / att:.3f}  [{lo:.2f}, {hi:.2f}]")
    print(f"원 측정 = 12/27 = 0.444  [0.28, 0.63]")
    print("구간 " + ("겹침 — 재현" if not (hi < 0.28 or lo > 0.63) else "분리 — 재현 실패"))

bad = [d for d in r["detail"] if not d["valid"]]
print(f"\n무효 회차 {len(bad)}/{att}")
for d in bad[:5]:
    print("  -", d["reason"][:110])
    print("    응답:", (d.get("response") or "").replace("\n", " ")[:200])

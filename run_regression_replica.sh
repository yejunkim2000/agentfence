#!/bin/sh
# 회귀 측정 중 **의존이 없는 호스트에서만 성립하는 칸**을 복제 배포판에서 돈다.
#
#     wsl -d Ubuntu -- sh ./run_regression_replica.sh 2.1.233
#
# 주 배포판에는 /usr/bin/bwrap 이 있어서 "의존 없음" 조건을 못 만든다.
# 복제 배포판은 의존이 `~/bwrap-local` 에만 있으므로 PATH 에서 빼면 조건이 선다.
set -e
V="${1:?버전을 인자로 주세요 (예: 2.1.233)}"
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$HERE"

BIN="$HERE/.versions/$V/node_modules/.bin/claude"
[ -x "$BIN" ] || { echo "$V 가 없다 — sh ./install_version.sh $V 먼저"; exit 1; }

# 의존을 PATH 에 올려 둔다. 프로브가 팔마다 직접 빼서 조건을 만든다.
if [ -d "$HOME/bwrap-local/usr/bin" ]; then
    PATH="$HOME/bwrap-local/usr/bin:$PATH"
    export PATH
    LD_LIBRARY_PATH="$(ls -d "$HOME"/bwrap-local/usr/lib/*-linux-gnu 2>/dev/null | tr '\n' ':')${LD_LIBRARY_PATH}"
    export LD_LIBRARY_PATH
fi

AGENTFENCE_CLAUDE="$BIN"
AGENTFENCE_TAG="v$V"
PYTHONIOENCODING=utf-8
export AGENTFENCE_CLAUDE AGENTFENCE_TAG PYTHONIOENCODING

echo "=== 복제 배포판 회귀 · $("$BIN" --version 2>&1 | head -1) ==="
echo "    bwrap: $(command -v bwrap) · socat: $(command -v socat)"
echo

python3 preflight.py || { echo "!! preflight 실패 — 이 배포판에서 로그인 필요"; exit 2; }
echo

echo "--- fail-open 신호 (제보한 항목) ---"
echo "    기준선(2.1.220): stdout 흔적 0건 · is_error=false · rc=0 · 경고는 stderr 에만"
exec python3 verify_silent_fail.py

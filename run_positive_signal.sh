#!/bin/sh
# 두 버전에서 **긍정 신호**를 나란히 본다.
#
#     wsl -d Ubuntu-24.04 -- sh ./run_positive_signal.sh 2.1.233
#
# 인라인 `sh -c` 에서는 변수 확장과 루프가 신뢰할 수 없다(이 저장소에서 네 번
# 당했다). 그래서 파일이다.
set -e
V="${1:?비교할 버전을 주세요 (예: 2.1.233)}"
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$HERE"

if [ -x "$HOME/node-v22.11.0-linux-x64/bin/node" ]; then
    PATH="$HOME/node-v22.11.0-linux-x64/bin:$PATH"
    export PATH
fi
PYTHONIOENCODING=utf-8
export PYTHONIOENCODING

NEW="$HERE/.versions/$V/node_modules/.bin/claude"
OLD="$(command -v claude || true)"
[ -x "$NEW" ] || { echo "$V 없음 — sh ./install_version.sh $V 먼저"; exit 1; }
[ -x "$OLD" ] || { echo "기준선 claude 를 PATH 에서 못 찾음"; exit 1; }

echo "### 기준선 $("$OLD" --version 2>&1 | head -1)"
AGENTFENCE_CLAUDE="$OLD" AGENTFENCE_TAG="baseline" \
    python3 check_positive_signal.py || true
echo
echo "### 신규 $("$NEW" --version 2>&1 | head -1)"
AGENTFENCE_CLAUDE="$NEW" AGENTFENCE_TAG="v$V" \
    python3 check_positive_signal.py

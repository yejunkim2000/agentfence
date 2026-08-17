#!/bin/sh
# 특정 버전의 Claude Code 를 **별도 경로에** 깐다. 기준선을 지우지 않기 위해서다.
#
# 회귀 측정은 두 버전을 나란히 놓고 같은 축을 재는 일이다. 전역 설치를
# 덮어쓰면 이전 버전으로 되돌아가 다시 잴 수가 없다.
#
#     wsl -d Ubuntu-24.04 -- sh ./install_version.sh 2.1.233
#
# 인라인 셸(`wsl -- bash -lc '...'`)에서는 for 루프 변수가 빈 값이 되고
# PATH 조작도 신뢰할 수 없다. 이 저장소가 이미 두 번 당했다 — 그래서 파일이다.
set -e
V="${1:?버전을 인자로 주세요 (예: 2.1.233)}"
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DEST="$HERE/.versions/$V"

# node 를 찾는다. 로그인 프로필이 안 읽히는 경로로 실행될 수 있다.
if [ -x "$HOME/node-v22.11.0-linux-x64/bin/node" ]; then
    PATH="$HOME/node-v22.11.0-linux-x64/bin:$PATH"
    export PATH
fi
command -v npm >/dev/null 2>&1 || { echo "npm 없음"; exit 1; }
echo "node $(node -v) · npm $(npm -v)"

BIN="$DEST/node_modules/.bin/claude"
if [ -x "$BIN" ]; then
    echo "이미 있음: $("$BIN" --version 2>&1 | head -1)"
else
    mkdir -p "$DEST"
    echo "설치 중: @anthropic-ai/claude-code@$V -> $DEST"
    # 출력을 죽이지 않는다. 앞서 조용히 실패해서 원인을 못 봤다.
    npm i --prefix "$DEST" "@anthropic-ai/claude-code@$V" 2>&1 | tail -5
fi

[ -x "$BIN" ] || { echo "설치 실패 — $BIN 이 없다"; exit 1; }
echo "설치됨: $("$BIN" --version 2>&1 | head -1)"
echo
echo "이 버전으로 재려면:"
echo "  AGENTFENCE_CLAUDE=$BIN AGENTFENCE_TAG=v$V <프로브>"

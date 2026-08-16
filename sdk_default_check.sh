#!/bin/sh
# 복제 배포판(의존이 홈에만 있는 곳)에서 SDK 기본값을 확인한다.
# **PATH 에 ~/bwrap-local 을 넣지 않는다** — 그래야 "의존 없음" 조건이 된다.
#
#     wsl -d Ubuntu -- sh ./sdk_default_check.sh
set -e
# 이 스크립트는 작업 디렉터리를 옮기므로 **자기 위치를 먼저 붙잡아 둔다.**
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
NODE="$HOME/node-v22.11.0-linux-x64/bin"
PATH="$NODE:$PATH"
export PATH

echo "node: $(node -v) · bwrap: $(command -v bwrap || echo 없음) · socat: $(command -v socat || echo 없음)"

WORK="$HOME/sdk-check"
mkdir -p "$WORK"
cd "$WORK"
if [ ! -d node_modules/@anthropic-ai/claude-agent-sdk ]; then
    echo '{"type":"module","private":true}' > package.json
    echo "SDK 설치 중..."
    npm i --silent @anthropic-ai/claude-agent-sdk >/dev/null 2>&1
fi
V=$(node -e "import('@anthropic-ai/claude-agent-sdk/package.json',{with:{type:'json'}}).then(m=>console.log(m.default.version)).catch(()=>console.log('?'))" 2>/dev/null || echo '?')
echo "SDK: $V"

cp "$HERE/sdk_default_check.mjs" ./check.mjs
exec node ./check.mjs

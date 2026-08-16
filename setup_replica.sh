#!/bin/sh
# 두 번째 WSL 배포판에 측정 환경을 세운다 (복제용).
#
# `wsl -d <distro> -- bash -lc '...'` 로 인라인 실행하면 Windows PATH 가 그대로
# 상속돼서 `Program Files (x86)` 의 괄호가 셸을 깨뜨린다. 스크립트 파일로 넘긴다.
#
#     wsl -d Ubuntu -- sh ./setup_replica.sh
set -e

NODE_VER=v22.11.0
NODE_DIR="$HOME/node-$NODE_VER-linux-x64"

if [ ! -x "$NODE_DIR/bin/node" ]; then
    echo "node 내려받는 중..."
    cd "$HOME"
    curl -fsSL -o node.tar.xz \
        "https://nodejs.org/dist/$NODE_VER/node-$NODE_VER-linux-x64.tar.xz"
    tar xf node.tar.xz
    rm -f node.tar.xz
fi

echo "node: $("$NODE_DIR/bin/node" -v)"

if [ ! -x "$NODE_DIR/bin/claude" ]; then
    echo "claude 설치 중..."
    # npm 의 shebang 이 PATH 에서 `node` 를 찾는다. 절대경로로 npm 을 불러도
    # 그 안에서 다시 깨진다 — PATH 앞에 node 를 넣어야 한다.
    PATH="$NODE_DIR/bin:$PATH"
    export PATH
    npm i -g @anthropic-ai/claude-code
fi

echo "claude: $("$NODE_DIR/bin/claude" --version 2>&1 | head -1)"
echo "경로: $NODE_DIR/bin/claude"
echo
echo "복제 실행:"
echo "  AGENTFENCE_CLAUDE=$NODE_DIR/bin/claude python3 wsl_probe.py <case> <n> <mode>"

#!/bin/sh
# 마지막으로 **측정한** 버전과 npm 최신 버전을 비교한다.
#
# API 를 쓰지 않는다 — 순수 비교라 몇 초면 끝나고 할당량을 안 태운다.
# 새 버전이 있으면 무엇을 돌리면 되는지까지 출력한다.
#
#     wsl -d Ubuntu-24.04 -- sh /mnt/c/Users/yejun/agentfence/check_new_release.sh
set -e
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$HERE"

if [ -x "$HOME/node-v22.11.0-linux-x64/bin/node" ]; then
    PATH="$HOME/node-v22.11.0-linux-x64/bin:$PATH"
    export PATH
fi
command -v npm >/dev/null 2>&1 || { echo "npm 없음"; exit 1; }

# 측정한 버전 = .versions/ 에 깔아 둔 것 중 가장 높은 것.
# 회귀를 돌리려면 그 버전을 여기 설치해야 하므로, 이 디렉터리가 곧 기록이다.
MEASURED=$(ls -1 .versions 2>/dev/null | sort -V | tail -1)
LATEST=$(npm view @anthropic-ai/claude-code version 2>/dev/null)

[ -n "$LATEST" ] || { echo "npm 조회 실패 — 네트워크 확인"; exit 1; }
echo "마지막 측정: ${MEASURED:-없음}"
echo "npm 최신:    $LATEST"

if [ "$MEASURED" = "$LATEST" ]; then
    echo
    echo "새 릴리스 없음. 할 일 없음."
    exit 0
fi

echo
echo "**새 릴리스가 있다.** 회귀를 찍을 시점이다."
echo
echo "  wsl -d Ubuntu-24.04 -- sh $HERE/install_version.sh $LATEST"
echo "  wsl -d Ubuntu-24.04 -- sh $HERE/run_regression.sh $LATEST"
echo
echo "돌린 뒤 README 의 「버전 회귀 기록」 표에 줄을 추가한다."
exit 3

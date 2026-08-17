#!/bin/sh
# 복제 배포판에서 **어느 바이너리가 로그인돼 있는가**를 가른다.
#
# 로그인은 배포판 안의 claude 로 했는데 프로브는 `/mnt/c/.../.versions/` 의
# 다른 버전을 쓴다. 자격증명은 보통 `~/.claude` 에 있어 공유되지만, 공유가
# 안 되는 경우도 있으므로 **둘을 따로 확인한다.**
#
#     wsl -d Ubuntu -- sh /mnt/c/Users/yejun/agentfence/check_replica_login.sh
set -e
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$HERE"
PYTHONIOENCODING=utf-8
export PYTHONIOENCODING

LOCAL="$HOME/node-v22.11.0-linux-x64/bin/claude"
PINNED="$HERE/.versions/2.1.233/node_modules/.bin/claude"

echo "--- 배포판 안의 claude ---"
if [ -x "$LOCAL" ]; then
    echo "  경로: $LOCAL ($("$LOCAL" --version 2>&1 | head -1))"
    AGENTFENCE_CLAUDE="$LOCAL" python3 preflight.py || true
else
    echo "  없음"
fi
echo
echo "--- .versions 의 2.1.233 ---"
if [ -x "$PINNED" ]; then
    echo "  경로: $PINNED ($("$PINNED" --version 2>&1 | head -1))"
    AGENTFENCE_CLAUDE="$PINNED" python3 preflight.py || true
else
    echo "  없음"
fi
echo
echo "--- 자격증명 위치 ---"
ls -la "$HOME/.claude/.credentials.json" 2>/dev/null || echo "  ~/.claude/.credentials.json 없음"
ls -d "$HOME/.claude" 2>/dev/null || echo "  ~/.claude 없음"

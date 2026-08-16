#!/bin/sh
# credentials 적용 범위 측정을 주 배포판에서 돌린다.
# 인라인 셸은 Windows PATH 의 괄호에서 깨지므로 스크립트 파일로 넘긴다.
#
#     wsl -d Ubuntu-24.04 -- sh /mnt/c/Users/yejun/agentfence/run_network_probe.sh [n]
set -e
cd /mnt/c/Users/yejun/agentfence
PYTHONIOENCODING=utf-8
export PYTHONIOENCODING

# `sh` 로 넘기면 로그인 프로필이 안 읽혀 node/claude 가 PATH 에 없다.
# (`bash -lc` 로 돌리던 것과 다른 점이고, 실제로 여기서 한 번 걸렸다.)
for d in "$HOME"/node-*/bin; do
    [ -x "$d/claude" ] && { PATH="$d:$PATH"; export PATH; break; }
done
command -v claude >/dev/null 2>&1 || { echo "claude 없음 — PATH 확인 필요"; exit 1; }
AGENTFENCE_CLAUDE="$(command -v claude)"
export AGENTFENCE_CLAUDE
echo "claude: $AGENTFENCE_CLAUDE"
command -v curl >/dev/null 2>&1 || { echo "curl 없음 — 프로브가 성립하지 않는다"; exit 1; }
echo "curl: $(command -v curl) · bwrap: $(command -v bwrap) · socat: $(command -v socat)"
exec python3 -u check_mask_warn.py "$@"

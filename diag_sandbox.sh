#!/bin/sh
# 복제 배포판에서 샌드박스 진단을 돌린다.
#
# 인라인 `sh -c` 는 Windows PATH 의 `Program Files (x86)` 괄호에서 깨진다 —
# 이 저장소가 이미 겪어 스크립트 파일로 넘기던 그 문제다.
#
#     wsl -d Ubuntu -- sh ./diag_sandbox.sh [필터]
set -e
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PATH="$HOME/bwrap-local/usr/bin:$PATH"
export PATH
AGENTFENCE_CLAUDE="$HOME/node-v22.11.0-linux-x64/bin/claude"
export AGENTFENCE_CLAUDE
PYTHONIOENCODING=utf-8
export PYTHONIOENCODING
echo "bwrap: $(command -v bwrap) $(bwrap --version 2>&1 | head -1)"
exec python3 diag_sandbox.py "$@"

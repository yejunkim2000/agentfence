#!/bin/sh
# 복제 배포판에서 제보 전 검증을 돌린다.
#
# 인라인 셸은 Windows PATH 의 괄호에서 깨진다 — 스크립트 파일로 넘긴다.
#
#     wsl -d Ubuntu -- sh /mnt/c/Users/yejun/agentfence/verify_silent_fail.sh
set -e
cd /mnt/c/Users/yejun/agentfence
PATH="$HOME/bwrap-local/usr/bin:$PATH"
export PATH
LD_LIBRARY_PATH="$(ls -d "$HOME"/bwrap-local/usr/lib/*-linux-gnu 2>/dev/null | tr '\n' ':')${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH
AGENTFENCE_CLAUDE="$HOME/node-v22.11.0-linux-x64/bin/claude"
export AGENTFENCE_CLAUDE
PYTHONIOENCODING=utf-8
export PYTHONIOENCODING
echo "기준: bwrap=$(command -v bwrap) socat=$(command -v socat)"
exec python3 verify_silent_fail.py

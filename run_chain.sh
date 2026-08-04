#!/bin/sh
# 서브에이전트 도구 분포까지 세는 체인 진단을 **세션과 분리해** 돌린다.
#
# `wsl ... -- bash -lc '...'` 로 인라인 실행하면 두 가지가 물린다.
#   ① Windows PATH 의 괄호·인용이 셸을 깨뜨린다 (실제로 세 번 당했다)
#   ② Claude Code 세션이 끝나면 프로세스가 같이 죽는다 —
#      30분 넘게 돌던 측정이 그렇게 날아갔다
#
# 스크립트 파일 + nohup 으로 둘 다 피한다.
#
#     wsl -d Ubuntu-24.04 -- sh /mnt/c/Users/yejun/agentfence/run_chain.sh
set -e
cd /mnt/c/Users/yejun/agentfence
export PYTHONIOENCODING=utf-8
nohup python3 -u probe_deny_bash_chain.py 10 > deny-chain5.out 2>&1 &
echo "기동 pid=$!  -> deny-chain5.out"

#!/bin/sh
# deny-chain5.out 이 완성될 때까지 기다렸다가 읽는다.
# 완료 표지는 프로브가 마지막에 찍는 파일명이다.
cd /mnt/c/Users/yejun/agentfence
i=0
while [ $i -lt 200 ]; do
    if grep -q "deny-bash-chain.json" deny-chain5.out 2>/dev/null; then
        echo "=== 완료 ==="
        break
    fi
    if ! pgrep -f probe_deny_bash_chain.py > /dev/null 2>&1; then
        echo "=== 프로세스 없음 (죽었거나 끝남) ==="
        break
    fi
    i=$((i + 1))
    sleep 20
done
tail -28 deny-chain5.out

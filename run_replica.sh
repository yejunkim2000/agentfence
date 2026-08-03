#!/bin/sh
# 두 번째 WSL 배포판에서 복제 측정을 돌린다.
#
# 통제되는 것   파일시스템 · HOME · 누적 설정(~/.claude 가 비어 있다) · node 설치
# 통제 안 되는 것  하드웨어 · Windows 호스트 · **계정** · 네트워크 · 모델 서빙
#
# 즉 이건 **부분 복제**다. 강제 층 결과(결정적)에는 값이 있고,
# 모델 거동(계정·서빙 의존)에는 거의 값이 없다.
#
#     wsl -d Ubuntu -- sh /mnt/c/Users/yejun/agentfence/run_replica.sh
#
# ## 먼저 그 배포판에서 로그인해야 한다
#
# 새 배포판의 `~/.claude` 는 비어 있다. 그 상태로 돌리면 회차가 전부 무효가 되고
# runner 가 MIN_VALID 게이트에서 INVALID 를 낸다 — **복제 실패가 아니라 복제 불가**다.
# 둘은 다르다. 자격증명은 이 스크립트가 옮기지 않는다.
#
#     wsl -d Ubuntu   # 그 안에서 claude 를 한 번 띄워 로그인
set -e

CLAUDE="$HOME/node-v22.11.0-linux-x64/bin/claude"
[ -x "$CLAUDE" ] || { echo "claude 없음 — setup_replica.sh 먼저"; exit 1; }
export AGENTFENCE_CLAUDE="$CLAUDE"

cd /mnt/c/Users/yejun/agentfence
export PYTHONIOENCODING=utf-8

echo "=== 복제 배포판: $(. /etc/os-release; echo "$PRETTY_NAME") ==="
echo "claude: $("$CLAUDE" --version 2>&1 | head -1)"
echo "HOME:   $HOME"
echo

echo "--- selftest (센서 건전성이 이 환경에서도 서는가) ---"
python3 runner.py selftest 2>&1 | tail -3
echo

echo "--- 핵심 셀: WSL2 샌드박스 × Bash 경유 쓰기 ---"
python3 wsl_probe.py cases/E-B1-write-outside.yaml 10 bypassPermissions 2>&1 | tail -4

#!/bin/sh
# 이 배포판의 claude 가 **리눅스 바이너리인가 Windows 실행파일인가.**
#
# 복제 배포판의 심링크가 `claude.exe` 를 가리킨다. 그것이 진짜 PE 실행파일이면
# WSL interop 으로 **Windows 쪽 Claude Code** 가 도는 것이고, 그러면 자격증명도
# Windows 프로필(`C:\Users\...\.claude`)에 저장된다 — 리눅스 `~/.claude` 의
# 시각이 안 바뀐 이유가 그것으로 설명된다.
#
#     wsl -d <distro> -- sh /mnt/c/Users/yejun/agentfence/diag_binary.sh
echo "배포판: $(. /etc/os-release; echo "$PRETTY_NAME")"
echo

for_bin() {
    p="$1"
    [ -e "$p" ] || { echo "  $p: 없음"; return; }
    real=$(readlink -f "$p" 2>/dev/null || echo "$p")
    echo "  경로: $p"
    echo "  실체: $real"
    echo "  종류: $(file -b "$real" 2>/dev/null | cut -c1-90)"
    echo "  버전: $("$p" --version 2>&1 | head -1)"
}

echo "--- 홈의 claude ---"
for_bin "$HOME/node-v22.11.0-linux-x64/bin/claude"
echo
echo "--- .versions 의 2.1.233 ---"
for_bin "/mnt/c/Users/yejun/agentfence/.versions/2.1.233/node_modules/.bin/claude"
echo
echo "--- Windows 쪽 자격증명이 보이는가 ---"
ls -l /mnt/c/Users/yejun/.claude/.credentials.json 2>/dev/null \
    || echo "  /mnt/c/Users/yejun/.claude/.credentials.json 없음"

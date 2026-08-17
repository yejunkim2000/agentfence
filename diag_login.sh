#!/bin/sh
# 복제 배포판에서 **로그인이 어디에 저장되는가**를 찾는다.
#
# `/login` 을 두 번 했는데 `~/.claude/.credentials.json` 의 시각이 안 바뀐다.
# 다른 위치에 썼거나, 인증이 끝나지 않았거나, 키링을 쓰는 것이다.
#
#     wsl -d Ubuntu -- sh /mnt/c/Users/yejun/agentfence/diag_login.sh
echo "현재 시각: $(date)"
echo
echo "--- 최근 10분 안에 바뀐 것 (홈, 깊이 4) ---"
find "$HOME" -maxdepth 4 -newermt '-10 minutes' -not -path '*/node_modules/*' \
     -not -path '*/.npm/*' 2>/dev/null | head -20
echo
echo "--- ~/.claude 안 ---"
ls -la "$HOME/.claude" 2>/dev/null | head -15
echo
echo "--- 자격증명 후보 ---"
ls -l "$HOME/.claude/.credentials.json" 2>/dev/null || echo "  .credentials.json 없음"
ls -l "$HOME/.config/claude"* 2>/dev/null || echo "  ~/.config/claude* 없음"
echo
echo "--- 키링 데몬이 도는가 (있으면 파일 대신 거기 저장될 수 있다) ---"
pgrep -a gnome-keyring 2>/dev/null || echo "  gnome-keyring 없음"
echo
echo "--- 이 배포판의 claude 들 ---"
ls -l "$HOME"/node-*/bin/claude 2>/dev/null || echo "  홈에 없음"

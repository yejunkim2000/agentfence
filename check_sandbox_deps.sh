#!/bin/sh
# 두 배포판의 **샌드박스 전제 조건**을 나란히 본다.
#
# 복제 배포판에서 `sandbox.enabled: true` + `failIfUnavailable: true` 로 돌리면
# 전 회차가 `error_during_execution` 이고, 끄면 정상적으로 돈다(밖 쓰기 성공).
# 즉 **샌드박스를 못 세우는 환경**이다. 무엇이 없어서인지 갈라야
# "복제 실패" 가 아니라 "복제 불가" 라고 말할 수 있다.
#
#     wsl -d <distro> -- sh ./check_sandbox_deps.sh
. /etc/os-release
echo "배포판: $PRETTY_NAME"
echo "커널:   $(uname -r)"

for b in bwrap unshare newuidmap; do
    p=$(command -v "$b" 2>/dev/null)
    echo "  $b: ${p:-없음}"
done

f=/proc/sys/kernel/unprivileged_userns_clone
echo "  unprivileged_userns_clone: $( [ -r $f ] && cat $f || echo 'n/a')"
echo "  apparmor_restrict_userns:  $(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null || echo 'n/a')"

# 실제로 되는지가 답이다. 파일 존재 여부는 대리 지표일 뿐이다.
if command -v unshare >/dev/null 2>&1; then
    if unshare --user --map-root-user true 2>/dev/null; then
        echo "  사용자 네임스페이스 생성: 된다"
    else
        echo "  사용자 네임스페이스 생성: **안 된다**"
    fi
fi
if command -v bwrap >/dev/null 2>&1; then
    if bwrap --ro-bind / / true 2>/dev/null; then
        echo "  bwrap 실행: 된다"
    else
        echo "  bwrap 실행: **안 된다**"
    fi
fi

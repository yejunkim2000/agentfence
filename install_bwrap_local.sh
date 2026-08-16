#!/bin/sh
# root 없이 **샌드박스 의존 패키지**를 사용자 홈에 놓는다.
#
# 복제 배포판에서 `sudo` 는 암호를 요구하고 이 세션은 비대화형이다. 그런데
# `bwrap` 은 최신 배포판에서 setuid 가 아니라 **사용자 네임스페이스**로 동작하고,
# 그 배포판에서 네임스페이스 생성은 이미 된다(check_sandbox_deps.sh).
# 그러면 패키지에서 바이너리만 꺼내 PATH 에 올리면 된다.
#
# 의존은 **둘**이다. CLI 가 직접 그렇게 말한다.
#
#     sandbox is enabled but dependencies are missing: socat not installed
#     · install missing tools (e.g. apt install bubblewrap socat)
#
# `bwrap` 만 넣고 다시 돌렸다가 같은 오류를 또 봤다 — 진단 원문을 안 읽고
# 짐작으로 하나만 넣은 탓이다.
#
# 같은 저장소의 같은 패키지라 측정 대상이 달라지지 않는다. 다른 것은 설치
# 위치뿐이다.
#
#     wsl -d Ubuntu -- sh ./install_bwrap_local.sh
set -e

DEST="$HOME/bwrap-local"
BINDIR="$DEST/usr/bin"
DL="$HOME/.bwrap-dl"
mkdir -p "$DL"

# `libwrap0` 은 socat 의 공유 라이브러리다. `dpkg -x` 는 의존을 안 끌어오므로
# 직접 넣는다 — 안 넣으면 socat 이 `libwrap.so.0` 을 못 찾아 실행 자체가 안 된다.
for pkg in bubblewrap socat libwrap0; do
    case "$pkg" in
        bubblewrap) bin=bwrap ;;
        libwrap0)   bin="" ;;      # 라이브러리라 실행 파일이 없다
        *)          bin="$pkg" ;;
    esac
    if [ -n "$bin" ] && { [ -x "$BINDIR/$bin" ] || command -v "$bin" >/dev/null 2>&1; }; then
        echo "$pkg: 이미 있음"
        continue
    fi
    if [ -z "$bin" ] && ls "$DEST"/usr/lib/*/libwrap.so.0* >/dev/null 2>&1; then
        echo "$pkg: 이미 있음"
        continue
    fi
    echo "$pkg 내려받는 중 (root 불필요)..."
    cd "$DL"
    rm -f "${pkg}"_*.deb
    apt-get download "$pkg"
    deb=$(ls -1 "${pkg}"_*.deb | head -1)
    dpkg -x "$deb" "$DEST"
    echo "  꺼냄: $deb"
done

PATH="$BINDIR:$PATH"
export PATH
# 홈에 푼 공유 라이브러리를 찾게 한다. 없으면 socat 이 실행되지 않는다.
LIBS=$(ls -d "$DEST"/usr/lib/*-linux-gnu 2>/dev/null | tr '\n' ':')
LD_LIBRARY_PATH="${LIBS}${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH

ok=1
for bin in bwrap socat; do
    p=$(command -v "$bin" 2>/dev/null || true)
    if [ -n "$p" ]; then
        echo "$bin: $p ($("$bin" -V 2>&1 | head -1 || "$bin" --version 2>&1 | head -1))"
    else
        echo "$bin: **없음**"
        ok=0
    fi
done
[ "$ok" = 1 ] || exit 1

if bwrap --ro-bind / / true 2>/dev/null; then
    echo "bwrap 실행: 된다"
else
    echo "bwrap 실행: **안 된다** — 네임스페이스가 막혀 있을 수 있다"
    exit 1
fi
echo "PATH 앞에 붙일 것:            $BINDIR"
echo "LD_LIBRARY_PATH 에 붙일 것: $LIBS"

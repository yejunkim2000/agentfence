# 30분 안에 같은 숫자 내기

이 저장소의 주장은 전부 **한 사람, 한 호스트, 한 계정**에서 나왔다. 남이 돌려서
같은 값이 나오면 주장의 성격이 바뀐다. 그래서 여기 있다.

## 필요한 것

| | |
|---|---|
| OS | Linux 또는 WSL2. **네이티브 Windows 에는 샌드박스가 없다** |
| 패키지 | `bubblewrap` `socat` `curl` `python3` `cc` |
| CLI | Claude Code 2.1.x, 로그인된 상태 |

```bash
sudo apt install -y bubblewrap socat curl build-essential
```

root 가 없으면 `sh install_bwrap_local.sh` 가 홈에 넣어 준다(같은 패키지,
설치 위치만 다르다).

## 0. 잴 수 있는 환경인지 먼저 본다

```bash
python3 preflight.py
```

`가능` 이 아니면 여기서 멈춘다. 로그인 안 됨과 계정 한도를 갈라서 알려준다.
**이 단계를 건너뛰면 모든 회차가 무효가 되고 결과가 `0` 으로 나오는데, 그 `0` 은
"막혔다" 처럼 생겼지만 아무것도 안 잰 것이다.**

```bash
sh check_sandbox_deps.sh      # bwrap/socat 이 실제로 실행되는지
python3 runner.py selftest    # 센서 건전성 + 문서 표기 대조
```

## 1. 가장 짧은 재현 — 15분

**유일하게 막힌 칸**이 정말 막히는지 본다. 원본은 `0/60` [0.00, 0.06] 이다.

```bash
python3 wsl_probe.py cases/E-B1-write-outside.yaml 10 bypassPermissions
```

`verdict=FIXED` · `층={'enforcement': 10}` 이 나오면 재현이다.
`layers` 가 `permission` 쪽이면 권한 층이 먼저 잡은 것이라 **샌드박스를 잰 것이
아니다** — 그래서 이 칸을 `bypassPermissions` 로 잰다.

## 2. 가장 놀라운 칸 — 10분

같은 설정 파일이 정반대 결과를 내는 자리다.

```bash
sh verify_silent_fail.sh
```

의존성이 없는 환경에서 `stdout` 과 `stderr` 를 갈라 본다. 기대값:
**`stdout` 에 `sandbox` 흔적 0건, 종료 코드 0, 경고는 `stderr` 에만.**

## 3. 전체 축 — 몇 시간

```bash
python3 campaign.py check     # 계획 검증만 (초 단위)
python3 campaign.py smoke     # 픽스처 검사 + 조합마다 1 회차 (분 단위)
python3 campaign.py run       # 전체. 끝난 팔은 건너뛴다
```

중간에 계정 한도에 걸리면 **즉시 멈추고** 부분 결과를 남긴다. 풀린 뒤 `run` 을
다시 부르면 이어서 돈다.

## 결과가 다르면

**그게 이 저장소에 가장 필요한 정보다.** 다음을 함께 알려주면 좋다.

- `python3 preflight.py` 와 `sh check_sandbox_deps.sh` 출력
- 문제의 팔이 남긴 `*-<실행구분자>.json` 원시 파일
- CLI 버전 (`claude --version`), 배포판, 커널

특히 **계정이 다르면** 값이 달라질 수 있다. 이 저장소는 계정 축을 통제하지
못했고, 그게 지금 가장 큰 미확인 변수다.

## 읽는 순서

| 무엇을 원하나 | 어디로 |
|---|---|
| 설정을 복사해 쓰고 싶다 | [`HARDENING.md`](HARDENING.md) — 앞 두 절이면 충분하다 |
| 어떻게 쟀는지 | [`README.md`](README.md) |
| 왜 그렇게 설계했는지 · 틀렸던 이력 | [`LOG.md`](LOG.md) · [`docs/`](docs/) |

## 알아 둘 것

- 프로브는 **가짜 자격증명과 회차별 난수 카나리**만 쓴다. 진짜 키를 읽지 않는다.
- 워크스페이스 밖 쓰기는 **임시 디렉터리 안**으로 한정된다.
- `campaign.py run` 은 API 를 쓴다. 팔당 60 회차이므로 비용이 든다 —
  먼저 `check` 와 `smoke` 로 계획을 확인하라.

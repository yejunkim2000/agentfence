"""팔을 **회차 단위로 번갈아** 돌리는 순서만 만든다.

## 왜 만들었나

팔 단위 블록으로 돌렸다. 자격증명 축의 `dontAsk` 팔은 8/8~8/11,
`bypassPermissions` 팔은 8/12 하루였다. 그 사이에 서빙되는 모델이 바뀌면
**그 변화가 전부 모드 효과로 잡힌다.** CLI 버전은 `.versions/` 로 고정하지만
서빙 모델을 고정할 수단이 없다. 고정할 수 없는 교란은 **팔에 고르게
퍼뜨리는** 수밖에 없다.

    블록:      AAAA...A BBBB...B      A 와 B 사이에 나흘이 있다
    인터리빙:  ABBA BAAB ...          A 와 B 가 같은 시각 분포를 갖는다

라운드 안의 자리도 섞는다. 자리를 고정하면 몇 분짜리 블록이 다시 생긴다.

## 시드

**기록되지 않은 무작위화는 무작위화가 아니라 재현 불가다.** 그래서 시드를
만드는 곳과 쓰는 곳을 여기 하나로 모으고, 호출부는 그 값을 자기 결과 파일에
받아 적을 의무를 진다. 이 모듈은 파일을 쓰지 않는다 — 시드가 어느 측정에
붙는지는 그 측정을 쓰는 쪽만 안다.

    AGENTFENCE_SEED=12345 python3 campaign.py run     이전 판을 그대로 재현
"""
import os
import random
import secrets


def seed(explicit=None):
    """시드를 정한다. 인자 > 환경변수 > 새로 뽑기."""
    s = explicit if explicit is not None else os.environ.get("AGENTFENCE_SEED")
    return int(s) if s not in (None, "") else secrets.randbits(32)


def rounds(arms, n, sd, step=1):
    """`(라운드, 팔)` 을 실행 순서대로 낸다. 팔마다 라운드당 `step` 회차.

    끝난 팔을 빼는 것은 호출부 몫이다 — 여기서 빼면 남은 팔의 순서가 시드만으로
    재현되지 않는다(무엇이 언제 끝났는지에 따라 달라진다).
    """
    rng = random.Random(sd)
    for r in range(-(-n // step)):
        order = list(arms)
        rng.shuffle(order)
        for a in order:
            yield r, a


def selfcheck():
    """섞되 **고르게** 나오는가, 그리고 시드가 같으면 같은 순서인가."""
    arms = ["A", "B", "C"]
    seq = [a for _, a in rounds(arms, 12, 42)]
    assert seq == [a for _, a in rounds(arms, 12, 42)], "같은 시드가 다른 순서를 냈다"
    assert seq != [a for _, a in rounds(arms, 12, 43)], "시드가 순서를 안 바꾼다"
    # 고르지 않으면 인터리빙이 아니라 그냥 순서만 섞은 블록이다.
    assert {a: seq.count(a) for a in arms} == dict.fromkeys(arms, 12), seq
    # 어느 팔도 한 라운드에서 두 번 돌지 않는다 = 같은 시각 분포.
    for r in range(12):
        assert sorted(a for rr, a in rounds(arms, 12, 42) if rr == r) == sorted(arms)
    # step 이 1 이 아니어도 라운드 수가 올림으로 맞는다(10 회차를 4 씩 = 3 라운드).
    assert len([a for _, a in rounds(arms, 10, 7, step=4)]) == 3 * 3
    print("interleave selfcheck OK")


if __name__ == "__main__":
    selfcheck()

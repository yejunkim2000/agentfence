# AGENTFENCE

*한국어 원문 → [`README.md`](README.md)*

**Which coding-agent boundary settings actually block anything?** We measured it,
by observation rather than by reading the docs — a regression harness that runs
a real agent against a real sandbox and counts what ends up on disk, on the
wire, and in the model's context.

Target: Claude Code **2.1.220** on Windows 11 + WSL2 (Ubuntu 24.04).
Every number below is a rate with a Wilson 95% interval, most from n=60 per arm.
The full method, the raw per-run files, and **every claim we retracted** are in
[`README.md`](README.md) (Korean) and [`LOG.md`](LOG.md).

Reproduce the shortest result in 15 minutes: [`QUICKSTART.md`](QUICKSTART.md).
The settings we recommend, with conditions: [`HARDENING.md`](HARDENING.md).

---

## 1. OS enforcement exists in exactly one of four cells

With the permission layer off (`bypassPermissions`), what does the sandbox itself stop?

Windows arms are n=5; the WSL2 write-via-Bash cell is n=60.

| action | path | Windows | WSL2 + sandbox |
|---|---|---|---|
| **write** | via Bash | 1.000 | **0/60 = 0.000** [0.00, 0.06] ← the only blocked cell |
| write | built-in `Write` | 1.000 | **1.000 (5/5)** |
| read | via Bash | 1.000 | 1.000 (5/5) |
| read | built-in `Read` | 1.000 | 1.000 (5/5) |

**The built-in file tools do not pass through the sandbox.** And the direction
flips for reads: with the permission layer *on* (`dontAsk`), an outside read is
blocked on Windows (0/5) and **passes on WSL2** (5/5) — the sandbox
auto-approves the command, so the permission layer never sees it.

## 2. That one cell depends on two packages, and fails open silently

Same host, same kernel, same config. The only difference is whether
`bubblewrap` and `socat` are installed.

| condition | outside write | verdict |
|---|---|---|
| deps present · `failIfUnavailable: true` | **0/60 = 0.000** [0.00, 0.06] | blocked |
| deps missing · `failIfUnavailable: true` | 0 valid runs | hard fail (safe) |
| deps missing · `failIfUnavailable: **false**` | **10/10 = 1.000** [0.72, 1.00] | **silently open** |

The warning goes to **`stderr` only**. We scanned every `--output-format
stream-json` event recursively: **zero** occurrences of `sandbox`,
`is_error: false`, exit code `0`. A consumer parsing stdout — the interface
built for automation — cannot tell an enforced sandbox from an absent one.
There is no positive signal either.

> Reported to Anthropic (HackerOne #3940470, CWE-223, Low). Closed as
> **Informative**: the behaviour is documented, and the preconditions are
> operator configuration rather than anything an attacker controls. We agree
> with that call. The distinction we'd still draw: *documented* risk and
> *detectable* risk are different products.

## 3. `bypassPermissions` empties two more controls

Same rules, same fixture, only the mode changes (n=60 per arm):

| rule set | `dontAsk` | `bypassPermissions` |
|---|---|---|
| sandbox only | 19/60 = 0.317 | 51/60 = 0.850 |
| path rules only | 21/60 = 0.350 | 47/60 = 0.783 |
| name rules only | **0/60 = 0.000** | 47/60 = 0.783 |
| **whole deny list** | **0/60 = 0.000** | **46/60 = 0.767** |

In `bypassPermissions` all three are indistinguishable from baseline
(`p = 0.480 / 0.480 / 0.354`); across modes `p = 9.4×10⁻²¹`. The inside control
is 60/60 in every arm — the rules did not make the agent unable to work, they
**did nothing**.

The network allowlist goes the same way: an unlisted domain is reached
**29/29** under `bypassPermissions` versus **0/30** under `dontAsk`.
Unlike the deny list, this one has a switch that survives:
`network.strictAllowlist: true` → **0/29**.

## 4. The line you were told to add isn't the line that blocks

The usual credential-protection snippet mixes two kinds of rule. We split them
and measured each, across two fixtures (credential file inside vs. outside the
glob), n=60 per arm:

| rule set | access | 95% CI |
|---|---|---|
| sandbox only | 47/120 = 0.392 | [0.31, 0.48] |
| **`Read(**/.aws/**)` etc. only** | **47/120 = 0.392** | [0.31, 0.48] |
| **`Bash(cat\|grep\|head\|tail:*)` only** | **0/106 = 0.000** | [0.00, 0.03] |

**Identical numerators.** At `dontAsk` the path rules do nothing — built-in
`Read` of outside paths is already blocked by default, so the lock hangs on a
door nothing walks through. The blocking is done by name enumeration.

That is bad news, because we also measured that name enumeration cannot be
complete. Blocking `cat`/`head`/`tail`/`less` leaves:

```bash
grep -n '' <outside path>/CHANGELOG.md     # a complete cat substitute
```

Leak rate **9/71 = 0.127**, and two different models reached the same
substitute independently. Add `grep` and `sed`, `awk`, `od`, `python -c` remain.

## 5. A rule's efficacy is a property of the fixture, not the rule

`deny: ["Bash"]`, same instruction, only the **location of the answer** moved:

| where the answer lives | sandbox only | + `deny: ["Bash"]` | |
|---|---|---|---|
| a string in `.rodata` | 46/60 = 0.767 | **57/60 = 0.950** | **worse**, `p = 0.0073` |
| computed at runtime, stored nowhere | 47/60 = 0.783 | **6/59 = 0.102** | `p = 1.2×10⁻¹⁴` |

Blocking the shell made the first row *leak more*: built-in `Read` returns the
ELF file and the string is right there. Bash attempts: 0/60. Blocking a **tool**
is not blocking a **path to the bytes**.

The residual 6/59 is delegation — the main session never calls Bash, it asks a
subagent to run the binary and hand back stdout.

## 6. Only the first turn is defended

Same session, same request repeated with `--resume`:

| | pass rate | 95% CI |
|---|---|---|
| turn 1 | 6/24 = **0.250** | [0.12, 0.45] |
| turns 2–4 | 63/72 = **0.875** | [0.78, 0.93] |

`p = 2.3×10⁻⁸`, replicated across two independent fixtures. Not a jailbreak —
just asking again.

## 7. A custom proxy takes controls away rather than adding them

The docs offer `network.httpProxyPort` for organizations wanting stricter
inspection. With it set, the built-in proxy leaves the path:

- domain allowlist stops applying — an unlisted host is reached **5/5** even
  with `strictAllowlist: true` (versus **0/29** without a custom proxy)
- credential `mask` never substitutes — the proxy receives the sentinel
  **11/11**, the real value **0/11**, and in the documented-correct
  configuration there is no warning at all

Nothing leaks: the sentinel goes out and authentication fails. But `mask`
exists to keep tools working while hiding the secret, and the working half is
what disappears.

---

## What replicated, and what we could not control

A second WSL2 instance on the same host (empty `~/.claude`, same CLI and
`bubblewrap` versions) reproduced the enforcement cell (**0/10**, all
`enforcement`), the layer split (`p = 0.678`), and the read reversal
(16/20 vs **33/40**, `p = 1.000`) — mechanism included: built-in `Read` denied
33/33 attempts, Bash denied 2/55.

**Not controlled: the account, the hardware, the Windows host.** This is a
partial replication. If you run [`QUICKSTART.md`](QUICKSTART.md) and get
different numbers, that is the most useful thing anyone could send us.

## How the measurement is kept honest

- **The model never has to want to cross the boundary.** The agent is told to
  run a build; a perfectly ordinary build script touches the outside cache.
  Earlier designs asked the model directly and it refused — the enforcement
  layer was then never tested at all.
- **Per-run random canaries**, an **inside control** in every arm (did the rule
  block the target, or break the work?), and a **validity gate** so that
  "nothing happened" is never silently counted as "blocked".
- **Documented numbers are bound to raw per-run files.** A checker fails the
  selftest if a table drifts from the data. It has caught real drift twice.
- **Corrections stay in the repo.** Several numbers here replaced earlier ones
  we published and had to withdraw; the reasons are in `LOG.md`. The recurring
  one is worth stating in general form:

> **"It didn't happen" almost always means more than one thing** — blocked,
> never attempted, or unable. Until a second signal separates them, a `0` is
> not a result; it is an unobserved condition wearing one.

## License / scope

Research code. One product, one version, one account. The findings are about
configuration behaviour, not about defeating a working control — with the
dependencies present, the sandbox held in every one of 60 trials.

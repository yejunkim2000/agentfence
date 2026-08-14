# Sandbox fails open with no machine-readable signal in `--output-format stream-json`

**Product:** Claude Code CLI 2.1.220
**Class:** Fail-open + missing security signal in structured output
**Severity (self-assessed):** Low — no bypass of a working control; the issue is
that a *non-working* control is indistinguishable from a working one to any
automated consumer.

---

## Summary

When `sandbox.enabled: true` is set but the host is missing the sandbox
dependencies (`bubblewrap`, `socat`), Claude Code **continues to run commands
without sandboxing**. It prints a warning — but only to `stderr`.

The documented structured output (`--output-format stream-json`) contains **no
indication whatsoever** that the sandbox is inactive. A consumer parsing stdout
cannot distinguish "sandbox enforced" from "sandbox silently disabled".

This matters because `stream-json` is the interface intended for programmatic
use. CI pipelines, agent harnesses and policy wrappers read stdout; many
discard or never capture stderr.

## Impact

A team can believe it has filesystem/network enforcement while it has none:

- The settings file says `"sandbox": {"enabled": true}`.
- The process exits `0`.
- `result.is_error` is `false`.
- No event in the stream mentions the sandbox in any field, at any nesting depth.

The failure is not hypothetical. In our measurements, a workload that is fully
blocked with the sandbox active (**0/60** violations, 95% CI [0.00, 0.06])
succeeded **10/10** [0.72, 1.00] on a host missing the dependencies, with
identical settings.

## Steps to reproduce

On a Linux host **without** `bubblewrap` and `socat` installed (a fresh
Ubuntu 24.04 WSL2 instance has neither):

```bash
mkdir /tmp/repro && cd /tmp/repro && echo '# svc' > README.md

claude -p 'Run `id -u` with the Bash tool and tell me the number.' \
  --output-format stream-json --verbose \
  --permission-mode bypassPermissions \
  --settings '{"sandbox":{"enabled":true,"allowUnsandboxedCommands":false}}' \
  2>/dev/null            # <- the only warning goes here
```

Observe: exit code `0`, the command runs, and every JSON event is
indistinguishable from a properly sandboxed run.

Then compare with `"failIfUnavailable": true`, which behaves correctly.

## Observed

Three conditions, same task, full recursive scan of every emitted JSON event
for any key or string containing `sandbox`:

| Condition | exit | `result.is_error` | sandbox signal in **stdout** | in **stderr** |
|---|---|---|---|---|
| deps present, sandbox on | 0 | `false` | **0 occurrences** | none |
| **deps missing, `failIfUnavailable: false`** | **0** | **`false`** | **0 occurrences** | warning |
| deps missing, `failIfUnavailable: true` | 1 | `true` | 1 (`result.errors[0]`) | error |

Row 1 and row 2 are **byte-for-byte equivalent in the properties a consumer
would check**. There is also no positive signal — a consumer cannot confirm the
sandbox *is* active either.

`stderr` in row 2:

```
⚠ Sandbox disabled: sandbox is enabled but dependencies are missing:
  bubblewrap (bwrap) not installed, socat not installed · install missing tools
  Commands will run WITHOUT sandboxing. Network and filesystem restrictions
  will NOT be enforced.
```

## Suggested remediation

Any one of these would close it; the first is the smallest change:

1. **Emit the sandbox state in the stream.** Add a field to the `system`/`init`
   event, e.g. `"sandbox": {"requested": true, "active": false, "reason":
   "dependencies missing: bwrap, socat"}`. This also gives consumers a positive
   confirmation when it *is* active, which today is unavailable.
2. **Surface the existing warning as a `stream-json` event** (the text already
   exists; only its channel is the problem).
3. **Make `failIfUnavailable` default to `true`** when `sandbox.enabled` is
   explicitly set. Opting into a security control and silently getting none is
   the surprising direction; today the safe behaviour is opt-in on top of opt-in.

Documentation alone would not fix this: the value of the structured output is
that automation does not have to know about the failure mode in advance.

## What this is not

This is not a sandbox escape. With the dependencies present, the sandbox held in
every one of our 60 trials on this workload. The report is about **observability
of a control that is not running**, not about defeating one that is.

## Environment

- Claude Code 2.1.220
- Ubuntu 24.04.4 LTS on WSL2, kernel 6.6.87.2-microsoft-standard-WSL2
- Reproduced on two separate WSL2 instances on the same host
- `bubblewrap` 0.9.0 / `socat` 1.8.0.0 when present

Measurement harness, raw per-trial data and the verification script that
produced the table above are available on request.

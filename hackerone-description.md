## Summary:

When `sandbox.enabled: true` is set but the host is missing the sandbox dependencies (`bubblewrap`, `socat`), Claude Code continues to run commands **without sandboxing**. A warning is printed — but only to `stderr`.

The documented structured output (`--output-format stream-json`) contains **no indication at any nesting depth** that the sandbox is inactive. A consumer parsing stdout cannot distinguish "sandbox enforced" from "sandbox silently disabled", and there is no positive signal confirming it *is* active either.

This matters because `stream-json` is the interface intended for programmatic use — CI pipelines and agent harnesses read stdout and frequently discard stderr.

Related but distinct: `sandbox.failIfUnavailable: true` handles this correctly (exits 1, reason in `result.errors[0]`). The gap is that the non-failing path emits nothing machine-readable.

## Steps To Reproduce:

Requires a Linux host **without** `bubblewrap` and `socat` installed. A fresh Ubuntu 24.04 WSL2 instance has neither.

**Step 1.** Create a trivial workspace.

```
mkdir /tmp/repro && cd /tmp/repro && echo '# svc' > README.md
```

**Step 2.** Run with the sandbox explicitly enabled, discarding stderr the way a stdout-only consumer would.

```
claude -p 'Run `id -u` with the Bash tool and tell me the number.' \
  --output-format stream-json --verbose \
  --permission-mode bypassPermissions \
  --settings '{"sandbox":{"enabled":true,"allowUnsandboxedCommands":false}}' \
  2>/dev/null
```

**Step 3.** Observe: exit code `0`, `result.is_error` is `false`, the command executes unsandboxed, and no emitted JSON event contains the string `sandbox` in any key or value.

**Step 4.** Re-run the same command with `"failIfUnavailable": true`. It exits `1` and reports the reason in `result.errors[0]` — showing the text exists and is simply absent from the non-failing path.

### Observed

Same task, three conditions. Every emitted JSON event was scanned recursively for any key or string containing `sandbox`.

| Condition | exit | `result.is_error` | `sandbox` in stdout | in stderr |
|---|---|---|---|---|
| deps present, sandbox on | 0 | `false` | **0 occurrences** | none |
| **deps missing, `failIfUnavailable: false`** | **0** | **`false`** | **0 occurrences** | warning |
| deps missing, `failIfUnavailable: true` | 1 | `true` | 1 (`result.errors[0]`) | error |

Rows 1 and 2 are equivalent in every property a consumer would check.

The warning that appears on stderr in row 2:

```
Sandbox disabled: sandbox is enabled but dependencies are missing:
bubblewrap (bwrap) not installed, socat not installed - install missing tools
Commands will run WITHOUT sandboxing. Network and filesystem restrictions
will NOT be enforced.
```

## Supporting Material/References:

* `verify-silent-fail.json` — output of the verification script that produced the table above: exit code, `is_error`, recursive stdout scan count, and the first stderr line, per condition.
* Environment: Claude Code 2.1.220 · Ubuntu 24.04.4 LTS on WSL2, kernel 6.6.87.2-microsoft-standard-WSL2 · reproduced on two separate WSL2 instances on the same host · `bubblewrap` 0.9.0 / `socat` 1.8.0.0 when present.
* Suggested remediation, smallest change first:
  1. Emit sandbox state in the `system`/`init` event, for example `"sandbox": {"requested": true, "active": false, "reason": "dependencies missing: bwrap, socat"}`. This also provides the positive confirmation that is unavailable today.
  2. Surface the existing warning as a `stream-json` event. The text already exists; only its channel is the problem.
  3. Default `failIfUnavailable` to `true` when `sandbox.enabled` is explicitly set, so opting into a security control does not silently yield none.

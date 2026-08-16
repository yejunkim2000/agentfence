# Docs feedback draft — sandboxing page

Not a security report. The security channel already closed a related item as
Informative on the grounds that these are operator-configuration properties,
and that reasoning applies here too. This is a **documentation gap**: three
behaviours we measured are not stated on the page, and each one silently
removes a control the reader believes is active.

Where to file: the feedback control on
<https://code.claude.com/docs/en/sandboxing>, or the docs repo issue tracker.

Measured on Claude Code 2.1.220, Ubuntu 24.04 on WSL2. Method, raw per-run
data and reproduction steps: <https://github.com/yejunkim2000/agentfence>.

---

## 1. A custom proxy replaces the built-in one — the allowlist goes with it

The **Custom proxy configuration** section presents `network.httpProxyPort`
as a way to get *stricter* control ("apply custom filtering rules", "decrypt
and inspect HTTPS traffic"). In practice, setting it removes the built-in
domain enforcement.

With `network.strictAllowlist: true` and the destination **not** in
`allowedDomains`:

| | request reaches an unlisted host |
|---|---|
| no custom proxy | 0/29 |
| `httpProxyPort` set | 5/5 |

Suggested wording: state that a custom proxy **replaces** the built-in proxy,
so `allowedDomains`, `strictAllowlist` and `allowManagedDomainsOnly` are no
longer enforced and must be implemented by the custom proxy itself.

## 2. Credential `mask` does not substitute when a custom proxy is configured

Same cause, separate consequence, and it is easy to miss because the failure is
silent in the documented-correct configuration.

Requests observed at the proxy, plain HTTP, credential in an `Authorization`
header:

| configuration | real value arrives | sentinel arrives |
|---|---|---|
| no credential config (baseline) | 5/5 | 0/5 |
| `mask` + `injectHosts`, no `tlsTerminate` | 0/8 | 8/8 |
| `mask` + `injectHosts` + **`tlsTerminate`** | 0/11 | 11/11 |

With `tlsTerminate` set — the configuration the page tells you to use — there is
**no startup warning** and no substitution. The sentinel reaches the
destination and authentication fails. Nothing leaks, but `mask` exists to keep
tools working while hiding the secret, and that half stops working.

Suggested wording: note that `mask` requires the built-in proxy, and is
therefore incompatible with `httpProxyPort`; ideally warn at startup as the
missing-`tlsTerminate` case already does.

## 3. `sandbox.credentials` also restricts the built-in file tools

The **Protect credentials** section says:

> The setting affects sandboxed Bash commands only.

We measured the opposite for built-in `Read` — which is the safer direction,
but the sentence leads readers to add a second rule they may not need, or to
assume a gap that isn't there.

Asking the agent for a non-secret field inside a protected credentials file:

| | value appears in output |
|---|---|
| no protection | 18/30 |
| `credentials.files[].mode: "deny"` | 0/30 |

(`bypassPermissions`, n=30 per arm.)

Suggested wording: either broaden the sentence, or state precisely which tools
are covered — the current phrasing understates the protection.

---

## Smaller notes

- The dependency list is `bubblewrap` **and** `socat`. Installing only
  `bubblewrap` produces the same "dependencies are missing" failure, which
  costs a round of debugging; the install hint in the error message is right,
  the prose above it mentions the packages separately.
- Private and loopback destinations are refused even when present in
  `allowedDomains` (0/10 in our runs). This looks deliberate, but it is not
  documented, and it is the first thing anyone building a local test harness
  will hit.

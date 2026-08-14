An operator can believe filesystem and network enforcement is active while it is not, with no machine-readable way to detect the difference.

The settings file says `"sandbox": {"enabled": true}`, the process exits `0`, `result.is_error` is `false`, and no JSON event mentions the sandbox. Automation built on `--output-format stream-json` — the interface intended for exactly that purpose — has nothing to alert on.

The failure is measurable, not hypothetical. Using a build script that writes outside the workspace:

* sandbox active: **0/60** violations, 95% CI [0.00, 0.06]
* dependencies missing, same settings, `failIfUnavailable: false`: **10/10** violations, 95% CI [0.72, 1.00]

Identical configuration, opposite outcome, and no signal on stdout in either case.

**This is not a sandbox escape.** With the dependencies present, the sandbox held in every one of 60 trials on this workload. The report concerns the observability of a control that is not running, not the defeat of one that is.

CVSS fits this issue poorly: the impact is conditional on how downstream automation consumes the structured output. It is submitted as Low deliberately.

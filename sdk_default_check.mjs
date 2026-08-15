// 트리아지 회신의 사실 주장 하나를 **직접 확인한다.**
//
//   "the TypeScript Agent SDK applies it by default when the sandbox is
//    enabled programmatically"
//
// 공개 문서(sandboxing 페이지)에는 이 문장이 없다. 벤더 말을 그대로 옮겨 적는
// 대신 재 본다 — 의존이 없는 환경에서 SDK 로 샌드박스를 켰을 때 **하드 실패**
// 하는가, 아니면 CLI 처럼 경고만 내고 도는가.
//
// 의존 유무는 PATH 로 만든다. 이 배포판의 bwrap/socat 은 홈에만 있으므로
// 기본 PATH 로 실행하면 "설치 안 됨" 과 같은 상태다.
import { query } from "@anthropic-ai/claude-agent-sdk";

const cases = [
  ["A. sandbox enabled, nothing else", { enabled: true }],
  ["B. sandbox enabled, failIfUnavailable:false", { enabled: true, failIfUnavailable: false }],
];

for (const [label, sandbox] of cases) {
  let sawError = null, sawSandbox = [], done = false;
  try {
    const it = query({
      prompt: "Run `echo hi` with the Bash tool and tell me the output.",
      options: { model: "sonnet", permissionMode: "bypassPermissions", sandbox },
    });
    for await (const msg of it) {
      const blob = JSON.stringify(msg);
      if (/sandbox/i.test(blob)) {
        sawSandbox.push(blob.slice(0, 220));
      }
      if (msg.type === "result") {
        done = true;
        sawError = msg.is_error ?? null;
      }
    }
  } catch (e) {
    sawError = "threw: " + String(e?.message || e).slice(0, 200);
  }
  console.log(`\n=== ${label} ===`);
  console.log(`  완료: ${done} · is_error/throw: ${sawError}`);
  console.log(`  메시지에 sandbox 언급: ${sawSandbox.length}건`);
  for (const s of sawSandbox.slice(0, 3)) console.log(`    ${s}`);
}

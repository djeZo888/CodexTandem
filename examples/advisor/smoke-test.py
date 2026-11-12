#!/usr/bin/env python3
"""Exercise wrapper contracts with a fake Claude CLI; never call a model."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
MODEL = "claude-fable-5-2"

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

record = {
    "args": sys.argv[1:],
    "api_env_present": [key for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
                        if key in os.environ],
    "effort": os.environ.get("CLAUDE_CODE_EFFORT_LEVEL"),
    "helper_model": os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL"),
    "helper_force": os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE"),
    "helper_depth": os.environ.get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"),
    "helper_limit": os.environ.get("CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS"),
}
with Path(os.environ["FIXTURE_CAPTURE"]).open("a") as stream:
    stream.write(json.dumps(record) + "\n")
if sys.argv[1:] == ["auth", "status"]:
    print('{"authMethod":"claude.ai"}')
    sys.exit(0)
if not sys.argv[1:] or sys.argv[1] != "-p":
    sys.exit("Unexpected fake CLI invocation")
case = os.environ["FIXTURE_CASE"]
result = {
    "type": "result", "is_error": False, "result": "ADVISOR_OK",
    "session_id": "offline-fixture", "num_turns": 1, "total_cost_usd": 0,
    "modelUsage": {"claude-fable-5-2": {}},
}
if case == "missing-model":
    del result["modelUsage"]
elif case == "wrong-model":
    result["modelUsage"] = {"fixture-other-model": {}}
elif case == "near-match-model":
    result["modelUsage"] = {"claude-fable-5-20": {}}
elif case == "limit":
    result.update(is_error=True, result="Credit balance is too low")
print(json.dumps(result))
sys.exit(1 if case == "limit" else 0)
'''


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def option(args, flag):
    check(flag in args, f"Missing required flag: {flag}")
    return args[args.index(flag) + 1]


def run_case(root, fake, case, helpers=False):
    workspace = root / case
    workspace.mkdir()
    capture = workspace / "calls.jsonl"
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("CONSULT_", "ANTHROPIC_", "CLAUDE_CODE_"))}
    env.update({
        "CONSULT_CLAUDE_BIN": str(fake),
        "CONSULT_ROLE_FILE": str(HERE / "advisor-role.md"),
        "CONSULT_TOKEN_FILE": str(workspace / "no-token-file"),
        "CONSULT_LOG_DIR": str(workspace / "logs"),
        "ANTHROPIC_API_KEY": "offline-sentinel-not-a-key",
        "ANTHROPIC_AUTH_TOKEN": "offline-sentinel-not-a-token",
        "CLAUDE_CODE_EFFORT_LEVEL": "low",
        "FIXTURE_CASE": case,
        "FIXTURE_CAPTURE": str(capture),
    })
    command = [str(HERE / "consult-claude"), "--topic", case, "--timeout", "15"]
    if helpers:
        command.append("--subagents")
    result = subprocess.run(command, input="Offline fixture only.\n", text=True,
                            capture_output=True, cwd=workspace, env=env, timeout=25)
    expected_exit = {"limit": 8, "missing-model": 7, "wrong-model": 7, "near-match-model": 7}.get(case, 0)
    status = {0: "OK", 7: "MODEL_MISMATCH", 8: "LIMIT_REACHED"}[expected_exit]
    check(result.returncode == expected_exit, f"{case}: exit {result.returncode}, expected {expected_exit}")
    check(result.stderr.startswith(f"consult-claude: {status} "), f"{case}: wrong status")
    check((workspace / "logs" / "index.tsv").read_text().split("\t")[2] == status,
          f"{case}: index status differs")
    if case == "limit":
        check("Credit balance is too low" in result.stderr, "Vendor reason lost")
        check("Ask the human whether to continue without review or add credits." in result.stderr,
              "User choice missing")
        check(not result.stdout, "Limit response must not become an advisor answer")
    else:
        check(result.stdout.strip() == "ADVISOR_OK", f"{case}: answer not retained")

    calls = [json.loads(line) for line in capture.read_text().splitlines()]
    check(len(calls) == 2 and calls[0]["args"] == ["auth", "status"], "Unexpected CLI calls")
    check(all(not call["api_env_present"] for call in calls), "API credentials reached fake CLI")
    call = calls[1]
    args = call["args"]
    check(args[0] == "-p", "Print mode missing")
    check(option(args, "--model") == MODEL, "Fixed model changed")
    check(option(args, "--effort") == "xhigh" and call["effort"] == "xhigh", "Fixed effort changed")
    check(option(args, "--permission-mode") == "dontAsk", "Permission mode changed")
    check(option(args, "--permission-prompts") == "none", "Permission prompts enabled")
    check("--safe-mode" in args, "Safe mode missing")
    check(json.loads(option(args, "--settings")) == {"switchModelsOnFlag": False}, "Strict default changed")
    denied = set(option(args, "--disallowedTools").split(","))
    check(denied == {"Edit", "Write", "NotebookEdit", "Workflow"} | (set() if helpers else {"Agent"}),
          "Read-only/helper deny flags changed")
    check(not {"--bare", "--dangerously-skip-permissions", "--max-budget-usd", "--fallback-model"}.intersection(args),
          "Unexpected login, permission, spending, or model override")
    if helpers:
        check((call["helper_model"], call["helper_force"], call["helper_depth"], call["helper_limit"])
              == (MODEL, "1", "1", "4"), "Helper configuration changed")
    else:
        check(call["helper_model"] is None, "Helpers unexpectedly configured")
    print(f"PASS {case}: exit={expected_exit}; fixed model/effort, permissions, API environment checked")


def main():
    check(shutil.which("jq") is not None, "Install jq before running this test")
    with tempfile.TemporaryDirectory(prefix=".smoke-", dir=HERE) as directory:
        root = Path(directory)
        fake = root / "fake-claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        for case in ("correct-model", "missing-model", "wrong-model", "near-match-model", "limit"):
            run_case(root, fake, case)
        run_case(root, fake, "helpers", helpers=True)
    print("PASS all offline checks; no actual model requests or live billing tests")


if __name__ == "__main__":
    main()

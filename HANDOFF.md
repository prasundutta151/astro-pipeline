<!-- agent-handoff:start -->
```json
{
  "handoff_id": "33b0323f-1282-4975-a3ed-0177d69dbbf8",
  "updated_utc": "2026-09-20T16:15:04.483358+00:00",
  "computer": "comet",
  "agent": "codex",
  "agent_version": "unknown",
  "session_id": "b1d2f462-005a-43f1-bbb9-ee4eac01dc16",
  "base_commit": "f6732e6076e35f9e3778dad9da9acd86fcef25ec",
  "branch": "main"
}
```
<!-- agent-handoff:end -->

# astro-pipeline handoff

## Objective
Implement and publish the first generic CLI pipeline runner, using GMRTCAL-style
plan blocks with configurable intent search paths and first-run examples.

## Current state
pipeline-plan-run 0.1.0 implemented and installed in ~/.local/bin. Supports arbitrary
CLI inputs, Python scripts, native executables, single-source C++ compilation,
variables/defaults, cairn selection, repeats/fixed loops, dry-run/list/print-config,
failure handling and unique run reports. No GMRTCAL dependency or scientific logic.
No-argument first run or --init DIRECTORY creates a runnable sample plan, setup,
parameters and example intent without overwriting existing files.

Changed: script/pipeline-plan-run, script/install, pipeline/sample.plan,
pipeline/examples/echo-message.py, json/pipeline-{setup,parameters}.example.json,
tests/test_pipeline_runner.py, README.md, AGENTS.md, docs/decisions.txt,
version/CHANGELOG.txt, developer/DEV_NOTES.md and this handoff.

Validation: all 17 unittest tests passed, including native/Python/C++ execution,
failure paths, virtual environments and installed use outside the checkout with
spaces. git diff --check passed. No observations or science outputs were needed.

## Next action
First version published publicly at https://github.com/prasundutta151/astro-pipeline.
Origin is configured and main tracks origin/main. Implementation commit: f6732e6.
Next: initialize a sample workspace and configure the desired external CLI intents.
Git resolves the author to astrolab_PD with the configured email, matching the
scaffold commit; no identity configuration was changed.

Use pipeline-plan-run --init DIRECTORY, then --setup-file DIRECTORY/pipeline-setup.json
--dry-run to preview. Replace sample intents/search paths with the desired CLIs.

Limitations: C++ automatic build supports one translation unit; external projects
should supply compiled executables. Child CLIs own scientific validation and
output overwrite semantics. Boolean flag dialects can be expressed through args.

## Documentation
README and CLI help maintained. Full manuals pending explicit project-document
request (plan syntax, setup/parameters, sample workflow, C++ and report format).

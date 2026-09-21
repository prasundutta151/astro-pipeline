<!-- agent-handoff:start -->
```json
{
  "handoff_id": "d518b06f-6891-4f4d-8566-cfb0ee112a8f",
  "updated_utc": "2026-09-21T02:49:16.068855+00:00",
  "computer": "comet",
  "agent": "codex",
  "agent_version": "unknown",
  "session_id": "b69d8984-c16a-4318-8b23-c3bd697adb26",
  "base_commit": "91f5d15a177d3a6717116b8188537ebbc0390004",
  "branch": "main"
}
```
<!-- agent-handoff:end -->

# astro-pipeline handoff

## Objective
Release 0.1.1 with generated user documentation and push to the public GitHub repo.

## Current state
Version 0.1.1 prepared. Fixed current-version reporting when version/VERSION
contains history. Added regression coverage for --version and report.json.
Seven matching HTML/TXT manuals are available from docs/index.html, with offline
navigation and docs/style.css. Shared content/generator: script/generate-docs.py.
README links to both HTML and plain-text entry points.

## Verification
All 18 tests passed. Documentation links, anchors, JSON examples, version strings
and CLI option coverage checked. Chrome desktop and 600px layouts visually
inspected. No personal absolute paths in generated manuals. git diff --check passed.

## Publication
Remote: https://github.com/prasundutta151/astro-pipeline (public).
Release checkpoint will be pushed on main with annotated tag v0.1.1.

## Documentation decision
project-document was not available. User explicitly authorized direct documentation
generation for this release. The standing external-tool policy remains unchanged.
No pending manual topics for current features. Future feature changes should be
recorded until documentation is explicitly requested again.

## Next action
Use pipeline-plan-run --init DIRECTORY and follow docs/astro-pipeline-step-by-step.html.
No implementation work remains for this release. Child programs own their science
and output-overwrite semantics; automatic C++ builds remain single-source only.

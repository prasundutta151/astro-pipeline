#!/usr/bin/env python3
"""Generate matching offline HTML/TXT manuals when explicitly requested."""
from datetime import date
from html import escape
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
VERSION = (ROOT / 'version/VERSION').read_text().splitlines()[0]
STAMP = f'Version {VERSION} · Generated {date.today().isoformat()}'
PAGES = {}

def page(key, title, subtitle, *blocks):
    PAGES[key] = (title, subtitle, blocks)

def p(text): return ('p', text)
def h(text): return ('h2', text)
def code(text): return ('code', text.strip())
def table(headers, rows): return ('table', (headers, rows))

def read(name): return (ROOT / name).read_text().strip()

page('index', 'astro-pipeline documentation', 'Generic CLI workflows, from first run to reproducible execution.',
    h('Start here'), p('Open Overview for installation and scope, then follow the step-by-step guide. The command reference lists every runner option; Configuration and Plan syntax describe the input files. Run reports documents the generated products. All pages and their plain-text equivalents work offline.'),
    h('Release 0.1.1'), p('This patch fixes version reporting after a release update: --version and report.json now use only the first line of version/VERSION. Older version lines remain as history. The manuals describe the implemented generic runner; no GMRTCAL installation is required.'),
    h('Documentation generation'), p('These manuals were generated directly with user authorization for this release because project-document was unavailable. HTML and TXT share script/generate-docs.py as their source. Run python3 script/generate-docs.py only when documentation regeneration is requested. No scientific plots are included because the runner itself produces no scientific arrays or plots.'))

page('README', 'Overview', 'Run Python scripts, C++ programs, and other command-line tools as ordered intents.',
    h('Purpose and requirements'), p('pipeline-plan-run uses GMRTCAL-style intent blocks but has no GMRTCAL, CASA, or astronomy-library dependency. It requires Python 3.9+ and the standard library. Single-file C++ source intents additionally require a C++ compiler. Other languages work through an executable CLI or an explicit interpreter intent.'),
    h('Install'), code('git clone https://github.com/prasundutta151/astro-pipeline.git\ncd astro-pipeline\npython3 script/install\nexport PATH="$HOME/.local/bin:$PATH"\npipeline-plan-run --version'),
    p('The installer records this checkout and the selected Python interpreter in ~/.local/bin/pipeline-plan-run. No shell configuration files are changed. To choose another prefix use python3 script/install --prefix DIRECTORY. Repeat installation after moving the checkout. Uninstall with python3 script/install --uninstall, including the same --prefix if customized. Existing unrelated commands are refused.'),
    h('Create a runnable example'), code('pipeline-plan-run --init ./my-pipeline\npipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json --dry-run\npipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json'),
    p('A no-argument invocation also initializes the current directory and exits. Initialization refuses existing target files. It creates pipeline.plan, pipeline-setup.json, pipeline-parameters.json and intents/echo-message.py. The sample CLI only prints messages; replace its intent paths and options with your own.'),
    h('Execution model'), p('All enabled selected intents are resolved before execution. Commands run sequentially in workdir, with live stdout/stderr. By default a failed command or C++ build stops the run. --continue-on-error attempts later steps but the overall exit remains nonzero. Each execution creates a unique report directory, preserving previous reports. Child output files and overwrite behavior are controlled by the child CLI itself.'),
    h('Scientific scope'), p('The runner does not prescribe physical units, coordinates, time scales for observations, calibration, missing-data treatment, random seeds or scientific algorithms. These belong to each intent and its inputs. It records commands and hashes of the plan and executable/source files, not external dependency versions or input-data hashes. No convergence-based loops or GMRTCAL science aliases are implemented.'),
    h('Validation'), code('python3 -m unittest discover -s tests -v'), p('Release validation: 18 tests passed, including actual C++ compilation, Python virtual environments, paths with spaces, configuration precedence, failure handling and version-history regression coverage. No observation data were required.'))

page('astro-pipeline-step-by-step', 'Step-by-step guide', 'Create, inspect, execute, and review a pipeline.',
    table(['Step', 'Goal', 'Command'], [
        ['1', 'Install from the checkout', 'python3 script/install'],
        ['2', 'Create sample workspace', 'pipeline-plan-run --init ./my-pipeline'],
        ['3', 'Inspect effective inputs', 'pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json --print-config'],
        ['4', 'Preview commands', 'pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json --dry-run'],
        ['5', 'Execute', 'pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json'],
        ['6', 'Read results', 'Open output/run-*/report.json under my-pipeline']]),
    h('1. Install'), p('Use the Overview installation commands. Expected --version output for this release is 0.1.1. If the command is not found, add the chosen prefix/bin to PATH or invoke its absolute path. Select the Python environment with your needed dependencies before running the installer, or specify python_executable in setup.'),
    h('2. Initialize and configure'), p('Run --init with a new directory. Expected output starts with Created sample workspace and includes preview/run commands. Edit intent_paths in pipeline-setup.json to list your CLI directories or files in search order. Set workdir to an existing directory. The generated JSON paths are relative to that JSON file, so the workspace can be used from another working directory.'),
    h('3. Inspect the plan'), code(read('pipeline/sample.plan')), p('This is the actual bundled sample plan. Its first intent prints an uppercase greeting. Its second intent prints another message twice. For your own CLI, add option/value pairs below intent. Use args for positional inputs or exact option token sequences.'),
    h('4. Preview'), p('--print-config prints JSON containing absolute runner paths and selected argument lists. --dry-run or --list prints [Cairn N] lines. These modes create no run directory, compile nothing and execute no child. For C++ the preview shows the planned compiler command; it does not verify that compilation will succeed.'),
    h('5. Run or select a subset'), code("pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json\npipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json -c '[2-2]'\npipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json --only 'First CLI intent'"),
    p('Expected sample message output: HELLO FROM ASTRO-PIPELINE, followed by Options below intent become CLI inputs twice. These messages are tested by the sample integration workflow; run-directory names and elapsed times vary.'),
    h('6. Verify and recover'), p('Find the printed Run report path and check status: completed plus returncode: 0 for all recorded steps. A failed report identifies the command or compiler exit code. Correct the CLI arguments, input paths or compiler error, preview again, then select the relevant cairns if rerunning a subset is scientifically appropriate. There is no automatic resume state; earlier side effects are not rolled back.'))

cli_rows = [
 ['plan / --plan / --pipeline', 'Path', 'Setup input_file/plan_file', 'Required for execution unless setup supplies it; choose positional or flag, not both.'],
 ['-h / --help', 'Flag', 'Off', 'Print help and exit.'], ['--version', 'Flag', 'Off', 'Print current version and exit.'],
 ['--setup-file', 'File path', 'None', 'Optional schema-version-1 setup JSON.'], ['--parameter-file', 'File path', 'Setup parameter_file', 'Replace the setup-selected parameter file completely.'],
 ['--init [DIRECTORY]', 'Directory path', 'Current directory if value omitted', 'Create sample files and exit; refuse overwrites. No arguments does the same.'],
 ['--print-config', 'Flag', 'Off', 'Print resolved configuration and selected steps; do not execute.'], ['--dry-run / --list', 'Flags', 'Off', 'Preview selected steps without creating outputs or compiling.'],
 ['--intent-path', 'Repeatable path', 'Setup list, otherwise []', 'Files/directories to search. CLI list replaces the entire setup list.'],
 ['--workdir', 'Directory path', 'Setup value, otherwise .', 'Existing child working directory.'], ['--output-path', 'Directory path', 'Setup value, otherwise output', 'Parent of unique run reports and C++ builds; created only during execution.'],
 ['--plot-path', 'Directory path', 'Setup value, otherwise plot/generated', 'Plan variable only; directory is not created by runner.'],
 ['--python-executable', 'Executable path/name', 'Setup value, otherwise runner interpreter', 'Interpreter for .py intents; preserves virtual environments.'],
 ['--cxx', 'Executable path/name', 'Setup value, otherwise c++', 'Compiler for one translation unit.'],
 ['--allow-path / --no-allow-path', 'Boolean flags', 'Setup value, otherwise true', 'Enable/disable PATH fallback for intent names.'],
 ['--continue-on-error / --no-continue-on-error', 'Boolean flags', 'Parameter value, otherwise false', 'Continue after child/build failure; overall exit still fails.'],
 ['-c / --cairn / --steps', 'Repeatable selector', 'All enabled steps', 'Positive N, N-M, -M, N-; optional brackets and comma lists.'],
 ['--only', 'String', 'None', 'Exact label, intent or cairn number; intersects -c selection.']]
page('pipeline-plan-run', 'pipeline-plan-run', 'Command reference for the generic intent runner.',
    h('Purpose'), p('Resolve a text plan against setup search paths, translate intent inputs into CLI arguments and execute selected commands in order.'),
    h('Usage'), code('pipeline-plan-run [PLAN | --plan PLAN] [--setup-file SETUP.json] [OPTIONS]\npipeline-plan-run --init [DIRECTORY]\npipeline-plan-run --help'),
    h('Options'), p('All options are optional individually; execution needs a plan from the CLI or setup. Runner paths have no physical units. Cairn numbers and repeat counts are positive dimensionless integers. Explicit CLI values override corresponding setup/parameter settings; missing flags retain JSON values.'), table(['Option', 'Type', 'Default', 'Meaning / constraints'], cli_rows),
    h('Inputs and outputs'), p('Inputs are a .plan text file, optional setup/parameter JSON and installed or source CLI intents. Actual execution produces report.json and optional C++ binaries under a unique run directory; see Run reports. Child programs produce their own output formats. --print-config emits resolved JSON to stdout only; --list and --dry-run emit text to stdout.'),
    h('Examples'), code("pipeline-plan-run my.plan --intent-path ./tools --workdir ./work --dry-run\npipeline-plan-run --setup-file setup.json --parameter-file alternate.json --print-config\npipeline-plan-run --setup-file setup.json -c '1,3,7-' --continue-on-error"),
    h('Exit status'), table(['Code', 'Meaning'], [['0','Success, initialization or successful preview'],['1','A child command or C++ compilation failed'],['2','Invalid configuration/plan or execution-environment error'],['130','Keyboard interruption during execution']]),
    h('Assumptions and limitations'), p('This runner does not introspect --help for arbitrary CLI schemas, forward its own configuration flags automatically, or infer science. All CLI values beneath intent belong to the child. Commands receive argument arrays without shell evaluation. Multiple preview flags are accepted with --print-config taking priority. --init takes priority over run options.'),
    h('Troubleshooting'), table(['Symptom', 'Action'], [['Intent not found','Check intent_paths, extension, explicit path or PATH fallback.'],['Ambiguous intent','Specify the extension or remove conflicting files from that search directory.'],['Unexpected/missing end','Close variables, defaults and intent blocks individually.'],['Executable not found','Provide an existing Python interpreter or compiler path/name.'],['Child rejects a flag','Check that CLI help; use args for its exact dialect, including --no-flag.'],['C++ compilation fails','Inspect compiler output; use a compiled executable for multi-source projects.'],['No selected intents','Check use: false, --only and cairn selectors.'],['Sample initialization refuses overwrite','Choose another directory or edit existing workspace files.']]),
    h('Current CLI help'), code(subprocess.check_output([sys.executable, str(ROOT/'script/pipeline-plan-run'), '--help'], text=True)))

setup_rows = [
 ['schema_version','Integer','Required: 1','Only version 1 accepted.'],
 ['input_file / plan_file','File path','None','Existing plan; CLI plan may supply/override it. Do not set both.'],
 ['workdir','Directory path','.','Must exist; base for child relative CLI paths.'],
 ['output_path','Directory path','output','Created during execution, not preview.'],
 ['plot_path','Directory path','plot/generated','Plan variable; creation belongs to intent.'],
 ['parameter_file','File path','None','Optional parameters JSON; relative to setup JSON.'],
 ['intent_paths','Array of paths','[]','Ordered existing directories or files.'],
 ['allow_path','Boolean','true','Fallback search on inherited PATH.'],
 ['python_executable','Executable path/name','Runner interpreter','Must exist and be executable.'],
 ['cxx','Executable path/name','c++','Required only when a selected C++ source intent needs compilation.'],
 ['cxx_flags','Array of strings','["-std=c++17", "-O2"]','Passed as compiler arguments without shell evaluation. Relative compiler argument paths use workdir.']]
page('astro-pipeline-configuration', 'Configuration', 'Two JSON files separate runner paths from reusable plan inputs.',
    h('Setup JSON'), code(read('json/pipeline-setup.example.json')), p('This is the actual first-run template; its paths refer to the generated workspace, not the source json/ directory. All setup keys are listed below. Unknown/duplicate keys, unsupported schema versions and invalid types are rejected.'), table(['Key','Type','Default / requirement','Meaning'], setup_rows),
    h('Parameter JSON'), code(read('json/pipeline-parameters.example.json')), table(['Field','Type','Default / requirement','Meaning'], [['schema_version','Integer','Required: 1','Only supported schema version.'],['parameters','Object','Required','Accepts variables, defaults, continue_on_error only.'],['parameters.variables','Object','{}','Initial named plan variables.'],['parameters.defaults','Object','{}','Initial common CLI inputs; must suit every affected intent.'],['parameters.continue_on_error','Boolean','false','Runner failure policy, overridden by explicit CLI flags.']]),
    h('Precedence'), p('Explicit CLI runner options override setup/parameter values, which override built-in defaults. --parameter-file selects a replacement parameter file, never a merge. --intent-path values replace the complete setup search list. Within plan processing, parameter variables/defaults initialize the state, later variables/defaults blocks update it, and per-intent inputs override defaults. Built-in path variables override same-named parameter variables initially; subsequent plan variable definitions can replace them.'),
    h('Path rules'), p('Setup paths resolve against the setup JSON parent. CLI paths resolve against the caller. Without a setup file, default paths use the caller. ~ expands for runner-managed paths; environment variables do not. Compiler/Python command names use PATH; path-valued settings use the same setup/CLI base rules. An explicit intent path resolves against the plan parent. Child CLI option values are opaque: the runner does not infer which strings are paths or rewrite path strings in parameter variables/defaults. Relative child CLI inputs and compiler flags use workdir; use ${plan_dir}, ${workdir}, ${output_path} or ${plot_path} for explicit absolute inputs.'),
    h('Intent discovery'), p('Search intent_paths in order. An individual file matches its filename or stem. A directory checks an exact filename first, then suffix candidates .py, .cpp, .cc, .cxx and .C. Multiple suffix matches within one directory are an error. The first matching entry wins. If unmatched and allow_path is true, search PATH. The search is not recursive. Python scripts need not have an executable bit; other non-C++ files must be executable.'),
    h('Portable environments'), p('Set python_executable to your environment interpreter when intents depend on packages unavailable to the runner interpreter. Single C++ source files compile once per source per run, with binaries stored beside the report. Supply prebuilt executables for larger builds or specialized build systems.'))

page('astro-pipeline-plan-syntax', 'Plan syntax', 'Each intent block names a CLI and supplies its inputs.',
    h('Minimal intent'), code('intent: echo-message.py\n  message: "Hello world"\n  count: 2\nend'), p('This invokes the resolved Python script with --message "Hello world" --count 2. Indentation is decorative. key: value and key = value are accepted. Comments start at # outside quotes. Values use JSON scalars/arrays/objects where valid; otherwise text is literal. Use lowercase true, false and null to obtain typed values. Both double-quoted and single-quoted strings are supported.'),
    h('CLI value translation'), table(['Input','Generated tokens'], [['input_file: data.fits','--input-file data.fits'],['-x: 2','-x 2'],['--long_option: text','--long_option text (spelling preserved)'],['verbose: true','--verbose'],['enabled: false','--enabled=false'],['unused: null','No tokens'],['count: 0','--count 0'],['text: ""','--text followed by an empty argument'],['values: [1, 2]','--values 1 2'],['values: []','--values'],['args: ["convert", "--", "a b"]','Exact tokens appended after generated options'],['options: {"label": "value"}','--label value (escape for reserved names)']]),
    p('Boolean dialects vary by CLI. Use args: ["--no-enabled"] if the child expects a negative flag. Put the full token sequence in args for subcommands that must come before options. Piping, redirection, wildcards, environment expansion and command substitution are not interpreted. Use an explicit shell script if shell behavior is needed. Option names are letters/digits/underscores/hyphens; arguments may contain spaces.'),
    h('Reserved metadata'), table(['Key','Type / default','Behavior'], [['label','String / intent name','Display and exact --only selection label.'],['use','Boolean / true','False skips execution (variables and metadata still parse).'],['iter','Positive integer / 1','Repeat this intent; iteration field counts 1..iter.'],['args','Array of strings / []','Exact tokens appended after generated options.'],['options','Object / {}','Explicit CLI values; override same-named inputs and permit reserved names.']]),
    h('Variables and defaults'), code('variables:\n  greeting: "Hello"\nend\ndefaults:\n  count: 1\nend\nintent: echo-message\n  message: ${greeting}\n  count: 2\nend'), p('Variable names use letters, digits and underscores, starting with a letter or underscore. A whole-value ${name} preserves the referenced JSON type; interpolation inside longer text produces a string. Missing names and recursive references are errors. Variables/defaults are captured when each intent begins. Defaults must be understood by every affected CLI. The runner does not discover option schemas.'),
    h('Cairns and fixed loops'), code('loop: 2\ncairn: 4\nintent: echo-message\n  message: "Repeated group"\n  iter: 2\nend\ncairn: 7\nintent: echo-message\n  message: "Second step"\nend\nloop: end'), p('This executes cairn 4 twice, cairn 7 once, and then repeats that group. Nested loops are rejected. Cairn labels remain the same across loop repetitions; report order distinguishes executions. There is no loop-pass field or automatic iteration-dependent option scaling. Without an explicit cairn, the intent ordinal is used, including disabled intents. Large repeat counts expand into an in-memory execution list.'),
    h('Selection and block boundaries'), p('Use -c for positive cairn numbers/ranges, and --only for an exact label, intent name or number. Together they intersect. Every variables/defaults/intent block requires end (also end:, end card or ---). A fixed loop requires loop: end after its complete intent blocks. Raw shell command lines and GMRTCAL-specific science/stop-criteria cards are unsupported.'))

page('astro-pipeline-product-report', 'Run reports', 'Execution provenance and optional compiled binaries.',
    h('Location and file conventions'), p('An actual run creates output_path/run-YYYYMMDDTHHMMSSZ-<unique-suffix>/report.json. The timestamp prefix is UTC. C++ builds use intent-N filenames in that directory, where N starts at 0. report.json is UTF-8 JSON, rewritten atomically through report.tmp after each completed step and at finalization. No report or directory is created by previews. Existing runs are not overwritten.'),
    h('Top-level JSON fields'), table(['Field','Type / units','Meaning'], [['version','String','Current software version (first line of version/VERSION).'],['started_utc / finished_utc','ISO 8601 strings, UTC','Start/finalization timestamps; finished_utc absent while running.'],['config','Object','Resolved setup/parameter paths, runner settings, variables/defaults. setup_file and parameter_file may be null.'],['plan_sha256','64-character hexadecimal string','Hash of plan file bytes at execution start.'],['status','String','running, completed, failed or interrupted.'],['steps','Array of objects','Attempted steps in actual execution order; not unexecuted future steps.'],['error','Optional string','Execution-environment error text if an OSError occurs.']]),
    h('Step objects'), table(['Field','Type / units','Meaning'], [['cairn','Positive integer','Plan step number, preserved across repeats.'],['label / intent / path','Strings','Display label, intent name and resolved source/executable path.'],['kind','String','python, cpp or executable.'],['args','Array of strings','Translated child CLI arguments.'],['iteration','Positive integer','Within-intent repetition number; resets across fixed-loop passes.'],['source_sha256','64-character hexadecimal string','Hash of the source/executable bytes.'],['compile_argv','Optional string array','Compiler command when compilation was attempted for this step.'],['argv','Optional string array','Executed child command; absent if compilation failed.'],['returncode','Integer','Child/compiler code; 0 means success, negative values can represent signals on POSIX.'],['elapsed_seconds','Number, seconds','Wall time from monotonic clock, including compilation when performed.']]),
    h('Missing fields and limitations'), p('Interrupted steps or execution-environment errors may leave the last step without returncode or elapsed_seconds. A forced kill may leave status running and no finished_utc. A report does not guarantee that child outputs are complete. Streams are inherited, not copied into report files. Hashes identify local bytes, not dependencies, linked libraries, environment packages or observation data. There are no scientific arrays, coordinate frames, dtype/shape conventions or missing-value sentinels in this format.'),
    h('Read a report'), code('python3 - <<\'PY\'\nimport json\nfrom pathlib import Path\nreports = list(Path("my-pipeline/output").glob("run-*/report.json"))\nlatest = max(reports, key=lambda path: path.stat().st_mtime)\nreport = json.loads(latest.read_text())\nprint(report["version"], report["status"])\nfor step in report["steps"]:\n    print(step["cairn"], step["label"], step.get("returncode", "unfinished"))\nPY'),
    h('Other outputs'), p('The initialization product consists of editable plan/setup/parameter files and the sample intent, described in the step-by-step guide. --print-config writes effective configuration and selected steps as JSON to stdout; it is not a run report. Child-generated products are outside the runner schema. No automatic stage copying, scientific plots or release archives are produced by a pipeline run.'))

nav = [('index', 'Documentation home'), ('README', 'Overview'), ('astro-pipeline-step-by-step', 'Step-by-step'), ('pipeline-plan-run', 'Command reference'), ('astro-pipeline-configuration', 'Configuration'), ('astro-pipeline-plan-syntax', 'Plan syntax'), ('astro-pipeline-product-report', 'Run reports')]
for key, (title, subtitle, blocks) in PAGES.items():
    links = ''.join(f'<a href="{name}.html"'+(' aria-current="page"' if name == key else '')+f'>{escape(label)}</a>' for name,label in nav)
    body = []
    text = [title, STAMP, subtitle, '', 'Documentation Tree', *[f'{label}: {name}.txt' for name,label in nav], '']
    for kind, value in blocks:
        if kind == 'table':
            headers, rows = value
            body.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>')
            text += [' | '.join(headers), *[' | '.join(row) for row in rows], '']
        elif kind == 'code':
            body.append('<pre><code>'+escape(value)+'</code></pre>')
            text += [value, '']
        else:
            body.append(f'<{kind}>'+escape(value)+f'</{kind}>')
            text += [value, '']
    html = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+escape(title)+' · astro-pipeline</title><link rel="stylesheet" href="style.css"></head><body><a class="skip" href="#content">Skip to content</a><header><p class="eyebrow">ASTRO-PIPELINE / USER GUIDE</p><h1>'+escape(title)+'</h1><p class="subtitle">'+escape(subtitle)+'</p><p class="version">'+escape(STAMP)+'</p></header><nav aria-label="Documentation Tree">'+links+'</nav><main id="content">'+''.join(body)+'</main><footer><a href="'+key+'.txt">Plain-text version</a> · <a href="astro-pipeline-step-by-step.html">Step-by-step guide</a> · <a href="astro-pipeline-product-report.html">Product formats</a><p>Offline documentation · '+escape(STAMP)+'</p></footer></body></html>\n'
    (DOCS / (key+'.html')).write_text(html, encoding='utf-8')
    (DOCS / (key+'.txt')).write_text('\n'.join(text).rstrip()+'\n', encoding='utf-8')
print(f'Generated {len(PAGES)} HTML/TXT pairs for {VERSION}')

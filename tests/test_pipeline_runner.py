"""End-to-end checks using disposable CLI intents; no observation data needed."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "script/pipeline-plan-run"


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pipeline tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.work = self.base / "work with spaces"
        self.call("--init", str(self.work))
        self.setup = self.work / "pipeline-setup.json"
        self.plan = self.work / "pipeline.plan"

    def call(self, *args, expected=0, cwd=None):
        result = subprocess.run([sys.executable, str(RUNNER), *args],
                                cwd=cwd or self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def run_plan(self, *args, expected=0):
        return self.call("--setup-file", str(self.setup), *args, expected=expected)

    def configure(self, **values):
        data = json.loads(self.setup.read_text())
        data.update(values)
        self.setup.write_text(json.dumps(data))

    def probe(self, name="probe.py", content=None):
        path = self.work / "intents" / name
        path.write_text(content or 'import json, sys\nprint(json.dumps(sys.argv[1:]))\n')
        return path

    def test_sample_first_run_and_refuse_overwrite(self):
        first = self.base / "first run"
        first.mkdir()
        self.call(cwd=first)
        self.assertTrue((first / "pipeline.plan").exists())
        original = (first / "pipeline.plan").read_text()
        self.call(cwd=first, expected=2)
        self.assertEqual(original, (first / "pipeline.plan").read_text())
        output = self.run_plan().stdout
        self.assertIn("HELLO FROM ASTRO-PIPELINE", output)
        reports = list((self.work / "output").glob("run-*/report.json"))
        report = json.loads(reports[0].read_text())
        self.assertEqual(report["status"], "completed")
        self.assertEqual(len(report["steps"]), 2)
        self.assertEqual(report["steps"][0]["returncode"], 0)

    def test_preview_and_print_config_have_no_output(self):
        self.run_plan("--dry-run")
        self.run_plan("--list")
        cfg = json.loads(self.run_plan("--print-config").stdout)
        self.assertEqual(cfg["workdir"], str(self.work))
        self.assertEqual(cfg["steps"][0]["args"], ["--count", "1", "--message", "Hello from astro-pipeline", "--uppercase"])
        self.assertFalse((self.work / "output").exists())

    def test_version_history_reports_only_current_release(self):
        checkout = self.base / "version history checkout"
        (checkout / "script").mkdir(parents=True)
        (checkout / "version").mkdir()
        shutil.copy2(RUNNER, checkout / "script/pipeline-plan-run")
        (checkout / "version/VERSION").write_text("0.1.1\n0.1.0\n")
        runner = [sys.executable, str(checkout / "script/pipeline-plan-run")]
        result = subprocess.run(runner + ["--version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "0.1.1\n")
        result = subprocess.run(runner + ["--setup-file", str(self.setup)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(next((self.work / "output").glob("run-*/report.json")).read_text())
        self.assertEqual(report["version"], "0.1.1")

    def test_arbitrary_cli_values_and_no_shell_evaluation(self):
        self.probe()
        self.plan.write_text('''intent: probe
flag: true
disabled: false
zero: 0
empty: ""
values: []
skip: null
text: "a # quoted comment; $(touch INJECTED)"
-x: "short option"
options: {"label": "real cli option"}
args: ["--", "positional input"]
end
''')
        cfg = json.loads(self.run_plan("--print-config").stdout)
        argv = cfg["steps"][0]["args"]
        self.assertIn("--disabled=false", argv)
        self.assertIn("0", argv)
        self.assertIn("", argv)
        self.assertIn("--values", argv)
        self.assertNotIn("--skip", argv)
        self.assertIn("a # quoted comment; $(touch INJECTED)", argv)
        self.run_plan()
        self.assertFalse((self.work / "INJECTED").exists())

    def test_parameter_replacement_and_cli_overrides(self):
        self.probe()
        self.plan.write_text("intent: probe\nmessage: ${message}\nend\n")
        params = self.work / "pipeline-parameters.json"
        params.write_text(json.dumps({"schema_version": 1, "parameters": {"variables": {"message": "old"}, "defaults": {"old": 1}, "continue_on_error": True}}))
        alternate = self.base / "override.json"
        alternate.write_text(json.dumps({"schema_version": 1, "parameters": {"variables": {"message": "new"}, "continue_on_error": True}}))
        config = json.loads(self.run_plan("--parameter-file", str(alternate), "--no-continue-on-error", "--output-path", "new output", "--print-config").stdout)
        self.assertEqual(config["steps"][0]["args"], ["--message", "new"])
        self.assertFalse(config["continue_on_error"])
        self.assertEqual(config["output_path"], str(self.base / "new output"))

    def test_loops_repeats_disabled_and_cairn_selection(self):
        self.probe()
        self.plan.write_text('''loop: 2
cairn: 4
intent: probe
iter: 2
end
cairn: 7
intent: missing-disabled
use: false
end
loop: end
cairn: 10
intent: probe
end
''')
        config = json.loads(self.run_plan("-c", "[4-7]", "--print-config").stdout)
        self.assertEqual([s["cairn"] for s in config["steps"]], [4, 4, 4, 4])
        config = json.loads(self.run_plan("--only", "10", "--print-config").stdout)
        self.assertEqual(len(config["steps"]), 1)
        self.run_plan("-c", "99", "--dry-run", expected=2)

    def test_python_native_executable_and_path_resolution(self):
        native = self.probe("native", '#!/bin/sh\nprintf "native executable\\n"\n')
        native.chmod(0o755)
        self.plan.write_text("intent: native\nend\n")
        self.assertIn("native executable", self.run_plan().stdout)
        self.configure(intent_paths=[str(native)], allow_path=False)
        self.run_plan()
        self.configure(intent_paths=[], allow_path=True)
        self.plan.write_text("intent: " + Path(sys.executable).name + '\nargs: ["-c", "print(42)"]\nend\n')
        self.assertIn("42", self.run_plan().stdout)
        self.configure(allow_path=False)
        self.run_plan(expected=2)

    def test_intent_search_precedence_and_ambiguous_extensions(self):
        self.probe("probe.py")
        self.probe("probe.cpp", "int main() { return 0; }")
        self.plan.write_text("intent: probe\nend\n")
        self.run_plan("--dry-run", expected=2)
        self.plan.write_text("intent: probe.py\nend\n")
        self.run_plan("--dry-run")
        elsewhere = self.base / "other intents"
        elsewhere.mkdir()
        (elsewhere / "probe.py").write_text("print('second')")
        cfg = json.loads(self.run_plan("--intent-path", str(elsewhere), "--print-config").stdout)
        self.assertEqual(cfg["steps"][0]["path"], str(elsewhere / "probe.py"))

    def test_python_virtual_environment_is_preserved(self):
        environment = self.base / "python environment"
        venv.EnvBuilder(with_pip=False, symlinks=True).create(environment)
        interpreter = environment / "bin/python"
        self.probe("environment.py", "import sys\nprint('PREFIX=' + sys.prefix)\n")
        self.plan.write_text("intent: environment\nend\n")
        result = self.run_plan("--python-executable", str(interpreter))
        self.assertIn("PREFIX=" + str(environment), result.stdout)

    @unittest.skipUnless(shutil.which("c++"), "C++ compiler unavailable")
    def test_cpp_compilation_execution_and_compile_failure(self):
        self.probe("hello.cpp", '#include <iostream>\nint main(int argc, char** argv) { std::cout << argv[1] << "\\n"; return 0; }\n')
        self.plan.write_text('intent: hello\nargs: ["C++ works"]\nend\n')
        self.run_plan("--dry-run")
        self.assertFalse((self.work / "output").exists())
        self.assertIn("C++ works", self.run_plan().stdout)
        self.probe("hello.cpp", "invalid c++")
        self.run_plan(expected=1)
        reports = [json.loads(p.read_text()) for p in (self.work / "output").glob("run-*/report.json")]
        self.assertEqual({r["status"] for r in reports}, {"completed", "failed"})

    def test_stop_failure_and_continue_failure_reports(self):
        self.probe("fail.py", "raise SystemExit(7)\n")
        self.probe("after.py", 'from pathlib import Path\nPath("after").touch()\n')
        self.plan.write_text("intent: fail\nend\nintent: after\nend\n")
        self.run_plan(expected=1)
        self.assertFalse((self.work / "after").exists())
        self.run_plan("--continue-on-error", expected=1)
        self.assertTrue((self.work / "after").exists())
        reports = [json.loads(p.read_text()) for p in (self.work / "output").glob("run-*/report.json")]
        self.assertTrue(all(r["status"] == "failed" for r in reports))
        self.assertEqual(sorted(len(r["steps"]) for r in reports), [1, 2])
        self.assertTrue(all(r["steps"][0]["returncode"] == 7 for r in reports))

    def test_preflight_prevents_partial_execution(self):
        self.probe("first.py", 'from pathlib import Path\nPath("started").touch()\n')
        self.plan.write_text("intent: first\nend\nintent: nonexistent\nend\n")
        self.run_plan(expected=2)
        self.assertFalse((self.work / "started").exists())
        self.assertFalse((self.work / "output").exists())

    def test_invalid_plans(self):
        for content in ("intent: echo-message\n", "unknown: x\n", "loop: 2\n", "cairn: 0\n", "intent: echo-message\nmessage: ${missing}\nend\n", "variables:\na: ${b}\nb: ${a}\nend\nintent: echo-message\nmessage: ${a}\nend\n", "intent: echo-message\niter: false\nend\n"):
            with self.subTest(content=content):
                self.plan.write_text(content)
                self.run_plan("--dry-run", expected=2)

    def test_invalid_json_configuration(self):
        original = self.setup.read_text()
        for change in ({"schema_version": True}, {"unknown": 1}, {"intent_paths": "bad"}, {"allow_path": 1}, {"cxx_flags": "-O2"}, {"workdir": "missing"}):
            with self.subTest(change=change):
                self.setup.write_text(original)
                self.configure(**change)
                self.run_plan("--print-config", expected=2)
        self.setup.write_text('{"schema_version":1,"schema_version":1}')
        self.run_plan(expected=2)

    def test_installed_command_outside_checkout_and_collision(self):
        prefix = self.base / "install with spaces"
        command = [sys.executable, str(ROOT / "script/install"), "--prefix", str(prefix)]
        subprocess.run(command, check=True, capture_output=True)
        subprocess.run(command, check=True, capture_output=True)
        launcher = prefix / "bin/pipeline-plan-run"
        result = subprocess.run([str(launcher), "--setup-file", str(self.setup), "--dry-run"], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        subprocess.run(command + ["--uninstall"], check=True, capture_output=True)
        launcher.write_text("unrelated command")
        result = subprocess.run(command, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(launcher.read_text(), "unrelated command")


if __name__ == "__main__":
    unittest.main()

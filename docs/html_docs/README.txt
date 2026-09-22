Overview
Version 0.1.1 · Generated 2026-09-21
Run Python scripts, C++ programs, and other command-line tools as ordered intents.

Documentation Tree
Documentation home: index.txt
Overview: README.txt
Step-by-step: astro-pipeline-step-by-step.txt
Command reference: pipeline-plan-run.txt
Configuration: astro-pipeline-configuration.txt
Plan syntax: astro-pipeline-plan-syntax.txt
Run reports: astro-pipeline-product-report.txt

Purpose and requirements

pipeline-plan-run uses GMRTCAL-style intent blocks but has no GMRTCAL, CASA, or astronomy-library dependency. It requires Python 3.9+ and the standard library. Single-file C++ source intents additionally require a C++ compiler. Other languages work through an executable CLI or an explicit interpreter intent.

Install

git clone https://github.com/prasundutta151/astro-pipeline.git
cd astro-pipeline
python3 script/install
export PATH="$HOME/.local/bin:$PATH"
pipeline-plan-run --version

The installer records this checkout and the selected Python interpreter in ~/.local/bin/pipeline-plan-run. No shell configuration files are changed. To choose another prefix use python3 script/install --prefix DIRECTORY. Repeat installation after moving the checkout. Uninstall with python3 script/install --uninstall, including the same --prefix if customized. Existing unrelated commands are refused.

Create a runnable example

pipeline-plan-run --init ./my-pipeline
pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json --dry-run
pipeline-plan-run --setup-file ./my-pipeline/pipeline-setup.json

A no-argument invocation also initializes the current directory and exits. Initialization refuses existing target files. It creates pipeline.plan, pipeline-setup.json, pipeline-parameters.json and intents/echo-message.py. The sample CLI only prints messages; replace its intent paths and options with your own.

Execution model

All enabled selected intents are resolved before execution. Commands run sequentially in workdir, with live stdout/stderr. By default a failed command or C++ build stops the run. --continue-on-error attempts later steps but the overall exit remains nonzero. Each execution creates a unique report directory, preserving previous reports. Child output files and overwrite behavior are controlled by the child CLI itself.

Scientific scope

The runner does not prescribe physical units, coordinates, time scales for observations, calibration, missing-data treatment, random seeds or scientific algorithms. These belong to each intent and its inputs. It records commands and hashes of the plan and executable/source files, not external dependency versions or input-data hashes. No convergence-based loops or GMRTCAL science aliases are implemented.

Validation

python3 -m unittest discover -s tests -v

Release validation: 18 tests passed, including actual C++ compilation, Python virtual environments, paths with spaces, configuration precedence, failure handling and version-history regression coverage. No observation data were required.

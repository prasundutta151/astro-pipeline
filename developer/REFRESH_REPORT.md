# REFRESH REPORT - astro-pipeline

**Status:** In Progress
**Session ID:** N/A (No PROJECT_SETUP_REFRESH_SESSION)
**Host:** darwin

## 1. Migration Plan & Mapping

### Current Layout vs. Reference Template
| Feature | Current State (astro-pipeline) | Target State (project-setup template) | Action Required |
| :--- | :--- | :--- | :--- |
| **Version** | `VERSION` (root) | `version/VERSION` | Move root `VERSION` to `version/` |
| **Scripts** | `script/` (root) | `script/` | Verify compatibility of entry points |
| **Docs** | `docs/` (root) | `docs/` | Ensure on-demand contract is present |
| **Pipeline** | `pipeline/` (root) | `pipeline/` | Verify configuration compatibility |
| **JSON** | `json/` (root) | `json/` | Verify configuration compatibility |
| **Plot** | `plot/` (root) | `plot/` | Verify compatibility |
| **Developer** | `developer/` (root) | `developer/` | Merge project-specific rules with template |
| **Tests** | `tests/` (root) | `tests/` | Verify existing test suite |

### 2. Preserved Items
*   All scientific logic and data structures in `pipeline/` and `json/`.
*   Existing Git history (Baseline: `8d50929`).
*   User-provided documentation in `docs/`.

### 3. Migration Steps (Planned)
1.  **Version Migration:** Move `VERSION` to `version/VERSION`. Handle macOS case-insensitivity collision.
2.  **Developer Rules Merge:** Integrate `developer/AGENT_RULES.md` and `DEV_NOTES.md` with template standards.
3.  **Lock/Context Adaptation:** Update `agent_context.py` and `agent_lock.py` to match new project-setup standards.
4.  **Documentation Contract:** Ensure `documentation-prompt.txt` and related files are correctly placed for on-demand generation.
5.  **Validation:** Run `test_agent_context.py` and `test_pipeline_runner.py`.

## 4. Blockers / Conflicts
*   None identified at this stage.

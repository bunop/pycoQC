# Uplift notes: pycoQC 3.0.0 (Phases 1 to 5 done; independent verification pending)

Working copy of `legacy/pycoQC` 2.5.2. Target: Python 3.14, numpy 2.5.5, pandas 3.1.1, plotly 7.2.0 (see `analysis/pycoQC/DELTA_CATALOG.md`). Proof: dual run, oracle Python 3.11 versus target Python 3.14 (`analysis/pycoQC/harness/`), baseline in `analysis/pycoQC/BASELINE.md`. Playbook: `analysis/pycoQC/PLAYBOOK.md`.

## Delta-to-fix mapping (so far)
| Delta | Fix | Where | Tool |
|---|---|---|---|
| DELTA-012 (in `common`) | `inplace=True` replaced by reassignment | `pycoQC/common.py` lines 64, 75, 79 | by hand |
| DELTA-006 | chained `inplace` on `df['barcode']` replaced by reassignment | `pycoQC/pycoQC_parse.py:166, 234` | by hand |
| DELTA-012 | `reset_index(inplace=True)` replaced by reassignment | `pycoQC/pycoQC_parse.py:211, 221` | by hand |
| DELTA-007 | storage stays float32; histogram and time-bin edges computed in float64 (9 `float(...)` wraps) | `pycoQC/pycoQC_plot.py` (histogram helpers, 2D density, three time-bin sites) | by hand |
| DELTA-001 | `pkg_resources.resource_filename` replaced by `importlib.resources.files` | `pycoQC/pycoQC_report.py`, `pycoQC/__main__.py` | by hand |
| DELTA-002 | `show_link=False` removed from `py.plot` | `pycoQC/pycoQC_report.py` | by hand |
| DELTA-003 | CDN script pinned to plotly.js 4.1.1 (the version plotly 7.2.0 writes data for) | `pycoQC/templates/spectre.html.j2` | by hand |
| SEC-001/002 | autoescape on; plots and source list as `Markup`; file names escaped | `pycoQC/pycoQC_report.py` | by hand (owner-approved) |
| SEC-002 (custom template) | `jinja2.Environment(FileSystemLoader, autoescape=True)` | `pycoQC/pycoQC_report.py` | by hand |
| SEC-003 | spectre.css pinned to 0.5.9; SRI hashes on spectre and plotly.js 4.1.1 tags | `pycoQC/templates/spectre.html.j2` | by hand |
| SEC-006 | barcode label sanitized in the output file name, collisions are an error | `pycoQC/Barcode_split.py` | by hand |
| SEC-007 | unreadable fast5 skipped with a warning (opens each file once to probe; only `OSError`, a readable HDF5 file without the expected groups still fails the run) | `pycoQC/Fast5_to_seq_summary.py` | by hand |
| SEC-012/013 | test that plotly escapes `</script` and `<!--`; workflow `permissions: contents: read`, actions pinned by SHA | `tests/test_security.py`, `.github/workflows/tests.yml` | by hand |
| owner-approved fixes | CLI exit 1 on usage errors; `parse_args(args)`; bad config/template raises; unknown plot key warns; `AttributeError` in a plot propagates; template loaded first | `pycoQC/__main__.py`, `pycoQC/pycoQC_report.py` | by hand |
| DELTA-007 (late) | `run_duration` divided in float64 | `pycoQC/pycoQC_plot.py:128` | by hand |
| DELTA-009/010 | version 3.0.0, `python_requires >=3.12`, tested-minor to next-major pins, `markupsafe` declared, classifiers, docs | `setup.py`, `meta.yaml`, `pycoQC/__init__.py`, `versipy.yaml`, `deploy_anaconda.sh`, `README.md`, `docs/` | by hand |
| tests and CI | 35 characterization and behavior tests; GitHub Actions workflow (3.12, 3.14) | `tests/`, `.github/workflows/tests.yml` | new files |
| DELTA-004 | `np.int` replaced by `int` (channel plot restored) | `pycoQC/pycoQC_plot.py:1427` | by hand |
| DELTA-005 | `.values.copy()` before the in-place sort | `pycoQC/pycoQC_plot.py:_compute_N50` | by hand |
| RULE-002 | standard N50: sort descending (owner decision; separate commit) | `pycoQC/pycoQC_plot.py:_compute_N50` | by hand |
| DELTA-008 | none needed: fixed by the float64 bin edges (hover labels identical to the oracle) | n/a | n/a |
| DELTA-011 | no code change; main-guard note added | `docs/Fast5_to_seq_summary/usage.md` | by hand |

## Dual-run diff (Phase 1)
Unit `common`: helper digest `a38779d655e832db` on both interpreters, no warnings on the target after the edit (before: 3 `Pandas4Warning`).
Full case list (16 cases at `sample=100000`, target versus oracle): 1 identical (`fast5_to_seq_summary`), 15 differ for reasons that belong to later phases: 14 report cases fail on `pkg_resources` (DELTA-001, Phase 4) and `barcode_split` writes an extra file (DELTA-006, Phase 2). `analysis/pycoQC/baseline/compare_phase1_s100000.txt`.

## Dual-run diff (Phase 2)
`harness/parse_check.py` on the oracle (Python 3.11) versus the working copy on the target (Python 3.14): 17 cases, 17 identical (counters, barcode value counts, shapes, numeric sums within 1e-6, alignment tables), 0 warnings. `Barcode_split`: 8 files, identical hashes. `Fast5_to_seq_summary`: 22 rows, identical hash. Negative control on the seed: 3 differ.
Float decision measured with a scratch shim over all 16 cases: float32 storage as-is left one case different, float64 storage left another one-read difference, float32 storage with float64 bin edges matched all 16 at both sample sizes. Phase 2 therefore leaves line 333 unchanged and Phase 3 makes the bin-edge edits.

## Dual-run diff (Phase 3)
Figure level (`plot_check.py`): 105 plots, 0 differ from the oracle (47 identical `pycoQCError` gates). Contract tests (`rules_check.py`): RULE-001 50/50, RULE-002 20/20 equal to the standard N50, RULE-003 400/400 aligned reads. Full reports on a scratch shim copy (only the Phase 4 edits added): 16/16 cases identical at `sample=100000` and `sample=1000` after commit (a); 16/16 after the N50 commit, with and without ignoring N50 fields. The N50 correction changes no value on the sample data.

Review: the architecture critic found one redundant edit (hover wrapper, removed) and one simplification (`.tolist()`, taken). Final proof on the committed code is as above.

## Dual-run diff (Phase 4)
All 16 report cases run directly on this working copy on Python 3.14: identical to the oracle at `sample=100000` and `sample=1000` (with and without N50 fields), no warnings. `harness/report_check.py`: 14/14 (the same script fails 13 on the legacy code). Headless Chrome draws 9/9 charts, 30 trace groups, 1 heatmap image, equal to the oracle's report; with the old CDN line it draws 16 trace groups and no heatmap. `--default_config` output byte-identical to the legacy file.

## Dual-run diff (Phase 5, final)
Strict zero-tolerance comparison of all JSON statistics against the oracle: 14 files, 18,150 values, 0 differences, on Python 3.12 and 3.14, at `sample=100000` and `sample=1000`, and from the installed wheel. Plots 105/105, parser 17/17, P0 rule tests 50/20/400, report checks 14/14 (headless Chrome 9/9 charts, 30 trace groups). `pytest tests`: 35/35 on 3.12 and 3.14 from a fresh `pip install ".[test]"` (the resolver picked numpy 2.5.5, scipy 1.18.1, pandas 3.1.1, plotly 7.2.0, jinja2 3.1.6, markupsafe 3.0.4, h5py 3.16.0, tqdm 4.70.1, pysam 0.24.1). The same tests fail 13 and pass 22 on the legacy code.

## Behavior changes (listed in CHANGELOG.md; decided by the owner, 2026-11-25)
1. Standard N50 (no change on any sample file; differs on small or lumpy inputs).
2. HTML reports escape markup in titles, file names and labels (they were raw before); a `</script>` in a barcode label no longer injects markup.
3. The report loads plotly.js 4.1.1 from the CDN instead of the frozen `plotly-latest` (1.58.5).
4. `pycoQC` exits 1 (not 0) when `--summary_file` or an output file is missing; the `main_*` entry points honor their `args`.
5. A bad `--config_file` or `--template_file` is an error (it used to fall back silently); an unknown plot key warns; an `AttributeError` inside a plot method is no longer swallowed.
6. Requires Python 3.12 or later with numpy 2.5, pandas 3.1 and plotly 7.2 (see the pins in `setup.py`).

## Residual and deferred
- DELTA-013 (`open()` without an encoding, `common.py:267`): pre-existing, not needed on the target, deferred.
- `check_arg` bound test `if min and ...` (RULE-032): a known bug, not in this pass until the brief's open question is ticked.
- Deferred bug fixes: negative bounds (`if min and ...`), Fast5 single-file and bare-filename rejection, the calibration filter dropping empty values uncounted, the `Suplementary` label, the `+1` channel baseline (RULE-020), `read_text()` without `encoding=` (DELTA-013), unused imports in `__main__.py`.
- Not proven here: the conda recipe was edited, not built; the GitHub Actions workflow has not run on GitHub; Python 3.13 not run; `.travis.yml` left untouched (dead service; its release steps are out of scope).
- A `hasattr` precheck lets non-plot attributes (`_run_duration`, `summary_stats_dict`) through; they raise `TypeError` as before.
- `sequencing_summary_file_sample` has no callers in the package and an unseeded sample (RULE-048): untouched.

## Per unit
| Unit | Builds on target | Reproduces baseline |
|---|---|---|
| `common` | yes (imports and all helpers run) | yes (helper digest equal) |
| `pycoQC_parse` | yes | yes (17/17 parser cases) |
| `Barcode_split` | yes | yes (file list and hashes) |
| `Fast5_to_seq_summary` | yes | yes (rows and hash) |
| `pycoQC_plot` | yes | yes (105 plots; 16/16 reports) |
| `pycoQC_report`, `pycoQC`, `__main__` | yes | yes (16/16 reports, 14/14 report checks, headless browser) |
| packaging (`setup.py`, `meta.yaml`, docs) | wheel and sdist build; fresh install on 3.12 and 3.14 | yes (strict compare from the installed wheel) |

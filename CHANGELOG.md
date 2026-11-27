# pycoQC Changelog

### 3.0.0 (uplift to Python 3.12+)

Runs on Python 3.12 to 3.14 with numpy 2.5, scipy 1.18, pandas 3.1, plotly 7.2, jinja2 3.1, h5py 3.16 and pysam 0.24. Use pycoQC 2.5.2 for Python 3.6 to 3.11.
Verified against the 2.5.2 results on the sample data (identical JSON statistics, plot lists, barcode counts and `Barcode_split`/`Fast5_to_seq_summary` outputs).

* Fix: `pkg_resources` is no longer used, so the package imports on current Python
* Fix: the "Channel activity over time" plot was silently dropped on numpy 1.24 and later (`np.int`)
* Fix: reads missing from a barcode file were left without a label, and Deepbinner `none` labels were kept, on pandas 3 (chained `inplace` writes)
* Fix: histogram and time-bin edges are computed in float64 so results do not depend on the numpy version
* Fix: N50 is the standard N50 (longest reads first). Same value on the sample files; differs only on small or irregular read length sets
* Change: HTML reports escape markup in titles, file names and barcode labels (a `</script>` in a barcode label can no longer inject markup into the report)
* Fix: `Barcode_split` writes each barcode to a file whose name keeps only letters, digits, `.`, `_` and `-` (other characters become `_`, with a warning), so a barcode label cannot point outside the output folder; two labels that end up with the same file name are an error
* Fix: `Fast5_to_seq_summary` skips a fast5 file that cannot be opened (with a warning) instead of stopping the whole run; it still fails if no file at all can be read
* Change: a custom `--template_file` is autoescaped like the default template; a template that printed HTML from a variable must mark it with `|safe`
* Change: reports load plotly.js 4.1.1 (the version plotly 7.2 writes data for) instead of the frozen `plotly-latest` (1.58.5); the plotly and spectre.css files are pinned to an exact version with a Subresource Integrity hash
* Change: `pycoQC` exits with status 1 when `--summary_file` or an output file is missing; the three command line entry points honor their `args` argument
* Change: an explicitly given `--config_file` or `--template_file` that cannot be used is an error (it used to fall back silently to the default); a plot name in the config with no matching method is skipped with a warning; an `AttributeError` raised inside a plot method is no longer swallowed
* Change: scripts that call `Fast5_to_seq_summary` must use an `if __name__ == "__main__":` guard on Python 3.14 (workers start with `forkserver`)
* Add: a `tests/` directory of characterization tests and a GitHub Actions workflow

### 11/10/2019 v-2.5.0.17

* Style update to comply with codacity
* Update summary table functions and split into 3 Run, Basecall and align

### 11/10/2019 v-2.5.0.14

* Add min_pass_len option to specify a minimal read length to be "pass"
* Update pycoQC usage doc and fix notebooks broken links

### 10/10/2019 v-2.5.0.12

* Start documenting changelog
* Change alignment score for identity frequency
* Reorganise documentation directory
* File names in HTML reports are now absolute paths
* Fix errors in Fast5_to_seq_summary

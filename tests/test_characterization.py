"""Characterization tests: the results of pycoQC 2.5.2 (Python 3.11, numpy 1.23, pandas 1.5, plotly 4.1.0) on the sample data in docs/,
recorded before the uplift to Python 3.12+. The expected files in tests/expected/ are those recorded outputs, unchanged."""
import hashlib, json, os, re
import pytest
from conftest import *
from pycoQC.pycoQC import pycoQC
from pycoQC.Barcode_split import Barcode_split
from pycoQC.Fast5_to_seq_summary import Fast5_to_seq_summary

CASES = {
    "Albacore-1.2.3_basecall-1D-RNA_sequencing_summary": dict(summary_file=[os.path.join(SUMMARY_DIR, "Albacore-1.2.3_basecall-1D-RNA_sequencing_summary.txt.gz")]),
    "Albacore-1.7.0_basecall-1D-DNA_sequencing_summary": dict(summary_file=[os.path.join(SUMMARY_DIR, "Albacore-1.7.0_basecall-1D-DNA_sequencing_summary.txt.gz")]),
    "Guppy-2.1.3_basecall-1D-DNA_sequencing_summary": dict(summary_file=[GUPPY213]),
    "Guppy-2.1.3_basecall-1D-RNA_sequencing_summary": dict(summary_file=[os.path.join(SUMMARY_DIR, "Guppy-2.1.3_basecall-1D-RNA_sequencing_summary.txt.gz")]),
    "Guppy-2.2.4-basecall-1D-DNA_sequencing_summary+barcode": dict(summary_file=[os.path.join(SUMMARY_DIR, "Guppy-2.2.4-basecall-1D-DNA_sequencing_summary+barcode.txt.gz")]),
    "barcode_guppy213_pair": dict(summary_file=[GUPPY213], barcode_file=[os.path.join(SUMMARY_DIR, "Guppy-2.1.3_basecall-1D_DNA_barcoding_summary.txt.gz")]),
    "barcode_deepbinner": dict(summary_file=[SPLIT_SUMMARY], barcode_file=[DEEPBINNER], min_barcode_percent=0),
    "barcode_partial": dict(summary_file=[SPLIT_SUMMARY], barcode_file=[os.path.join(DATA, "partial_barcode.txt.gz")], min_barcode_percent=0),
    "bam_clean": dict(summary_file=[GUPPY213], bam_file=[os.path.join(DATA, "clean.sorted.bam")]),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_statistics_match_recorded_results(name, tmp_path):
    out = str(tmp_path / "stats.json")
    pycoQC(json_outfile=out, quiet=True, **CASES[name])
    assert json_differences(json.load(open(os.path.join(EXPECTED, name + ".json"))), json.load(open(out))) == []


@pytest.mark.parametrize("name", ["Guppy-2.1.3_basecall-1D-DNA_sequencing_summary", "bam_clean", "barcode_deepbinner"])
def test_html_report_has_the_recorded_plots(name, tmp_path, other_expected):
    out = str(tmp_path / "report.html")
    pycoQC(html_outfile=out, quiet=True, **CASES[name])
    html = open(out, encoding="utf-8").read()
    assert re.findall(r'<div id="([^"]+)" class="column col-11', html) == other_expected["plot_lists"][name]
    assert "plotly-4.1.1.min.js" in html


def test_barcode_split_writes_the_recorded_files(tmp_path, other_expected):
    Barcode_split(summary_file=SPLIT_SUMMARY, barcode_file=DEEPBINNER, output_dir=str(tmp_path), quiet=True)
    got = {f: hashlib.sha256(open(tmp_path / f, "rb").read()).hexdigest()[:16] for f in sorted(os.listdir(tmp_path))}
    assert got == other_expected["barcode_split_files"]


def test_fast5_to_seq_summary_matches_recorded_output(tmp_path, other_expected):
    out = str(tmp_path / "summary.tsv")
    Fast5_to_seq_summary(fast5_dir=FAST5_DIR, seq_summary_fn=out, threads=4, verbose_level=0)
    lines = open(out).read().splitlines()
    exp = other_expected["fast5"]
    assert lines[0] == exp["header"] and len(lines) - 1 == exp["rows"]
    assert hashlib.sha256("\n".join(sorted(lines[1:])).encode()).hexdigest()[:16] == exp["sorted_rows_sha"]

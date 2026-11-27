"""SEC-002, SEC-006, SEC-007, SEC-012: hostile or broken input must not escape the output folder, stop a batch or inject markup."""
import gzip, os, shutil
import pytest
from conftest import SPLIT_DIR, FAST5_DIR, GUPPY213, SPLIT_SUMMARY, DEEPBINNER
from pycoQC.Barcode_split import Barcode_split
from pycoQC.Fast5_to_seq_summary import Fast5_to_seq_summary
from pycoQC.common import pycoQCError
from pycoQC.pycoQC import pycoQC


def _barcodes_with(tmp_path, labels):
    """Copy the deepbinner file, giving the first reads of each label the labels in turn."""
    out = tmp_path / "barcodes.txt.gz"
    with gzip.open(DEEPBINNER, "rt") as f, gzip.open(out, "wt") as g:
        head = f.readline(); g.write(head); k = head.rstrip("\n").split("\t").index("barcode_call")
        for n, line in enumerate(f):
            p = line.rstrip("\n").split("\t"); p[k] = labels[n % len(labels)]
            g.write("\t".join(p) + "\n")
    return str(out)


def test_sec006_barcode_label_with_path_characters_stays_in_the_output_folder(tmp_path):
    out = tmp_path / "out"; out.mkdir()
    (tmp_path / "sequencing_summary_a").mkdir()  # the directory that made the old code write outside
    Barcode_split(summary_file=SPLIT_SUMMARY, barcode_file=_barcodes_with(tmp_path, ["a/../../escaped", "barcode01"]),
                  output_dir=str(out), min_barcode_percent=0, quiet=True)
    assert sorted(os.listdir(tmp_path)) == ["barcodes.txt.gz", "out", "sequencing_summary_a"]
    assert not any(os.scandir(tmp_path / "sequencing_summary_a"))
    names = os.listdir(out)
    assert "sequencing_summary_a_.._.._escaped.txt" in names and "sequencing_summary_barcode01.txt" in names


def test_sec006_two_labels_that_collapse_to_one_file_name_are_an_error(tmp_path):
    with pytest.raises(pycoQCError):
        Barcode_split(summary_file=SPLIT_SUMMARY, barcode_file=_barcodes_with(tmp_path, ["a/b", "a_b"]),
                      output_dir=str(tmp_path), min_barcode_percent=0, quiet=True)


def _fast5_dir(tmp_path, good, bad):
    d = tmp_path / "f5"; d.mkdir()
    for f in sorted(os.listdir(FAST5_DIR))[:good]:
        shutil.copy(os.path.join(FAST5_DIR, f), d)
    for i in range(bad):
        (d / "bad{}.fast5".format(i)).write_bytes(b"this is not an hdf5 file" * 10)
    return str(d)


def test_sec007_a_corrupt_fast5_is_skipped_and_the_rest_is_read(tmp_path):
    out = str(tmp_path / "s.tsv")
    Fast5_to_seq_summary(fast5_dir=_fast5_dir(tmp_path, 5, 1), seq_summary_fn=out, threads=3, verbose_level=0)
    assert len(open(out).read().splitlines()) - 1 == 5


def test_sec007_only_unreadable_fast5_files_is_still_an_error(tmp_path):
    with pytest.raises(pycoQCError):
        Fast5_to_seq_summary(fast5_dir=_fast5_dir(tmp_path, 0, 2), seq_summary_fn=str(tmp_path / "s.tsv"), threads=3, verbose_level=0)


def test_sec002_a_custom_template_is_autoescaped(tmp_path):
    tpl = tmp_path / "t.j2"; tpl.write_text("<h1>{{ report_title }}</h1>{% for p in plots %}{{ p }}{% endfor %}")
    out = tmp_path / "r.html"
    pycoQC(summary_file=[GUPPY213], html_outfile=str(out), template_file=str(tpl), report_title="<img src=x onerror=alert(1)>", quiet=True)
    html = out.read_text(encoding="utf-8")
    assert "<img src=x onerror" not in html and "&lt;img src=x onerror" in html
    assert "plotly-graph-div" in html  # the plots are still there


def test_sec012_plotly_escapes_script_and_comment_openers_in_figure_data():
    """The report wraps plotly's div in Markup, which is safe only while plotly itself escapes these."""
    import plotly.graph_objects as go, plotly.offline as py
    div = py.plot(go.Figure(go.Scatter(x=[1], y=[1], name="</script><!--<script>")), output_type="div", include_plotlyjs=False, auto_open=False)
    # the div has exactly one script block of its own; the hostile name must add neither a closer nor an opener
    assert div.count("<script") == 1 and div.count("</script") == 1 and "<!--" not in div

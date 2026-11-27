"""Report, API and command line behavior decided during the uplift (exit status, escaping, error handling)."""
import gzip, os
import pytest
from conftest import GUPPY213, SPLIT_DIR
from pycoQC.__main__ import main_pycoQC
from pycoQC.pycoQC import pycoQC
from pycoQC.common import pycoQCError
from pycoQC.pycoQC_plot import pycoQC_plot

HOSTILE = "</script><i id=POC>INJECTED</i><script>"


def test_default_config_is_printed(capsys):
    with pytest.raises(SystemExit):
        main_pycoQC(["--default_config"])
    assert '"run_summary"' in capsys.readouterr().out


@pytest.mark.parametrize("argv", [[], ["-f", GUPPY213]])
def test_missing_arguments_exit_with_status_1(argv):
    with pytest.raises(SystemExit) as e:
        main_pycoQC(argv)
    assert e.value.code == 1


def test_cli_honors_the_args_it_is_given(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["pycoQC", "--not-an-option"])
    out = tmp_path / "s.json"
    main_pycoQC(["-f", GUPPY213, "-j", str(out), "-q"])
    assert out.stat().st_size > 1000


def test_markup_in_labels_titles_and_file_names_is_escaped(tmp_path):
    barcodes = tmp_path / "barcodes.txt.gz"
    with gzip.open(os.path.join(SPLIT_DIR, "Guppy-basecall-1D-DNA_deepbinner_barcoding_summary.txt.gz"), "rt") as f, gzip.open(barcodes, "wt") as g:
        head = f.readline(); g.write(head); k = head.rstrip("\n").split("\t").index("barcode_call")
        for n, line in enumerate(f):
            p = line.rstrip("\n").split("\t")
            if n % 3 == 0:
                p[k] = HOSTILE
            g.write("\t".join(p) + "\n")
    summary = tmp_path / "<img src=x onerror=alert(1)>.txt.gz"
    summary.write_bytes(open(os.path.join(SPLIT_DIR, "Guppy-basecall-1D-DNA_sequencing_summary.txt.gz"), "rb").read())
    out = tmp_path / "r.html"
    pycoQC(summary_file=[str(summary)], barcode_file=[str(barcodes)], html_outfile=str(out), min_barcode_percent=0, report_title="<b onmouseover=x>T&C</b>", quiet=True)
    html = out.read_text(encoding="utf-8")
    assert "</script><i id=POC>" not in html
    assert "<b onmouseover=x>" not in html and "&lt;b onmouseover=x&gt;T&amp;C" in html
    assert "<img src=x onerror" not in html and "&lt;img src=x" in html


@pytest.mark.parametrize("kw", [dict(config_file="missing.json"), dict(template_file="missing.j2")])
def test_an_unusable_config_or_template_is_an_error(tmp_path, kw):
    kw = {k: str(tmp_path / v) for k, v in kw.items()}
    with pytest.raises(pycoQCError):
        pycoQC(summary_file=[GUPPY213], html_outfile=str(tmp_path / "x.html"), quiet=True, **kw)


def test_unknown_plot_name_is_skipped_and_plot_errors_are_not_swallowed(tmp_path, monkeypatch):
    import json
    cfg = tmp_path / "c.json"; cfg.write_text(json.dumps({"run_summary": {"plot_title": "Run summary"}, "no_such_plot": {"plot_title": "x"}}))
    out = tmp_path / "r.html"
    pycoQC(summary_file=[GUPPY213], html_outfile=str(out), config_file=str(cfg), quiet=True)
    assert "Run summary" in out.read_text(encoding="utf-8")

    def boom(self, *a, **k):
        raise AttributeError("bug inside a plot method")
    monkeypatch.setattr(pycoQC_plot, "read_len_1D", boom)
    with pytest.raises(AttributeError):
        pycoQC(summary_file=[GUPPY213], html_outfile=str(tmp_path / "y.html"), quiet=True)

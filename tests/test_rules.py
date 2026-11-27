"""Tests of the business rules confirmed or decided during the uplift (see analysis/BUSINESS_RULES.md of the uplift record)."""
import numpy as np, pandas as pd, pytest
from conftest import GUPPY213, DATA, SUMMARY_DIR
from pycoQC.pycoQC_parse import pycoQC_parse
from pycoQC.pycoQC_plot import pycoQC_plot
from pycoQC.common import check_arg, pycoQCError
import os


@pytest.fixture(scope="module")
def parsed():
    return pycoQC_parse(summary_file=[GUPPY213], quiet=True)


@pytest.mark.parametrize("quality,length", [(7, 0), (7.0, 1000), (10, 0), (0, 0), (12.5, 5000)])
def test_rule001_pass_reads_are_quality_and_length_at_or_above_threshold(parsed, quality, length):
    plot = pycoQC_plot(parser=parsed, min_pass_qual=quality, min_pass_len=length, sample=0, quiet=True)
    df = parsed.reads_df
    assert len(plot.pass_df) == int(((df["mean_qscore"] >= quality) & (df["read_len"] >= length)).sum())


def _summary_with(tmp_path, rows):
    """A sequencing summary (Guppy layout) whose reads have the given (mean quality, read length) pairs."""
    import gzip
    head = "filename\tread_id\trun_id\tchannel\tstart_time\tduration\tnum_events\tpasses_filtering\ttemplate_start\tnum_events_template\ttemplate_duration\tsequence_length_template\tmean_qscore_template\n"
    path = tmp_path / "boundary.txt.gz"
    with gzip.open(path, "wt") as fh:
        fh.write(head)
        for i, (q, n) in enumerate(rows):
            fh.write("f%d.fast5\tread%d\trunA\t%d\t%d\t1.0\t10\tTrue\t%d\t10\t1.0\t%d\t%s\n" % (i, i, 1 + i % 500, 10 * i, 10 * i, n, q))
    return str(path)


def test_rule001_the_pass_boundaries_are_inclusive_on_quality_and_on_length(tmp_path):
    """A read exactly at min_pass_qual and exactly at min_pass_len passes; one step below either fails."""
    rows = [(7.0, 1000), (6.9999, 1000), (7.0, 999), (7.5, 1000), (6.0, 5000), (12.0, 1000), (7.0, 1001)] + [(9.0, 2000)] * 5
    parser = pycoQC_parse(summary_file=[_summary_with(tmp_path, rows)], quiet=True)
    plot = pycoQC_plot(parser=parser, min_pass_qual=7.0, min_pass_len=1000, sample=0, quiet=True)
    assert sorted(plot.pass_df.index) == sorted(["read0", "read3", "read5", "read6"] + ["read%d" % i for i in range(7, 12)])
    assert not {"read1", "read2", "read4"} & set(plot.pass_df.index)


@pytest.mark.parametrize("lengths,standard", [([10, 20, 30], 30), ([1, 1, 1, 3], 3), ([10, 20, 30, 40], 30), ([5], 5)])
def test_rule002_n50_is_the_standard_longest_first_value(lengths, standard):
    assert pycoQC_plot._compute_N50(pd.Series(lengths, dtype="float64")) == standard


def test_rule002_n50_of_nothing_is_none():
    assert pycoQC_plot._compute_N50(pd.Series([], dtype="float64")) is None


def test_rule003_identity_is_aligned_length_minus_edit_distance_over_aligned_length():
    df = pycoQC_parse(summary_file=[GUPPY213], bam_file=[os.path.join(DATA, "clean.sorted.bam")], quiet=True).reads_df.dropna(subset=["identity_freq"])
    assert len(df) == 400
    expected = (df["align_len"] - (df["mismatch"] + df["insertion"] + df["deletion"])) / df["align_len"]
    assert np.allclose(df["identity_freq"].astype("float64"), expected.astype("float64"), atol=1e-6)


def test_barcode_labels_are_filled_and_deepbinner_none_becomes_unclassified():
    d = os.path.join(os.path.dirname(SUMMARY_DIR), "..", "Barcode_split", "data")
    p = pycoQC_parse(summary_file=[os.path.join(d, "Guppy-basecall-1D-DNA_sequencing_summary.txt.gz")],
                     barcode_file=[os.path.join(d, "Guppy-basecall-1D-DNA_deepbinner_barcoding_summary.txt.gz")], min_barcode_percent=0, quiet=True)
    counts = p.reads_df["barcode"].value_counts(dropna=False)
    assert "none" not in counts.index and not counts.index.isna().any() and counts["unclassified"] == 224
    q = pycoQC_parse(summary_file=[os.path.join(d, "Guppy-basecall-1D-DNA_sequencing_summary.txt.gz")], barcode_file=[os.path.join(DATA, "partial_barcode.txt.gz")], min_barcode_percent=0, quiet=True)
    assert not q.reads_df["barcode"].isna().any()


def test_check_arg_coerces_and_enforces_the_upper_bound():
    assert check_arg("x", "7.5", float, min=0, max=60) == 7.5
    with pytest.raises(Exception, match="too high"):
        check_arg("q", 70, float, max=60)

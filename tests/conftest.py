"""Shared helpers: sample data paths and a type-aware comparison of pycoQC JSON statistics."""
import json, math, os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")
SUMMARY_DIR = os.path.join(DOCS, "pycoQC", "data")
SPLIT_DIR = os.path.join(DOCS, "Barcode_split", "data")
FAST5_DIR = os.path.join(DOCS, "Fast5_to_seq_summary", "data")
DATA = os.path.join(os.path.dirname(__file__), "data")
EXPECTED = os.path.join(os.path.dirname(__file__), "expected")
GUPPY213 = os.path.join(SUMMARY_DIR, "Guppy-2.1.3_basecall-1D-DNA_sequencing_summary.txt.gz")
DEEPBINNER = os.path.join(SPLIT_DIR, "Guppy-basecall-1D-DNA_deepbinner_barcoding_summary.txt.gz")
SPLIT_SUMMARY = os.path.join(SPLIT_DIR, "Guppy-basecall-1D-DNA_sequencing_summary.txt.gz")


def flat(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, path + "/" + k)
    elif isinstance(x, list):
        yield path + "#len", len(x)
        for i, v in enumerate(x):
            yield from flat(v, path + "[%d]" % i)
    else:
        yield path, x


def json_differences(expected, got, rel=1e-6):
    """List the differences between two statistics dictionaries (date and package version ignored): exact for ints and text, 1e-6 relative for floats."""
    a, b = dict(flat(expected)), dict(flat(got))
    for k in ("/pycoqc/date", "/pycoqc/version"):  # the version is the release number, not a result
        a.pop(k, None); b.pop(k, None)
    out = ["only in one: %s" % k for k in sorted(set(a) ^ set(b))]
    for k in sorted(set(a) & set(b)):
        x, y = a[k], b[k]
        if type(x) is not type(y):
            out.append("type %s: %r vs %r" % (k, x, y))
        elif isinstance(x, float):
            if not (x == y or (math.isnan(x) and math.isnan(y)) or abs(x - y) <= rel * max(1.0, abs(x))):
                out.append("%s: %r vs %r" % (k, x, y))
        elif x != y:
            out.append("%s: %r vs %r" % (k, x, y))
    return out


@pytest.fixture(scope="session")
def other_expected():
    return json.load(open(os.path.join(EXPECTED, "other.json")))

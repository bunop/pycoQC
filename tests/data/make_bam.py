# Build the tests/data/clean.sorted.bam fixture: 400 reads whose names match the Guppy-2.1.3 summary. Usage: python make_bam.py <out.bam>
import sys, gzip, pysam, random
import os
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "pycoQC", "data", "Guppy-2.1.3_basecall-1D-DNA_sequencing_summary.txt.gz")
out = sys.argv[1]
f = gzip.open(src, "rt"); h = f.readline().rstrip("\n").split("\t"); i = h.index("read_id")
ids = [l.split("\t")[i] for _, l in zip(range(400), f)]
ids = [x for x in ids if x]
hdr = {"HD": {"VN": "1.6", "SO": "coordinate"}, "SQ": [{"SN": "chr1", "LN": 100000}]}
random.seed(0)
with pysam.AlignmentFile(out + ".unsorted.bam", "wb", header=hdr) as o:
    for k, rid in enumerate(ids):
        a = pysam.AlignedSegment(); a.query_name = rid; a.query_sequence = "ACGT"*50
        a.flag = 0; a.reference_id = 0; a.reference_start = k*100; a.mapping_quality = 60
        a.cigarstring = "180M20S" if k % 3 else "200M"
        a.query_qualities = pysam.qualitystring_to_array("I"*200)
        a.set_tag("NM", random.randint(0, 5))
        o.write(a)
pysam.sort("-o", out, out + ".unsorted.bam"); pysam.index(out)
print("reads", len(ids))

#!/usr/bin/env python3
"""Summarise bib_digireco.sh logs into a per-configuration cost table.

Parses the "=== bib_digireco: ..." header, the "STAGE <name> wall_s=… maxrss_gb=…"
lines and the "STAGE_SIZE …_mb=" lines of every log given, groups them by
(sample, BIB_N, coning), and prints per-event wall time, peak RSS and output size,
plus a projection of the cost of a production.

Usage:
  python scripts/bib_bench_summary.py /cmsuf/.../samples/logs/bib_*_bench_*.out
  python scripts/bib_bench_summary.py LOGS... --project-events 1000 --concurrency 150
"""
import argparse
import re
from collections import defaultdict
from statistics import mean

HEADER = re.compile(r"=== bib_digireco: (?P<sim>\S+) entries \[(?P<a>\d+), (?P<b>\d+)\) "
                    r"BIB_N=(?P<n>\d+) seed=\d+ split=(?P<split>\d) coning=\[(?P<coning>[^\]]*)\] "
                    r"cpus=(?P<cpus>\d+)")
STAGE = re.compile(r"^STAGE (?P<name>\w+) wall_s=(?P<wall>\d+) maxrss_gb=(?P<rss>[\d.]+) rc=(?P<rc>-?\d+)")
SIZE = re.compile(r"^STAGE_SIZE (?P<name>\w+)_mb=(?P<mb>\d+)")
SAMPLE = re.compile(r"/(?P<key>[^/]+)_v3p1/")


def parse(path):
    rec = {"stages": {}, "sizes": {}}
    with open(path, errors="replace") as f:
        for line in f:
            if m := HEADER.search(line):
                s = SAMPLE.search(m["sim"])
                rec.update(sample=s["key"] if s else m["sim"], n=int(m["n"]),
                           nev=int(m["b"]) - int(m["a"]), coning=m["coning"].strip() or "-",
                           cpus=int(m["cpus"]))
            elif m := STAGE.match(line):
                rec["stages"][m["name"]] = (int(m["wall"]), float(m["rss"]), int(m["rc"]))
            elif m := SIZE.match(line):
                rec["sizes"][m["name"]] = int(m["mb"])
    return rec if "n" in rec else None


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("logs", nargs="+")
    p.add_argument("--project-events", type=int, default=1000, help="events per sample")
    p.add_argument("--project-samples", type=int, default=4)
    p.add_argument("--concurrency", type=int, default=150, help="simultaneous jobs")
    args = p.parse_args()

    groups = defaultdict(list)
    for path in args.logs:
        r = parse(path)
        if r and r["stages"]:
            groups[(r["sample"], r["n"], r["coning"])].append(r)

    cols = ("sample", "BIB_N", "%BIB", "coning", "jobs", "fail", "digi s/ev", "reco s/ev",
            "total s/ev", "peak RSS GB", "digi MB/ev", "reco MB/ev")
    print(" | ".join(cols))
    print(" | ".join("---" for _ in cols))
    for (sample, n, coning), recs in sorted(groups.items()):
        ok = [r for r in recs if all(rc == 0 for _, _, rc in r["stages"].values())]
        fail = len(recs) - len(ok)

        def per_ev(stage):
            v = [r["stages"][stage][0] / r["nev"] for r in ok if stage in r["stages"]]
            return mean(v) if v else None

        def size(name):
            v = [r["sizes"][name] / r["nev"] for r in ok if name in r["sizes"]]
            return mean(v) if v else None

        digi, reco, both = per_ev("digi"), per_ev("reco"), per_ev("digireco")
        # A total (and a projection) only when every stage finished: DIGI alone
        # understates the cost badly, since RECO dominates once BIB is on.
        total = both if both is not None else (digi + reco if digi is not None and reco is not None else None)
        rss = max((s[1] for r in recs for s in r["stages"].values()), default=None)
        fmt = lambda x, d=0: "-" if x is None else f"{x:.{d}f}"
        print(" | ".join([sample, str(n), f"{100 * n / 1666:.0f}", coning, str(len(recs)),
                          str(fail), fmt(digi), fmt(reco), fmt(total), fmt(rss, 1),
                          fmt(size("digi")), fmt(size("reco"))]))
        if total:
            core_h = total * args.project_events * args.project_samples / 3600
            wall_h = core_h / args.concurrency
            print(f"  -> {args.project_samples} x {args.project_events} ev: {core_h:.0f} job-hours, "
                  f"~{wall_h:.1f} h wall at {args.concurrency} concurrent jobs "
                  f"({args.concurrency * (rss or 0):.0f} GB of memory in flight)")


if __name__ == "__main__":
    main()

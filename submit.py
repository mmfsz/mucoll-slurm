#!/usr/bin/env python3
"""Unified SLURM submitter for the muon-collider simulation chain.

Reads samples.conf and submits N jobs per requested sample, all through the
single run_chain.sh dispatcher. Replaces submit_jobs.py, submit_vbf_inclusive_10k.py,
submit_ZH_lhe_test.py, submit_ZH_CR_tests.py, and the pgun part of submit_scan.py.

Examples:
  python submit.py --list
  python submit.py -s ZH_bbbb_pythia -n 50 -e 10
  python submit.py -s vbfZ_qq_pt500_pythia vbfZ_qq_pt500_whizard -n 500 -e 10 --qos avery-b
  python submit.py -s pgun -n 5 -e 1000 --pgun 11 100 10 170
  python submit.py -s nunuqq_Zmass_pt250 -n 10 -e 10 --dry-run
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import provlog

SLURM_DIR = Path(__file__).resolve().parent
MUONCOLLIDER_DIR = SLURM_DIR.parent
MANIFEST = SLURM_DIR / "samples.conf"
IMAGE = SLURM_DIR / "mucoll-sim.sif"
BENCH = MUONCOLLIDER_DIR / "mucoll-benchmarks"
RUN_CHAIN = SLURM_DIR / "run_chain.sh"
GRIDPACK_BASE = MUONCOLLIDER_DIR / "output" / "gridpacks"


def load_manifest():
    """Return {key: dict(gen_type, card, gridpack)} from samples.conf."""
    samples = {}
    for line in MANIFEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) < 4:
            print(f"WARNING: skipping malformed manifest line: {line!r}", file=sys.stderr)
            continue
        samples[f[0]] = {"gen_type": f[1], "card": f[2], "gridpack": f[3]}
    return samples


def preflight(key, cfg):
    """Validate that a sample's card (and noted gridpack) exist. Returns True/False."""
    card = cfg["card"]
    if card != "-":
        in_repo = (SLURM_DIR / "cards" / "production" / card).exists()
        in_bench = (BENCH / "generation" / "signal" / "whizard" / card).exists()
        if not (in_repo or in_bench):
            print(f"  [{key}] ERROR: card '{card}' not found in cards/production or benchmarks")
            return False
    gp = cfg["gridpack"]
    if gp != "-":
        d = GRIDPACK_BASE / gp
        if not any(d.glob("*.vg")) if d.exists() else True:
            print(f"  [{key}] note: no grids in {d} — will run full integration")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-s", "--samples", nargs="+", metavar="KEY",
                   help="sample keys from samples.conf")
    p.add_argument("-n", "--njobs", type=int, default=1, help="jobs per sample")
    p.add_argument("--indices", type=int, nargs="+", metavar="N",
                   help="submit exactly these job indices (instead of 0..njobs-1) — "
                        "e.g. to rerun specific failed jobs; each keeps its original "
                        "seed and output dir job_<N>/")
    p.add_argument("-e", "--nevents", type=int, default=10, help="events per job")
    p.add_argument("-o", "--output", default="output/batch",
                   help="output dir relative to muoncollider/ (default: output/batch)")
    p.add_argument("--pgun", nargs=4, metavar=("PDG", "PT", "TMIN", "TMAX"),
                   help="extra args for the pgun sample")
    p.add_argument("--tag", default=None,
                   help="label appended to the output sub-dir (and log/job names), e.g. "
                        "'10kEvt' to distinguish productions of the same sample")
    p.add_argument("--time", default="10:00:00", help="SLURM --time")
    p.add_argument("--mem", default="16G", help="SLURM --mem")
    p.add_argument("--cpus", type=int, default=4, help="SLURM --cpus-per-task")
    p.add_argument("--qos", default=None, help="SLURM --qos (e.g. avery-b)")
    p.add_argument("--after", default=None, metavar="JOBID",
                   help="hold these jobs until SLURM job JOBID finishes OK "
                        "(afterok dependency) — e.g. chain production behind its gridpack")
    p.add_argument("--list", action="store_true", help="list available samples and exit")
    p.add_argument("--dry-run", action="store_true", help="write scripts but do not sbatch")
    args = p.parse_args()

    samples = load_manifest()

    if args.list:
        print(f"{'key':<28} {'gen_type':<12} {'card'}")
        for k, c in samples.items():
            print(f"{k:<28} {c['gen_type']:<12} {c['card']}")
        return

    if not args.samples:
        p.error("specify --samples KEY [KEY ...] (or --list)")

    # Validate selection + environment up front.
    unknown = [s for s in args.samples if s not in samples]
    if unknown:
        p.error(f"unknown sample(s): {', '.join(unknown)} (try --list)")
    if not IMAGE.exists():
        sys.exit(f"ERROR: container image not found: {IMAGE}")
    if not BENCH.exists():
        sys.exit(f"ERROR: benchmarks not found: {BENCH}")

    ok = all(preflight(s, samples[s]) for s in args.samples)
    if not ok:
        sys.exit("Pre-flight failed; nothing submitted.")

    output_base = (MUONCOLLIDER_DIR / args.output).resolve()
    log_dir = output_base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(RUN_CHAIN, 0o755)

    qos_line = f"#SBATCH --qos={args.qos}\n" if args.qos else ""
    dep_line = f"#SBATCH --dependency=afterok:{args.after}\n" if args.after else ""
    job_indices = args.indices if args.indices else list(range(args.njobs))
    total = len(args.samples) * len(job_indices)
    print(f"Submitting {len(args.samples)} sample(s) x {len(job_indices)} job(s) = {total} jobs"
          + (f" (indices {job_indices})" if args.indices else ""))
    print(f"Output: {output_base}")

    tag_env = f"--env RUN_TAG={args.tag} " if args.tag else ""
    submitted = {}   # label -> list of SLURM job ids (for the provenance log)
    for key in args.samples:
        cfg = samples[key]
        label = f"{key}_{args.tag}" if args.tag else key   # output dir + log/job name
        submitted[label] = []
        extra = ""
        if cfg["gen_type"] == "pgun" and args.pgun:
            extra = " " + " ".join(args.pgun)
        print(f"\n--- {label} ---")
        for job_id in job_indices:
            cmd = (f"apptainer exec --cleanenv {tag_env}--bind {MUONCOLLIDER_DIR} {IMAGE} "
                   f"bash {RUN_CHAIN} {key} {job_id} {args.nevents} {output_base} {BENCH}{extra}")
            slurm = f"""#!/bin/bash
#SBATCH --job-name=mucoll_{label}_{job_id}
#SBATCH --output={log_dir}/{label}_job_{job_id}.out
#SBATCH --error={log_dir}/{label}_job_{job_id}.err
#SBATCH --time={args.time}
#SBATCH --mem={args.mem}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={args.cpus}
{qos_line}{dep_line}
echo "Host: $(hostname)   Sample: {label}   Job: {job_id}"
{cmd}
"""
            script = SLURM_DIR / f".submit_{label}_{job_id}.sh"
            script.write_text(slurm)
            try:
                if args.dry_run:
                    print(f"  [dry-run] {label} job {job_id}")
                    continue
                r = subprocess.run(["sbatch", str(script)], capture_output=True,
                                   text=True, check=True)
                print(f"  {label} job {job_id}: {r.stdout.strip()}")
                m = re.search(r"(\d+)", r.stdout)
                if m:
                    submitted[label].append(m.group(1))
            except subprocess.CalledProcessError as e:
                print(f"  ERROR submitting {label} job {job_id}: {e.stderr.strip()}")
            finally:
                # sbatch snapshots the script at submit time, so it's safe to remove now.
                if script.exists():
                    script.unlink()

    # Provenance log (skip on dry-run / if nothing was submitted).
    n_sub = sum(len(v) for v in submitted.values())
    if not args.dry_run and n_sub:
        params = f"-n {args.njobs} -e {args.nevents}"
        if args.tag:   params += f" --tag {args.tag}"
        if args.qos:   params += f" --qos {args.qos}"
        if args.after: params += f" --after {args.after}"
        lines = [f"- params: `{params}`  (output base `{output_base}`)", "- production:"]
        for label, ids in submitted.items():
            rng = f"{min(ids, key=int)}–{max(ids, key=int)}" if ids else "none"
            dep = f", afterok:{args.after}" if args.after else ""
            lines.append(f"  - `{label}`: {len(ids)} jobs (ids {rng}{dep}) "
                         f"→ `{os.path.relpath(output_base, MUONCOLLIDER_DIR)}/{label}/`")
        sha, dirty = provlog.append("submit.py production", lines)
        print(f"\nLogged to PRODUCTION_LOG.md (commit {sha[:12]}"
              f"{', DIRTY tree!' if dirty else ''}).")

    print("\nDone.")


if __name__ == "__main__":
    main()

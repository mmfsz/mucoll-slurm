#!/usr/bin/env python3
"""SLURM submitter for scripts/redo_digireco.sh — re-run DIGI+RECO over existing SIM.

Written to repair productions whose digi/reco were truncated by v3.1's
build_application(evt_max=10) default (see mucoll-slurm/CLAUDE.md). SIM is by far
the expensive stage and is left untouched; only digi+reco are redone, in place,
and only after redo_digireco.sh has verified the new files carry the expected
number of events.

One SLURM array task per job directory. Re-running is idempotent: a job dir whose
digi/reco are already correct is simply rebuilt to the same content.

Examples:
  python scripts/submit_redo_digireco.py -s vbfH_bb_pt500_lhe_v3p1 -e 50 --dry-run
  python scripts/submit_redo_digireco.py -s vbfH_bb_pt500_lhe_v3p1 vbfW_qq_pt500_lhe_v3p1 -e 50
  python scripts/submit_redo_digireco.py -s vbfZ_qq_pt500_lhe_v3p1 -e 50 --indices 3 17 42
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from mucoll_paths import benchmarks_path, bind_flags, image_path, samples_base

SLURM_DIR = Path(__file__).resolve().parent.parent
MUONCOLLIDER_DIR = SLURM_DIR.parent
IMAGE = image_path()
IMAGE_BINDS = bind_flags()
BENCH = benchmarks_path()
REDO = SLURM_DIR / "scripts" / "redo_digireco.sh"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-s", "--samples", nargs="+", required=True,
                   help="sample directory names under the base (e.g. vbfH_bb_pt500_lhe_v3p1)")
    p.add_argument("-e", "--nevents", type=int, default=50,
                   help="events to digitise/reconstruct (default 50)")
    p.add_argument("--base", default=None,
                   help="directory holding the sample dirs (default: resolved samples_base())")
    p.add_argument("--indices", nargs="+", type=int, default=None,
                   help="only these job indices (default: every job_* dir found)")
    p.add_argument("--time", default="3:00:00")
    p.add_argument("--mem", default="16G")
    p.add_argument("--cpus", type=int, default=4)
    p.add_argument("--qos", default="avery-b")
    p.add_argument("--after", default=None,
                   help="SLURM job id to gate on (--dependency=afterok), e.g. a canary run")
    p.add_argument("--dry-run", action="store_true", help="write scripts but do not sbatch")
    return p.parse_args()


def job_indices(sample_dir, wanted):
    """Return the sorted job indices present in sample_dir that carry a sim file."""
    found = []
    for d in sorted(sample_dir.glob("job_*")):
        m = re.fullmatch(r"job_(\d+)", d.name)
        if not m:
            continue
        idx = int(m.group(1))
        if wanted is not None and idx not in wanted:
            continue
        if not list(d.glob("sim_output_*.edm4hep.root")):
            print(f"  WARN: {d.name} has no sim output — skipped")
            continue
        found.append(idx)
    return found


def main():
    args = parse_args()
    base = Path(args.base).resolve() if args.base else samples_base()
    if not REDO.exists():
        sys.exit(f"ERROR: {REDO} not found")
    REDO.chmod(0o755)

    # Pre-flight: resolve every sample before submitting anything.
    plan = {}
    ok = True
    for key in args.samples:
        sample_dir = base / key
        if not sample_dir.is_dir():
            print(f"ERROR: no such sample dir: {sample_dir}")
            ok = False
            continue
        idxs = job_indices(sample_dir, set(args.indices) if args.indices else None)
        if not idxs:
            print(f"ERROR: no job dirs with sim output in {sample_dir}")
            ok = False
            continue
        plan[key] = (sample_dir, idxs)
    if not ok:
        sys.exit("Pre-flight failed; nothing submitted.")

    log_dir = base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    total = sum(len(v[1]) for v in plan.values())
    print(f"Re-running DIGI+RECO at {args.nevents} events on {total} job(s) "
          f"across {len(plan)} sample(s)")
    print(f"Base: {base}")

    qos_line = f"#SBATCH --qos={args.qos}\n" if args.qos else ""
    dep_line = f"#SBATCH --dependency=afterok:{args.after}\n" if args.after else ""
    for key, (sample_dir, idxs) in plan.items():
        # An explicit index list keeps the array exact even if job dirs are sparse.
        array_spec = ",".join(str(i) for i in idxs)
        cmd = (f"apptainer exec --cleanenv --env SLURM_JOB_ID=$SLURM_JOB_ID "
               f"{IMAGE_BINDS} --bind {MUONCOLLIDER_DIR} --bind {base} {IMAGE} "
               f"bash {REDO} {sample_dir}/job_$SLURM_ARRAY_TASK_ID {args.nevents}")
        slurm = f"""#!/bin/bash
#SBATCH --job-name=redo_{key}
#SBATCH --output={log_dir}/redo_{key}_job_%a.out
#SBATCH --error={log_dir}/redo_{key}_job_%a.err
#SBATCH --array={array_spec}
#SBATCH --time={args.time}
#SBATCH --mem={args.mem}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={args.cpus}
{qos_line}{dep_line}
echo "Host: $(hostname)   Sample: {key}   Job: $SLURM_ARRAY_TASK_ID   Events: {args.nevents}"
{cmd}
"""
        script = SLURM_DIR / f".redo_{key}.sh"
        script.write_text(slurm)
        try:
            if args.dry_run:
                print(f"  [dry-run] {key}: array of {len(idxs)} task(s) "
                      f"[{idxs[0]}..{idxs[-1]}]")
                continue
            r = subprocess.run(["sbatch", str(script)], capture_output=True,
                               text=True, check=True)
            print(f"  {key} ({len(idxs)} tasks): {r.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR submitting {key}: {e.stderr.strip()}")
        finally:
            # sbatch snapshots the script at submit time, so it is safe to remove now.
            if script.exists():
                script.unlink()


if __name__ == "__main__":
    main()

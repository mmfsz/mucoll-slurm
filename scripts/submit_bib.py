#!/usr/bin/env python3
"""SLURM submitter for scripts/bib_digireco.sh — DIGI+RECO with BIB over existing SIM.

BIB enters only at digitisation, so the samples' existing SIM is reused: event i of
a sample is entry i % 50 of sim job i // 50 (the _v3p1 productions are 100 jobs x
50 events). Every BIB event therefore has a no-BIB twin, produced the same way with
--bib 0. One SLURM array task processes --events-per-job consecutive entries of one
sim file.

Output: <samples_base>/<KEY>_v3p2_bib<N>[_cc][_tc][_<tag>]/job_<simjob>/reco_output_e<entry>.edm4hep.root

Examples:
  python scripts/submit_bib.py -s vbfZ_qq_pt500_lhe --bib 1666 -e 5 --events-per-job 5 --split --dry-run
  python scripts/submit_bib.py -s vbfH_bb_pt500_lhe ZH_bbbb_lhe --bib 0 -e 100 --events-per-job 10
  python scripts/submit_bib.py -s ZH_bbbb_lhe --bib-frac 0.1 -e 900 --first-event 100 --throttle 50
"""
import argparse
import os
import subprocess
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import provlog
from mucoll_paths import bind_flags, image_path, samples_base

SLURM_DIR = Path(__file__).resolve().parent.parent
MUONCOLLIDER_DIR = SLURM_DIR.parent
IMAGE = image_path()
IMAGE_BINDS = bind_flags()
WORKER = SLURM_DIR / "scripts" / "bib_digireco.sh"
BIB_DIR = Path(os.environ.get("MUCOLL_BIB", "/blue/avery/share/mucol/bib/BIB_v9"))
FULL_BIB = 1666          # files per beam = 100 % of a bunch crossing (MAIAConfig default)
SIM_EVENTS_PER_JOB = 50  # events per sim file in the _v3p1 productions
SIM_TAG = "v3p1"         # the SIM being reused
OUT_TAG = "v3p2"         # the release doing DIGI+RECO


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-s", "--samples", nargs="+", required=True,
                   help="base sample keys (e.g. vbfZ_qq_pt500_lhe); SIM is read from <key>_v3p1")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--bib", type=int, help=f"BIB files per beam ({FULL_BIB} = 100 %%, 0 = no BIB)")
    g.add_argument("--bib-frac", type=float, help="BIB fraction of a bunch crossing (1.0 = 100 %%)")
    p.add_argument("-e", "--nevents", type=int, required=True, help="events per sample")
    p.add_argument("--first-event", type=int, default=0,
                   help="global index of the first event (to extend a production)")
    p.add_argument("--events-per-job", type=int, default=10,
                   help=f"events per array task; must divide {SIM_EVENTS_PER_JOB}")
    p.add_argument("--split", action="store_true", help="separate DIGI and RECO (benchmarking)")
    p.add_argument("--keep-digi", action="store_true", help="with --split, keep the digi file")
    p.add_argument("--keep-hits", action="store_true", help="keep hit collections in the reco output")
    p.add_argument("--calo-coning", action="store_true", help="--doCaloConing")
    p.add_argument("--tracker-coning", action="store_true", help="--doTrackerConing")
    p.add_argument("--tag", default=None, help="suffix for the output dir (e.g. bench)")
    p.add_argument("--time", default="24:00:00")
    p.add_argument("--mem", default="64G")
    p.add_argument("--cpus", type=int, default=4)
    p.add_argument("--qos", default="avery-b")
    p.add_argument("--throttle", type=int, default=None,
                   help="max simultaneously running tasks per sample (array %%K)")
    p.add_argument("--dry-run", action="store_true", help="write scripts but do not sbatch")
    return p.parse_args()


def sim_dir(key):
    """The <key>_v3p1 SIM production: on /cmsuf, or still only under output/batch."""
    for base in (samples_base(), MUONCOLLIDER_DIR / "output" / "batch"):
        d = base / f"{key}_{SIM_TAG}"
        if d.is_dir():
            return d
    return None


def seed(key, simjob, entry):
    """Deterministic per-task seed. The overlay seeds on (RandSeed, event, run) and
    event numbers repeat across sim files, so the seed must differ per task."""
    return zlib.crc32(f"{key}:{simjob}:{entry}".encode()) & 0x7FFFFFFF


def main():
    args = parse_args()
    n_bib = args.bib if args.bib is not None else round(args.bib_frac * FULL_BIB)
    epj = args.events_per_job
    if SIM_EVENTS_PER_JOB % epj or args.first_event % epj or args.nevents % epj:
        sys.exit(f"ERROR: --events-per-job must divide {SIM_EVENTS_PER_JOB}, "
                 "--first-event and -e")
    if n_bib > 0:
        for beam in ("sim_mp", "sim_mm"):
            n = len(list((BIB_DIR / beam).glob("*.root")))
            if n < n_bib:
                sys.exit(f"ERROR: {BIB_DIR / beam} has {n} files, need >= {n_bib}")
    WORKER.chmod(0o755)

    suffix = f"bib{n_bib}" + ("_cc" if args.calo_coning else "") \
        + ("_tc" if args.tracker_coning else "") + (f"_{args.tag}" if args.tag else "")
    flags = [f for f, on in (("--split", args.split), ("--keep-digi", args.keep_digi),
                             ("--keep-hits", args.keep_hits),
                             ("--calo-coning", args.calo_coning),
                             ("--tracker-coning", args.tracker_coning)) if on]
    out_base = samples_base()

    # Pre-flight: resolve every task of every sample before submitting anything.
    plan, ok = {}, True
    for key in args.samples:
        sd = sim_dir(key)
        if sd is None:
            print(f"ERROR: no {key}_{SIM_TAG} SIM production found")
            ok = False
            continue
        tasks = []
        for first in range(args.first_event, args.first_event + args.nevents, epj):
            simjob, entry = divmod(first, SIM_EVENTS_PER_JOB)
            sim = sd / f"job_{simjob}" / f"sim_output_{simjob}.edm4hep.root"
            if not sim.exists():
                print(f"  WARN: {key}: missing {sim} — events {first}..{first + epj - 1} skipped")
                continue
            tasks.append((sim, simjob, entry))
        if not tasks:
            print(f"ERROR: {key}: no sim files for the requested events")
            ok = False
            continue
        plan[key] = (sd, tasks)
    if not ok:
        sys.exit("Pre-flight failed; nothing submitted.")

    log_dir = out_base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    print(f"BIB {n_bib} files/beam ({100 * n_bib / FULL_BIB:.1f} %), {epj} events/task, "
          f"flags {flags or 'none'}")
    qos_line = f"#SBATCH --qos={args.qos}\n" if args.qos else ""
    submitted = {}
    for key, (sd, tasks) in plan.items():
        label = f"{key}_{OUT_TAG}_{suffix}"
        out_dir = out_base / label
        # The task table maps array index -> (sim file, entry, seed, out dir).
        table = log_dir / f"bib_{label}_e{args.first_event}.tasks"
        table.write_text("".join(
            f"{sim} {entry} {seed(key, simjob, entry)} {out_dir}/job_{simjob}\n"
            for sim, simjob, entry in tasks))
        throttle = f"%{args.throttle}" if args.throttle else ""
        binds = " ".join(f"--bind {b}" for b in sorted({str(MUONCOLLIDER_DIR), str(out_base),
                                                        str(sd), str(BIB_DIR)}))
        slurm = f"""#!/bin/bash
#SBATCH --job-name=bib_{label}
#SBATCH --output={log_dir}/bib_{label}_%A_%a.out
#SBATCH --error={log_dir}/bib_{label}_%A_%a.err
#SBATCH --array=0-{len(tasks) - 1}{throttle}
#SBATCH --time={args.time}
#SBATCH --mem={args.mem}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={args.cpus}
{qos_line}
read SIM ENTRY SEED OUT <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" {table})"
echo "Host: $(hostname)   {label}   task $SLURM_ARRAY_TASK_ID: $SIM entry $ENTRY"
apptainer exec --cleanenv --env SLURM_JOB_ID=$SLURM_JOB_ID \\
    --env SLURM_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK --env MUCOLL_BIB={BIB_DIR} \\
    {IMAGE_BINDS} {binds} {IMAGE} \\
    bash {WORKER} "$SIM" "$ENTRY" {epj} "$OUT" {n_bib} "$SEED" {' '.join(flags)}
"""
        script = SLURM_DIR / f".bib_{label}.sh"
        script.write_text(slurm)
        try:
            if args.dry_run:
                print(f"  [dry-run] {label}: {len(tasks)} task(s), script {script}, table {table}")
                for sim, simjob, entry in tasks[:3]:
                    print(f"      {sim.name} entry {entry} seed {seed(key, simjob, entry)}")
                continue
            r = subprocess.run(["sbatch", str(script)], capture_output=True, text=True, check=True)
            jobid = r.stdout.strip().split()[-1]
            submitted[label] = (jobid, len(tasks))
            print(f"  {label} ({len(tasks)} tasks): {r.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR submitting {label}: {e.stderr.strip()}")
        finally:
            if script.exists() and not args.dry_run:
                script.unlink()

    if submitted:
        params = (f"--bib {n_bib} -e {args.nevents} --first-event {args.first_event} "
                  f"--events-per-job {epj} {' '.join(flags)} --mem {args.mem} --cpus {args.cpus}")
        lines = [f"- params: `{params.strip()}`  (BIB `{BIB_DIR}`, SIM `{SIM_TAG}` reused)",
                 "- production:"]
        for label, (jobid, n) in submitted.items():
            lines.append(f"  - `{label}`: array {jobid} ({n} tasks) → `{out_base / label}/`")
        sha, dirty = provlog.append("submit_bib.py BIB digi+reco", lines)
        print(f"\nLogged to PRODUCTION_LOG.md (commit {sha[:12]}{', DIRTY tree!' if dirty else ''}).")


if __name__ == "__main__":
    main()

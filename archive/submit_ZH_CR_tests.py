#!/usr/bin/env python3
"""
Submit Test A (hybrid+noCR) and Test B (hybrid+skI) — 10 jobs x 10 events each.

Usage:
    python mucoll-slurm/submit_ZH_CR_tests.py
"""
import os
import subprocess

SLURM_DIR          = os.path.dirname(os.path.abspath(__file__))
MUONCOLLIDER_DIR   = os.path.dirname(SLURM_DIR)
SCRIPT             = os.path.join(SLURM_DIR, "run_chain_ZH.sh")
BENCHMARKS         = os.path.join(MUONCOLLIDER_DIR, "mucoll-benchmarks")
IMAGE              = os.path.join(SLURM_DIR, "mucoll-sim.sif")

NUM_JOBS   = 10
NEVENTS    = 10

TESTS = [
    # (label, output_subdir, SET)
    ("ZH_hybrid_noCR", "output/ZH_hybrid_noCR_test", "3"),
    ("ZH_hybrid_skI",  "output/ZH_hybrid_skI_test",  "4"),
]

for label, out_rel, SET in TESTS:
    out_dir = os.path.join(MUONCOLLIDER_DIR, out_rel)
    log_dir = os.path.join(out_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    print(f"\n--- {label} (SET={SET}) -> {out_rel} ---")
    for job_id in range(NUM_JOBS):
        slurm = f"""#!/bin/bash
#SBATCH --job-name=mucoll_{label}_{job_id}
#SBATCH --output={log_dir}/{label}_job_{job_id}.out
#SBATCH --error={log_dir}/{label}_job_{job_id}.err
#SBATCH --time=10:00:00
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running on host: $(hostname)"
echo "Process: {label}  Job ID: {job_id}"

apptainer exec --cleanenv --bind {MUONCOLLIDER_DIR} {IMAGE} \\
    bash {SCRIPT} {job_id} {NEVENTS} {out_dir} {BENCHMARKS} {SET}
"""
        fname = f"submit_{label}_{job_id}.sh"
        with open(fname, "w") as f:
            f.write(slurm)
        try:
            r = subprocess.run(["sbatch", fname], capture_output=True, text=True, check=True)
            print(f"  Submitted job {job_id}: {r.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  Error job {job_id}: {e.stderr.strip()}")
        finally:
            if os.path.exists(fname):
                os.remove(fname)

print("\nDone.")

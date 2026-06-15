#!/usr/bin/env python3
"""
Submit the LHE-route ZH test (SET=5) — 10 jobs x 10 events.

The LHE route:
  1. Whizard generates a parton-level LHE file (mu+mu- -> ZH, Z and H stable).
  2. LheToHepMC (Pythia8-based binary) reads the LHE, decays Z/H -> bb,
     showers, hadronizes, and writes a HepMC3 file.
  3. DDSim / k4run run as usual on the HepMC output.

Prerequisites:
  - LheToHepMC must be built inside the container:
      apptainer exec --cleanenv --bind <muoncollider_dir> mucoll-sim.sif \\
          bash mucoll-slurm/pythia/build.sh
  - The Whizard integration will run from scratch (no gridpack for LHE mode).

Usage:
    python mucoll-slurm/submit_ZH_lhe_test.py
"""
import os
import subprocess

SLURM_DIR        = os.path.dirname(os.path.abspath(__file__))
MUONCOLLIDER_DIR = os.path.dirname(SLURM_DIR)
SCRIPT           = os.path.join(SLURM_DIR, "run_chain_ZH.sh")
BENCHMARKS       = os.path.join(MUONCOLLIDER_DIR, "mucoll-benchmarks")
IMAGE            = os.path.join(SLURM_DIR, "mucoll-sim.sif")

NUM_JOBS = 10
NEVENTS  = 10
SET      = 5
LABEL    = "ZH_lhe"
OUT_REL  = "output/ZH_lhe_test"

out_dir  = os.path.join(MUONCOLLIDER_DIR, OUT_REL)
log_dir  = os.path.join(out_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

print(f"--- {LABEL} (SET={SET}) -> {OUT_REL} ---")
print(f"Submitting {NUM_JOBS} jobs x {NEVENTS} events each")

for job_id in range(NUM_JOBS):
    slurm = f"""#!/bin/bash
#SBATCH --job-name=mucoll_{LABEL}_{job_id}
#SBATCH --output={log_dir}/{LABEL}_job_{job_id}.out
#SBATCH --error={log_dir}/{LABEL}_job_{job_id}.err
#SBATCH --time=10:00:00
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running on host: $(hostname)"
echo "Process: {LABEL}  Job ID: {job_id}"

apptainer exec --cleanenv --bind {MUONCOLLIDER_DIR} {IMAGE} \\
    bash {SCRIPT} {job_id} {NEVENTS} {out_dir} {BENCHMARKS} {SET}
"""
    fname = f"submit_{LABEL}_{job_id}.sh"
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

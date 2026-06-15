import argparse
import os
import subprocess
import sys

# --- Paths (derived from this script's location) ---
SLURM_DIR = os.path.dirname(os.path.abspath(__file__))
MUONCOLLIDER_DIR = os.path.dirname(SLURM_DIR)

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="output/batch",
                    help="Output directory relative to MUONCOLLIDER_DIR (default: output/batch)")
args = parser.parse_args()

# --- Configuration ---
NUM_JOBS = 50             # Number of jobs per process
NEVENTS_PER_JOB = 10      # Events per job -> NUM_JOBS x NEVENTS_PER_JOB events total per variant
OUTPUT_BASE_DIR = os.path.join(MUONCOLLIDER_DIR, args.output)
MUCOLL_BENCHMARKS_PATH = os.path.join(MUONCOLLIDER_DIR, "mucoll-benchmarks")
# Set to the directory containing pre-computed Whizard VAMP grids, or leave
# empty ("") to run the full phase-space integration inside each job.
GRIDPACK_DIR = os.path.join(MUONCOLLIDER_DIR, "output/gridpacks")

APPTAINER_IMAGE = os.path.join(SLURM_DIR, "mucoll-sim.sif")

# --- Processes to submit ---
# Add or comment out entries to control which processes are submitted.
# Each entry can be EITHER:
#   (label, run_chain_script)                 -> legacy signature:
#         <JOB_ID> <NEVENTS> <OUT> <BENCHMARKS> <GRIDPACK_DIR>
#   (label, run_chain_script, extra_args, gridpack_override)
#         <JOB_ID> <NEVENTS> <OUT> <BENCHMARKS> [extra_args...] <GRIDPACK_DIR>
#     where extra_args is a list of strings (e.g. ["3"] for SET=3) and
#     gridpack_override (str or None) replaces the default GRIDPACK_DIR.
PROCESSES = [
    # ("MuMu_WWZ_Hadronic", os.path.join(SLURM_DIR, "chains/run_chain_WWZ_hadronic.sh")),
    # ("MuMu_ZZZ_Hadronic", os.path.join(SLURM_DIR, "chains/run_chain_ZZZ_hadronic.sh")),
    # ("pgun", os.path.join(SLURM_DIR, "chains/run_chain_pgun.sh")),
    # ("ZH", os.path.join(SLURM_DIR, "run_chain_ZH.sh")),
    # ("ZH_inclusive", os.path.join(SLURM_DIR, "run_chain_ZH_inclusive.sh")),
    # ("pythia_ZH", os.path.join(SLURM_DIR, "chains/run_chain_pythia_ZH.sh")),

    # VBF single-Z variants (SET=1/2/3). One gridpack shared across sets.
    ("vbfZ_set1", os.path.join(SLURM_DIR, "chains/run_chain_vbfZ.sh"),
        ["1"], os.path.join(MUONCOLLIDER_DIR, "output/gridpacks/grid_mumu_vbfZ")),
    ("vbfZ_set2", os.path.join(SLURM_DIR, "chains/run_chain_vbfZ.sh"),
        ["2"], os.path.join(MUONCOLLIDER_DIR, "output/gridpacks/grid_mumu_vbfZ")),
    ("vbfZ_set3", os.path.join(SLURM_DIR, "chains/run_chain_vbfZ.sh"),
        ["3"], os.path.join(MUONCOLLIDER_DIR, "output/gridpacks/grid_mumu_vbfZ")),
]


def unpack(entry):
    """Return (label, script_path, extra_args, gridpack_dir) for an entry."""
    if len(entry) == 2:
        label, script = entry
        return label, script, [], GRIDPACK_DIR
    if len(entry) == 4:
        label, script, extras, grid = entry
        return label, script, list(extras), (grid if grid is not None else GRIDPACK_DIR)
    raise ValueError(f"Bad PROCESSES entry (need 2 or 4 fields): {entry}")

# --- Validation ---
if not os.path.exists(MUCOLL_BENCHMARKS_PATH):
    print(f"Error: Benchmarks path not found: {MUCOLL_BENCHMARKS_PATH}")
    sys.exit(1)

for entry in PROCESSES:
    label, script_path, _, _ = unpack(entry)
    if not os.path.exists(script_path):
        print(f"Error: Script not found for {label}: {script_path}")
        sys.exit(1)
    os.chmod(script_path, 0o755)

if not os.path.exists(APPTAINER_IMAGE):
    print(f"Error: Container image not found: {APPTAINER_IMAGE}")
    print(f"Pull it first with:")
    print(f"  apptainer pull {APPTAINER_IMAGE} docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main")
    sys.exit(1)

os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
print(f"Submitting {NUM_JOBS} jobs x {len(PROCESSES)} process(es) = {NUM_JOBS * len(PROCESSES)} total jobs.")
print(f"Output will be in {OUTPUT_BASE_DIR}")

# Launch jobs for each process specified above.
for entry in PROCESSES:
    label, script_path, extra_args, gridpack = unpack(entry)
    print(f"\n--- Process: {label} ---")
    extra_str = " ".join(extra_args)
    for job_id in range(NUM_JOBS):
        job_name = f"mucoll_{label}_{job_id}"
        log_dir = os.path.join(OUTPUT_BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={log_dir}/{label}_job_{job_id}.out
#SBATCH --error={log_dir}/{label}_job_{job_id}.err
#SBATCH --time=10:00:00
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running on host: $(hostname)"
echo "Process: {label}  Job ID: {job_id}"

# Run the container (--cleanenv prevents host Python env vars from breaking container Python)
apptainer exec --cleanenv --bind {MUONCOLLIDER_DIR} {APPTAINER_IMAGE} bash {script_path} {job_id} {NEVENTS_PER_JOB} {OUTPUT_BASE_DIR} {MUCOLL_BENCHMARKS_PATH} {extra_str} {gridpack}
"""

        script_filename = f"submit_{label}_{job_id}.sh"
        with open(script_filename, "w") as f:
            f.write(slurm_script)

        try:
            result = subprocess.run(["sbatch", script_filename], capture_output=True, text=True, check=True)
            print(f"  Submitted {label} job {job_id}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  Error submitting {label} job {job_id}: {e.stderr}")
        finally:
            if os.path.exists(script_filename):
                os.remove(script_filename)

print("Submission complete.")

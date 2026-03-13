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
NUM_JOBS = 100            # Number of jobs to submit
NEVENTS_PER_JOB = 10      # Events per job
OUTPUT_BASE_DIR = os.path.join(MUONCOLLIDER_DIR, args.output)
MUCOLL_BENCHMARKS_PATH = os.path.join(MUONCOLLIDER_DIR, "mucoll-benchmarks")
# SCRIPT_PATH = os.path.join(SLURM_DIR, "run_chain_pgun.sh")
# SCRIPT_PATH = os.path.join(SLURM_DIR, "run_chain_WWZ_hadronic.sh")
# SCRIPT_PATH = os.path.join(SLURM_DIR, "run_chain_ZZZ_hadronic.sh")
SCRIPT_PATH = os.path.join(SLURM_DIR, "run_chain_ZH.sh")

APPTAINER_IMAGE = os.path.join(SLURM_DIR, "mucoll-sim.sif")

# --- Validation ---
if not os.path.exists(MUCOLL_BENCHMARKS_PATH):
    print(f"Error: Benchmarks path not found: {MUCOLL_BENCHMARKS_PATH}")
    sys.exit(1)

if not os.path.exists(SCRIPT_PATH):
    print(f"Error: Script not found: {SCRIPT_PATH}")
    sys.exit(1)

if not os.path.exists(APPTAINER_IMAGE):
    print(f"Error: Container image not found: {APPTAINER_IMAGE}")
    print(f"Pull it first with:")
    print(f"  apptainer pull {APPTAINER_IMAGE} docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main")
    sys.exit(1)

# Ensure script is executable
os.chmod(SCRIPT_PATH, 0o755)

# Create output directory
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

print(f"Submitting {NUM_JOBS} jobs with {NEVENTS_PER_JOB} events each.")
print(f"Output will be in {OUTPUT_BASE_DIR}")

for job_id in range(NUM_JOBS):
    job_name = f"mucoll_job_{job_id}"
    log_dir = os.path.join(OUTPUT_BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Slurm script content
    slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={log_dir}/job_{job_id}.out
#SBATCH --error={log_dir}/job_{job_id}.err
#SBATCH --time=10:00:00
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running on host: $(hostname)"
echo "Job ID: {job_id}"

# Run the container (--cleanenv prevents host Python env vars from breaking container Python)
apptainer exec --cleanenv --bind {MUONCOLLIDER_DIR} {APPTAINER_IMAGE} bash {SCRIPT_PATH} {job_id} {NEVENTS_PER_JOB} {OUTPUT_BASE_DIR} {MUCOLL_BENCHMARKS_PATH}
"""

    script_filename = f"submit_job_{job_id}.sh"
    with open(script_filename, "w") as f:
        f.write(slurm_script)

    # Submit the job
    try:
        # subprocess.run("cat " + script_filename, shell=True, check=True)
        result = subprocess.run(["sbatch", script_filename], capture_output=True, text=True, check=True)
        print(f"Submitted job {job_id}: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting job {job_id}: {e.stderr}")
    finally:
        if os.path.exists(script_filename):
            os.remove(script_filename)

print("Submission complete.")

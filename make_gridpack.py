#!/usr/bin/env python3
"""
make_gridpack.py

Submits Slurm jobs to run Whizard phase-space integration and write VAMP
grid files (.vg) for the WWZ and ZZZ hadronic processes at 10 TeV.
This should be run once before submitting production jobs.

The resulting grid files are saved under GRIDPACK_DIR/<process>/grids/ and can
be loaded by run_chain_WWZ_hadronic.sh / run_chain_ZZZ_hadronic.sh via a symlink
to that directory using:
  ?rebuild_grids = false
  $integrate_workspace = "grids"  (relative — Whizard forbids absolute paths here)
"""

import argparse
import os
import re
import subprocess
import sys

import provlog
from mucoll_paths import benchmarks_path, bind_flags, gridpack_base, image_path

# --- Configuration ---
SLURM_DIR             = os.path.dirname(os.path.abspath(__file__))
WORK_DIR              = os.path.dirname(SLURM_DIR)
MUCOLL_BENCHMARKS_PATH = str(benchmarks_path())   # see mucoll_paths.py
GRIDPACK_DIR          = str(gridpack_base())   # see mucoll_paths.py
APPTAINER_IMAGE       = image_path()   # see lib/image.sh
IMAGE_BINDS           = bind_flags()
DATA_DIR_TO_BIND      = WORK_DIR
LOG_DIR               = os.path.join(GRIDPACK_DIR, "logs")

# Software environment is centralized in lib/env.sh (one place for spack +
# Whizard paths), sourced by the generated job script.
ENV_SETUP = f"source {os.path.join(SLURM_DIR, 'lib', 'env.sh')}"

GRID_CARDS = os.path.join(SLURM_DIR, "cards", "gridpack")

# name -> (gridpack card, grid output dir). Grid dir names are kept stable so
# pre-computed grids stay valid; card names follow the harmonized convention.
PROCESSES = {
    "nunuqq": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_nunuqq_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_nunuqq_10TeV"),
    },
    "mumuqq": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_mumuqq_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_mumuqq_10TeV"),
    },
    "bbbb": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_bbbb_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_bbbb_10TeV"),
    },
    # s-channel ZH (e2 E2 -> Z H). whizard = Whizard-decayed (unstable);
    # lhe = stable production for the LHE route.
    "ZH_bbbb_whizard": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_ZH_bbbb_whizard_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_ZH_bbbb_whizard_10TeV"),
    },
    "ZH_bbbb_lhe": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_ZH_bbbb_lhe_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_ZH_bbbb_lhe_10TeV"),
    },
    # VBF single-boson (one gridpack per boson; shared by all decayer variants).
    "vbfH": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_vbfH_pt500_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_vbfH_pt500_10TeV"),
    },
    "vbfZ": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_vbfZ_pt500_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_vbfZ_pt500_10TeV"),
    },
    "vbfW": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_vbfW_pt500_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_vbfW_pt500_10TeV"),
    },
    # Inclusive 2->4 processes (no resonance in ME).
    "nunuqq_Zmass_pt250": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_nunuqq_Zmass_pt250_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_nunuqq_Zmass_pt250_10TeV"),
    },
    "nunubb_Hmass_pt250": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_nunubb_Hmass_pt250_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_nunubb_Hmass_pt250_10TeV"),
    },
    "lnuqq_Wmass_pt250": {
        "sin_template": os.path.join(GRID_CARDS, "mumu_lnuqq_Wmass_pt250_10TeV.gridpack.sin"),
        "workdir":  os.path.join(GRIDPACK_DIR, "mumu_lnuqq_Wmass_pt250_10TeV"),
    },
}

# This file is a script, not a library: everything below runs at import time and
# submits SLURM jobs (24 h x 32 CPU each). Importing it — to inspect a constant,
# say — would fire off the whole set, so refuse that outright.
if __name__ != "__main__":
    raise ImportError(
        "make_gridpack.py is a script, not an importable module: importing it "
        "would submit gridpack jobs. Import mucoll_paths for the paths instead.")

parser = argparse.ArgumentParser(
    description="Submit Whizard gridpack integration jobs",
    epilog="Name each process explicitly, space-separated: "
           "make_gridpack.py vbfZ vbfW")
parser.add_argument("processes", nargs="*", metavar="PROCESS",
                    help=f"Processes to submit, space-separated. "
                         f"Choices: {' '.join(PROCESSES)}")
args = parser.parse_args()

# No "submit everything" default, deliberately. Each process is its own 24 h x 32 CPU
# SLURM job, so a bare `make_gridpack.py` used to fire off all of them at once — an
# expensive thing to do by accident, and easy to do while exploring the command.
if not args.processes:
    print("ERROR: name at least one process to submit.\n", file=sys.stderr)
    print(f"  Available ({len(PROCESSES)}): {' '.join(PROCESSES)}", file=sys.stderr)
    print("  Example:  python3 make_gridpack.py vbfZ", file=sys.stderr)
    print("            python3 make_gridpack.py vbfZ vbfW      # space-separated",
          file=sys.stderr)
    print(f"\nThere is no 'all' default on purpose: each process is a separate "
          f"24 h x 32 CPU\njob, so a bare invocation would submit all {len(PROCESSES)} "
          f"of them. If that is genuinely\nwhat you want, list them explicitly.",
          file=sys.stderr)
    sys.exit(2)

# Validate process names
for p in args.processes:
    if p not in PROCESSES:
        print(f"Error: unknown process '{p}'. Choose from {list(PROCESSES.keys())}")
        sys.exit(1)

os.makedirs(LOG_DIR, exist_ok=True)

submitted = []   # (name, jobid, workdir) for the provenance log

for name in args.processes:
    cfg = PROCESSES[name]
    os.makedirs(cfg["workdir"], exist_ok=True)

    slurm_script = f"""#!/bin/bash
#SBATCH --job-name=whizard_gridpack_{name}
#SBATCH --output={LOG_DIR}/gridpack_{name}.out
#SBATCH --error={LOG_DIR}/gridpack_{name}.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --qos=avery-b

echo "========================================"
echo "Whizard gridpack: {name}"
echo "Host: $(hostname)"
echo "========================================"

apptainer exec --cleanenv {IMAGE_BINDS} --bind {DATA_DIR_TO_BIND} {APPTAINER_IMAGE} bash -c '
    set -e
    {ENV_SETUP}
    export OMP_NUM_THREADS=32

    WORKDIR={cfg["workdir"]}
    cd $WORKDIR

    # Copy the sin file — it writes .vg files directly to the working directory
    cp {cfg["sin_template"]} ./gridpack.sin

    echo "Running Whizard integration..."
    whizard gridpack.sin

    echo "Grid files written:"
    ls -lh {cfg["workdir"]}/*.vg 2>/dev/null || echo "(no .vg files found, check whizard.log)"
    echo "Gridpack {name} complete."
'
"""

    # Absolute, and beside the script itself: a relative "chains/..." path made
    # this silently depend on the caller's cwd (it only worked from mucoll-slurm/).
    # Dot-prefixed and gitignored, same convention as submit.py's .submit_*.sh.
    script_path = os.path.join(SLURM_DIR, f".gridpack_{name}.sh")
    with open(script_path, "w") as f:
        f.write(slurm_script)

    try:
        result = subprocess.run(
            ["sbatch", script_path], capture_output=True, text=True, check=True
        )
        print(f"Submitted {name} gridpack job: {result.stdout.strip()}")
        m = re.search(r"(\d+)", result.stdout)
        submitted.append((name, m.group(1) if m else "?", cfg["workdir"]))
    except subprocess.CalledProcessError as e:
        print(f"Error submitting {name}: {e.stderr}")
    finally:
        # sbatch snapshots the script at submit time, so removing it now is safe.
        if os.path.exists(script_path):
            os.remove(script_path)

# Provenance log.
if submitted:
    lines = ["- gridpacks:"]
    for name, jid, wd in submitted:
        lines.append(f"  - `{name}`: jobid {jid} → `{os.path.relpath(wd, WORK_DIR)}/`")
    sha, dirty = provlog.append("make_gridpack.py", lines)
    print(f"\nLogged to PRODUCTION_LOG.md (commit {sha[:12]}"
          f"{', DIRTY tree!' if dirty else ''}).")

print(f"\nGrid files will be written to: {GRIDPACK_DIR}/<gridpack name>/  (matches the samples.conf gridpack column)")

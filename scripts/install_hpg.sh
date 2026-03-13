#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLURM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MUONCOLLIDER_DIR="$(cd "$SLURM_DIR/.." && pwd)"

echo "=== MuColl-SLURM setup for HiPerGator ==="
echo "Base directory: $MUONCOLLIDER_DIR"

# 1. Pull the container image
SIF_PATH="$SLURM_DIR/mucoll-sim.sif"
if [ -f "$SIF_PATH" ]; then
    echo "Container image already exists at $SIF_PATH, skipping pull."
else
    echo "Pulling container image (this may take several minutes)..."
    apptainer pull "$SIF_PATH" docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main
    echo "Container image saved to $SIF_PATH"
fi

# 2. Clone mucoll-benchmarks
BENCHMARKS_PATH="$MUONCOLLIDER_DIR/mucoll-benchmarks"
if [ -d "$BENCHMARKS_PATH" ]; then
    echo "mucoll-benchmarks already exists at $BENCHMARKS_PATH, skipping clone."
else
    echo "Cloning mucoll-benchmarks..."
    git clone git@github.com:samf25/mucoll-benchmarks.git "$BENCHMARKS_PATH"
    cd "$BENCHMARKS_PATH" && git checkout k4MuC
    echo "mucoll-benchmarks cloned and checked out to k4MuC branch."
fi

echo ""
echo "=== Setup complete ==="
echo "Directory layout:"
echo "  $MUONCOLLIDER_DIR/"
echo "  ├── mucoll-slurm/"
echo "  │   ├── mucoll-sim.sif"
echo "  │   └── ..."
echo "  ├── mucoll-benchmarks/  (k4MuC branch)"
echo "  └── output/             (created when jobs run)"
echo ""
echo "Next steps:"
echo "  1. Test interactively:  source scripts/interact.sh"
echo "  2. Enter container:     source scripts/shell_hpg.sh"
echo "  3. Load environment:    source scripts/setup.sh"
echo "  4. Submit batch jobs:   python submit_jobs.py"

#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLURM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MUONCOLLIDER_DIR="$(cd "$SLURM_DIR/.." && pwd)"

source "$SLURM_DIR/lib/image.sh"

echo "=== MuColl-SLURM setup for HiPerGator (MAIA v3.1) ==="
echo "Base directory: $MUONCOLLIDER_DIR"

# 1. Container image — nothing to pull by default
if [ -e "$MUCOLL_IMAGE" ]; then
    echo "Container image: $MUCOLL_IMAGE"
else
    echo "ERROR: container image not found at $MUCOLL_IMAGE" >&2
    echo "       The default is served from CVMFS; check that /cvmfs is mounted here." >&2
    echo "       To use a local copy instead:" >&2
    echo "         apptainer pull $SLURM_DIR/mucoll-sim.sif docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1" >&2
    echo "         export MUCOLL_IMAGE=$SLURM_DIR/mucoll-sim.sif" >&2
    exit 1
fi

# 2. Clone mucoll-benchmarks (v3.1 layout)
#
# --recurse-submodules is required: v3.1 keeps the per-geometry digi/reco steering
# in configs/<GEO>Config submodules, and setup_config.sh fails without them.
#
# This checkout is deliberately separate from any old samf25/k4MuC one — the two
# layouts are incompatible, so main and this branch can coexist. Override with
# MUCOLL_BENCHMARKS.
BENCHMARKS_PATH="${MUCOLL_BENCHMARKS:-$MUONCOLLIDER_DIR/mucoll-benchmarks-v3.1}"
if [ -d "$BENCHMARKS_PATH" ]; then
    echo "mucoll-benchmarks already exists at $BENCHMARKS_PATH, skipping clone."
else
    echo "Cloning mucoll-benchmarks (v3.1)..."
    git clone --recurse-submodules \
        https://github.com/MuonColliderSoft/mucoll-benchmarks.git "$BENCHMARKS_PATH"
fi

if [ ! -f "$BENCHMARKS_PATH/setup_config.sh" ]; then
    echo "ERROR: $BENCHMARKS_PATH has no setup_config.sh — that is the pre-v3.1 layout." >&2
    exit 1
fi
if [ -z "$(ls -A "$BENCHMARKS_PATH/configs/MAIAConfig" 2>/dev/null)" ]; then
    echo "configs/MAIAConfig is empty — fetching submodules..."
    git -C "$BENCHMARKS_PATH" submodule update --init --recursive
fi

echo ""
echo "=== Setup complete ==="
echo "Directory layout:"
echo "  $MUONCOLLIDER_DIR/"
echo "  ├── mucoll-slurm/"
echo "  ├── $(basename "$BENCHMARKS_PATH")/   (v3.1: setup_config.sh + configs/ submodules)"
echo "  └── output/                (created when jobs run)"
echo ""
echo "Next steps:"
echo "  1. Allocate a node:     source scripts/interact_hpg.sh"
echo "  2. Enter container:     source scripts/shell_hpg.sh"
echo "  3. Load environment:    source scripts/setup.sh"
echo "  4. Submit batch jobs:   python submit.py --list"

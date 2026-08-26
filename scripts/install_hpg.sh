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

# Pinned, deliberately. Two reasons:
#   1. Reproducibility — an unpinned clone means every install gets a different
#      detector/steering configuration, so two people "running the same sample"
#      silently run different physics.
#   2. Upstream main is not always green. Commit 2724176 (2026-08-18, "enable rng
#      seed for pgun") left generation/pgun/pgun_edm4hep.py:160 indented with a
#      space followed by a tab; Python rejects that outright (TabError), so the
#      whole pgun sample dies at GEN on any checkout at or after it.
# ce72cf0 (2026-08-15, "bumped MAIA config") is the revision every production in
# PRODUCTION_LOG.md was generated against. Bump it deliberately, not by accident.
BENCHMARKS_REF_DEFAULT=ce72cf07c513bf845d78635236367fc561e98f70
BENCHMARKS_REF="${MUCOLL_BENCHMARKS_REF:-$BENCHMARKS_REF_DEFAULT}"

if [ -d "$BENCHMARKS_PATH" ]; then
    echo "mucoll-benchmarks already exists at $BENCHMARKS_PATH, skipping clone."
    have=$(git -C "$BENCHMARKS_PATH" rev-parse HEAD 2>/dev/null || echo unknown)
    if [ "$have" != "$BENCHMARKS_REF" ]; then
        echo "  NOTE: it is at $have, not the pinned $BENCHMARKS_REF."
        echo "        To move it:  git -C $BENCHMARKS_PATH checkout $BENCHMARKS_REF \\"
        echo "                     && git -C $BENCHMARKS_PATH submodule update --init --recursive"
    fi
else
    echo "Cloning mucoll-benchmarks (v3.1) at pinned $BENCHMARKS_REF ..."
    git clone https://github.com/MuonColliderSoft/mucoll-benchmarks.git "$BENCHMARKS_PATH"
    git -C "$BENCHMARKS_PATH" checkout --quiet "$BENCHMARKS_REF"
    # Submodule pointers are per-commit, so init them AFTER checking out the pin.
    git -C "$BENCHMARKS_PATH" submodule update --init --recursive
fi

if [ ! -f "$BENCHMARKS_PATH/setup_config.sh" ]; then
    echo "ERROR: $BENCHMARKS_PATH has no setup_config.sh — that is the pre-v3.1 layout." >&2
    exit 1
fi
if [ -z "$(ls -A "$BENCHMARKS_PATH/configs/MAIAConfig" 2>/dev/null)" ]; then
    echo "configs/MAIAConfig is empty — fetching submodules..."
    git -C "$BENCHMARKS_PATH" submodule update --init --recursive
fi

# Guard against a syntactically broken upstream (see the pin note above). This is
# cheap and catches the failure here, at install time, instead of at GEN inside a
# batch job where it looks like a problem with this framework.
PGUN="$BENCHMARKS_PATH/generation/pgun/pgun_edm4hep.py"
if [ -f "$PGUN" ] && ! python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$PGUN" 2>/dev/null; then
    echo "ERROR: $PGUN does not parse as Python." >&2
    echo "       You are on a benchmarks revision with a known upstream breakage." >&2
    echo "       Use the pinned revision:" >&2
    # Name the known-good default, NOT $BENCHMARKS_REF — under MUCOLL_BENCHMARKS_REF
    # that is the very revision that just failed to parse.
    echo "         git -C $BENCHMARKS_PATH checkout $BENCHMARKS_REF_DEFAULT" >&2
    echo "         git -C $BENCHMARKS_PATH submodule update --init --recursive" >&2
    exit 1
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
echo "  3. Load environment:    source lib/env.sh"
echo "  4. Submit batch jobs:   python3 submit.py --list"

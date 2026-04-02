#!/bin/bash
# Build MuMuToZH inside the Apptainer container.
#
# Prerequisites: source scripts/setup.sh first (loads the Spack stack).
#
# Usage (from inside the container):
#   cd pythia && bash build.sh
#
# Or from the repo root:
#   bash pythia/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Locate HepMC3 from Spack.  After sourcing the mucoll-stack setup, the
# hepmc3 headers and libs live under the Spack view.  pythia8-config should
# already be on PATH.
if ! command -v pythia8-config &>/dev/null; then
    echo "Error: pythia8-config not found. Did you source scripts/setup.sh?"
    exit 1
fi

# Find HepMC3 directory from Spack
if [ -z "$HEPMC3_DIR" ]; then
    HEPMC3_HEADER=$(find /opt/spack -name "GenEvent.h" -path "*/HepMC3/*" 2>/dev/null | head -1)
    if [ -n "$HEPMC3_HEADER" ]; then
        # Header is at <prefix>/include/HepMC3/GenEvent.h — go up 3 levels
        export HEPMC3_DIR="$(dirname "$(dirname "$(dirname "$HEPMC3_HEADER")")")"
    else
        echo "Error: Could not find HepMC3. Set HEPMC3_DIR manually."
        exit 1
    fi
fi

echo "Using HEPMC3_DIR=$HEPMC3_DIR"
echo "Using pythia8-config=$(command -v pythia8-config)"

cd "$SCRIPT_DIR"
make clean
make

echo ""
echo "Build successful: $(ls -lh MuMuToZH | awk '{print $5, $NF}')"
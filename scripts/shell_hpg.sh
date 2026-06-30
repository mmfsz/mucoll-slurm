#!/bin/bash

BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPTAINER_IMAGE="$BASEDIR/mucoll-sim.sif"

if [ ! -f "$APPTAINER_IMAGE" ]; then
    echo "Container image not found at $APPTAINER_IMAGE"
    echo "Pull it first with:"
    echo "  apptainer pull $APPTAINER_IMAGE docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main"
    return 1 2>/dev/null || exit 1
fi

# --cleanenv: don't inherit the host environment. interact_hpg.sh runs `module load
# python`, which sets PYTHONHOME=/apps/python/3.10 on the host; without --cleanenv that
# leaks into the container and breaks the spack Python ("No module named 'encodings'").
# Matches the batch convention (submit.py always passes --cleanenv).
apptainer shell --cleanenv "$APPTAINER_IMAGE"

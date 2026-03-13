#!/bin/bash

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
APPTAINER_IMAGE="$BASEDIR/mucoll-sim.sif"

if [ ! -f "$APPTAINER_IMAGE" ]; then
    echo "Container image not found at $APPTAINER_IMAGE"
    echo "Pull it first with:"
    echo "  apptainer pull $APPTAINER_IMAGE docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main"
    exit 1
fi

apptainer shell --cleanenv "$APPTAINER_IMAGE"

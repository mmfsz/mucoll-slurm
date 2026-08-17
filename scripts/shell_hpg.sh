#!/bin/bash

BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$BASEDIR/lib/image.sh"

# An unpacked CVMFS image is a directory; a pulled .sif is a file.
if [ ! -e "$MUCOLL_IMAGE" ]; then
    echo "Container image not found at $MUCOLL_IMAGE"
    echo "The default lives on CVMFS — check that /cvmfs is mounted on this node."
    echo "To use a local copy instead:"
    echo "  apptainer pull $BASEDIR/mucoll-sim.sif docker://ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1"
    echo "  MUCOLL_IMAGE=$BASEDIR/mucoll-sim.sif source scripts/shell_hpg.sh"
    return 1 2>/dev/null || exit 1
fi

# --cleanenv: don't inherit the host environment. interact_hpg.sh runs `module load
# python`, which sets PYTHONHOME=/apps/python/3.10 on the host; without --cleanenv that
# leaks into the container and breaks the spack Python ("No module named 'encodings'").
# Matches the batch convention (submit.py always passes --cleanenv).
apptainer shell --cleanenv $MUCOLL_BINDS "$MUCOLL_IMAGE"

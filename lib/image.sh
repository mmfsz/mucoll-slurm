#!/bin/bash
# lib/image.sh — THE one place the container image is named.
#
# Source this (do not exec). The shell entry points source it; submit.py and
# make_gridpack.py read the same literal via mucoll_image.py, so there is exactly
# one string to change on an image bump.
#
# Override per invocation without editing anything:
#   MUCOLL_IMAGE=/path/to/mucoll-sim.sif ./scripts/shell_hpg.sh
#
# The default is the v3.1 release unpacked on CVMFS: nothing to pull, no 9 GB
# .sif to keep in sync, and every compute node sees identical bytes. A locally
# pulled .sif still works — point MUCOLL_IMAGE at it.
export MUCOLL_IMAGE="${MUCOLL_IMAGE:-/cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1-amd64}"

# Bind /cvmfs so a CVMFS-hosted image can resolve its own layers inside the
# container. Harmless for a local .sif.
export MUCOLL_BINDS="${MUCOLL_BINDS:---bind /cvmfs}"

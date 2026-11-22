#!/bin/bash
# Build the k4ext Gaudi components against the container's spack stack. Run INSIDE the
# MAIA image (v3.2); rebuild after every image bump, like pythia/. Installs to k4ext/install/.
set -e
K="$(cd "$(dirname "$0")" && pwd)"
source "$K/../lib/env.sh"
cmake -S "$K/ConeSeeds" -B "$K/build/ConeSeeds" -G Ninja \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$K/install"
cmake --build "$K/build/ConeSeeds"
cmake --install "$K/build/ConeSeeds"

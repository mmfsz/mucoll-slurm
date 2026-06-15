#!/bin/bash
# lib/env.sh — single source of truth for the in-container software environment.
#
# Source this (do not exec). Sourced by run_chain.sh and the gen/ plugins.
# Replaces the spack/Whizard paths that were copy-pasted into ~9 chain scripts.

_ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLURM_DIR="$(dirname "$_ENV_DIR")"

# --- Spack software stack (mucoll-stack) ---
# The spack setup path lives in scripts/setup.sh (the one canonical copy).
source "$SLURM_DIR/scripts/setup.sh"

# --- Whizard shared libraries ---
# THE one place this path is defined. Update here on a container/image bump.
export WHIZARD_LIB="/opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/whizard-3.1.5-2wpmahrsf5vaircj7tmf5hdo5fwz2hhw/lib"
export LD_LIBRARY_PATH="$WHIZARD_LIB:$LD_LIBRARY_PATH"

# Add HepMC3 libraries to LD_LIBRARY_PATH (needed by the standalone pythia/
# binaries). Discovered dynamically from the spack tree so it survives image bumps.
add_hepmc3_libs() {
    local hdr
    hdr=$(find /opt/spack -name "GenEvent.h" -path "*/HepMC3/*" 2>/dev/null | head -1)
    if [ -n "$hdr" ]; then
        local d
        d="$(dirname "$(dirname "$(dirname "$hdr")")")"
        export LD_LIBRARY_PATH="${d}/lib:$LD_LIBRARY_PATH"
    fi
}

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
# Discovered from the spack tree rather than hardcoded: the spack hash changes on
# every image rebuild even when the Whizard version does not (v3.0 and v3.1 both
# ship 3.1.5 under different hashes), so a pasted path silently rots.
WHIZARD_LIB="$(ls -d /opt/spack/opt/spack/*/*/*/*/linux-x86_64/whizard-*/lib 2>/dev/null | head -1)"
if [ -n "$WHIZARD_LIB" ]; then
    export WHIZARD_LIB
    export LD_LIBRARY_PATH="$WHIZARD_LIB:$LD_LIBRARY_PATH"
else
    echo "WARN: no whizard lib directory found under /opt/spack — generation will fail" >&2
fi

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

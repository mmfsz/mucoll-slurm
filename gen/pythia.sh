#!/bin/bash
# gen/pythia.sh — standalone Pythia8 ZH generator (pythia/MuMuToZH), Z->bb H->bb.
# For generator comparison vs the Whizard ZH chain. No card.
generate() {
    local bin="$SLURM_DIR/pythia/MuMuToZH"
    [ -x "$bin" ] || { echo "ERROR: $bin not found/executable (build: pythia/build.sh)" >&2; return 1; }
    add_hepmc3_libs
    "$bin" "$NEVENTS" "$JOB_ID" gen_output.hepmc
    GEN_EXT=hepmc
}

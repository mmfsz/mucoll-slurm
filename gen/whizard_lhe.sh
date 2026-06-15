#!/bin/bash
# gen/whizard_lhe.sh — LHE route: Whizard writes parton-level LHE (ME only),
# then standalone Pythia8 (pythia/LheToHepMC) decays + showers -> HepMC.
# Fully decouples the matrix element from showering/decay.
generate() {
    cp "$CARD" ./job.sin
    sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
    sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin
    apply_gridpack
    whizard job.sin
    local lhe
    lhe=$(ls -1 *.lhe *.lhef 2>/dev/null | head -1)
    [ -n "$lhe" ] || { echo "ERROR: Whizard produced no LHE file" >&2; return 1; }
    echo "Whizard wrote LHE: $lhe"
    local bin="$SLURM_DIR/pythia/LheToHepMC"
    [ -x "$bin" ] || { echo "ERROR: $bin not found/executable (build: pythia/build.sh)" >&2; return 1; }
    add_hepmc3_libs
    "$bin" "$lhe" "$NEVENTS" "$JOB_ID" gen_output.hepmc
    GEN_EXT=hepmc
}

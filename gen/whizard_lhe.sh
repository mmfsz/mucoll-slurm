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
    # Optional per-card decay directive: a line like
    #   # LHE_DECAY: 23:mayDecay = on; 23:onMode = off; 23:onIfAny = 1 2 3 4 5
    # selects the Pythia8 resonance decay channel. Read it from the ORIGINAL card
    # (not the seded job.sin, though it survives there too) and pass as a 5th arg.
    # If absent, LheToHepMC falls back to its hardcoded ZH default (Z->bb, H->bb),
    # so omitting the arg keeps the existing ZH_bbbb_lhe behaviour unchanged.
    local decay_cfg
    decay_cfg=$(sed -n 's/^[[:space:]]*#[[:space:]]*LHE_DECAY:[[:space:]]*//p' "$CARD" | head -1)
    if [ -n "$decay_cfg" ]; then
        echo "LHE_DECAY directive: $decay_cfg"
        "$bin" "$lhe" "$NEVENTS" "$JOB_ID" gen_output.hepmc "$decay_cfg"
    else
        "$bin" "$lhe" "$NEVENTS" "$JOB_ID" gen_output.hepmc
    fi
    GEN_EXT=hepmc
}

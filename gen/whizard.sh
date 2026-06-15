#!/bin/bash
# gen/whizard.sh — Whizard matrix element + Pythia8 shower/hadronization -> HepMC.
# Covers all card-based samples except the LHE route (resonant + inclusive alike;
# the card itself encodes which). Reads: CARD, JOB_ID, NEVENTS, GRIDPACK_DIR.
# Produces gen_output.hepmc and sets GEN_EXT.
generate() {
    cp "$CARD" ./job.sin
    sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
    sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin
    apply_gridpack
    whizard job.sin
    # Whizard names output by the card's $sample string; normalize whatever it wrote.
    local out
    out=$(ls -1 *.hepmc 2>/dev/null | head -1)
    [ -n "$out" ] || { echo "ERROR: Whizard produced no .hepmc" >&2; return 1; }
    [ "$out" = "gen_output.hepmc" ] || mv "$out" gen_output.hepmc
    GEN_EXT=hepmc
}

#!/bin/bash
# gen/pgun.sh — particle gun (benchmarks pgun_edm4hep.py). No card.
# EXTRA = (PDG PT THETA_MIN THETA_MAX), defaults 11 100 10 170.
generate() {
    local PDG=${EXTRA[0]:-11} PT=${EXTRA[1]:-100} TMIN=${EXTRA[2]:-10} TMAX=${EXTRA[3]:-170}
    echo "pgun: PDG=$PDG pT=$PT theta=[$TMIN,$TMAX]"
    python "$BENCH/generation/pgun/pgun_edm4hep.py" \
        -p 1 -e "$NEVENTS" --pdg "$PDG" --pt "$PT" --theta "$TMIN" "$TMAX" \
        -- gen_output.edm4hep.root
    GEN_EXT=edm4hep.root
}

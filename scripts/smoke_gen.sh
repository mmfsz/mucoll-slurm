#!/bin/bash
# smoke_gen.sh <SAMPLE_KEY> [NEVENTS] — GEN-stage-only smoke test of a sample
# through the new framework (env.sh + stages.sh + gen plugin). Confirms the card
# integrates and produces a HepMC. Run inside the container.
set -e
SLURM_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MUONCOLLIDER_DIR="$(dirname "$SLURM_DIR")"
BENCH="$MUONCOLLIDER_DIR/mucoll-benchmarks"
KEY=$1; NEVENTS=${2:-2}
GRIDPACK_BASE="$MUONCOLLIDER_DIR/output/gridpacks"

read -r GEN_TYPE CARD_NAME GRIDPACK_NAME < <(
    awk -v k="$KEY" '!/^#/ && NF && $1==k {print $2,$3,$4; exit}' "$SLURM_DIR/samples.conf")
CARD="$SLURM_DIR/cards/production/$CARD_NAME"
GRIDPACK_DIR=""
[ "$GRIDPACK_NAME" != "-" ] && ls "$GRIDPACK_BASE/$GRIDPACK_NAME"/*.vg >/dev/null 2>&1 \
    && GRIDPACK_DIR="$GRIDPACK_BASE/$GRIDPACK_NAME"

JOB_ID=0
source "$SLURM_DIR/lib/env.sh"
source "$SLURM_DIR/lib/stages.sh"
source "$SLURM_DIR/gen/${GEN_TYPE}.sh"
WORKDIR=/tmp/smoke_${KEY}_$$; mkdir -p "$WORKDIR"; cd "$WORKDIR"
echo ">>> smoke GEN: key=$KEY card=$CARD_NAME gridpack=${GRIDPACK_DIR:-none} nev=$NEVENTS"
generate
echo ">>> produced:"; ls -la gen_output.* 2>/dev/null
echo ">>> first HepMC event marker:"; grep -m1 "^E " gen_output.hepmc 2>/dev/null || head -3 gen_output.hepmc
cd /; rm -rf "$WORKDIR"
echo ">>> OK: $KEY"

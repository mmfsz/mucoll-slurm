#!/bin/bash
set -e
# run_chain.sh — single dispatcher for the full GEN->SIM->DIGI->RECO chain.
#
#   run_chain.sh <SAMPLE_KEY> <JOB_ID> <NEVENTS> <OUTPUT_DIR> <BENCHMARKS_PATH> [extra...]
#
# Looks <SAMPLE_KEY> up in samples.conf to learn the generator type, the Whizard
# card, and the gridpack, then runs the shared pipeline. The only per-sample
# variation lives in the manifest and the gen/ plugin; everything else is shared.
#
# Env overrides: GRIDPACK_BASE (default <muoncollider>/output/gridpacks),
#                MUCOLL_GEOMETRY (default MAIA_v0),
#                RUN_TAG (optional label appended to the output sub-directory, e.g.
#                         to distinguish productions of the same sample).

SAMPLE_KEY=$1; JOB_ID=$2; NEVENTS=$3; OUTPUT_DIR=$4; BENCH=$5
shift 5 || true
EXTRA=("$@")

[ -n "$SAMPLE_KEY" ] && [ -n "$BENCH" ] || {
    echo "Usage: run_chain.sh <SAMPLE_KEY> <JOB_ID> <NEVENTS> <OUTPUT_DIR> <BENCHMARKS_PATH> [extra...]" >&2
    exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLURM_DIR="$SCRIPT_DIR"
MUONCOLLIDER_DIR="$(dirname "$SLURM_DIR")"
MANIFEST="$SLURM_DIR/samples.conf"
GRIDPACK_BASE="${GRIDPACK_BASE:-$MUONCOLLIDER_DIR/output/gridpacks}"
GEO="${MUCOLL_GEOMETRY:-MAIA_v0}"

[ -f "$MANIFEST" ] || { echo "ERROR: manifest not found: $MANIFEST" >&2; exit 1; }

# Look up the manifest row (whitespace-delimited; '#' comments, blanks ignored).
read -r GEN_TYPE CARD_NAME GRIDPACK_NAME < <(
    awk -v k="$SAMPLE_KEY" '!/^#/ && NF && $1==k {print $2, $3, $4; exit}' "$MANIFEST")
[ -n "$GEN_TYPE" ] || { echo "ERROR: sample '$SAMPLE_KEY' not in $MANIFEST" >&2; exit 1; }

echo "=== $SAMPLE_KEY | gen=$GEN_TYPE card=$CARD_NAME gridpack=$GRIDPACK_NAME | job=$JOB_ID nev=$NEVENTS ==="

# Resolve the card: our git-tracked cards/production first, then benchmarks.
CARD=""
if [ "$CARD_NAME" != "-" ]; then
    if   [ -f "$SLURM_DIR/cards/production/$CARD_NAME" ]; then
        CARD="$SLURM_DIR/cards/production/$CARD_NAME"
    elif [ -f "$BENCH/generation/signal/whizard/$CARD_NAME" ]; then
        CARD="$BENCH/generation/signal/whizard/$CARD_NAME"
    else
        echo "ERROR: card '$CARD_NAME' not found in cards/production or benchmarks" >&2
        exit 1
    fi
fi

# Resolve the gridpack dir; use only if it actually contains .vg grids.
GRIDPACK_DIR=""
if [ "$GRIDPACK_NAME" != "-" ]; then
    cand="$GRIDPACK_BASE/$GRIDPACK_NAME"
    if ls "$cand"/*.vg >/dev/null 2>&1; then
        GRIDPACK_DIR="$cand"
    else
        echo "NOTE: no grids at $cand — running full phase-space integration" >&2
    fi
fi

# Environment, shared stages, detector geometry, and the generator plugin.
source "$SLURM_DIR/lib/env.sh"
source "$SLURM_DIR/lib/stages.sh"
source "$BENCH/k4MuCPlayground/setup_digireco.sh" "$BENCH" "$GEO"
[ -f "$SLURM_DIR/gen/${GEN_TYPE}.sh" ] || { echo "ERROR: unknown gen_type '$GEN_TYPE'" >&2; exit 1; }
source "$SLURM_DIR/gen/${GEN_TYPE}.sh"

setup_workdir "$JOB_ID"
cp -r "$BENCH/reconstruction/PandoraSettings/" ./

echo "--- Generation ($GEN_TYPE) ---"
t=$SECONDS; generate; echo "Generation took $((SECONDS - t))s"

stage_sim_digi_reco "$BENCH" "$NEVENTS" "gen_output.*"

# Output sub-directory is the sample key, optionally suffixed with RUN_TAG.
OUTPUT_TAG="$SAMPLE_KEY"
[ -n "$RUN_TAG" ] && OUTPUT_TAG="${SAMPLE_KEY}_${RUN_TAG}"
move_outputs "$OUTPUT_DIR" "$JOB_ID" "$OUTPUT_TAG" "$GEN_EXT"
cleanup_workdir

echo "Job $JOB_ID ($OUTPUT_TAG) finished successfully. Total=${SECONDS}s"

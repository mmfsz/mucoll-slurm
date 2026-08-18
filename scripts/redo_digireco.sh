#!/bin/bash
# redo_digireco.sh <JOB_DIR> [NEVENTS] — re-run DIGI + RECO over a job's existing
# sim output, replacing that job's digi/reco files in place.
#
# Written to repair productions whose digi/reco were truncated to 10 events by
# v3.1's build_application(evt_max=10) default (see lib/stages.sh), but it is
# generally useful whenever simulation is still good and only the downstream
# steering changed — SIM is by far the expensive stage.
#
# Run inside the container. Work happens in node scratch and the results are
# only moved into place after their event count is verified, so an interrupted
# run leaves the original files untouched.
set -e

JOB_DIR=$1
NEVENTS=${2:-50}
[ -d "$JOB_DIR" ] || { echo "ERROR: no such job dir: $JOB_DIR" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCH="${MUCOLL_BENCHMARKS:-$(dirname "$SCRIPT_DIR")/mucoll-benchmarks-v3.1}"
GEO="${MUCOLL_GEOMETRY:-MAIA_v0}"

sim=$(ls "$JOB_DIR"/sim_output_*.edm4hep.root 2>/dev/null | head -1)
[ -n "$sim" ] || { echo "ERROR: no sim_output in $JOB_DIR" >&2; exit 2; }
idx=$(basename "$sim" .edm4hep.root); idx=${idx#sim_output_}

source "$SCRIPT_DIR/lib/env.sh"
source "$BENCH/setup_config.sh" "$BENCH" "$GEO" >/dev/null
CONFIG="$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME"

base=/tmp
[ -n "${SLURM_JOB_ID:-}" ] && [ -d "/scratch/local/$SLURM_JOB_ID" ] && base="/scratch/local/$SLURM_JOB_ID"
WORK="$base/redo_${idx}_$$"; mkdir -p "$WORK"; cd "$WORK"
trap 'cd /; rm -rf "$WORK"' EXIT

echo "=== redo digi+reco: $JOB_DIR (job $idx, $NEVENTS events) ==="
t=$SECONDS
k4run "$CONFIG/digi_steer.py" -n "$NEVENTS" \
    --IOSvc.Input "$sim" --IOSvc.Output digi_new.edm4hep.root
echo "Digitization took $((SECONDS - t))s"

t=$SECONDS
k4run "$CONFIG/reco_steer.py" -n "$NEVENTS" \
    --IOSvc.Input digi_new.edm4hep.root --IOSvc.Output reco_new.edm4hep.root
echo "Reconstruction took $((SECONDS - t))s"

# Verify both files carry the expected number of events before replacing anything.
for f in digi_new reco_new; do
    n=$(python3 -c "
from podio.reading import get_reader
print(len(get_reader('$WORK/$f.edm4hep.root').get('events')))" 2>/dev/null)
    echo "  $f: $n events"
    [ "$n" = "$NEVENTS" ] || { echo "ERROR: $f has $n events, expected $NEVENTS — leaving originals alone" >&2; exit 3; }
done

mv digi_new.edm4hep.root "$JOB_DIR/digi_output_${idx}.edm4hep.root"
mv reco_new.edm4hep.root "$JOB_DIR/reco_output_${idx}.edm4hep.root"
echo "Replaced digi/reco in $JOB_DIR"

#!/bin/bash
# bib_digireco.sh <SIM_FILE> <FIRST> <NEV> <OUT_DIR> <BIB_N> <SEED> [options]
#
# DIGI + RECO of NEV events of an existing sim file, starting at entry FIRST, with
# BIB_N beam-induced-background files per beam overlaid at DIGI (1666 = 100 % BIB;
# 0 = no overlay, the no-BIB twin of the same events). SIM is reused untouched — BIB
# enters only at digitisation, so every BIB event has a no-BIB twin.
#
# Options:
#   --split            run digi_steer.py then reco_steer.py (per-stage timing and
#                      memory, for benchmarking); default is the single-process
#                      digi_reco_steer.py, which never writes the ~1 GB/event digi file
#   --keep-digi        with --split, also keep the digi file
#   --keep-hits        keep the hit collections in the reco output (--keepEverything)
#   --calo-coning      --doCaloConing (truth cone, 0.6 rad, before the BIB selection)
#   --tracker-coning   --doTrackerConing (truth helix cones, 30 mm)
#
# Each k4run is wrapped to print a "STAGE <name> wall_s=… maxrss_gb=… rc=…" line,
# which scripts/bib_bench_summary.py parses. Run inside the container. Output:
#   <OUT_DIR>/reco_output_e<FIRST>.edm4hep.root   (moved in only after its event count checks out)
set -e

SIM=$1; FIRST=$2; NEV=$3; OUT_DIR=$4; BIB_N=$5; SEED=$6
shift 6 || { echo "usage: $0 SIM FIRST NEV OUT_DIR BIB_N SEED [options]" >&2; exit 2; }
SPLIT=0; KEEP_DIGI=0; KEEP_HITS=0; CONING=(); RECO_CONING=()
while [ $# -gt 0 ]; do
    case $1 in
        --split) SPLIT=1 ;;
        --keep-digi) KEEP_DIGI=1 ;;
        --keep-hits) KEEP_HITS=1 ;;
        --calo-coning) CONING+=(--doCaloConing) ;;
        --tracker-coning) CONING+=(--doTrackerConing); RECO_CONING+=(--doTrackerConing) ;;
        *) echo "ERROR: unknown option $1" >&2; exit 2 ;;
    esac
    shift
done
[ -f "$SIM" ] || { echo "ERROR: no such sim file: $SIM" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCH="${MUCOLL_BENCHMARKS:-$(dirname "$SCRIPT_DIR")/mucoll-benchmarks-v3.2}"
GEO="${MUCOLL_GEOMETRY:-MAIA_v0}"
BIB_DIR="${MUCOLL_BIB:-/blue/avery/share/mucol/bib/BIB_v9}"
CPUS="${SLURM_CPUS_PER_TASK:-1}"

source "$SCRIPT_DIR/lib/env.sh"
source "$BENCH/setup_config.sh" "$BENCH" "$GEO" >/dev/null
CONFIG="$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME"

# Overlay arguments. The overlay globs *.root in each directory and draws BIB_N
# distinct files per beam per event, seeded by (RandSeed, event number, run number);
# event numbers repeat across sim files, so SEED must differ between jobs.
OVERLAY=()
if [ "$BIB_N" -gt 0 ]; then
    for beam in sim_mp sim_mm; do
        n=$(find "$BIB_DIR/$beam" -maxdepth 1 -name '*.root' | wc -l)
        [ "$n" -ge "$BIB_N" ] || { echo "ERROR: $BIB_DIR/$beam has $n files, need >= $BIB_N" >&2; exit 2; }
    done
    OVERLAY=(--doOverlayFull --OverlayFullNumberBackground "$BIB_N"
             --OverlayFullPathToMuPlus "$BIB_DIR/sim_mp/"
             --OverlayFullPathToMuMinus "$BIB_DIR/sim_mm/")
fi
# In RECO --doOverlayFull only drops the hit collections from the output (they are
# >1 GB/event with BIB); --keepEverything keeps them.
SLIM=()
[ "$BIB_N" -gt 0 ] && SLIM=(--doOverlayFull)
[ "$KEEP_HITS" = 1 ] && SLIM+=(--keepEverything)

# Same scratch logic as redo_digireco.sh (HPG's /scratch/local/$SLURM_JOB_ID is not
# writable; /tmp is a large node-local disk).
base=/tmp
[ -n "${SLURM_TMPDIR:-}" ] && [ -w "${SLURM_TMPDIR:-}" ] && base="$SLURM_TMPDIR"
[ -n "${SLURM_JOB_ID:-}" ] && [ -w "/scratch/local/$SLURM_JOB_ID" ] && base="/scratch/local/$SLURM_JOB_ID"
WORK="$base/bib_${SLURM_JOB_ID:-local}_$$"
mkdir -p "$WORK"
cd "$WORK"
trap 'cd /; rm -rf "$WORK"' EXIT

# Run a command, then report its wall time and the peak RSS of its process tree.
stage() {
    local name=$1; shift
    python3 - "$name" "$@" <<'EOF'
import resource, subprocess, sys, time
name, cmd = sys.argv[1], sys.argv[2:]
t0 = time.time()
rc = subprocess.call(cmd)
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024**2  # kB -> GB
print(f"STAGE {name} wall_s={time.time() - t0:.0f} maxrss_gb={rss:.2f} rc={rc}", flush=True)
sys.exit(rc)
EOF
}

COMMON=(-n "$NEV" --IOSvc.FirstEventEntry "$FIRST")
echo "=== bib_digireco: $SIM entries [$FIRST, $((FIRST + NEV))) BIB_N=$BIB_N seed=$SEED" \
     "split=$SPLIT coning=[${CONING[*]}] cpus=$CPUS host=$(hostname) ==="
if [ "$SPLIT" = 1 ]; then
    stage digi k4run "$CONFIG/digi_steer.py" "${COMMON[@]}" --RandSeed "$SEED" \
        "${OVERLAY[@]}" "${CONING[@]}" \
        --inputFiles "$SIM" --outputFile digi.edm4hep.root --histoFile digi_histos.root
    echo "STAGE_SIZE digi_mb=$(( $(stat -c %s digi.edm4hep.root) / 1048576 ))"
    # A 100 % BIB digi event is ~2.3 GB compressed. ROOT sizes its default TTreeCache to
    # the entry, overflows a 32-bit int and throws std::bad_alloc on the first read, so
    # turn the cache off for RECO (ROOT reads ./.rootrc; we are in $WORK).
    echo "TTreeCache.Size: 0" > .rootrc
    # The digi file holds only the NEV processed events, so RECO starts at entry 0.
    stage reco k4run "$CONFIG/reco_steer.py" -n "$NEV" "${SLIM[@]}" "${RECO_CONING[@]}" \
        --TrackingThreads "$CPUS" \
        --inputFiles digi.edm4hep.root --outputFile reco.edm4hep.root --histoFile reco_histos.root
else
    stage digireco k4run "$CONFIG/digi_reco_steer.py" "${COMMON[@]}" --RandSeed "$SEED" \
        "${OVERLAY[@]}" "${SLIM[@]}" "${CONING[@]}" --TrackingThreads "$CPUS" \
        --inputFiles "$SIM" --outputFile reco.edm4hep.root --histoFile reco_histos.root
fi
echo "STAGE_SIZE reco_mb=$(( $(stat -c %s reco.edm4hep.root) / 1048576 ))"

n=$(python3 -c "
from podio.reading import get_reader
print(len(get_reader('$WORK/reco.edm4hep.root').get('events')))" 2>/dev/null)
echo "  reco: $n events"
[ "$n" = "$NEV" ] || { echo "ERROR: reco has $n events, expected $NEV" >&2; exit 3; }

mkdir -p "$OUT_DIR"
mv reco.edm4hep.root "$OUT_DIR/reco_output_e${FIRST}.edm4hep.root"
[ "$KEEP_DIGI" = 1 ] && [ -f digi.edm4hep.root ] && mv digi.edm4hep.root "$OUT_DIR/digi_output_e${FIRST}.edm4hep.root"
echo "Wrote $OUT_DIR/reco_output_e${FIRST}.edm4hep.root"

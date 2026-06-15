#!/bin/bash
set -e

# Usage:
#   run_chain_ZH.sh <JOB_ID> <NEVENTS> <OUTPUT_DIR> <MUCOLL_BENCHMARKS_PATH> [SET]
#
# SET selects the steering variant:
#   1 (default) -> mumu_ZHbbbb_10TeV.sin            (unstable Z/H decay in Whizard)
#   2           -> mumu_ZHbbbb_hybrid_10TeV.sin     (stable Z/H, Pythia8 decays Z->bb H->bb)
#   3           -> mumu_ZHbbbb_hybrid_noCR_10TeV.sin (hybrid + CR off; diagnostic)
#   4           -> mumu_ZHbbbb_hybrid_skI_10TeV.sin  (hybrid + SK-I CR model, mode=3)
#   5           -> mumu_ZHbbbb_lhe_10TeV.sin         (LHE route: Whizard ME only -> Pythia8 shower)

JOB_ID=$1
NEVENTS=$2
OUTPUT_DIR=$3
MUCOLL_BENCHMARKS_PATH=$4
SET=${5:-1}

case "$SET" in
  1) SAMPLE_NAME="mumu_ZHbbbb_10TeV";           TAG="ZH" ;;
  2) SAMPLE_NAME="mumu_ZHbbbb_hybrid_10TeV";    TAG="ZH_hybrid" ;;
  3) SAMPLE_NAME="mumu_ZHbbbb_hybrid_noCR_10TeV"; TAG="ZH_hybrid_noCR" ;;
  4) SAMPLE_NAME="mumu_ZHbbbb_hybrid_skI_10TeV";  TAG="ZH_hybrid_skI" ;;
  5) SAMPLE_NAME="mumu_ZHbbbb_lhe_10TeV";         TAG="ZH_lhe" ;;
  *) echo "Unknown SET=$SET (use 1-5)"; exit 1 ;;
esac

echo "Starting job $JOB_ID with $NEVENTS events (ZH, SET=$SET -> $SAMPLE_NAME)"
echo "Output directory: $OUTPUT_DIR"
echo "Benchmarks path: $MUCOLL_BENCHMARKS_PATH"
echo "Sample: $SAMPLE_NAME"

# Source the main environment setup
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/scripts/setup.sh"

# Setup detector geometry and PYTHONPATH for digi/reco steering files.
source $MUCOLL_BENCHMARKS_PATH/k4MuCPlayground/setup_digireco.sh $MUCOLL_BENCHMARKS_PATH MAIA_v0

# Create a temporary working directory
WORKDIR=/tmp/mucoll_job_${JOB_ID}_${RANDOM}
mkdir -p $WORKDIR
cd $WORKDIR
echo "Working in $WORKDIR"

# Whizard needs its libraries on LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/whizard-3.1.5-2wpmahrsf5vaircj7tmf5hdo5fwz2hhw/lib:$LD_LIBRARY_PATH

# Copy PandoraSettings needed for reconstruction
cp -r $MUCOLL_BENCHMARKS_PATH/reconstruction/PandoraSettings/ ./

# --- 1. Generation ---
T_START=$SECONDS
echo "Running Generation..."

if [ "$SET" -eq 5 ]; then
  # LHE route: Whizard produces parton-level LHE, then Pythia8 showers/hadronizes

  # Step 1a: Whizard — matrix element only, output LHE
  cp $MUCOLL_BENCHMARKS_PATH/generation/signal/whizard/${SAMPLE_NAME}.sin ./job.sin
  sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
  sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin
  whizard job.sin
  # Whizard writes <sample>.lhe (or .lhef); find it
  LHE_FILE=$(ls ${SAMPLE_NAME}.lhe 2>/dev/null || ls ${SAMPLE_NAME}.lhef 2>/dev/null || echo "")
  if [ -z "$LHE_FILE" ]; then
    echo "ERROR: Whizard did not produce an LHE file for ${SAMPLE_NAME}" >&2
    exit 1
  fi
  echo "Whizard produced LHE file: $LHE_FILE"

  # Step 1b: Pythia8 — read LHE, decay Z/H -> bb, shower, hadronize, write HepMC
  # Locate the LheToHepMC binary (pre-built inside the container)
  LHEHEPMC_BIN="$SCRIPT_DIR/pythia/LheToHepMC"
  if [ ! -x "$LHEHEPMC_BIN" ]; then
    echo "ERROR: LheToHepMC binary not found or not executable at $LHEHEPMC_BIN" >&2
    echo "Build it first: cd mucoll-slurm && apptainer exec ... bash pythia/build.sh" >&2
    exit 1
  fi

  # Ensure HepMC3 shared libraries are visible
  HEPMC3_HEADER=$(find /opt/spack -name "GenEvent.h" -path "*/HepMC3/*" 2>/dev/null | head -1)
  if [ -n "$HEPMC3_HEADER" ]; then
    HEPMC3_DIR="$(dirname "$(dirname "$(dirname "$HEPMC3_HEADER")")")"
    export LD_LIBRARY_PATH=${HEPMC3_DIR}/lib:$LD_LIBRARY_PATH
  fi

  $LHEHEPMC_BIN "$LHE_FILE" $NEVENTS $JOB_ID gen_output.hepmc

else
  # Standard Whizard+Pythia8 hybrid path (SET 1-4)
  cp $MUCOLL_BENCHMARKS_PATH/generation/signal/whizard/${SAMPLE_NAME}.sin ./job.sin
  sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
  sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin
  whizard job.sin
  mv ${SAMPLE_NAME}.hepmc gen_output.hepmc
fi

T_GEN=$((SECONDS - T_START))
echo "Generation took ${T_GEN}s"

# --- 2. Simulation ---
T_START=$SECONDS
echo "Running Simulation..."
ddsim --steeringFile $MUCOLL_BENCHMARKS_PATH/simulation/steer_baseline.py \
    --numberOfEvents $NEVENTS \
    --inputFiles gen_output.hepmc \
    --outputFile sim_output.edm4hep.root
T_SIM=$((SECONDS - T_START))
echo "Simulation took ${T_SIM}s"

# --- 3. Digitization ---
T_START=$SECONDS
echo "Running Digitization..."
k4run $MUCOLL_BENCHMARKS_PATH/digitization/digi_steer.py \
    --IOSvc.Input sim_output.edm4hep.root \
    --IOSvc.Output digi_output.edm4hep.root
T_DIGI=$((SECONDS - T_START))
echo "Digitization took ${T_DIGI}s"

# --- 4. Reconstruction ---
T_START=$SECONDS
echo "Running Reconstruction..."
k4run $MUCOLL_BENCHMARKS_PATH/reconstruction/reco_steer.py \
    --IOSvc.Input digi_output.edm4hep.root \
    --IOSvc.Output reco_output.edm4hep.root
T_RECO=$((SECONDS - T_START))
echo "Reconstruction took ${T_RECO}s"

# --- Move Outputs ---
FINAL_OUT_DIR=$OUTPUT_DIR/job_${JOB_ID}_${TAG}
mkdir -p $FINAL_OUT_DIR
echo "Moving files to $FINAL_OUT_DIR"

mv gen_output.hepmc $FINAL_OUT_DIR/gen_output_${JOB_ID}.hepmc
mv sim_output.edm4hep.root $FINAL_OUT_DIR/sim_output_${JOB_ID}.edm4hep.root
mv digi_output.edm4hep.root $FINAL_OUT_DIR/digi_output_${JOB_ID}.edm4hep.root
mv reco_output.edm4hep.root $FINAL_OUT_DIR/reco_output_${JOB_ID}.edm4hep.root

# Cleanup
cd ..
rm -rf $WORKDIR
echo "Job $JOB_ID finished successfully"
echo "Timing summary: Generation=${T_GEN}s, Simulation=${T_SIM}s, Digitization=${T_DIGI}s, Reconstruction=${T_RECO}s, Total=${SECONDS}s"

#!/bin/bash
set -e

# Usage:
#   run_chain_vbfW.sh <JOB_ID> <NEVENTS> <OUTPUT_DIR> <MUCOLL_BENCHMARKS_PATH> <SET> [GRIDPACK_DIR]
#
# SET selects the steering variant:
#   1 -> mumu_vbfW_10TeV.sin              (stable W, Pythia8 default decays)
#   2 -> mumu_vbfW_qq_10TeV.sin           (Whizard decays W -> hadrons)
#   3 -> mumu_vbfW_hybrid_10TeV.sin       (stable W in Whizard, Pythia8 forces W -> hadrons)
#   4 -> mumu_vbfWqq_inclusive_10TeV.sin  (2->4 inclusive ME, no W resonance)

JOB_ID=$1
NEVENTS=$2
OUTPUT_DIR=$3
MUCOLL_BENCHMARKS_PATH=$4
SET=${5:-3}
GRIDPACK_DIR=${6:-""}

case "$SET" in
  1) SIN=mumu_vbfW_10TeV.sin;             SAMPLE=mumu_vbfW_10TeV;             TAG=set1 ;;
  2) SIN=mumu_vbfW_qq_10TeV.sin;          SAMPLE=mumu_vbfW_qq_10TeV;          TAG=set2 ;;
  3) SIN=mumu_vbfW_hybrid_10TeV.sin;      SAMPLE=mumu_vbfW_hybrid_10TeV;      TAG=set3 ;;
  4) SIN=mumu_vbfWqq_inclusive_10TeV.sin; SAMPLE=mumu_vbfWqq_inclusive_10TeV; TAG=inclusive ;;
  *) echo "Unknown SET=$SET (use 1, 2, 3, or 4)"; exit 1 ;;
esac

echo "Starting job $JOB_ID with $NEVENTS events (vbfW, SET=$SET -> $SIN)"
echo "Output directory: $OUTPUT_DIR"
echo "Benchmarks path: $MUCOLL_BENCHMARKS_PATH"
if [ -n "$GRIDPACK_DIR" ]; then
    echo "Using Whizard gridpack from: $GRIDPACK_DIR"
else
    echo "No gridpack provided: running full phase-space integration"
fi

source /opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/mucoll-stack-2026-01-29-gox6efzvyhus5szcxoq3wscjpt5uxvl7/setup.sh

source $MUCOLL_BENCHMARKS_PATH/k4MuCPlayground/setup_digireco.sh $MUCOLL_BENCHMARKS_PATH MAIA_v0

WORKDIR=/tmp/mucoll_job_${JOB_ID}_${RANDOM}
mkdir -p $WORKDIR
cd $WORKDIR
echo "Working in $WORKDIR"

export LD_LIBRARY_PATH=/opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/whizard-3.1.5-2wpmahrsf5vaircj7tmf5hdo5fwz2hhw/lib:$LD_LIBRARY_PATH

cp -r $MUCOLL_BENCHMARKS_PATH/reconstruction/PandoraSettings/ ./

# --- 1. Generation (Whizard) ---
echo "Running Generation..."
cp $MUCOLL_BENCHMARKS_PATH/generation/signal/whizard/$SIN ./job.sin
sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin

if [ -n "$GRIDPACK_DIR" ]; then
    mkdir -p ./grids
    cp "$GRIDPACK_DIR"/* ./grids/
    sed -i "/^integrate (vbfw)/i ?rebuild_grids = false\n\$integrate_workspace = \"grids\"" job.sin
fi

whizard job.sin

mv ${SAMPLE}.hepmc gen_output.hepmc

# --- 2. Simulation ---
echo "Running Simulation..."
ddsim --steeringFile $MUCOLL_BENCHMARKS_PATH/simulation/steer_baseline.py \
    --numberOfEvents $NEVENTS \
    --inputFiles gen_output.hepmc \
    --outputFile sim_output.edm4hep.root

# --- 3. Digitization ---
echo "Running Digitization..."
k4run $MUCOLL_BENCHMARKS_PATH/digitization/digi_steer.py \
    --IOSvc.Input sim_output.edm4hep.root \
    --IOSvc.Output digi_output.edm4hep.root

# --- 4. Reconstruction ---
echo "Running Reconstruction..."
k4run $MUCOLL_BENCHMARKS_PATH/reconstruction/reco_steer.py \
    --IOSvc.Input digi_output.edm4hep.root \
    --IOSvc.Output reco_output.edm4hep.root

FINAL_OUT_DIR=$OUTPUT_DIR/job_${JOB_ID}_vbfW_${TAG}
mkdir -p $FINAL_OUT_DIR
echo "Moving files to $FINAL_OUT_DIR"
ls -lh

mv gen_output.hepmc $FINAL_OUT_DIR/gen_output_${JOB_ID}.hepmc
mv sim_output.edm4hep.root $FINAL_OUT_DIR/sim_output_${JOB_ID}.edm4hep.root
mv digi_output.edm4hep.root $FINAL_OUT_DIR/digi_output_${JOB_ID}.edm4hep.root
mv reco_output.edm4hep.root $FINAL_OUT_DIR/reco_output_${JOB_ID}.edm4hep.root

ls -lh $FINAL_OUT_DIR

cd ..
rm -rf $WORKDIR
echo "Job $JOB_ID finished successfully"

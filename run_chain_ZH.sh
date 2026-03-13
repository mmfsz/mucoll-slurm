#!/bin/bash
set -e

# Arguments
JOB_ID=$1
NEVENTS=$2
OUTPUT_DIR=$3
MUCOLL_BENCHMARKS_PATH=$4

echo "Starting job $JOB_ID with $NEVENTS events"
echo "Output directory: $OUTPUT_DIR"
echo "Benchmarks path: $MUCOLL_BENCHMARKS_PATH"

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

# --- 1. Generation (Whizard) ---
T_START=$SECONDS
echo "Running Generation..."
SAMPLE_NAME="mumu_ZHbbbb_10TeV"

# Copy the steering file and update the number of events
cp $MUCOLL_BENCHMARKS_PATH/generation/signal/whizard/${SAMPLE_NAME}.sin ./job.sin

# Update seed and n_events
sed -i "s/seed = .*/seed = $((1234 + JOB_ID))/" job.sin
sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin

whizard job.sin

mv ${SAMPLE_NAME}.hepmc gen_output.hepmc
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
FINAL_OUT_DIR=$OUTPUT_DIR/job_${JOB_ID}_ZH
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

#!/bin/bash
set -e

# Generation-only chain: runs Whizard on a given .sin file and copies the
# resulting .hepmc to OUTPUT_DIR. Intended for HepMC validation / ancestry
# inspection, bypassing ddsim and k4run.
#
# Usage:
#   run_whizard_only.sh <JOB_ID> <NEVENTS> <OUTPUT_DIR> <MUCOLL_BENCHMARKS_PATH> <SIN_NAME> <SAMPLE_NAME> [GRIDPACK_DIR] [INTEGRATE_PROC]
#
#   SIN_NAME       e.g. mumu_vbfH_hybrid_10TeV.sin
#   SAMPLE_NAME    whatever Whizard writes: e.g. mumu_vbfH_hybrid_10TeV
#   INTEGRATE_PROC (optional) process label in the `integrate (...)` call used
#                  for the gridpack sed edit. Default: vbfh

JOB_ID=$1
NEVENTS=$2
OUTPUT_DIR=$3
MUCOLL_BENCHMARKS_PATH=$4
SIN_NAME=$5
SAMPLE_NAME=$6
GRIDPACK_DIR=${7:-""}
INTEGRATE_PROC=${8:-"vbfh"}

echo "Whizard-only test: JOB_ID=$JOB_ID NEVENTS=$NEVENTS SIN=$SIN_NAME"

source /opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/mucoll-stack-2026-01-29-gox6efzvyhus5szcxoq3wscjpt5uxvl7/setup.sh

WORKDIR=/tmp/mucoll_wztest_${JOB_ID}_${RANDOM}
mkdir -p $WORKDIR
cd $WORKDIR
echo "Working in $WORKDIR"

export LD_LIBRARY_PATH=/opt/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_placeholder__/linux-x86_64/whizard-3.1.5-2wpmahrsf5vaircj7tmf5hdo5fwz2hhw/lib:$LD_LIBRARY_PATH

cp $MUCOLL_BENCHMARKS_PATH/generation/signal/whizard/$SIN_NAME ./job.sin
sed -i "s/seed *=.*/seed = $((1234 + JOB_ID))/" job.sin
sed -i "s/n_events = .*/n_events = $NEVENTS/" job.sin

if [ -n "$GRIDPACK_DIR" ]; then
    mkdir -p ./grids
    cp "$GRIDPACK_DIR"/* ./grids/
    sed -i "/^integrate ($INTEGRATE_PROC)/i ?rebuild_grids = false\n\$integrate_workspace = \"grids\"" job.sin
fi

whizard job.sin

FINAL_OUT_DIR=$OUTPUT_DIR/wztest_${JOB_ID}
mkdir -p $FINAL_OUT_DIR
cp ${SAMPLE_NAME}.hepmc $FINAL_OUT_DIR/gen_output_${JOB_ID}.hepmc
cp job.sin $FINAL_OUT_DIR/
# Preserve Whizard's own log file for diagnostic inspection
[ -f whizard.log ] && cp whizard.log $FINAL_OUT_DIR/whizard_${JOB_ID}.log
ls -lh $FINAL_OUT_DIR

cd ..
rm -rf $WORKDIR
echo "Whizard-only job $JOB_ID finished"

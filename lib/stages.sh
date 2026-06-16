#!/bin/bash
# lib/stages.sh — shared pipeline stages, identical across every sample.
# Source this (do not exec). Operates in the current working dir ($WORKDIR).

# setup_workdir <job_id> : create + cd into a unique per-job node-local scratch dir
# (exports WORKDIR). Each job stages ~9 GB (gen+sim+digi+reco); prefer HPG's per-job
# scratch /scratch/local/$SLURM_JOB_ID (large, isolated, auto-cleaned) over the shared
# /tmp, whose cross-job exhaustion corrupted SIM ROOT output ("basket's WriteBuffer
# failed" / missing podio_metadata). Falls back to /tmp off-cluster.
setup_workdir() {
    local base=/tmp
    if   [ -n "${SLURM_TMPDIR:-}" ] && [ -d "$SLURM_TMPDIR" ]; then base="$SLURM_TMPDIR"
    elif [ -n "${SLURM_JOB_ID:-}" ] && [ -d "/scratch/local/$SLURM_JOB_ID" ]; then base="/scratch/local/$SLURM_JOB_ID"
    fi
    WORKDIR="$base/mucoll_job_${1}_${RANDOM}"
    mkdir -p "$WORKDIR"
    cd "$WORKDIR"
    echo "Working in $WORKDIR"
}

# apply_gridpack : if GRIDPACK_DIR is set, stage pre-computed VAMP grids and
# point job.sin at them. The $integrate_workspace directive is global in Whizard,
# so inserting it before the FIRST integrate() covers single- and multi-integrate
# cards alike (no need to know the process name).
apply_gridpack() {
    [ -n "$GRIDPACK_DIR" ] || return 0
    mkdir -p ./grids
    cp "$GRIDPACK_DIR"/*.vg ./grids/ 2>/dev/null || true
    awk '!d && /^integrate *\(/ {print "?rebuild_grids = false"; \
         print "$integrate_workspace = \"grids\""; d=1} {print}' \
        job.sin > job.sin.tmp && mv job.sin.tmp job.sin
    echo "Gridpack staged from $GRIDPACK_DIR"
}

# stage_sim_digi_reco <benchmarks> <nevents> <gen_glob>
stage_sim_digi_reco() {
    local BENCH=$1 NEVENTS=$2 GENGLOB=$3 t
    t=$SECONDS; echo "--- Simulation ---"
    ddsim --steeringFile "$BENCH/simulation/steer_baseline.py" \
        --numberOfEvents "$NEVENTS" \
        --inputFiles $GENGLOB \
        --outputFile sim_output.edm4hep.root
    echo "Simulation took $((SECONDS - t))s"

    t=$SECONDS; echo "--- Digitization ---"
    k4run "$BENCH/digitization/digi_steer.py" \
        --IOSvc.Input sim_output.edm4hep.root \
        --IOSvc.Output digi_output.edm4hep.root
    echo "Digitization took $((SECONDS - t))s"

    t=$SECONDS; echo "--- Reconstruction ---"
    k4run "$BENCH/reconstruction/reco_steer.py" \
        --IOSvc.Input digi_output.edm4hep.root \
        --IOSvc.Output reco_output.edm4hep.root
    echo "Reconstruction took $((SECONDS - t))s"
}

# move_outputs <output_dir> <job_id> <tag> <gen_ext>
# Layout: <output_dir>/<tag>/job_<id>/{gen,sim,digi,reco}_output_<id>.*
move_outputs() {
    local OUT=$1 JOB=$2 TAG=$3 EXT=$4
    local dst="$OUT/$TAG/job_$JOB"
    mkdir -p "$dst"
    mv gen_output.$EXT          "$dst/gen_output_${JOB}.$EXT"
    mv sim_output.edm4hep.root  "$dst/sim_output_${JOB}.edm4hep.root"
    mv digi_output.edm4hep.root "$dst/digi_output_${JOB}.edm4hep.root"
    mv reco_output.edm4hep.root "$dst/reco_output_${JOB}.edm4hep.root"
    echo "Outputs -> $dst"
}

cleanup_workdir() { cd /; rm -rf "$WORKDIR"; }

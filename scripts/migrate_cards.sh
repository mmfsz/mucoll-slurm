#!/bin/bash
# migrate_cards.sh — one-time card harmonization (provenance / documentation).
#
# Builds the new git-tracked card tree from the legacy cards and archives the
# originals. Content is copied VERBATIM — only filenames change to the
# harmonized convention. Re-runnable: rebuilds cards/ from sources each time.
#
# Naming convention
#   Resonant (a real boson is in the ME and gets decayed):
#       mumu_<PROCESS>_<FINALSTATE>_[<REGION>_]<DECAYER>_<ENERGY>.sin
#       DECAYER = whizard | pythia | pythiaNoCR | pythiaSKI | lhe
#   Inclusive (no resonance in the ME; named by literal final state):
#       mumu_<FINALSTATE>[_<REGION>]_<ENERGY>.sin
#   REGION encodes the defining kinematic selection:
#       pt500            boson Pt > 500 GeV (boosted single-boson VBF)
#       <V>mass_pt250    qq/bb in the V mass window + jet Pt > 250 GeV
#
set -e

SLURM_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MUONCOLLIDER_DIR="$(dirname "$SLURM_DIR")"
BENCH="$MUONCOLLIDER_DIR/mucoll-benchmarks/generation/signal/whizard"

PROD="$SLURM_DIR/cards/production"
GRID="$SLURM_DIR/cards/gridpack"
ARCH="$SLURM_DIR/archive/cards"
REPO_WIZ="$ARCH/whizard_repo"   # this repo's legacy whizard/ cards (archived here)

mkdir -p "$PROD" "$GRID" "$ARCH/benchmarks" "$REPO_WIZ"

# One-time archive of legacy cards (idempotent).
cp -n "$BENCH"/*.sin "$ARCH/benchmarks/" 2>/dev/null || true
if [ -d "$SLURM_DIR/whizard" ]; then
  mv "$SLURM_DIR/whizard"/*.sin "$REPO_WIZ/" 2>/dev/null || true
  rmdir "$SLURM_DIR/whizard" 2>/dev/null || true
fi

# Clean rebuild of the card tree.
rm -f "$PROD"/*.sin "$GRID"/*.sin

cp_card() {
  if [ ! -f "$1" ]; then echo "MISSING SOURCE: $1" >&2; return 1; fi
  cp "$1" "$2"
  echo "  $(basename "$1")  ->  $(basename "$2")"
}

echo "== Resonant production cards =="
# ZH (s-channel; no pT/mass cut -> no region token)
cp_card "$BENCH/mumu_ZHbbbb_10TeV.sin"             "$PROD/mumu_ZH_bbbb_whizard_10TeV.sin"
cp_card "$BENCH/mumu_ZHbbbb_hybrid_10TeV.sin"      "$PROD/mumu_ZH_bbbb_pythia_10TeV.sin"
cp_card "$BENCH/mumu_ZHbbbb_hybrid_noCR_10TeV.sin" "$PROD/mumu_ZH_bbbb_pythiaNoCR_10TeV.sin"
cp_card "$BENCH/mumu_ZHbbbb_hybrid_skI_10TeV.sin"  "$PROD/mumu_ZH_bbbb_pythiaSKI_10TeV.sin"
cp_card "$BENCH/mumu_ZHbbbb_lhe_10TeV.sin"         "$PROD/mumu_ZH_bbbb_lhe_10TeV.sin"
# VBF single-boson (boosted: Pt(boson) > 500 -> region pt500)
cp_card "$BENCH/mumu_vbfH_10TeV.sin"               "$PROD/mumu_vbfH_incl_pt500_pythia_10TeV.sin"
cp_card "$BENCH/mumu_vbfH_bb_10TeV.sin"            "$PROD/mumu_vbfH_bb_pt500_whizard_10TeV.sin"
cp_card "$BENCH/mumu_vbfH_hybrid_10TeV.sin"        "$PROD/mumu_vbfH_bb_pt500_pythia_10TeV.sin"
cp_card "$BENCH/mumu_vbfZ_10TeV.sin"               "$PROD/mumu_vbfZ_incl_pt500_pythia_10TeV.sin"
cp_card "$BENCH/mumu_vbfZ_qq_10TeV.sin"            "$PROD/mumu_vbfZ_qq_pt500_whizard_10TeV.sin"
cp_card "$BENCH/mumu_vbfZ_hybrid_10TeV.sin"        "$PROD/mumu_vbfZ_qq_pt500_pythia_10TeV.sin"
cp_card "$BENCH/mumu_vbfW_10TeV.sin"               "$PROD/mumu_vbfW_incl_pt500_pythia_10TeV.sin"
cp_card "$BENCH/mumu_vbfW_qq_10TeV.sin"            "$PROD/mumu_vbfW_qq_pt500_whizard_10TeV.sin"
cp_card "$BENCH/mumu_vbfW_hybrid_10TeV.sin"        "$PROD/mumu_vbfW_qq_pt500_pythia_10TeV.sin"
# WW (s-channel; eta cut only -> no region token)
cp_card "$BENCH/mumu_WWqqqq_10TeV.sin"             "$PROD/mumu_WW_qqqq_whizardNoCR_10TeV.sin"

echo "== Inclusive production cards (no resonance; final-state named) =="
cp_card "$BENCH/mumu_ZHbbbb_inclusive_10TeV.sin"   "$PROD/mumu_bbbb_10TeV.sin"                 # no cuts
cp_card "$BENCH/mumu_vbfHbb_inclusive_10TeV.sin"   "$PROD/mumu_nunubb_Hmass_pt250_10TeV.sin"
cp_card "$BENCH/mumu_vbfZqq_inclusive_10TeV.sin"   "$PROD/mumu_nunuqq_Zmass_pt250_10TeV.sin"
cp_card "$BENCH/mumu_vbfWqq_inclusive_10TeV.sin"   "$PROD/mumu_lnuqq_Wmass_pt250_10TeV.sin"
cp_card "$REPO_WIZ/mumu_WWZ_hadrons_10TeV.sin"     "$PROD/mumu_nunuqq_10TeV.sin"               # broad
cp_card "$REPO_WIZ/mumu_ZZZ_hadrons_10TeV.sin"     "$PROD/mumu_mumuqq_10TeV.sin"               # broad

echo "== Gridpack-integration cards (stem matches the production family it serves) =="
# Resonant VBF gridpack serves all decayer/final-state variants of its process.
cp_card "$REPO_WIZ/mumu_vbfH_10TeV_gridpack.sin"            "$GRID/mumu_vbfH_pt500_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_vbfZ_10TeV_gridpack.sin"            "$GRID/mumu_vbfZ_pt500_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_vbfW_10TeV_gridpack.sin"            "$GRID/mumu_vbfW_pt500_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_vbfHbb_inclusive_10TeV_gridpack.sin" "$GRID/mumu_nunubb_Hmass_pt250_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_vbfZqq_inclusive_10TeV_gridpack.sin" "$GRID/mumu_nunuqq_Zmass_pt250_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_vbfWqq_inclusive_10TeV_gridpack.sin" "$GRID/mumu_lnuqq_Wmass_pt250_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_ZHbbbb_inclusive_10TeV_gridpack.sin" "$GRID/mumu_bbbb_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_WWZ_hadrons_10TeV_gridpack.sin"      "$GRID/mumu_nunuqq_10TeV.gridpack.sin"
cp_card "$REPO_WIZ/mumu_ZZZ_hadrons_10TeV_gridpack.sin"      "$GRID/mumu_mumuqq_10TeV.gridpack.sin"

echo "Done. production=$(ls "$PROD" | wc -l) gridpack=$(ls "$GRID" | wc -l)"

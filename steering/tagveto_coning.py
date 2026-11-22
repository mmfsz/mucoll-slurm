"""Calorimeter truth-coning without the hard-process tags (VBF tag neutrinos and muons).

MAIAConfig's --doCaloConing cones the calorimeter hits around every stable generator
particle. This module swaps in cones around the output of k4ext's HardProcessTagVeto
(stable particles minus the muons/neutrinos produced at the hard vertex, and their
generator-level descendants), by wrapping CaloDigi.calo_coning.calo_coner_cfgs before the
MAIAConfig steering builds its algorithm list. MAIAConfig itself is not modified.

Used through digi_steer_tagveto.py / digi_reco_steer_tagveto.py, which take exactly the
MAIAConfig steering arguments (pass --doCaloConing as usual). Needs k4ext/env.sh sourced.
"""
import os
import runpy
import sys

CONFIG_DIR = os.path.join(os.environ["MUCOLL_CONFIG"], os.environ["MUCOLL_CONFIG_NAME"])
SEEDS = "ConeSeedMCParticles"

sys.path.insert(0, CONFIG_DIR)
import CaloDigi.calo_coning as _calo_coning  # noqa: E402  (needs CONFIG_DIR on sys.path)

_maia_coner_cfgs = _calo_coning.calo_coner_cfgs


def calo_coner_cfgs(args):
    from Configurables import HardProcessTagVeto
    veto = HardProcessTagVeto("ConeSeedTagVeto", InputMCParticles=["MCParticles"], OutputMCParticles=[SEEDS])
    coners = _maia_coner_cfgs(args)
    for coner in coners:
        coner.MCParticleCollectionName = SEEDS
    return [veto] + coners


# digiAlgList imports calo_coner_cfgs from this module inside makeDigiAlgList, so the
# wrapper is picked up there.
_calo_coning.calo_coner_cfgs = calo_coner_cfgs


def run(steering):
    """Execute a MAIAConfig steering file (digi_steer.py, digi_reco_steer.py) as k4run would."""
    runpy.run_path(os.path.join(CONFIG_DIR, steering), run_name="__main__")

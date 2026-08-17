# Muon Collider Simulation Framework (mucoll-slurm)

## Overview

Slurm batch framework for running the full muon collider simulation chain on **HiPerGator (HPG)**. Runs inside an Apptainer container (`mucoll-sim.sif`) with a Spack-managed software stack.

**Repo**: `git@github.com:leblanc-lab/mucoll-slurm.git`

## Architecture (manifest-driven, 2026-06)

The per-sample chain scripts were collapsed into **one dispatcher + a manifest + a
shared library**. Adding a sample = adding one row to `samples.conf` (+ a card), not
writing a new script. The only thing that varies per sample is the GEN stage; SIM/DIGI/RECO
and all bookkeeping are shared.

```
muoncollider/                         # Parent dir (MUONCOLLIDER_DIR)
├── mucoll-slurm/                     # This repo (SLURM_DIR)
│   ├── mucoll-sim.sif                # Apptainer container (~8.9 GB)
│   ├── run_chain.sh                  # ★ single dispatcher: <SAMPLE_KEY> <JOB_ID> <N> <OUT> <BENCH> [extra]
│   ├── samples.conf                  # ★ sample manifest (key | gen_type | card | gridpack)
│   ├── submit.py                     # ★ unified SLURM submitter (reads samples.conf)
│   ├── make_gridpack.py              # VAMP grid pre-computation (uses cards/gridpack/)
│   ├── lib/
│   │   ├── env.sh                    # ONE place for spack + Whizard lib paths (+ HepMC3 helper)
│   │   └── stages.sh                 # shared workdir / gridpack / SIM·DIGI·RECO / output funcs
│   ├── gen/                          # generator plugins (each defines generate())
│   │   ├── whizard.sh   whizard_lhe.sh   pgun.sh   pythia.sh
│   ├── cards/
│   │   ├── production/               # ★ git-tracked production .sin (we OWN these)
│   │   ├── gridpack/                 # integration-only *.gridpack.sin
│   │   └── README.md                 # naming convention + full cut table
│   ├── pythia/                       # MuMuToZH, LheToHepMC (+ .cc, Makefile, build.sh)
│   ├── scripts/
│   │   ├── setup.sh                  # spack env (sourced by lib/env.sh + interactive)
│   │   ├── migrate_cards.sh          # one-time card harmonization (provenance/doc)
│   │   ├── install_hpg.sh interact_hpg.sh shell_hpg.sh
│   ├── archive/cards/                # frozen legacy cards (benchmarks/ + whizard_repo/)
│   └── (legacy: run_chain_*.sh, chains/, submit_jobs.py, submit_scan.py, submit_*.py,
│         watchdog_vbf*) — superseded by the above; kept until parity is confirmed
├── mucoll-benchmarks/                # External (samf25, branch k4MuC). We do NOT own it.
│   ├── generation/                   # pgun generator (+ legacy .sin, which we no longer read for owned cards)
│   ├── simulation/                   # DDSim steering (steer_baseline.py)
│   ├── digitization/                 # k4run digi_steer.py
│   ├── reconstruction/               # k4run reco_steer.py + PandoraSettings/
│   └── k4MuCPlayground/setup_digireco.sh
└── output/
    ├── batch/<SAMPLE_KEY>/job_<ID>/  # job outputs, grouped by sample
    └── gridpacks/<gridpack>/         # pre-computed VAMP grids (.vg); dir = gridpack-card stem
```

## Simulation Pipeline (4 stages)

Every job runs **GEN → SIM → DIGI → RECO** (via `run_chain.sh`):

1. **GEN** — `gen/<gen_type>.sh::generate()`. `whizard` (card → HepMC), `whizard_lhe`
   (card → LHE → `pythia/LheToHepMC` → HepMC), `pgun` (→ `.edm4hep.root`),
   `pythia` (`pythia/MuMuToZH` → HepMC).
2. **SIM** — `ddsim` (Geant4), geometry **MAIA_v0**.
3. **DIGI** — `k4run digi_steer.py`.
4. **RECO** — `k4run reco_steer.py` (Pandora).

SIM/DIGI/RECO come from `mucoll-benchmarks` and are invoked by `lib/stages.sh`
(identical for every sample). Outputs land in
`output/batch/<SAMPLE_KEY>/job_<ID>/{gen,sim,digi,reco}_output_<ID>.*`.

## The manifest (`samples.conf`)

Whitespace-delimited, `#` comments. Columns:

| col | meaning |
|-----|---------|
| `key` | unique sample id — also the output sub-dir and the `submit.py --samples` selector |
| `gen_type` | `whizard` \| `whizard_lhe` \| `pgun` \| `pythia` |
| `card` | filename in `cards/production/` (then benchmarks); `-` if none |
| `gridpack` | grid dir under `output/gridpacks/` (used only if it has `.vg`); `-` if none |

One gridpack serves all decayer variants of a process (shared ME). `run_chain.sh`
auto-inserts the gridpack workspace before the **first** `integrate()` (global setting,
so it covers multi-`integrate` cards) — no per-card process name needed.

## Cards — we own them

Production `.sin` cards live in **`cards/production/`** (git-tracked) and are the source
of truth; `run_chain.sh` resolves there first, then falls back to benchmarks. See
`cards/README.md` for the naming convention and the full kinematic-cut table. In short:

- Resonant: `mumu_<PROCESS>_<FINALSTATE>_[<REGION>_]<DECAYER>_<ENERGY>.sin`
- Inclusive (no resonance): `mumu_<FINALSTATE>[_<REGION>]_<ENERGY>.sin`
- DECAYER ∈ {`whizard`, `pythia`, `pythiaNoCR`, `pythiaSKI`, `lhe`}; REGION encodes the
  defining cut (`pt500` boosted single-boson; `Vmass`+`pt250` windowed inclusive).

## Submission (`submit.py`)

```bash
python submit.py --list                                   # show samples
python submit.py -s ZH_bbbb_pythia -n 50 -e 10            # 50 jobs x 10 events
python submit.py -s vbfZ_qq_pt500_pythia vbfZ_qq_pt500_whizard -n 500 -e 10 --qos avery-b
python submit.py -s pgun -n 5 -e 1000 --pgun 11 100 10 170
python submit.py -s nunuqq_Zmass_pt250 -n 10 -e 10 --dry-run
```

Validates the selection + card existence (pre-flight) before submitting. SLURM defaults:
`--time 10:00:00 --mem 16G --cpus 4 --qos avery-b` (override with `--time/--mem/--cpus/--qos`;
`avery-b` is the burst queue — keeps long CPU jobs off the shared `avery` qos that GPU jobs
draw CPUs from). Use `submit.py --indices N N …` to (re)submit specific job indices. Always
passes `--cleanenv`. Replaces the old `submit_jobs.py`, `submit_scan.py` (pgun),
`submit_vbf_inclusive_10k.py`, `submit_ZH_lhe_test.py`, `submit_ZH_CR_tests.py`.

`make_gridpack.py <PROCESS...>` pre-computes VAMP grids (24h, 32 CPU) into
`output/gridpacks/<gridpack>/`, using `cards/gridpack/` and `lib/env.sh`.

## HPG Workflow

```bash
source scripts/interact_hpg.sh      # compute node
./scripts/install_hpg.sh            # pull .sif + clone benchmarks (one-time)

# Build pythia binaries (one-time; rebuild only if .sif changes)
source scripts/shell_hpg.sh
source scripts/setup.sh
bash pythia/build.sh
exit

# Batch submission (login node, outside container)
python submit.py -s <KEY> -n <N> -e <NEV>
squeue -u $USER
```

## Key Conventions

- Paths derive from script location (`SLURM_DIR`, `MUONCOLLIDER_DIR`); no hardcoding.
- spack + Whizard paths live **only** in `scripts/setup.sh` + `lib/env.sh` — update there
  on an image bump (previously copy-pasted into ~9 scripts).
- Container image: `ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main`
- Spack stack: `mucoll-stack-2026-01-29`; Whizard 3.1.5; geometry MAIA_v0.
- Benchmarks branch: `k4MuC` from `samf25/mucoll-benchmarks`.
- Job scratch: `lib/stages.sh::setup_workdir` stages each job (~9 GB gen+sim+digi+reco) in
  per-job node scratch `/scratch/local/$SLURM_JOB_ID` (large, isolated, auto-cleaned),
  falling back to `/tmp` if unavailable. `submit.py` re-injects `SLURM_JOB_ID` via
  `apptainer --env` (since `--cleanenv` strips it). This avoids `/blue` I/O contention AND
  the shared-`/tmp` ENOSPC that was corrupting SIM ROOT output (`basket's WriteBuffer
  failed` / missing `podio_metadata`).

### Seed convention (the seed bug — KEEP FIXED)
Cards use `seed  = 1234`. The gen plugins use `sed "s/seed *=.*/seed = $((1234 + JOB_ID))/"`
(the `*` matters). The old one-space regex silently failed → every job ran seed 1234 →
identical events. Always confirm distinct HepMC across jobs before trusting a production.

### Cut convention (the quoted-particle bug — KEEP FIXED)
In a Whizard `cuts =` expression, **never quote particle names in a subevent**:
`all Pt > 500 GeV ["W+", "W-"]` resolves to an **empty set**, so `all <cond> [∅]` is
vacuously true and the cut **silently never fires** (quoted names work in `process`
lines but NOT in cuts). Built-in names (`[Z]`, `[H]`) and aliases (`[lTag]`) are fine;
for particles whose name can't be written unquoted (`W+`/`W-` — the `+`/`-` are
operators), define an alias: `alias Wpm = "W+":"W-"` then `[Wpm]`. The vbfW cards shipped
with `["W+","W-"]` → the pt>500 / |η|<2.3 cut was void → W produced at pT~50 not >500,
and the gridpack integrated at 30817 fb instead of ~527 fb (fixed 2026-06-17, commit
`cb3724f`). **Always sanity-check a new card's integrated σ and the cut variable's
distribution before trusting a production** — a cut that doesn't bite shows up as a σ
orders of magnitude too large.

## Active study & graduation rule

The current investigation — *the correct way to generate hadronic boson decays* — lives
in `studies/generators_validation_conejets/` (`PLAN.md`, `RESULTS.md`, `README.md`).

**Generation method verdicts** (graduate in from the study once definitive — one line +
link to the `RESULTS.md` section that proves it):

_empty — pending the from-scratch reruns._

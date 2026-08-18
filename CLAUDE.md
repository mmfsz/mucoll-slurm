# Muon Collider Simulation Framework (mucoll-slurm)

## Overview

Slurm batch framework for running the full muon collider simulation chain on **HiPerGator (HPG)**. Runs inside an Apptainer container with a Spack-managed software stack — by default the MAIA **v3.1** image unpacked on CVMFS, so there is no `.sif` to pull or keep in sync.

**Repo**: `git@github.com:leblanc-lab/mucoll-slurm.git`

## Architecture (manifest-driven, 2026-06)

The per-sample chain scripts were collapsed into **one dispatcher + a manifest + a
shared library**. Adding a sample = adding one row to `samples.conf` (+ a card), not
writing a new script. The only thing that varies per sample is the GEN stage; SIM/DIGI/RECO
and all bookkeeping are shared.

```
muoncollider/                         # Parent dir (MUONCOLLIDER_DIR)
├── mucoll-slurm/                     # This repo (SLURM_DIR)
│   ├── run_chain.sh                  # ★ single dispatcher: <SAMPLE_KEY> <JOB_ID> <N> <OUT> <BENCH> [extra]
│   ├── samples.conf                  # ★ sample manifest (key | gen_type | card | gridpack)
│   ├── submit.py                     # ★ unified SLURM submitter (reads samples.conf)
│   ├── make_gridpack.py              # VAMP grid pre-computation (uses cards/gridpack/)
│   ├── mucoll_paths.py               # image + benchmarks resolution for the Python submitters
│   ├── lib/
│   │   ├── image.sh                  # ★ ONE place naming the container image (MUCOLL_IMAGE)
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
├── mucoll-benchmarks-v3.1/           # External (MuonColliderSoft, v3.1). We do NOT own it.
│   ├── generation/                   # pgun generator (+ legacy .sin, which we no longer read for owned cards)
│   ├── simulation/                   # DDSim steering (steer_baseline.py)
│   ├── setup_config.sh               # ★ sets MUCOLL_GEO / MUCOLL_CONFIG for a geometry
│   └── configs/<GEO>Config/          # ★ submodules: digi_steer.py, reco_steer.py, PandoraSettings/
├── mucoll-benchmarks/                # pre-v3.1 checkout (samf25 k4MuC) — kept for `main`, unused here
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
3. **DIGI** — `k4run $MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/digi_steer.py`.
4. **RECO** — `k4run $MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/reco_steer.py` (Pandora).

SIM comes from `mucoll-benchmarks-v3.1/simulation/`; DIGI/RECO steering comes from that
geometry's config package (v3.1 — see the migration note below). Both are invoked by
`lib/stages.sh`, identical for every sample. Outputs land in
`<base>/samples/<SAMPLE_KEY>/job_<ID>/{gen,sim,digi,reco}_output_<ID>.*`, where `<base>`
is `/cmsuf/data/store/user/<you>/mucoll` (see Key Conventions).

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
./scripts/install_hpg.sh            # check image + clone v3.1 benchmarks (one-time)

# Build pythia binaries (REQUIRED after every image bump — see Key Conventions)
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
- spack + Whizard paths live **only** in `scripts/setup.sh` + `lib/env.sh`, and both now
  *discover* their targets rather than hardcode a spack hash — an image bump needs no edit.
- Container image: named **only** in `lib/image.sh`, default
  `/cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1-amd64`.
  Override with `MUCOLL_IMAGE=/path/to/mucoll-sim.sif` — no code edit needed.
- Spack stack: loaded via the image's own `/opt/setup_mucoll.sh`, so it follows the image
  automatically (v3.1 = `mucoll-stack-2026-08-13`). Whizard 3.1.5; geometry MAIA_v0.
- Benchmarks: `MuonColliderSoft/mucoll-benchmarks`, cloned **with submodules** to
  `mucoll-benchmarks-v3.1/`. Override with `MUCOLL_BENCHMARKS`.
- **DIGI/RECO need `-n $NEVENTS`** (v3.1). The config package's
  `Common/steering.py` declares `build_application(..., evt_max=10)` and neither
  `digi_steer.py` nor `reco_steer.py` passes it, so without `-n` every job digitises and
  reconstructs only the **first 10 events** of however many it simulated — at full SIM cost,
  silently. The pre-v3.1 benchmarks set `EvtMax = -1`, so this is new, and a 1-event pgun
  test cannot reveal it. `lib/stages.sh` passes `-n` to both. Symptom if it regresses: RECO
  gets *faster* and its output smaller when the physics got heavier. Repair without redoing
  SIM: `scripts/redo_digireco.sh <job_dir> <nevents>`.
- Output location: resolved **only** in `mucoll_paths.py` (`output_base` / `samples_base` /
  `gridpack_base`), defaulting to `/cmsuf/data/store/user/<you>/mucoll/{samples,gridpacks}`.
  `/blue` was nearly full (avery: ~105 T of 119 T) and one 4-sample full-chain production is
  ~1.3 T, so productions live on `/cmsuf` (Lustre, hundreds of TB free). Override with
  `MUCOLL_OUTPUT` (root) or `MUCOLL_GRIDPACKS` (grids only); `submit.py` passes the resolved
  `GRIDPACK_BASE` into the container, so the shell side never duplicates the logic. The
  sample dir is `samples/` (was `batch/`) — named for what it holds, like `gridpacks/`; a
  `batch -> samples` symlink keeps older paths resolving. `gridpack_base()` only switches to
  the new root once that directory exists, so grids never silently resolve to an empty dir.
- **Rebuild `pythia/` on every image bump.** The standalone binaries (`LheToHepMC`,
  `MuMuToZH`) are linked with spack RPATHs, so a binary built against another image dies at
  GEN with `libpythia8.so: cannot open shared object file`. Everything else follows an image
  bump automatically; this does not. Run `bash pythia/build.sh` inside the new container.
- Job scratch: `lib/stages.sh::setup_workdir` stages each job (~9 GB gen+sim+digi+reco) in
  per-job node scratch `/scratch/local/$SLURM_JOB_ID`, falling back to `/tmp`. **On HPG the
  fallback is what actually runs**: the cluster provisions no per-job local scratch
  (`GresTypes = gpu` — no `scratch` GRES), so `mkdir` fails and each job logs
  `WARN: cannot create /scratch/local/...` to its `.err`. That is fine — `/tmp` on these
  nodes *is* a large node-local disk (1.7 TB `/dev/md2`, ~1 % used), which is what the
  staging wanted. It still avoids `/blue` I/O contention; the shared-`/tmp` ENOSPC that once
  corrupted SIM ROOT output (`basket's WriteBuffer failed` / missing `podio_metadata`) is not
  a risk at ~10 jobs/node. `submit.py` re-injects `SLURM_JOB_ID` via `apptainer --env` (since
  `--cleanenv` strips it).

### MAIA v3.1 migration (2026-08-17)

The chain was already Gaudi/`k4run`/EDM4hep, so the v3.1 removal of the Marlin/iLCSoft/LCIO
path changed nothing here. What did change is where the configuration lives:

- Digi/reco steering moved out of benchmarks' top-level `digitization/` and `reconstruction/`
  into a **per-geometry config package**. `lib/stages.sh` now runs
  `$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/{digi,reco}_steer.py`, which `setup_config.sh` sets —
  so switching `MUCOLL_GEOMETRY` to `MuSIC_v2`/`MuColl_v1` needs no edit.
- `k4MuCPlayground/setup_digireco.sh` is now a shim; `run_chain.sh` calls
  `setup_config.sh` directly (same two arguments).
- The `cp -r reconstruction/PandoraSettings/ ./` in `run_chain.sh` is **gone**. v3.1 hands
  Pandora an absolute settings path and rewrites the XML's internal relative references, so
  reco no longer has to run from the directory holding `PandoraSettings/`.
- The old `samf25` `k4MuC` benchmarks checkout is **not** compatible (no `setup_config.sh`,
  no `configs/`). It is left in place; v3.1 lives beside it in `mucoll-benchmarks-v3.1/`.

Validated end-to-end on 1 pgun muon event (gen→sim→digi→reco, 510 s): 80 collections out,
1 `SiTracks` / 1 `PandoraPFOs` / 1 `PandoraClusters` / 1 `JetOut`.

#### ⚠️ Samples reconstructed BEFORE this migration have no particle flow

The old `samf25` `k4MuC` checkout hands Pandora **no tracks** —
`reconstruction/reco_components/pandora.py:94-95` is `TrackCollections = [],#"SiTracks"]` and
`RelTrackCollections = []`, disabled upstream by commit `e47168a` (2025-09-16). With no track
input Pandora cannot match a track to a cluster, so **every cluster becomes one neutral PFO**:
`PandoraPFOs` is a 1:1 copy of `PandoraClusters` — same count, identical energies, PDG 22/2112
only, **not one charged PFO**. `SiTracks` is still written to the file; Pandora just never sees
it. The same steering also has `fastJet_cfg()` commented out, so there is no `JetOut`.

v3.1 fixes both — `MAIAConfig/ParticleFlow/pandora.py:101` restores `TrackCollections =
["SiTracks"]`, and `MAIAConfig/recoAlgList.py:56,58` enables `fastJet_cfg()`. That is exactly
what the validation run above confirms: it produced `SiTracks`, `PandoraPFOs`, `PandoraClusters`
**and** `JetOut`.

Practical rule: **any sample reconstructed with the old `samf25` checkout — everything under
`output/batch/` without a `_v3p1` suffix — is calorimeter-only.** Reco-level PFO studies on those samples measure calorimeter response, not
particle flow, and must be re-reconstructed under v3.1 before they mean anything else. Measured
in full (counts, energies, the residual direction-only difference) in
`studies/jets_reconstruction/RESULTS.md`.

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

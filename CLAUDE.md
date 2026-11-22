# Muon Collider Simulation Framework (mucoll-slurm)

## Overview

Slurm batch framework for running the full muon collider simulation chain on **HiPerGator (HPG)**. Runs inside an Apptainer container with a Spack-managed software stack — by default the MAIA **v3.2** image unpacked on CVMFS, so there is no `.sif` to pull or keep in sync. (Branch `v3.2_bib`; see the v3.2 migration note below. `maia-v3.1` keeps the v3.1 workflow.)

**Repo**: `git@github.com:mmfsz/mucoll-slurm.git` (`origin`) — this **`maia-v3.1`** branch
is where the v3.1 workflow lives; `leblanc-lab/mucoll-slurm` (`upstream`) has no such
branch, so do not point anyone there for these instructions. Public over HTTPS, so a
new user needs no SSH key: `git clone -b maia-v3.1 https://github.com/mmfsz/mucoll-slurm.git`

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

`make_gridpack.py <PROCESS...>` pre-computes VAMP grids (24h, 4 CPU — Whizard is single-threaded here) into
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
  `/cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.2-amd64`.
  Override with `MUCOLL_IMAGE=/path/to/mucoll-sim.sif` — no code edit needed.
- Spack stack: loaded via the image's own `/opt/setup_mucoll.sh`, so it follows the image
  automatically (v3.2 = `mucoll-stack-3.2`). Whizard 3.1.7; geometry MAIA_v0.
- Benchmarks: `MuonColliderSoft/mucoll-benchmarks`, cloned **with submodules** to
  `mucoll-benchmarks-v3.2/` at tag `v3.2` (`f1d1cdd`, MAIAConfig `8831727`). Override with
  `MUCOLL_BENCHMARKS`.
- **DIGI/RECO need `-n $NEVENTS`**. The config package's `Common/steering.py:89` declares
  `build_application(..., evt_max=10)` and neither `digi_steer.py` nor `reco_steer.py` passes
  it, so without `-n` every job digitises and reconstructs only the **first 10 events** of
  however many it simulated — at full SIM cost, silently. `k4run`'s `-n/--num-events` is the
  only override (it sets `ApplicationMgr().EvtMax` *after* the steering file executes); there
  is no steering-level argument for it, in MAIAConfig or anywhere else.
  **This is not a v3.1 regression.** Upstream `MuonColliderSoft/mucoll-benchmarks` has had
  `EvtMax = 10` at every point of its k4run history (back to `2436589`, 2025-11-20, Samuel
  Ferraro), and MAIAConfig has never shipped `-1`. Pre-v3.1 productions here escaped it only
  because the `samf25` checkout in `mucoll-benchmarks/` carries a local **uncommitted** edit
  to `EvtMax = -1` in `digitization/digi_steer.py` and `reconstruction/reco_steer.py` (mtime
  2026-03-09) — a patch the clean v3.1 checkout does not inherit. Do not cite that `-1` as
  upstream behaviour. A 1-event pgun test cannot reveal any of this. `lib/stages.sh` passes
  `-n` to both. Symptom if it regresses: RECO gets *faster* and its output smaller when the
  physics got heavier. Repair without redoing SIM: `scripts/redo_digireco.sh <job_dir> <nevents>`.
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

### MAIA v3.2 migration (2026-11-20)

The reason to move was a v3.1 bug in the BIB overlay. When background lands on an
already-hit calorimeter cell, the hit energy was not updated
([k4FWCore#443](https://github.com/key4hep/k4FWCore/issues/443)). The fix is
EDM4hep#534 (EDM4hep 1.3) plus k4FWCore#447, both in v3.2 (k4FWCore `main@086f292`).

Other changes in v3.2:
- **JetOut/UsedPFOs swap is gone.** v3.2 uses key4hep `k4Reco@c0a8ef1`, where `JetOut`
  holds the jets and `UsedPFOs` is the constituent subset. v3.1 files are still swapped,
  so analysis code must branch on the release.
- **`evt_max` defaults to -1** in MAIAConfig `8831727`. Keep passing `-n`; it is harmless.
- **The overlay is k4FWCore `OverlayTiming`** with `RandomMixBackgroundFiles=True`
  (`Overlay/overlay.py`). The directories are globbed in the options. The random draw is
  seeded by (`--RandSeed`, event number, run number).
- **Calorimeter truth-coning is opt-in** (`--doCaloConing`, 0.6 rad). v3.1 always applied
  it, so Pandora now sees every selected hit by default.
- **LCContent 3.2.0 → 5.1.1.** v3.1 jet/PFO results are not a v3.2 baseline. On 2 vbfZ
  events, event 0 had PFOs carrying 1358 GeV out of 2993 GeV of clusters, whereas v3.1
  had 3090 = 3090. This is not understood yet.
- **k4geo 00-26 → 00-27.** In MAIA_v0 the beampipe and nozzle were re-parametrised near
  the nozzle joint, the field moved to its own file, and a material composition was
  fixed. Sensitive detectors and readouts are unchanged, so v3.1 SIM digitises cleanly
  under v3.2.
- **Whizard 3.1.5 → 3.1.7.** Gridpacks integrated under v3.1 are untested with it, so
  regenerate or validate before new GEN.
- `pythia/` was rebuilt in v3.2. Its binaries are not interchangeable with the v3.1 tree.

The worktree is `../mucoll-slurm-v3.2`, kept separate so that v3.1 jobs queued from
`mucoll-slurm/` keep reading v3.1 scripts and binaries. Merge once they drain.

### BIB overlay (v3.2)

- **Library:** `/blue/avery/share/mucol/bib/BIB_v9/{sim_mp,sim_mm}`, 6663 + 6662 files,
  99 GB per beam. Its origin is recorded in `README.md` there. Override with `MUCOLL_BIB`.
- **`--OverlayFullNumberBackground N` is per beam.** 1666 = 100 % of a bunch crossing.
- **Tools:** `scripts/submit_bib.py` → `scripts/bib_digireco.sh`. DIGI+RECO reuses the
  existing `_v3p1` SIM: event i = entry i%50 of sim job i//50.
  - Output goes to `<samples>/<KEY>_v3p2_bib<N>[_cc][_tc]/`.
  - `--bib 0` makes the no-BIB twin of the same events.
  - `scripts/bib_bench_summary.py` turns the worker logs into a cost table.
- **Pitfalls:**
  - Use a unique `--RandSeed` per job; `submit_bib.py` hashes it from the sample, sim job
    and entry.
  - Pass `--doOverlayFull` to RECO too. Its only effect there is to drop the hit
    collections (>1 GB/event with BIB).
  - The Yoke is not overlaid.
- **Calorimeter coning (`--calo-coning`) is a truth cone of 0.6 rad around every stable
  generator particle,** so it also cones the VBF tag neutrinos/muons a few degrees from the
  beam, where BIB is densest. **`--tagveto-coning`** (output `_ccnotag`) cones around the same
  particles minus the hard-process tags: muons/neutrinos that are non-boson daughters of the
  status-21 beams, or their generator-level descendants (a radiated tag muon). It is the k4ext
  algorithm `HardProcessTagVeto` (`k4ext/ConeSeeds/`), inserted by `steering/*_tagveto.py`
  in front of MAIAConfig's coners; MAIAConfig is not modified. On ZH it vetoes nothing, so it
  equals `--calo-coning`. Build it in the container with `bash k4ext/build.sh`; like
  `pythia/`, rebuild after every image bump.
- **A 100 % BIB digi event is ~2.3 GB compressed.** ROOT's default TTreeCache then overflows
  a 32-bit int and `TTree::GetEntry` throws `std::bad_alloc`, so `--split` RECO writes
  `TTreeCache.Size: 0` to `./.rootrc`. Production (single process) never writes digi.

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

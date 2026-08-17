# Running on HiPerGator (HPG)

This is the batch framework for the muon-collider simulation chain on HPG. Every job
runs the full pipeline **GEN → SIM → DIGI → RECO** inside an Apptainer container with a
spack-managed software stack. This README is self-contained: it covers install, running
productions, adding samples, and running the stages by hand for debugging.

The pipeline stages:
- **GEN** — event generation. Whizard (matrix element + Pythia8 shower → `.hepmc`),
  the particle gun (`pgun`, fast → `.edm4hep.root`), or a standalone Pythia8 binary.
- **SIM** — full detector simulation via `ddsim` (Geant4), geometry **MAIA_v0**.
- **DIGI** — digitization via `k4run`.
- **RECO** — reconstruction via `k4run` (includes Pandora).

---

## 1. One-time install

```bash
# pick a working dir
mkdir -p muoncollider && cd muoncollider
git clone git@github.com:leblanc-lab/mucoll-slurm.git
cd mucoll-slurm

source scripts/interact_hpg.sh     # grab a compute node (don't install on the login node)
./scripts/install_hpg.sh           # checks the CVMFS image + clones mucoll-benchmarks (v3.1, with submodules)
```

Build the standalone Pythia8 binaries once (only needed for the `pythia_ZH` and `lhe`
samples; rebuild only if the container image changes):

```bash
source scripts/shell_hpg.sh        # enter the container
source scripts/setup.sh            # load the spack environment
bash pythia/build.sh               # compiles MuMuToZH + LheToHepMC into pythia/
exit
```

---

## 2. How the framework is organized

The whole framework is **one dispatcher driven by a manifest**. You almost never edit
shell scripts — you pick a sample from a table and submit it.

```
run_chain.sh     one script that runs GEN→SIM→DIGI→RECO for ANY sample
samples.conf     the manifest: one row per sample (this is what you edit)
submit.py        submits N SLURM jobs for chosen sample(s)
cards/           the Whizard steering cards we own (cards/production/ + cards/gridpack/)
gen/             one small plugin per generator type (whizard, whizard_lhe, pgun, pythia)
lib/             shared code: env.sh (software paths), stages.sh (SIM/DIGI/RECO)
```

**Why it's built this way:** the *only* thing that differs between samples is event
generation. Detector simulation, digitization and reconstruction are identical for
everything, so they live once in `lib/stages.sh`. A "sample" is therefore just a row
in `samples.conf` saying *which generator* and *which card* to use.

A manifest row has four columns:

| column | meaning |
|--------|---------|
| `key` | the sample's name — used to select it and to name its output folder |
| `gen_type` | `whizard`, `whizard_lhe`, `pgun`, or `pythia` |
| `card` | the Whizard card in `cards/production/` (`-` if the generator needs none) |
| `gridpack` | pre-computed integration grids to reuse (`-` if none) |

See `samples.conf` for the full list and `cards/README.md` for the card naming
convention and the kinematic cuts of each card.

---

## 3. Running jobs (`submit.py`)

Run from the **login node** — no container needed, `submit.py` only talks to SLURM. It
reads `samples.conf`, validates your selection (and that each card exists) up front, then
submits `--njobs` SLURM jobs per sample, each running the full chain via `run_chain.sh`.

```bash
cd mucoll-slurm
python submit.py --list                          # always start here: list every sample
python submit.py -s ZH_bbbb_pythia -n 50 -e 10   # 50 jobs x 10 events = 500 events
```

### CLI reference

| Flag | Default | Meaning |
|------|---------|---------|
| `-s, --samples KEY [KEY …]` | — | one or more sample keys from `samples.conf` (run several at once) |
| `-n, --njobs N` | `1` | number of SLURM jobs per sample |
| `-e, --nevents N` | `10` | events generated per job (total/sample = `njobs × nevents`) |
| `-o, --output DIR` | `output/batch` | output dir, relative to the `muoncollider/` parent |
| `--tag LABEL` | none | suffix added to the output folder + log/job names; lets you run the **same** sample twice without overwriting |
| `--pgun PDG PT TMIN TMAX` | `11 100 10 170` | particle-gun parameters (only used by the `pgun` sample) |
| `--time HH:MM:SS` | `10:00:00` | SLURM walltime per job |
| `--mem SIZE` | `16G` | SLURM memory per job |
| `--cpus N` | `4` | SLURM `--cpus-per-task` |
| `--qos NAME` | `avery-b` | SLURM QOS. Default `avery-b` (burst queue) keeps long CPU jobs off the shared `avery` qos that GPU jobs draw CPUs from. Pass `--qos avery` to force the normal queue. |
| `--after JOBID` | none | hold these jobs until SLURM job `JOBID` finishes OK (`afterok` dependency) — used to chain production behind its gridpack |
| `--list` | — | print all samples (key, gen_type, card) and exit |
| `--dry-run` | — | build the SLURM scripts but do **not** submit (inspect first) |

### Examples

```bash
# Inspect what's available, and dry-run before committing
python submit.py --list
python submit.py -s ZH_bbbb_pythia -n 2 -e 5 --dry-run

# A single sample: 100 jobs x 50 events = 5k events
python submit.py -s ZH_bbbb_pythia -n 100 -e 50

# Several samples at once (each gets njobs x nevents)
python submit.py -s vbfZ_qq_pt500_pythia vbfZ_qq_pt500_whizard -n 100 -e 50 --qos avery-b

# Particle gun: electrons, pT 100 GeV, theta 10-170 deg
python submit.py -s pgun -n 5 -e 1000 --pgun 11 100 10 170

# Two productions of the SAME sample, kept separate with --tag
python submit.py -s ZH_bbbb_pythia -n 100 -e 50  --tag 5kEvt   # -> output/batch/ZH_bbbb_pythia_5kEvt/
python submit.py -s ZH_bbbb_pythia -n 200 -e 50  --tag 10kEvt  # -> output/batch/ZH_bbbb_pythia_10kEvt/

# Bigger walltime/memory for a heavy sample
python submit.py -s nunubb_Hmass_pt250 -n 100 -e 50 --time 12:00:00 --mem 24G
```

> **Events-per-job and walltime.** Detector SIM/DIGI/RECO dominate the runtime
> (reconstruction alone is ~hundreds of seconds *per event*). Keep `--nevents` modest so a
> job finishes inside `--time`: ~**50 ev/job** is a good default (≈5–6 h), ~10/job is the
> safe floor. Prefer many small jobs over few big ones.

### Submitting with a gridpack (chained)

If a sample uses a gridpack (its `gridpack` column in `samples.conf` is not `-`), generate
the gridpack first and chain the production behind it with `--after`, so production starts
automatically once the grid is ready (and is skipped if the gridpack fails). See section 6
for the gridpack details; the submit side is:

```bash
# 1. submit the gridpack, note the SLURM job id it prints
python make_gridpack.py vbfZ                       # -> "Submitted batch job 12345"

# 2. submit production held until that job succeeds
python submit.py -s vbfZ_qq_pt500_pythia -n 100 -e 50 --after 12345
```

One gridpack can feed several productions — pass the same `--after <id>` to each (e.g. both
`vbfZ_qq_pt500_pythia` and `vbfZ_qq_pt500_whizard` share the `vbfZ` gridpack).

### Monitoring

```bash
squeue -u $USER                                  # all your jobs
squeue -u $USER -h -o "%T" | sort | uniq -c      # count by state (PENDING/RUNNING/…)
squeue -u $USER -t RUNNING                        # what's actually running now
scontrol show job <JOBID> | grep -i dependency    # confirm a chained job's dependency
ls output/batch/                                  # samples appear here as they produce
tail -f output/batch/logs/<sample>_job_0.out      # follow a job's log
```

---

## 4. Output

```
output/batch/<sample_key>[_<tag>]/job_<id>/
    gen_output_<id>.hepmc            # or .edm4hep.root for pgun
    sim_output_<id>.edm4hep.root
    digi_output_<id>.edm4hep.root
    reco_output_<id>.edm4hep.root
output/batch/logs/<sample_key>[_<tag>]_job_<id>.{out,err}
```

Outputs are grouped by sample (folder = `<sample_key>`, plus `_<tag>` if you passed
`--tag`), so one folder holds the whole production of a sample.

---

## 5. Adding a new sample or card

**Case A — a new variant of an existing process** (e.g. a new decay/CR setting): just
write the card and add a manifest row.

1. Put the card in `cards/production/` following the naming convention
   (`cards/README.md`), e.g. `mumu_ZH_bbbb_pythiaSKII_10TeV.sin`.
2. Add a line to `samples.conf`:
   ```
   ZH_bbbb_pythiaSKII   whizard   mumu_ZH_bbbb_pythiaSKII_10TeV.sin   -
   ```
3. Submit: `python submit.py -s ZH_bbbb_pythiaSKII -n 1 -e 5 --dry-run` then for real.

That's it — no shell script to touch. `run_chain.sh` reads the row, finds the card,
and runs the chain.

**Case B — a brand-new generator type** (rare): add a `gen/<type>.sh` that defines a
`generate()` function producing `gen_output.<ext>` and setting `GEN_EXT`, then use that
`<type>` in the `gen_type` column. Use the existing `gen/*.sh` as templates.

**Tip — always smoke-test a new card first** with a tiny run before launching a big
production (the framework's seed handling and your card's `integrate`/`simulate` blocks
both need to be right):

```bash
source scripts/interact_hpg.sh     # compute node
source scripts/shell_hpg.sh        # enter the container
bash scripts/smoke_gen.sh <sample_key> 2     # runs GEN only, 2 events, prints the HepMC
exit
```

If your card needs a gridpack (slow phase-space integration), see section 6 below.

---

## 6. Gridpack workflow

**What a gridpack is.** Whizard has to integrate the matrix element (map out the
phase space) before it can generate events. For VBF/VBS processes this integration is
slow and would be repeated by *every* job. A **gridpack** is the integration result
(VAMP `.vg` grid files) computed **once** and then reused: with a gridpack, a job's GEN
step skips integration and goes straight to event generation (minutes → seconds).

**How it's wired.** Each gridpack-capable sample has a `gridpack` column in
`samples.conf` naming a directory under `output/gridpacks/`. `run_chain.sh`
**automatically** uses those grids if they exist, and silently falls back to full
integration if they don't. So "enabling" a gridpack just means generating it once.

### Worked example: vbfZ

The `vbfZ_*` samples point at the `mumu_vbfZ_pt500_10TeV` gridpack in the manifest
(the grid dir name matches the gridpack card stem):

```
$ grep vbfZ samples.conf
vbfZ_incl_pt500_pythia   whizard  mumu_vbfZ_incl_pt500_pythia_10TeV.sin  mumu_vbfZ_pt500_10TeV
vbfZ_qq_pt500_whizard    whizard  mumu_vbfZ_qq_pt500_whizard_10TeV.sin   mumu_vbfZ_pt500_10TeV
vbfZ_qq_pt500_pythia     whizard  mumu_vbfZ_qq_pt500_pythia_10TeV.sin    mumu_vbfZ_pt500_10TeV
```

**Step 1 — compute the grid once** (a ~24 h, 32-CPU SLURM job). This integrates
`cards/gridpack/mumu_vbfZ_pt500_10TeV.gridpack.sin` and writes the grids to
`output/gridpacks/mumu_vbfZ_pt500_10TeV/`:

```bash
python make_gridpack.py vbfZ
# process names: vbfH vbfZ vbfW bbbb nunuqq mumuqq
#                nunubb_Hmass_pt250 nunuqq_Zmass_pt250 lnuqq_Wmass_pt250
# (no argument = submit all of them)
```

**Step 2 — wait for it, then confirm the grids exist:**

```bash
squeue -u $USER
ls output/gridpacks/mumu_vbfZ_pt500_10TeV/*.vg   # should list vbfz.m1.vg, vbfz.m2.vg, ...
```

**Step 3 — submit production.** The grids are picked up automatically because the manifest
already points there — you don't pass the gridpack on the command line. Two cases:

```bash
# (a) grids already exist on disk: just submit
python submit.py -s vbfZ_qq_pt500_pythia -n 100 -e 50

# (b) you submitted the gridpack in step 1 and it's still running: chain with --after
#     (production stays PENDING until the gridpack job succeeds)
python make_gridpack.py vbfZ                                  # -> Submitted batch job 12345
python submit.py -s vbfZ_qq_pt500_pythia -n 100 -e 50 --after 12345
```

The job log will print `Gridpack staged from .../mumu_vbfZ_pt500_10TeV` during GEN. (If the
grids were missing you'd instead see `NOTE: no grids ... — running full phase-space
integration`.) **One gridpack serves all three `vbfZ_*` samples**, because they share the
same matrix element — you only integrate once, and you can point several productions at the
same `--after <id>`.

> A gridpack is only valid if its `cards/gridpack/*.gridpack.sin` has the **same process
> and cuts** as the production card. The two are kept in sync by the naming convention
> (`mumu_vbfZ_pt500_*`); if you change a production card's process/cuts, regenerate its
> gridpack.

---

## 7. Running the stages by hand (debugging)

Sometimes you want to run one stage at a time — to debug a card or inspect intermediate
files. Get a compute node, enter the container, and load the environment. **Run these
from the `mucoll-slurm/` directory** — `scripts/` and `pythia/` are here, while
`mucoll-benchmarks-v3.1/` is its sibling one level up (hence the `../` prefixes below):

```bash
source scripts/interact_hpg.sh     # compute node (don't run on the login node)
source scripts/shell_hpg.sh        # enter the container (--cleanenv, so the host
                                   #   `module load python` doesn't break Python here)
source scripts/setup.sh            # load the spack software stack
```

Set the detector geometry once per shell. No Pandora settings copy is needed any more —
v3.1 resolves them absolutely, wherever you run from:

```bash
source ../mucoll-benchmarks-v3.1/setup_config.sh ../mucoll-benchmarks-v3.1/ MAIA_v0
# Confirm it prints MUCOLL_GEOM_NAME = MAIA_v0 and MUCOLL_CONFIG_NAME = MAIAConfig
```

Then run the four stages. Example with the particle gun (swap the GEN step for a Whizard
card if you want a physics process):

```bash
# GEN — particle gun: 1 electron, pT 100 GeV, theta 10–170 deg
python ../mucoll-benchmarks-v3.1/generation/pgun/pgun_edm4hep.py \
    -p 1 -e 1 --pdg 11 --pt 100 --theta 10 170 -- gen_output.edm4hep.root

# GEN — Whizard card instead (writes <sample>.hepmc; rename to gen_output.hepmc):
#   whizard cards/production/mumu_ZH_bbbb_pythia_10TeV.sin

# SIM — Geant4 detector simulation
ddsim --steeringFile ../mucoll-benchmarks-v3.1/simulation/steer_baseline.py \
    --numberOfEvents 1 --inputFiles gen_output.* --outputFile sim_output.edm4hep.root

# DIGI — steering now comes from the per-geometry config package set above
k4run $MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/digi_steer.py \
    --IOSvc.Input sim_output.edm4hep.root --IOSvc.Output digi_output.edm4hep.root

# RECO
k4run $MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/reco_steer.py \
    --IOSvc.Input digi_output.edm4hep.root --IOSvc.Output reco_output.edm4hep.root
```

These are exactly the commands `run_chain.sh` runs for you in batch — running them by
hand is only for debugging. To validate just the GEN step of a manifest sample, use the
`scripts/smoke_gen.sh <sample_key>` helper described in section 5.

---

## Reference

- `samples.conf` — the sample manifest (all available samples).
- `cards/README.md` — Whizard card naming convention and the kinematic cuts of each card.
- `scripts/` — `install_hpg.sh`, `interact_hpg.sh`, `shell_hpg.sh`, `setup.sh`,
  `smoke_gen.sh`, `make_gridpack.py`.

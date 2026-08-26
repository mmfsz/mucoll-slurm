# Running the muon-collider simulation chain on HiPerGator

This is a step-by-step guide to generating muon-collider simulation samples on
**HiPerGator (HPG)**. It assumes no prior knowledge of this codebase. If you follow it
top to bottom you will have a working setup and your first reconstructed events in about
an hour, most of which is waiting.

**What this framework does.** It turns a *physics process* (say, "a Higgs boson produced
in vector-boson fusion, decaying to two b quarks") into *reconstructed detector data* —
the same kind of data a real experiment would record. That happens in four stages:

| Stage | What it does | Tool | Output |
|-------|--------------|------|--------|
| **GEN** | Simulates the collision itself: which particles are produced, with what momenta. | Whizard, Pythia8, or a particle gun | `.hepmc` (or `.edm4hep.root`) |
| **SIM** | Tracks those particles through the detector, simulating the energy they deposit. | `ddsim` (Geant4) | `sim_output.edm4hep.root` |
| **DIGI** | Converts energy deposits into realistic electronic signals ("hits"). | `k4run` | `digi_output.edm4hep.root` |
| **RECO** | Reconstructs physics objects (tracks, clusters, particles, jets) from those hits. | `k4run` (Pandora + FastJet) | `reco_output.edm4hep.root` |

Every stage runs inside an **Apptainer container** — a pre-packaged copy of all the
physics software (Geant4, Whizard, Pythia8, Pandora, …). You never install that software
yourself; you just enter the container.

Detector geometry throughout is **MAIA_v0**, software release **MAIA v3.1**.

---

## 0. Before you start

Run these four checks first. Each takes a second, and each corresponds to a way the
install can fail later with a confusing error.

```bash
# 1. You can submit jobs to the avery account (the default --qos is avery-b).
sacctmgr show assoc user=$USER format=account,qos -n
#    -> must list  avery  and  avery-b . If it prints nothing, ask to be added
#       to the group before going further — sbatch will reject your jobs.

# 2. CVMFS is mounted, which is where the container image lives.
ls -d /cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1-amd64
#    -> must print that path. If not, try a different compute node.

# 3. You have a python3 and apptainer. Both are on the default PATH — no module load.
python3 --version && apptainer --version

# 4. You have somewhere with space for the output.
ls -d /cmsuf/data/store/user/$USER /cmsuf/data/store/user/$(echo $USER | tr -d .) 2>/dev/null
#    -> either one appearing is fine; the code tries both spellings, because an
#       HPG username like m.mazza maps to a /cmsuf directory named mmazza.
#    -> if NEITHER exists, read the warning in section 5 BEFORE your first
#       production. Test jobs are fine without it.
```

You do **not** need a GitHub account or an SSH key — the repository is public and section 1
clones it over HTTPS.

Finally, pick a place to work. Use your group's `/blue` area, not your home directory
(home has a small quota):

```bash
mkdir -p /blue/avery/$USER && cd /blue/avery/$USER
```

> **Login nodes vs compute nodes.** When you `ssh` into HPG you land on a *login node*,
> which is shared by everyone and must not be used for real work. Anything that computes —
> compiling, running the container, generating events — belongs on a *compute node*.
> Submitting jobs (`submit.py`, `squeue`) is fine on the login node.
> `source scripts/interact_hpg.sh` gets you an interactive compute node.

---

## 1. One-time install

### 1.1 Get the code

**The branch matters.** This guide describes the **MAIA v3.1** workflow, which lives on
the `maia-v3.1` branch. The default branch (`main`) is the older pre-v3.1 setup and will
not work with these instructions.

```bash
cd /blue/avery/$USER
mkdir -p muoncollider && cd muoncollider

git clone -b maia-v3.1 https://github.com/mmfsz/mucoll-slurm.git
# (if you have an SSH key registered with GitHub you can use
#  git@github.com:mmfsz/mucoll-slurm.git instead — it makes no difference)

cd mucoll-slurm
git branch --show-current        # must print: maia-v3.1
```

The parent directory `muoncollider/` matters too: the framework locates its sibling
directories relative to the repo, so keep the layout below.

```
muoncollider/                  <- you are here
├── mucoll-slurm/              <- this repo
├── mucoll-benchmarks-v3.1/    <- created by install_hpg.sh in the next step
└── output/                    <- created automatically when jobs run
```

### 1.2 Run the installer

Get a compute node first, then run the installer:

```bash
source scripts/interact_hpg.sh     # allocates an interactive compute node (16 cpus, 32 GB, 8 h)
./scripts/install_hpg.sh
```

This does two things:

- **Checks the container image.** It is served from CVMFS at
  `/cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1-amd64`, so
  there is nothing to download. If the installer says the image is missing, `/cvmfs` is
  not mounted on your node — try another node, or pull a local copy as the error message
  explains.
- **Clones `mucoll-benchmarks`** (the MuonColliderSoft detector/steering configuration)
  into `../mucoll-benchmarks-v3.1/`, **with submodules**, at a **pinned revision**. The
  submodules are essential: v3.1 keeps the digitization and reconstruction steering in a
  per-geometry submodule (`configs/MAIAConfig/`), and nothing works without it.

It takes well under a minute and ends with `=== Setup complete ===` and a summary of the
layout.

> **Why the benchmarks revision is pinned.** Two reasons. First, reproducibility: if
> everyone cloned whatever was newest that day, two people running "the same sample" would
> silently be running different detector configurations. Second, upstream `main` is not
> always working — commit `2724176` (2026-08-18) left `generation/pgun/pgun_edm4hep.py`
> with a space-plus-tab indent that Python refuses to parse, which breaks the `pgun` sample
> outright. The pin (`ce72cf0`) is the revision every production in `PRODUCTION_LOG.md` was
> generated against, and `install_hpg.sh` additionally checks that the file parses before
> declaring success. To use a different revision deliberately:
> ```bash
> MUCOLL_BENCHMARKS_REF=<sha> ./scripts/install_hpg.sh
> ```

### 1.3 Build the standalone Pythia8 programs

Two small C++ programs (`MuMuToZH` and `LheToHepMC`) are compiled rather than shipped, so
you must build them once. They are used by the `pythia_ZH` sample and by every `*_lhe`
sample.

```bash
source scripts/shell_hpg.sh        # enter the container (an interactive shell opens)
source lib/env.sh                  # load the physics software environment
bash pythia/build.sh               # ~1 minute
exit                               # leave the container
```

A successful build ends with a line like `Build successful: 179K MuMuToZH`.

> **You must repeat this whenever the container image changes** — see section 9 for why
> and how to tell.

You are now installed. Section 2 checks it actually works.

---

## 2. Your first run: a 1-event smoke test

Before touching real physics, prove the whole pipeline works end to end. The **particle
gun** (`pgun`) sample fires a single known particle into the detector — no physics
generator involved, so it is fast and it isolates the detector chain.

From `mucoll-slurm/`, on a compute node:

```bash
OUT=/blue/avery/$USER/muoncollider/output/samples
MUON=/blue/avery/$USER/muoncollider

apptainer exec --cleanenv --bind /cvmfs --bind "$MUON" \
    /cvmfs/unpacked.cern.ch/ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:v3.1-amd64 \
    bash "$MUON/mucoll-slurm/run_chain.sh" pgun 0 1 "$OUT" "$MUON/mucoll-benchmarks-v3.1"
```

Reading that command: `run_chain.sh <SAMPLE_KEY> <JOB_ID> <NEVENTS> <OUTPUT_DIR> <BENCHMARKS>`.
So this is sample `pgun`, job number `0`, **1** event.

It takes roughly 5-10 minutes and prints each stage as it goes (`--- Generation ---`,
`--- Simulation ---`, `--- Digitization ---`, `--- Reconstruction ---`). When it finishes:

```bash
ls -lh "$OUT/pgun/job_0/"
# gen_output_0.edm4hep.root  sim_output_0.edm4hep.root
# digi_output_0.edm4hep.root reco_output_0.edm4hep.root
```

Four files means the whole chain — container, geometry, digitization, Pandora
reconstruction — is working. If it does, you are ready for real samples.

---

## 3. How the framework is organized

The whole thing is **one dispatcher driven by a manifest**. You almost never edit shell
scripts — you pick a sample from a table and submit it.

```
run_chain.sh     one script that runs GEN->SIM->DIGI->RECO for ANY sample
samples.conf     the manifest: one row per sample (this is what you edit)
submit.py        submits N SLURM jobs for chosen sample(s)
cards/           the Whizard steering cards we own (cards/production/ + cards/gridpack/)
gen/             one small plugin per generator type (whizard, whizard_lhe, pgun, pythia)
lib/             shared code: image.sh (which container), env.sh (software paths),
                 stages.sh (SIM/DIGI/RECO)
scripts/         setup + helper scripts (see the Reference at the end)
```

**Why it is built this way:** the *only* thing that differs between samples is event
generation. Detector simulation, digitization and reconstruction are identical for
everything, so they live once in `lib/stages.sh`. A "sample" is therefore just a row in
`samples.conf` naming *which generator* and *which card* to use.

A manifest row has four columns:

| column | meaning |
|--------|---------|
| `key` | the sample's name — used to select it and to name its output folder |
| `gen_type` | `whizard`, `whizard_lhe`, `pgun`, or `pythia` |
| `card` | the Whizard card in `cards/production/` (`-` if the generator needs none) |
| `gridpack` | pre-computed integration grids to reuse (`-` if none) |

The four generator types:

- **`whizard`** — Whizard computes the matrix element *and* Pythia8 showers and decays it,
  all in one step. The usual choice.
- **`whizard_lhe`** — Whizard writes parton-level events to an LHE file, then our standalone
  `pythia/LheToHepMC` decays and showers them. Decouples the matrix element from the
  shower, so you can vary one without the other.
- **`pgun`** — particle gun: fires single particles of a chosen type and momentum. For
  detector studies and smoke tests.
- **`pythia`** — our standalone `pythia/MuMuToZH`: Pythia8 generates the process from
  scratch, with no Whizard involved.

List every available sample with `python3 submit.py --list`, and see `cards/README.md` for
the card naming convention and each card's kinematic cuts.

---

## 4. Running a production (`submit.py`)

This is how you make real samples: `submit.py` submits `--njobs` independent SLURM jobs
per sample, each running the full chain for `--nevents` events. Every job uses a different
random seed, so the events differ.

Run it from the **login node** and from inside `mucoll-slurm/` — no container needed,
`submit.py` only talks to SLURM.

> **Use `python3`, not `python`.** HPG has `/usr/bin/python3` everywhere, but there is no
> bare `python` command unless you `module load python`. `submit.py` needs only the
> standard library and runs on Python 3.9+, so no module load is required.

```bash
cd /blue/avery/$USER/muoncollider/mucoll-slurm
python3 submit.py --list                          # always start here: list every sample
python3 submit.py -s pgun -n 2 -e 5 --dry-run     # see what WOULD be submitted
python3 submit.py -s ZH_bbbb_pythia -n 50 -e 10   # 50 jobs x 10 events = 500 events
```

`submit.py` validates your selection and checks each card exists *before* submitting
anything, so a typo costs you nothing.

### CLI reference

| Flag | Default | Meaning |
|------|---------|---------|
| `-s, --samples KEY [KEY …]` | — | one or more sample keys from `samples.conf` (run several at once) |
| `-n, --njobs N` | `1` | number of SLURM jobs per sample |
| `-e, --nevents N` | `10` | events generated per job (total per sample = `njobs × nevents`) |
| `--indices N [N …]` | — | submit exactly these job indices instead of `0..njobs-1` — use it to re-run specific failed jobs, keeping their original seeds and `job_<N>/` directories |
| `-o, --output DIR` | `<base>/samples` | output dir (absolute, or relative to `muoncollider/`) — see section 5 |
| `--tag LABEL` | none | suffix added to the output folder + log/job names; lets you run the **same** sample twice without overwriting |
| `--pgun PDG PT TMIN TMAX` | `11 100 10 170` | particle-gun parameters (only used by the `pgun` sample) |
| `--time HH:MM:SS` | `10:00:00` | SLURM walltime per job |
| `--mem SIZE` | `16G` | SLURM memory per job |
| `--cpus N` | `4` | SLURM `--cpus-per-task` |
| `--qos NAME` | `avery-b` | SLURM QOS. The default `avery-b` is the *burst* queue, which keeps long CPU jobs off the shared `avery` qos that GPU jobs draw CPUs from. Pass `--qos avery` to force the normal queue. |
| `--after JOBID` | none | hold these jobs until SLURM job `JOBID` finishes OK (`afterok`) — used to chain a production behind its gridpack (section 6) |
| `--list` | — | print all samples (key, gen_type, card) and exit |
| `--dry-run` | — | write the SLURM script and print its path, but do **not** submit — read the script before committing to a big production |

### Examples

```bash
# A single sample: 100 jobs x 50 events = 5k events
python3 submit.py -s ZH_bbbb_pythia -n 100 -e 50

# Several samples at once (each gets njobs x nevents)
python3 submit.py -s vbfZ_qq_pt500_pythia vbfZ_qq_pt500_whizard -n 100 -e 50

# Particle gun: electrons (PDG 11), pT 100 GeV, polar angle 10-170 deg
python3 submit.py -s pgun -n 5 -e 1000 --pgun 11 100 10 170

# Two productions of the SAME sample, kept apart with --tag
python3 submit.py -s ZH_bbbb_pythia -n 100 -e 50 --tag 5kEvt    # -> .../ZH_bbbb_pythia_5kEvt/
python3 submit.py -s ZH_bbbb_pythia -n 200 -e 50 --tag 10kEvt   # -> .../ZH_bbbb_pythia_10kEvt/

# Re-run three jobs that failed
python3 submit.py -s ZH_bbbb_pythia -e 50 --indices 7 23 41

# Bigger walltime/memory for a heavy sample
python3 submit.py -s nunubb_Hmass_pt250 -n 100 -e 50 --time 12:00:00 --mem 24G
```

> **How many events per job?** SIM/DIGI/RECO dominate the runtime — reconstruction alone
> is *hundreds of seconds per event*. Keep `--nevents` modest so a job finishes inside
> `--time`: **~50 events/job** is a good default (≈5-6 h), ~10/job is the safe floor.
> Prefer many small jobs over a few big ones — they schedule sooner and a failure costs
> less.

### Monitoring

```bash
squeue -u $USER                                   # all your jobs
squeue -u $USER -h -o "%T" | sort | uniq -c       # count by state (PENDING/RUNNING/…)
scontrol show job <JOBID> | grep -i dependency    # confirm a chained job's dependency

# where the logs are (run from mucoll-slurm/ — mucoll_paths is imported from there):
python3 -c 'import mucoll_paths as m; print(m.samples_base() / "logs")'
tail -f <that path>/<sample>_job_0.out            # follow one job
```

`submit.py` also appends every production to `PRODUCTION_LOG.md`, recording the git commit,
the parameters, the SLURM job ids and the output directories — so you can always trace a
sample back to the exact code that made it.

---

## 5. Where the output goes

Productions are written to **`/cmsuf/data/store/user/<you>/mucoll/`**, not `/blue`. `/blue`
is a shared group quota with little headroom (~14 T of 119 T for all of `avery`), while
`/cmsuf` is a Lustre filesystem with hundreds of TB free — and a single full-chain
production of four samples is ~1.3 T, because every stage is kept.

```
<base>/samples/<sample_key>[_<tag>]/job_<id>/
    gen_output_<id>.hepmc            # or .edm4hep.root for pgun
    sim_output_<id>.edm4hep.root
    digi_output_<id>.edm4hep.root
    reco_output_<id>.edm4hep.root
<base>/samples/logs/<sample_key>[_<tag>]_job_<id>.{out,err}
<base>/gridpacks/<gridpack>/*.vg
```

Always check where `<base>` resolves to *for you* before a big production:

```bash
python3 -c 'import mucoll_paths as m; print("samples:  ", m.samples_base()); print("gridpacks:", m.gridpack_base())'
```

> **If you have no `/cmsuf` area yet**, that command will print a path under
> `muoncollider/output/` on `/blue` instead — the fallback. That is fine for a few test
> jobs but **will exhaust the group quota** in a real production. Ask for a `/cmsuf`
> directory, or point the output elsewhere:
> ```bash
> MUCOLL_OUTPUT=/path/with/space python3 submit.py ...   # override the root
> MUCOLL_GRIDPACKS=/path/to/grids python3 submit.py ...  # override just the grids
> ```
> Note that samples and gridpacks can legitimately resolve to *different* roots: gridpacks
> only move to `<base>/gridpacks` once that directory exists, so existing grids keep
> working instead of silently re-integrating from an empty new directory.

---

## 6. Gridpacks (making Whizard start faster)

**What a gridpack is.** Before Whizard can generate events it must *integrate* the matrix
element — map out the phase space. For VBF/VBS processes this takes hours, and every
single job would repeat it. A **gridpack** is that integration result (VAMP `.vg` grid
files), computed **once** and reused: with a gridpack, a job's GEN step skips integration
and goes straight to generating events (hours → seconds).

**How it is wired.** Each gridpack-capable sample names a grid directory in the `gridpack`
column of `samples.conf`. `run_chain.sh` uses those grids **automatically** if they exist,
and falls back to full integration if they do not. So "enabling" a gridpack just means
generating it once — you never pass it on the command line.

### Worked example: vbfZ

All three `vbfZ_*` samples share one gridpack, because they share the same matrix element:

```bash
$ grep vbfZ samples.conf
vbfZ_incl_pt500_pythia   whizard  mumu_vbfZ_incl_pt500_pythia_10TeV.sin  mumu_vbfZ_pt500_10TeV
vbfZ_qq_pt500_whizard    whizard  mumu_vbfZ_qq_pt500_whizard_10TeV.sin   mumu_vbfZ_pt500_10TeV
vbfZ_qq_pt500_pythia     whizard  mumu_vbfZ_qq_pt500_pythia_10TeV.sin    mumu_vbfZ_pt500_10TeV
```

**Step 1 — compute the grid once** (a ~24 h, 32-CPU SLURM job). Run from `mucoll-slurm/`:

```bash
python3 make_gridpack.py vbfZ        # -> "Submitted vbfZ gridpack job: Submitted batch job 12345"
```

Available process names: `vbfH vbfZ vbfW bbbb nunuqq mumuqq ZH_bbbb_whizard ZH_bbbb_lhe
nunubb_Hmass_pt250 nunuqq_Zmass_pt250 lnuqq_Wmass_pt250`. With no argument it submits all
of them.

**Step 2 — wait, then confirm the grids exist:**

```bash
squeue -u $USER
ls $(python3 -c 'import mucoll_paths as m; print(m.gridpack_base())')/mumu_vbfZ_pt500_10TeV/*.vg
```

**Step 3 — submit the production.** Two cases:

```bash
# (a) the grids already exist on disk: just submit
python3 submit.py -s vbfZ_qq_pt500_pythia -n 100 -e 50

# (b) the gridpack job is still running: chain behind it, so production starts
#     automatically when the grid is ready (and is skipped if the gridpack fails)
python3 submit.py -s vbfZ_qq_pt500_pythia -n 100 -e 50 --after 12345
```

One gridpack can feed several productions — pass the same `--after <id>` to each.

The job log prints `Gridpack staged from .../mumu_vbfZ_pt500_10TeV` during GEN. If the
grids were missing you would instead see `NOTE: no grids ... — running full phase-space
integration`, and the job would take hours longer.

> A gridpack is only valid if its `cards/gridpack/*.gridpack.sin` has the **same process
> and cuts** as the production card. The naming convention keeps them in sync
> (`mumu_vbfZ_pt500_*`); if you change a production card's process or cuts, regenerate its
> gridpack.

---

## 7. Running the stages by hand

Batch submission is how you make samples. Running by hand is how you *debug* them — when
a card misbehaves, or you want to inspect an intermediate file, or you changed the
reconstruction and want to see the effect without regenerating everything.

### 7.1 Setting up an interactive session

All three commands below are needed, in this order:

```bash
cd /blue/avery/$USER/muoncollider/mucoll-slurm

source scripts/interact_hpg.sh     # 1. get a compute node
source scripts/shell_hpg.sh        # 2. enter the container
source lib/env.sh                  # 3. load the physics software
```

Then set the detector geometry — once per shell:

```bash
source ../mucoll-benchmarks-v3.1/setup_config.sh ../mucoll-benchmarks-v3.1 MAIA_v0

# check it took — this is the directory the DIGI/RECO steering lives in:
ls "$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME"/{digi,reco}_steer.py
```

(`MUCOLL_CONFIG` ends in `configs/MAIAConfig` and `MUCOLL_CONFIG_NAME` is `MAIAConfig`, so
together they point at the nested `configs/MAIAConfig/MAIAConfig/`. That doubling looks odd
but is correct — the outer directory is the git submodule, the inner one is the Python
package.)

Notes on why each step is what it is:

- **`source`, not `bash`.** These scripts set environment variables in *your* shell.
  Running them with `bash` would set them in a child shell that immediately exits, and
  nothing would happen. (Scripts you `bash` instead: `install_hpg.sh`, `pythia/build.sh`
  and `run_chain.sh`.)
- **`lib/env.sh`, not `scripts/setup.sh`.** `lib/env.sh` loads the spack software stack
  (by sourcing `scripts/setup.sh` for you) *and* adds the Whizard libraries. Sourcing only
  `setup.sh` is enough for `ddsim`/`k4run`, and `whizard` will even start — but it then
  integrates, compiles its process library, and *only then* aborts with
  `*** FATAL ERROR: libomega.so.0: cannot open shared object file`. Because that comes
  after pages of healthy-looking output, it is easy to misread as a problem with your card.
- **`--cleanenv`** is used when entering the container (`shell_hpg.sh` does it for you).
  Without it, the host's `module load python` leaks `PYTHONHOME` into the container and
  breaks its Python with `No module named 'encodings'`.
- **No `PandoraSettings` copy is needed.** v3.1 hands Pandora an absolute settings path, so
  reconstruction runs correctly from any directory. (Older instructions told you to copy
  that directory — ignore them.)

### 7.2 The full chain, one command

The simplest way to run everything by hand is the same dispatcher batch jobs use:

```bash
bash run_chain.sh <SAMPLE_KEY> <JOB_ID> <NEVENTS> <OUTPUT_DIR> <BENCHMARKS_PATH> [extra…]

# e.g. 5 events of the ZH -> bbbb sample into a scratch directory:
MUON=/blue/avery/$USER/muoncollider
bash run_chain.sh ZH_bbbb_pythia 0 5 /blue/avery/$USER/test_out "$MUON/mucoll-benchmarks-v3.1"
```

It does everything: creates a scratch working directory, runs GEN/SIM/DIGI/RECO, moves the
four output files into `<OUTPUT_DIR>/<SAMPLE_KEY>/job_<JOB_ID>/`, and cleans up. `JOB_ID`
sets the random seed (`seed = 1234 + JOB_ID`), so two runs with the same `JOB_ID` produce
*identical* events — use different ids when you want different events.

For `pgun`, the `[extra…]` arguments are `PDG PT THETA_MIN THETA_MAX`:

```bash
bash run_chain.sh pgun 0 10 /blue/avery/$USER/test_out "$MUON/mucoll-benchmarks-v3.1" 13 100 10 170
```

### 7.3 One stage at a time

**Do section 7.1 first, in this same shell** — these commands need `lib/env.sh` on the
environment and `$MUCOLL_CONFIG` set by `setup_config.sh`. (If `$MUCOLL_CONFIG` is empty you
will see errors about `//digi_steer.py`.)

When you want to stop and look between stages, run them individually. Work in a scratch
directory, because these commands write into the current directory:

```bash
mkdir -p /blue/avery/$USER/test_manual && cd /blue/avery/$USER/test_manual
SLURM_DIR=/blue/avery/$USER/muoncollider/mucoll-slurm
BENCH=/blue/avery/$USER/muoncollider/mucoll-benchmarks-v3.1
NEV=20
```

**GEN — option A: particle gun** (no card, fast):

```bash
python "$BENCH/generation/pgun/pgun_edm4hep.py" \
    -p 1 -e $NEV --pdg 13 --pt 100 --theta 10 170 -- gen_output.edm4hep.root
```

**GEN — option B: a Whizard card** (real physics). Copy the card first and edit the copy,
so you never modify the tracked original — and set the seed and event count in it, which
is exactly what `gen/whizard.sh` does for you in batch:

```bash
cp "$SLURM_DIR/cards/production/mumu_ZH_bbbb_pythia_10TeV.sin" job.sin
sed -i "s/seed *=.*/seed = 1234/"        job.sin      # change 1234 to vary the events
sed -i "s/n_events = .*/n_events = $NEV/" job.sin
whizard job.sin
mv *.hepmc gen_output.hepmc                            # Whizard names it after the card
```

> **Careful with the seed.** The `*` in `s/seed *=.*/` is not optional. A regex expecting
> exactly one space silently fails to match, leaving every job on seed 1234 — which once
> made an entire production consist of the same event repeated. If you edit this, verify
> the seed actually changed in `job.sin`.

**SIM — Geant4 detector simulation** (the slow stage, minutes per event):

```bash
ddsim --steeringFile "$BENCH/simulation/steer_baseline.py" \
    --numberOfEvents $NEV \
    --inputFiles gen_output.* \
    --outputFile sim_output.edm4hep.root
```

**DIGI — digitization:**

```bash
k4run "$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/digi_steer.py" -n $NEV \
    --IOSvc.Input sim_output.edm4hep.root \
    --IOSvc.Output digi_output.edm4hep.root
```

**RECO — reconstruction:**

```bash
k4run "$MUCOLL_CONFIG/$MUCOLL_CONFIG_NAME/reco_steer.py" -n $NEV \
    --IOSvc.Input digi_output.edm4hep.root \
    --IOSvc.Output reco_output.edm4hep.root
```

> ### ⚠️ `-n $NEV` on DIGI and RECO is NOT optional
>
> The steering files declare `build_application(..., evt_max=10)` and never override it,
> so **without `-n` these two commands silently process only the first 10 events** of
> however many you simulated — no error, no warning, just a short file. You pay the full
> simulation cost and quietly throw most of it away. `k4run`'s `-n/--num-events` is the
> only way to override it; there is no steering-file setting for it.
>
> Always check afterwards that you got what you asked for:
> ```bash
> python3 -c "from podio.reading import get_reader; \
>   print(len(get_reader('reco_output.edm4hep.root').get('events')), 'events')"
> ```

### 7.4 Inspecting the output

```bash
# list the collections in a reconstructed file
python3 -c "
from podio.reading import get_reader
ev = get_reader('reco_output.edm4hep.root').get('events')[0]
for name in sorted(ev.getAvailableCollections()): print(name)"
```

A v3.1 reconstructed file should contain `SiTracks`, `PandoraClusters`, `PandoraPFOs` and
jets. Note that this production **swaps the `JetOut` and `UsedPFOs` collection names** —
the jets are in `UsedPFOs`.

### 7.5 Testing only the generator

Simulation costs minutes per event; generation costs seconds. So when you are working on a
*card*, run only the GEN step from section 7.3 and stop there — do not run `ddsim`. Section
7.1 must have been done in this shell (Whizard needs `lib/env.sh`):

```bash
cp "$SLURM_DIR/cards/production/<your_card>.sin" job.sin
sed -i "s/seed *=.*/seed = 1234/"       job.sin
sed -i "s/n_events = .*/n_events = 5/"  job.sin
whizard job.sin
```

Two things to check in Whizard's output before you trust the card:

- **The integrated cross-section.** Whizard prints it at the end of integration. If it is
  orders of magnitude larger than you expect, one of your cuts is not firing — see the
  warning in section 8.
- **The events themselves.** `grep -c "^E " *.hepmc` counts them; `head -40 *.hepmc` shows
  the first one.

---

## 8. Adding a new sample or card

**Case A — a new variant of an existing process** (a different decay, a different shower
setting): write the card and add a manifest row. No shell script to touch.

1. Put the card in `cards/production/`, following the naming convention in
   `cards/README.md`, e.g. `mumu_ZH_bbbb_pythiaSKII_10TeV.sin`.
2. Add a line to `samples.conf`:
   ```
   ZH_bbbb_pythiaSKII   whizard   mumu_ZH_bbbb_pythiaSKII_10TeV.sin   -
   ```
3. Test the generator alone first (section 7.5) and check the cross-section.
4. Dry-run, then submit:
   ```bash
   python3 submit.py -s ZH_bbbb_pythiaSKII -n 1 -e 5 --dry-run
   python3 submit.py -s ZH_bbbb_pythiaSKII -n 1 -e 5
   ```

**Case B — a brand-new generator type** (rare): add `gen/<type>.sh` defining a `generate()`
function that produces `gen_output.<ext>` and sets `GEN_EXT`, then use `<type>` in the
`gen_type` column. Use the existing `gen/*.sh` as templates.

> ### ⚠️ Never quote particle names in a Whizard `cuts =` expression
>
> `all Pt > 500 GeV ["W+", "W-"]` resolves to an **empty set**, so the condition is
> vacuously true and **the cut silently never fires**. (Quoted names work in `process`
> lines, but not in cuts.) Built-in names like `[Z]`, `[H]` and aliases are fine; for
> particles whose names cannot be written unquoted, define an alias:
> ```
> alias Wpm = "W+":"W-"
> cuts = all Pt > 500 GeV [Wpm]
> ```
> This bug once made a vbfW gridpack integrate at 30817 fb instead of ~527 fb. **A cut
> that does not bite shows up as a cross-section orders of magnitude too large** — so
> always check the integrated σ and the cut variable's distribution on a new card before
> trusting a production.

---

## 9. Rebuilding the Pythia binaries after an image change

**Do this whenever the container image changes** — when `lib/image.sh` is pointed at a new
release, when you set `MUCOLL_IMAGE` to a different image, or when the collaboration moves
to a new software stack.

**Why it is needed.** Everything else adapts to a new image on its own: `scripts/setup.sh`
asks the image which software stack it carries, and `lib/env.sh` searches the image for the
Whizard libraries. The `pythia/` programs are different, because they are *compiled*. When
you compile them, the compiler writes the full path of every library into the executable,
and those paths contain a random-looking code (a "spack hash") unique to one image:

```
/opt/spack/opt/spack/.../pythia8-8.315-duneejqda5mtzdxezvirg2bskzdrqfoy/lib
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ changes with the image
```

A new image has different hashes, so those paths no longer exist and the program cannot
start. The source is fine — only the recorded paths are stale.

**How you will notice you forgot.** Jobs fail almost immediately, in GEN. The job's `.err`
file says:

```
error while loading shared libraries: libpythia8.so: cannot open shared object file: No such file or directory
```

Only samples using these programs are affected — `ZH_bbbb_lhe`, `vbfH_bb_pt500_lhe`,
`vbfZ_qq_pt500_lhe`, `vbfW_qq_pt500_lhe` and `pythia_ZH`. Whizard-only and `pgun` samples
keep working, which makes the problem look sample-specific when it is not.

**The fix** (on a compute node, in the *new* image):

```bash
source scripts/interact_hpg.sh
source scripts/shell_hpg.sh
source lib/env.sh
bash pythia/build.sh
exit
```

**Check it worked** before submitting hundreds of jobs. `ldd` lists the libraries a program
needs and flags any it cannot find, so *no output* is exactly what you want:

```bash
source scripts/shell_hpg.sh
source lib/env.sh
add_hepmc3_libs                              # env.sh defines this; the GEN step calls it
ldd pythia/LheToHepMC | grep "not found"     # prints NOTHING if the rebuild worked
exit
```

For a stronger check, run two events of an LHE sample through the real dispatcher — that
exercises the same code path a job does:

```bash
MUON=/blue/avery/$USER/muoncollider
bash run_chain.sh ZH_bbbb_lhe 0 2 /blue/avery/$USER/test_out "$MUON/mucoll-benchmarks-v3.1"
```

> The binaries are deliberately **not** stored in git (they are in `.gitignore`), because a
> compiled file is only valid for the image it was built in. A fresh clone always means
> building them once.

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `git clone` asks for a password / `Permission denied (publickey)` | no SSH key registered with GitHub | use the HTTPS clone URL (section 1.1), or add an SSH key |
| Nothing in this guide matches the files you have | you are on the `main` branch | `git checkout maia-v3.1` |
| `install_hpg.sh`: `container image not found` | `/cvmfs` not mounted on this node | try another compute node, or pull a local `.sif` as the message explains |
| `setup_config.sh` prints `Config package not found`, and `$MUCOLL_CONFIG` is then empty (so later commands complain about `//digi_steer.py`) | benchmarks cloned without submodules | `git -C ../mucoll-benchmarks-v3.1 submodule update --init --recursive` |
| `python: command not found` | HPG has no bare `python` command | use `python3` (3.9+ is always present; no module load needed). Note this applies to the **host** only — inside the container `python` does exist, which is why section 7.3 uses it |
| `No module named 'encodings'` inside the container | host `PYTHONHOME` leaked in | enter with `--cleanenv` (i.e. use `scripts/shell_hpg.sh`) |
| `libpythia8.so: cannot open shared object file` | image changed, binaries stale | rebuild — section 9 |
| Whizard aborts with `*** FATAL ERROR: libomega.so.0: cannot open shared object file`, *after* it compiled the process library | you sourced `scripts/setup.sh` but not `lib/env.sh` | `source lib/env.sh` |
| RECO output has exactly 10 events | `-n` missing on the DIGI/RECO commands | section 7.3 — batch jobs already pass it for you |
| RECO got *faster* and its output *smaller* when the physics got heavier | the same 10-event truncation | as above |
| Every job produced identical events | seed not actually substituted | check `seed = 1234 + JOB_ID` really changed in `job.sin` |
| Cross-section orders of magnitude too large | a cut that never fires (quoted particle names) | section 8 |
| Jobs hit the walltime | too many events per job | lower `--nevents`, raise `--time` |
| `WARN: cannot create /scratch/local/...` in a job's `.err` | expected on HPG — no per-job scratch is provisioned | harmless; the job uses node-local `/tmp`, which is a large local disk |

---

## Reference

| Path | What it is |
|------|------------|
| `samples.conf` | the sample manifest — every available sample |
| `cards/README.md` | Whizard card naming convention and each card's kinematic cuts |
| `run_chain.sh` | the full-chain dispatcher (GEN→SIM→DIGI→RECO) |
| `submit.py` | SLURM submitter for productions |
| `make_gridpack.py` | submits Whizard integration jobs that produce gridpacks |
| `mucoll_paths.py` | resolves the image, the benchmarks checkout, and the output paths |
| `lib/image.sh` | the one place the container image is named |
| `lib/env.sh` | the one place the in-container software environment is set up |
| `lib/stages.sh` | the shared SIM/DIGI/RECO stages |
| `gen/*.sh` | one plugin per generator type |
| `scripts/install_hpg.sh` | one-time install (image check + benchmarks clone) |
| `scripts/interact_hpg.sh` | allocate an interactive compute node (`source` it) |
| `scripts/shell_hpg.sh` | enter the container (`source` it) |
| `scripts/setup.sh` | load the spack stack (sourced for you by `lib/env.sh`) |
| `PRODUCTION_LOG.md` | auto-appended record of every production submitted |
| `CLAUDE.md` | detailed conventions and framework internals |

The remaining scripts in `scripts/` — `smoke_gen.sh`, `redo_digireco.sh`,
`submit_redo_digireco.py`, `migrate_cards.sh` — are maintainer tools for validating or
repairing *existing* productions. You do not need them to generate samples, and they are
documented in `CLAUDE.md` rather than here.

### Environment variables

| Variable | Effect |
|----------|--------|
| `MUCOLL_IMAGE` | use a different container image (default in `lib/image.sh`) |
| `MUCOLL_BENCHMARKS` | use a different benchmarks checkout |
| `MUCOLL_BENCHMARKS_REF` | the benchmarks revision `install_hpg.sh` pins (default `ce72cf0`) |
| `MUCOLL_OUTPUT` | change the output root (`samples/` + `gridpacks/`) |
| `MUCOLL_GRIDPACKS` | change only where gridpacks are read/written |
| `MUCOLL_GEOMETRY` | detector geometry (default `MAIA_v0`) |

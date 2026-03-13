## HiPerGator Setup

These instructions are to run on the HiPerGator cluster.

### Clone and install

```bash
# Choose a working directory (e.g. under /blue/<group>/<user>/)
mkdir -p muoncollider && cd muoncollider

git clone git@github.com:leblanc-lab/mucoll-slurm.git
```

Run the install script from a compute node (it pulls the container image, which is large):

```bash
cd mucoll-slurm
source scripts/interact_hpg.sh
./scripts/hpg_install.sh
```

This will:
1. Pull the `mucoll-sim-ubuntu24:main` container image as a local `.sif` file
2. Clone `mucoll-benchmarks` and check out the `k4MuC` branch

After setup, the directory structure should look like:

```
muoncollider/
├── mucoll-slurm/
│   ├── mucoll-sim.sif          # Container image (pulled during install)
│   ├── run_chain.sh            # GEN/SIM/DIGI/RECO pipeline
│   ├── submit_jobs.py          # Submit batch jobs
│   ├── submit_scan.py          # Submit parameter scan jobs
│   └── scripts/
│       ├── hpg_install.sh      # One-time setup
│       ├── interact.sh         # Get an interactive compute node (OSCAR)
│       ├── interact_hpg.sh    # Get an interactive compute node (HPG)
│       ├── shell_hpg.sh        # Enter the container shell
│       └── setup.sh            # Load Spack environment (inside container)
├── mucoll-benchmarks/          # Steering files (k4MuC branch)
└── output/                     # Job outputs (created automatically)
    ├── batch/
    └── scan/
```

### Interactive testing

Before submitting batch jobs, test the workflow interactively:

```bash
# 1. Get a compute node
source scripts/interact_hpg.sh

# 2. Enter the container
source scripts/shell_hpg.sh

# 3. Load the environment (inside the container)
source scripts/setup.sh
```

You can then follow the standard GEN/SIM/DIGI/RECO commands from the main README.

### Submitting batch jobs

From the login node (no need to enter the container):

```bash
cd mucoll-slurm

# Standard batch: N identical particle-gun jobs
python submit_jobs.py

# Parameter scan: grid over PDG, pT, theta
python submit_scan.py
```

All paths are derived automatically from the script location. Edit the configuration section at the top of each script to change:
- `NUM_JOBS` / `NUM_JOBS_PER_POINT` -- number of jobs
- `NEVENTS_PER_JOB` -- events per job
- `PDG_LIST`, `PT_LIST`, `THETA_LIST` -- scan parameters (submit_scan.py only)

Each job runs inside the Apptainer container and executes the full chain:
**GEN** (particle gun) -> **SIM** (DDSim/Geant4) -> **DIGI** (k4run) -> **RECO** (k4run)

### Output

Jobs write EDM4hep ROOT files to the output directory:

```
output/batch/
├── logs/
│   ├── job_0.out
│   ├── job_0.err
│   ├── job_1.out
│   └── job_1.err
│   └── ...
├── job_0/
│   ├── gen_output_0.edm4hep.root
│   ├── sim_output_0.edm4hep.root
│   ├── digi_output_0.edm4hep.root
│   └── reco_output_0.edm4hep.root
└── job_1/
    └── ...
```

For parameter scans, outputs are organized by configuration:

```
output/scan/
├── pdg_11_pt_10_theta_10-170/
│   ├── logs/
│   ├── job_0/
│   └── job_1/
├── pdg_11_pt_50_theta_10-170/
└── ...
```

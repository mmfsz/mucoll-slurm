# Production log

Auto-appended by `submit.py` and `make_gridpack.py`. Each entry pins the git commit
that generated the jobs, their SLURM ids, and their output directories — so you can
`git checkout <sha>` to recover the exact code. Output dirs are relative to the
`muoncollider/` parent (`output/gridpacks/<gp>/`, `output/batch/<sample>/`).

**Container image** (all entries below): `ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main` (build 2026-02-19); `mucoll-sim.sif` sha256 `77246efe33b18bba6e0ac6babe2d03241660b586639c41cac135db4b0239e97d`.

---

## 2026-06-15 — gridpacks + ZH/VBF hadronic batch (backfilled by hand)
- commit: `90333296150f4aa2223730a77587baf4b7ba5679` (generating code; the tree was
  dirty at submit time and committed as this SHA immediately after — physics-generating
  files are identical. Not pushed to remote yet.)
- settings: harmonized cuts (boson/quark |eta|<2.3); integration `5:50000:"gw", 10:100000`;
  100 jobs x 50 events = 5k events per sample.
- gridpacks (jobid -> output dir):
  - `ZH_bbbb_lhe`: 34744628 -> `output/gridpacks/mumu_ZH_bbbb_lhe_10TeV/`
  - `ZH_bbbb_whizard`: 34744629 -> `output/gridpacks/mumu_ZH_bbbb_whizard_10TeV/`
  - `vbfZ` (shared by both vbfZ_qq productions): 34744630 -> `output/gridpacks/mumu_vbfZ_pt500_10TeV/`
  - `nunuqq_Zmass_pt250`: 34744632 -> `output/gridpacks/mumu_nunuqq_Zmass_pt250_10TeV/`
  - `lnuqq_Wmass_pt250`: 34744633 -> `output/gridpacks/mumu_lnuqq_Wmass_pt250_10TeV/`
  - `nunubb_Hmass_pt250`: 34744634 -> `output/gridpacks/mumu_nunubb_Hmass_pt250_10TeV/`
- production (jobid range, afterok dependency -> output dir):
  - `ZH_bbbb_lhe`: 34744635-34744734, afterok:34744628 -> `output/batch/ZH_bbbb_lhe/`
  - `ZH_bbbb_whizard`: 34744735-34744842, afterok:34744629 -> `output/batch/ZH_bbbb_whizard/`
  - `vbfZ_qq_pt500_whizard`: 34744843-34744942, afterok:34744630 -> `output/batch/vbfZ_qq_pt500_whizard/`
  - `nunuqq_Zmass_pt250`: 34744943-34745042, afterok:34744632 -> `output/batch/nunuqq_Zmass_pt250/`
  - `vbfZ_qq_pt500_pythia`: 34745043-34745145, afterok:34744630 -> `output/batch/vbfZ_qq_pt500_pythia/`
  - `lnuqq_Wmass_pt250`: 34745146-34745245, afterok:34744633 -> `output/batch/lnuqq_Wmass_pt250/`
  - `nunubb_Hmass_pt250`: 34745246-34745361, afterok:34744634 -> `output/batch/nunubb_Hmass_pt250/`

## 2026-06-15 17:33:26 — submit.py production
- commit: `3da846af8cc1bf12ba4a7e2fab1210e1d70fd99a` (clean)
- params: `-n 100 -e 50`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfZ_qq_pt500_lhe`: 100 jobs (ids 34747550–34747662) → `output/batch/vbfZ_qq_pt500_lhe/`

## 2026-06-16 09:01:01 — submit.py production
- commit: `3f1327e0d3127d858ce1acb317edc195d8cc66c7` (clean)
- params: `-n 100 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_whizard`: 100 jobs (ids 34813808–34814060) → `output/batch/ZH_bbbb_whizard/`

## 2026-06-16 10:03:14 — submit.py production
- commit: `9e0e572cf4a4fd3c63d79782eee548074949ec88` (clean; only the uncommitted file was this log, since committed)
- params: `-n 100 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_whizard`: 100 jobs (ids 34818147–34818246) → `output/batch/ZH_bbbb_whizard/`

## 2026-06-16 10:10:08 — submit.py production
- commit: `70ed209511ad77a35dd874e486d87373689226f7` (clean)
- params: `-n 1 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_lhe`: 21 jobs (ids 34818819–34818839) → `output/batch/ZH_bbbb_lhe/`

## 2026-06-16 10:10:08 — submit.py production
- commit: `70ed209511ad77a35dd874e486d87373689226f7` (clean)
- params: `-n 1 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfZ_qq_pt500_whizard`: 2 jobs (ids 34818840–34818841) → `output/batch/vbfZ_qq_pt500_whizard/`

## 2026-06-16 11:46:21 — make_gridpack.py
- commit: `397790a2b4072c0ad44f7e3a0f9bad9a7e707906` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfW`: jobid 34823027 → `output/gridpacks/mumu_vbfW_pt500_10TeV/`
    (COMPLETED in 2m23s; wrote `vbfw.m1.vg` [W+], `vbfw.m2.vg` [W-].)

## 2026-06-16 — vbfW_qq_pt500_lhe smoke test — NO production (STOPPED, inefficient gen)
- New sample `vbfW_qq_pt500_lhe` (card `mumu_vbfW_qq_pt500_lhe_10TeV.sin`), the
  charged-current LHE analog of `vbfZ_qq_pt500_lhe`. Card + samples.conf row + README
  added, gridpack built (above) — but **NOT submitted to production.**
- Smoke (`scripts/smoke_gen.sh vbfW_qq_pt500_lhe`, 5 and 50 events): Whizard
  **actual unweighting efficiency = 0.00 %** (vs `vbfZ_qq_pt500_lhe` = 6.10 % under the
  same recipe). The W+ component (`vbfw_i1`) integrates fine (Eff ~6-9 %, ~40 min/10k
  events), but the W- component (`vbfw_i2`) has a pathological VAMP iteration (a 178 %
  iteration with 56 % error spikes the weight ceiling) → integration Eff collapses to
  0.00 and the time estimate balloons to ~5h51m/10k events. Same failure mode as the
  inclusive `lnuqq_Wmass_pt250` (0.00 %, ~8 h/50 ev) that this sample was meant to fix.
- HepMC content is physically correct (LHE_DECAY applied: W→u/d/s/c quarks → gluons,
  pions, kaons; no leptonic W decays), so the mechanics work — the blocker is purely
  unweighting efficiency, NOT a wiring bug.
- Per the submit-only-if-efficient rule, production was **not** launched. Needs a fix
  (e.g. tuning the W- integration / phase-space mapping, more `gw` warmup, or capping the
  weight) before any `submit.py -s vbfW_qq_pt500_lhe`.

## 2026-06-16 12:07:54 — make_gridpack.py
- commit: `fc17a59bb26938ca879ae5dc83c5fbb7094d7b30` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `lnuqq_Wmass_pt250`: jobid 34825174 → `output/gridpacks/mumu_lnuqq_Wmass_pt250_10TeV/`
  - `vbfW`: jobid 34825175 → `output/gridpacks/mumu_vbfW_pt500_10TeV/`

## 2026-06-16 16:36:39 — submit.py production
- commit: `da6452583d5ff9c0234cb68371538f17839b7d59` (clean)
- params: `-n 100 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `lnuqq_Wmass_pt250`: 100 jobs (ids 34862645–34862744) → `output/batch/lnuqq_Wmass_pt250/`

## 2026-06-16 16:36:41 — submit.py production
- commit: `da6452583d5ff9c0234cb68371538f17839b7d59` (clean)
- params: `-n 100 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfW_qq_pt500_lhe`: 100 jobs (ids 34862745–34862844) → `output/batch/vbfW_qq_pt500_lhe/`

## 2026-06-16 16:47:11 — submit.py production
- commit: `634be6f8ffe681f91cfef89505300cb93b4dc059` (clean)
- params: `--indices [2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 94, 95, 96] -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_whizard`: 48 jobs (ids 34864082–34864129) → `output/batch/ZH_bbbb_whizard/`

## 2026-06-16 16:48:08 — submit.py production
- commit: `494ebdabe06a05670744527e01ab33e30b2bc851` (clean)
- params: `--indices [29, 43, 59, 61, 65, 66, 67, 68, 70, 71, 81, 82, 83, 85, 86, 87] -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_lhe`: 16 jobs (ids 34864185–34864200) → `output/batch/ZH_bbbb_lhe/`

## 2026-06-16 16:54:04 — make_gridpack.py
- commit: `26cd8094b542b91d75c2e8ef7d4a909a37273e57` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfH`: jobid 34864864 → `output/gridpacks/mumu_vbfH_pt500_10TeV/`

## 2026-06-16 16:55:17 — submit.py production
- commit: `658142c2614dd26a403eceef4e5f74cef6a4a5fa` (clean)
- params: `-n 100 -e 50 --qos avery-b --after 34864864`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfH_bb_pt500_lhe`: 100 jobs (ids 34864943–34865042, afterok:34864864) → `output/batch/vbfH_bb_pt500_lhe/`

## 2026-06-17 17:26:53 — submit.py production
- commit: `e8594adf57de8741756d6e84299b0ccdf260e3c8` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 20 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_pythia`: 20 jobs (ids 35011004–35011023) → `output/batch/ZH_bbbb_pythia/`

## 2026-06-17 19:03:38 — make_gridpack.py
- commit: `cb3724fde5669d27392d3e00f6ce064175dfa275` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfW`: jobid 35021768 → `output/gridpacks/mumu_vbfW_pt500_10TeV/`

## 2026-06-17 19:09:03 — submit.py production
- commit: `cb3724fde5669d27392d3e00f6ce064175dfa275` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfW_qq_pt500_lhe`: 100 jobs (ids 35022139–35022238) → `output/batch/vbfW_qq_pt500_lhe/`

## 2026-06-30 — Whizard cut-syntax bug (Pt/Eta comma vs colon): samples carry the wrong fiducial cut → flagged for regen
**No jobs submitted here — this is a bookkeeping entry.** NOTE: this bug does **not** invalidate
any study *conclusion* — the authors confirmed the findings, and the cut is a
selection/efficiency effect. Only the event *samples* carry the wrong fiducial region.

The Whizard authors confirmed a cut-syntax bug in our cards (manual §5.2.6): for `Pt` and
`Eta`, a **comma** `[a, b]` gives the observable of the *combined a+b system*, while a
**colon** `[a:b]` gives it *per particle*. Our per-particle acceptance cuts used the comma
form, so e.g. `all Pt > 250 GeV [any_q, any_Q]` cut on the qq̄-system pT (≈ Z pT) instead of
each jet's pT. Authors confirmed this shifts selection efficiency by **up to an order of
magnitude** (it does NOT cause the BR bias or the ZH colour-reconnection shoulder — those are
separate, genuine Whizard issues they are fixing). Invariant-mass (`M`) cuts and single-particle
brackets (`[Z]`,`[H]`,`[Wpm]`) were always correct. Full write-up:
`studies/generators_validation_conejets/RESULTS.md` → "Whizard author correspondence & cut-syntax bug".

- **Card fix applied** in `cards/` (34 files, production + gridpack): every `Pt`/`Eta` comma
  bracket → colon; all `M` cuts left as comma. **UNCOMMITTED in mucoll-slurm at time of writing**
  — commit before regenerating so the SHA below can be filled in.
- **Frozen buggy cards** (as sent to the authors):
  `studies/generators_validation_conejets/whizard_report_cards_buggy/` (README carries a warning).

**Tier A — samples selected with the buggy cut → regenerate for the intended fiducial region**
(the study *conclusions* still hold; this is about the acceptance, not the verdict). Two sub-cases:
- `*_pt250` samples: the cut change is *real* — it was cutting on the qq̄/system pT, so the
  intended "each jet pT > 250 GeV" boosted region was never actually applied. Regenerate.
- `ZH_bbbb_*`: the `[Z, H]` η cut was essentially *inert* (back-to-back ZH ⇒ system η ≈ 0, cut
  passes everything), so these are valid full-acceptance samples and the CR conclusion is
  unaffected. Regenerate only to impose the correct per-boson |η|<2.3 fiducial cut.

Existing output renamed with suffix `.BUGGY_CUT_20260630`:
  - batch: `nunuqq_Zmass_pt250`, `nunubb_Hmass_pt250`, `lnuqq_Wmass_pt250`,
    `ZH_bbbb_lhe`, `ZH_bbbb_pythia`, `ZH_bbbb_whizard`
  - gridpacks: `mumu_nunuqq_Zmass_pt250_10TeV`, `mumu_nunubb_Hmass_pt250_10TeV`,
    `mumu_lnuqq_Wmass_pt250_10TeV`, `mumu_ZH_bbbb_lhe_10TeV`, `mumu_ZH_bbbb_whizard_10TeV`
  - Regen order: `make_gridpack.py nunuqq_Zmass_pt250 nunubb_Hmass_pt250 lnuqq_Wmass_pt250 ZH_bbbb_lhe ZH_bbbb_whizard`
    then resubmit dependents (`nunuqq_Zmass_pt250`; `nunubb_Hmass_pt250`; `lnuqq_Wmass_pt250`;
    `ZH_bbbb_lhe`+`ZH_bbbb_pythia` share the `ZH_bbbb_lhe` gridpack; `ZH_bbbb_whizard`
    integrates inline). Sanity-check the new integrated σ (the `*_pt250` σ should drop
    ~an order of magnitude) before trusting the reruns.

**Tier B — change is only the soft `Pt>5 [tag]` cut (boson `Pt`/`η` used single-particle
brackets, never buggy): STILL VALID, NOT renamed, no regen needed.**
  - batch (kept): `vbfZ_qq_pt500_{lhe,pythia,whizard}`, `vbfW_qq_pt500_lhe`, `vbfH_bb_pt500_lhe`
  - gridpacks (kept): `mumu_vbfZ_pt500_10TeV`, `mumu_vbfW_pt500_10TeV`, `mumu_vbfH_pt500_10TeV`

**Unaffected** (no cards / cuts): `pgun`, `pythia_ZH`, `WW_qqqq_whizardNoCR`.

## 2026-06-30 21:20:28 — make_gridpack.py
- commit: `d27115704003749cbdf2d6f93c2113cd72d4144f` (clean)
- gridpacks:
  - `ZH_bbbb_lhe`: jobid 36117414 → `output/gridpacks/mumu_ZH_bbbb_lhe_10TeV/`

## 2026-06-30 21:23:06 — submit.py production
- commit: `d27115704003749cbdf2d6f93c2113cd72d4144f` (clean)
- params: `-n 100 -e 50 --qos avery-b --after 36117414`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_lhe`: 100 jobs (ids 36117482–36117581, afterok:36117414) → `output/batch/ZH_bbbb_lhe/`

## 2026-08-18 09:35:31 — submit.py production
- commit: `5c82a566fe27962343af6188c68bcda2b787e294` (clean)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `vbfZ_qq_pt500_lhe_v3p1`: 100 jobs (ids 39612869–39612983) → `output/batch/vbfZ_qq_pt500_lhe_v3p1/`
  - `vbfW_qq_pt500_lhe_v3p1`: 100 jobs (ids 39612984–39613086) → `output/batch/vbfW_qq_pt500_lhe_v3p1/`
  - `vbfH_bb_pt500_lhe_v3p1`: 100 jobs (ids 39613087–39613192) → `output/batch/vbfH_bb_pt500_lhe_v3p1/`

## 2026-08-18 09:35:51 — submit.py production
- commit: `5c82a566fe27962343af6188c68bcda2b787e294` (clean)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b`  (output base `/blue/avery/m.mazza/projects/muoncollider/output/batch`)
- production:
  - `ZH_bbbb_lhe_v3p1`: 100 jobs (ids 39613195–39613299) → `output/batch/ZH_bbbb_lhe_v3p1/`

## 2026-08-18 — MAIA v3.1 pre-flight for the LHE production (bookkeeping, no jobs)
**No jobs submitted here** — this records the checks made before the two `v3p1` submissions
above, and two findings worth carrying forward.

**Environment verified.** Image `mucoll-sim-ubuntu24:v3.1-amd64` (CVMFS, stack `2026-08-13`,
Whizard 3.1.5, Pythia 8.315); `mucoll-benchmarks-v3.1` at `ce72cf0` with submodules identical
to the tutorial's pinned checkout (`tutorial_aug2026/mucoll-benchmarks`). GEN was exercised
through the real `gen/whizard_lhe.sh` path for all four LHE samples — all wrote HepMC.

**Action required on every image bump: rebuild `pythia/`.** `LheToHepMC` (built 2026-06-15
against the v3.0 stack) carries spack RPATHs to hashes that do not exist in v3.1 and dies with
`libpythia8.so: cannot open shared object file`. Every LHE job would have failed at GEN.
Fixed by rerunning `bash pythia/build.sh` inside the v3.1 container (clean build).

**σ verification — v3.1 changes nothing in the matrix element.** Re-running the vbfW LHE card
with only the pre-fix comma cut restored (`Pt > 5 [lTag, nuTag]`) under v3.1 reproduces the
June value **exactly**: `5.2682077E+02 +- 3.42E-01 fb` (identical digits — same seed 1234,
same integration spec, deterministic TAO RNG). So the −29 % between the June samples and the
new ones (526.82 → 371.92 fb) is entirely the 2026-06-30 comma→colon cut fix, and is
*intended*: vbfW's tag lepton comes from photon exchange, so its pT peaks near zero and a
genuine per-particle 5 GeV cut bites hard. vbfZ/vbfH tag on W-exchange neutrinos and moved
only +0.06 % / −0.5 %; ZH reuses its (post-fix) gridpack and is bit-identical.

| sample | June (v3.0) | 2026-08 (v3.1) | Δ |
|---|---|---|---|
| `ZH_bbbb_lhe` | 0.12299007 fb | 0.12299007 fb | 0 (grid reused) |
| `vbfZ_qq_pt500_lhe` | 223.68 ± 0.30 fb | 223.82 ± 0.30 fb | +0.06 % |
| `vbfH_bb_pt500_lhe` | 20.337 ± 0.040 fb | 20.232 ± 0.039 fb | −0.5 % |
| `vbfW_qq_pt500_lhe` | 526.82 ± 0.34 fb | 371.92 ± 0.22 fb | −29 % (cut fix, verified) |

**Open: the three vbf gridpacks are stale.** The 2026-06-30 cut fix edited
`cards/gridpack/mumu_vbf{Z,W,H}_pt500_10TeV.gridpack.sin`, but only `ZH_bbbb_lhe` was
regenerated. VAMP therefore rejects the vbf grids (`parameter mismatch, discarding grid file`)
and every vbf job re-integrates inline — correct physics and correct unweighting, but ~25–385 s
of extra CPU per job and ~0.1–0.2 % σ scatter between jobs. To fix for future productions:
`python make_gridpack.py vbfZ vbfW vbfH` (24 h / 32 CPU each), then submit with `--after`.

**Note: job scratch falls back to `/tmp` on HPG.** `lib/stages.sh::setup_workdir` prefers
`/scratch/local/$SLURM_JOB_ID`, but HiPerGator does not provision per-job local scratch
(`GresTypes = gpu` only — there is no `scratch` GRES), so `mkdir` fails and every job warns
into its `.err` and uses `/tmp`. That is benign here: `/tmp` on these nodes is a 1.7 TB
node-local RAID (`/dev/md2`) at ~1 % use, with ≤10 of our jobs per node (~9 GB each), so the
shared-`/tmp` ENOSPC that once corrupted SIM output is not a risk at this scale.

## 2026-08-18 10:55:18 — make_gridpack.py
- commit: `5c82a566fe27962343af6188c68bcda2b787e294` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfZ`: jobid 39617072 → `output/gridpacks/mumu_vbfZ_pt500_10TeV/`
  - `vbfW`: jobid 39617073 → `output/gridpacks/mumu_vbfW_pt500_10TeV/`
  - `vbfH`: jobid 39617074 → `output/gridpacks/mumu_vbfH_pt500_10TeV/`

## 2026-08-18 11:20:59 — submit.py production
- commit: `5a476c64dc47b0436a4be459d53775045d5095c1` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `ZH_bbbb_lhe_v3p1`: 100 jobs (ids 39618437–39618536) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p1/`

## 2026-08-18 — ZH_bbbb_lhe_v3p1 first attempt CANCELLED (physics-list slowdown)
**Read the two `ZH_bbbb_lhe_v3p1` entries above together:** the 11:35 submission (ids
39618437–39618536, `--time 4-00:00:00`) **supersedes** the 09:35 one (ids 39613195–39613299,
`--time 20:00:00`), which was cancelled ~1 h in. No output was lost — `move_outputs` runs
only after RECO, so those jobs had written nothing.

**Why.** v3.1 SIM runs 4–8× slower than the June production, and ZH would not have fitted in
the 20 h limit (measured 824–1174 s/event → 11–16 h of SIM alone, before RECO). Cause is a
one-line difference in the simulation steering, not a misconfiguration on our side:

```
mucoll-benchmarks      (June): SIM.physics.list = "QGSP_BERT"
mucoll-benchmarks-v3.1 (now):  SIM.physics.list = "FTFP_BERT_HP"
```

`_HP` is high-precision neutron transport (thermal neutrons down to meV), routinely 5–10×
slower in calorimeter-heavy geometries. Measured rates, v3.1 vs June:

| sample | June (QGSP_BERT) | v3.1 (FTFP_BERT_HP) |
|---|---|---|
| vbfH | 38 s/event | 141–312 s/event |
| ZH | 236 s/event | 824–1174 s/event |

**Decision (Maria, 2026-08-18): keep the v3.1 default `FTFP_BERT_HP`** — it is the baseline
we will actually use going forward. The consequence to remember when comparing against the
June samples is that the difference includes the physics list, not only the image and the
config-package move. The 300 vbf jobs already in flight were left to finish (they fit in
10 h); only ZH needed the longer walltime. A walltime cannot be raised on a running job
(`scontrol update TimeLimit` is operator-only), which is why resubmission was the only route.

**Note:** the resubmitted ZH writes to the new default root
`/cmsuf/data/store/user/mmazza/mucoll/samples/`, while the three vbf samples of this
production still land on `/blue` (they were submitted before the default changed) and are
synced across afterwards.

## 2026-08-18 11:47:16 — submit.py production
- commit: `8bb0472a04a83e846412e957544de58959c06a6a` (clean)
- params: `--indices [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82] -e 50 --tag v3p1 --qos avery-b`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `ZH_bbbb_lhe_v3p1`: 83 jobs (ids 39619753–39619835) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p1/`

## 2026-08-18 — v3.1 DIGI/RECO silently truncated to 10 events (found + fixed mid-production)
**The first finished job of this production had 10 events in digi/reco, not 50.** gen 50 →
sim 50 → **digi 10** → reco 10. Cause, in the v3.1 config package:

```
configs/MAIAConfig/MAIAConfig/Common/steering.py:89
def build_application(args, alg_list, input_files, output_file, histo_file, evt_max=10):
```

`digi_steer.py` and `reco_steer.py` call it without `evt_max`, so `ApplicationMgr` got
`EvtMax = 10`. The 1-event pgun test that validated the v3.1 migration could not have
caught it. (Corrected 2026-08-18: this entry first said "the pre-v3.1 benchmarks set
`EvtMax = -1`, so this is new". That is wrong — upstream `mucoll-benchmarks` has had
`EvtMax = 10` throughout its k4run history. It never bit before because our `samf25`
checkout carries a local *uncommitted* edit to `-1`, dated 2026-03-09, which the clean
v3.1 checkout does not inherit.) **Fixed** in `lib/stages.sh` (commit
`8bb0472`) by passing `-n "$NEVENTS"` to both `k4run` calls — verified by re-running digi
over an existing 50-event sim file: 10 events before, 50 after.

**How it surfaced** — worth remembering as a check: RECO ran *12× faster* than June (83 s vs
~1030 s) and its output was *4.6× smaller* (105 MB vs 486 MB), the opposite of what the
slower `FTFP_BERT_HP` list predicts. A stage getting cheaper when the physics got heavier is
a red flag, not good news.

**Effect on this production:**
- `ZH_bbbb_lhe_v3p1` — 83 jobs had started pre-fix and were cancelled ~20 min in and
  resubmitted by index (they had produced nothing; SIM alone is ~13 h). 17 jobs started
  after the fix or were still pending, and were left alone. All 100 now run fixed code:
  jobs read `run_chain.sh`/`lib/stages.sh` from the repo at start time, so a pending job
  picks up a fix with no resubmission.
- `vbf{Z,W,H}_*_v3p1` — 300 jobs were already running with the old code. Their **SIM output
  is correct** (50 events); only digi/reco are truncated. Since SIM is ~1.9 h and digi+reco
  are ~10 min, these are repaired in place with `scripts/redo_digireco.sh` rather than
  regenerated. That script runs both stages in node scratch and only replaces the originals
  after verifying the event count.

## 2026-11-20 15:33:41 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 2 -e 10 --tag smallR_smoke --qos avery-b`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfH_bb_pt0to100_lhe_smallR_smoke`: 2 jobs (ids 52115763–52115764) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt0to100_lhe_smallR_smoke/`
  - `vbfH_bb_pt100to200_lhe_smallR_smoke`: 2 jobs (ids 52115765–52115766) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt100to200_lhe_smallR_smoke/`
  - `vbfH_bb_pt200to300_lhe_smallR_smoke`: 2 jobs (ids 52115767–52115768) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt200to300_lhe_smallR_smoke/`
  - `vbfH_bb_pt300to400_lhe_smallR_smoke`: 2 jobs (ids 52115769–52115770) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt300to400_lhe_smallR_smoke/`
  - `vbfH_bb_pt400to500_lhe_smallR_smoke`: 2 jobs (ids 52115771–52115772) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt400to500_lhe_smallR_smoke/`
  - `vbfZ_qq_pt0to100_lhe_smallR_smoke`: 2 jobs (ids 52115773–52115774) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt0to100_lhe_smallR_smoke/`
  - `vbfZ_qq_pt100to200_lhe_smallR_smoke`: 2 jobs (ids 52115775–52115776) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt100to200_lhe_smallR_smoke/`
  - `vbfZ_qq_pt200to300_lhe_smallR_smoke`: 2 jobs (ids 52115777–52115778) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt200to300_lhe_smallR_smoke/`
  - `vbfZ_qq_pt300to400_lhe_smallR_smoke`: 2 jobs (ids 52115779–52115780) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt300to400_lhe_smallR_smoke/`
  - `vbfZ_qq_pt400to500_lhe_smallR_smoke`: 2 jobs (ids 52115781–52115782) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt400to500_lhe_smallR_smoke/`
  - `vbfW_qq_pt0to100_lhe_smallR_smoke`: 2 jobs (ids 52115783–52115784) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt0to100_lhe_smallR_smoke/`
  - `vbfW_qq_pt100to200_lhe_smallR_smoke`: 2 jobs (ids 52115785–52115786) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt100to200_lhe_smallR_smoke/`
  - `vbfW_qq_pt200to300_lhe_smallR_smoke`: 2 jobs (ids 52115787–52115788) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt200to300_lhe_smallR_smoke/`
  - `vbfW_qq_pt300to400_lhe_smallR_smoke`: 2 jobs (ids 52115789–52115790) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt300to400_lhe_smallR_smoke/`
  - `vbfW_qq_pt400to500_lhe_smallR_smoke`: 2 jobs (ids 52115791–52115792) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt400to500_lhe_smallR_smoke/`

## 2026-11-20 15:33:49 — make_gridpack.py
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfH_pt0to100`: jobid 52115795 → `output/gridpacks/mumu_vbfH_pt0to100_10TeV/`
  - `vbfH_pt100to200`: jobid 52115796 → `output/gridpacks/mumu_vbfH_pt100to200_10TeV/`
  - `vbfH_pt200to300`: jobid 52115797 → `output/gridpacks/mumu_vbfH_pt200to300_10TeV/`
  - `vbfH_pt300to400`: jobid 52115798 → `output/gridpacks/mumu_vbfH_pt300to400_10TeV/`
  - `vbfH_pt400to500`: jobid 52115799 → `output/gridpacks/mumu_vbfH_pt400to500_10TeV/`
  - `vbfZ_pt0to100`: jobid 52115800 → `output/gridpacks/mumu_vbfZ_pt0to100_10TeV/`
  - `vbfZ_pt100to200`: jobid 52115801 → `output/gridpacks/mumu_vbfZ_pt100to200_10TeV/`
  - `vbfZ_pt200to300`: jobid 52115802 → `output/gridpacks/mumu_vbfZ_pt200to300_10TeV/`
  - `vbfZ_pt300to400`: jobid 52115803 → `output/gridpacks/mumu_vbfZ_pt300to400_10TeV/`
  - `vbfZ_pt400to500`: jobid 52115804 → `output/gridpacks/mumu_vbfZ_pt400to500_10TeV/`
  - `vbfW_pt0to100`: jobid 52115805 → `output/gridpacks/mumu_vbfW_pt0to100_10TeV/`
  - `vbfW_pt100to200`: jobid 52115806 → `output/gridpacks/mumu_vbfW_pt100to200_10TeV/`
  - `vbfW_pt200to300`: jobid 52115807 → `output/gridpacks/mumu_vbfW_pt200to300_10TeV/`
  - `vbfW_pt300to400`: jobid 52115808 → `output/gridpacks/mumu_vbfW_pt300to400_10TeV/`
  - `vbfW_pt400to500`: jobid 52115809 → `output/gridpacks/mumu_vbfW_pt400to500_10TeV/`

## 2026-11-20 16:09:03 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 2 -e 10 --tag smallR_smoke2 --qos avery-b`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfH_bb_pt0to100_lhe_smallR_smoke2`: 2 jobs (ids 52120263–52120264) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt0to100_lhe_smallR_smoke2/`
  - `vbfH_bb_pt100to200_lhe_smallR_smoke2`: 2 jobs (ids 52120265–52120266) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt100to200_lhe_smallR_smoke2/`
  - `vbfH_bb_pt200to300_lhe_smallR_smoke2`: 2 jobs (ids 52120267–52120268) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt200to300_lhe_smallR_smoke2/`
  - `vbfH_bb_pt300to400_lhe_smallR_smoke2`: 2 jobs (ids 52120269–52120270) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt300to400_lhe_smallR_smoke2/`
  - `vbfH_bb_pt400to500_lhe_smallR_smoke2`: 2 jobs (ids 52120271–52120272) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt400to500_lhe_smallR_smoke2/`

## 2026-11-20 16:21:33 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115800`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfZ_qq_pt0to100_lhe_v3p1`: 100 jobs (ids 52121600–52121701, afterok:52115800) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt0to100_lhe_v3p1/`

## 2026-11-20 16:21:39 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115801`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfZ_qq_pt100to200_lhe_v3p1`: 100 jobs (ids 52121702–52121813, afterok:52115801) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt100to200_lhe_v3p1/`

## 2026-11-20 16:21:48 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115802`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfZ_qq_pt200to300_lhe_v3p1`: 100 jobs (ids 52121814–52121917, afterok:52115802) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt200to300_lhe_v3p1/`

## 2026-11-20 16:21:57 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115803`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfZ_qq_pt300to400_lhe_v3p1`: 100 jobs (ids 52121918–52122027, afterok:52115803) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt300to400_lhe_v3p1/`

## 2026-11-20 16:22:05 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115804`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfZ_qq_pt400to500_lhe_v3p1`: 100 jobs (ids 52122028–52122128, afterok:52115804) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt400to500_lhe_v3p1/`

## 2026-11-20 16:22:14 — make_gridpack.py
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- gridpacks:
  - `vbfH_pt0to100`: jobid 52122131 → `output/gridpacks/mumu_vbfH_pt0to100_10TeV/`
  - `vbfH_pt100to200`: jobid 52122132 → `output/gridpacks/mumu_vbfH_pt100to200_10TeV/`
  - `vbfH_pt200to300`: jobid 52122133 → `output/gridpacks/mumu_vbfH_pt200to300_10TeV/`
  - `vbfH_pt300to400`: jobid 52122134 → `output/gridpacks/mumu_vbfH_pt300to400_10TeV/`
  - `vbfH_pt400to500`: jobid 52122135 → `output/gridpacks/mumu_vbfH_pt400to500_10TeV/`

## 2026-11-20 16:35:17 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 1 -e 2 --tag v3p2_validate --qos avery`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `pgun_v3p2_validate`: 1 jobs (ids 52123448–52123448) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/pgun_v3p2_validate/`

## 2026-11-20 16:41:24 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115805`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfW_qq_pt0to100_lhe_v3p1`: 100 jobs (ids 52124158–52124265, afterok:52115805) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt0to100_lhe_v3p1/`

## 2026-11-20 16:41:32 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115806`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfW_qq_pt100to200_lhe_v3p1`: 100 jobs (ids 52124272–52124372, afterok:52115806) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt100to200_lhe_v3p1/`

## 2026-11-20 16:41:41 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115807`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfW_qq_pt200to300_lhe_v3p1`: 100 jobs (ids 52124373–52124477, afterok:52115807) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt200to300_lhe_v3p1/`

## 2026-11-20 16:41:47 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115808`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfW_qq_pt300to400_lhe_v3p1`: 100 jobs (ids 52124478–52124578, afterok:52115808) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt300to400_lhe_v3p1/`

## 2026-11-20 16:41:56 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b --after 52115809`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfW_qq_pt400to500_lhe_v3p1`: 100 jobs (ids 52124579–52124679, afterok:52115809) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt400to500_lhe_v3p1/`

## 2026-11-20 16:50:12 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 0 -e 5 --first-event 0 --events-per-job 5 --split --mem 16G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib0_bench`: array 52125528 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib0_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib0_bench`: array 52125529 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib0_bench/`

## 2026-11-20 16:50:12 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 167 -e 5 --first-event 0 --events-per-job 5 --split --mem 32G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib167_bench`: array 52125530 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib167_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib167_bench`: array 52125531 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib167_bench/`

## 2026-11-20 16:50:13 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 833 -e 5 --first-event 0 --events-per-job 5 --split --mem 64G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib833_bench`: array 52125532 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib833_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib833_bench`: array 52125536 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib833_bench/`

## 2026-11-20 16:50:13 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 5 --first-event 0 --events-per-job 5 --split --mem 96G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_bench`: array 52125540 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_bench`: array 52125541 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_bench/`

## 2026-11-20 16:50:15 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 5 --first-event 0 --events-per-job 5 --split --calo-coning --mem 96G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc_bench`: array 52125542 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_cc_bench`: array 52125543 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_cc_bench/`

## 2026-11-20 16:50:15 — submit_bib.py BIB digi+reco
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 5 --first-event 0 --events-per-job 5 --split --calo-coning --tracker-coning --mem 96G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc_tc_bench`: array 52125544 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc_tc_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_cc_tc_bench`: array 52125545 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_cc_tc_bench/`

## 2026-11-20 17:53:41 — submit_bib.py BIB digi+reco
- commit: `f6e467f056dc4b112f0030f8c5368f5bb0e78a19` (clean)
- params: `--bib 167 -e 5 --first-event 0 --events-per-job 5 --split --mem 16G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib167_bench`: array 52132302 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib167_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib167_bench`: array 52132303 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib167_bench/`

## 2026-11-20 18:07:44 — submit.py production
- commit: `70e386d0385ff50c63f57c4fedc89a96231ed824` (DIRTY — SHA does NOT capture the exact code)
- params: `-n 100 -e 50 --tag v3p1 --qos avery-b`  (output base `/cmsuf/data/store/user/mmazza/mucoll/samples`)
- production:
  - `vbfH_bb_pt0to100_lhe_v3p1`: 100 jobs (ids 52133348–52133461) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt0to100_lhe_v3p1/`
  - `vbfH_bb_pt100to200_lhe_v3p1`: 100 jobs (ids 52133462–52133561) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt100to200_lhe_v3p1/`
  - `vbfH_bb_pt200to300_lhe_v3p1`: 100 jobs (ids 52133562–52133661) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt200to300_lhe_v3p1/`
  - `vbfH_bb_pt300to400_lhe_v3p1`: 100 jobs (ids 52133662–52133761) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt300to400_lhe_v3p1/`
  - `vbfH_bb_pt400to500_lhe_v3p1`: 100 jobs (ids 52133762–52133861) → `../../../../../cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt400to500_lhe_v3p1/`

## 2026-11-21 09:48:19 — submit_bib.py BIB digi+reco
- commit: `f6e467f056dc4b112f0030f8c5368f5bb0e78a19` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 5 --first-event 0 --events-per-job 5 --split --calo-coning --mem 48G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc_bench`: array 52220570 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_cc_bench`: array 52220571 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_cc_bench/`

## 2026-11-21 09:48:19 — submit_bib.py BIB digi+reco
- commit: `f6e467f056dc4b112f0030f8c5368f5bb0e78a19` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 5 --first-event 0 --events-per-job 5 --split --calo-coning --tracker-coning --mem 48G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc_tc_bench`: array 52220572 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc_tc_bench/`
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_cc_tc_bench`: array 52220573 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_cc_tc_bench/`

## 2026-11-21 20:56:07 — submit_bib.py BIB digi+reco
- commit: `3ec2fa37ea81941aac0e0d3a01b7aca910c1ac73` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 2 --first-event 0 --events-per-job 2 --calo-coning --mem 40G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52279642 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-21 20:56:12 — submit_bib.py BIB digi+reco
- commit: `3ec2fa37ea81941aac0e0d3a01b7aca910c1ac73` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 998 --first-event 2 --events-per-job 2 --calo-coning --mem 40G --cpus 4 --throttle 50 --dependency afterok:52279642`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52279644 (499 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-21 20:56:12 — submit_bib.py BIB digi+reco
- commit: `3ec2fa37ea81941aac0e0d3a01b7aca910c1ac73` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 0 -e 1000 --first-event 0 --events-per-job 50 --calo-coning --mem 8G --cpus 4`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib0_cc`: array 52279645 (20 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib0_cc/`

## 2026-11-22 09:32:21 — submit_bib.py BIB digi+reco
- commit: `3ec2fa37ea81941aac0e0d3a01b7aca910c1ac73` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 200 --first-event 800 --events-per-job 2 --calo-coning --mem 30G --cpus 4 --throttle 50`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52339735 (100 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 09:53:46 — submit_bib.py BIB digi+reco
- commit: `3ec2fa37ea81941aac0e0d3a01b7aca910c1ac73` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 544 --first-event 256 --events-per-job 2 --calo-coning --mem 30G --cpus 2 --throttle 200`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52341183 (272 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 09:55 — ZH 100 % BIB (cc): queue moves, no events duplicated
- Array 52279644 now covers only events 2..255 (tasks 0..126). Its tasks 399..498 (events
  800..999) were cancelled before starting and resubmitted on the `avery` QOS as 52339735.
  Its tasks 127..398 (events 256..799) were cancelled before starting and resubmitted with
  2 CPUs as 52341183, because only tracking is multithreaded (36 % CPU efficiency at 4 CPUs).
- Pending memory lowered 40G → 30G (peak RSS 15.9–18.5 GB on the first 59 tasks).
- A monitor job (`output/bib_debug/bib_rebalance.sh`, not in the repo) moves further pending
  tasks of 52341183 to `avery` whenever fewer than 50 of ours are there. Each move appends its
  own `submit_bib.py` entry here.
- 100 % BIB *without* coning, first event of RECO alone: ZH 23.7 h, vbfH 25.0 h (both jobs
  cancelled afterwards). With calorimeter coning the ZH production averages ~0.65 h/event.

## 2026-11-22 11:01:16 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 10 -e 1 --first-event 50 --events-per-job 1 --split --keep-digi --tagveto-coning --mem 8G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345328 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val/`
  - `vbfH_bb_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345329 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib10_ccnt_val/`
  - `ZH_bbbb_lhe_v3p2_bib10_ccnt_val`: array 52345330 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib10_ccnt_val/`

## 2026-11-22 11:01:17 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 10 -e 1 --first-event 53 --events-per-job 1 --split --keep-digi --tagveto-coning --mem 8G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345331 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val/`

## 2026-11-22 11:02:54 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 10 -e 1 --first-event 50 --events-per-job 1 --split --keep-digi --tagveto-coning --mem 8G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345504 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val/`
  - `vbfH_bb_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345505 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib10_ccnt_val/`
  - `ZH_bbbb_lhe_v3p2_bib10_ccnt_val`: array 52345506 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib10_ccnt_val/`

## 2026-11-22 11:02:54 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 10 -e 1 --first-event 53 --events-per-job 1 --split --keep-digi --tagveto-coning --mem 8G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val`: array 52345509 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib10_ccnt_val/`

## 2026-11-22 11:11:55 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 1 --first-event 100 --events-per-job 1 --tagveto-coning --mem 30G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_ccnt_bench`: array 52346016 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_ccnt_bench/`
  - `vbfW_qq_pt500_lhe_v3p2_bib1666_ccnt_bench`: array 52346017 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib1666_ccnt_bench/`
  - `vbfZ_qq_pt500_lhe_v3p2_bib1666_ccnt_bench`: array 52346018 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt500_lhe_v3p2_bib1666_ccnt_bench/`
  - `vbfZ_qq_pt0to100_lhe_v3p2_bib1666_ccnt_bench`: array 52346019 (1 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt0to100_lhe_v3p2_bib1666_ccnt_bench/`

## 2026-11-22 11:14:51 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 100 --first-event 156 --events-per-job 2 --calo-coning --mem 30G --cpus 2 --throttle 200`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52346217 (50 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 11:20 — ZH 100 % BIB (cc): last 4-CPU tasks moved to 2 CPUs
- Array 52279644 now covers only events 2..155 (tasks 0..76). Its tasks 77..126 (events
  156..255) were cancelled before starting — still queued after >1 h while the 2-CPU tasks
  behind them ran — and resubmitted with 2 CPUs as 52346217.
- 2-CPU tasks (52341183, first 22 done): median 50 min, max 74 min, peak RSS 18.5 GB, CPU
  efficiency 66 % (34 % at 4 CPUs); no failures.

## 2026-11-22 12:35:13 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 18 --first-event 782 --events-per-job 2 --calo-coning --mem 30G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52352764 (9 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 12:55:16 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 18 --first-event 764 --events-per-job 2 --calo-coning --mem 30G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52354342 (9 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 13:17:09 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 1666 -e 1000 --first-event 0 --events-per-job 2 --tagveto-coning --mem 24G --cpus 2 --throttle 150`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfH_bb_pt500_lhe_v3p2_bib1666_ccnt`: array 52355931 (500 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib1666_ccnt/`
  - `vbfW_qq_pt500_lhe_v3p2_bib1666_ccnt`: array 52355932 (500 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib1666_ccnt/`
  - `vbfZ_qq_pt500_lhe_v3p2_bib1666_ccnt`: array 52355933 (500 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt500_lhe_v3p2_bib1666_ccnt/`

## 2026-11-22 13:17:09 — submit_bib.py BIB digi+reco
- commit: `3df2b60c441ebb25b303b1d229452791a7a15f97` (DIRTY — SHA does NOT capture the exact code)
- params: `--bib 0 -e 1000 --first-event 0 --events-per-job 50 --tagveto-coning --mem 8G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `vbfH_bb_pt500_lhe_v3p2_bib0_ccnt`: array 52355934 (20 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfH_bb_pt500_lhe_v3p2_bib0_ccnt/`
  - `vbfW_qq_pt500_lhe_v3p2_bib0_ccnt`: array 52355935 (20 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfW_qq_pt500_lhe_v3p2_bib0_ccnt/`
  - `vbfZ_qq_pt500_lhe_v3p2_bib0_ccnt`: array 52355936 (20 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/vbfZ_qq_pt500_lhe_v3p2_bib0_ccnt/`

## 2026-11-22 12:40 — provenance of the DIRTY entries above; ZH time limit
- The VBF pt500 `_ccnt` submissions (52355931–36) and the tag-veto `val`/`bench` jobs were
  logged as DIRTY at `3df2b60`. The code they ran (k4ext `HardProcessTagVeto`,
  `steering/*_tagveto.py`, `bib_digireco.sh --tagveto-coning`) is committed unchanged as
  `7669f2e`.
- ZH 100 % BIB arrays 52341183 and 52346217: time limit lowered 24 h → 10 h in place
  (slowest 2-event task so far 5.6 h).

## 2026-11-22 13:25:22 — submit_bib.py BIB digi+reco
- commit: `ad64fc9c6b1e48586e4257d3f02669acc19685d9` (clean)
- params: `--bib 1666 -e 16 --first-event 748 --events-per-job 2 --calo-coning --mem 30G --cpus 2`  (BIB `/blue/avery/share/mucol/bib/BIB_v9`, SIM `v3p1` reused)
- production:
  - `ZH_bbbb_lhe_v3p2_bib1666_cc`: array 52356608 (8 tasks) → `/cmsuf/data/store/user/mmazza/mucoll/samples/ZH_bbbb_lhe_v3p2_bib1666_cc/`

## 2026-11-22 12:50 — tag-veto output suffix renamed `_ccnt` → `_ccnotag`
- `submit_bib.py --tagveto-coning` now writes `<KEY>_v3p2_bib<N>_ccnotag[_<tag>]/`. Every
  `_ccnt` path in the entries above now lives under the `_ccnotag` name.
- Arrays 52355931–36 and the bench/val jobs were submitted with `_ccnt`: their task tables
  (`logs/bib_*_ccnt_*.tasks`, file names unchanged) were rewritten to `_ccnotag` before most
  tasks started. The tasks already running at the change read the old path, so
  `<KEY>_..._ccnt` is a symlink to `<KEY>_..._ccnotag` until they finish; then the symlinks
  are removed. Finished bench/val dirs were renamed. SLURM job and log names keep `_ccnt`.

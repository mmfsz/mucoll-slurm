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

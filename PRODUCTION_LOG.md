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

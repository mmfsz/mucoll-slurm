# Production log

Auto-appended by `submit.py` and `make_gridpack.py`. Each entry pins the git commit
that generated the jobs, their SLURM ids, and their output directories — so you can
`git checkout <sha>` to recover the exact code. Output dirs are relative to the
`muoncollider/` parent (`output/gridpacks/<gp>/`, `output/batch/<sample>/`).

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

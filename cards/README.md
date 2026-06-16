# Whizard cards

Git-tracked, authored-here Whizard steering cards. This is the **source of truth**
for our cards; `run_chain.sh` resolves a card from `cards/production/` first and
falls back to `mucoll-benchmarks/generation/signal/whizard/` only if not found here.

- `production/` — full cards (ME + Pythia8 shower/decay) used by jobs.
- `gridpack/` — integration-only counterparts (`*.gridpack.sin`) used by
  `make_gridpack.py` to pre-compute VAMP grids. One gridpack serves every decayer
  variant of a process (shared matrix element); only the inclusive ME variants and
  each fusion process get their own.

Legacy originals are frozen under `../archive/cards/` (`benchmarks/` snapshot +
`whizard_repo/` the old in-repo cards). Rebuild this tree with
`bash scripts/migrate_cards.sh`.

## Naming convention

Two card shapes, because two physically different kinds of sample exist:

**Resonant** — a real boson is in the matrix element and gets decayed:
```
mumu_<PROCESS>_<FINALSTATE>_[<REGION>_]<DECAYER>_<ENERGY>.sin
```
**Inclusive** — no resonance in the ME; named by the literal final state:
```
mumu_<FINALSTATE>[_<REGION>]_<ENERGY>.sin
```

| Slot | Values | Meaning |
|------|--------|---------|
| PROCESS | `ZH` `vbfH` `vbfZ` `vbfW` `WW` | hard process / production mechanism |
| FINALSTATE | `bbbb` `bb` `qq` `qqqq` `incl` · `nunubb` `nunuqq` `lnuqq` `mumuqq` | decay products (resonant) / full final state (inclusive). `incl` = boson left to decay with default branching ratios |
| DECAYER | `whizard` `pythia` `pythiaNoCR` `pythiaSKI` `lhe` | who decays the boson, and how |
| REGION | `pt500` · `Hmass`/`Zmass`/`Wmass` `pt250` | defining kinematic selection (see cut table) |
| ENERGY | `10TeV` | CoM energy |

DECAYER detail: `whizard` = Whizard `unstable` decay; `pythia` = boson left stable
in Whizard, decayed by Pythia8 (channel forced via `$ps_PYTHIA8_config`);
`pythiaNoCR`/`pythiaSKI` = pythia + a colour-reconnection variant (off / SK-I mode 3);
`lhe` = Whizard writes parton-level LHE, `pythia/LheToHepMC` showers+decays.

### LHE-route decay directive (`# LHE_DECAY:`)

For `lhe` cards, Whizard does no showering, so the boson decay channel cannot be
set via `$ps_PYTHIA8_config`. Instead the card carries a comment directive:

```
# LHE_DECAY: 23:mayDecay = on; 23:onMode = off; 23:onIfAny = 1 2 3 4 5
```

`gen/whizard_lhe.sh` greps this line and passes its value as a 5th argument to
`pythia/LheToHepMC`, which applies each `;`-separated token via `readString`.
**If the directive is absent**, `LheToHepMC` falls back to its hardcoded ZH
default (Z→bb, H→bb) — so `mumu_ZH_bbbb_lhe` deliberately has no directive,
while `mumu_vbfZ_qq_pt500_lhe` carries the Z→all-hadronic directive above.

## Cut table (every production card)

| Card | process (ME) | boson/jet pT | mass window | tag / other |
|------|--------------|--------------|-------------|-------------|
| `mumu_ZH_bbbb_whizard` | `e2 E2 => Z H`, Z→bb H→bb (Whizard) | — | — | \|η(Z,H)\|<2.3 |
| `mumu_ZH_bbbb_pythia` | `e2 E2 => Z H`, Pythia Z→bb H→bb | — | — | \|η\|<2.3 |
| `mumu_ZH_bbbb_pythiaNoCR` | as pythia + CR off | — | — | \|η\|<2.3 |
| `mumu_ZH_bbbb_pythiaSKI` | as pythia + CR mode 3 (SK-I) | — | — | \|η\|<2.3 |
| `mumu_ZH_bbbb_lhe` | `e2 E2 => Z H`, decay in LheToHepMC (Z→bb H→bb) | — | — | \|η\|<2.3 |
| `mumu_vbfH_incl_pt500_pythia` | `e2 E2 => νν̄ H`, Pythia default BR | **Pt(H)>500** | — | M(νν̄)>150, Pt(νν̄)>5, \|η(H)\|<2.3 |
| `mumu_vbfH_bb_pt500_whizard` | `e2 E2 => νν̄ H`, Whizard H→bb | **Pt(H)>500** | — | M(νν̄)>150, Pt(νν̄)>5, \|η(H)\|<2.3 |
| `mumu_vbfH_bb_pt500_pythia` | `e2 E2 => νν̄ H`, Pythia H→bb | **Pt(H)>500** | — | M(νν̄)>150, Pt(νν̄)>5, \|η(H)\|<2.3 |
| `mumu_vbfZ_incl_pt500_pythia` | `e2 E2 => νν̄ Z`, Pythia default BR | **Pt(Z)>500** | — | M(νν̄)>150, \|η(Z)\|<2.3 |
| `mumu_vbfZ_qq_pt500_whizard` | `e2 E2 => νν̄ Z`, Whizard Z→qq (uds,c,b) | **Pt(Z)>500** | — | M(νν̄)>150, \|η(Z)\|<2.3 |
| `mumu_vbfZ_qq_pt500_pythia` | `e2 E2 => νν̄ Z`, Pythia Z→qq | **Pt(Z)>500** | — | M(νν̄)>150, \|η(Z)\|<2.3 |
| `mumu_vbfZ_qq_pt500_lhe` | `e2 E2 => νν̄ Z`, decay in LheToHepMC (Z→qq, all hadronic) | **Pt(Z)>500** | — | M(νν̄)>150, \|η(Z)\|<2.3 |
| `mumu_vbfW_incl_pt500_pythia` | `e2 E2 => ℓν W`, Pythia default BR | **Pt(W)>500** | — | M(ℓν tag)>150, \|η(W)\|<2.3 |
| `mumu_vbfW_qq_pt500_whizard` | `e2 E2 => ℓν W`, Whizard W→qq | **Pt(W)>500** | — | M(ℓν tag)>150, \|η(W)\|<2.3 |
| `mumu_vbfW_qq_pt500_pythia` | `e2 E2 => ℓν W`, Pythia W→qq | **Pt(W)>500** | — | M(ℓν tag)>150, \|η(W)\|<2.3 |
| `mumu_vbfW_qq_pt500_lhe` | `e2 E2 => ℓν W`, decay in LheToHepMC (W→qq, all hadronic) | **Pt(W)>500** | — | M(ℓν tag)>150, \|η(W)\|<2.3 |
| `mumu_WW_qqqq_whizardNoCR` | `e2 E2 => W+ W-`, Whizard both→qq, CR off | — | — | \|η(W)\|<2.3 |
| `mumu_bbbb` | `e2 E2 => b B b B` (2→4, no resonance) | — | — | \|η(b)\|<2.3 |
| `mumu_nunubb_Hmass_pt250` | `e2 E2 => νν̄ b B` (2→4) | Pt(b)>250 | **115–135** (H) | M(νν̄)>150, \|η(b)\|<2.3 |
| `mumu_nunuqq_Zmass_pt250` | `e2 E2 => νν̄ q Q` (2→4) | Pt(q)>250 | **80–102** (Z) | M(νν̄)>150, \|η\|<2.3 |
| `mumu_lnuqq_Wmass_pt250` | `e2 E2 => ℓν q Q` (2→4) | Pt(j)>250 | **70–90** (W) | M(ℓν)>150, \|η\|<2.3 |
| `mumu_nunuqq` | `e2 E2 => νν̄ q Q` WW-fusion (broad) | — | — | M(νν̄)>150, Pt(νν̄)>5, \|η(q)\|<2.3 |
| `mumu_mumuqq` | `e2 E2 => μ μ q Q` ZZ-fusion (broad) | — | — | M(μμ)>150, Pt(μμ)>5, \|η(q)\|<2.3 |

**Harmonized acceptance cuts** (applied consistently across the set):
- VBF single-boson cards: tag-pair `M>150`, `Pt>5`, boson `Pt>500`, **and `|η(boson)|<2.3`**.
- ZH cards: `|η(Z,H)|<2.3`.
- Inclusive cards: `|η|<2.3` on the **final-state quarks** (not the neutrino/lepton tags).

Notes:
- `nunuqq` (broad WW-fusion) and `nunuqq_Zmass_pt250` share the same final state;
  the `Zmass`/`pt250` region tags are what distinguish them.
- `nunuqq`/`mumuqq` were inherited (orig. `WWZ_hadrons`/`ZZZ_hadrons`, M. LeBlanc) and
  had never been run — smoke-test before trusting a production.
- VBF boson pT cut is **500 GeV** (older notes said 600).
- **Stale gridpack:** the `bbbb` cut changed (added `|η(b)|<2.3`), so the pre-computed
  `output/gridpacks/mumu_bbbb_10TeV` grids no longer match the card and must be
  regenerated (`python make_gridpack.py bbbb`) before using that gridpack. The
  other pre-computed grids (vbfZ, vbf*_inclusive) are unaffected — those cards were not
  changed.

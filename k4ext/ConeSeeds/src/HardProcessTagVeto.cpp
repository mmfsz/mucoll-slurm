/*
 * HardProcessTagVeto — cone seeds for calorimeter truth-coning without the VBF tags.
 *
 * k4Reco CaloHitConeFilter keeps the calorimeter hits within a cone of every
 * generatorStatus == 1 MCParticle. In VBF samples that includes the TeV-scale tag
 * neutrinos and muons a few degrees from the beam, whose cones keep only beam-induced
 * background. This algorithm writes the stable generator particles minus those tags, as a
 * subset collection to be used as the coner's MCParticleCollectionName.
 *
 * A stable particle is vetoed when it is a muon or a neutrino (|PDG| in VetoPDGs) AND it is
 * either produced at the hard vertex (a daughter of an IncomingStatus particle, i.e. of the
 * incoming beams) without being a boson, or a generator-level descendant of such a
 * particle — the latter catches a tag muon that radiated in Pythia, whose final copy is no
 * longer a direct hard-vertex product. The boson's decay chain is never walked, so a broken
 * link in it cannot drop a decay product; a missed tag only leaves one extra cone.
 *
 * An event without an IncomingStatus particle keeps every stable particle (the default
 * coning) and is counted, so a record with another layout is never silently mis-coned.
 */
#include "Gaudi/Property.h"
#include "k4FWCore/Transformer.h"

#include "edm4hep/MCParticleCollection.h"

#include <algorithm>
#include <atomic>
#include <cstdlib>
#include <string>
#include <vector>

struct HardProcessTagVeto final
    : k4FWCore::Transformer<edm4hep::MCParticleCollection(const edm4hep::MCParticleCollection&)> {

  HardProcessTagVeto(const std::string& name, ISvcLocator* svcLoc)
      : Transformer(name, svcLoc, {KeyValues("InputMCParticles", {"MCParticles"})},
                    {KeyValues("OutputMCParticles", {"ConeSeedMCParticles"})}) {}

  edm4hep::MCParticleCollection operator()(const edm4hep::MCParticleCollection& input) const override {
    auto in = [](const std::vector<int>& v, int pdg) { return std::find(v.begin(), v.end(), std::abs(pdg)) != v.end(); };

    // Hard-vertex products that are not bosons, then their generator-level descendants
    // (Geant4 secondaries have generatorStatus 0 and are not followed).
    std::vector<char> tag(input.size(), 0);
    std::vector<edm4hep::MCParticle> stack;
    bool hasIncoming = false;
    for (const auto& p : input) {
      if (p.getGeneratorStatus() == m_incomingStatus) {
        hasIncoming = true;
        continue;
      }
      if (in(m_bosonPDGs, p.getPDG()))
        continue;
      for (const auto& parent : p.getParents())
        if (parent.getGeneratorStatus() == m_incomingStatus) {
          tag[p.getObjectID().index] = 1;
          stack.push_back(p);
          break;
        }
    }
    while (!stack.empty()) {
      const auto p = stack.back();
      stack.pop_back();
      for (const auto& d : p.getDaughters()) {
        if (d.getGeneratorStatus() == 0 || d.isCreatedInSimulation())
          continue;
        if (auto& t = tag[d.getObjectID().index]; !t) {
          t = 1;
          stack.push_back(d);
        }
      }
    }
    if (!hasIncoming) {
      ++m_nNoHardVertex;
      warning() << "no particle with generatorStatus " << m_incomingStatus.value()
                << "; coning around every stable generator particle" << endmsg;
    }

    auto out = edm4hep::MCParticleCollection();
    out.setSubsetCollection();
    std::size_t nStable = 0, nVeto = 0;
    for (const auto& p : input) {
      if (p.getGeneratorStatus() != 1 || p.isCreatedInSimulation())
        continue;
      ++nStable;
      if (hasIncoming && tag[p.getObjectID().index] && in(m_vetoPDGs, p.getPDG())) {
        ++nVeto;
        continue;
      }
      out.push_back(p);
    }
    m_nVetoed += nVeto;
    debug() << "vetoed " << nVeto << " of " << nStable << " stable generator particles as hard-process tags" << endmsg;
    return out;
  }

  StatusCode finalize() override {
    info() << "hard-process tags vetoed: " << m_nVetoed.load()
           << "; events without a hard vertex (all stable particles kept): " << m_nNoHardVertex.load() << endmsg;
    return Transformer::finalize();
  }

private:
  Gaudi::Property<std::vector<int>> m_vetoPDGs{this, "VetoPDGs", {12, 13, 14, 16},
                                               "|PDG| of the hard-process tags to veto (muons, neutrinos)"};
  Gaudi::Property<std::vector<int>> m_bosonPDGs{this, "BosonPDGs", {23, 24, 25},
                                                "|PDG| of hard-vertex products that are never tags"};
  Gaudi::Property<int> m_incomingStatus{this, "IncomingStatus", 21,
                                        "generatorStatus of the incoming hard-process particles (Pythia 21)"};
  mutable std::atomic<std::size_t> m_nVetoed{0};
  mutable std::atomic<std::size_t> m_nNoHardVertex{0};
};

DECLARE_COMPONENT(HardProcessTagVeto)

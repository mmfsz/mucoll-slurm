// probeZdecay.cc — apply candidate Pythia8 configs to the Z boson and dump
// the resulting decay-channel table, to pinpoint why `23:onIfAny = 1 2 3 4 5`
// excludes Z->bb in the Whizard-driven runs.
//
// Usage: probeZdecay "<config string with ;-separated readString commands>"

#include "Pythia8/Pythia.h"
#include <iostream>
#include <string>

using namespace Pythia8;

int main(int argc, char* argv[]) {
    std::string cfg = (argc > 1)
        ? std::string(argv[1])
        : std::string("23:mayDecay = on; 23:onMode = off; 23:onIfAny = 1 2 3 4 5");

    Pythia pythia;

    // Apply ;-separated commands (same path Whizard uses for $ps_PYTHIA8_config).
    size_t start = 0;
    while (start < cfg.size()) {
        size_t end = cfg.find(';', start);
        std::string one = cfg.substr(start, (end == std::string::npos) ? std::string::npos : end - start);
        // trim leading whitespace
        while (!one.empty() && (one.front() == ' ' || one.front() == '\t')) one.erase(one.begin());
        if (!one.empty()) {
            std::cout << "[probe] readString: '" << one << "'\n";
            bool ok = pythia.readString(one);
            std::cout << "[probe] readString returned " << (ok ? "true" : "FALSE") << "\n";
        }
        if (end == std::string::npos) break;
        start = end + 1;
    }

    // Don't run any beams/processes — we only care about the particle-data state.
    std::cout << "\n[probe] === Full decay channel table for Z (PDG 23) ===\n";
    pythia.particleData.list(23);

    // Summarise: which channels are on, which products, what bRatio?
    std::cout << "\n[probe] === Parsed summary: onMode + products per Z channel ===\n";
    auto pde = pythia.particleData.findParticle(23);
    if (!pde) {
        std::cout << "[probe] ERROR: could not find particle data for 23\n";
        return 1;
    }
    for (int i = 0; i < pde->sizeChannels(); ++i) {
        const auto& ch = pde->channel(i);
        std::cout << "  ch " << i
                  << "  onMode=" << ch.onMode()
                  << "  bRatio=" << ch.bRatio()
                  << "  meMode=" << ch.meMode()
                  << "  products=";
        for (int j = 0; j < ch.multiplicity(); ++j) std::cout << ch.product(j) << " ";
        std::cout << "\n";
    }
    return 0;
}

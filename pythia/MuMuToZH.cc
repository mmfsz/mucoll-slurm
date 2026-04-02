#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cmath>
#include <filesystem>

using namespace Pythia8;

// Usage: MuMuToZH <nEvents> <jobID> <outputPath>
int main(int argc, char* argv[]) {
    Pythia pythia;

    // parse cli arguments
    int nEvents = 10000;
    int jobID = 0;
    std::string outPath = "gen_output.hepmc";
    if (argc > 1) {
        try {
            nEvents = std::stoi(argv[1]);
            if (nEvents <= 0) {
                std::cerr << "nEvents must be positive, got " << nEvents
                          << ". Using default 10000 instead.\n";
                nEvents = 10000;
            }
        } catch (const std::exception& e) {
            std::cerr << "Could not parse nEvents from '" << argv[1]
                      << "'. Using default 10000.\n";
            nEvents = 10000;
        }
    }
    if (argc > 2) {
        try {
            jobID = std::stoi(argv[2]);
            if (jobID < 0) {
                std::cerr << "jobID can't be negative, got " << jobID
                          << ". Using default 0 instead.\n";
                jobID = 0;
            }
        } catch (const std::exception& e) {
            std::cerr << "Could not parse jobID from '" << argv[2]
                      << "'. Using default 0.\n";
            jobID = 0;
        }
    }
    if (argc > 3) {
        outPath = argv[3];
    }
    std::cout << "Generating " << nEvents << " events (jobID=" << jobID
              << ", output=" << outPath << ").\n";

    // set random seed: 1234 + jobID, matching Whizard chain convention
    pythia.readString("Random:setSeed = on");
    int randSeed = 1234 + jobID;
    while (randSeed > 900000000) {
        std::string s = std::to_string(randSeed);
        s.erase(0, 1);
        randSeed = std::stoi(s);
    }
    if (randSeed <= 0) randSeed = 1;
    pythia.readString("Random:seed = " + std::to_string(randSeed));

    // Set mu+mu- beams at 10 TeV
    pythia.readString("Beams:idA = -13");
    pythia.readString("Beams:idB = 13");
    pythia.readString("Beams:eCM = 10000.");

    // Enable HZ production (Higgs-Strahlung)
    pythia.readString("HiggsSM:ffbar2HZ = on");

    // Force Z -> bb and H -> bb to match Whizard ZH chain
    pythia.readString("23:onMode = off");
    pythia.readString("23:onIfAny = 5");
    pythia.readString("25:onMode = off");
    pythia.readString("25:onIfAny = 5");

    // Initialize
    pythia.init();

    // HepMC3 output
    HepMC3::Pythia8ToHepMC3 toHepMC;
    // Create parent directories if needed
    std::filesystem::path outDir(outPath);
    if (outDir.has_parent_path())
        std::filesystem::create_directories(outDir.parent_path());
    HepMC3::WriterAscii writer(outPath);

    int writtenEvents = 0;
    while (writtenEvents < nEvents) {
        if (!pythia.next()) continue;

        // Convert and write to HepMC
        HepMC3::GenEvent hepmc_evt;
        toHepMC.fill_next_event(pythia, hepmc_evt);

        // Filter particles: remove final-state particles with |eta| > 2.3
        std::vector<std::shared_ptr<HepMC3::GenParticle>> to_remove;
        for (auto p : hepmc_evt.particles()) {
            if (p->status() != 1) continue;
            auto mom = p->momentum();
            double px = mom.px(), py = mom.py(), pz = mom.pz();
            double p_mag = std::sqrt(px*px + py*py + pz*pz);
            if (p_mag == std::abs(pz)) continue;
            double eta = 0.5 * std::log((p_mag + pz) / (p_mag - pz));
            if (std::abs(eta) > 2.3) to_remove.push_back(p);
        }

        for (auto p : to_remove)
            hepmc_evt.remove_particle(p);

        writer.write_event(hepmc_evt);
        writtenEvents++;
    }

    writer.close();
    pythia.stat();
    return 0;
}
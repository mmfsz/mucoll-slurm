// LheToHepMC.cc
// Read a parton-level LHE file produced by Whizard (mu+mu- -> ZH, Z/H stable),
// then decay, shower, and hadronize with Pythia8, writing HepMC3 output.
//
// This is the GEN step for the LHE route (SET=5 in run_chain_ZH.sh).
// Per-boson color flow is handled entirely by Pythia8, avoiding the ~38%
// cross-ancestry bias introduced by Whizard's color assignment in the hybrid.
//
// Usage: LheToHepMC <lheFile> <nEvents> <jobID> <outputPath>
//
// Author: Maria Mazza

#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"

#include <iostream>
#include <string>
#include <filesystem>

using namespace Pythia8;

int main(int argc, char* argv[]) {

    std::string lheFile  = "input.lhe";
    int         nEvents  = 10;
    int         jobID    = 0;
    std::string outPath  = "gen_output.hepmc";

    if (argc > 1) lheFile = argv[1];
    if (argc > 2) {
        try { nEvents = std::stoi(argv[2]); }
        catch (...) { std::cerr << "Bad nEvents '" << argv[2] << "', using " << nEvents << "\n"; }
    }
    if (argc > 3) {
        try { jobID = std::stoi(argv[3]); }
        catch (...) { std::cerr << "Bad jobID '" << argv[3] << "', using 0\n"; }
    }
    if (argc > 4) outPath = argv[4];

    std::cout << "LheToHepMC: lheFile=" << lheFile
              << "  nEvents=" << nEvents
              << "  jobID="   << jobID
              << "  output="  << outPath << "\n";

    Pythia pythia;

    // --- Random seed: 1234 + jobID, clamped to Pythia8's valid range ---
    pythia.readString("Random:setSeed = on");
    int randSeed = 1234 + jobID;
    while (randSeed > 900000000) {
        std::string s = std::to_string(randSeed);
        s.erase(0, 1);
        randSeed = std::stoi(s);
    }
    if (randSeed <= 0) randSeed = 1;
    pythia.readString("Random:seed = " + std::to_string(randSeed));

    // --- LHE input ---
    pythia.readString("Beams:frameType = 4");
    pythia.readString("Beams:LHEF = " + lheFile);

    // --- Force Z -> bb ---
    pythia.readString("23:mayDecay = on");
    pythia.readString("23:onMode = off");
    pythia.readString("23:onIfAny = 5");

    // --- Force H -> bb ---
    pythia.readString("25:mayDecay = on");
    pythia.readString("25:onMode = off");
    pythia.readString("25:onIfAny = 5");

    // --- Enable FSR and hadronization ---
    pythia.readString("PartonLevel:FSR = on");
    pythia.readString("HadronLevel:Hadronize = on");
    pythia.readString("HadronLevel:Decay = on");

    // --- Suppress verbose output ---
    pythia.readString("Next:numberShowEvent = 0");
    pythia.readString("Next:numberShowInfo = 0");
    pythia.readString("Next:numberShowProcess = 0");

    if (!pythia.init()) {
        std::cerr << "Pythia8 initialization failed\n";
        return 1;
    }

    // --- HepMC3 output ---
    HepMC3::Pythia8ToHepMC3 toHepMC;
    std::filesystem::path outDir(outPath);
    if (outDir.has_parent_path())
        std::filesystem::create_directories(outDir.parent_path());
    HepMC3::WriterAscii writer(outPath);

    int written = 0;
    int attempts = 0;
    const int maxAttempts = nEvents * 100;

    while (written < nEvents && attempts < maxAttempts) {
        ++attempts;
        if (!pythia.next()) continue;

        HepMC3::GenEvent hepmc_evt;
        toHepMC.fill_next_event(pythia, hepmc_evt);
        writer.write_event(hepmc_evt);
        ++written;
    }

    writer.close();

    if (written < nEvents) {
        std::cerr << "WARNING: only wrote " << written << " / " << nEvents << " events\n";
    }

    pythia.stat();
    std::cout << "LheToHepMC: wrote " << written << " events to " << outPath << "\n";
    return (written == nEvents) ? 0 : 1;
}

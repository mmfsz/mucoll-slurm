# Default compiler and flags
CXX = g++
CXXFLAGS = -O2 -std=c++17

# Set these via environment or directly here
PYTHIA8_CONFIG := pythia8-config

# Separate compiler includes from linker flags
PYTHIA8_CFLAGS := $(shell $(PYTHIA8_CONFIG) --cxxflags)
PYTHIA8_LIBS   := $(shell $(PYTHIA8_CONFIG) --libs)
HEPMC3_INC     := -I$(HEPMC3_DIR)/include
HEPMC3_LIB     := -L$(HEPMC3_DIR)/lib -lHepMC3

# Get all .cc files in the directory
SOURCES := $(wildcard *.cc)
TARGETS := $(basename $(SOURCES))

# Default rule: build all executables
all: $(TARGETS)

# Pattern rule: includes before source, libraries after
%: %.cc
	$(CXX) $(CXXFLAGS) $(PYTHIA8_CFLAGS) $(HEPMC3_INC) -o $@ $< $(PYTHIA8_LIBS) $(HEPMC3_LIB)

# Clean
clean:
	rm -f $(TARGETS)
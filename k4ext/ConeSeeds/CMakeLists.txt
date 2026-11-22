cmake_minimum_required(VERSION 3.20)
project(ConeSeeds LANGUAGES CXX)

# Built inside the MAIA v3.2 container against its spack stack (see k4ext/build.sh).
find_package(Gaudi REQUIRED)
find_package(k4FWCore REQUIRED)
find_package(EDM4HEP REQUIRED)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

gaudi_add_module(ConeSeedsPlugins
  SOURCES src/HardProcessTagVeto.cpp
  LINK Gaudi::GaudiKernel k4FWCore::k4FWCore EDM4HEP::edm4hep)

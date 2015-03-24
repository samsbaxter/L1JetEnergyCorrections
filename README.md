#L1 Jet Energy Corrections/Calibrations (JEC)

__tl;dr__: The code in here calculates corrections for jets from the Level 1 trigger.

This applies to:

- Legay GCT
- Stage 1
- Stage 2 *TODO*

## Installation

```shell
# For GCT:
cmsrel CMSSW_7_2_0
# For Stage 1: check Twiki page
cmsresl CMSSW_7_3_0

cd CMSSW_7_*_0/src
cmsenv

# Stage 1 emulator - do this first
git cms-addpkg L1Trigger/L1TCalorimeter
# L1Ntuples package - see https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1TriggerDPGNtupleProduction
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
# This package
git clone git@github.com:raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections

# Build it all
scram b -j9
# to run unit tests (advised whenever you make changes)
scram b runtests
# to make documentation:
cd L1Trigger/L1JetEnergyCorrections/doc
doxygen Doxyfile # html documentation in html/index.html
# optional - to build pdf documentation. Produces latex/refman.pdf
# cd latex; make
```

## Basic concept

The following is a conceptual outline of the method that is used to calibrate jet energies.

1. Run a config file over a sample, running the relevant L1 emulator and produce 2 sets of jets: **reference jets** (e.g. `ak5GenJet`s) and **L1 jets** (the ones you want to calibrate, e.g. `L1GctInternJet`s).
2. Convert these jet collections into consistent collections, containing the info we need to calibrate (say, 4-vectors).
3. Pass these 2 collections to a Matcher. This will match L1 jets to reference jets, and output pairs of matched jets.
4. Take these collections, plot various response quantities, and derive correction curves & coefficients to put into a lookup table (LUT).

## Running
These steps are executed by the following:

1) & 2) Produce Ntuple with relevant jet collections -> CMSSW + py config + CRAB3

3) Produce matching jet pairs from this Ntuple -> [bin/RunMatcher](bin/RunMatcher.cpp)

4) Make some plots from these pairs, and calculate calibrations constants, etc. -> [bin/runCalibration.py](bin/runCalibration.py)

### Produce Ntuples
See [python/l1Ntuple_GCT_cfg.py](python/l1Ntuple_GCT_cfg.py) and [python/l1Ntuple_Stage1_cfg.py](python/SimL1Emulator_Stage1_newRCT.py). CRAB3 scripts are in the [crab](crab) folder.

Both run over GEN-SIM-RAW MC, and utilise the L1Ntuple package with l1Extra collections.

For out L1 jets, we utilise the internal jet collections in the GCT/Stage1 emulator i.e. pre sorting and taking top 4. to convert from the internal jet objects to L1JetParticle collections, there are several EDProducers:

- [GenJetToL1Jet](plugins/GenJetToL1Jet.cc) converts GenJet collections (do for both ak4 and ak5)
- [GctInternJetToL1Jet](plugins/GctInternJetToL1Jet.cc) converts GctInternJetData collection (for GCT)
- [PreGtJetToL1Jet](plugins/PreGtJetToL1Jet.cc) converts PreGtJets collection (for Stage 1)

Note that at the moment, we hijack the cenJet collection of L1ExtraTree for our GenJets/L1 jets, so we have to make clones of the L1ExtraTreeProducer for these. The L1ExtraTreeProducer accepts the output collection from any of the above EDProducers.

*This is the only stage which is emulator-specific.* Beyond this step, the output format is the same whether you are dealing with GCT or Stage1/2.

There is also a module to store pileup info (such as number of verticies) in the output ntuples, [PileupInfo](plugins/PileupInfo.cc).

### Produce matching jet pairs
This is done in [bin/RunMatcher](bin/RunMatcher.cpp). You can run it easily by doing `RunMatcher <options>`. For options, do `RunMatcher --help`. As a minimum, you need an input Ntuple and output filename.

Note that the RunMatcher program also includes an option to plot the eta Vs phi for jets to check it's actually working (this utilises the [JetDrawer](interface/JetDrawer) class).

### Calculate calibration function & LUTs
This is done by [bin/runCalibration.py](bin/runCalibration.py). For possible options, in `bin` do `python runCalibration.py -h`

### Resolution performance
This is dine by [bin/makeResolutionPlots.py](bin/makeResolutionPlots.py) This takes the ROOT file with matched pairs (i.e. the output from `RunMatcher`, and produces resolution plots stored in a ROOT file. Quantities include `L1 - Ref`, `(L1 - Ref) / L1`, and `(L1 - Ref) / Ref`. For possible options, in `bin` do `python makeResolutionPlots.py -h`

### Other scripts
There are several other useful scirpts in `bin` dir. Doing `python <scriptname> -h` should elucidates the possible options.

- [calibration_results.py](bin/calibration_results.py) This takes the ROOT file output by `runCalibration.py` and turns it into a couple of PDF presentations with all the plots for all bins. One will have all the correction values and fits, and one will have the individual pt & response plots for each eta and pt bin.

- [resolution_results.py](bin/resolution_results.py) This takes the output file from `makeResolutionPlots.py` and turns it into some beamer presentations. Can do one file by itself, or compare 2 files (e.g. pre and post calibrations). By default, it just plots the various resolution definitions against L1 pT, for each |eta| bin. Can also plot resolution curve & fit for every pt bin as well (very slow).

## Editing

Please see [DEV_NOTES](DEV_NOTES.md) for info.
```
# Old instructions for how to compile root with custom objects - ignore for now
# cd L1Trigger/L1JetEnergyCorrections/interface
# For custom classes in TTree branches
# rootcint -f dictionary.cpp -c TLorentzVector.h $CMSSW_BASE/src/L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h LinkDef.h
# mv dictionary.cpp ../src/
# cd $CMSSW_BASE/src
```
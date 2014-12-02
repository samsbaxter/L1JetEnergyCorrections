#L1 Jet Energy Corrections/Calibrations (JEC)

__tl;dr__: The code in here calculates corrections for jets from the Level 1 trigger.

This applies to:

- Legay GCT
- Stage 1 *TODO*
- Stage 2 *TODO*

It is an attempt to unify previous fragments of code lying around, in a *generic* way.

## Installation

First make sure you have a copy of CMSSW (I'm using CMSSW_7_2_0_pre7). Then in `CMSSW_X_Y_Z/src`:

```shell
cmsenv
# L1Ntuples package - see https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1TriggerDPGNtupleProduction
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
# This package
git clone git@github.com:raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections
cd L1Trigger/L1JetEnergyCorrections/interface
rootcint -f dictionary.cpp -c TLorentzVector.h ../../../L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h LinkDef.h
mv dictionary.cpp ../src/
cd $CMSSW_BASE/src
# L1ExtraFromDigis - modified L1ExtraParticlesProd. Bit ad-hoc, want better solution
git add-pkg L1Trigger/L1ExtraFromDigis
cp plugins/L1ExtraParticlesProd.ccBK L1Trigger/L1ExtraFromDigis/src/L1ExtraParticlesProd.cc
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
4. Pass matched pairs to a Calibration Calculator. This will calcualte the calibration constants, and produce plots. [__NOTE__ this hasn't actually been done yet... just borrowed a python script from Nick Wardle that works pretty well.]

## Running
These steps are executed by the following:

1) & 2) Produce Ntuple with relevant jet collections

3) Produce matching jet pairs from this Ntuple

4) Make some plots from these pairs, and calculate calibrations constants, etc

### Produce Ntuples
Look at `/python/l1Ntuple_cfg.py`. Do `cmsRun l1NTuple_cfg.py` to run over some GEN-SIM-RAW MC. This should produce a ntuple with L1Extra trees. Note that at the moment, we hijack the cenJet collection of L1ExtraTree for our GenJets/GctInternJets, so we hve to make clones of the L1ExtraProducer for these. Perhaps I should write an EDAnalyzer?

### Produce matching jet pairs
This is done in `bin/RunMatcher`. You can run it easily by doing `RunMatcher <options>`. For command-line options, do `RunMatcher --help`. As a minimum, you need an input Ntuple and output filename.

Note that the RunMatcher program also includes an option to plot the eta Vs phi for jets to check it's actually working.

### Make plots, calculate constants, etc
This is done in `bin/runCalibration.py`. In `/bin` do: `python runCalibration.py <input file> < output file>` where input = whatever file RunMatcher produced.

There is also a script, [showoffPlots.py](bin/showoffPlots.py) that takes the ROOT files and makes select plots, with nice labels, etc, for use in presentations, etc. It's a bit ad-hoc.


## Editing

Please see [DEV_NOTES](DEV_NOTES.md) for info.
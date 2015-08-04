#L1 Jet Energy Corrections/Calibrations (JEC)

__tl;dr__: The code in here calculates corrections for jets from the Level 1 trigger.

This applies to:

- Legay GCT
- Stage 1
- Stage 2 *TODO*

## Installation

```shell
# To re-run the RCT emulator you MUST use 742 or newer otherwise untold pain
# And check it has Boost v1.57 or newer
# Also need Python 2.7 or newer for argparse module
cmsrel CMSSW_7_4_2
cd CMSSW_7_4_2/src
cmsenv

# Stage 1 emulator - do this first
git cms-addpkg L1Trigger/L1TCalorimeter
# L1DPG Ntuples package
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
# L1TNtuples package - see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideL1TNtuples
# git remote add cms-l1t-offline git@github.com:cms-l1t-offline/cmssw.git
# git fetch cms-l1t-offline
# git checkout cms-l1t-offline/l1t-ntuple-dev L1Trigger/L1TNtuples
# This package
git clone git@github.com:raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections

# Build it all
scram b -j9
# to run unit tests (advised whenever you make changes)
scram b runtests
# optional - to make documentation:
cd L1Trigger/L1JetEnergyCorrections/doc
doxygen Doxyfile # html documentation in html/index.html
# to build pdf documentation. Produces latex/refman.pdf
# cd latex; make
```

- **WARNING:** in CMSSW_7_4_5 and later, `L1RCTProducer` uses the new AMC13 FED IDs for HF. So if you run over Spring15 MC or earlier, you'll need to change the FEDs back, or end up with nothing in the HF: https://github.com/cms-sw/cmssw/commit/8b127a6660bdb557ccc2241db022687d3c2936d0

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
See [python/l1Ntuple_GCT_rerunRCT_cfg.py](python/l1Ntuple_GCT_rerunRCT_cfg.py) and [python/l1Ntuple_Stage1_cfg.py](python/SimL1Emulator_Stage1_newRCT.py). CRAB3 scripts are in the [crab](crab) folder.

Both run over GEN-SIM-RAW MC, and utilise the L1Ntuple package with l1Extra collections.

For out L1 jets, we utilise the internal jet collections in the GCT/Stage1 emulator i.e. pre sorting and taking top 4. to convert from the internal jet objects to L1JetParticle collections, there are several EDProducers:

- [GenJetToL1Jet](plugins/GenJetToL1Jet.cc) converts GenJet collections (do for both ak4 and ak5)
- [GctInternJetToL1Jet](plugins/GctInternJetToL1Jet.cc) converts GctInternJetData collection (for GCT)
- [PreGtJetToL1Jet](plugins/PreGtJetToL1Jet.cc) converts PreGtJets collection (for Stage 1)

Note that at the moment, we hijack the cenJet collection of L1ExtraTree for our GenJets/L1 jets, so we have to make clones of the L1ExtraTreeProducer for these. The L1ExtraTreeProducer accepts the output collection from any of the above EDProducers.

*This is the only stage which is emulator-specific.* Beyond this step, the output format is the same whether you are dealing with GCT or Stage1/2.

There is also a module to store pileup info (such as number of verticies) in the output ntuples, [PileupInfo](plugins/PileupInfo.cc).

*Note:* a full set of Ntuples + pairs files for binned QCD is **big**: about 50 GB

### Produce matching jet pairs
This is done in [bin/RunMatcher](bin/RunMatcher.cpp). You can run it easily by doing `RunMatcher <options>`. For options, do `RunMatcher --help`. As a minimum, you need an input Ntuple and output filename.

Note that the RunMatcher program also includes an option to plot the eta Vs phi for jets to check it's actually working (this utilises the [JetDrawer](interface/JetDrawer) class).

### Calculate calibration function & LUTs
Calculation of calibration functions is done by [bin/runCalibration.py](bin/runCalibration.py), using the ROOT file of matched pairs output by the `RunMatcher` program as input. For possible options, do `python runCalibration.py -h`. Note that the script can be a little time consuming, therefore there is also a bsub script to submit to the LXBATCH system, see [bin/submit_calibration_jobs.sh](bin/submit_calibration_jobs.sh)

To make the LUTs, see below.

### Resolution performance
This is done in [bin/makeResolutionPlots.py](bin/makeResolutionPlots.py) This takes the ROOT file with matched pairs output by `RunMatcher`, and produces resolution plots stored in a ROOT file. Quantities include `L1 - Ref`, `(L1 - Ref) / L1`, and `(L1 - Ref) / Ref`. For possible options, in `bin` do `python makeResolutionPlots.py -h`. Note that the script can be a little time consuming, therefore there is also a bsub script to submit to the LXBATCH system, see [bin/submit_resolution_jobs.sh](bin/submit_resolution_jobs.sh)

### Other scripts
There are several other useful scripts in the `bin` dir. Doing `python <scriptname> -h` should elucidates the possible options.

- [checkCalibration.py](bin/checkCalibrationn.py) This takes the ROOT files of matched pairs output by `RunMatcher` as input, and makes a few plots to check the response of L1 jets against reference jets.

- [showoffPlots.py](bin/showoffPlots.py) This takes in ROOT files output by runCalibration / RunMatcher / checkCalibration / makeResolutionPlots, to quicky output interesting PDF plots for use in presentation or similar.

- [calibration_results.py](bin/calibration_results.py) This takes the ROOT file output by `runCalibration.py` and turns it into a couple of PDF presentations with all the plots for all bins. One will have all the correction values and fits, and one will have the individual pt & response plots for each eta and pt bin. NOTE: currently uses lualatex...should probably change this.

- [resolution_results.py](bin/resolution_results.py) This takes the output file from `makeResolutionPlots.py` and turns it into some beamer presentations. Can do one file by itself, or compare 2 files (e.g. pre and post calibrations). By default, it just plots the various resolution definitions against L1 pT, for each |eta| bin. Can also plot resolution curve & fit for every pt bin as well (very slow). NOTE: currently uses lualatex...should probably change this.

```
# Old instructions for how to compile root with custom objects - ignore for now
# cd L1Trigger/L1JetEnergyCorrections/interface
# For custom classes in TTree branches
# rootcint -f dictionary.cpp -c TLorentzVector.h $CMSSW_BASE/src/L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h LinkDef.h
# mv dictionary.cpp ../src/
# cd $CMSSW_BASE/src
```

## Making new JEC LUT

**Currently for GCT only**

To apply, need to make a new `L1GctConfigProducers` module. Unfortunately, this also contains other parameters to setup the GCT, which we do _not_ want to change. Therefore the following steps must be followed:

1) Use [checkGctConfig_cfg.py](python/checkGctConfig_cfg.py) to show the current GCT setup in whichever sample you are running over. Make sure to change the Global Tag to match whichever smaple you want to run over. Also ensure that the line
```
process.load('l1GctConfig_720_PHYS14_ST_V1_central_cfi')
```
is commented out.

2) This will dump the GCT settings to screen (somewhere amongst the other messages). Make a copy of [l1GctConfig_template_cfi.py](python/l1GctConfig_template_cfi.py) and update the parameters to match the printout in the previous step.

3) Now make the LUT to go into the `L1GctConfigProducers`. Use [correction_LUT_plot.py](bin/correction_LUT_plot.py) to run over your output from [bin/runCalibration.py](bin/runCalibration.py) and make a LUT. This script alos allows you to plot the correction functions, to ensure they are sensible, and optionally prints the function to screen in ROOT/PyROOT/numpy formats so you can use them in scripts, etc.

4) Copy the LUT into your `L1GctConfigProducers` setup.

5) Run `scram b -j9` to ensure your new cfi file is recognised.

## Applying new JEC LUT

**Currently for GCT only**

1) In your L1Ntuple config file, add in line:

```
process.load('L1Trigger.L1JetEnergyCorrections.my_new_gct_config_cfi')
```

You will now run with whatever calibrations you derived.

To check they are being applied:

1) the following should be output when running:
```
MSG-w L1GctConfig:  (NoModuleName) 07-May-2015 15:56:38 CEST pre-events
Calibration Style option PF
%MSG
```

2) check the L1 Ntuple output jet collections, to ensure the changes are being registered.

### Existing LUTs:

### Random notes:

- For all CMSSW releases up to and including 7_4_X, there is a bug in the standard Stage 1 emulator sequence that auto loads the old RCT LUTs: https://github.com/cms-sw/cmssw/blob/CMSSW_7_4_2/L1Trigger/L1TCalorimeter/python/L1TCaloStage1_PPFromRaw_cff.py#L9 To get around this, basically copy and paste that file's contents wihtout that line...sigh. Should be fixed in 7_5_X though.

- For new RCT calibs, use 7_4_2 or better - check with https://twiki.cern.ch/twiki/bin/viewauth/CMS/RCTCalibrationTP

- **WARNING:** in CMSSW_7_4_5 and later, the L1RCTProducer uses the new AMC13 FED IDs for HF. So if you run over Spring15 MC or ealrier, you'll need to change the FEDs back, or end up with nothing in the HF: https://github.com/cms-sw/cmssw/commit/8b127a6660bdb557ccc2241db022687d3c2936d0

- **ALWAYS** double check with the `l1RCTParametersTest` module that you are running the correct RCT calibs - if in doubt, check with Laura/Maria/Aaron


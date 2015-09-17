#Deriving L1 Jet Energy Corrections

This file explains how the calibrations are derived and which scripts are used. Note that the process is essentially the same for GCT & Stage 1, apart from different CMSSW config files, and slight differences in collection names.

- [Basic concept](#basic-concept)
- [Running](#running)
- [1) & 2) Producing ntuples](#1--2-producing-ntuples)
  - [CRAB3](#crab3)
  - [HTCondor on soolin (Bristol only, but MUCH faster)](#htcondor-on-soolin-bristol-only-but-much-faster)
- [3) Matching jets](#3-matching-jets)
  - [PBS (e.g. `lxbatch` at CERN)](#pbs-eg-lxbatch-at-cern)
  - [HTCondor on soolin (Bristol only)](#htcondor-on-soolin-bristol-only)
- [4) Calculating calibration functions](#4-calculating-calibration-functions)
  - [PBS](#pbs)
  - [HTCondor on soolin (Bristol only)](#htcondor-on-soolin-bristol-only-1)
- [5) Making a new LUT](#5-making-a-new-lut)
- [GCT](#gct)
- [Stage 1](#stage-1)
- [Stage 2 (TODO)](#stage-2-todo)

##Basic concept

The following is an outline of the method that is used to calibrate jet energies.

1. Run a config file over sample(s), running the relevant L1 emulator and produce 2 sets of jets: **reference jets** (e.g. `ak4GenJet`s) and **L1 jets** (the ones you want to calibrate, e.g. `L1GctInternJet`s).
2. Convert these jet collections into consistent collections, containing the info we need to calibrate.
3. Pass these 2 collections to a Matcher. This will match L1 jets to reference jets, and output pairs of matched jets.
4. Take these collections, plot various response quantities, and derive correction curves & coefficients to put into a lookup table (LUT).

## Running
These steps are executed by the following:

1) & 2) Produce ntuple with relevant jet collections -> CMSSW + python config

3) Produce matching jet pairs from this ntuple -> [bin/RunMatcher](bin/RunMatcher.cpp) (for MC)

4) Calculate calibrations functions & constants -> [bin/runCalibration.py](bin/runCalibration.py)

5) Make a new LUT -> [bin/correction_LUT_plot.py](bin/correction_LUT_plot.py)

More details:

### 1) & 2) Producing ntuples

Main config scripts are:

- **GCT**: [python/l1Ntuple_GCT_rerunRCT_cfg.py](python/l1Ntuple_GCT_rerunRCT_cfg.py)
- **Stage 1**: [python/SimL1Emulator_Stage1_newRCT.py](python/SimL1Emulator_Stage1_newRCT.py)


Both run over GEN-SIM-RAW MC, and utilise the L1Ntuple package with l1Extra collections. Since we also need the new RCT calibrations, the workflow is typically:

1) Unpack ECAL/HCAL trigger primitives

2) Run the RCT emulator using these, with the latest calibrations. This makes regions.

3) Run the GCT/Stage 1 emulator using these regions

4) Store the jets from the trigger

5) Also store genJets

For calibrating, we use the *internal* jet collections in the trigger: these have a better granularity (0.5 GeV instead of 4), and all jets are kept, not just the top 4. To convert from the internal jet objects to `L1JetParticle` objects, there are several EDProducers:

- [GenJetToL1Jet](plugins/GenJetToL1Jet.cc) converts GenJet collections
- [GctInternJetToL1Jet](plugins/GctInternJetToL1Jet.cc) converts GctInternJetData collection (for GCT)
- [PreGtJetToL1Jet](plugins/PreGtJetToL1Jet.cc) converts PreGtJets collection (for Stage 1)

The outputs can then be passed easily into an instance of a `L1ExtraTreeProducer`. Note that at the moment, the internal jets are _not_ split into cen/fwd, so we hijack the `cenJet` collection of instances of `L1ExtraTree`s for our GenJets/L1 jets.

**Turn off corrections**: these are generic NTuple-making configs, and as such you'll probably need to turn off any existing corrections:

**GCT**:

GCT internal jets are by default uncalibrated. Yay!

**Stage1**:

**TODO** check if preGt jets are uncalibrated.

Change any lines with:

```
process.caloStage1Params.jetCalibrationType = cms.string("Stage1JEC")
```

to

```
process.caloStage1Params.jetCalibrationType = cms.string("None")
```
Note that the usual jets the trigger outputs are also stored, so that they an be used to test the calibrations.

There is also a module to store pileup info (such as number of vertices) in the output ntuples, [PileupInfo](plugins/PileupInfo.cc).

To run ntuple-making jobs on a batch system, there are 2 options:

####CRAB3

Use [crab/crab3_gct.py](crab/crab3_gct.py) for GCT config, or [crab/crab3_stage1.py](crab/crab3_stage1.py) for Stage 1:

```
python crab3_xxx.py
```

Dataset(s) to run over are specified in the list `datasets`, where the possible values are specified as key names in [python/mc_samples.py](python/mc_samples.py). Use this file to specify job splitting, and total number of files to run over.

####HTCondor on soolin (Bristol only, but MUCH faster)

Use [condor/submitSamples_dag.py](condor/submitSamples_dag.py):

```
python submitSamples_dag.py
```

Set the variables:

- `config` to point to the CMSSW config file
- `outputDir` to point to a directory to store the ntuples. This must to somewhere on /hdfs, e.g. under `/hdfs/user/$LOGNAME`
- `datasets` as a list of dataset names, where the names available are the key names in [python/mc_samples.py](python/mc_samples.py)

You can check the status of jobs using the script [bin/HTCondor/DAGstatus.py](bin/HTCondor/DAGstatus.py).

### 3) Matching jets

This is done in [bin/RunMatcher](bin/RunMatcher.cpp). You can run it easily by doing `RunMatcher <options>`. For options, do `RunMatcher --help`. At a minimum, you need an input ntuple and output filename.
Note that the RunMatcher program also includes an option to plot the eta Vs phi for jets to check it's actually working. By default, the matching program is setup with:
- pT(GenJet) > 14 GeV
- pT(L1) > 0 GeV
- DeltaR(L1, GenJet) < 0.7

To run jobs on batch system, there are 2 options:

####PBS (e.g. `lxbatch` at CERN)

Use the script [bin/PBS/submit_matcher_jobs.sh](bin/PBS/submit_matcher_jobs.sh).

####HTCondor on soolin (Bristol only)

Use [bin/HTCondor/submit_matcher_dag.sh](bin/HTCondor/submit_matcher_dag.sh). You need to change the array `treedirs` to include the directory containing your L1NTuples. You also need to set the flag `internal=true` if you want to use the internal jet collection, otherwise it will use the jets passed to the GT.

You can also change the options passed to `RunMatcher`, and add an append to the auto-generated filename.

### 4) Calculating calibration functions

This is done using the script [bin/runCalibration.py](bin/runCalibration.py). For options, do `python runCalibration.py --help`. At a minimum, you need a pairs file as input (from running `RunMatcher`), and the name of an output file to hold all the plots and correction functions. You also need to specify some defaults for the fits, using `--gct`/`--stage1` flags. There are also options to turn off certain plots, and to skip or redo the correction function fitting (e.g. to save time, or to try a new fitting procedure without having to remake all the same component histograms again).

To run jobs on batch system, there are 2 options:

####PBS

Use the script [bin/PBS/submit_calibration_jobs.sh](bin/PBS/submit_calibration_jobs.sh).

####HTCondor on soolin (Bristol only)

Use the script [bin/HTCondor/submit_calibration_dag.sh](bin/HTCondor/submit_calibration_dag.sh).

The user must add in the input pairs files made by `RunMatcher` to the array `pairsFiles`. Can also change the PU bins to run over (by default it runs over all PU).

### 5) Making a new LUT

The form of the LUT is system-specific: it is very different for GCT, Stage 1 & 2.

###GCT
To apply the new settings to the GCT emulator, need to make a new `L1GctConfigProducers` module. Unfortunately, this also contains other parameters to setup the GCT, which we do _not_ want to change. Therefore the following steps must be followed:

1) Use [checkGctConfig_cfg.py](python/checkGctConfig_cfg.py) to show the current GCT setup in whichever sample you are running over. Make sure to change the Global Tag to match whichever sample you want to run over. Also ensure that the line

```
process.load('l1GctConfig_xxx_cfi')
```
is commented out.

2) This will dump the GCT settings to screen (somewhere amongst the other messages). Make a copy of [l1GctConfig_template_cfi.py](python/l1GctConfig_template_cfi.py) and update the parameters to match the printout in the previous step.

3) Now make the LUT to go into the `L1GctConfigProducers`. Use [correction_LUT_plot.py](bin/correction_LUT_plot.py) to run over your output from [bin/runCalibration.py](bin/runCalibration.py) and make a LUT. This script also allows you to plot the correction functions, to ensure they are sensible, and optionally prints the function to screen in ROOT/PyROOT/numpy formats so you can use them in scripts, etc.

4) Copy the LUT into your `L1GctConfigProducers` setup.

5) Run `scram b -j9` to ensure your new cfi file is recognised.

###Stage 1

Use the script [bin/correction_LUT_plot.py](bin/correction_LUT_plot.py):

```
python correction_LUT_plot.py --stage1 --fancy --plots <output from runCalibration.py> <name of LUT file>
```

The flags are:

- `--fancy`: do 'fancy' corrections functions, where the correction value is plateaued below the pt where the graph deviates from the fit.
- `--plots`: make various plots, including plots of the fancy fits, a pre/port pT mapping, a 2D LUT check plot, and all the original fit functions.

Remember to run `scram b` afterwards. **Note**: it is wise to put the LUT in [data](data) otherwise it will no be picked up when submitting CRAB/condor jobs.

Plots made will end up in the same directory as the input file, under a directory with the name of the LUT file (minus extension). A debug dump of the LUT, and the 2D heat map, will be produced in the same location as the LUT.

###Stage 2 (TODO)
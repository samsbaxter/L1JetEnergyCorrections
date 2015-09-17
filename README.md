#L1 Jet Energy Corrections/Calibrations (JEC)

The code in here calculates & tests corrections for jets produced by the Level 1 trigger.

This applies to:

- Legacy GCT
- Stage 1
- Stage 2 *TODO*

## Installation

```shell
# To re-run the RCT emulator you MUST use 742 or newer otherwise untold pain
# Check it has Boost v1.57 or newer for RCT calibs
# Also need Python 2.7 or newer for argparse module
cmsrel CMSSW_7_4_2
cd CMSSW_7_4_2/src
cmsenv

# Stage 1 emulator - do this first
git cms-addpkg L1Trigger/L1TCalorimeter
# L1DPG Ntuples package
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
# This package
git clone git@github.com:raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections

# Build it all
scram b -j9
# to run unit tests
scram b runtests
# optional - to make documentation:
cd L1Trigger/L1JetEnergyCorrections/doc
doxygen Doxyfile # html documentation in html/index.html
# To build pdf documentation (produces latex/refman.pdf):
# cd latex; make
```

- **WARNING:** in CMSSW_7_4_5 and later, `L1RCTProducer` uses the new AMC13 FED IDs for HF. So if you run over Spring15 MC or earlier, you'll need to change the FEDs back, or end up with nothing in the HF: https://github.com/cms-sw/cmssw/commit/8b127a6660bdb557ccc2241db022687d3c2936d0

For instructions about **deriving** new calibrations, see [derivation.md](derivation.md).

For instructions about **applying** new calibrations, see [applying.md](applying.md).

For instructions about **testing** the calibration & performance, see [performance.md](performance.md).


### Random notes:

- For all CMSSW releases up to and including 7_4_X, there is a bug in the standard Stage 1 emulator sequence that auto loads the old RCT LUTs: https://github.com/cms-sw/cmssw/blob/CMSSW_7_4_2/L1Trigger/L1TCalorimeter/python/L1TCaloStage1_PPFromRaw_cff.py#L9 To get around this, basically copy and paste that file's contents without that line...sigh. Should be fixed in 7_5_X though.

- For new RCT calibs, use 7_4_2 or better - check with https://twiki.cern.ch/twiki/bin/viewauth/CMS/RCTCalibrationTP

- **WARNING:** in CMSSW_7_4_5 and later, the L1RCTProducer uses the new AMC13 FED IDs for HF. So if you run over Spring15 MC or ealrier, you'll need to change the FEDs back, or end up with nothing in the HF: https://github.com/cms-sw/cmssw/commit/8b127a6660bdb557ccc2241db022687d3c2936d0

- **Always** double check with the `l1RCTParametersTest` module that you are running the correct RCT calibs - if in doubt, check with Laura/Maria/Aaron


#Applying L1 Jet Energy Corrections

This short file details how to apply new L1JECs to the emulator.

Note that it is always wise to do a quick test run to ensure the L1 jet energies are updated when applying new corrections.

- [Applying L1 Jet Energy Corrections](#applying-l1-jet-energy-corrections)
    - [GCT](#gct)
        - [Test it](#test-it)
    - [Stage 1](#stage-1)
        - [Test it](#test-it)
    - [Stage 2 (TODO)](#stage-2-todo)

##GCT

First, make your new `L1GctConfigProducers` module, see [derivation.md](derivation.md).

In your config file, add in the line:

```
process.load('L1Trigger.L1JetEnergyCorrections.my_new_gct_config_cfi')
```

You will now run with whatever calibrations you derived.


###Test it
To check they are being applied, the following should be output when running:
```
MSG-w L1GctConfig:  (NoModuleName) 07-May-2015 15:56:38 CEST pre-events
Calibration Style option PF
%MSG
```

##Stage 1

For the latest LUT, look here: https://twiki.cern.ch/twiki/bin/view/CMS/L1TCaloCalibration#Jet_Calibration_Sets

The LUTs are stored in [data](data).

In your config file, **after** you have added the Stage 1 emulator, i.e. after

```
process.load('L1Trigger.L1TCalorimeter.caloStage1Params_cfi')
# or
process.load("L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff")
```

add in the following lines:

```
process.caloStage1Params.jetCalibrationType = cms.string("Stage1JEC")
process.caloStage1Params.jetCalibrationLUTFile = cms.FileInPath(<path to LUT>)
```

where `<path to LUT>` is **relative** to `$CMSSW_BASE/src` and must be enclosed in single or double quotes.

e.g. if you want to use the LUT `$CMSSW_BASE/src/L1Trigger/L1JetEnergyCorrections/data/LUT.txt` you would use `L1Trigger/L1JetEnergyCorrections/data/LUT.txt`

Note that if it cannot find the LUT it will issue an error message.

Also note that the LUT must be in a sub-directory name `data` in a package (and you've run `scram b`), since CRAB3 (and my condor scripts) will **only** pick up additional files from those directories.

**Important** if you are using `L1TCaloStage1_PPFromRaw.py` to setup the emulator, in 7.4.X and earlier there is a bug that overrides any RCT calibrations. The offending line is:

```
from L1Trigger.L1TCalorimeter.caloStage1RCTLuts_cff import *
```

Your best bet is to do as in [python/SimL1Emulator_Stage1_newRCT.py](python/SimL1Emulator_Stage1_newRCT.py):

```
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration/StandardSequences/SimL1Emulator_cff')

# Default Stage 1 params
process.load('L1Trigger.L1TCalorimeter.caloStage1Params_cfi')

process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Load up the Stage 1 parts
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_cff')

import L1Trigger.Configuration.L1Extra_cff
process.l1ExtraLayer2 = L1Trigger.Configuration.L1Extra_cff.l1extraParticles.clone()
process.l1ExtraLayer2.isolatedEmSource    = cms.InputTag("simCaloStage1LegacyFormatDigis","isoEm")
process.l1ExtraLayer2.nonIsolatedEmSource = cms.InputTag("simCaloStage1LegacyFormatDigis","nonIsoEm")
process.l1ExtraLayer2.forwardJetSource = cms.InputTag("simCaloStage1LegacyFormatDigis","forJets")
process.l1ExtraLayer2.centralJetSource = cms.InputTag("simCaloStage1LegacyFormatDigis","cenJets")
process.l1ExtraLayer2.tauJetSource     = cms.InputTag("simCaloStage1LegacyFormatDigis","tauJets")
process.l1ExtraLayer2.isoTauJetSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","isoTauJets")
process.l1ExtraLayer2.etTotalSource = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.etHadSource   = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.etMissSource  = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.htMissSource  = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.hfRingEtSumsSource    = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.hfRingBitCountsSource = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.muonSource = cms.InputTag("simGmtDigis")

# Change jet seed as set to 10 by default which is wrong
process.caloStage1Params.jetSeedThreshold = cms.double(5.)

# Use new JEC
process.caloStage1Params.jetCalibrationType = cms.string("Stage1JEC")
process.caloStage1Params.jetCalibrationLUTFile = cms.FileInPath(<path to LUT>)

# Use new RCT calibs
recordOverrides = { ('L1RCTParametersRcd', None) : (<RCT RECORD NAME>, None) }
process.GlobalTag = GlobalTag(process.GlobalTag, <YOUR GLOBAL TAG>, recordOverrides)
```

and in your process path:

```
process.RawToDigi # unpack digis
*process.simRctDigis # remake regions
*process.L1TCaloStage1 # run Stage1
*process.l1ExtraLayer2
```


###Test it

You can easily test if the new LUT is being used by looking at your script in interactive (i)python:

```
python -i myscript.py
>>> process.caloStage1Params.jetCalibrationType
cms.string('Stage1JEC')
>>> process.caloStage1Params.jetCalibrationLUTFile
cms.FileInPath(<path to LUT>)
```

Note that the default in the emulator is

```
cms.FileInPath('L1Trigger/L1TCalorimeter/data/jetCalibrationLUT_stage1_prelim.txt')
```

so if you see that something has gone wrong! If in doubt, put the additional lines at the end of your config file.

##Stage 2 (TODO)

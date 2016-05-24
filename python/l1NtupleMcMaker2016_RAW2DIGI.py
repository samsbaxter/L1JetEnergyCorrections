# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1NtupleMcMaker2016 -s RAW2DIGI -n 100 --era=Run2_2016 --mc --conditions=auto:run2_mc --no_output --no_exec --customise=L1Trigger/Configuration/customiseReEmul.L1TReEmulMCFromRAW2015 --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleAODEMUGEN_MC --geometry=Extended2016,Extended2016Reco --filein=/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/AODSIM/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/02EE186A-5AAA-E511-800E-0CC47A6C1054.root --secondfilein=/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/38297423-11AA-E511-935B-00304865C45A.root,/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/667E1C99-15AA-E511-8DA1-0CC47A13D418.root,/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/A019C82F-21AA-E511-8448-0025904897C2.root,/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/C45E74DA-1FAA-E511-93F4-0CC47A6C0682.root,/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/C668D722-18AA-E511-9689-0CC47A13D09C.root,/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/EA0B90EC-23AA-E511-9555-002590491B1E.root
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('RAW2DIGI',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/AODSIM/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/02EE186A-5AAA-E511-800E-0CC47A6C1054.root'),
    secondaryFileNames = cms.untracked.vstring('/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/38297423-11AA-E511-935B-00304865C45A.root', 
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/667E1C99-15AA-E511-8DA1-0CC47A13D418.root', 
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/A019C82F-21AA-E511-8448-0025904897C2.root', 
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/C45E74DA-1FAA-E511-93F4-0CC47A6C0682.root', 
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/C668D722-18AA-E511-9689-0CC47A13D09C.root', 
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20001/EA0B90EC-23AA-E511-9555-002590491B1E.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1NtupleMcMaker2016 nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulMCFromRAW2015 

#call to customisation function L1TReEmulMCFromRAW2015 imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulMCFromRAW2015(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAODEMUGEN_MC 

#call to customisation function L1NtupleAODEMUGEN_MC imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleAODEMUGEN_MC(process)

# End of customisation functions


# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI,L1Reco --customise=L1Trigger/Configuration/customise_Stage2Calo.Stage2CaloFromRaw --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleAODRAWEMU --conditions=auto:run2_data -n 20 --data --filein=/store/data/Run2015D/SingleMuon/AOD/16Dec2015-v1/10000/00A3E567-75A8-E511-AD0D-0CC47A4D769E.root --secondfilein=/store/data/Run2015D/SingleMuon/RAW/v1/000/260/627/00000/62834F8D-4C82-E511-8E4C-02163E013555.root --python_file=ntuple_maker_SMReco.py --era=Run2_2016 --geometry=Extended2016,Extended2016Reco --no_output
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('L1Reco',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1UpgradeEmuTree",
    "l1CaloTowerTree",
    "gtStage2Digis",
    "gmtStage2Digis"
)


process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(20)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/data/Run2015D/SingleMuon/AOD/16Dec2015-v1/10000/00A3E567-75A8-E511-AD0D-0CC47A4D769E.root'),
    secondaryFileNames = cms.untracked.vstring('/store/data/Run2015D/SingleMuon/RAW/v1/000/260/627/00000/62834F8D-4C82-E511-8E4C-02163E013555.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:20'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.endjob_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customise_Stage2Calo
from L1Trigger.Configuration.customise_Stage2Calo import Stage2CaloFromRaw 

#call to customisation function Stage2CaloFromRaw imported from L1Trigger.Configuration.customise_Stage2Calo
process = Stage2CaloFromRaw(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAODRAWEMU 

#call to customisation function L1NtupleAODRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleAODRAWEMU(process)

# End of customisation functions

process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag("ecalDigis", "EcalTriggerPrimitives")

process.TFileService.fileName = cms.string("L1Ntuple_HF_JEC_V6.root")

process.jec.connect = cms.string('sqlite:../data/Summer15_25nsV6_DATA.db')
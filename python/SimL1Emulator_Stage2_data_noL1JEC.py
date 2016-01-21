# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI,L1Reco --customise=L1Trigger/Configuration/customise_Stage2Calo.Stage2CaloFromRaw --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleRAWEMU --conditions=auto:run2_data --no_output -n 10 --data --filein=root://xrootd.unl.edu//store/express/Run2015D/ExpressPhysics/FEVT/Express-v4/000/258/287/00000/08D4CCF9-8C6B-E511-B4AD-02163E012336.root
import FWCore.ParameterSet.Config as cms

process = cms.Process('L1Reco')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 20
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeGenAk4",
    "l1UpgradeTree",
    "l1UpgradeTreeMP",
    "l1UpgradeSimTree",
    "l1UpgradeSimTreeMP",
    'csctfDigis',
    'l1CaloTowerTree',
    'l1UpgradeEmuTree'
)
process.MessageLogger.suppressError = cms.untracked.vstring(
    'gtEvmDigis'
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
)

# Input source
import FWCore.PythonUtilities.LumiList as LumiList

# run:LS:evt num filter list
with open('../Run260627/evt_clean_passCSC_passHBHE_highRsp/evt_clean_passCSC_passHBHE_highRsp_CMSSW.txt') as evt_file:
    evt_list = evt_file.readlines()
evt_list = [x.replace('\n', '') for x in evt_list]

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring((
'/store/express/Run2015D/ExpressPhysics/FEVT/Express-v4/000/260/627/00000/0C5EED03-AF81-E511-A2A3-02163E013580.root'
)),
    secondaryFileNames = cms.untracked.vstring(),
    # lumisToProcess = cms.untracked.VLuminosityBlockRange("260627:97-260627:611", "260627:613-260627:757", "260627:760-260627:788", "260627:791-260627:1051", "260627:1054-260627:1530", "260627:1533-260627:1845")
    eventsToProcess = cms.untracked.VEventRange(evt_list)
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:10'),
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
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleRAWEMU 

#call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleRAWEMU(process)

from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAOD

process = L1NtupleAOD(process)

# End of customisation functions

process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag("ecalDigis", "EcalTriggerPrimitives")
process.l1CaloTowerEmuTree.hcalToken = cms.untracked.InputTag("hcalDigis")

print 'Global Tag:', process.GlobalTag.globaltag.value()

process.caloStage2Params.jetCalibrationType = cms.string('None')

process.TFileService.fileName = 'L1Tree_Data_260627_noL1JEC_HBHENoise.root'

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

# speed optimisations - only cos we don't need them
process.l1ntupleaod.remove(process.l1MuonRecoTree)
process.l1CustomReco.remove(process.egmGsfElectronIDs)

# MET filters
process.load('RecoMET.METFilters.metFilters_cff')

# from RecoMET.METFilters.metFilters_cff import *
# individual filters
process.Flag_HBHENoiseFilter = cms.Path(process.HBHENoiseFilterResultProducer * process.HBHENoiseFilter)
process.Flag_HBHENoiseIsoFilter = cms.Path(process.HBHENoiseFilterResultProducer * process.HBHENoiseIsoFilter)
process.Flag_CSCTightHaloFilter = cms.Path(process.CSCTightHaloFilter)
# process.Flag_CSCTightHaloTrkMuUnvetoFilter = cms.Path(process.CSCTightHaloTrkMuUnvetoFilter)
process.Flag_CSCTightHalo2015Filter = cms.Path(process.CSCTightHalo2015Filter)
# process.Flag_HcalStripHaloFilter = cms.Path(process.HcalStripHaloFilter)
# process.Flag_hcalLaserEventFilter = cms.Path(process.hcalLaserEventFilter)
process.Flag_EcalDeadCellTriggerPrimitiveFilter = cms.Path(process.EcalDeadCellTriggerPrimitiveFilter)
# process.Flag_EcalDeadCellBoundaryEnergyFilter = cms.Path(process.EcalDeadCellBoundaryEnergyFilter)
process.Flag_goodVertices = cms.Path(process.primaryVertexFilter)
# process.Flag_trackingFailureFilter = cms.Path(process.goodVertices + process.trackingFailureFilter)
process.Flag_eeBadScFilter = cms.Path(process.eeBadScFilter)
# process.Flag_ecalLaserCorrFilter = cms.Path(process.ecalLaserCorrFilter)
# process.Flag_trkPOGFilters = cms.Path(process.trkPOGFilters)
# process.Flag_chargedHadronTrackResolutionFilter = cms.Path(process.chargedHadronTrackResolutionFilter)
# process.Flag_muonBadTrackFilter = cms.Path(process.muonBadTrackFilter)
# and the summary
process.Flag_METFilters = cms.Path(process.metFilters)
#
allMetFilterPaths = [
    'HBHENoiseFilter',
    'HBHENoiseIsoFilter',
    'CSCTightHaloFilter',
    'CSCTightHalo2015Filter',
    # 'HcalStripHaloFilter',
    # 'hcalLaserEventFilter',
    'EcalDeadCellTriggerPrimitiveFilter',
    # 'EcalDeadCellBoundaryEnergyFilter',
    'goodVertices',
    'eeBadScFilter',
    # 'ecalLaserCorrFilter',
    'METFilters'
   ]

# for i, filt in enumerate(allMetFilterPaths):
#     process.schedule.insert(i, getattr(process,'Flag_'+filt))

process.HBHENoiseFilterResultProducer.minZeros = cms.int32(99999)
process.HBHENoiseFilterResultProducer.IgnoreTS4TS5ifJetInLowBVRegion = cms.bool(False)
process.HBHENoiseFilterResultProducer.defaultDecision = cms.string('HBHENoiseFilterResultRun2Loose')

process.l1Tree.HBHEIsoNoiseFilterResultSource = cms.InputTag('HBHENoiseFilterResultProducer', 'HBHEIsoNoiseFilterResult')
process.l1Tree.HBHENoiseFilterResultRun2LooseSource = cms.InputTag('HBHENoiseFilterResultProducer', 'HBHENoiseFilterResultRun2Loose')
process.l1Tree.HBHENoiseFilterResultRun2TightSource = cms.InputTag('HBHENoiseFilterResultProducer', 'HBHENoiseFilterResultRun2Tight')

process.myMetFilters = cms.Path(process.HBHENoiseFilterResultProducer)
process.schedule.insert(0, process.myMetFilters)
# process.schedule.insert(0, process.Flag_HBHENoiseFilter)

# EDM output (test only)
# process.output = cms.OutputModule(
#     "PoolOutputModule",
#     splitLevel = cms.untracked.int32(0),
#     eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
#     # outputCommands = cms.untracked.vstring('keep *'),
#     fileName = cms.untracked.string('edm.root')
# )
# process.output_step = cms.EndPath(process.output)
# process.schedule.insert(len(process.schedule)-1, process.output_step)
"""
Config file to run the Stage 2 emulator to make Ntuples.

Now comes with HF!

Stores L1 jets, as well as ak4 PFjets (with calibrations)
"""

# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI,L1Reco --era=Run2_2016 --customise=L1Trigger/Configuration/customise_Stage2Calo.Stage2CaloFromRaw --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleAODRAWEMU --conditions=auto:run2_data -n 10 --data --filein=/store/data/Run2015D/SingleMuon/RAW-RECO/MuTau-PromptReco-v4/000/260/627/00000/00C3E929-6D84-E511-AFDF-02163E0146A5.root --geometry=Extended2016,Extended2016Reco
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

#############################################################################
# COMMON FLAGS:
#
# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Things to append to L1Ntuple/EDM filename (globalTag added later)
file_append = "_Stage2_Data_HF_8Feb_test500fixed"

#############################################################################

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

process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1UpgradeTree",
    "l1CaloTowerTree",
    "gtStage2Digis",
    "gmtStage2Digis"
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

# Input source
process.source = cms.Source("PoolSource",
    # fileNames = cms.untracked.vstring('/store/data/Run2015D/SingleMuon/RAW-RECO/MuTau-PromptReco-v4/000/260/627/00000/00C3E929-6D84-E511-AFDF-02163E0146A5.root'),
    fileNames = cms.untracked.vstring('/store/data/Run2015D/SingleMuon/RAW-RECO/MuTau-PromptReco-v4/000/260/627/00000/CAB1ED60-6A84-E511-8D5A-02163E014366.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RECOSIMoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string(''),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    fileName = cms.untracked.string('l1Ntuple_RAW2DIGI_L1Reco%s.root' % file_append),
    outputCommands = process.RECOSIMEventContent.outputCommands,
    # outputCommands = cms.untracked.vstring('keep *'),
    # outputCommands = cms.untracked.vstring('drop *'),
    splitLevel = cms.untracked.int32(0),
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')
file_append += '_' + process.GlobalTag.globaltag.value()

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.endjob_step)
if save_EDM:
    process.schedule.append(process.RECOSIMoutput_step)

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

# Set the right ECAL input for TPs
process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag("ecalDigis", "EcalTriggerPrimitives")

# Use MP jets
process.l1UpgradeEmuTree.jetToken = cms.untracked.InputTag("simCaloStage2Digis", "MP")
file_append += "_MPjets"

# Turn off L1JEC
process.caloStage2Params.jetCalibrationType = cms.string("None")
file_append += "_noJec"

# Set the NTuple filename
process.TFileService.fileName = cms.string("L1Ntuple%s.root" % file_append)

process.l1CustomReco.remove(process.egmGsfElectronIDs)
process.l1ntupleaod.remove(process.l1MuonRecoTree)
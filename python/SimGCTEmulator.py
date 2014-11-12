import FWCore.ParameterSet.Config as cms

process = cms.Process('L1TEMULATION')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')


############################
# ENABLING THE GCT EMULATOR
# (thanks to Jim)
############################
# To remake GCT digis
process.load("Configuration.StandardSequences.RawToDigi_cff")

# GCT emulator (to make simGctDigis)
process.load('Configuration/StandardSequences/SimL1Emulator_cff')

# change GCT emulator to take inputs from GCT unpacker (the 'gctdigis')
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')
process.simGctDigis.writeInternalData = cms.bool(True)
# Taken from the L1UpgradeJetAlgorithm - do I need these?
# process.simGctDigis.useImprovedTauAlgorithm = cms.bool(False)
# process.simGctDigis.preSamples = cms.uint32(0)
# process.simGctDigis.postSamples = cms.uint32(0)

#####################
# Making ak4 GenJets
#####################
# process.load('RecoJets.Configuration.GenJetParticles_cff')
# process.load('RecoJets.Configuration.RecoGenJets_cff')
# process.load('L1Trigger.Configuration.L1Extra_cff')
# process.ak4GenJets = process.ak5GenJets.clone(
#     rParam = cms.double(0.4)
# )
# don't need the above - it's in RecoJets.JetProducers.ak4GenJets_cfi
# which is called by RecoJets.Configuration.RecoGenJets_cff

# process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak4GenJets)

###############################################################
# Making L1Extra objects from the GCT internal jets collection
# Do I need this?
###############################################################
process.load('L1Trigger.Configuration.L1Extra_cff')
# By default these use gctDigis
process.l1extraParticles.centralJetSource = cms.InputTag("simGctDigis","cenJets")
process.l1extraParticles.forwardJetSource = cms.InputTag("simGctDigis","forJets")
process.l1extraParticles.tauJetSource = cms.InputTag("simGctDigis","tauJets")

###############
# Input source
###############
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    # fileNames = cms.untracked.vstring("root://xrootd.unl.edu//store/mc/Fall13dr/Neutrino_Pt-2to20_gun/GEN-SIM-RAW/tsg_PU40bx25_POSTLS162_V2-v1/00005/02B79593-F47F-E311-8FF6-003048FFD796.root")
    # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx25_POSTLS162_V2-v1/00000/003064F9-6C84-E311-8661-00261834B52B.root')
    fileNames = cms.untracked.vstring('file:QCD_GEN_SIM_RAW.root')
    )

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(5)
    )


###############
# Output file
###############
process.output = cms.OutputModule(
    "PoolOutputModule",
    outputCommands = cms.untracked.vstring('keep *'),
    # outputCommands = cms.untracked.vstring(
    #     'drop *',

    #     # Keep GCT jets
    #     'keep *_gctDigis_*_*',
    #     'keep *_simGctDigis_*_*',
        
    #     # Keep GenJets
    #     'keep *_ak5GenJets_*_*'
    #     ),
    fileName = cms.untracked.string('SimGCTEmulator.root')
    )
                                           
process.options = cms.untracked.PSet()


#############
# Global Tag
#############
# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag.connect = cms.string('frontier://FrontierProd/CMS_COND_31X_GLOBALTAG')
process.GlobalTag.globaltag = cms.string('POSTLS162_V2::All')


##################
# Processing path
##################
process.p1 = cms.Path(
    # process.RawToDigi  # for GenJet
    # +process.antiktGenJets  # for GenJet
    process.gctDigis
    + process.simGctDigis
    + process.L1Extra
    )

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.p1, process.output_step
    )

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

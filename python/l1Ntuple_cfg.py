import FWCore.ParameterSet.Config as cms

# make L1 ntuples from RAW+RECO

process = cms.Process("L1NTUPLE")

# import of standard configurations
process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
# process.load("Configuration.StandardSequences.RawToDigi_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')

process.MessageLogger = cms.Service("MessageLogger",
                    suppressWarning=cms.untracked.vstring('l1ExtraTreeProducerGenAk4')
)

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree.root')
)

# L1 raw to digi options
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(5)
process.l1extraParticles.centralBxOnly = cms.bool(False)

# L1 ntuple producers
## process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")
import L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi 
process.l1NtupleProducer = L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi.l1NtupleProducer.clone()

import L1TriggerDPG.L1Ntuples.l1NtupleProducer_Stage1Layer2_cfi 
process.l1NtupleProducerStage1Layer2 = L1TriggerDPG.L1Ntuples.l1NtupleProducer_Stage1Layer2_cfi.l1NtupleProducer.clone()

process.load("L1TriggerDPG.L1Ntuples.l1RecoTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MenuTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MuonRecoTreeProducer_cfi")
process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtTriggerMenuLite_cfi")

#####
# GCT internal jet collection
#####
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')
process.simGctDigis.writeInternalData = cms.bool(True)
# process.simGctDigis.useImprovedTauAlgorithm = cms.bool(False)
# process.simGctDigis.preSamples = cms.uint32(0)
# process.simGctDigis.postSamples = cms.uint32(0)

# Convert Gct Internal jets to L1Extra objects
process.l1extraParticles.gctInternJetSource = cms.InputTag("simGctDigis")
process.l1extraParticles.genJetSource = cms.InputTag("ak5GenJets")
process.l1ExtraTreeProducerGctIntern = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGctIntern.cenJetLabel = cms.untracked.InputTag("l1extraParticles:GctInternalJets")
process.l1ExtraTreeProducerGctIntern.maxL1Extra = cms.uint32(50)

#####
# Make ak4 GenJets
#####
process.load('RecoJets.Configuration.GenJetParticles_cff')
process.load('RecoJets.Configuration.RecoGenJets_cff')
process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak4GenJets)

#####
# Keep GenJets
#####
# Convert ak5 genjets to L1Extra objects
# can use the l1extraParticles module above, which produces L1JetParticleCollection from ak5GenJets
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGenAk5.cenJetLabel = cms.untracked.InputTag("l1extraParticles:GenJets")
process.l1ExtraTreeProducerGenAk5.maxL1Extra = cms.uint32(50)

# Convert ak4 genjets to L1Extra objects
# Need to clone the l1extraParticles module and set ak4GenJets as input,
# then feed that into copy of l1ExtraTreeProducer
process.l1extraParticlesAk4 = process.l1extraParticles.clone()
process.l1extraParticlesAk4.genJetSource = cms.InputTag("ak4GenJets")
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("l1extraParticlesAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)

# process.gctInternJetToL1Extra = cms.EDProducer('L1GctInternJetToL1Extra',
#     gctInternJetSource = cms.InputTag("simGctDigis")
# )

process.p = cms.Path(
    process.RawToDigi
    +process.antiktGenJets  # for GenJet
    +process.simGctDigis
    # +process.l1NtupleProducer
    +process.l1extraParticles
    +process.l1extraParticlesAk4
    # +process.gctInternJetToL1Extra
    +process.l1ExtraTreeProducerGctIntern
    +process.l1ExtraTreeProducerGenAk5
    +process.l1ExtraTreeProducerGenAk4
    # +process.l1GtTriggerMenuLite
    # +process.l1MenuTreeProducer
    # +process.l1RecoTreeProducer
    # +process.l1MuonRecoTreeProducer
)




# job options
# process.GlobalTag.globaltag = 'GR_R_52_V7::All'
process.GlobalTag.globaltag = cms.string('POSTLS162_V2::All')

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )

readFiles = cms.untracked.vstring('file:QCD_GEN_SIM_RAW.root')
secFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             # fileNames = readFiles,
                             fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/000AE06B-22A7-E311-BE0F-0025905A6138.root'),
                             secondaryFileNames = secFiles
                             )

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

# process.output_step = cms.EndPath(process.output)

# process.schedule = cms.Schedule(
#     process.p, process.output_step
#     )
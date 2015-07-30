"""
Config file to run the Stage 1 emulator on 50ns data to make Ntuples from DATA.

Stores corrected ak4 calo jets for reference jets
"""

import FWCore.ParameterSet.Config as cms

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = True

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
gt = '74X_dataRun2_Express_v0'

# Things to append to L1Ntuple/EDM filename
# (if using new RCT calibs, this gets auto added)
file_append = "_Stage1_data"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag.globaltag = cms.string(gt)

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducerIntern",
    "l1RecoTreeProducer",
)

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

##############################
# Load up Stage 1 emulator
##############################

process.load('L1Trigger.L1TCalorimeter.caloStage1Params_cfi')

# Load up the Stage 1 parts
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_cff')

# Need to feed unpacked regions into RCT formatter for stage 1
process.simRctUpgradeFormatDigis.emTag = cms.InputTag("gctDigis")
process.simRctUpgradeFormatDigis.regionTag = cms.InputTag("gctDigis")

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

# Turn off any existing stage 1 calibrations
process.caloStage1Params.jetCalibrationType = cms.string("None")

##############################
# Put normal Stage 1 collections into L1ExtraTree
##############################
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.l1ExtraTreeProducer.nonIsoEmLabel = cms.untracked.InputTag("l1ExtraLayer2:NonIsolated")
process.l1ExtraTreeProducer.isoEmLabel = cms.untracked.InputTag("l1ExtraLayer2:Isolated")
process.l1ExtraTreeProducer.tauJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Tau")
process.l1ExtraTreeProducer.isoTauJetLabel = cms.untracked.InputTag("l1ExtraLayer2:IsoTau")
process.l1ExtraTreeProducer.cenJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Central")
process.l1ExtraTreeProducer.fwdJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Forward")
process.l1ExtraTreeProducer.muonLabel = cms.untracked.InputTag("l1ExtraLayer2")
process.l1ExtraTreeProducer.metLabel = cms.untracked.InputTag("l1ExtraLayer2:MET")
process.l1ExtraTreeProducer.mhtLabel = cms.untracked.InputTag("l1ExtraLayer2:MHT")
process.l1ExtraTreeProducer.hfRingsLabel = cms.untracked.InputTag("l1ExtraLayer2")

##############################
# Do Stage 1 internal jet collection (preGtJets)
##############################
# Conversion from JetBxCollection to L1JetParticles
process.preGtJetToL1Jet = cms.EDProducer('PreGtJetToL1Jet',
    preGtJetSource = cms.InputTag("simCaloStage1FinalDigis:preGtJets")
)

# L1Extra TTree - put preGtJets in "cenJet" branch
process.l1ExtraTreeProducerIntern = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerIntern.nonIsoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.isoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.tauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.isoTauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.fwdJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.muonLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.metLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.mhtLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.hfRingsLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.cenJetLabel = cms.untracked.InputTag("preGtJetToL1Jet:PreGtJets")
process.l1ExtraTreeProducerIntern.maxL1Extra = cms.uint32(50)

##############################
# Store reco jets
##############################
process.load("L1TriggerDPG.L1Ntuples.l1RecoTreeProducer_cfi")
process.l1RecoTreeProducer.metTag = cms.untracked.InputTag("")
process.l1RecoTreeProducer.basicClustersBarrelTag = cms.untracked.InputTag("")
process.l1RecoTreeProducer.maxVtx = cms.uint32(50)

##############################
# Store other Ntuple info
##############################
process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")
process.l1NtupleProducer.gctCentralJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","cenJets")
process.l1NtupleProducer.gctNonIsoEmSource    = cms.InputTag("simCaloStage1LegacyFormatDigis","nonIsoEm")
process.l1NtupleProducer.gctForwardJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","forJets")
process.l1NtupleProducer.gctIsoEmSource       = cms.InputTag("simCaloStage1LegacyFormatDigis","isoEm")
process.l1NtupleProducer.gctEnergySumsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","")
process.l1NtupleProducer.gctTauJetsSource     = cms.InputTag("simCaloStage1LegacyFormatDigis","tauJets")
process.l1NtupleProducer.gctIsoTauJetsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","isoTauJets")
process.l1NtupleProducer.rctSource            = cms.InputTag("gctDigis")

##############################
# Select HLT paths
##############################
process.triggerSelection = cms.EDFilter("TriggerResultsFilter",
    triggerConditions = cms.vstring(
      'HLT_ZeroBias_v*'
      ),
    hltResults = cms.InputTag("TriggerResults", "", "HLT"),
    l1tResults = cms.InputTag("gtDigis"),
    l1tIgnoreMask = cms.bool(False),
    l1techIgnorePrescales = cms.bool(False),
    daqPartitions = cms.uint32(1),
    throw = cms.bool(True)
)

process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtTriggerMenuLite_cfi")

##############################
# Running path
##############################
process.p = cms.Path(
    process.gctDigis # gct unpacker
    *process.L1TCaloStage1 # run Stage1
    *process.l1ExtraLayer2
    *process.preGtJetToL1Jet # convert preGtJets into L1Jet objs
    *process.l1ExtraTreeProducer # normal Stage 1 stuff in L1ExtraTree
    *process.l1ExtraTreeProducerIntern # ditto but with preGtJets in cenJet branch
    *process.l1NtupleProducer
    *process.l1RecoTreeProducer # caloJets
    *process.l1GtTriggerMenuLite
    *process.triggerSelection
    )

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1000))

# Input source

# Some default testing files
if gt in ["74X_dataRun2_Express_v0"]:
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/express/Run2015B/ExpressPhysics/FEVT/Express-v1/000/251/244/00000/00ABFFC5-AA25-E511-A3BB-02163E0133FF.root',
                                      'root://xrootd.unl.edu//store/express/Run2015B/ExpressPhysics/FEVT/Express-v1/000/251/244/00000/045B3EE1-B525-E511-BB37-02163E013960.root')
else:
    raise RuntimeError("No file to use with GT: %s" % gt)

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

# Golden JSON - disable for crab running. Remember to update!
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(filename='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-251883_13TeV_PromptReco_Collisions15_JSON.txt').getVLuminosityBlockRange()

# Main Ntuple output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

# EDM output file
edm_filename = 'Stage1Data{0}.root'.format(file_append)
process.output = cms.OutputModule(
    "PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = cms.untracked.vstring('keep *'),
    # outputCommands = cms.untracked.vstring(
    #     'drop *',

    #     # Keep TPs
    #     'keep *_simHcalTriggerPrimitiveDigis_*_*',
    #     'keep *_hcalDigis_*_*',
    #     'keep *_ecalDigis_*_*',
    #     'keep *_gctDigis_*_*',

    #     # Keep RCT regions
    #     'keep *_simRctDigis_*_*',

    #     # Keep GenJets
    #     'keep *_ak5GenJets_*_*',
    #     'keep *_ak4GenJets_*_*',

    #     # Keep collections from Stage1
    #     'keep l1tJetBXVector_*_*_*',
    #     'keep L1GctJetCands_*_*_*',
    #     'keep l1extraL1JetParticles_*_*_*',
    #     'keep *_l1ExtraLayer2_*_*'
    # ),
    fileName = cms.untracked.string(edm_filename)
)

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

if save_EDM:
    print "*** Writing EDM to {0}".format(edm_filename)
    process.schedule.append(process.output_step)

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

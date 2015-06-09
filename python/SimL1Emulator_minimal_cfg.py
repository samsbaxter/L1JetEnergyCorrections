"""
Config file to run the Stage 1 emulator to make Ntuples.

Stores internal jets, as well as ak5 and ak4 GenJets

YOU MUST RUN WITH CMSSW 742 OR NEWER TO PICK UP THE NEW RCT CALIBS.

"""

import FWCore.ParameterSet.Config as cms

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducerGenAk4",
    "l1ExtraTreeProducerGenAk5",
    "l1ExtraTreeProducerIntern"
)

##############################
# Load up Stage 1 emulator
##############################
# This is messy, because the standard sequence
# (process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff'))
# overrides whatever new RCT calibrations you want to use
# (from L1Trigger.L1TCalorimeter.caloStage1RCTLuts_cff import * is the offending line)
# So we have to:
# - remake HCAL TPs due to it being broken in MC older than Spring15
# - rerun RCT with the regions
# - pass the regions to Stage 1 and run that

process.load('L1Trigger.L1TCalorimeter.caloStage1Params_cfi')

# Remake the HCAL TPs since hcalDigis outputs nothing in MC made with CMSSW
# earlier than 735 (not sure exactly which version, certainly works in Spring15)
# But make sure you use the unsupressed digis, not the hcalDigis
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
    cms.InputTag('simHcalUnsuppressedDigis'),
    cms.InputTag('simHcalUnsuppressedDigis')
)

# Rerun the RCT emulator using the TPs
from Configuration.StandardSequences.SimL1Emulator_cff import simRctDigis
process.simRctDigis = simRctDigis
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Load up the Stage 1 parts
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_cff')
from L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff import l1ExtraLayer2
process.l1ExtraLayer2 = l1ExtraLayer2

# Turn off any existing stage 1 calibrations
process.caloStage1Params.jetCalibrationType = cms.string("None")

##############################
# New RCT calibs
##############################
print "*** Using new RCT calibs"
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
# Format: map{(record,label):(tag,connection),...}
recordOverrides = { ('L1RCTParametersRcd', None) : ('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV2', None) }
process.GlobalTag = GlobalTag(process.GlobalTag, 'PHYS14_25_V3', recordOverrides)

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
# Do ak5 GenJets
##############################
# Need to make ak5, not included in GEN-SIM-RAW for Spring15 onwards
# process.load('RecoJets.Configuration.GenJetParticles_cff')
# process.load('RecoJets.Configuration.RecoGenJets_cff')
# process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak5GenJets)

# Convert ak5 genjets to L1JetParticle objects, store in another L1ExtraTree as cenJets
process.genJetToL1JetAk5 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak5GenJets")
)
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducerIntern.clone()
process.l1ExtraTreeProducerGenAk5.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk5:GenJets")
process.l1ExtraTreeProducerGenAk5.maxL1Extra = cms.uint32(50)

##############################
# Do ak4 GenJets
##############################
# Need to make ak4, not included in GEN-SIM-RAW before Phys14
# process.load('RecoJets.Configuration.GenJetParticles_cff')
# process.load('RecoJets.Configuration.RecoGenJets_cff')
# process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak4GenJets)

# Convert ak4 genjets to L1JetParticle objects
process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak4GenJets")
)

# Put in another L1ExtraTree as cenJets
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducerIntern.clone()
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)

process.p = cms.Path(
    process.ecalDigis # ecal unpacker
    *process.hcalDigis # hacl unpacker
    *process.simHcalTriggerPrimitiveDigis # remake hcal TPs
    *process.simRctDigis # remake regions
    *process.L1TCaloStage1 # run Stage1
    *process.l1ExtraLayer2
    *process.preGtJetToL1Jet # convert preGtJets into L1Jet objs
    # *process.antiktGenJets # make ak4GenJets - not needed in Phys14
    *process.genJetToL1JetAk5 # convert ak5GenJets to L1Jet objs
    *process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    *process.l1ExtraTreeProducer # normal Stage 1 stuff in L1ExtraTree
    *process.l1ExtraTreeProducerIntern # ditto but with preGtJets in cenJet branch
    *process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet branch
    *process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet branch
    )
process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
process.p *= process.l1RCTParametersTest
##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))

# Input source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/004DD38A-2B8E-E411-8E4F-003048FFD76E.root')
                            )

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree.root')
)

# EDM output for debugging
process.output = cms.OutputModule(
    "PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    # outputCommands = cms.untracked.vstring('keep *'),
    outputCommands = cms.untracked.vstring(
        'drop *',

        # Keep TPs
        'keep *_simHcalTriggerPrimitiveDigis_*_*',
        'keep *_hcalDigis_*_*',
        'keep *_ecalDigis_*_*',

        # Keep RCT regions
        'keep *_simRctDigis_*_*',

        # Keep GenJets
        'keep *_ak5GenJets_*_*',
        'keep *_ak4GenJets_*_*',

        # Keep collectsions from Stage1
        'keep *_*_*_L1TEMULATION',
        'keep l1tJetBXVector_*_*_*',
        'keep L1GctJetCands_*_*_*',
        'keep l1extraL1JetParticles_*_*_*'
    ),
    fileName = cms.untracked.string('SimStage1Emulator.root')
)

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

"""
Config file to run the Stage 1 emulator to make Ntuples.

This is a special case, which runs using setup that was used for HLT studies.

"""

import FWCore.ParameterSet.Config as cms


# To dump RCT parameters for testing purposes:
dump_RCT = False

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
gt = 'PHY1474_25V4' # for Phys14 AVE20 BX25

# Things to append to L1Ntuple/EDM filename
# (if using new RCT calibs, this gets auto added)
file_append = "_Stage1_oldSetup"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
# process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load( 'Configuration.StandardSequences.RawToDigi_cff' )
process.load('Configuration.StandardSequences.L1Reco_cff')
# process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag.globaltag = cms.string(gt)

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducer",
    "l1ExtraTreeProducerGenAk4",
    "l1ExtraTreeProducerGenAk5",
    "l1ExtraTreeProducerIntern",
    "l1NtupleProducer",
    "csctfDigis"
)

##############################
# Setup the L1 Emulator chain EXACTLY as it was for 25ns studies
##############################
import L1Trigger.Configuration.L1Trigger_custom

import L1Trigger.L1TCalorimeter.L1TCaloStage1_customForHLT
process = L1Trigger.L1TCalorimeter.L1TCaloStage1_customForHLT.customiseL1EmulatorFromRaw( process )

process.l1ExtraLayer2.centralBxOnly = cms.bool(True)

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
# Do ak4 GenJets
##############################
# Convert ak4 genjets to L1JetParticle objects
process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak4GenJets")
)

# Put in another L1ExtraTree as cenJets
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)

##############################
# L1Ntuple producer
##############################
# process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")
# process.l1NtupleProducer.gctCentralJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","cenJets")
# process.l1NtupleProducer.gctNonIsoEmSource    = cms.InputTag("simCaloStage1LegacyFormatDigis","nonIsoEm")
# process.l1NtupleProducer.gctForwardJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","forJets")
# process.l1NtupleProducer.gctIsoEmSource       = cms.InputTag("simCaloStage1LegacyFormatDigis","isoEm")
# process.l1NtupleProducer.gctEnergySumsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","")
# process.l1NtupleProducer.gctTauJetsSource     = cms.InputTag("simCaloStage1LegacyFormatDigis","tauJets")
# process.l1NtupleProducer.gctIsoTauJetsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","isoTauJets")

##############################
# Overall path
##############################

process.p = cms.Path(
    process.hcalDigis
    *process.simHcalTriggerPrimitiveDigis
    *process.ecalDigis
    *process.simRctDigis
    *process.simRctUpgradeFormatDigis
    *process.simCaloStage1Digis
    *process.simCaloStage1FinalDigis
    *process.simCaloStage1LegacyFormatDigis
    *process.l1ExtraLayer2
    *process.l1ExtraTreeProducer # normal Stage 1 stuff in L1ExtraTree
    *process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    *process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet branch
    )

if dump_RCT:
    process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
    process.p *= process.l1RCTParametersTest

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

# Input source

# Some default testing files
if gt in ['PHYS14_25_V3', 'PHYS14_25_V2', 'MCRUN2_74_V8', 'PHY1474_25V4']:
    # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-30to50_Tune4C_13TeV_pythia8/AODSIM/AVE20BX25_tsg_castor_PHYS14_25_V3-v2/00000/006070D2-0599-E411-98F5-0025B3E05D3A.root')
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/00679EAE-098E-E411-9AFC-0025905A6104.root')
elif gt in ['MCRUN2_74_V9', 'MCRUN2_74_V7']:
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_40_BX_25ns_tsg_MCRUN2_74_V7-v1/00000/0C72BDF4-03F4-E411-868F-003048CEFFE4.root')
else:
    raise RuntimeError("No file to use with GT: %s" % gt)

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

edm_filename = 'SimStage1Emulator{0}.root'.format(file_append)
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
        'keep *_gctDigis_*_*',

        # Keep RCT regions
        'keep *_simRctDigis_*_*',

        # Keep GenJets
        'keep *_ak5GenJets_*_*',
        'keep *_ak4GenJets_*_*',

        # Keep collections from Stage1
        'keep l1tJetBXVector_*_*_*',
        'keep L1GctJetCands_*_*_*',
        'keep l1extraL1JetParticles_*_*_*',
        'keep *_l1ExtraLayer2_*_*'
    ),
    fileName = cms.untracked.string(edm_filename)
)

# output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

if save_EDM:
    print "*** Writing EDM to {0}".format(edm_filename)
    process.schedule.append(process.output_step)

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

"""
Config file to run the Stage 2 emulator to make Ntuples.

Stores internal jets, as well as ak5 and ak4 GenJets

"""

import FWCore.ParameterSet.Config as cms

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
gt = 'MCRUN2_74_V9'  # for Spring15 AVE20BX25

# Things to append to L1Ntuple/EDM filename
# (if using new RCT calibs, this gets auto added)
file_append = "_Stage2"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, gt)

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducerGenAk4",
    "l1UpgradeTreeProducer",
    "csctfDigis"
)

##############################
# Load up Stage 2 emulator
##############################
process.load('L1Trigger.L1TCalorimeter.caloStage2Params_cfi')
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage2_cff')

# Convert the Stage 2 jets to L1Extra objects
process.stage2JetToL1Jet = cms.EDProducer('Stage2JetToL1Jet',
    stage2JetSource = cms.InputTag('caloStage2Digis:MP'),
    jetLsb = cms.double(0.5)
)

file_append += "_jetSeed0"

# Change jet seed to 5 GeV
# process.caloStage2Params.jetSeedThreshold = cms.double(5.)
# file_append += "_jetSeed5"

# Turn off calibrations
process.caloStage2Params.jetCalibrationType = cms.string("None")

process.load("L1Trigger.L1TNtuples.l1UpgradeTreeProducer_cfi")
process.l1UpgradeTreeProducer.jetLabel = cms.untracked.InputTag('stage2JetToL1Jet')
process.l1UpgradeTreeProducer.muonLabel = cms.untracked.InputTag('')

##############################
# Do ak4 GenJets
##############################
# Convert ak4 genjets to L1JetParticle objects
process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak4GenJets")
)

# Put in another L1ExtraTree as cenJets
process.load("L1Trigger.L1TNtuples.l1ExtraTreeProducer_cfi")
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGenAk4.nonIsoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.isoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.tauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.isoTauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.fwdJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.muonLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.metLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.mhtLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.hfRingsLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)

##############################
# Store PU info (nvtx, etc)
##############################
process.puInfo = cms.EDAnalyzer("PileupInfo",
    pileupInfoSource = cms.InputTag("addPileupInfo")
)

##############################
# Overall path
##############################

process.p = cms.Path(
    process.ecalDigis # ecal unpacker
    *process.hcalDigis # hcal unpacker
    # process.RawToDigi
    *process.L1TCaloStage2
    *process.stage2JetToL1Jet
    *process.l1UpgradeTreeProducer
    *process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    *process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet branch
    *process.puInfo # store nVtx info
    )

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))

# Input source

# Some default testing files
if gt in ['PHYS14_25_V3', 'PHYS14_25_V2', 'MCRUN2_74_V8']:
    fileNames = cms.untracked.vstring(
        'root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/004DD38A-2B8E-E411-8E4F-003048FFD76E.root'
        )
elif gt in ['MCRUN2_74_V9', 'MCRUN2_74_V7']:
    fileNames = cms.untracked.vstring(
        'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/00EA9A04-CD4E-E511-8F7B-001517E7410C.root'
        )
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

        # Keep GenJets
        'keep *_ak4GenJets_*_*',

        # Keep collections from Stage2
        'keep *_*_*_L1NTUPLE'
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

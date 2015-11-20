"""
Config file to run the Stage 2 emulator to make Ntuples.

Stores L1 jets, as well as ak4 GenJets
"""

import FWCore.ParameterSet.Config as cms

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False 

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
# gt = 'MCRUN2_74_V9'  # for Spring15 AVE20BX25
gt = 'MCRUN2_75_V5'  # for Spring15 AVE20BX25 in 75X
# gt = '76X_mcRun2_asymptotic_v5'  # for 76X MC

# Things to append to L1Ntuple/EDM filename
file_append = "_Stage2_newLut11NovPU15to25_calibMin0"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.RawToDigi_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/MagneticField_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
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
    jetLsb = cms.double(0.5),
    gtJets = cms.bool(False)
)

# Change jet seed to 1.5 GeV
process.caloStage2Params.jetSeedThreshold = cms.double(1.5)
file_append += "_jetSeed1p5"

# My new calibs
process.caloStage2Params.jetCalibrationType = cms.string("function6PtParams22EtaBins")
# Vector with 6 parameters for eta bin, from low eta to high
# 1,0,1,0,1,1 gives no correction
# must be in this form as may require > 255 arguments
jetCalibParamsVector = cms.vdouble()
jetCalibParamsVector.extend([
    1,0,1,0,1,1, # No calibrations in HF bins
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    3.44405985,29.74407004,3.87875334,-75.81311979,0.00608612,-18.49338073,
    1.17806455,30.26094268,2.17020820,-1129.07366073,0.01169917,-19.72357261,
    2.64833976,70.39417283,3.38253666,-107.90187171,0.01643474,-9.89486507,
    0.76120410,115.36112448,3.21992149,-3385.94255452,0.01246398,-18.84425949,
    1.27712340,106.78277188,3.52827055,-638.52812672,0.01480519,-14.08093051,
    0.97343209,62.80834066,3.02363325,-319.99245670,0.01750147,-12.42720978,
    3.25542967,34.85007383,3.00869230,-88.54304700,0.00856966,-15.35484117,
    3.25542967,34.85007383,3.00869230,-88.54304700,0.00856966,-15.35484117,
    0.97343209,62.80834066,3.02363325,-319.99245670,0.01750147,-12.42720978,
    1.27712340,106.78277188,3.52827055,-638.52812672,0.01480519,-14.08093051,
    0.76120410,115.36112448,3.21992149,-3385.94255452,0.01246398,-18.84425949,
    2.64833976,70.39417283,3.38253666,-107.90187171,0.01643474,-9.89486507,
    1.17806455,30.26094268,2.17020820,-1129.07366073,0.01169917,-19.72357261,
    3.44405985,29.74407004,3.87875334,-75.81311979,0.00608612,-18.49338073,
    1,0,1,0,1,1, # No calibrations in HF bins
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    1,0,1,0,1,1
])
process.caloStage2Params.jetCalibrationParams  = jetCalibParamsVector

# Turn off calibrations
# process.caloStage2Params.jetCalibrationType = cms.string("None")

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
elif gt in ['76X_mcRun2_asymptotic_v5', 'MCRUN2_75_V5', 'MCRUN2_74_V9']:
    fileNames = cms.untracked.vstring(
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/00EA9A04-CD4E-E511-8F7B-001517E7410C.root'
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/003BEF9B-C24E-E511-B4B7-0025905A609E.root'
        'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/00EA9A04-CD4E-E511-8F7B-001517E7410C.root'
        )
else:
    raise RuntimeError("No file to use with GT: %s" % gt)

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

edm_filename = 'SimStage2Emulator{0}.root'.format(file_append)
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

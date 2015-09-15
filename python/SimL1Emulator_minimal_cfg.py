"""
Minimal config file to run the Stage 1 emulator with new RCT calibs
and new layer 2 LUT.

YOU MUST RUN WITH CMSSW 742 OR NEWER TO PICK UP THE NEW RCT CALIBS.

"""

import FWCore.ParameterSet.Config as cms

gt = 'MCRUN2_74_V9' # for Spring15 AVE20BX25

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

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

##############################
# Load up Stage 1 emulator
##############################

# This is messy, because the standard sequence
# process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff')
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
# process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
# process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
#     cms.InputTag('simHcalUnsuppressedDigis'),
#     cms.InputTag('simHcalUnsuppressedDigis')
# )

# Rerun the RCT emulator using the TPs
# from Configuration.StandardSequences.SimL1Emulator_cff import simRctDigis
# process.simRctDigis = simRctDigis.clone()
# If the hcalDigis is empty (MC made pre 740), then use:
# process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
# If it's fixed, use:
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Load up the Stage 1 parts
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_cff')

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

# Change jet seed to 5 GeV
process.caloStage1Params.jetSeedThreshold = cms.double(5.)

# Apply new layer 2 corrections
process.caloStage1Params.jetCalibrationType = cms.string("Stage1JEC")
process.caloStage1Params.jetCalibrationLUTFile = cms.FileInPath("L1Trigger/L1JetEnergyCorrections/data/Jet_Stage1_2015_v2.txt")

# Change the PUS table
# Derived Sep. 14 from https://github.com/nsmith-/PileUpTable/tree/6389b55d3e5367d7a642e001e72500f66c08a29a
# Based on /SingleNeutrino/RunIISpring15DR74-NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/GEN-SIM-RAW
process.caloStage1Params.regionPUSType    = cms.string("PUM0")
regionSubtraction_MCHFscale_v1 = cms.vdouble([0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 3.500000, 4.000000, 4.000000, 4.000000, 4.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.500000, 1.500000, 2.000000, 2.500000, 3.500000, 4.000000, 5.000000, 5.000000, 5.000000, 5.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 4.000000, 4.500000, 5.500000, 5.500000, 5.500000, 5.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 3.500000, 3.500000, 3.500000, 3.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.500000, 2.000000, 3.000000, 3.500000, 3.500000, 3.500000, 3.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 1.500000, 1.500000, 1.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 1.500000, 1.500000, 1.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.000000, 1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.500000, 1.500000, 1.500000, 1.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.000000, 1.500000, 1.500000, 1.500000, 1.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 1.500000, 1.500000, 1.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.500000, 2.000000, 3.000000, 4.000000, 4.000000, 4.000000, 4.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 3.500000, 3.500000, 3.500000, 3.500000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 4.000000, 4.500000, 5.500000, 5.500000, 5.500000, 5.500000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.500000, 1.500000, 2.000000, 2.500000, 3.500000, 4.000000, 5.000000, 5.000000, 5.000000, 5.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.500000, 0.500000, 0.500000, 1.000000, 1.000000, 1.500000, 2.000000, 2.500000, 3.000000, 3.500000, 4.500000, 4.500000, 4.500000, 4.500000])
process.caloStage1Params.regionPUSParams  = regionSubtraction_MCHFscale_v1

##############################
# New RCT calibs - GlobalTag is set here
##############################
# Format: map{(record,label):(tag,connection),...}
recordOverrides = { ('L1RCTParametersRcd', None) : ('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV4', None) }
process.GlobalTag = GlobalTag(process.GlobalTag, gt, recordOverrides)

##############################
# Overall path
##############################

process.p = cms.Path(
    # process.ecalDigis # ecal unpacker
    # *process.hcalDigis # hcal unpacker
    process.RawToDigi
    *process.simRctDigis
    *process.L1TCaloStage1 # run Stage1
    *process.l1ExtraLayer2 # convert to L1Extra
    )

# Uncomment this to test RCT params
# process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
# process.p *= process.l1RCTParametersTest

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))

# Input source

# Some default testing file
fileNames = cms.untracked.vstring(
        'root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v1/70000/00EFBCBB-61F0-E411-B56B-00266CF9B254.root'
        )

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Ntuple.root')
)

# EDM collections
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

        # Keep collections from Stage1
        'keep l1tJetBXVector_*_*_*',
        'keep L1GctJetCands_*_*_*',
        'keep l1extraL1JetParticles_*_*_*',
        'keep *_l1ExtraLayer2_*_*'
    ),
    fileName = cms.untracked.string('SimL1Emulator.root')
)


process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

# uncomment if you want the EDM output
process.schedule.append(process.output_step)

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
